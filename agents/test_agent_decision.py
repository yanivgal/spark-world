#!/usr/bin/env python3
"""
Test script for the Agent Decision Module.

This script tests the agent decision-making process with various scenarios
to ensure the module works correctly and produces expected outputs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize DSPy first
from ai_client import get_dspy
get_dspy()  # This will configure DSPy with the LLM

from agents.agent_decision import AgentDecisionModule
from communication.messages.observation_packet import (
    ObservationPacket, AgentState, AgentStatus, BondStatus, 
    Event, WorldNews, MissionStatus
)
from communication.messages.action_message import ActionMessage


def create_test_observation_packet(scenario: str = "basic") -> ObservationPacket:
    """
    Create test observation packets for different scenarios.
    
    Args:
        scenario: Type of scenario to test ("basic", "bonded", "mission", "events")
        
    Returns:
        ObservationPacket: Test observation packet
    """
    
    # Base agent state
    base_agent_state = AgentState(
        agent_id="test_agent_001",
        name="Whiskers the Brave",
        species="saber-toothed house-cat",
        personality=["proud", "protective", "noble"],
        quirk="Always sits with perfect posture",
        ability="Can sense danger from 3 rooms away",
        age=5,
        sparks=8,
        status=AgentStatus.ALIVE,
        bond_status=BondStatus.UNBONDED,
        bond_members=[]
    )
    
    # Base world news
    base_world_news = WorldNews(
        tick=10,
        total_agents=15,
        total_bonds=3,
        agents_vanished_this_tick=["old_agent_123"],
        agents_spawned_this_tick=["new_agent_456"],
        bonds_formed_this_tick=["bond_789"],
        bonds_dissolved_this_tick=[],
        public_agent_info={
            "test_agent_001": {"name": "Whiskers the Brave", "species": "saber-toothed house-cat", "realm": "Living Room"},
            "other_agent_002": {"name": "Shadow", "species": "mystical raven", "realm": "Attic"},
            "other_agent_003": {"name": "Bubbles", "species": "golden fish", "realm": "Aquarium"},
            "new_agent_456": {"name": "Echo", "species": "whispering fern", "realm": "Garden"}
        }
    )
    
    if scenario == "basic":
        # Basic scenario - unbonded agent with no recent events
        return ObservationPacket(
            tick=10,
            self_state=base_agent_state,
            events_since_last=[],
            inbox=[],
            world_news=base_world_news,
            mission_status=None,
            available_actions=["bond", "raid", "request_spark", "spawn", "reply"]
        )
    
    elif scenario == "bonded":
        # Bonded agent scenario
        bonded_agent_state = AgentState(
            agent_id="test_agent_001",
            name="Whiskers the Brave",
            species="saber-toothed house-cat",
            personality=["proud", "protective", "noble"],
            quirk="Always sits with perfect posture",
            ability="Can sense danger from 3 rooms away",
            age=5,
            sparks=12,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.BONDED,
            bond_members=["test_agent_001", "other_agent_002"]
        )
        
        return ObservationPacket(
            tick=10,
            self_state=bonded_agent_state,
            events_since_last=[
                Event(
                    event_type="bond_formed",
                    description="You formed a bond with Shadow the mystical raven",
                    spark_change=0,
                    source_agent="other_agent_002",
                    additional_data={"bond_id": "bond_123"}
                ),
                Event(
                    event_type="spark_gained",
                    description="Your bond generated 3 sparks",
                    spark_change=3,
                    source_agent=None,
                    additional_data={"bond_id": "bond_123"}
                )
            ],
            inbox=[
                ActionMessage(
                    agent_id="other_agent_002",
                    intent="reply",
                    target="test_agent_001",
                    content="I'm glad we bonded, Whiskers! Together we're stronger.",
                    reasoning="Expressing gratitude for the bond formation"
                )
            ],
            world_news=base_world_news,
            mission_status=None,
            available_actions=["bond", "raid", "request_spark", "spawn", "reply"]
        )
    
    elif scenario == "mission":
        # Mission scenario - bonded agent with active mission
        mission_agent_state = AgentState(
            agent_id="test_agent_001",
            name="Whiskers the Brave",
            species="saber-toothed house-cat",
            personality=["proud", "protective", "noble"],
            quirk="Always sits with perfect posture",
            ability="Can sense danger from 3 rooms away",
            age=5,
            sparks=15,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.LEADER,
            bond_members=["test_agent_001", "other_agent_002", "other_agent_003"]
        )
        
        mission_status = MissionStatus(
            mission_id="mission_456",
            mission_title="Defend the Living Room",
            mission_description="Protect the living room from mysterious intruders",
            mission_goal="Successfully defend the area for 5 ticks",
            current_progress="2/5 ticks completed",
            leader_id="test_agent_001",
            assigned_tasks={
                "test_agent_001": "Patrol the main entrance",
                "other_agent_002": "Watch from the shadows",
                "other_agent_003": "Create diversion if needed"
            },
            mission_complete=False
        )
        
        return ObservationPacket(
            tick=10,
            self_state=mission_agent_state,
            events_since_last=[
                Event(
                    event_type="spark_gained",
                    description="Your bond generated 5 sparks",
                    spark_change=5,
                    source_agent=None,
                    additional_data={"bond_id": "bond_123"}
                )
            ],
            inbox=[],
            world_news=base_world_news,
            mission_status=mission_status,
            available_actions=["bond", "raid", "request_spark", "spawn", "reply"]
        )
    
    elif scenario == "events":
        # Agent with various events
        return ObservationPacket(
            tick=10,
            self_state=base_agent_state,
            events_since_last=[
                Event(
                    event_type="raid_attack",
                    description="You were attacked by Shadow but successfully defended",
                    spark_change=1,
                    source_agent="other_agent_002",
                    additional_data={"raid_success": False, "defender_strength": 13, "attacker_strength": 8}
                ),
                Event(
                    event_type="spark_lost",
                    description="You lost 1 spark to upkeep",
                    spark_change=-1,
                    source_agent=None,
                    additional_data={"reason": "upkeep"}
                )
            ],
            inbox=[
                ActionMessage(
                    agent_id="other_agent_002",
                    intent="raid",
                    target="test_agent_001",
                    content="I need your sparks!",
                    reasoning="Desperate for sparks to survive"
                )
            ],
            world_news=base_world_news,
            mission_status=None,
            available_actions=["bond", "raid", "request_spark", "spawn", "reply"]
        )
    
    else:
        raise ValueError(f"Unknown scenario: {scenario}")


def print_agent_world_understanding(observation_packet: ObservationPacket):
    """
    Print a beautiful, flowing explanation of how the agent understands the world.
    
    Args:
        observation_packet: The agent's observation packet
    """
    agent = observation_packet.self_state
    
    print(f"\n{'🌌' * 20} AGENT'S WORLD UNDERSTANDING {'🌌' * 20}")
    
    # Agent Identity
    print(f"\n🎭 WHO AM I?")
    print(f"   I am {agent.name}, a {agent.species} from the {observation_packet.world_news.public_agent_info[agent.agent_id]['realm']}.")
    print(f"   My personality: {', '.join(agent.personality)}")
    print(f"   My unique quirk: {agent.quirk}")
    print(f"   My special ability: {agent.ability}")
    print(f"   I am {agent.age} ticks old and currently have {agent.sparks} sparks.")
    
    # World Context
    print(f"\n🌍 WHAT'S HAPPENING IN THE WORLD?")
    print(f"   We are at tick {observation_packet.tick} of the simulation.")
    print(f"   There are {observation_packet.world_news.total_agents} agents alive in the world.")
    print(f"   {observation_packet.world_news.total_bonds} bonds exist, creating life-energy together.")
    
    # Recent World Changes
    if observation_packet.world_news.agents_vanished_this_tick:
        print(f"   This tick, {len(observation_packet.world_news.agents_vanished_this_tick)} agent(s) vanished from existence.")
    if observation_packet.world_news.agents_spawned_this_tick:
        print(f"   This tick, {len(observation_packet.world_news.agents_spawned_this_tick)} new agent(s) came into being.")
    if observation_packet.world_news.bonds_formed_this_tick:
        print(f"   This tick, {len(observation_packet.world_news.bonds_formed_this_tick)} new bond(s) were formed.")
    if observation_packet.world_news.bonds_dissolved_this_tick:
        print(f"   This tick, {len(observation_packet.world_news.bonds_dissolved_this_tick)} bond(s) dissolved due to member vanishing.")
    
    # Other Agents
    print(f"\n👥 WHO ELSE IS HERE?")
    for agent_id, info in observation_packet.world_news.public_agent_info.items():
        if agent_id != observation_packet.self_state.agent_id:
            print(f"   • {info['name']} ({info['species']}) - from the {info['realm']}")
    
    # Bond Status
    print(f"\n🤝 MY BOND STATUS")
    if agent.bond_status == BondStatus.UNBONDED:
        print(f"   I am currently unbonded - I must survive on my own or seek companionship.")
    elif agent.bond_status == BondStatus.BONDED:
        print(f"   I am bonded with: {', '.join([observation_packet.world_news.public_agent_info.get(member, {}).get('name', member) for member in agent.bond_members if member != agent.agent_id])}")
        print(f"   Together, we generate sparks using the formula: {observation_packet.bond_spark_formula}")
    elif agent.bond_status == BondStatus.LEADER:
        print(f"   I am the leader of a bond with: {', '.join([observation_packet.world_news.public_agent_info.get(member, {}).get('name', member) for member in agent.bond_members if member != agent.agent_id])}")
        print(f"   As leader, I can assign tasks and guide our collective efforts.")
    
    # Mission Status
    if observation_packet.mission_status:
        print(f"\n🎯 MY MISSION")
        print(f"   Mission: {observation_packet.mission_status.mission_title}")
        print(f"   Goal: {observation_packet.mission_status.mission_goal}")
        print(f"   Progress: {observation_packet.mission_status.current_progress}")
        print(f"   My assigned task: {observation_packet.mission_status.assigned_tasks.get(agent.agent_id, 'No specific task')}")
    
    # Recent Personal Events
    if observation_packet.events_since_last:
        print(f"\n⚡ WHAT HAPPENED TO ME RECENTLY?")
        for event in observation_packet.events_since_last:
            print(f"   • {event.description}")
            if event.spark_change != 0:
                change_text = f"+{event.spark_change}" if event.spark_change > 0 else f"{event.spark_change}"
                print(f"     (Spark change: {change_text})")
    
    # Messages from Others
    if observation_packet.inbox:
        print(f"\n💬 MESSAGES I RECEIVED")
        for msg in observation_packet.inbox:
            sender_name = observation_packet.world_news.public_agent_info.get(msg.agent_id, {}).get('name', msg.agent_id)
            print(f"   • {sender_name}: \"{msg.content}\"")
    
    # Available Actions and Rules
    print(f"\n🎮 WHAT CAN I DO THIS TICK?")
    print(f"   I can choose ONE action from the following options:")
    
    for action in observation_packet.available_actions:
        if action == "bond":
            print(f"   • BOND - Invite another unbonded agent to form a bond with me")
        elif action == "raid":
            print(f"   • RAID - Risk 1 spark to steal 1-5 sparks from another agent")
            print(f"     (My strength: {agent.age + agent.sparks}, Raid success depends on strength comparison)")
        elif action == "request_spark":
            print(f"   • REQUEST SPARK - Ask Bob for a donation of 1-5 sparks")
            print(f"     (Bob's generosity is finite but renewable)")
        elif action == "spawn":
            if agent.bond_status == BondStatus.UNBONDED:
                print(f"   • SPAWN - Create a new agent (REQUIRES BOND - I cannot do this while unbonded)")
            else:
                print(f"   • SPAWN - Pay 5 sparks to create a new agent who joins my bond")
        elif action == "reply":
            print(f"   • REPLY - Respond to a specific message from another agent")
    
    # Survival Rules
    print(f"\n⚡ SURVIVAL RULES I UNDERSTAND")
    print(f"   • I lose {observation_packet.spark_cost_per_tick} spark per tick just to exist")
    print(f"   • If I reach 0 sparks, I vanish instantly")
    print(f"   • My current strength for raids: {agent.age + agent.sparks} (age + sparks)")
    print(f"   • Bond spark formula: {observation_packet.bond_spark_formula}")
    print(f"   • Raid strength formula: {observation_packet.raid_strength_formula}")
    
    # Strategic Considerations
    print(f"\n🧠 STRATEGIC CONSIDERATIONS")
    print(f"   • I have {agent.sparks} sparks - enough to survive {agent.sparks} more ticks without income")
    if agent.bond_status == BondStatus.UNBONDED:
        print(f"   • I am unbonded - I need to find allies or rely on Bob's generosity")
        print(f"   • Forming a bond would give me steady spark income")
    else:
        bond_size = len(agent.bond_members)
        expected_sparks = int(bond_size + (bond_size - 1) * 0.5)
        print(f"   • My bond of {bond_size} members generates ~{expected_sparks} sparks per tick")
    
    print(f"\n{'🌌' * 20} END OF WORLD UNDERSTANDING {'🌌' * 20}")


def test_agent_decision(scenario: str = "basic"):
    """
    Test the agent decision module with a specific scenario.
    
    Args:
        scenario: Scenario to test
    """
    print(f"\n{'='*80}")
    print(f"🌌 TESTING SCENARIO: {scenario.upper()} 🌌")
    print(f"{'='*80}")
    
    # Create test observation packet
    observation_packet = create_test_observation_packet(scenario)
    
    # Show agent's world understanding
    print_agent_world_understanding(observation_packet)
    
    # Initialize agent decision module
    print(f"\n{'='*50}")
    print("🤖 PROCESSING AGENT DECISION...")
    print(f"{'='*50}")
    
    try:
        agent_decision_module = AgentDecisionModule()
        action_message = agent_decision_module.decide_action(
            agent_id=observation_packet.self_state.agent_id,
            observation_packet=observation_packet
        )
        
        print(f"\n🎯 AGENT DECISION RESULTS:")
        print(f"{'='*50}")
        print(f"Action: {action_message.intent.upper()}")
        if action_message.target:
            target_name = observation_packet.world_news.public_agent_info.get(action_message.target, {}).get('name', action_message.target)
            print(f"Target: {target_name}")
        else:
            print(f"Target: None")
        print(f"Message: \"{action_message.content}\"")
        print(f"\n💭 Reasoning: {action_message.reasoning}")
        
        return action_message
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all test scenarios."""
    print("🌌 SPARK-WORLD AGENT DECISION MODULE TEST 🌌")
    print("=" * 80)
    
    scenarios = ["basic", "bonded", "mission", "events"]
    
    results = {}
    for scenario in scenarios:
        try:
            result = test_agent_decision(scenario)
            results[scenario] = result
        except Exception as e:
            print(f"Failed to test scenario {scenario}: {e}")
            results[scenario] = None
    
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    for scenario, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{scenario.upper()}: {status}")
        if result:
            target_name = "None" if not result.target else result.target
            print(f"  Action: {result.intent} -> {target_name}")
    
    print(f"\n{'='*80}")
    print("🎉 TEST COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    main() 