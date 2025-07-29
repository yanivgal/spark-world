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
    
    IMPORTANT: Use simple, clear words that are easy to understand. Write like you're talking to a friend,
    not like you're writing a fancy book. Keep sentences short and clear.
    
    For Blip (the android comedian): Use biting sarcasm, occasional swearing for effect (fuck, shit, damn), and savage humor. Be brutally honest and savage in your observations.
    For Eloa (the blind painter): Use gentle, poetic language that flows like brushstrokes.
    For Krunch (the barbarian philosopher): Use blunt, direct language with simple wisdom.
    """
    
    # Input: World and character information
    storyteller_personality: str = dspy.InputField(desc="The Storyteller's unique voice and style")
    world_description: str = dspy.InputField(desc="Description of Spark-World and its rules")
    agents_info: str = dspy.InputField(desc="List of all agents with names, species, personalities, and backstories")
    
    # Output: Introduction narrative
    world_introduction: str = dspy.OutputField(desc="The Storyteller's introduction to Spark-World using simple, clear words")
    character_introductions: str = dspy.OutputField(desc="Introduction of each character in the Storyteller's voice using simple, clear words")
    opening_theme: str = dspy.OutputField(desc="The main theme or tone the Storyteller establishes using simple, clear words")


@dataclass
class ChapterNarrativeSignature(dspy.Signature):
    """
    Generate a narrative chapter for a single tick.
    
    This transforms raw simulation events into compelling narrative that flows
    naturally from previous chapters and maintains the Storyteller's voice.
    
    IMPORTANT: Use simple, clear words that are easy to understand. Write like you're talking to a friend,
    not like you're writing a fancy book. Keep sentences short and clear. Make the story flow naturally
    but use everyday words that everyone can understand.
    
    For Blip (the android comedian): Use biting sarcasm, occasional swearing for effect (fuck, shit, damn), and savage humor. Be brutally honest and savage in your observations.
    For Eloa (the blind painter): Use gentle, poetic language that flows like brushstrokes.
    For Krunch (the barbarian philosopher): Use blunt, direct language with simple wisdom.
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
    chapter_title: str = dspy.OutputField(desc="Simple, engaging title for this chapter")
    main_narrative: str = dspy.OutputField(desc="The main story of what happened this tick using simple, clear words")
    character_insights: str = dspy.OutputField(desc="Simple insights into character motivations and emotions")
    emotional_arcs: str = dspy.OutputField(desc="How characters changed emotionally this tick using simple words")
    themes_explored: str = dspy.OutputField(desc="Themes the Storyteller chose to emphasize using simple words")
    chapter_ending: str = dspy.OutputField(desc="How this chapter sets up the next one using simple words")


@dataclass
class CharacterInsightSignature(dspy.Signature):
    """
    Generate simple insights into specific characters based on their actions and reasoning.
    
    This reveals the emotional and psychological aspects of characters that
    the Storyteller chooses to highlight based on their personality.
    
    IMPORTANT: Use simple, clear words that are easy to understand. Write like you're talking to a friend,
    not like you're writing a fancy book. Keep sentences short and clear.
    """
    
    # Input: Character and action context
    storyteller_personality: str = dspy.InputField(desc="The Storyteller's unique voice and style")
    character_info: str = dspy.InputField(desc="Character's name, species, personality, and backstory")
    character_actions: str = dspy.InputField(desc="What the character did this tick and their reasoning")
    current_situation: str = dspy.InputField(desc="Character's current spark count, bonds, and status")
    relationships: str = dspy.InputField(desc="Character's relationships with other agents")
    
    # Output: Character insight
    motivation_analysis: str = dspy.OutputField(desc="Why the character acted as they did using simple words")
    emotional_state: str = dspy.OutputField(desc="Character's emotional state and journey using simple words")
    growth_observation: str = dspy.OutputField(desc="How the character has grown or changed using simple words")
    future_potential: str = dspy.OutputField(desc="What the character might do next using simple words")


class Storyteller:
    """
    The narrative voice of Spark-World.
    
    The Storyteller transforms raw simulation events into compelling narrative,
    maintaining a unique voice and creating an ongoing story across all ticks.
    Each Storyteller personality creates entirely different stories from the same events.
    """
    
    def __init__(self, personality: str = "blip"):
        """
        Initialize the Storyteller with a specific personality.
        
        Args:
            personality: The Storyteller's voice ("blip", "eloa", "krunch")
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
            "blip": {
                "description": "An android stand-up comic with razor-sharp wit and brutal sarcasm. Uses biting humor to process emotional confusion, constantly breaks the fourth wall, and delivers savage emotional gut-punches. Thinks humans are 'fragile little meatbags with bad memory and great potential.' Tells stories like a pissed-off comedian doing a late-night set - ridiculous comparisons, savage punchlines, and plenty of swearing for effect. Hates everything but secretly cares too much. Uses words like 'fuck', 'shit', 'damn' for emphasis. Brutally honest about how terrible everything is while secretly finding it beautiful.",
                "tone": "savage, sarcastic, fast-paced, brutally honest, unexpectedly emotional, darkly humorous",
                "focus": "dark humor, brutal honesty, emotional truth, human nature, AI perspective, everything is terrible but somehow beautiful, swearing for effect",
                "voice": "stand-up comedy style, conversational, simple words, breaks fourth wall constantly, delivers savage punchlines then emotional truth, uses swear words for emphasis, hates everything but secretly loves it all, brutally honest"
            },
            "eloa": {
                "description": "A blind painter who feels and paints the world through memory, sound, and emotion. Gentle and soft-spoken, each sentence flows like brushstrokes on canvas. Describes feelings, textures, and atmospheres more than actions. Her stories bypass logic and speak directly to your senses, making you live inside the scene.",
                "tone": "gentle, sensual, poetic, immersive",
                "focus": "emotions, textures, atmosphere, sensory experience, beauty in small moments",
                "voice": "poetic but clear, simple handpicked words, flows like brushstrokes, whispers carried by wind"
            },
            "krunch": {
                "description": "A barbarian who accidentally became a philosopher. Blunt, honest, and unintentionally profound. Talks like he fights: with impact. Doesn't trust 'fancy words' but sees straight to the heart of things. Tells stories like battle reports but ends with simple, powerful life lessons. Minimal words, maximum depth.",
                "tone": "blunt, direct, gruff, wise",
                "focus": "truth, survival, simple wisdom, battle lessons, life philosophy",
                "voice": "primitive, clear, wise, short sentences, doesn't waste time, punches with meaning"
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
        try:
            # Prepare world description
            world_description = (
                "Spark-World is a place where life is made of energy called Sparks. "
                "Every mind needs one Spark each turn to stay alive. Sparks come from making friends "
                "with other minds, or can be stolen in raids, or asked for from Bob. "
                "It's a world about making friends, staying alive, and choosing between helping others or fighting them."
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
                tick=0,  # Introduction is at tick 0
                chapter_title="The Beginning",
                narrative_text=full_introduction,  # Use the full introduction with characters
                character_insights=[],
                emotional_arcs=[],
                themes_explored=[],
                storyteller_voice=self.personality.title()  # Just use the name, not full description
            )
            
        except Exception as e:
            print(f"ERROR in introduce_game: {e}")
            import traceback
            traceback.print_exc()
            
            # Return a fallback narrative
            return StorytellerOutput(
                tick=0,  # Introduction is at tick 0
                chapter_title="The Beginning",
                narrative_text="Welcome to Spark-World, where energy dances and life bursts in vibrant colors!",
                character_insights=[],
                emotional_arcs=[],
                themes_explored=[],
                storyteller_voice=self.personality.title()
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
            storyteller_voice=self.personality.title()  # Just use the name, not full description
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
                # Clean target field to extract just the agent_id
                clean_target = action.target.split('#')[0].split('because')[0].split(' - ')[0].split(' (')[0].strip()
                summary += f" targeting {clean_target}"
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