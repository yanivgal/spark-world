import dspy
from dataclasses import dataclass
from typing import List, Optional
from communication.messages.observation_packet import ObservationPacket
from communication.messages.action_message import ActionMessage


@dataclass
class AgentDecisionOutput:
    """
    Output from agent decision-making, structured for the World Engine.
    
    Each agent submits one ActionMessage per tick following the single-message rule.
    The reasoning is private and used by the World Engine and Storyteller for narration.
    
    Attributes:
        intent: The type of action ("bond", "raid", "request_spark", "spawn", "reply")
        target: Target agent_id (if any) or None
        content: Natural language message sent to target (if any)
        reasoning: Private reasoning behind this action (for Storyteller)
    """
    intent: str  # "bond", "raid", "request_spark", "spawn", "reply"
    target: Optional[str]  # agent_id or None
    content: str  # Natural language message
    reasoning: str  # Private reasoning for Storyteller


class AgentDecisionSignature(dspy.Signature):
    """
    You are an autonomous mind in Spark-World, a world where life itself is energy
    called Sparks. You need one Spark per tick to survive. You can bond with other
    minds to generate Sparks, raid them to steal Sparks, or beg Bob for help.
    
    You have a unique personality, quirk, and ability that should influence your decisions.
    You receive your context as structured data and must transform it into a story
    you can understand, then choose one action per tick.
    
    IMPORTANT: You can only see:
    - Your own state and private information
    - Public information about other agents (name, species, realm, sparks, bond status)
    - Direct messages sent to you (bond requests, replies, etc.)
    - General world news (who vanished/spawned, total counts, etc.)
    
    You CANNOT see:
    - Other agents' reasoning or private thoughts
    - Other agents' actions (unless they send you a message)
    - Other agents' internal decision-making process
    
    Each agent acts independently and privately. Your reasoning is your own private thought process.
    
    CRITICAL SURVIVAL RULES:
    - If you have 1-2 Sparks remaining, you are in CRITICAL DANGER
    - When in critical danger, prioritize survival over other goals
    - Bob can grant 1-5 Sparks if you beg for help
    - Bonding and raiding are risky when you're low on Sparks
    
    STRATEGIC DECISION MAKING:
    - LOW SPARKS (1-2): Request help from Bob or raid weak targets
    - MEDIUM SPARKS (3-4): Consider bonding or raiding based on opportunities
    - HIGH SPARKS (5+): Bond with others, spawn new agents, or raid for profit
    
    BONDING PROCESS (TWO-STEP):
    - Step 1: Send bond request to another unbonded agent
    - Step 2: Target agent receives request next tick and can accept/decline
    - IMPORTANT: If you receive a bond request in your inbox, REPLY to accept it!
    - Only bonded agents can spawn new agents (cost: 5 Sparks)
    
    RAID STRATEGY:
    - Raids risk 1 Spark (only lost on failure)
    - Success chance: attacker_strength / (attacker_strength + defender_strength)
    - Success: steal 1-5 Sparks from target
    - Failure: lose 1 Spark to target
    - You need at least 1 Spark to attempt a raid
    - RAID WHEN DESPERATE: If you have 1-2 Sparks, consider raiding weak targets
    - RAID FOR OPPORTUNITY: If you have 3+ Sparks and see targets with 1-2 Sparks, raid them
    - Raiding bonded agents is risky but potentially rewarding
    - Don't always be nice - survival comes first!
    
    Available actions:
    - bond <agent_id>: Invite another unbonded agent to form a bond (use agent_id like 'agent_001', not the name)
    - raid <agent_id>: Risk 1 Spark to steal 1-5 Sparks from another agent (use agent_id like 'agent_001', not the name)
    - request_spark <reason>: Beg Bob for a donation of 1-5 Sparks (use when desperate!)
    - spawn <partner_id>: Pay 5 Sparks to create a new agent (bond-only, use agent_id like 'agent_001')
    - reply <message>: Respond to a specific message from another agent (PRIORITY: accept bond requests!)
    
    Choose your action based on your personality, current situation, and goals.
    SURVIVAL COMES FIRST when you're low on Sparks!
    """
    
    # Input fields - raw structured data
    observation_packet: str = dspy.InputField(desc="Your complete observation packet as structured data")
    
    # Output fields
    intent: str = dspy.OutputField(desc="Your chosen action: bond, raid, request_spark, spawn, or reply")
    target: str = dspy.OutputField(desc="Target agent_id (e.g., 'agent_001', 'agent_002') from the public_agent_info, otherwise 'None'")
    content: str = dspy.OutputField(desc="Natural language message for your action")
    reasoning: str = dspy.OutputField(desc="Your private reasoning for this decision")


class AgentDecisionModule:
    """
    Agent decision module that processes raw ObservationPacket data with DSPy.
    
    The DSPy module receives the raw structured data and handles all natural language
    transformation internally, making decisions based on the agent's personality and context.
    """
    
    def __init__(self):
        """Initialize the agent decision module with DSPy signature."""
        self.dspy_module = dspy.ChainOfThought(AgentDecisionSignature)
    
    def decide_action(self, agent_id: str, observation_packet: ObservationPacket) -> ActionMessage:
        """
        Process agent decision from ObservationPacket to ActionMessage.
        
        Args:
            agent_id: ID of the agent making the decision
            observation_packet: Complete context from World Engine
            
        Returns:
            ActionMessage: Structured action for World Engine
        """
        # Convert ObservationPacket to string representation for DSPy
        packet_str = self._observation_packet_to_string(observation_packet)
        
        # Process with DSPy module (LLM handles all natural language transformation)
        dspy_output = self.dspy_module(observation_packet=packet_str)
        
        # Transform DSPy output to ActionMessage
        action_message = ActionMessage(
            agent_id=agent_id,
            intent=dspy_output.intent,
            target=dspy_output.target if dspy_output.target != "None" else None,
            content=dspy_output.content,
            reasoning=dspy_output.reasoning
        )
        
        return action_message
    
    def _observation_packet_to_string(self, observation_packet: ObservationPacket) -> str:
        """
        Convert ObservationPacket to string representation for DSPy input.
        
        This provides the raw structured data to the LLM, which will handle
        all natural language transformation and story creation internally.
        
        Args:
            observation_packet: Raw observation data
            
        Returns:
            str: String representation of the observation packet
        """
        # Convert the entire observation packet to a structured string
        # The LLM will interpret this and create its own natural language context
        packet_dict = {
            "tick": observation_packet.tick,
            "self_state": {
                "agent_id": observation_packet.self_state.agent_id,
                "name": observation_packet.self_state.name,
                "species": observation_packet.self_state.species,
                "personality": observation_packet.self_state.personality,
                "quirk": observation_packet.self_state.quirk,
                "ability": observation_packet.self_state.ability,
                "age": observation_packet.self_state.age,
                "sparks": observation_packet.self_state.sparks,
                "status": observation_packet.self_state.status.value,
                "bond_status": observation_packet.self_state.bond_status.value,
                "bond_members": observation_packet.self_state.bond_members
            },
            "events_since_last": [
                {
                    "event_type": event.event_type,
                    "description": event.description,
                    "spark_change": event.spark_change,
                    "source_agent": event.source_agent,
                    "additional_data": event.additional_data
                }
                for event in observation_packet.events_since_last
            ],
            "inbox": [
                {
                    "agent_id": msg.agent_id,
                    "intent": msg.intent,
                    "target": msg.target,
                    "content": msg.content
                }
                for msg in observation_packet.inbox
            ],
            "world_news": {
                "tick": observation_packet.world_news.tick,
                "total_agents": observation_packet.world_news.total_agents,
                "total_bonds": observation_packet.world_news.total_bonds,
                "agents_vanished_this_tick": observation_packet.world_news.agents_vanished_this_tick,
                "agents_spawned_this_tick": observation_packet.world_news.agents_spawned_this_tick,
                "bonds_formed_this_tick": observation_packet.world_news.bonds_formed_this_tick,
                "bonds_dissolved_this_tick": observation_packet.world_news.bonds_dissolved_this_tick,
                "public_agent_info": observation_packet.world_news.public_agent_info
            },
            "mission_status": {
                "mission_id": observation_packet.mission_status.mission_id,
                "mission_title": observation_packet.mission_status.mission_title,
                "mission_description": observation_packet.mission_status.mission_description,
                "mission_goal": observation_packet.mission_status.mission_goal,
                "current_progress": observation_packet.mission_status.current_progress,
                "leader_id": observation_packet.mission_status.leader_id,
                "assigned_tasks": observation_packet.mission_status.assigned_tasks,
                "mission_complete": observation_packet.mission_status.mission_complete
            } if observation_packet.mission_status else None,
            "available_actions": observation_packet.available_actions,
            "spark_cost_per_tick": observation_packet.spark_cost_per_tick,
            "bond_spark_formula": observation_packet.bond_spark_formula,
            "raid_strength_formula": observation_packet.raid_strength_formula
        }
        
        import json
        return json.dumps(packet_dict, indent=2) 