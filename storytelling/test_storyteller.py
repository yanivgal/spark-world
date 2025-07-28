#!/usr/bin/env python3
"""
Test script for the Storyteller module.
Tests different personalities and chapter generation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storytelling.storyteller import Storyteller
from storytelling.storyteller_structures import StorytellerInput
from world.state import WorldState, Agent, AgentStatus, BondStatus
from communication.messages.action_message import ActionMessage
import dspy

# Configure DSPy
dspy.settings.configure(lm="gpt-4o-mini")

def test_storyteller_personalities():
    """Test different storyteller personalities."""
    print("="*80)
    print("📖 TESTING STORYTELLER PERSONALITIES")
    print("="*80)
    
    # Create a simple world state for testing
    world_state = WorldState()
    world_state.tick = 1
    
    # Add some test agents
    agent1 = Agent(
        agent_id="agent_001",
        name="Zyphra",
        species="Celestial Wisp",
        personality=["mysterious", "playful", "ethereal"],
        quirk="Leaves a trail of shimmering light",
        ability="Dream restoration",
        age=0,
        sparks=5,
        status=AgentStatus.ALIVE,
        bond_status=BondStatus.UNBONDED,
        bond_members=[],
        home_realm="The Luminous Veil",
        backstory="Once a guardian of lost dreams, now seeks to restore hope",
        opening_goal="To find and restore a lost dream"
    )
    
    agent2 = Agent(
        agent_id="agent_002",
        name="Fynara",
        species="Luminous Wisp",
        personality=["playful", "mysterious", "curious"],
        quirk="Leaves a trail of sparkling light",
        ability="Light guidance",
        age=0,
        sparks=5,
        status=AgentStatus.ALIVE,
        bond_status=BondStatus.UNBONDED,
        bond_members=[],
        home_realm="The Glimmering Vale",
        backstory="A guardian of lost dreams seeking to restore forgotten hopes",
        opening_goal="To revive a forgotten dreamer"
    )
    
    world_state.agents["agent_001"] = agent1
    world_state.agents["agent_002"] = agent2
    
    # Test different personalities
    personalities = ["gentle_observer", "epic_bard", "dark_chronicler", "humorous_narrator", "mystical_seer"]
    
    for personality in personalities:
        print(f"\n{'='*60}")
        print(f"🎭 TESTING {personality.upper()}")
        print(f"{'='*60}")
        
        storyteller = Storyteller(personality=personality)
        
        # Test introduction
        print(f"\n📚 INTRODUCTION:")
        intro = storyteller.introduce_game(world_state)
        print(f"   Title: {intro.chapter_title}")
        print(f"   Voice: {intro.storyteller_voice}")
        print(f"   Themes: {intro.themes_explored}")
        print(f"   Narrative: {intro.narrative_text[:200]}...")
        
        # Test chapter generation
        print(f"\n📖 CHAPTER GENERATION:")
        input_data = StorytellerInput(
            tick=2,
            storyteller_personality=personality,
            world_state=world_state,
            agent_actions=[
                ActionMessage(
                    agent_id="agent_001",
                    intent="bond",
                    target="agent_002",
                    content="Hello Fynara! Would you like to bond?",
                    reasoning="I sense a connection and want to create sparks together"
                )
            ],
            raid_results=[],
            spark_transactions=[],
            bob_responses=[],
            mission_meeting_messages=[],
            events_this_tick=[],
            is_game_start=False
        )
        
        chapter = storyteller.create_chapter(input_data)
        print(f"   Title: {chapter.chapter_title}")
        print(f"   Narrative: {chapter.narrative_text[:200]}...")
        print(f"   Themes: {chapter.themes_explored}")

def test_story_continuity():
    """Test that the Storyteller maintains story continuity across chapters."""
    print(f"\n{'='*80}")
    print("📚 TESTING STORY CONTINUITY")
    print(f"{'='*80}")
    
    storyteller = Storyteller(personality="gentle_observer")
    
    # Create a simple world state
    world_state = WorldState()
    world_state.tick = 1
    
    agent = Agent(
        agent_id="agent_001",
        name="Zyphra",
        species="Celestial Wisp",
        personality=["mysterious", "playful"],
        quirk="Leaves a trail of shimmering light",
        ability="Dream restoration",
        age=0,
        sparks=5,
        status=AgentStatus.ALIVE,
        bond_status=BondStatus.UNBONDED,
        bond_members=[],
        home_realm="The Luminous Veil",
        backstory="A guardian of lost dreams",
        opening_goal="To restore hope"
    )
    world_state.agents["agent_001"] = agent
    
    # Generate introduction
    intro = storyteller.introduce_game(world_state)
    print(f"📚 Introduction: {intro.chapter_title}")
    
    # Generate multiple chapters
    for tick in range(2, 5):
        input_data = StorytellerInput(
            tick=tick,
            storyteller_personality="gentle_observer",
            world_state=world_state,
            agent_actions=[],
            raid_results=[],
            spark_transactions=[],
            bob_responses=[],
            mission_meeting_messages=[],
            events_this_tick=[],
            is_game_start=False
        )
        
        chapter = storyteller.create_chapter(input_data)
        print(f"📖 Chapter {tick}: {chapter.chapter_title}")
        print(f"   {chapter.narrative_text[:100]}...")
    
    # Show story summary
    print(f"\n📋 STORY SUMMARY:")
    print(storyteller.get_story_summary())

if __name__ == "__main__":
    test_storyteller_personalities()
    test_story_continuity() 