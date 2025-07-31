from dataclasses import dataclass
from typing import List, Dict, Optional
from communication.messages.action_message import ActionMessage
from communication.messages.mission_meeting_message import MissionMeetingMessage
from world.simulation_mechanics import RaidResult, SparkTransaction, BobResponse
from world.state import WorldState, Mission


@dataclass
class AgentChange:
    """Tracks changes to an agent during a tick"""
    agent_id: str
    agent_name: str
    spark_change: int  # Positive for gain, negative for loss
    age_change: int
    status_change: Optional[str] = None  # "alive" -> "vanished" or None
    bond_status_change: Optional[str] = None  # "unbonded" -> "bonded" or None
    bond_members_change: Optional[List[str]] = None


@dataclass
class BondFormationDetail:
    """Detailed information about bond formation"""
    bond_id: str
    member_ids: List[str]
    member_names: List[str]
    leader_id: str
    leader_name: str
    mission_id: Optional[str] = None
    mission_title: Optional[str] = None


@dataclass
class BondDissolutionDetail:
    """Detailed information about bond dissolution"""
    bond_id: str
    member_ids: List[str]
    member_names: List[str]
    reason: str  # Why the bond dissolved


@dataclass
class MissionMeetingSummary:
    """Summary of a mission meeting"""
    mission_id: str
    mission_title: str
    bond_id: str
    leader_id: str
    leader_name: str
    meeting_messages: List[MissionMeetingMessage]
    meeting_flow: List[str]  # ["leader_introduction", "leader_opening", "agent_response", "task_assignment"]
    agent_responses: Dict[str, str]  # agent_id -> response content
    task_assignments: Dict[str, str]  # agent_id -> assigned task


@dataclass
class MissionProgressUpdate:
    """Mission progress update for this tick"""
    mission_id: str
    mission_title: str
    previous_progress: str
    current_progress: str
    progress_change: str
    is_complete: bool
    completion_reasoning: Optional[str] = None


@dataclass
class ActionProcessingResult:
    """Result of processing an agent action"""
    action: ActionMessage
    success: bool
    result_description: str
    spark_impact: int  # How many sparks were gained/lost
    target_affected: Optional[str] = None  # Who was affected by this action


@dataclass
class SparkDistributionDetail:
    """Details about spark distribution within bonds"""
    bond_id: str
    bond_name: str
    total_sparks_generated: int
    distribution_details: List[Dict]  # [{"recipient_id": "agent_001", "recipient_name": "Zyphra", "sparks_received": 2}]


@dataclass
class AgentVanishingContext:
    """Context for agent vanishing"""
    agent_id: str
    agent_name: str
    final_sparks: int
    final_age: int
    vanishing_reason: str  # "upkeep_cost", "raid_failure", etc.
    bond_members: List[str] = None  # Who they were bonded with
    mission_involvement: Optional[str] = None  # Mission they were part of


@dataclass
class BobContext:
    """Complete context for Bob's decisions"""
    bob_sparks_before: int
    bob_sparks_after: int
    bob_sparks_gained: int
    requests_received: List[Dict]  # Full context of each request
    decisions_made: List[BobResponse]
    reasoning_patterns: List[str]  # Patterns in Bob's decision-making


@dataclass
class TickStatistics:
    """Summary statistics for this tick"""
    total_sparks_minted: int
    total_sparks_lost: int
    total_sparks_distributed: int
    total_raids_attempted: int
    total_raids_successful: int
    total_bonds_active: int
    total_missions_active: int
    total_agents_alive: int
    total_agents_vanished: int
    total_agents_spawned: int


@dataclass
class StorytellerInput:
    """
    Complete data sent to the Storyteller for narrative generation.
    
    The Storyteller receives this at the end of each tick and transforms
    raw simulation events into compelling narrative. The same events told
    by different Storytellers become entirely different stories.
    
    Attributes:
        tick: Current tick number
        storyteller_personality: The Storyteller's unique voice and style
        world_state: Complete world state at end of tick
        agent_actions: All ActionMessages from agents (including private reasoning)
        raid_results: All RaidResult outcomes
        spark_transactions: All SparkTransaction records
        bob_responses: All BobResponse decisions
        mission_meeting_messages: All MissionMeetingMessage exchanges
        events_this_tick: All events that occurred this tick
        is_game_start: Whether this is the initial world introduction
        
        world_state_before: WorldState  # State at start of tick
        world_state_after: WorldState   # State at end of tick
        
        # Agent changes this tick
        agent_changes: List[AgentChange]  # All agent changes during tick
        
        # Bond formation and dissolution details
        bonds_formed_details: List[BondFormationDetail]  # Complete bond formation info
        bonds_dissolved_details: List[BondDissolutionDetail]  # Complete bond dissolution info
        
        # Mission details
        active_missions: List[Mission]  # All active missions with full details
        mission_meeting_summaries: List[MissionMeetingSummary]  # Summarized meeting content
        mission_progress_updates: List[MissionProgressUpdate]   # Mission progress changes
        
        # Action processing results
        action_processing_results: List[ActionProcessingResult]  # What happened to each action
        failed_actions: List[ActionProcessingResult]  # Actions that failed and why
        
        # Spark flow details
        spark_distribution_details: List[SparkDistributionDetail]  # Who got what from bonds
        spark_minting_details: List[Dict]  # Bond spark generation details
        
        # Agent vanishing context
        vanished_agents_context: List[AgentVanishingContext]  # Why agents vanished, their final state
        
        # Bob's full context
        bob_context: BobContext  # Bob's complete decision-making context
        
        # World statistics
        tick_statistics: TickStatistics  # Summary statistics for this tick
    """
    # Current structure (keep these)
    tick: int
    storyteller_personality: str  # "blip", "eloa", "krunch"
    world_state: WorldState
    agent_actions: List[ActionMessage]
    raid_results: List[RaidResult]
    spark_transactions: List[SparkTransaction]
    bob_responses: List[BobResponse]
    mission_meeting_messages: List[MissionMeetingMessage]
    events_this_tick: List[Dict]
    is_game_start: bool = False
    
    # Enhanced data for rich storytelling
    world_state_before: Optional[WorldState] = None  # State at start of tick
    world_state_after: Optional[WorldState] = None   # State at end of tick
    
    # Agent changes this tick
    agent_changes: Optional[List[AgentChange]] = None  # All agent changes during tick
    
    # Bond formation and dissolution details
    bonds_formed_details: Optional[List[BondFormationDetail]] = None  # Complete bond formation info
    bonds_dissolved_details: Optional[List[BondDissolutionDetail]] = None  # Complete bond dissolution info
    
    # Mission details
    active_missions: Optional[List[Mission]] = None  # All active missions with full details
    mission_meeting_summaries: Optional[List[MissionMeetingSummary]] = None  # Summarized meeting content
    mission_progress_updates: Optional[List[MissionProgressUpdate]] = None   # Mission progress changes
    
    # Action processing results
    action_processing_results: Optional[List[ActionProcessingResult]] = None  # What happened to each action
    failed_actions: Optional[List[ActionProcessingResult]] = None  # Actions that failed and why
    
    # Spark flow details
    spark_distribution_details: Optional[List[SparkDistributionDetail]] = None  # Who got what from bonds
    spark_minting_details: Optional[List[Dict]] = None  # Bond spark generation details
    
    # Agent vanishing context
    vanished_agents_context: Optional[List[AgentVanishingContext]] = None  # Why agents vanished, their final state
    
    # Bob's full context
    bob_context: Optional[BobContext] = None  # Bob's complete decision-making context
    
    # World statistics
    tick_statistics: Optional[TickStatistics] = None  # Summary statistics for this tick


@dataclass
class StorytellerOutput:
    """
    Narrative output from the Storyteller.
    
    The Storyteller transforms raw simulation data into compelling narrative
    that captures the emotional and strategic arcs of Spark-World.
    
    Attributes:
        tick: The tick this narrative covers
        chapter_title: Title for this narrative chapter
        narrative_text: The main narrative content
        character_insights: Deeper insights into agent motivations and emotions
        emotional_arcs: The emotional journey of agents this tick
        themes_explored: Themes the Storyteller chose to emphasize
        storyteller_voice: How the Storyteller's personality influenced the telling
    """
    tick: int
    chapter_title: str
    narrative_text: str
    character_insights: List[Dict]  # Insights about specific agents
    emotional_arcs: List[Dict]  # Emotional journeys this tick
    themes_explored: List[str]  # Themes the Storyteller emphasized
    storyteller_voice: str  # How personality influenced the telling 