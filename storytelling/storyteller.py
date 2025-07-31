import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_client import get_dspy
import dspy
from dataclasses import dataclass
from typing import List, Dict, Optional
import json

from storytelling.storyteller_structures import StorytellerInput, StorytellerOutput, ActionProcessingResult
from communication.messages.action_message import ActionMessage
from communication.messages.mission_meeting_message import MissionMeetingMessage
from world.simulation_mechanics import RaidResult, SparkTransaction, BobResponse
from world.state import WorldState, Agent


@dataclass
class GameIntroductionSignature(dspy.Signature):
    """
    Generate the opening introduction to Spark-World and its characters.
    
    This happens once at the start of the game, setting the stage for the entire story.
    The Storyteller introduces themselves, explains the world, and introduces all characters 
    in their unique voice - like a friendly guide welcoming someone to a new universe.
    
    Think of it like the robot in Hitchhiker's Guide to the Galaxy - welcoming, informative,
    and completely in character. The storyteller should feel like they're personally 
    introducing a newcomer to this world.
    
    IMPORTANT: Use simple, clear words that are easy to understand. Write like you're talking to a friend,
    not like you're writing a fancy book. Keep sentences short and clear.
    
    For Blip (the android comedian): Use biting sarcasm, occasional swearing for effect (fuck, shit, damn), and savage humor. Be brutally honest and savage in your observations.
    For Eloa (the blind painter): Use gentle, poetic language that flows like brushstrokes.
    For Krunch (the barbarian philosopher): Use blunt, direct language with simple wisdom.
    """
    
    # Input: World and character information
    storyteller_personality: str = dspy.InputField(desc="The Storyteller's unique voice and style")
    storyteller_name: str = dspy.InputField(desc="The Storyteller's name and title")
    agents_info: str = dspy.InputField(desc="List of all agents with names, species, personalities, and backstories")
    
    # Output: Complete introduction narrative
    complete_introduction: str = dspy.OutputField(desc="A complete, flowing introduction where the storyteller introduces themselves, explains Spark-World, and introduces all characters in their unique voice. Should feel like a personal welcome to a newcomer.")


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
    
    # Enhanced data for rich storytelling (replaces old basic summaries)
    agent_changes: str = dspy.InputField(desc="Detailed changes to agents this tick (sparks, age, status, bonds)")
    bond_formations: str = dspy.InputField(desc="Detailed bond formation information with member names and missions")
    bond_dissolutions: str = dspy.InputField(desc="Detailed bond dissolution information with reasons")
    mission_details: str = dspy.InputField(desc="Active missions and their progress updates")
    mission_meeting_summaries: str = dspy.InputField(desc="Detailed mission meeting summaries with agent responses and task assignments")
    action_results: str = dspy.InputField(desc="Results of processing agent actions (success/failure, spark impact)")
    spark_distribution: str = dspy.InputField(desc="Detailed spark distribution within bonds")
    vanished_agents: str = dspy.InputField(desc="Context for agents that vanished (final state, bond members, missions)")
    bob_context: str = dspy.InputField(desc="Complete context for Bob's decisions (requests, reasoning patterns)")
    tick_statistics: str = dspy.InputField(desc="Summary statistics for this tick")
    
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
            # Get storyteller name and title
            storyteller_names = {
                "blip": "🤖 BLIP - The Savage Comedian",
                "eloa": "🎨 ELOA - The Gentle Poet", 
                "krunch": "⚔️ KRUNCH - The Wise Warrior"
            }
            storyteller_name = storyteller_names.get(self.personality, self.personality.title())
            
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
            
            # Generate complete introduction using DSPy - let the storyteller generate everything
            intro_output = self.introduction_generator(
                storyteller_personality=self.personality_prompts[self.personality]["description"],
                storyteller_name=storyteller_name,
                agents_info=agents_text
            )
            
            # Use the complete introduction generated by the storyteller
            full_introduction = intro_output.complete_introduction
            
            return StorytellerOutput(
                tick=1,  # Introduction is at tick 1
                chapter_title="The Beginning",
                narrative_text=full_introduction,  # Use the complete storyteller-generated introduction
                character_insights=[],
                emotional_arcs=[],
                themes_explored=[],
                storyteller_voice=self.personality.title()
            )
            
        except Exception as e:
            print(f"ERROR in introduce_game: {e}")
            import traceback
            traceback.print_exc()
            
            # Return a fallback narrative
            return StorytellerOutput(
                tick=1,  # Introduction is at tick 1
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
        
        # Prepare enhanced data summaries (replaces old basic summaries)
        agent_changes_summary = self._create_agent_changes_summary(input_data.agent_changes)
        bond_formations_summary = self._create_bond_formations_summary(input_data.bonds_formed_details)
        bond_dissolutions_summary = self._create_bond_dissolutions_summary(input_data.bonds_dissolved_details)
        mission_details_summary = self._create_mission_details_summary(input_data.active_missions)
        mission_meeting_summaries = self._create_mission_meeting_summaries(input_data.mission_meeting_summaries)
        action_results_summary = self._create_action_results_summary(input_data.action_processing_results)
        spark_distribution_summary = self._create_spark_distribution_summary(input_data.spark_distribution_details)
        vanished_agents_summary = self._create_vanished_agents_summary(input_data.vanished_agents_context)
        bob_context_summary = self._create_bob_context_summary(input_data.bob_context)
        tick_statistics_summary = self._create_tick_statistics_summary(input_data.tick_statistics)
        
        # Generate chapter using DSPy
        chapter_output = self.chapter_generator(
            storyteller_personality=self.personality_prompts[self.personality]["description"],
            tick_number=str(input_data.tick),
            previous_chapter_summary=previous_summary,
            world_state_summary=world_summary,
            agent_changes=agent_changes_summary,
            bond_formations=bond_formations_summary,
            bond_dissolutions=bond_dissolutions_summary,
            mission_details=mission_details_summary,
            mission_meeting_summaries=mission_meeting_summaries,
            action_results=action_results_summary,
            spark_distribution=spark_distribution_summary,
            vanished_agents=vanished_agents_summary,
            bob_context=bob_context_summary,
            tick_statistics=tick_statistics_summary
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
    
    def _create_agent_changes_summary(self, agent_changes) -> str:
        """Create a summary of agent changes this tick."""
        if not agent_changes:
            return "No agent changes this tick"
        
        summaries = []
        for change in agent_changes:
            summary = f"{change.agent_name}: "
            changes = []
            
            if change.spark_change != 0:
                changes.append(f"sparks {change.spark_change:+d}")
            if change.age_change != 0:
                changes.append(f"age +{change.age_change}")
            if change.status_change:
                changes.append(f"status {change.status_change}")
            if change.bond_status_change:
                changes.append(f"bond {change.bond_status_change}")
            
            summary += ", ".join(changes)
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _create_bond_formations_summary(self, bonds_formed_details) -> str:
        """Create a summary of bond formations this tick."""
        if not bonds_formed_details:
            return "No bonds formed this tick"
        
        summaries = []
        for bond in bonds_formed_details:
            member_names = ", ".join(bond.member_names)
            summary = f"Bond formed: {member_names} (leader: {bond.leader_name})"
            if bond.mission_title:
                summary += f" - Mission: {bond.mission_title}"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _create_bond_dissolutions_summary(self, bonds_dissolved_details) -> str:
        """Create a summary of bond dissolutions this tick."""
        if not bonds_dissolved_details:
            return "No bonds dissolved this tick"
        
        summaries = []
        for bond in bonds_dissolved_details:
            member_names = ", ".join(bond.member_names)
            summary = f"Bond dissolved: {member_names} - {bond.reason}"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _create_mission_details_summary(self, active_missions) -> str:
        """Create a summary of active missions."""
        if not active_missions:
            return "No active missions"
        
        summaries = []
        for mission in active_missions:
            summary = f"Mission '{mission.title}': {mission.current_progress}"
            if mission.is_complete:
                summary += " (COMPLETED)"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _create_mission_meeting_summaries(self, mission_meeting_summaries) -> str:
        """Create a summary of mission meeting summaries."""
        if not mission_meeting_summaries:
            return "No mission meetings this tick"
        
        summaries = []
        for meeting in mission_meeting_summaries:
            summary = f"Mission '{meeting.mission_title}' meeting: "
            summary += f"{len(meeting.meeting_messages)} messages, "
            summary += f"{len(meeting.agent_responses)} agent responses, "
            summary += f"{len(meeting.task_assignments)} task assignments"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _create_action_results_summary(self, action_processing_results) -> str:
        """Create a summary of action processing results."""
        if not action_processing_results:
            return "No action results this tick"
        
        summaries = []
        for result in action_processing_results:
            summary = f"{result.action.agent_id}: {result.action.intent} - "
            summary += f"{'SUCCESS' if result.success else 'FAILED'} - "
            summary += f"{result.result_description}"
            if result.spark_impact != 0:
                summary += f" (spark impact: {result.spark_impact:+d})"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _create_spark_distribution_summary(self, spark_distribution_details) -> str:
        """Create a summary of spark distribution details."""
        if not spark_distribution_details:
            return "No spark distribution this tick"
        
        summaries = []
        for distribution in spark_distribution_details:
            summary = f"{distribution.bond_name}: {distribution.total_sparks_generated} sparks generated, "
            recipient_summaries = []
            for detail in distribution.distribution_details:
                recipient_summaries.append(f"{detail['recipient_name']} (+{detail['sparks_received']})")
            summary += "distributed to " + ", ".join(recipient_summaries)
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _create_vanished_agents_summary(self, vanished_agents_context) -> str:
        """Create a summary of vanished agents context."""
        if not vanished_agents_context:
            return "No agents vanished this tick"
        
        summaries = []
        for context in vanished_agents_context:
            summary = f"{context.agent_name} vanished: "
            summary += f"final sparks {context.final_sparks}, age {context.final_age}, "
            summary += f"reason: {context.vanishing_reason}"
            if context.bond_members:
                summary += f", was bonded with {', '.join(context.bond_members)}"
            if context.mission_involvement:
                summary += f", was part of mission '{context.mission_involvement}'"
            summaries.append(summary)
        
        return "; ".join(summaries)
    
    def _create_bob_context_summary(self, bob_context) -> str:
        """Create a summary of Bob's context."""
        if not bob_context:
            return "No Bob interactions this tick"
        
        summary = f"Bob's sparks: {bob_context.bob_sparks_before} -> {bob_context.bob_sparks_after} "
        summary += f"(gained {bob_context.bob_sparks_gained})"
        
        if bob_context.requests_received:
            summary += f"; {len(bob_context.requests_received)} requests received"
        
        if bob_context.decisions_made:
            summary += f"; {len(bob_context.decisions_made)} decisions made"
        
        if bob_context.reasoning_patterns:
            summary += f"; reasoning patterns: {', '.join(bob_context.reasoning_patterns[:3])}"
        
        return summary
    
    def _create_tick_statistics_summary(self, tick_statistics) -> str:
        """Create a summary of tick statistics."""
        if not tick_statistics:
            return "No statistics available"
        
        summary = f"Tick stats: "
        summary += f"{tick_statistics.total_sparks_minted} minted, "
        summary += f"{tick_statistics.total_sparks_lost} lost, "
        summary += f"{tick_statistics.total_sparks_distributed} distributed, "
        summary += f"{tick_statistics.total_raids_attempted} raids ({tick_statistics.total_raids_successful} successful), "
        summary += f"{tick_statistics.total_bonds_active} active bonds, "
        summary += f"{tick_statistics.total_missions_active} active missions, "
        summary += f"{tick_statistics.total_agents_alive} living agents, "
        summary += f"{tick_statistics.total_agents_vanished} vanished, "
        summary += f"{tick_statistics.total_agents_spawned} spawned"
        
        return summary 

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
                
                # Get agent's actions and results
                agent_actions = [a for a in input_data.agent_actions if a.agent_id == agent_id]
                agent_results = []
                if input_data.action_processing_results:
                    agent_results = [r for r in input_data.action_processing_results if r.action.agent_id == agent_id]
                
                # Create action summary using enhanced data
                actions_text = self._create_action_summary_for_insights(agent_actions, agent_results)
                
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
    
    def _create_action_summary_for_insights(self, actions: List[ActionMessage], results: List[ActionProcessingResult]) -> str:
        """Create a summary of agent actions for character insights."""
        if not actions:
            return "No actions taken this tick"
        
        summaries = []
        for action in actions:
            summary = f"{action.intent}"
            if action.target:
                # Clean target field to extract just the agent_id
                clean_target = action.target.split('#')[0].split('because')[0].split(' - ')[0].split(' (')[0].strip()
                summary += f" targeting {clean_target}"
            if action.content:
                summary += f" - '{action.content[:50]}...'"
            if action.reasoning:
                summary += f" (Reasoning: {action.reasoning[:100]}...)"
            
            # Add result if available
            for result in results:
                if result.action == action:
                    summary += f" - {'SUCCESS' if result.success else 'FAILED'}: {result.result_description}"
                    break
            
            summaries.append(summary)
        
        return "\n".join(summaries)
    
    def get_story_summary(self) -> str:
        """Get a summary of the entire story so far."""
        if not self.story_history:
            return "No story has been told yet."
        
        summary = f"Story told by {self.personality_prompts[self.personality]['description']}\n\n"
        summary += f"Chapters: {len(self.story_history)}\n"
        
        for chapter in self.story_history:
            summary += f"Chapter {chapter.tick}: {chapter.chapter_title}\n"
        
        return summary 