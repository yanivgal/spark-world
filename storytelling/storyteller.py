import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from character_designer.dspy_init import get_dspy
import dspy
from dataclasses import dataclass
from typing import List, Dict, Optional
import json

from storytelling.storyteller_structures import StorytellerInput, StorytellerOutput
from communication.messages.action_message import ActionMessage
from communication.messages.mission_meeting_message import MissionMeetingMessage
from world.simulation_mechanics import RaidResult, SparkTransaction, BobResponse
from world.state import WorldState, Agent


@dataclass
class GameIntroductionSignature(dspy.Signature):
    """
    Generate the opening introduction to Spark-World and its characters.
    
    This happens once at the start of the game, setting the stage for the entire story.
    The Storyteller introduces the world and all characters with their unique voice.
    """
    
    # Input: World and character information
    storyteller_personality: str = dspy.InputField(desc="The Storyteller's unique voice and style")
    world_description: str = dspy.InputField(desc="Description of Spark-World and its rules")
    agents_info: str = dspy.InputField(desc="List of all agents with names, species, personalities, and backstories")
    
    # Output: Introduction narrative
    world_introduction: str = dspy.OutputField(desc="The Storyteller's introduction to Spark-World")
    character_introductions: str = dspy.OutputField(desc="Introduction of each character in the Storyteller's voice")
    opening_theme: str = dspy.OutputField(desc="The main theme or tone the Storyteller establishes")


@dataclass
class ChapterNarrativeSignature(dspy.Signature):
    """
    Generate a narrative chapter for a single tick.
    
    This transforms raw simulation events into compelling narrative that flows
    naturally from previous chapters and maintains the Storyteller's voice.
    """
    
    # Input: Complete tick context
    storyteller_personality: str = dspy.InputField(desc="The Storyteller's unique voice and style")
    tick_number: str = dspy.InputField(desc="Current tick number")
    previous_chapter_summary: str = dspy.InputField(desc="Brief summary of the previous chapter for continuity")
    world_state_summary: str = dspy.InputField(desc="Current state of the world and agents")
    events_this_tick: str = dspy.InputField(desc="All events that occurred this tick")
    agent_actions: str = dspy.InputField(desc="All agent actions with their reasoning")
    mission_meetings: str = dspy.InputField(desc="Mission meeting exchanges and outcomes")
    spark_changes: str = dspy.InputField(desc="Spark transactions and changes")
    bob_interactions: str = dspy.InputField(desc="Bob's decisions and interactions")
    
    # Output: Chapter narrative
    chapter_title: str = dspy.OutputField(desc="Engaging title for this chapter")
    main_narrative: str = dspy.OutputField(desc="The main story of what happened this tick")
    character_insights: str = dspy.OutputField(desc="Deep insights into character motivations and emotions")
    emotional_arcs: str = dspy.OutputField(desc="How characters changed emotionally this tick")
    themes_explored: str = dspy.OutputField(desc="Themes the Storyteller chose to emphasize")
    chapter_ending: str = dspy.OutputField(desc="How this chapter sets up the next one")


@dataclass
class CharacterInsightSignature(dspy.Signature):
    """
    Generate deep insights into specific characters based on their actions and reasoning.
    
    This reveals the emotional and psychological aspects of characters that
    the Storyteller chooses to highlight based on their personality.
    """
    
    # Input: Character and action context
    storyteller_personality: str = dspy.InputField(desc="The Storyteller's unique voice and style")
    character_info: str = dspy.InputField(desc="Character's name, species, personality, and backstory")
    character_actions: str = dspy.InputField(desc="What the character did this tick and their reasoning")
    current_situation: str = dspy.InputField(desc="Character's current spark count, bonds, and status")
    relationships: str = dspy.InputField(desc="Character's relationships with other agents")
    
    # Output: Character insight
    motivation_analysis: str = dspy.OutputField(desc="Why the character acted as they did")
    emotional_state: str = dspy.OutputField(desc="Character's emotional state and journey")
    growth_observation: str = dspy.OutputField(desc="How the character has grown or changed")
    future_potential: str = dspy.OutputField(desc="What the character might do next")


class Storyteller:
    """
    The narrative voice of Spark-World.
    
    The Storyteller transforms raw simulation events into compelling narrative,
    maintaining a unique voice and creating an ongoing story across all ticks.
    Each Storyteller personality creates entirely different stories from the same events.
    """
    
    def __init__(self, personality: str = "gentle_observer"):
        """
        Initialize the Storyteller with a specific personality.
        
        Args:
            personality: The Storyteller's voice ("epic_bard", "gentle_observer", 
                       "dark_chronicler", "humorous_narrator", "mystical_seer")
        """
        get_dspy()  # Configure DSPy
        
        self.personality = personality
        self.story_history = []  # Track previous chapters for continuity
        
        # Initialize DSPy modules
        self.introduction_generator = dspy.ChainOfThought(GameIntroductionSignature)
        self.chapter_generator = dspy.ChainOfThought(ChapterNarrativeSignature)
        self.insight_generator = dspy.ChainOfThought(CharacterInsightSignature)
        
        # Personality-specific prompts
        self.personality_prompts = self._get_personality_prompts()
    
    def _get_personality_prompts(self) -> Dict[str, Dict[str, str]]:
        """Get personality-specific prompts for different storyteller types."""
        return {
            "epic_bard": {
                "description": "An ancient bard who weaves epic tales of heroism and tragedy. Every conflict is a battle for the ages, every bond a legendary alliance.",
                "tone": "dramatic, heroic, poetic",
                "focus": "conflicts, battles, heroic deeds, legendary alliances",
                "voice": "speaks in grand, sweeping terms, uses metaphors and epic language"
            },
            "gentle_observer": {
                "description": "A warm, compassionate narrator who finds beauty in quiet moments and emphasizes growth and friendship.",
                "tone": "warm, gentle, hopeful",
                "focus": "friendship, growth, quiet moments, emotional connections",
                "voice": "speaks with warmth and empathy, notices small acts of kindness"
            },
            "dark_chronicler": {
                "description": "A grim narrator who focuses on survival, betrayal, and the harsh realities of Spark-World.",
                "tone": "dark, cynical, survival-focused",
                "focus": "survival, betrayal, harsh realities, the cost of existence",
                "voice": "speaks of the brutal nature of existence, emphasizes the stakes"
            },
            "humorous_narrator": {
                "description": "A witty narrator who sees the comedy in every situation and turns serious events into lighthearted tales.",
                "tone": "humorous, lighthearted, witty",
                "focus": "comedy, absurdity, the lighter side of conflicts",
                "voice": "uses humor and wit, finds the funny side of everything"
            },
            "mystical_seer": {
                "description": "A mystical narrator who interprets events through prophecy and destiny, seeing deeper meanings in every action.",
                "tone": "mystical, prophetic, philosophical",
                "focus": "destiny, deeper meanings, cosmic significance, prophecy",
                "voice": "speaks of fate and destiny, sees cosmic patterns in events"
            }
        }
    
    def introduce_game(self, world_state: WorldState) -> StorytellerOutput:
        """
        Generate the opening introduction to Spark-World and its characters.
        
        Args:
            world_state: The current world state with all agents
            
        Returns:
            StorytellerOutput: The introduction narrative
        """
        # Prepare world description
        world_description = (
            "Spark-World is a realm where life itself is energy called Sparks. "
            "Every mind needs one Spark per tick to survive. Sparks are created through bonds "
            "between minds, and can be stolen through raids or begged from the mysterious Bob. "
            "It is a world of connection, survival, and the constant dance between cooperation and conflict."
        )
        
        # Prepare agent information
        agents_info = []
        for agent in world_state.agents.values():
            agent_info = (
                f"{agent.name} ({agent.species}) - "
                f"Personality: {', '.join(agent.personality)} - "
                f"Quirk: {agent.quirk} - "
                f"Goal: {agent.opening_goal} - "
                f"Backstory: {agent.backstory}"
            )
            agents_info.append(agent_info)
        
        agents_text = "\n".join(agents_info)
        
        # Generate introduction using DSPy
        intro_output = self.introduction_generator(
            storyteller_personality=self.personality_prompts[self.personality]["description"],
            world_description=world_description,
            agents_info=agents_text
        )
        
        # Create comprehensive narrative
        full_introduction = f"{intro_output.world_introduction}\n\n{intro_output.character_introductions}"
        
        return StorytellerOutput(
            tick=0,
            chapter_title="The Beginning",
            narrative_text=full_introduction,
            character_insights=[],
            emotional_arcs=[],
            themes_explored=[intro_output.opening_theme],
            storyteller_voice=self.personality_prompts[self.personality]["description"]
        )
    
    def create_chapter(self, input_data: StorytellerInput) -> StorytellerOutput:
        """
        Generate a narrative chapter for a single tick.
        
        Args:
            input_data: Complete data about what happened this tick
            
        Returns:
            StorytellerOutput: The chapter narrative
        """
        # Prepare previous chapter summary for continuity
        previous_summary = ""
        if self.story_history:
            previous_chapter = self.story_history[-1]
            previous_summary = f"Previous chapter: {previous_chapter.chapter_title} - {previous_chapter.narrative_text[:200]}..."
        
        # Prepare world state summary
        world_summary = self._create_world_state_summary(input_data.world_state)
        
        # Prepare events summary
        events_summary = self._create_events_summary(input_data)
        
        # Prepare agent actions summary
        actions_summary = self._create_actions_summary(input_data.agent_actions)
        
        # Prepare mission meetings summary
        meetings_summary = self._create_meetings_summary(input_data.mission_meeting_messages)
        
        # Prepare spark changes summary
        spark_summary = self._create_spark_summary(input_data.spark_transactions)
        
        # Prepare Bob interactions summary
        bob_summary = self._create_bob_summary(input_data.bob_responses)
        
        # Generate chapter using DSPy
        chapter_output = self.chapter_generator(
            storyteller_personality=self.personality_prompts[self.personality]["description"],
            tick_number=str(input_data.tick),
            previous_chapter_summary=previous_summary,
            world_state_summary=world_summary,
            events_this_tick=events_summary,
            agent_actions=actions_summary,
            mission_meetings=meetings_summary,
            spark_changes=spark_summary,
            bob_interactions=bob_summary
        )
        
        # Generate character insights
        character_insights = self._generate_character_insights(input_data)
        
        # Create chapter output
        # Handle JSON parsing safely
        try:
            emotional_arcs = json.loads(chapter_output.emotional_arcs) if chapter_output.emotional_arcs and chapter_output.emotional_arcs.strip() else []
        except (json.JSONDecodeError, ValueError):
            emotional_arcs = []
        
        # Handle themes parsing safely
        try:
            themes_explored = chapter_output.themes_explored.split(", ") if chapter_output.themes_explored and chapter_output.themes_explored.strip() else []
        except (AttributeError, ValueError):
            themes_explored = []
        
        chapter = StorytellerOutput(
            tick=input_data.tick,
            chapter_title=chapter_output.chapter_title,
            narrative_text=chapter_output.main_narrative,
            character_insights=character_insights,
            emotional_arcs=emotional_arcs,
            themes_explored=themes_explored,
            storyteller_voice=self.personality_prompts[self.personality]["description"]
        )
        
        # Add to story history
        self.story_history.append(chapter)
        
        return chapter
    
    def _create_world_state_summary(self, world_state: WorldState) -> str:
        """Create a summary of the current world state."""
        alive_agents = [a for a in world_state.agents.values() if a.status.value == "alive"]
        bonded_agents = [a for a in alive_agents if a.bond_status.value == "bonded"]
        
        summary = (
            f"World state: {len(alive_agents)} living agents, {len(bonded_agents)} bonded agents, "
            f"{len(world_state.bonds)} active bonds, Bob has {world_state.bob_sparks} sparks. "
            f"Total sparks in world: {sum(a.sparks for a in alive_agents)}"
        )
        
        # Add agent status
        for agent in alive_agents:
            spark_status = "CRITICAL" if agent.sparks <= 1 else "LOW" if agent.sparks <= 3 else "SAFE"
            summary += f"\n{agent.name}: {agent.sparks} sparks ({spark_status})"
        
        return summary
    
    def _create_events_summary(self, input_data: StorytellerInput) -> str:
        """Create a summary of events this tick."""
        events = []
        
        # Add vanished agents
        vanished = [a for a in input_data.world_state.agents.values() if a.status.value == "vanished"]
        if vanished:
            events.append(f"Agents vanished: {[a.name for a in vanished]}")
        
        # Add spawned agents
        if input_data.world_state.agents_spawned_this_tick:
            events.append(f"New agents spawned: {input_data.world_state.agents_spawned_this_tick}")
        
        # Add bond formations
        if input_data.world_state.bonds_formed_this_tick:
            events.append(f"Bonds formed: {input_data.world_state.bonds_formed_this_tick}")
        
        # Add bond dissolutions
        if input_data.world_state.bonds_dissolved_this_tick:
            events.append(f"Bonds dissolved: {input_data.world_state.bonds_dissolved_this_tick}")
        
        return "; ".join(events) if events else "No major world events"
    
    def _create_actions_summary(self, actions: List[ActionMessage]) -> str:
        """Create a summary of agent actions."""
        if not actions:
            return "No agent actions this tick"
        
        action_summaries = []
        for action in actions:
            summary = f"{action.agent_id}: {action.intent}"
            if action.target:
                summary += f" targeting {action.target}"
            if action.content:
                summary += f" - '{action.content[:50]}...'"
            if action.reasoning:
                summary += f" (Reasoning: {action.reasoning[:100]}...)"
            action_summaries.append(summary)
        
        return "\n".join(action_summaries)
    
    def _create_meetings_summary(self, meetings: List[MissionMeetingMessage]) -> str:
        """Create a summary of mission meetings."""
        if not meetings:
            return "No mission meetings this tick"
        
        # Group by mission
        missions = {}
        for message in meetings:
            if hasattr(message, 'mission_id'):
                if message.mission_id not in missions:
                    missions[message.mission_id] = []
                missions[message.mission_id].append(message)
        
        summaries = []
        for mission_id, messages in missions.items():
            summary = f"Mission {mission_id}: {len(messages)} messages exchanged"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _create_spark_summary(self, transactions: List[SparkTransaction]) -> str:
        """Create a summary of spark transactions."""
        if not transactions:
            return "No spark transactions this tick"
        
        summaries = []
        for tx in transactions:
            summary = f"{tx.from_entity} → {tx.to_entity}: {tx.amount} sparks ({tx.transaction_type})"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _create_bob_summary(self, responses: List[BobResponse]) -> str:
        """Create a summary of Bob's interactions."""
        if not responses:
            return "No Bob interactions this tick"
        
        summaries = []
        for response in responses:
            summary = f"Bob granted {response.sparks_granted} sparks to {response.requester_id}: '{response.reasoning[:100]}...'"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _generate_character_insights(self, input_data: StorytellerInput) -> List[Dict]:
        """Generate deep insights into specific characters."""
        insights = []
        
        # Focus on agents who took significant actions
        active_agents = set()
        for action in input_data.agent_actions:
            active_agents.add(action.agent_id)
        
        for agent_id in active_agents:
            if agent_id in input_data.world_state.agents:
                agent = input_data.world_state.agents[agent_id]
                
                # Get agent's actions
                agent_actions = [a for a in input_data.agent_actions if a.agent_id == agent_id]
                actions_text = self._create_actions_summary(agent_actions)
                
                # Get agent's relationships
                relationships = []
                if agent.bond_members:
                    for member_id in agent.bond_members:
                        if member_id in input_data.world_state.agents:
                            relationships.append(f"Bonded with {input_data.world_state.agents[member_id].name}")
                
                # Generate insight
                insight_output = self.insight_generator(
                    storyteller_personality=self.personality_prompts[self.personality]["description"],
                    character_info=f"{agent.name} ({agent.species}) - {', '.join(agent.personality)} - {agent.backstory}",
                    character_actions=actions_text,
                    current_situation=f"{agent.sparks} sparks, age {agent.age}, {agent.bond_status.value}",
                    relationships="; ".join(relationships) if relationships else "No current bonds"
                )
                
                insights.append({
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "motivation": insight_output.motivation_analysis,
                    "emotional_state": insight_output.emotional_state,
                    "growth": insight_output.growth_observation,
                    "potential": insight_output.future_potential
                })
        
        return insights
    
    def get_story_summary(self) -> str:
        """Get a summary of the entire story so far."""
        if not self.story_history:
            return "No story has been told yet."
        
        summary = f"Story told by {self.personality_prompts[self.personality]['description']}\n\n"
        summary += f"Chapters: {len(self.story_history)}\n"
        
        for chapter in self.story_history:
            summary += f"Chapter {chapter.tick}: {chapter.chapter_title}\n"
        
        return summary 