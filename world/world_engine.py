import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import json
import random
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

from character_designer.dspy_init import get_dspy
from world.state import WorldState, Agent, Bond, Mission, AgentStatus, BondStatus
from world.simulation_mechanics import RaidResult, SparkTransaction, BobResponse
from world.mission_system import MissionSystem
from world.mission_meeting_coordinator import MissionMeetingCoordinator
from agents.agent_decision import AgentDecisionModule
from agents.bob_decision import BobDecisionModule
from character_designer.shard_sower_dspy import ShardSowerModule
from communication.messages.action_message import ActionMessage
from communication.messages.observation_packet import ObservationPacket, AgentState, Event, WorldNews, MissionStatus
from communication.messages.mission_meeting_message import MissionMeetingMessage


@dataclass
class TickResult:
    """Result of a complete tick execution"""
    tick: int
    stage_results: Dict[str, str]  # Stage name -> result summary
    events_logged: List[Dict]
    agents_vanished: List[str]
    agents_spawned: List[str]
    bonds_formed: List[str]
    bonds_dissolved: List[str]
    total_sparks_minted: int
    total_sparks_lost: int
    total_raids_attempted: int


class WorldEngine:
    """
    The central orchestrator of Spark-World.
    
    This engine runs the 6-stage tick process, manages all game mechanics,
    coordinates all DSPy modules, and maintains world state persistence.
    """
    
    def __init__(self, db_path: str = "spark_world.db"):
        """Initialize the World Engine with database and all modules."""
        # Initialize DSPy
        get_dspy()
        
        # Database
        self.db_path = db_path
        self._init_database()
        
        # World state
        self.world_state = WorldState()
        
        # DSPy modules
        self.agent_decision_module = AgentDecisionModule()
        self.bob_decision_module = BobDecisionModule()
        self.shard_sower_module = ShardSowerModule()
        self.mission_system = MissionSystem()
        self.mission_meeting_coordinator = MissionMeetingCoordinator()
        
        # Pending actions from previous tick
        self.pending_bond_requests: Dict[str, ActionMessage] = {}  # target_id -> request
        self.pending_spawn_requests: List[ActionMessage] = []
        
        # Mission meeting messages for this tick
        self.mission_meeting_messages: List[MissionMeetingMessage] = []
        
        # Event logging
        self.events_this_tick: List[Dict] = []
    
    def _init_database(self):
        """Initialize SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS simulations (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS ticks (
                    id INTEGER PRIMARY KEY,
                    simulation_id INTEGER,
                    tick_number INTEGER,
                    stage TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES simulations (id)
                );
                
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    simulation_id INTEGER,
                    name TEXT,
                    species TEXT,
                    personality TEXT,
                    quirk TEXT,
                    ability TEXT,
                    age INTEGER,
                    sparks INTEGER,
                    status TEXT,
                    bond_status TEXT,
                    bond_members TEXT,
                    home_realm TEXT,
                    backstory TEXT,
                    opening_goal TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES simulations (id)
                );
                
                CREATE TABLE IF NOT EXISTS bonds (
                    id TEXT PRIMARY KEY,
                    simulation_id INTEGER,
                    leader_id TEXT,
                    mission_id TEXT,
                    members TEXT,
                    sparks_generated_this_tick INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES simulations (id)
                );
                
                CREATE TABLE IF NOT EXISTS missions (
                    id TEXT PRIMARY KEY,
                    simulation_id INTEGER,
                    bond_id TEXT,
                    title TEXT,
                    description TEXT,
                    goal TEXT,
                    current_progress TEXT,
                    leader_id TEXT,
                    assigned_tasks TEXT,
                    is_complete BOOLEAN,
                    created_tick INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES simulations (id)
                );
                
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY,
                    simulation_id INTEGER,
                    tick INTEGER,
                    event_type TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES simulations (id)
                );
                
                CREATE TABLE IF NOT EXISTS spark_transactions (
                    id INTEGER PRIMARY KEY,
                    simulation_id INTEGER,
                    tick INTEGER,
                    from_entity TEXT,
                    to_entity TEXT,
                    amount INTEGER,
                    transaction_type TEXT,
                    reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (simulation_id) REFERENCES simulations (id)
                );
            """)
    
    def initialize_world(self, num_agents: int = 3, simulation_name: str = "Spark-World Simulation") -> int:
        """
        Initialize a new Spark-World simulation.
        
        Args:
            num_agents: Number of agents to create
            simulation_name: Name for this simulation
            
        Returns:
            int: Simulation ID
        """
        # Create simulation record
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO simulations (name) VALUES (?)",
                (simulation_name,)
            )
            simulation_id = cursor.lastrowid
        
        # Create agents using Shard-Sower
        agents = {}
        for i in range(num_agents):
            agent = self.shard_sower_module.create_agent()
            agent.agent_id = f"agent_{i+1:03d}"
            agents[agent.agent_id] = agent
        
        # Initialize world state
        self.world_state = WorldState()
        self.world_state.agents = agents
        self.world_state.tick = 0
        self.world_state.is_running = True
        
        # Initialize Bob's sparks based on agent count
        num_agents = len(agents)
        self.world_state.bob_sparks = num_agents  # 1 spark per agent initially
        self.world_state.bob_sparks_per_tick = max(1, int(num_agents ** 0.5))  # Square root scaling
        
        # Save initial state
        self.save_state(simulation_id)
        
        # Log initialization event
        self._log_event(simulation_id, 0, "world_initialized", {
            "num_agents": num_agents,
            "simulation_name": simulation_name
        })
        
        return simulation_id
    
    def tick(self, simulation_id: int) -> TickResult:
        """
        Execute one complete tick of the Spark-World simulation.
        
        Args:
            simulation_id: ID of the simulation to run
            
        Returns:
            TickResult: Complete results of the tick
        """
        # Load current state
        self.load_state(simulation_id)
        
        # Increment tick
        self.world_state.tick += 1
        
        # Clear tick-specific data
        self.events_this_tick = []
        self.world_state.events_this_tick = []
        self.world_state.agents_vanished_this_tick = []
        self.world_state.agents_spawned_this_tick = []
        self.world_state.bonds_formed_this_tick = []
        self.world_state.bonds_dissolved_this_tick = []
        
        stage_results = {}
        
        # Stage 1: Mint Sparks
        self.world_state.current_processing_stage = "mint_sparks"
        stage_results["mint_sparks"] = self._stage_1_mint_sparks()
        
        # Stage 2: Bob Decides
        self.world_state.current_processing_stage = "bob_decides"
        stage_results["bob_decides"] = self._stage_2_bob_decides()
        
        # Stage 3: Agents Act
        self.world_state.current_processing_stage = "agents_act"
        stage_results["agents_act"] = self._stage_3_agents_act()
        
        # Process pending bond requests (two-step process)
        self._process_pending_bond_requests()
        
        # Stage 4: Distribute Sparks
        self.world_state.current_processing_stage = "distribute_sparks"
        stage_results["distribute_sparks"] = self._stage_4_distribute_sparks()
        
        # Stage 5: Upkeep & Vanishings
        self.world_state.current_processing_stage = "upkeep_and_vanishings"
        stage_results["upkeep_and_vanishings"] = self._stage_5_upkeep_and_vanishings()
        
        # Stage 6: Storytime (placeholder for Storyteller)
        self.world_state.current_processing_stage = "storytime"
        stage_results["storytime"] = "Events logged for Storyteller processing"
        
        # Save state
        self.save_state(simulation_id)
        
        # Create tick result
        result = TickResult(
            tick=self.world_state.tick,
            stage_results=stage_results,
            events_logged=self.events_this_tick,
            agents_vanished=self.world_state.agents_vanished_this_tick,
            agents_spawned=self.world_state.agents_spawned_this_tick,
            bonds_formed=self.world_state.bonds_formed_this_tick,
            bonds_dissolved=self.world_state.bonds_dissolved_this_tick,
            total_sparks_minted=self.world_state.total_sparks_minted,
            total_sparks_lost=self.world_state.total_sparks_lost,
            total_raids_attempted=self.world_state.total_raids_attempted
        )
        
        return result
    
    def _stage_1_mint_sparks(self) -> str:
        """Stage 1: Calculate spark generation for all bonds."""
        total_minted = 0
        
        for bond in self.world_state.bonds.values():
            if len(bond.members) >= 2:  # Only bonds with 2+ members generate sparks
                # Calculate sparks using formula: floor(n + (n-1) × 0.5)
                n = len(bond.members)
                sparks = math.floor(n + (n - 1) * 0.5)
                bond.sparks_generated_this_tick = sparks
                total_minted += sparks
                
                # Log spark minting event
                self._log_spark_transaction(
                    from_entity="bond",
                    to_entity="bond_pool",
                    amount=sparks,
                    transaction_type="bond_minting",
                    reason=f"Bond of {n} agents generated {sparks} sparks"
                )
        
        self.world_state.total_sparks_minted += total_minted
        return f"Minted {total_minted} sparks from {len(self.world_state.bonds)} bonds"
    
    def _stage_2_bob_decides(self) -> str:
        """Stage 2: Bob processes spark requests from previous tick."""
        # Get all request_spark actions from previous tick
        spark_requests = self.world_state.pending_spark_requests.copy()
        
        if not spark_requests:
            # Add Bob's regeneration even if no requests
            self.world_state.bob_sparks += self.world_state.bob_sparks_per_tick
            return "No spark requests to process"
        
        # Process with Bob decision module
        bob_responses = self.bob_decision_module.process_spark_requests(
            bob_sparks=self.world_state.bob_sparks,
            tick=self.world_state.tick,
            request_messages=spark_requests
        )
        
        # Apply Bob's decisions
        total_granted = 0
        for response in bob_responses:
            if response.sparks_granted > 0:
                # Grant sparks to agent
                agent = self.world_state.agents[response.requesting_agent_id]
                agent.sparks += response.sparks_granted
                total_granted += response.sparks_granted
                
                # Log spark transaction
                self._log_spark_transaction(
                    from_entity="bob",
                    to_entity=response.requesting_agent_id,
                    amount=response.sparks_granted,
                    transaction_type="bob_donation",
                    reason=response.reasoning
                )
                
                # Log Bob donation event
                self._log_event(
                    simulation_id=1,  # TODO: Get from context
                    tick=self.world_state.tick,
                    event_type="bob_donation",
                    data={
                        "to_entity": response.requesting_agent_id,
                        "amount": response.sparks_granted,
                        "reason": response.reasoning
                    }
                )
        
        # Update Bob's spark count
        self.world_state.bob_sparks = max(0, self.world_state.bob_sparks - total_granted)
        
        # Add Bob's regeneration
        self.world_state.bob_sparks += self.world_state.bob_sparks_per_tick
        
        # Clear processed requests
        self.world_state.pending_spark_requests.clear()
        
        return f"Bob granted {total_granted} sparks to {len([r for r in bob_responses if r.sparks_granted > 0])} agents"
    
    def _stage_3_agents_act(self) -> str:
        """Stage 3: Generate observation packets and collect agent actions."""
        # Conduct mission meetings first (pre-tick phase)
        self._conduct_mission_meetings()
        
        # Generate observation packets for all agents
        observation_packets = self._generate_observation_packets()
        
        # Collect actions from all living agents
        agent_actions = []
        for agent_id, agent in self.world_state.agents.items():
            if agent.status == AgentStatus.ALIVE:
                observation = observation_packets[agent_id]
                action = self.agent_decision_module.decide_action(agent_id, observation)
                agent_actions.append(action)
        
        # Store actions for processing in later stages
        self.world_state.pending_actions = agent_actions
        
        return f"Collected actions from {len(agent_actions)} agents"
    
    def _stage_4_distribute_sparks(self) -> str:
        """Stage 4: Distribute minted sparks randomly within bonds."""
        total_distributed = 0
        
        for bond in self.world_state.bonds.values():
            if bond.sparks_generated_this_tick > 0:
                # Get bond members
                bond_members = list(bond.members)
                
                # Distribute sparks one by one randomly
                for _ in range(bond.sparks_generated_this_tick):
                    recipient_id = random.choice(bond_members)
                    recipient = self.world_state.agents[recipient_id]
                    recipient.sparks += 1
                    total_distributed += 1
                    
                    # Log spark transaction
                    self._log_spark_transaction(
                        from_entity="bond_pool",
                        to_entity=recipient_id,
                        amount=1,
                        transaction_type="bond_distribution",
                        reason=f"Random distribution within bond {bond.bond_id}"
                    )
        
        return f"Distributed {total_distributed} sparks randomly within bonds"
    
    def _stage_5_upkeep_and_vanishings(self) -> str:
        """Stage 5: Apply upkeep costs and handle vanishings."""
        vanished_count = 0
        total_upkeep = 0
        
        # Apply upkeep costs
        for agent_id, agent in list(self.world_state.agents.items()):
            if agent.status == AgentStatus.ALIVE:
                agent.sparks -= 1
                agent.age += 1
                total_upkeep += 1
                
                # Log upkeep transaction
                self._log_spark_transaction(
                    from_entity=agent_id,
                    to_entity="upkeep",
                    amount=1,
                    transaction_type="upkeep",
                    reason="Cost of existence"
                )
                
                # Check for vanishing
                if agent.sparks <= 0:
                    self._handle_agent_vanishing(agent_id)
                    vanished_count += 1
        
        # Process pending actions (bond requests, spawns, raids)
        self._process_pending_actions()
        
        self.world_state.total_sparks_lost += total_upkeep
        return f"Applied {total_upkeep} upkeep costs, {vanished_count} agents vanished"
    
    def _conduct_mission_meetings(self):
        """Conduct mission meetings for all active missions."""
        self.world_state.mission_meetings_in_progress = True
        self.world_state.mission_meeting_messages.clear()  # Clear previous tick's messages
        
        for mission in self.world_state.missions.values():
            if not mission.is_complete:
                bond = self.world_state.bonds[mission.bond_id]
                
                # Get previous actions for context
                previous_actions = []
                for action in self.world_state.pending_actions:
                    if action.agent_id in bond.members:
                        previous_actions.append(f"{action.agent_id}: {action.intent}")
                
                # Conduct meeting
                meeting_messages = self.mission_meeting_coordinator.conduct_mission_meeting(
                    mission=mission,
                    bond=bond,
                    agents=self.world_state.agents,
                    tick=self.world_state.tick,
                    previous_actions=previous_actions
                )
                
                # Update tick numbers and store messages
                for message in meeting_messages:
                    message.tick = self.world_state.tick
                
                self.world_state.mission_meeting_messages.extend(meeting_messages)
                
                # Update mission with task assignments from the meeting
                self._update_mission_tasks(mission, meeting_messages)
        
        self.world_state.mission_meetings_in_progress = False
    
    def _update_mission_tasks(self, mission: Mission, meeting_messages: List):
        """Update mission with task assignments from meeting."""
        # Find the task assignment message (last message from leader)
        task_assignment = None
        for message in reversed(meeting_messages):
            if message.sender_id == mission.leader_id and message.message_type == "TASK_ASSIGNMENT":
                task_assignment = message
                break
        
        if task_assignment:
            # Parse task assignments from the message content
            # This is a simplified version - in practice, you'd want more structured parsing
            mission.assigned_tasks = {
                "leader_message": task_assignment.content
            }
    
    def _generate_observation_packets(self) -> Dict[str, ObservationPacket]:
        """Generate observation packets for all agents."""
        packets = {}
        
        for agent_id, agent in self.world_state.agents.items():
            if agent.status == AgentStatus.ALIVE:
                # Create agent state
                agent_state = AgentState(
                    agent_id=agent.agent_id,
                    name=agent.name,
                    species=agent.species,
                    personality=agent.personality,
                    quirk=agent.quirk,
                    ability=agent.ability,
                    age=agent.age,
                    sparks=agent.sparks,
                    status=agent.status,
                    bond_status=agent.bond_status,
                    bond_members=agent.bond_members
                )
                
                # Create events since last tick
                events = self._get_agent_events(agent_id)
                
                # Create world news
                world_news = self._create_world_news()
                
                # Create mission status (if applicable)
                mission_status = self._get_mission_status(agent_id)
                
                # Create observation packet
                packet = ObservationPacket(
                    tick=self.world_state.tick,
                    self_state=agent_state,
                    events_since_last=events,
                    inbox=self.world_state.message_queue.get(agent_id, []),
                    world_news=world_news,
                    mission_status=mission_status,
                    available_actions=["bond", "raid", "request_spark", "spawn", "reply"]
                )
                
                packets[agent_id] = packet
        
        return packets
    
    def _get_agent_events(self, agent_id: str) -> List[Event]:
        """Get events that happened to a specific agent since last tick."""
        # This would be populated based on what happened to the agent
        # For now, return empty list
        return []
    
    def _create_world_news(self) -> WorldNews:
        """Create world news for all agents."""
        public_agent_info = {}
        for agent_id, agent in self.world_state.agents.items():
            public_agent_info[agent_id] = {
                "name": agent.name,
                "species": agent.species,
                "home_realm": agent.home_realm
            }
        
        return WorldNews(
            tick=self.world_state.tick,
            total_agents=len(self.world_state.agents),
            total_bonds=len(self.world_state.bonds),
            agents_vanished_this_tick=self.world_state.agents_vanished_this_tick,
            agents_spawned_this_tick=self.world_state.agents_spawned_this_tick,
            bonds_formed_this_tick=self.world_state.bonds_formed_this_tick,
            bonds_dissolved_this_tick=self.world_state.bonds_dissolved_this_tick,
            public_agent_info=public_agent_info
        )
    
    def _get_mission_status(self, agent_id: str) -> Optional[MissionStatus]:
        """Get mission status for a bonded agent."""
        for mission in self.world_state.missions.values():
            if not mission.is_complete:
                bond = self.world_state.bonds[mission.bond_id]
                if agent_id in bond.members:
                    # Get recent meeting messages for this mission
                    recent_messages = []
                    for message in self.world_state.mission_meeting_messages:
                        if hasattr(message, 'mission_id') and message.mission_id == mission.mission_id:
                            agent_name = self.world_state.agents[message.sender_id].name
                            recent_messages.append(f"{agent_name}: {message.content}")
                    
                    # Get team member names
                    team_members = []
                    for member_id in bond.members:
                        agent = self.world_state.agents[member_id]
                        team_members.append(agent.name)
                    
                    return MissionStatus(
                        mission_id=mission.mission_id,
                        mission_title=mission.title,
                        mission_description=mission.description,
                        mission_goal=mission.goal,
                        current_progress=mission.current_progress,
                        leader_id=mission.leader_id,
                        assigned_tasks=mission.assigned_tasks,
                        mission_complete=mission.is_complete,
                        team_members=team_members,
                        recent_messages=recent_messages
                    )
        return None
    
    def _process_pending_actions(self):
        """Process all pending actions from agents."""
        for action in self.world_state.pending_actions:
            if action.intent == "bond":
                self._handle_bond_request(action)
            elif action.intent == "raid":
                self._handle_raid_action(action)
            elif action.intent == "spawn":
                self._handle_spawn_request(action)
            elif action.intent == "reply":
                self._handle_reply_action(action)
            elif action.intent == "request_spark":
                # Store for Bob's decision in next tick
                self.world_state.pending_spark_requests.append(action)
        
        # Clear processed actions
        self.world_state.pending_actions.clear()
    
    def _process_pending_bond_requests(self):
        """Process pending bond requests and form bonds."""
        for target_id, request in self.world_state.pending_bond_requests.items():
            requester_id = request.agent_id
            
            # Check if both agents are still alive and unbonded
            if (requester_id in self.world_state.agents and 
                target_id in self.world_state.agents and
                self.world_state.agents[requester_id].status == AgentStatus.ALIVE and
                self.world_state.agents[target_id].status == AgentStatus.ALIVE and
                self.world_state.agents[requester_id].bond_status == BondStatus.UNBONDED and
                self.world_state.agents[target_id].bond_status == BondStatus.UNBONDED):
                
                # Form the bond
                self._form_bond(requester_id, target_id)
        
        # Clear processed bond requests
        self.world_state.pending_bond_requests.clear()
    
    def _form_bond(self, agent1_id: str, agent2_id: str):
        """Form a bond between two agents."""
        agent1 = self.world_state.agents[agent1_id]
        agent2 = self.world_state.agents[agent2_id]
        
        # Create bond
        bond_id = f"bond_{len(self.world_state.bonds) + 1:03d}"
        bond = Bond(
            bond_id=bond_id,
            members={agent1_id, agent2_id},
            leader_id=agent1_id,  # Requester becomes leader
            mission_id=None
        )
        
        # Add bond to world
        self.world_state.bonds[bond_id] = bond
        self.world_state.bonds_formed_this_tick.append(bond_id)
        self.world_state.total_bonds_formed += 1
        
        # Update agent states
        agent1.bond_status = BondStatus.BONDED
        agent1.bond_members = [agent2_id]
        agent2.bond_status = BondStatus.BONDED
        agent2.bond_members = [agent1_id]
        
        # Log bond formation event
        self._log_event(
            simulation_id=1,  # TODO: Get from context
            tick=self.world_state.tick,
            event_type="bond_formed",
            data={
                "bond_id": bond_id,
                "agent1_id": agent1_id,
                "agent2_id": agent2_id,
                "leader_id": agent1_id
            }
        )
        
        # Generate mission for the new bond
        self._generate_mission_for_bond(bond_id)
    
    def _generate_mission_for_bond(self, bond_id: str):
        """Generate a mission for a newly formed bond."""
        bond = self.world_state.bonds[bond_id]
        
        # Create world context string
        world_context = f"Tick {self.world_state.tick}, {len(self.world_state.agents)} total agents, {len(self.world_state.bonds)} active bonds"
        
        # Create mission using Mission System
        mission = self.mission_system.generate_mission_for_bond(bond, self.world_state.agents, world_context)
        
        # Add mission to world
        self.world_state.missions[mission.mission_id] = mission
        bond.mission_id = mission.mission_id
        
        # Log mission generation event
        self._log_event(
            simulation_id=1,  # TODO: Get from context
            tick=self.world_state.tick,
            event_type="mission_generated",
            data={
                "mission_id": mission.mission_id,
                "bond_id": bond_id,
                "title": mission.title,
                "goal": mission.goal
            }
        )
    
    def _handle_bond_request(self, action: ActionMessage):
        """Handle a bond request (two-step process)."""
        if action.target and action.target in self.world_state.agents:
            # Store request for next tick processing
            self.world_state.pending_bond_requests[action.target] = action
            
            # Log bond request event
            self._log_event(
                simulation_id=1,  # TODO: Get from context
                tick=self.world_state.tick,
                event_type="bond_request",
                data={
                    "requester_id": action.agent_id,
                    "target_id": action.target,
                    "content": action.content
                }
            )
    
    def _handle_raid_action(self, action: ActionMessage):
        """Handle a raid action."""
        if action.target and action.target in self.world_state.agents:
            attacker = self.world_state.agents[action.agent_id]
            defender = self.world_state.agents[action.target]
            
            # Check if attacker has enough sparks to risk (needs at least 1 spark)
            if attacker.sparks < 1:
                # Log failed raid attempt due to insufficient sparks
                self._log_event(
                    simulation_id=1,  # TODO: Get from context
                    tick=self.world_state.tick,
                    event_type="raid_failed_no_sparks",
                    data={
                        "attacker_id": action.agent_id,
                        "defender_id": action.target,
                        "reason": "Attacker has no sparks to risk"
                    }
                )
                return
            
            # Calculate strengths (before any spark changes)
            attacker_strength = attacker.age + attacker.sparks
            defender_strength = defender.age + defender.sparks
            
            # Calculate success probability
            success_prob = attacker_strength / (attacker_strength + defender_strength)
            success = random.random() < success_prob
            
            # Process raid outcome
            if success:
                # Attacker steals 1-5 sparks from defender
                steal_amount = min(random.randint(1, 5), defender.sparks)
                attacker.sparks += steal_amount
                defender.sparks -= steal_amount
                sparks_transferred = steal_amount
                
                # Log spark transaction for successful raid
                self._log_spark_transaction(
                    from_entity=action.target,
                    to_entity=action.agent_id,
                    amount=steal_amount,
                    transaction_type="raid_success",
                    reason=f"Successful raid: {attacker_strength} vs {defender_strength} strength"
                )
            else:
                # Defender steals 1 spark from attacker (this is the "risk")
                attacker.sparks -= 1
                defender.sparks += 1
                sparks_transferred = -1
                
                # Log spark transaction for failed raid
                self._log_spark_transaction(
                    from_entity=action.agent_id,
                    to_entity=action.target,
                    amount=1,
                    transaction_type="raid_failure",
                    reason=f"Failed raid: {attacker_strength} vs {defender_strength} strength"
                )
            
            # Create raid result
            raid_result = RaidResult(
                attacker_id=action.agent_id,
                defender_id=action.target,
                success=success,
                attacker_strength=attacker_strength,
                defender_strength=defender_strength,
                sparks_transferred=sparks_transferred,
                reasoning=f"Raid {'succeeded' if success else 'failed'} with {attacker_strength} vs {defender_strength} strength"
            )
            
            # Log raid event
            self._log_event(
                simulation_id=1,  # TODO: Get from context
                tick=self.world_state.tick,
                event_type="raid",
                data=asdict(raid_result)
            )
            
            self.world_state.total_raids_attempted += 1
    
    def _handle_spawn_request(self, action: ActionMessage):
        """Handle a spawn request."""
        parent = self.world_state.agents[action.agent_id]
        
        # Check if parent has enough sparks and is bonded
        if parent.sparks >= 5 and parent.bond_status != BondStatus.UNBONDED:
            # Deduct spawn cost
            parent.sparks -= 5
            
            # Create new agent using Shard-Sower
            new_agent = self.shard_sower_module.create_agent()
            new_agent.agent_id = f"agent_{len(self.world_state.agents) + 1:03d}"
            new_agent.sparks = 5  # Newborn starts with 5 sparks
            new_agent.age = 0
            
            # Add to world
            self.world_state.agents[new_agent.agent_id] = new_agent
            self.world_state.agents_spawned_this_tick.append(new_agent.agent_id)
            
            # Log spawn event
            self._log_event(
                simulation_id=1,  # TODO: Get from context
                tick=self.world_state.tick,
                event_type="agent_spawned",
                data={
                    "parent_id": action.agent_id,
                    "new_agent_id": new_agent.agent_id,
                    "new_agent_name": new_agent.name
                }
            )
    
    def _handle_reply_action(self, action: ActionMessage):
        """Handle a reply action."""
        # Add to message queue for target agent
        if action.target:
            if action.target not in self.world_state.message_queue:
                self.world_state.message_queue[action.target] = []
            self.world_state.message_queue[action.target].append(action)
    
    def _handle_agent_vanishing(self, agent_id: str):
        """Handle an agent vanishing (sparks <= 0)."""
        agent = self.world_state.agents[agent_id]
        agent.status = AgentStatus.VANISHED
        self.world_state.agents_vanished_this_tick.append(agent_id)
        
        # Dissolve bonds containing this agent
        bonds_to_dissolve = []
        for bond_id, bond in self.world_state.bonds.items():
            if agent_id in bond.members:
                bonds_to_dissolve.append(bond_id)
        
        for bond_id in bonds_to_dissolve:
            self._dissolve_bond(bond_id)
        
        # Log vanishing event
        self._log_event(
            simulation_id=1,  # TODO: Get from context
            tick=self.world_state.tick,
            event_type="agent_vanished",
            data={
                "agent_id": agent_id,
                "agent_name": agent.name,
                "final_sparks": agent.sparks
            }
        )
    
    def _dissolve_bond(self, bond_id: str):
        """Dissolve a bond and update all member agents."""
        bond = self.world_state.bonds[bond_id]
        
        # Update all member agents
        for agent_id in bond.members:
            if agent_id in self.world_state.agents:
                agent = self.world_state.agents[agent_id]
                agent.bond_status = BondStatus.UNBONDED
                agent.bond_members = []
        
        # Remove bond
        del self.world_state.bonds[bond_id]
        self.world_state.bonds_dissolved_this_tick.append(bond_id)
        
        # Mark mission as complete if exists
        if bond.mission_id in self.world_state.missions:
            mission = self.world_state.missions[bond.mission_id]
            mission.is_complete = True
    
    def _log_event(self, simulation_id: int, tick: int, event_type: str, data: Dict):
        """Log an event to the database."""
        self.events_this_tick.append({
            "tick": tick,
            "event_type": event_type,
            "data": data
        })
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO events (simulation_id, tick, event_type, data) VALUES (?, ?, ?, ?)",
                (simulation_id, tick, event_type, json.dumps(data))
            )
    
    def _log_spark_transaction(self, from_entity: str, to_entity: str, amount: int, 
                              transaction_type: str, reason: str):
        """Log a spark transaction to the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO spark_transactions (simulation_id, tick, from_entity, to_entity, amount, transaction_type, reason) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (1, self.world_state.tick, from_entity, to_entity, amount, transaction_type, reason)
            )
    
    def save_state(self, simulation_id: int):
        """Save current world state to database."""
        with sqlite3.connect(self.db_path) as conn:
            # Save agents
            for agent in self.world_state.agents.values():
                conn.execute("""
                    INSERT OR REPLACE INTO agents 
                    (id, simulation_id, name, species, personality, quirk, ability, age, sparks, status, bond_status, bond_members, home_realm, backstory, opening_goal)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent.agent_id, simulation_id, agent.name, agent.species,
                    json.dumps(agent.personality), agent.quirk, agent.ability,
                    agent.age, agent.sparks, agent.status.value, agent.bond_status.value,
                    json.dumps(agent.bond_members), agent.home_realm, agent.backstory, agent.opening_goal
                ))
            
            # Save bonds
            for bond in self.world_state.bonds.values():
                conn.execute("""
                    INSERT OR REPLACE INTO bonds 
                    (id, simulation_id, leader_id, mission_id, members, sparks_generated_this_tick)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    bond.bond_id, simulation_id, bond.leader_id, bond.mission_id,
                    json.dumps(list(bond.members)), bond.sparks_generated_this_tick
                ))
            
            # Save missions
            for mission in self.world_state.missions.values():
                conn.execute("""
                    INSERT OR REPLACE INTO missions 
                    (id, simulation_id, bond_id, title, description, goal, current_progress, leader_id, assigned_tasks, is_complete, created_tick)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    mission.mission_id, simulation_id, mission.bond_id, mission.title,
                    mission.description, mission.goal, mission.current_progress,
                    mission.leader_id, json.dumps(mission.assigned_tasks),
                    mission.is_complete, mission.created_tick
                ))
    
    def load_state(self, simulation_id: int):
        """Load world state from database."""
        with sqlite3.connect(self.db_path) as conn:
            # Load agents
            agents = {}
            for row in conn.execute("SELECT * FROM agents WHERE simulation_id = ?", (simulation_id,)):
                agent = Agent(
                    agent_id=row[0],
                    name=row[2],
                    species=row[3],
                    personality=json.loads(row[4]),
                    quirk=row[5],
                    ability=row[6],
                    age=row[7],
                    sparks=row[8],
                    status=AgentStatus(row[9]),
                    bond_status=BondStatus(row[10]),
                    bond_members=json.loads(row[11]),
                    home_realm=row[12],
                    backstory=row[13],
                    opening_goal=row[14]
                )
                agents[agent.agent_id] = agent
            
            # Load bonds
            bonds = {}
            for row in conn.execute("SELECT * FROM bonds WHERE simulation_id = ?", (simulation_id,)):
                bond = Bond(
                    bond_id=row[0],
                    members=set(json.loads(row[4])),
                    leader_id=row[2],
                    mission_id=row[3],
                    sparks_generated_this_tick=row[5]
                )
                bonds[bond.bond_id] = bond
            
            # Load missions
            missions = {}
            for row in conn.execute("SELECT * FROM missions WHERE simulation_id = ?", (simulation_id,)):
                mission = Mission(
                    mission_id=row[0],
                    bond_id=row[2],
                    title=row[3],
                    description=row[4],
                    goal=row[5],
                    current_progress=row[6],
                    leader_id=row[7],
                    assigned_tasks=json.loads(row[8]),
                    is_complete=bool(row[9]),
                    created_tick=row[10]
                )
                missions[mission.mission_id] = mission
            
            # Update world state
            self.world_state.agents = agents
            self.world_state.bonds = bonds
            self.world_state.missions = missions 