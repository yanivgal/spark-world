from dataclasses import dataclass
from typing import Optional, List, Dict
from enum import Enum
from .action_message import ActionMessage


class AgentStatus(Enum):
    """Status of an agent in the world"""
    ALIVE = "alive"
    VANISHED = "vanished"


class BondStatus(Enum):
    """Bond status of an agent"""
    UNBONDED = "unbonded"
    BONDED = "bonded"
    LEADER = "leader"


@dataclass
class AgentState:
    """Current state of the agent"""
    agent_id: str
    name: str
    species: str
    personality: List[str]
    quirk: str
    ability: str
    age: int
    sparks: int
    status: AgentStatus
    bond_status: BondStatus
    bond_members: List[str]  # List of agent_ids in the same bond, including self


@dataclass
class Event:
    """Something that happened to this agent since last tick"""
    event_type: str  # "spark_gained", "spark_lost", "raid_attack", "raid_defense", "bond_request", "bond_formed", "bond_member_vanished"
    description: str
    spark_change: int  # How many sparks gained/lost
    source_agent: Optional[str]  # Who caused this event
    additional_data: Dict  # Any extra info (raid success/failure, etc.)


@dataclass
class WorldNews:
    """General world information all agents know"""
    tick: int
    total_agents: int
    total_bonds: int
    agents_vanished_this_tick: List[str]
    agents_spawned_this_tick: List[str]
    bonds_formed_this_tick: List[str]
    bonds_dissolved_this_tick: List[str]  # Bonds that dissolved due to member vanishing
    public_agent_info: Dict[str, Dict]  # name, species, realm for all agents


@dataclass
class MissionStatus:
    """Mission information for bonded agents"""
    mission_id: str
    mission_title: str
    mission_description: str
    mission_goal: str
    current_progress: str
    leader_id: str
    assigned_tasks: Dict[str, str]  # agent_id -> task description
    mission_complete: bool


@dataclass
class ObservationPacket:
    """
    Complete context packet sent to each agent every tick.
    
    This contains everything an agent needs to know to make informed decisions.
    Used in both regular ticks and mission meetings.
    
    Attributes:
        tick: Current tick number
        self_state: Complete current state of this agent
        events_since_last: What happened to this agent since last tick
        inbox: Direct messages from other agents
        world_news: General world context and changes
        mission_status: Mission context (only for bonded agents)
        available_actions: What actions this agent can take
        spark_cost_per_tick: How many sparks are lost per tick
        bond_spark_formula: Formula for bond spark generation
        raid_strength_formula: Formula for raid strength calculation
    """
    # System Information
    tick: int
    
    # Personal State
    self_state: AgentState
    
    # Recent Personal Events
    events_since_last: List[Event]
    
    # Direct Communications
    inbox: List[ActionMessage]  # Messages from other agents
    
    # World Context
    world_news: WorldNews
    
    # Mission Context (only for bonded agents)
    mission_status: Optional[MissionStatus]
    
    # Available Actions
    available_actions: List[str]  # ["bond", "raid", "request_spark", "spawn", "reply"]
    
    # Game Rules Context
    spark_cost_per_tick: int = 1
    bond_spark_formula: str = "floor(n + (n-1) × 0.5)"
    raid_strength_formula: str = "age + sparks" 