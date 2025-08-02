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
    home_realm: str
    backstory: str
    opening_goal: str
    speech_style: str


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
    bob_sparks: int  # Bob's current spark count


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
    team_members: Optional[List[str]] = None  # Names of team members
    recent_messages: Optional[List[str]] = None  # Recent meeting messages


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
        previous_tick_events: Events from previous tick that affected this agent
        previous_tick_actions_targeting_me: Actions from previous tick targeting this agent
        previous_tick_my_actions: Actions this agent took in previous tick
        previous_tick_bond_requests: Bond requests received in previous tick
        previous_tick_messages: Messages received in previous tick
        previous_tick_raids: Raids involving this agent in previous tick
        my_action_history: All actions this agent has taken (for reasoning)
        actions_targeting_me: All actions where this agent was the target (for reasoning)
    """
    # System Information
    tick: int
    
    # Personal State
    self_state: AgentState
    
    # Recent Personal Events
    events_since_last: List[Event]
    
    # Direct Communications
    inbox: List[ActionMessage]  # Messages from other agents (from previous tick, same source as historical context)
    
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
    
    # Previous Tick Context (for immediate decision making)
    previous_tick_events: List[Event] = None
    previous_tick_actions_targeting_me: List[ActionMessage] = None
    previous_tick_my_actions: List[ActionMessage] = None
    previous_tick_bond_requests: List[ActionMessage] = None
    previous_tick_messages: List[ActionMessage] = None
    previous_tick_raids: List[ActionMessage] = None
    
    # Full History (for reasoning and context)
    my_action_history: List[ActionMessage] = None
    actions_targeting_me: List[ActionMessage] = None
    
    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.events_since_last is None:
            self.events_since_last = []
        if self.previous_tick_events is None:
            self.previous_tick_events = []
        if self.previous_tick_actions_targeting_me is None:
            self.previous_tick_actions_targeting_me = []
        if self.previous_tick_my_actions is None:
            self.previous_tick_my_actions = []
        if self.previous_tick_bond_requests is None:
            self.previous_tick_bond_requests = []
        if self.previous_tick_messages is None:
            self.previous_tick_messages = []
        if self.previous_tick_raids is None:
            self.previous_tick_raids = []
        if self.my_action_history is None:
            self.my_action_history = []
        if self.actions_targeting_me is None:
            self.actions_targeting_me = [] 