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
import copy

from ai_client import get_dspy
from world.state import WorldState, Agent, Bond, Mission, AgentStatus, BondStatus
from world.simulation_mechanics import RaidResult, SparkTransaction, BobResponse
from world.mission_system import MissionSystem
from world.mission_meeting_coordinator import MissionMeetingCoordinator
from agents.agent_decision import AgentDecisionModule
from storytelling.storyteller import Storyteller
from storytelling.storyteller_structures import (
    StorytellerInput, AgentChange, BondFormationDetail, BondDissolutionDetail,
    MissionMeetingSummary, MissionProgressUpdate, ActionProcessingResult,
    SparkDistributionDetail, AgentVanishingContext, BobContext, TickStatistics
)
from agents.bob_decision import BobDecisionModule
from shard_sower import ShardSower
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
    agent_actions: List[ActionMessage]  # Actions taken by agents this tick
    observation_packets: Dict[str, ObservationPacket]  # Observation packets for UI display


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
        self.shard_sower_module = ShardSower()
        self.mission_system = MissionSystem()
        self.mission_meeting_coordinator = MissionMeetingCoordinator()
        self.storyteller = Storyteller(personality="blip")  # Default personality
        
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
                    speech_style TEXT,
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
    
    def reset_database(self):
        """Clear all data from the database and start fresh."""
        with sqlite3.connect(self.db_path) as conn:
            # Drop all tables
            conn.executescript("""
                DROP TABLE IF EXISTS spark_transactions;
                DROP TABLE IF EXISTS events;
                DROP TABLE IF EXISTS missions;
                DROP TABLE IF EXISTS bonds;
                DROP TABLE IF EXISTS agents;
                DROP TABLE IF EXISTS ticks;
                DROP TABLE IF EXISTS simulations;
            """)
            
            # Recreate tables
            self._init_database()
            
            # Reset world state
            self.world_state = WorldState()
            self.storyteller.story_history = []
            
            # Reset Shard-Sower for fresh character generation
            self.shard_sower_module.reset()
    
    def reset_all_modules(self):
        """Reset all modules for a completely fresh simulation start."""
        # Reset Shard-Sower
        self.shard_sower_module.reset()
        
        # Reset Storyteller
        self.storyteller.story_history = []
        
        # Reset pending actions
        self.pending_bond_requests.clear()
        self.pending_spawn_requests.clear()
        self.mission_meeting_messages.clear()
        self.events_this_tick.clear()
        
        # Reset world state
        self.world_state = WorldState()
        
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

        # --- Store previous tick's bond requests and messages for delayed inbox ---
        self.world_state.previous_tick_bond_requests = copy.deepcopy(self.world_state.pending_bond_requests)
        self.world_state.previous_tick_message_queue = copy.deepcopy(self.world_state.message_queue)
        
        # Add debug logs for bond formation timing
        print(f"🔍 TICK DEBUG: Storing previous tick data for tick {self.world_state.tick}")
        print(f"🔍 TICK DEBUG: bonds_formed_this_tick before clearing: {self.world_state.bonds_formed_this_tick}")
        
        # Store bonds formed in previous tick for delayed notification
        self.world_state.previous_tick_bonds_formed = copy.deepcopy(self.world_state.bonds_formed_this_tick)
        
        # Clear current for this tick's processing
        self.world_state.pending_bond_requests.clear()
        self.world_state.message_queue.clear()
        # --- End store previous tick ---
        
        # Capture world state BEFORE the tick begins
        world_state_before = self._capture_world_state_snapshot()
        
        # Increment tick
        self.world_state.tick += 1
        
        # Clear tick-specific data
        self.events_this_tick = []
        self.world_state.events_this_tick = []
        self.world_state.agent_actions_for_logging = []  # Clear logged agent actions
        self.world_state.raid_results_this_tick = []
        self.world_state.spark_transactions_this_tick = []
        self.world_state.bob_responses_this_tick = []
        self.world_state.agents_vanished_this_tick = []
        self.world_state.agents_spawned_this_tick = []
        self.world_state.bonds_formed_this_tick = []
        self.world_state.bonds_dissolved_this_tick = []
        self.world_state.bond_requests_for_display = {}  # Clear display bond requests
        
        # Clear enhanced tracking data
        self.world_state.agent_spark_changes.clear()
        self.world_state.agent_age_changes.clear()
        self.world_state.agent_status_changes.clear()
        self.world_state.agent_bond_status_changes.clear()
        self.world_state.bonds_formed_details.clear()
        self.world_state.bonds_dissolved_details.clear()
        self.world_state.mission_progress_updates.clear()
        self.world_state.mission_meeting_summaries.clear()
        self.world_state.action_processing_results.clear()
        self.world_state.failed_actions.clear()
        self.world_state.spark_distribution_details.clear()
        self.world_state.spark_minting_details.clear()
        self.world_state.vanished_agents_context.clear()
        self.world_state.bob_requests_received.clear()
        self.world_state.tick_statistics.clear()
        
        # Track this tick's spark generation and loss
        self.sparks_minted_this_tick = 0
        self.sparks_lost_this_tick = 0
        self.raids_attempted_this_tick = 0
        
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
        
        # Stage 4: Distribute Sparks (now handled in Stage 1)
        self.world_state.current_processing_stage = "distribute_sparks"
        stage_results["distribute_sparks"] = self._stage_4_distribute_sparks()
        
        # Stage 5: Upkeep & Vanishings
        self.world_state.current_processing_stage = "upkeep_and_vanishings"
        stage_results["upkeep_and_vanishings"] = self._stage_5_upkeep_and_vanishings()
        
        # Stage 6: Storytime (Storyteller)
        self.world_state.current_processing_stage = "storytime"
        stage_results["storytime"] = self._stage_6_storytime(world_state_before)
        
        # Generate observation packets for UI display
        observation_packets = self._generate_observation_packets()

        # Store bonds formed this tick for next tick's delayed notification
        print(f"🔍 TICK DEBUG: Storing bonds formed this tick for next tick: {self.world_state.bonds_formed_this_tick}")
        self.world_state.previous_tick_bonds_formed = copy.deepcopy(self.world_state.bonds_formed_this_tick)

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
            total_sparks_minted=self.sparks_minted_this_tick,  # Use this tick's amount, not cumulative
            total_sparks_lost=self.sparks_lost_this_tick,
            total_raids_attempted=self.raids_attempted_this_tick,
            agent_actions=self.world_state.agent_actions_for_logging,  # Use stored actions for logging
            observation_packets=observation_packets  # Add observation packets for UI
        )
        
        print(f"📋 TICK RESULT CREATED: Tick {self.world_state.tick}, bonds_formed: {result.bonds_formed}")
        
        return result
    
    def _stage_1_mint_sparks(self) -> str:
        """Stage 1: Apply upkeep costs and mint/distribute sparks from bonds."""
        # Apply upkeep costs FIRST (before any other actions)
        vanished_count = 0
        total_upkeep = 0
        
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
        
        self.world_state.total_sparks_lost += total_upkeep
        
        # Store this tick's spark loss (for TickResult)
        self.sparks_lost_this_tick = total_upkeep
        
        # Mint AND DISTRIBUTE sparks from existing bonds
        total_minted = 0
        total_distributed = 0
        
        for bond in self.world_state.bonds.values():
            # Each bond generates 1 spark per member per tick
            sparks_generated = len(bond.members)
            bond.sparks_generated_this_tick = sparks_generated
            total_minted += sparks_generated
            
            # Track distribution details for Storyteller
            distribution_details = []
            bond_name = f"Bond {bond.bond_id}"
            
            # Distribute sparks randomly within the bond
            bond_members = list(bond.members)
            for _ in range(sparks_generated):
                recipient_id = random.choice(bond_members)
                recipient = self.world_state.agents[recipient_id]
                recipient.sparks += 1
                total_distributed += 1
                
                # Track individual distribution
                distribution_details.append({
                    "recipient_id": recipient_id,
                    "recipient_name": recipient.name,
                    "sparks_received": 1
                })
                
                # Log spark transaction
                self._log_spark_transaction(
                    from_entity="bond_pool",
                    to_entity=recipient_id,
                    amount=1,
                    transaction_type="bond_distribution",
                    reason=f"Random distribution within bond {bond.bond_id}"
                )
            
            # Store distribution details for Storyteller
            self.world_state.spark_distribution_details.append({
                "bond_id": bond.bond_id,
                "bond_name": bond_name,
                "total_sparks_generated": bond.sparks_generated_this_tick,
                "distribution_details": distribution_details
            })
            
            # Log bond minting
            self._log_spark_transaction(
                from_entity="bond_pool",
                to_entity="minting",
                amount=sparks_generated,
                transaction_type="bond_minting",
                reason=f"Bond {bond.bond_id} generated {sparks_generated} sparks"
            )
        
        # Store this tick's minted sparks (for TickResult) and also accumulate to world state
        self.sparks_minted_this_tick = total_minted
        self.world_state.total_sparks_minted += total_minted
        
        return f"Applied {total_upkeep} upkeep costs ({vanished_count} vanished), minted and distributed {total_minted} sparks from bonds"
    
    def _stage_2_bob_decides(self) -> str:
        """Stage 2: Bob processes spark requests from previous tick."""
        # Store Bob's sparks before decisions
        self.world_state.bob_sparks_before = self.world_state.bob_sparks
        
        # Get all request_spark actions from previous tick
        spark_requests = self.world_state.pending_spark_requests.copy()
        
        if not spark_requests:
            # Add Bob's regeneration even if no requests
            self.world_state.bob_sparks += self.world_state.bob_sparks_per_tick
            self.world_state.bob_sparks_after = self.world_state.bob_sparks
            return "No spark requests to process"
        
        # Add spark requests to history BEFORE processing them
        for request in spark_requests:
            request.tick = self.world_state.tick - 1  # Set to previous tick when they were made
        self.world_state.all_agent_actions.extend(spark_requests)

        # Track requests received for Storyteller
        for request in spark_requests:
            requester_name = ""
            if request.agent_id in self.world_state.agents:
                requester_name = self.world_state.agents[request.agent_id].name
            self.world_state.bob_requests_received.append({
                "agent_id": request.agent_id,
                "agent_name": requester_name,
                "content": request.content,
                "reasoning": request.reasoning
            })
        
        # Process with Bob decision module
        bob_responses = self.bob_decision_module.process_spark_requests(
            bob_sparks=self.world_state.bob_sparks,
            tick=self.world_state.tick,
            request_messages=spark_requests
        )
        
        # Store Bob responses in memory for Storyteller
        self.world_state.bob_responses_this_tick = bob_responses
        
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
        # Store Bob's sparks after decisions
        self.world_state.bob_sparks_after = self.world_state.bob_sparks
        # Clear processed spark requests to prevent reprocessing
        self.world_state.pending_spark_requests.clear()
        return f"Bob granted {total_granted} sparks to {len(bob_responses)} agents"
    
    def _stage_3_agents_act(self) -> str:
        """Stage 3: All agents make their decisions and take actions."""
        # Conduct mission meetings first (pre-tick phase)
        self._conduct_mission_meetings()
        
        # Generate observation packets for all agents
        observation_packets = self._generate_observation_packets()
        
        # Collect actions from all agents
        agent_actions = []
        for agent_id, packet in observation_packets.items():
            action = self.agent_decision_module.decide_action(agent_id, packet)

            print(f"🔍 DEBUG: Agent {agent_id} decided action: {action}")
            
            # Set the tick when this action was created
            action.tick = self.world_state.tick
            agent_actions.append(action)
        
        # Store actions for processing
        self.world_state.pending_actions = agent_actions
        
        # Store actions for logging (before they get processed and cleared)
        self.world_state.agent_actions_for_logging = agent_actions.copy()
        
        # Accumulate all agent actions for history
        self.world_state.all_agent_actions.extend(agent_actions)
        
        # Store bond requests for display BEFORE processing them
        self.world_state.bond_requests_for_display = {}
        for action in agent_actions:
            if action.intent == "bond" and action.target:
                target_id = self._clean_target_field(action.target)
                if target_id:
                    self.world_state.bond_requests_for_display[target_id] = action
        
        return f"Collected {len(agent_actions)} agent actions"
    
    def _stage_4_distribute_sparks(self) -> str:
        """Stage 4: Distribute minted sparks randomly within bonds."""
        # This stage is now handled in Stage 1 (mint_and_distribute_sparks)
        return "Spark distribution moved to Stage 1"
    
    def _stage_5_upkeep_and_vanishings(self) -> str:
        """Stage 5: Process pending actions and handle any remaining vanishings."""
        # Process pending actions (bond requests, spawns, raids)
        self._process_pending_actions()
        
        return f"Processed pending actions"
    
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
    
    def _stage_6_storytime(self, world_state_before: WorldState) -> str:
        """Stage 6: Generate narrative using the Storyteller."""
        try:
            # Collect all enhanced data for the Storyteller
            agent_changes = self._collect_agent_changes(world_state_before)
            bonds_formed_details = self._collect_bond_formation_details()
            bonds_dissolved_details = self._collect_bond_dissolution_details()
            mission_meeting_summaries = self._collect_mission_meeting_summaries()
            mission_progress_updates = self._collect_mission_progress_updates()
            action_processing_results, failed_actions = self._collect_action_processing_results()
            spark_distribution_details = self._collect_spark_distribution_details()
            vanished_agents_context = self._collect_vanished_agents_context()
            bob_context = self._collect_bob_context(world_state_before)
            tick_statistics = self._collect_tick_statistics()
            
            # Get active missions
            active_missions = list(self.world_state.missions.values())
            
            # Collect all data for the Storyteller
            input_data = StorytellerInput(
                tick=self.world_state.tick,
                storyteller_personality=self.storyteller.personality,
                world_state=self.world_state,
                agent_actions=self.world_state.agent_actions_for_logging.copy(),
                raid_results=self.world_state.raid_results_this_tick.copy(),
                spark_transactions=self.world_state.spark_transactions_this_tick.copy(),
                bob_responses=self.world_state.bob_responses_this_tick.copy(),
                mission_meeting_messages=self.world_state.mission_meeting_messages.copy(),
                events_this_tick=self.world_state.events_this_tick.copy(),
                is_game_start=(self.world_state.tick == 1),
                
                # NEW: Enhanced data for rich storytelling
                world_state_before=world_state_before,
                world_state_after=self.world_state,
                agent_changes=agent_changes,
                bonds_formed_details=bonds_formed_details,
                bonds_dissolved_details=bonds_dissolved_details,
                active_missions=active_missions,
                mission_meeting_summaries=mission_meeting_summaries,
                mission_progress_updates=mission_progress_updates,
                action_processing_results=action_processing_results,
                failed_actions=failed_actions,
                spark_distribution_details=spark_distribution_details,
                spark_minting_details=self.world_state.spark_minting_details.copy(),
                vanished_agents_context=vanished_agents_context,
                bob_context=bob_context,
                tick_statistics=tick_statistics
            )
            
            # Generate narrative
            if self.world_state.tick == 1:
                # First tick: introduce the game
                story_output = self.storyteller.introduce_game(self.world_state)
            else:
                # Regular tick: create chapter
                story_output = self.storyteller.create_chapter(input_data)
            
            # Store the narrative for later use
            self.world_state.storyteller_output = story_output
            
            return f"Generated narrative: {story_output.chapter_title}"
            
        except Exception as e:
            return f"Storyteller error: {str(e)}"
    
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
                    bond_members=agent.bond_members,
                    home_realm=agent.home_realm,
                    backstory=agent.backstory,
                    opening_goal=agent.opening_goal,
                    speech_style=agent.speech_style
                )
                
                # Create events since last tick
                events = self._get_agent_events(agent_id)
                
                # Create world news
                world_news = self._create_world_news()
                
                # Create mission status (if applicable)
                mission_status = self._get_mission_status(agent_id)
                
                # Create observation packet
                # Use previous tick's bond requests and message queue for inbox to ensure consistency
                # This ensures the inbox matches what was actually processed and stored
                inbox = self._get_inbox_from_previous_tick(agent_id)
                
                # Get previous tick context (MOST IMPORTANT for decision making)
                # Note: inbox now uses pending_bond_requests and message_queue for consistency
                previous_tick_events = self._get_previous_tick_events(agent_id)
                previous_tick_actions_targeting_me = self._get_previous_tick_actions_targeting_agent(agent_id)
                previous_tick_my_actions = self._get_previous_tick_agent_actions(agent_id)
                previous_tick_bond_requests = self._get_previous_tick_bond_requests(agent_id)
                previous_tick_messages = self._get_previous_tick_messages(agent_id)
                previous_tick_raids = self._get_previous_tick_raids(agent_id)
                
                # Get full history (for reasoning and context)
                my_action_history = self.get_agent_action_history(agent_id)
                actions_targeting_me = self._get_actions_targeting_agent(agent_id)
                
                packet = ObservationPacket(
                    tick=self.world_state.tick,
                    self_state=agent_state,
                    events_since_last=events,
                    inbox=inbox,
                    world_news=world_news,
                    mission_status=mission_status,
                    available_actions=["bond", "raid", "request_spark", "spawn", "message"],
                    
                    # Previous tick context (for immediate decision making)
                    previous_tick_events=previous_tick_events,
                    previous_tick_actions_targeting_me=previous_tick_actions_targeting_me,
                    previous_tick_my_actions=previous_tick_my_actions,
                    previous_tick_bond_requests=previous_tick_bond_requests,
                    previous_tick_messages=previous_tick_messages,
                    previous_tick_raids=previous_tick_raids,
                    
                    # Full history (for reasoning and context)
                    my_action_history=my_action_history,
                    actions_targeting_me=actions_targeting_me
                )
                
                packets[agent_id] = packet
        
        return packets
    
    def _get_agent_events(self, agent_id: str) -> List[Event]:
        """Get events that happened to a specific agent since last tick."""
        events = []
        
        # Check if this agent received sparks from bond distribution
        for distribution in self.world_state.spark_distribution_details:
            for detail in distribution['distribution_details']:
                if detail['recipient_id'] == agent_id:
                    events.append(Event(
                        event_type="spark_gained",
                        description=f"Received {detail['sparks_received']} spark(s) from bond distribution",
                        spark_change=detail['sparks_received'],
                        source_agent=None,  # From bond system, not a specific agent
                        additional_data={
                            "bond_id": distribution['bond_id'],
                            "bond_name": distribution['bond_name'],
                            "reason": "bond_distribution"
                        }
                    ))
        
            # Check if this agent formed a bond in the previous tick (for delayed notification)
            print(f"🔍 AGENT EVENTS DEBUG: Checking previous_tick_bonds_formed for {agent_id}: {self.world_state.previous_tick_bonds_formed}")
            for bond_id in self.world_state.previous_tick_bonds_formed:
                # Add safety check to ensure bond exists
                if bond_id not in self.world_state.bonds:
                    print(f"🔍 UI DEBUG: Bond {bond_id} not found in bonds dictionary, skipping...")
                    continue
                
                bond = self.world_state.bonds[bond_id]
                if bond.created_tick == self.world_state.tick - 1 and agent_id in bond.members:
                    # Get other member's name
                    other_member = [mid for mid in bond.members if mid != agent_id][0]
                    other_name = self.world_state.agents[other_member].name
                    # Add bond formation event
                    events.append(Event(
                        event_type="bond_formed",
                        description=f"🎉 You formed a bond with {other_name}!",
                        spark_change=0,
                        source_agent=other_member,
                        additional_data={"bond_id": bond_id}
                    ))
                    # Add mission notification if there's a mission
                    if bond.mission_id:
                        mission = self.world_state.missions[bond.mission_id]
                        events.append(Event(
                            event_type="mission_assigned",
                            description=f"�� You received a new mission: {mission.title}",
                            spark_change=0,
                            source_agent=None,
                            additional_data={"mission_id": bond.mission_id, "mission_title": mission.title}
                        ))
            
            return events
    
    def _create_world_news(self) -> WorldNews:
        """Create world news for all agents."""
        # Count living agents
        living_agents = [agent for agent in self.world_state.agents.values() if agent.status == AgentStatus.ALIVE]
        
        # Count bonds
        active_bonds = len(self.world_state.bonds)
        
        # Get recent events
        agents_vanished = []
        agents_spawned = []
        bonds_formed = []
        bonds_dissolved = []
        
        for event in self.world_state.events_this_tick:
            if event.get('event_type') == 'agent_vanished':
                agent_name = self.world_state.agents[event['data']['agent_id']].name
                agents_vanished.append(agent_name)
            elif event.get('event_type') == 'agent_spawned':
                agent_name = self.world_state.agents[event['data']['agent_id']].name
                agents_spawned.append(agent_name)
            elif event.get('event_type') == 'bond_formed':
                bonds_formed.append(event['data']['bond_id'])
            elif event.get('event_type') == 'bond_dissolved':
                bonds_dissolved.append(event['data']['bond_id'])
        
        # Create public agent info (RESTRICTED - only basic info)
        public_agent_info = {}
        for agent in living_agents:
            # Only show basic info - agents must discover details through messaging
            public_agent_info[agent.agent_id] = {
                'name': agent.name,
                'species': agent.species,
                'realm': agent.home_realm,
                # REMOVED: sparks, bond_status - agents must discover this through interaction
            }
        
        return WorldNews(
            tick=self.world_state.tick,
            total_agents=len(living_agents),
            total_bonds=active_bonds,
            agents_vanished_this_tick=agents_vanished,
            agents_spawned_this_tick=agents_spawned,
            bonds_formed_this_tick=bonds_formed,
            bonds_dissolved_this_tick=bonds_dissolved,
            public_agent_info=public_agent_info,
            bob_sparks=self.world_state.bob_sparks
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
            print(f"🔍 PROCESSING ACTION: {action.agent_id} → {action.target} (intent: {action.intent}, bond_type: {getattr(action, 'bond_type', 'None')})")
            
            if action.intent == "bond":
                if action.bond_type == "request":
                    print(f"🔍 ROUTING TO: _handle_bond_request")
                    self._handle_bond_request(action)
                elif action.bond_type == "acceptance":
                    print(f"🔍 ROUTING TO: _handle_bond_acceptance")
                    self._handle_bond_acceptance(action)
                else:
                    # Default to request for backward compatibility
                    print(f"🔍 ROUTING TO: _handle_bond_request (default)")
                    self._handle_bond_request(action)
            elif action.intent == "raid":
                print(f"🔍 ROUTING TO: _handle_raid_action")
                self._handle_raid_action(action)
            elif action.intent == "spawn":
                print(f"🔍 ROUTING TO: _handle_spawn_request")
                self._handle_spawn_request(action)
            elif action.intent == "message":
                print(f"🔍 ROUTING TO: _handle_message_action")
                self._handle_message_action(action)
            elif action.intent == "request_spark":
                print(f"🔍 ROUTING TO: pending_spark_requests")
                # Store for Bob's decision in next tick
                self.world_state.pending_spark_requests.append(action)
        
        # Clear processed actions
        self.world_state.pending_actions.clear()
    
    def _process_pending_bond_requests(self):
        """Process pending bond requests and form bonds."""
        # First, collect all bond requests by target
        bond_requests_by_target = {}
        for target_id, requests in self.world_state.pending_bond_requests.items():
            for request in requests:
                requester_id = request.agent_id
                
                # Check if both agents are still alive and unbonded
                if (requester_id in self.world_state.agents and 
                    target_id in self.world_state.agents and
                    self.world_state.agents[requester_id].status == AgentStatus.ALIVE and
                    self.world_state.agents[target_id].status == AgentStatus.ALIVE and
                    self.world_state.agents[requester_id].bond_status == BondStatus.UNBONDED and
                    self.world_state.agents[target_id].bond_status == BondStatus.UNBONDED):
                    
                    if target_id not in bond_requests_by_target:
                        bond_requests_by_target[target_id] = []
                    bond_requests_by_target[target_id].append(requester_id)
        
        # Process bond requests to form fully-connected cliques
        processed_agents = set()
        
        for target_id, requesters in bond_requests_by_target.items():
            if target_id in processed_agents:
                continue
                
            # Find all agents that want to bond with each other (transitive closure)
            clique_members = {target_id}
            to_process = requesters.copy()
            
            while to_process:
                requester_id = to_process.pop(0)
                if requester_id in processed_agents:
                    continue
                    
                clique_members.add(requester_id)
                processed_agents.add(requester_id)
                
                # Check if this requester also has bond requests (mutual bonding)
                if requester_id in bond_requests_by_target:
                    for other_requester in bond_requests_by_target[requester_id]:
                        if other_requester not in clique_members and other_requester not in processed_agents:
                            to_process.append(other_requester)
            
            # Form the bond with all clique members
            if len(clique_members) >= 2:
                self._form_bond_clique(list(clique_members))
        
        # Clear processed bond requests
        # self.world_state.pending_bond_requests.clear()
    
    def _form_bond_clique(self, agent_ids: List[str]):
        """Form a bond between multiple agents (fully-connected clique)."""
        if len(agent_ids) < 2:
            return
            
        # Create bond
        bond_id = f"bond_{len(self.world_state.bonds) + 1:03d}"
        bond = Bond(
            bond_id=bond_id,
            members=set(agent_ids),
            leader_id=agent_ids[0],  # First agent becomes leader
            mission_id=None,
            created_tick=self.world_state.tick
        )
        
        # Add bond to world
        self.world_state.bonds[bond_id] = bond
        self.world_state.bonds_formed_this_tick.append(bond_id)
        self.world_state.total_bonds_formed += 1
        
        print(f"🤝 BOND CREATED: {bond_id} with members {agent_ids} (Tick {self.world_state.tick})")
        print(f"📊 bonds_formed_this_tick now contains: {self.world_state.bonds_formed_this_tick}")
        
        # Update all agent states
        for agent_id in agent_ids:
            agent = self.world_state.agents[agent_id]
            agent.bond_status = BondStatus.BONDED
            agent.bond_members = [aid for aid in agent_ids if aid != agent_id]  # All other members
        
        # Track bond formation details for Storyteller
        member_names = []
        for agent_id in agent_ids:
            if agent_id in self.world_state.agents:
                member_names.append(self.world_state.agents[agent_id].name)
        
        leader_name = ""
        if bond.leader_id in self.world_state.agents:
            leader_name = self.world_state.agents[bond.leader_id].name
        
        self.world_state.bonds_formed_details.append({
            "bond_id": bond_id,
            "member_ids": agent_ids,
            "member_names": member_names,
            "leader_id": bond.leader_id,
            "leader_name": leader_name,
            "mission_id": None,
            "mission_title": None
        })
        
        # Log bond formation event
        self._log_event(
            simulation_id=1,  # TODO: Get from context
            tick=self.world_state.tick,
            event_type="bond_formed",
            data={
                "bond_id": bond_id,
                "members": agent_ids,
                "member_names": member_names,
                "leader_id": bond.leader_id,
                "leader_name": leader_name
            }
        )
        
        # Generate mission for the new bond
        print(f"🎯 GENERATING MISSION for bond {bond_id}")
        self._generate_mission_for_bond(bond_id)
    
    def _generate_mission_for_bond(self, bond_id: str):
        """Generate a mission for a newly formed bond."""
        bond = self.world_state.bonds[bond_id]
        
        # Create world context string
        world_context = f"Tick {self.world_state.tick}, {len(self.world_state.agents)} total agents, {len(self.world_state.bonds)} active bonds"
        
        # Create mission using Mission System
        mission = self.mission_system.generate_mission_for_bond(bond, self.world_state.agents, world_context)
        
        # Set the created tick to the current tick
        mission.created_tick = self.world_state.tick
        
        # Add mission to world
        self.world_state.missions[mission.mission_id] = mission
        bond.mission_id = mission.mission_id
        
        print(f"🎯 MISSION CREATED: {mission.mission_id} - '{mission.title}' for bond {bond_id} (Tick {self.world_state.tick})")
        
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
    
    def _clean_target_field(self, target: str) -> str:
        """Clean target field to extract just the agent_id, removing comments and reasoning."""
        if not target:
            return None
        # Remove comments and reasoning, keep only the agent_id
        clean_target = target.split('#')[0].split('because')[0].split(' - ')[0].split(' (')[0].strip()
        return clean_target if clean_target else None

    def _handle_bond_request(self, action: ActionMessage):
        """Handle a bond request action."""
        if not action.target:
            return  # Invalid bond request
        
        requester_id = action.agent_id
        target_id = self._clean_target_field(action.target)
        
        if not target_id:
            return  # Invalid target after cleaning
        
        # Check if both agents are alive and target is unbonded
        if (requester_id in self.world_state.agents and 
            target_id in self.world_state.agents and
            self.world_state.agents[requester_id].status == AgentStatus.ALIVE and
            self.world_state.agents[target_id].status == AgentStatus.ALIVE and
            self.world_state.agents[target_id].bond_status == BondStatus.UNBONDED):  # Only target must be unbonded
            
            # Store the bond request for the target to respond to
            if target_id not in self.world_state.pending_bond_requests:
                self.world_state.pending_bond_requests[target_id] = []
            self.world_state.pending_bond_requests[target_id].append(action)
            
            print(f"🔍 BOND REQUEST STORED: {requester_id} → {target_id}")
            print(f"🔍 PENDING BOND REQUESTS for {target_id}: {[req.agent_id for req in self.world_state.pending_bond_requests[target_id]]}")
            
            # Log bond request event
            self._log_event(
                simulation_id=1,  # TODO: Get from context
                tick=self.world_state.tick,
                event_type="bond_request",
                data={
                    "requester_id": requester_id,
                    "target_id": target_id,
                    "message": action.content
                }
            )
        else:
            # Log invalid bond request
            requester = self.world_state.agents.get(requester_id)
            target = self.world_state.agents.get(target_id)
            
            if requester and target:
                if target.bond_status != BondStatus.UNBONDED:
                    print(f"DEBUG: {requester.name} tried to bond with {target.name} who is already bonded")
    
    def _handle_bond_acceptance(self, action: ActionMessage):
        """Handle a bond acceptance action."""
        target_id = self._clean_target_field(action.target)
        if not target_id:
            return
        
        print(f"🔍 BOND ACCEPTANCE HANDLER: {action.agent_id} → {target_id}")
        print(f"🔍 PREVIOUS TICK BOND REQUESTS for {action.agent_id}: {[req.agent_id for req in self.world_state.previous_tick_bond_requests.get(action.agent_id, [])]}")
        
        # Check if there's a pending bond request from target_id to action.agent_id
        if (action.agent_id in self.world_state.previous_tick_bond_requests and 
            any(req.agent_id == target_id for req in self.world_state.previous_tick_bond_requests[action.agent_id])):
            
            # Check if both agents are still alive and unbonded
            if (target_id in self.world_state.agents and 
                action.agent_id in self.world_state.agents and
                self.world_state.agents[target_id].status == AgentStatus.ALIVE and
                self.world_state.agents[action.agent_id].status == AgentStatus.ALIVE and
                self.world_state.agents[target_id].bond_status == BondStatus.UNBONDED and
                self.world_state.agents[action.agent_id].bond_status == BondStatus.UNBONDED):
                
                print(f"🔍 BOND ACCEPTANCE DETECTED: {action.agent_id} accepted bond request from {target_id}")
                print(f"✅ BOND FORMATION STARTING: {action.agent_id} + {target_id} (Tick {self.world_state.tick})")
                
                # Form the bond
                self._form_bond_clique([action.agent_id, target_id])
                
                # Remove the specific bond request that was accepted (from previous tick data)
                for i, req in enumerate(self.world_state.previous_tick_bond_requests[action.agent_id]):
                    if req.agent_id == target_id:
                        del self.world_state.previous_tick_bond_requests[action.agent_id][i]
                        break
                
                # Log bond acceptance event
                self._log_event(
                    simulation_id=1,  # TODO: Get from context
                    tick=self.world_state.tick,
                    event_type="bond_accepted",
                    data={
                        "accepter_id": action.agent_id,
                        "requester_id": target_id,
                        "message": action.content
                    }
                )
    
    def _handle_raid_action(self, action: ActionMessage):
        """Handle a raid action."""
        target_id = self._clean_target_field(action.target)
        if target_id and target_id in self.world_state.agents:
            attacker = self.world_state.agents[action.agent_id]
            defender = self.world_state.agents[target_id]
            
            # Check if attacker has enough sparks to risk (needs at least 1 spark)
            if attacker.sparks < 1:
                # Log failed raid attempt due to insufficient sparks
                self._log_event(
                    simulation_id=1,  # TODO: Get from context
                    tick=self.world_state.tick,
                    event_type="raid_failed_no_sparks",
                    data={
                        "attacker_id": action.agent_id,
                        "defender_id": target_id,
                        "reason": "Attacker has no sparks to risk"
                    }
                )
                
                # Track failed action for Storyteller
                self.world_state.action_processing_results.append({
                    "action": action,
                    "success": False,
                    "result_description": "Failed: Attacker has no sparks to risk",
                    "spark_impact": 0,
                    "target_affected": target_id
                })
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
                    from_entity=target_id,
                    to_entity=action.agent_id,
                    amount=steal_amount,
                    transaction_type="raid_success",
                    reason=f"Successful raid: {attacker_strength} vs {defender_strength} strength"
                )
                
                # Track successful action for Storyteller
                self.world_state.action_processing_results.append({
                    "action": action,
                    "success": True,
                    "result_description": f"Successful raid: stole {steal_amount} sparks",
                    "spark_impact": steal_amount,
                    "target_affected": target_id
                })
            else:
                # Defender steals 1 spark from attacker (this is the "risk")
                attacker.sparks -= 1
                defender.sparks += 1
                sparks_transferred = -1
                
                # Log spark transaction for failed raid
                self._log_spark_transaction(
                    from_entity=action.agent_id,
                    to_entity=target_id,
                    amount=1,
                    transaction_type="raid_failure",
                    reason=f"Failed raid: {attacker_strength} vs {defender_strength} strength"
                )
                
                # Track failed action for Storyteller
                self.world_state.action_processing_results.append({
                    "action": action,
                    "success": False,
                    "result_description": f"Failed raid: lost 1 spark to defender",
                    "spark_impact": -1,
                    "target_affected": target_id
                })
            
            # Create raid result
            raid_result = RaidResult(
                attacker_id=action.agent_id,
                defender_id=target_id,
                success=success,
                attacker_strength=attacker_strength,
                defender_strength=defender_strength,
                sparks_transferred=sparks_transferred,
                reasoning=f"Raid {'succeeded' if success else 'failed'} with {attacker_strength} vs {defender_strength} strength"
            )
            
            # Store raid result in memory for Storyteller
            self.world_state.raid_results_this_tick.append(raid_result)
            
            # Log raid event
            self._log_event(
                simulation_id=1,  # TODO: Get from context
                tick=self.world_state.tick,
                event_type="raid",
                data=asdict(raid_result)
            )
            
            self.world_state.total_raids_attempted += 1
            
            # Store this tick's raid attempt (for TickResult)
            self.raids_attempted_this_tick += 1
    
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
    
    def _handle_message_action(self, action: ActionMessage):
        """Handle a message action."""
        # Add to message queue for target agent
        target_id = self._clean_target_field(action.target)
        if target_id:
            if target_id not in self.world_state.message_queue:
                self.world_state.message_queue[target_id] = []
            self.world_state.message_queue[target_id].append(action)
            
            print(f"🔍 MESSAGE ACTION: {action.agent_id} → {target_id} (intent: {action.intent}, bond_type: {getattr(action, 'bond_type', 'None')})")
            print(f"🔍 PREVIOUS TICK BOND REQUESTS for {target_id}: {[req.agent_id for req in self.world_state.previous_tick_bond_requests.get(target_id, [])]}")
            
            # Check if this is a reply to a bond request (bond acceptance)
            # If the target agent has a pending bond request from this agent, form the bond
            if (target_id in self.world_state.previous_tick_bond_requests and 
                any(req.agent_id == action.agent_id for req in self.world_state.previous_tick_bond_requests[target_id])):
                
                # This is a bond acceptance - form the bond immediately
                requester_id = action.agent_id
                
                print(f"🔍 BOND ACCEPTANCE DETECTED: {requester_id} accepted bond request from {target_id}")
                
                # Check if both agents are still alive and unbonded
                if (requester_id in self.world_state.agents and 
                    target_id in self.world_state.agents and
                    self.world_state.agents[requester_id].status == AgentStatus.ALIVE and
                    self.world_state.agents[target_id].status == AgentStatus.ALIVE and
                    self.world_state.agents[requester_id].bond_status == BondStatus.UNBONDED and
                    self.world_state.agents[target_id].bond_status == BondStatus.UNBONDED):
                    
                    print(f"✅ BOND FORMATION STARTING: {requester_id} + {target_id} (Tick {self.world_state.tick})")
                    
                    # Form the bond
                    self._form_bond_clique([requester_id, target_id])
                    
                    # Remove the specific bond request that was accepted (from previous tick data)
                    for i, req in enumerate(self.world_state.previous_tick_bond_requests[target_id]):
                        if req.agent_id == requester_id:
                            del self.world_state.previous_tick_bond_requests[target_id][i]
                            break
    
    def _handle_agent_vanishing(self, agent_id: str):
        """Handle an agent vanishing (sparks <= 0)."""
        agent = self.world_state.agents[agent_id]
        agent.status = AgentStatus.VANISHED
        self.world_state.agents_vanished_this_tick.append(agent_id)
        
        # Track vanishing context for Storyteller
        bond_members = []
        mission_involvement = None
        
        # Find bond members
        for bond in self.world_state.bonds.values():
            if agent_id in bond.members:
                for member_id in bond.members:
                    if member_id != agent_id and member_id in self.world_state.agents:
                        bond_members.append(self.world_state.agents[member_id].name)
                
                # Check for mission involvement
                if bond.mission_id and bond.mission_id in self.world_state.missions:
                    mission_involvement = self.world_state.missions[bond.mission_id].title
                break
        
        self.world_state.vanished_agents_context.append({
            "agent_id": agent_id,
            "agent_name": agent.name,
            "final_sparks": agent.sparks,
            "final_age": agent.age,
            "bond_members": bond_members,
            "mission_involvement": mission_involvement,
            "vanishing_reason": "upkeep_cost"  # Could be enhanced to track other reasons
        })
        
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
                "final_sparks": agent.sparks,
                "final_age": agent.age,
                "bond_members": bond_members,
                "mission_involvement": mission_involvement
            }
        )
    
    def _dissolve_bond(self, bond_id: str):
        """Dissolve a bond and update all member agents."""
        bond = self.world_state.bonds[bond_id]
        
        # Track bond dissolution details for Storyteller
        member_names = []
        for member_id in bond.members:
            if member_id in self.world_state.agents:
                member_names.append(self.world_state.agents[member_id].name)
        
        self.world_state.bonds_dissolved_details.append({
            "bond_id": bond_id,
            "member_ids": list(bond.members),
            "member_names": member_names,
            "reason": "Bond dissolved due to member vanishing or mission completion"
        })
        
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
        # Log to both instance and world state for consistency
        self.events_this_tick.append({
            "tick": tick,
            "event_type": event_type,
            "data": data
        })
        
        # Also log to world state for observation packets
        self.world_state.events_this_tick.append({
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
        """Log a spark transaction to the database and store in memory for Storyteller."""
        # Log to database
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO spark_transactions (simulation_id, tick, from_entity, to_entity, amount, transaction_type, reason) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (1, self.world_state.tick, from_entity, to_entity, amount, transaction_type, reason)
            )
        
        # Store in memory for Storyteller
        from world.simulation_mechanics import SparkTransaction
        transaction = SparkTransaction(
            from_entity=from_entity,
            to_entity=to_entity,
            amount=amount,
            transaction_type=transaction_type,
            reason=reason,
            tick=self.world_state.tick
        )
        self.world_state.spark_transactions_this_tick.append(transaction)
    
    def save_state(self, simulation_id: int):
        """Save current world state to database."""
        with sqlite3.connect(self.db_path) as conn:
            # Save agents
            for agent in self.world_state.agents.values():
                conn.execute("""
                    INSERT OR REPLACE INTO agents 
                    (id, simulation_id, name, species, personality, quirk, ability, age, sparks, status, bond_status, bond_members, home_realm, backstory, opening_goal, speech_style)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    agent.agent_id, simulation_id, agent.name, agent.species,
                    json.dumps(agent.personality), agent.quirk, agent.ability,
                    agent.age, agent.sparks, agent.status.value, agent.bond_status.value,
                    json.dumps(agent.bond_members), agent.home_realm, agent.backstory, agent.opening_goal, agent.speech_style
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
                    opening_goal=row[14],
                    speech_style=row[15]
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
    
    def _capture_world_state_snapshot(self) -> WorldState:
        """Create a deep copy of the current world state for before/after comparison."""
        # Create a deep copy of the world state
        snapshot = copy.deepcopy(self.world_state)
        return snapshot
    
    def _collect_agent_changes(self, world_state_before: WorldState) -> List[AgentChange]:
        """Collect all agent changes that occurred during this tick."""
        agent_changes = []
        
        for agent_id, agent_after in self.world_state.agents.items():
            if agent_id in world_state_before.agents:
                agent_before = world_state_before.agents[agent_id]
                
                # Calculate changes
                spark_change = agent_after.sparks - agent_before.sparks
                age_change = agent_after.age - agent_before.age
                status_change = None
                bond_status_change = None
                bond_members_change = None
                
                # Check for status changes
                if agent_after.status != agent_before.status:
                    status_change = f"{agent_before.status.value} -> {agent_after.status.value}"
                
                # Check for bond status changes
                if agent_after.bond_status != agent_before.bond_status:
                    bond_status_change = f"{agent_before.bond_status.value} -> {agent_after.bond_status.value}"
                
                # Check for bond members changes
                if agent_after.bond_members != agent_before.bond_members:
                    bond_members_change = agent_after.bond_members
                
                # Only create change record if there were actual changes
                if (spark_change != 0 or age_change != 0 or status_change or 
                    bond_status_change or bond_members_change):
                    agent_changes.append(AgentChange(
                        agent_id=agent_id,
                        agent_name=agent_after.name,
                        spark_change=spark_change,
                        age_change=age_change,
                        status_change=status_change,
                        bond_status_change=bond_status_change,
                        bond_members_change=bond_members_change
                    ))
        
        return agent_changes
    
    def _collect_bond_formation_details(self) -> List[BondFormationDetail]:
        """Collect detailed information about bonds formed this tick."""
        bond_details = []
        
        for bond_id in self.world_state.bonds_formed_this_tick:
            if bond_id in self.world_state.bonds:
                bond = self.world_state.bonds[bond_id]
                
                # Get member names
                member_names = []
                for member_id in bond.members:
                    if member_id in self.world_state.agents:
                        member_names.append(self.world_state.agents[member_id].name)
                
                # Get leader name
                leader_name = ""
                if bond.leader_id in self.world_state.agents:
                    leader_name = self.world_state.agents[bond.leader_id].name
                
                # Get mission info if exists
                mission_id = bond.mission_id
                mission_title = None
                if mission_id and mission_id in self.world_state.missions:
                    mission_title = self.world_state.missions[mission_id].title
                
                bond_details.append(BondFormationDetail(
                    bond_id=bond_id,
                    member_ids=list(bond.members),
                    member_names=member_names,
                    leader_id=bond.leader_id,
                    leader_name=leader_name,
                    mission_id=mission_id,
                    mission_title=mission_title
                ))
        
        return bond_details
    
    def _collect_bond_dissolution_details(self) -> List[BondDissolutionDetail]:
        """Collect detailed information about bonds dissolved this tick."""
        bond_details = []
        
        for bond_id in self.world_state.bonds_dissolved_this_tick:
            # Get bond info from before dissolution (stored in world state tracking)
            for detail in self.world_state.bonds_dissolved_details:
                if detail.get('bond_id') == bond_id:
                    bond_details.append(BondDissolutionDetail(
                        bond_id=bond_id,
                        member_ids=detail.get('member_ids', []),
                        member_names=detail.get('member_names', []),
                        reason=detail.get('reason', 'Unknown')
                    ))
                    break
        
        return bond_details
    
    def _collect_mission_meeting_summaries(self) -> List[MissionMeetingSummary]:
        """Collect detailed summaries of mission meetings this tick."""
        meeting_summaries = []
        
        # Group meeting messages by mission
        mission_meetings = {}
        for message in self.world_state.mission_meeting_messages:
            mission_id = message.mission_id
            if mission_id not in mission_meetings:
                mission_meetings[mission_id] = []
            mission_meetings[mission_id].append(message)
        
        # Create summaries for each mission
        for mission_id, messages in mission_meetings.items():
            if mission_id in self.world_state.missions:
                mission = self.world_state.missions[mission_id]
                
                # Get meeting flow
                meeting_flow = [msg.message_type for msg in messages]
                
                # Get agent responses
                agent_responses = {}
                task_assignments = {}
                
                for message in messages:
                    if message.message_type == "agent_response":
                        agent_responses[message.sender_id] = message.content
                    elif message.message_type == "task_assignment":
                        # Parse task assignments from content (simplified)
                        task_assignments[message.sender_id] = message.content
                
                # Get leader name
                leader_name = ""
                if mission.leader_id in self.world_state.agents:
                    leader_name = self.world_state.agents[mission.leader_id].name
                
                meeting_summaries.append(MissionMeetingSummary(
                    mission_id=mission_id,
                    mission_title=mission.title,
                    bond_id=mission.bond_id,
                    leader_id=mission.leader_id,
                    leader_name=leader_name,
                    meeting_messages=messages,
                    meeting_flow=meeting_flow,
                    agent_responses=agent_responses,
                    task_assignments=task_assignments
                ))
        
        return meeting_summaries
    
    def _collect_mission_progress_updates(self) -> List[MissionProgressUpdate]:
        """Collect mission progress updates for this tick."""
        progress_updates = []
        
        for update in self.world_state.mission_progress_updates:
            progress_updates.append(MissionProgressUpdate(
                mission_id=update.get('mission_id', ''),
                mission_title=update.get('mission_title', ''),
                previous_progress=update.get('previous_progress', ''),
                current_progress=update.get('current_progress', ''),
                progress_change=update.get('progress_change', ''),
                is_complete=update.get('is_complete', False),
                completion_reasoning=update.get('completion_reasoning')
            ))
        
        return progress_updates
    
    def _collect_action_processing_results(self) -> Tuple[List[ActionProcessingResult], List[ActionProcessingResult]]:
        """Collect results of processing agent actions this tick."""
        successful_actions = []
        failed_actions = []
        
        for result in self.world_state.action_processing_results:
            action_result = ActionProcessingResult(
                action=result.get('action'),
                success=result.get('success', False),
                result_description=result.get('result_description', ''),
                spark_impact=result.get('spark_impact', 0),
                target_affected=result.get('target_affected')
            )
            
            if action_result.success:
                successful_actions.append(action_result)
            else:
                failed_actions.append(action_result)
        
        return successful_actions, failed_actions
    
    def _collect_spark_distribution_details(self) -> List[SparkDistributionDetail]:
        """Collect details about spark distribution within bonds this tick."""
        distribution_details = []
        
        for detail in self.world_state.spark_distribution_details:
            distribution_details.append(SparkDistributionDetail(
                bond_id=detail.get('bond_id', ''),
                bond_name=detail.get('bond_name', ''),
                total_sparks_generated=detail.get('total_sparks_generated', 0),
                distribution_details=detail.get('distribution_details', [])
            ))
        
        return distribution_details
    
    def _collect_vanished_agents_context(self) -> List[AgentVanishingContext]:
        """Collect context for agents that vanished this tick."""
        vanished_context = []
        
        for context in self.world_state.vanished_agents_context:
            vanished_context.append(AgentVanishingContext(
                agent_id=context.get('agent_id', ''),
                agent_name=context.get('agent_name', ''),
                final_sparks=context.get('final_sparks', 0),
                final_age=context.get('final_age', 0),
                bond_members=context.get('bond_members', []),
                mission_involvement=context.get('mission_involvement'),
                vanishing_reason=context.get('vanishing_reason', 'Unknown')
            ))
        
        return vanished_context
    
    def _collect_bob_context(self, world_state_before: WorldState) -> BobContext:
        """Collect complete context for Bob's decisions this tick."""
        # Calculate Bob's spark changes
        bob_sparks_before = world_state_before.bob_sparks
        bob_sparks_after = self.world_state.bob_sparks
        bob_sparks_gained = bob_sparks_after - bob_sparks_before
        
        # Get requests received
        requests_received = self.world_state.bob_requests_received.copy()
        
        # Get decisions made
        decisions_made = self.world_state.bob_responses_this_tick.copy()
        
        # Analyze reasoning patterns
        reasoning_patterns = []
        for response in decisions_made:
            if hasattr(response, 'reasoning') and response.reasoning:
                reasoning_patterns.append(response.reasoning)
        
        return BobContext(
            bob_sparks_before=bob_sparks_before,
            bob_sparks_after=bob_sparks_after,
            bob_sparks_gained=bob_sparks_gained,
            requests_received=requests_received,
            decisions_made=decisions_made,
            reasoning_patterns=reasoning_patterns
        )
    
    def _collect_tick_statistics(self) -> TickStatistics:
        """Collect summary statistics for this tick."""
        # Count successful raids
        successful_raids = sum(1 for result in self.world_state.raid_results_this_tick if result.success)
        
        # Count active bonds and missions
        active_bonds = len(self.world_state.bonds)
        active_missions = len([m for m in self.world_state.missions.values() if not m.is_complete])
        
        # Count living agents
        living_agents = len([a for a in self.world_state.agents.values() if a.status == AgentStatus.ALIVE])
        
        # Calculate total sparks distributed
        total_sparks_distributed = sum(
            detail.get('total_sparks_generated', 0) 
            for detail in self.world_state.spark_distribution_details
        )
        
        return TickStatistics(
            total_sparks_minted=self.sparks_minted_this_tick,
            total_sparks_lost=self.sparks_lost_this_tick,
            total_sparks_distributed=total_sparks_distributed,
            total_raids_attempted=self.raids_attempted_this_tick,
            total_raids_successful=successful_raids,
            total_bonds_active=active_bonds,
            total_missions_active=active_missions,
            total_agents_alive=living_agents,
            total_agents_vanished=len(self.world_state.agents_vanished_this_tick),
            total_agents_spawned=len(self.world_state.agents_spawned_this_tick)
        ) 

    def get_actions_from_tick(self, tick_number: int) -> List[ActionMessage]:
        return [action for action in self.world_state.all_agent_actions if action.tick == tick_number] 

    def get_agent_action_history(self, agent_id: str) -> List[ActionMessage]:
        """Get all actions taken by this agent."""
        return [action for action in self.world_state.all_agent_actions if action.agent_id == agent_id]

    def _get_previous_tick_events(self, agent_id: str) -> List[Event]:
        """Get events from previous tick that affected this agent."""
        previous_tick = self.world_state.tick - 1
        events = []
        
        # Get actions from previous tick that affected this agent
        previous_tick_actions = [action for action in self.world_state.all_agent_actions 
                                if action.tick == previous_tick]
        
        for action in previous_tick_actions:
            if action.target == agent_id:
                if action.intent == "raid":
                    events.append(Event(
                        event_type="raid_attack",
                        description=f"Was raided by {action.agent_id}",
                        spark_change=0,  # Will be calculated by raid logic
                        source_agent=action.agent_id,
                        additional_data={"raid_action": action}
                    ))
                elif action.intent == "bond":
                    events.append(Event(
                        event_type="bond_request_received",
                        description=f"Received bond request from {action.agent_id}",
                        spark_change=0,
                        source_agent=action.agent_id,
                        additional_data={"bond_request": action}
                    ))
                elif action.intent == "message":
                    events.append(Event(
                        event_type="message_received",
                        description=f"Received message from {action.agent_id}",
                        spark_change=0,
                        source_agent=action.agent_id,
                        additional_data={"message": action}
                    ))
        
        # Add events for actions this agent took in previous tick
        for action in previous_tick_actions:
            if action.agent_id == agent_id:
                if action.intent == "raid":
                    events.append(Event(
                        event_type="raid_executed",
                        description=f"Raided {action.target}",
                        spark_change=0,  # Will be calculated by raid logic
                        source_agent=agent_id,
                        additional_data={"raid_action": action}
                    ))
                elif action.intent == "request_spark":
                    events.append(Event(
                        event_type="spark_requested",
                        description=f"Requested sparks from Bob",
                        spark_change=0,
                        source_agent=agent_id,
                        additional_data={"spark_request": action}
                    ))
        
        return events

    def _get_previous_tick_actions_targeting_agent(self, agent_id: str) -> List[ActionMessage]:
        """Get actions from previous tick where this agent was the target."""
        previous_tick = self.world_state.tick - 1
        return [action for action in self.world_state.all_agent_actions 
                if action.tick == previous_tick and action.target == agent_id]

    def _get_previous_tick_agent_actions(self, agent_id: str) -> List[ActionMessage]:
        """Get actions this agent took in previous tick."""
        previous_tick = self.world_state.tick - 1
        return [action for action in self.world_state.all_agent_actions 
                if action.tick == previous_tick and action.agent_id == agent_id]

    def _get_previous_tick_bond_requests(self, agent_id: str) -> List[ActionMessage]:
        """Get bond requests this agent received in previous tick."""
        previous_tick = self.world_state.tick - 1
        return [action for action in self.world_state.all_agent_actions 
                if action.tick == previous_tick and action.target == agent_id and action.intent == "bond" 
                and (action.bond_type == "request" or action.bond_type is None)]  # Include None for backward compatibility

    def _get_previous_tick_messages(self, agent_id: str) -> List[ActionMessage]:
        """Get messages this agent received in previous tick."""
        previous_tick = self.world_state.tick - 1
        return [action for action in self.world_state.all_agent_actions 
                if action.tick == previous_tick and action.target == agent_id and action.intent == "message"]

    def _get_previous_tick_raids(self, agent_id: str) -> List[ActionMessage]:
        """Get raids involving this agent in previous tick (as attacker or defender)."""
        previous_tick = self.world_state.tick - 1
        return [action for action in self.world_state.all_agent_actions 
                if action.tick == previous_tick and 
                action.intent == "raid" and 
                (action.agent_id == agent_id or action.target == agent_id)]

    def _get_actions_targeting_agent(self, agent_id: str) -> List[ActionMessage]:
        """Get all actions where this agent was the target (full history)."""
        return [action for action in self.world_state.all_agent_actions if action.target == agent_id]
    
    def _get_bob_responses_for_agent(self, agent_id: str) -> List[ActionMessage]:
        """Get Bob's responses for a specific agent from the previous tick."""
        bob_responses = []
        previous_tick = self.world_state.tick - 1
        
        # Check if we have Bob's responses from the previous tick
        if hasattr(self.world_state, 'bob_responses_this_tick'):
            for bob_response in self.world_state.bob_responses_this_tick:
                if bob_response.requesting_agent_id == agent_id and bob_response.tick == previous_tick:
                    # Create an ActionMessage from Bob's response
                    status = "granted" if bob_response.sparks_granted > 0 else "denied"
                    content = f"Your request for sparks has been {status}. {bob_response.reasoning}"
                    
                    bob_message = ActionMessage(
                        agent_id="bob",
                        intent="bob_response",
                        target=agent_id,
                        content=content,
                        reasoning=bob_response.reasoning,
                        tick=previous_tick,
                        bond_type=None
                    )
                    bob_responses.append(bob_message)
        
        return bob_responses
    
    def _get_inbox_from_previous_tick(self, agent_id: str) -> List[ActionMessage]:
        """Get inbox messages from previous tick's bond requests, message queue, and Bob's responses for this agent."""
        inbox = []
        if agent_id in self.world_state.previous_tick_bond_requests:
            inbox.extend(self.world_state.previous_tick_bond_requests[agent_id])
        if agent_id in self.world_state.previous_tick_message_queue:
            inbox.extend(self.world_state.previous_tick_message_queue[agent_id])
        
        # Add Bob's responses from previous tick
        bob_responses = self._get_bob_responses_for_agent(agent_id)
        inbox.extend(bob_responses)
        
        return inbox