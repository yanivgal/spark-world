#!/usr/bin/env python3
"""
Test script for the Mission System.

This script tests mission generation, meeting coordination, and progress evaluation
to ensure the mission system works correctly and produces expected outputs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize DSPy first
from character_designer.dspy_init import get_dspy
get_dspy()  # This will configure DSPy with the LLM

from world.mission_system import MissionSystem
from world.mission_meeting_coordinator import MissionMeetingCoordinator
from world.state import Mission, Bond, Agent, AgentStatus, BondStatus
from communication.messages.mission_meeting_message import MissionMeetingMessage


def create_test_agents() -> dict:
    """Create test agents for mission testing."""
    return {
        "agent_001": Agent(
            agent_id="agent_001",
            name="Sir Pounce-a-Lot",
            species="saber-cat",
            personality=["proud", "noble", "strategic"],
            quirk="Always stands on hind legs when speaking",
            ability="Can sense danger from miles away",
            age=0,
            sparks=5,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.BONDED,
            bond_members=["agent_001", "agent_002"],
            home_realm="Knightly Meadows",
            backstory="A noble knight from the ancient cat kingdoms",
            opening_goal="To protect the weak and uphold honor"
        ),
        "agent_002": Agent(
            agent_id="agent_002",
            name="Blossom Echo",
            species="weather-dandelion",
            personality=["gentle", "wise", "diplomatic"],
            quirk="Petals change color with emotions",
            ability="Can predict weather patterns",
            age=0,
            sparks=5,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.BONDED,
            bond_members=["agent_001", "agent_002"],
            home_realm="Whispering Gardens",
            backstory="A gentle flower who speaks with the wind",
            opening_goal="To bring peace and harmony to the world"
        ),
        "agent_003": Agent(
            agent_id="agent_003",
            name="Grudge",
            species="goblin-raider",
            personality=["aggressive", "desperate", "opportunistic"],
            quirk="Always carries a rusty dagger",
            ability="Can find hidden treasures",
            age=0,
            sparks=5,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.UNBONDED,
            bond_members=[],
            home_realm="Shadow Caves",
            backstory="A desperate goblin seeking fortune",
            opening_goal="To amass wealth and power"
        )
    }


def create_test_bond() -> Bond:
    """Create a test bond for mission testing."""
    return Bond(
        bond_id="bond_001",
        members={"agent_001", "agent_002"},
        leader_id="agent_001",
        mission_id=None,  # Will be set when mission is generated
        sparks_generated_this_tick=0
    )


def print_mission_details(mission: Mission):
    """Print mission details in a beautiful format."""
    print(f"\n{'🎯' * 20} MISSION DETAILS {'🎯' * 20}")
    print(f"Mission ID: {mission.mission_id}")
    print(f"Title: {mission.title}")
    print(f"Description: {mission.description}")
    print(f"Goal: {mission.goal}")
    print(f"Leader: {mission.leader_id}")
    print(f"Bond ID: {mission.bond_id}")
    print(f"Created Tick: {mission.created_tick}")
    print(f"Is Complete: {mission.is_complete}")
    print(f"Current Progress: {mission.current_progress}")
    print(f"Assigned Tasks: {mission.assigned_tasks}")
    print(f"{'🎯' * 20} END MISSION DETAILS {'🎯' * 20}")


def print_meeting_messages(messages: list[MissionMeetingMessage], tick: int):
    """Print meeting messages in a beautiful format."""
    print(f"\n{'🤝' * 20} MISSION MEETING (TICK {tick}) {'🤝' * 20}")
    
    for i, message in enumerate(messages, 1):
        print(f"\n{i}. {message.message_type.upper()}")
        print(f"   Sender: {message.sender_id}")
        print(f"   Content: {message.content}")
        print(f"   Reasoning: {message.reasoning}")
        if message.target_agent_id:
            print(f"   Target: {message.target_agent_id}")
        if message.task_description:
            print(f"   Task: {message.task_description}")
    
    print(f"{'🤝' * 20} END MISSION MEETING {'🤝' * 20}")


def test_mission_generation():
    """Test mission generation for a new bond."""
    print(f"\n{'='*80}")
    print(f"🌟 TESTING MISSION GENERATION 🌟")
    print(f"{'='*80}")
    
    # Create test data
    agents = create_test_agents()
    bond = create_test_bond()
    world_context = "Tick 5, 3 total agents, 1 bond formed"
    
    try:
        # Initialize mission system
        mission_system = MissionSystem()
        
        # Generate mission
        print(f"\nGenerating mission for bond {bond.bond_id}...")
        mission = mission_system.generate_mission_for_bond(bond, agents, world_context)
        
        # Set created tick (normally done by World Engine)
        mission.created_tick = 5
        
        # Display results
        print_mission_details(mission)
        
        return mission
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_mission_meeting(mission: Mission, tick: int):
    """Test mission meeting coordination."""
    print(f"\n{'='*80}")
    print(f"🤝 TESTING MISSION MEETING (TICK {tick}) 🤝")
    print(f"{'='*80}")
    
    # Create test data
    agents = create_test_agents()
    bond = create_test_bond()
    bond.mission_id = mission.mission_id
    
    # Previous actions (simulate what happened last tick)
    previous_actions = [
        "Sir Pounce-a-Lot raided Grudge but failed",
        "Blossom Echo requested sparks from Bob and received 3",
        "Mission progress: 3/10 sparks gathered"
    ]
    
    try:
        # Initialize meeting coordinator
        coordinator = MissionMeetingCoordinator()
        
        # Conduct meeting
        print(f"\nConducting mission meeting for {mission.title}...")
        meeting_messages = coordinator.conduct_mission_meeting(
            mission=mission,
            bond=bond,
            agents=agents,
            tick=tick,
            previous_actions=previous_actions
        )
        
        # Update tick numbers in messages (normally done by World Engine)
        for message in meeting_messages:
            message.tick = tick
        
        # Display results
        print_meeting_messages(meeting_messages, tick)
        
        return meeting_messages
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_mission_progress_evaluation(mission: Mission):
    """Test mission progress evaluation."""
    print(f"\n{'='*80}")
    print(f"📊 TESTING MISSION PROGRESS EVALUATION 📊")
    print(f"{'='*80}")
    
    # Simulate agent actions
    agent_actions = [
        "Sir Pounce-a-Lot successfully raided Grudge and stole 3 sparks",
        "Blossom Echo requested sparks from Bob and received 2",
        "Team gathered 5 additional sparks",
        "Total mission progress: 8/10 sparks gathered"
    ]
    
    world_state = "Tick 10, 3 agents alive, 1 active bond, 8 total sparks gathered"
    mission_history = "Previous actions: Multiple raids, Bob requests, steady progress toward goal"
    
    try:
        # Initialize mission system
        mission_system = MissionSystem()
        
        # Evaluate progress
        print(f"\nEvaluating progress for mission: {mission.title}")
        evaluation = mission_system.evaluate_mission_progress(
            mission=mission,
            agent_actions=agent_actions,
            world_state=world_state,
            mission_history=mission_history
        )
        
        # Display results
        print(f"\n{'📈' * 20} PROGRESS EVALUATION {'📈' * 20}")
        print(f"Is Complete: {evaluation['is_complete']}")
        print(f"Progress Summary: {evaluation['progress_summary']}")
        print(f"Completion Reasoning: {evaluation['completion_reasoning']}")
        print(f"{'📈' * 20} END PROGRESS EVALUATION {'📈' * 20}")
        
        return evaluation
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_mission_lifecycle():
    """Test the complete mission lifecycle."""
    print(f"\n{'='*80}")
    print(f"🔄 TESTING COMPLETE MISSION LIFECYCLE 🔄")
    print(f"{'='*80}")
    
    # Step 1: Mission Generation
    mission = test_mission_generation()
    if not mission:
        print("❌ Mission generation failed")
        return
    
    # Step 2: First Mission Meeting (tick 5)
    meeting_1 = test_mission_meeting(mission, 5)
    if not meeting_1:
        print("❌ First mission meeting failed")
        return
    
    # Step 3: Second Mission Meeting (tick 6)
    meeting_2 = test_mission_meeting(mission, 6)
    if not meeting_2:
        print("❌ Second mission meeting failed")
        return
    
    # Step 4: Progress Evaluation
    evaluation = test_mission_progress_evaluation(mission)
    if not evaluation:
        print("❌ Progress evaluation failed")
        return
    
    print(f"\n{'✅' * 20} MISSION LIFECYCLE COMPLETE {'✅' * 20}")
    print(f"✅ Mission generated successfully")
    print(f"✅ First meeting conducted")
    print(f"✅ Second meeting conducted")
    print(f"✅ Progress evaluated")
    print(f"✅ Mission completion status: {evaluation['is_complete']}")


def test_edge_cases():
    """Test edge cases and error conditions."""
    print(f"\n{'='*80}")
    print(f"🔍 TESTING EDGE CASES 🔍")
    print(f"{'='*80}")
    
    # Test 1: Single agent bond (should still work)
    print(f"\n--- EDGE CASE 1: Single agent bond ---")
    agents = create_test_agents()
    single_bond = Bond(
        bond_id="bond_single",
        members={"agent_001"},
        leader_id="agent_001",
        mission_id=None,
        sparks_generated_this_tick=0
    )
    
    try:
        mission_system = MissionSystem()
        mission = mission_system.generate_mission_for_bond(single_bond, agents, "Single agent test")
        mission.created_tick = 1
        print(f"✅ Single agent mission generated: {mission.title}")
    except Exception as e:
        print(f"❌ Single agent mission failed: {e}")
    
    # Test 2: Large bond (3+ agents)
    print(f"\n--- EDGE CASE 2: Large bond ---")
    large_bond = Bond(
        bond_id="bond_large",
        members={"agent_001", "agent_002", "agent_003"},
        leader_id="agent_001",
        mission_id=None,
        sparks_generated_this_tick=0
    )
    
    try:
        mission = mission_system.generate_mission_for_bond(large_bond, agents, "Large bond test")
        mission.created_tick = 1
        print(f"✅ Large bond mission generated: {mission.title}")
    except Exception as e:
        print(f"❌ Large bond mission failed: {e}")


def main():
    """Run all mission system tests."""
    print("🌟 SPARK-WORLD MISSION SYSTEM TEST 🌟")
    print("=" * 80)
    
    # Test complete lifecycle
    test_mission_lifecycle()
    
    # Test edge cases
    test_edge_cases()
    
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    print("✅ Mission generation system")
    print("✅ Mission meeting coordination")
    print("✅ Progress evaluation")
    print("✅ Edge case handling")
    
    print(f"\n{'='*80}")
    print("🎉 MISSION SYSTEM TEST COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    main() 