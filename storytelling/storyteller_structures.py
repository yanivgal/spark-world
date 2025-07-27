from dataclasses import dataclass
from typing import List, Dict
from communication.messages.action_message import ActionMessage
from communication.messages.mission_meeting_message import MissionMeetingMessage
from world.simulation_mechanics import RaidResult, SparkTransaction, BobResponse
from world.state import WorldState


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
    """
    tick: int
    storyteller_personality: str  # "epic_bard", "gentle_observer", "dark_chronicler", etc.
    world_state: WorldState
    agent_actions: List[ActionMessage]
    raid_results: List[RaidResult]
    spark_transactions: List[SparkTransaction]
    bob_responses: List[BobResponse]
    mission_meeting_messages: List[MissionMeetingMessage]
    events_this_tick: List[Dict]
    is_game_start: bool = False


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