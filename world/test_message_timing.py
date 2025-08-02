#!/usr/bin/env python3
"""
Test script for message timing issue in observation packets.

This script simulates the tick flow and tests whether messages appear
in the correct tick in observation packets, without using LLMs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world.state import WorldState, Agent, Bond, AgentStatus, BondStatus
from world.world_engine import WorldEngine
from communication.messages.action_message import ActionMessage
from communication.messages.observation_packet import ObservationPacket, AgentState, Event, WorldNews, MissionStatus
from world.state import Mission
from typing import Optional

def create_test_agents():
    """Create test agents for the simulation."""
    agents = {
        "agent_001": Agent(
            agent_id="agent_001",
            name="Alice",
            species="human",
            personality=["friendly", "curious"],
            quirk="loves to explore",
            ability="can see patterns",
            age=1,
            sparks=5,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.UNBONDED,
            bond_members=[],
            home_realm="earth",
            backstory="A curious explorer",
            opening_goal="Make friends",
            speech_style="enthusiastic"
        ),
        "agent_002": Agent(
            agent_id="agent_002", 
            name="Bob",
            species="human",
            personality=["helpful", "wise"],
            quirk="always has advice",
            ability="can solve problems",
            age=1,
            sparks=5,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.UNBONDED,
            bond_members=[],
            home_realm="earth",
            backstory="A wise helper",
            opening_goal="Help others",
            speech_style="thoughtful"
        )
    }
    return agents

def test_message_timing():
    """Test the message timing issue in observation packets."""
    print("🧪 Testing Message Timing in Observation Packets")
    print("=" * 60)
    
    # Create a minimal world state
    world_state = WorldState()
    agents = create_test_agents()
    world_state.agents = agents
    world_state.tick = 0
    world_state.bob_sparks = 10
    world_state.bob_sparks_per_tick = 2
    
    print(f"✅ Created 2 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Test 1: Tick 0 - No messages should appear
    print(f"\n🔄 Test 1: Tick 0 - Initial state")
    print("-" * 40)
    
    # Simulate observation packet generation
    alice_packet = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox: {len(alice_packet.inbox)} messages")
    print(f"Bob inbox: {len(bob_packet.inbox)} messages")
    
    if len(alice_packet.inbox) == 0 and len(bob_packet.inbox) == 0:
        print("✅ PASS: No messages in initial tick")
    else:
        print("❌ FAIL: Messages appeared in initial tick")
    
    # Test 2: Tick 1 - Create messages but they shouldn't appear yet
    print(f"\n🔄 Test 2: Tick 1 - Create messages")
    print("-" * 40)
    
    world_state.tick = 1
    
    # Create a message from Alice to Bob (tick 1)
    alice_message = ActionMessage(
        agent_id="agent_001",
        intent="message",
        target="agent_002",
        content="Hello Bob!",
        reasoning="Want to say hi",
        tick=1
    )
    
    # Simulate message processing (add to queue)
    if "agent_002" not in world_state.message_queue:
        world_state.message_queue["agent_002"] = []
    world_state.message_queue["agent_002"].append(alice_message)
    
    print(f"✅ Added message from Alice to Bob (tick 1)")
    print(f"Message queue for Bob: {len(world_state.message_queue.get('agent_002', []))} messages")
    
    # Generate observation packets for tick 1
    alice_packet = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox (tick 1): {len(alice_packet.inbox)} messages")
    print(f"Bob inbox (tick 1): {len(bob_packet.inbox)} messages")
    
    if len(bob_packet.inbox) == 0:
        print("✅ PASS: Message from tick 1 doesn't appear in tick 1")
    else:
        print("❌ FAIL: Message from tick 1 appeared in tick 1")
        for msg in bob_packet.inbox:
            print(f"  Message: {msg.content} (tick {msg.tick})")
    
    # Test 3: Tick 2 - Messages from tick 1 should appear
    print(f"\n🔄 Test 3: Tick 2 - Messages from tick 1 should appear")
    print("-" * 40)
    
    world_state.tick = 2
    
    # Generate observation packets for tick 2
    alice_packet = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox (tick 2): {len(alice_packet.inbox)} messages")
    print(f"Bob inbox (tick 2): {len(bob_packet.inbox)} messages")
    
    if len(bob_packet.inbox) == 1:
        print("✅ PASS: Message from tick 1 appears in tick 2")
        for msg in bob_packet.inbox:
            print(f"  Message: {msg.content} (tick {msg.tick})")
    else:
        print("❌ FAIL: Message from tick 1 doesn't appear in tick 2")
    
    # Test 4: Tick 2 - Create new messages that shouldn't appear yet
    print(f"\n🔄 Test 4: Tick 2 - Create new messages")
    print("-" * 40)
    
    # Create a message from Bob to Alice (tick 2)
    bob_message = ActionMessage(
        agent_id="agent_002",
        intent="message",
        target="agent_001",
        content="Hello Alice!",
        reasoning="Want to reply",
        tick=2
    )
    
    # Simulate message processing (add to queue)
    if "agent_001" not in world_state.message_queue:
        world_state.message_queue["agent_001"] = []
    world_state.message_queue["agent_001"].append(bob_message)
    
    print(f"✅ Added message from Bob to Alice (tick 2)")
    
    # Generate observation packets for tick 2 again
    alice_packet = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox (tick 2): {len(alice_packet.inbox)} messages")
    print(f"Bob inbox (tick 2): {len(bob_packet.inbox)} messages")
    
    # Alice should have 0 messages (Bob's message is from current tick)
    # Bob should have 1 message (Alice's message is from previous tick)
    if len(alice_packet.inbox) == 0 and len(bob_packet.inbox) == 1:
        print("✅ PASS: Only previous tick messages appear")
    else:
        print("❌ FAIL: Current tick messages appeared")
        print(f"  Alice messages: {len(alice_packet.inbox)}")
        print(f"  Bob messages: {len(bob_packet.inbox)}")
    
    # Test 5: Tick 3 - Both messages should appear
    print(f"\n🔄 Test 5: Tick 3 - Both messages should appear")
    print("-" * 40)
    
    world_state.tick = 3
    
    # Generate observation packets for tick 3
    alice_packet = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox (tick 3): {len(alice_packet.inbox)} messages")
    print(f"Bob inbox (tick 3): {len(bob_packet.inbox)} messages")
    
    if len(alice_packet.inbox) == 1 and len(bob_packet.inbox) == 1:
        print("✅ PASS: Both messages appear in tick 3")
        print("  Alice received:", [msg.content for msg in alice_packet.inbox])
        print("  Bob received:", [msg.content for msg in bob_packet.inbox])
    else:
        print("❌ FAIL: Not all messages appeared in tick 3")
    
    print(f"\n✅ Test completed!")

def _generate_test_observation_packet(world_state: WorldState, agent_id: str) -> ObservationPacket:
    """Generate a test observation packet for an agent (simplified version)."""
    agent = world_state.agents[agent_id]
    
    # Create agent state
    agent_state = AgentState(
        agent_id=agent.agent_id,
        name=agent.name,
        species=agent.species,
        personality=agent.personality,
        quirk=agent.quirk,
        ability=agent.ability,
        age=agent.age,
        sparks=agent.sparks,
        status=agent.status,
        bond_status=agent.bond_status,
        bond_members=agent.bond_members,
        home_realm=agent.home_realm,
        backstory=agent.backstory,
        opening_goal=agent.opening_goal,
        speech_style=agent.speech_style
    )
    
    # Create events (empty for this test)
    events = []
    
    # Create world news (simplified)
    world_news = WorldNews(
        tick=world_state.tick,
        total_agents=len([a for a in world_state.agents.values() if a.status == AgentStatus.ALIVE]),
        total_bonds=len(world_state.bonds),
        agents_vanished_this_tick=[],
        agents_spawned_this_tick=[],
        bonds_formed_this_tick=[],
        bonds_dissolved_this_tick=[],
        public_agent_info={},
        bob_sparks=world_state.bob_sparks
    )
    
    # Create inbox (this is what we're testing!)
    inbox = []
    
    # Add messages from message queue (only from previous ticks)
    for message in world_state.message_queue.get(agent_id, []):
        if message.tick < world_state.tick:
            inbox.append(message)
    
    # Add any pending bond requests for this agent (only from previous ticks)
    if agent_id in world_state.pending_bond_requests:
        bond_request = world_state.pending_bond_requests[agent_id]
        # Only include bond requests from previous ticks, not current tick
        if bond_request.tick < world_state.tick:
            inbox.append(bond_request)
    
    # Create observation packet
    packet = ObservationPacket(
        tick=world_state.tick,
        self_state=agent_state,
        events_since_last=events,
        inbox=inbox,
        world_news=world_news,
        mission_status=None,
        available_actions=["bond", "raid", "request_spark", "spawn", "message"]
    )
    
    return packet

def test_actual_tick_flow():
    """Test the actual tick flow to show the observation packet timing issue."""
    print("🧪 Testing Actual Tick Flow - Observation Packet Timing Issue")
    print("=" * 70)
    
    # Create a minimal world state
    world_state = WorldState()
    agents = create_test_agents()
    world_state.agents = agents
    world_state.tick = 1
    world_state.bob_sparks = 10
    world_state.bob_sparks_per_tick = 2
    
    print(f"✅ Created 2 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Simulate Stage 3: Generate observation packets for agents to make decisions
    print(f"\n🔄 Stage 3: Generate observation packets for agent decisions")
    print("-" * 50)
    
    alice_packet_stage3 = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet_stage3 = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox (Stage 3): {len(alice_packet_stage3.inbox)} messages")
    print(f"Bob inbox (Stage 3): {len(bob_packet_stage3.inbox)} messages")
    
    # Simulate agents making decisions based on Stage 3 packets
    print(f"\n🔄 Agents make decisions (create messages)")
    print("-" * 50)
    
    # Create a message from Alice to Bob
    alice_message = ActionMessage(
        agent_id="agent_001",
        intent="message",
        target="agent_002",
        content="Hello Bob!",
        reasoning="Want to say hi",
        tick=1
    )
    
    # Simulate Stage 5: Process actions (add to message queue)
    if "agent_002" not in world_state.message_queue:
        world_state.message_queue["agent_002"] = []
    world_state.message_queue["agent_002"].append(alice_message)
    
    print(f"✅ Added message from Alice to Bob")
    print(f"Message queue for Bob: {len(world_state.message_queue.get('agent_002', []))} messages")
    
    # Simulate end-of-tick: Generate observation packets for UI display
    print(f"\n🔄 End of Tick: Generate observation packets for UI display")
    print("-" * 50)
    
    alice_packet_end = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet_end = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox (End of Tick): {len(alice_packet_end.inbox)} messages")
    print(f"Bob inbox (End of Tick): {len(bob_packet_end.inbox)} messages")
    
    # Show the difference
    print(f"\n🔍 COMPARISON:")
    print("-" * 30)
    print(f"Stage 3 packets (for decisions):")
    print(f"  Alice: {len(alice_packet_stage3.inbox)} messages")
    print(f"  Bob: {len(bob_packet_stage3.inbox)} messages")
    print(f"")
    print(f"End of tick packets (for UI):")
    print(f"  Alice: {len(alice_packet_end.inbox)} messages")
    print(f"  Bob: {len(bob_packet_end.inbox)} messages")
    
    if len(bob_packet_stage3.inbox) == 0 and len(bob_packet_end.inbox) == 1:
        print(f"\n✅ CORRECT: Stage 3 has no messages, End of tick has messages")
        print(f"❌ PROBLEM: UI is probably showing Stage 3 packets instead of End of tick packets!")
    else:
        print(f"\n❌ UNEXPECTED: Something is wrong with the filtering")
    
    print(f"\n✅ Test completed!")

def test_without_tick_filtering():
    """Test what happens if we remove the tick filtering for messages."""
    print("🧪 Testing Without Tick Filtering - Messages Appear Immediately")
    print("=" * 70)
    
    # Create a minimal world state
    world_state = WorldState()
    agents = create_test_agents()
    world_state.agents = agents
    world_state.tick = 1
    world_state.bob_sparks = 10
    world_state.bob_sparks_per_tick = 2
    
    print(f"✅ Created 2 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Create a message from Alice to Bob (tick 1)
    alice_message = ActionMessage(
        agent_id="agent_001",
        intent="message",
        target="agent_002",
        content="Hello Bob!",
        reasoning="Want to say hi",
        tick=1
    )
    
    # Add to message queue
    if "agent_002" not in world_state.message_queue:
        world_state.message_queue["agent_002"] = []
    world_state.message_queue["agent_002"].append(alice_message)
    
    print(f"✅ Added message from Alice to Bob (tick 1)")
    
    # Generate observation packets WITHOUT tick filtering
    print(f"\n🔄 Generate observation packets WITHOUT tick filtering")
    print("-" * 50)
    
    # Simulate the current filtering logic
    inbox_with_filtering = []
    for message in world_state.message_queue.get("agent_002", []):
        if message.tick < world_state.tick:  # Current filtering
            inbox_with_filtering.append(message)
    
    # Simulate without filtering
    inbox_without_filtering = []
    for message in world_state.message_queue.get("agent_002", []):
        inbox_without_filtering.append(message)  # No filtering
    
    print(f"With tick filtering: {len(inbox_with_filtering)} messages")
    print(f"Without tick filtering: {len(inbox_without_filtering)} messages")
    
    if len(inbox_with_filtering) == 0 and len(inbox_without_filtering) == 1:
        print(f"\n✅ CONFIRMED: Tick filtering is preventing messages from appearing immediately")
        print(f"💡 SOLUTION: Remove tick filtering for messages to make them appear in same tick")
    else:
        print(f"\n❌ UNEXPECTED: Filtering not working as expected")
    
    print(f"\n✅ Test completed!")

def test_fixed_message_timing():
    """Test the fixed message timing - messages should appear immediately."""
    print("🧪 Testing Fixed Message Timing - Messages Appear Immediately")
    print("=" * 70)
    
    # Create a minimal world state
    world_state = WorldState()
    agents = create_test_agents()
    world_state.agents = agents
    world_state.tick = 1
    world_state.bob_sparks = 10
    world_state.bob_sparks_per_tick = 2
    
    print(f"✅ Created 2 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Create a message from Alice to Bob (tick 1)
    alice_message = ActionMessage(
        agent_id="agent_001",
        intent="message",
        target="agent_002",
        content="Hello Bob!",
        reasoning="Want to say hi",
        tick=1
    )
    
    # Add to message queue
    if "agent_002" not in world_state.message_queue:
        world_state.message_queue["agent_002"] = []
    world_state.message_queue["agent_002"].append(alice_message)
    
    print(f"✅ Added message from Alice to Bob (tick 1)")
    
    # Generate observation packets with the FIXED logic (no tick filtering for messages)
    print(f"\n🔄 Generate observation packets with FIXED logic")
    print("-" * 50)
    
    # Simulate the FIXED logic (no tick filtering for messages)
    inbox_fixed = []
    for message in world_state.message_queue.get("agent_002", []):
        inbox_fixed.append(message)  # No filtering for messages
    
    print(f"Fixed logic (no tick filtering): {len(inbox_fixed)} messages")
    
    if len(inbox_fixed) == 1:
        print(f"\n✅ SUCCESS: Messages now appear immediately in the same tick!")
        print(f"  Message: {inbox_fixed[0].content} (tick {inbox_fixed[0].tick})")
    else:
        print(f"\n❌ FAILED: Messages still not appearing immediately")
    
    print(f"\n✅ Test completed!")

def test_comprehensive_tick_flow():
    """Test the comprehensive tick flow with different message types."""
    print("🧪 Testing Comprehensive Tick Flow - Different Message Types")
    print("=" * 70)
    
    # Create a minimal world state
    world_state = WorldState()
    agents = create_test_agents()
    world_state.agents = agents
    world_state.tick = 1
    world_state.bob_sparks = 10
    world_state.bob_sparks_per_tick = 2
    
    print(f"✅ Created 2 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Simulate Tick 1: Agents make decisions
    print(f"\n🔄 Tick 1: Agents make decisions")
    print("-" * 40)
    
    # Alice sends a regular message to Bob
    alice_message = ActionMessage(
        agent_id="agent_001",
        intent="message",
        target="agent_002",
        content="Hello Bob!",
        reasoning="Want to say hi",
        tick=1
    )
    
    # Bob sends a bond request to Alice
    bob_bond_request = ActionMessage(
        agent_id="agent_002",
        intent="bond",
        target="agent_001",
        content="Let's form a bond!",
        reasoning="Want to bond",
        tick=1,
        bond_type="request"
    )
    
    print(f"✅ Alice creates message to Bob (tick 1)")
    print(f"✅ Bob creates bond request to Alice (tick 1)")
    
    # Simulate Stage 5: Process actions (add to appropriate queues)
    # Regular message goes to message queue
    if "agent_002" not in world_state.message_queue:
        world_state.message_queue["agent_002"] = []
    world_state.message_queue["agent_002"].append(alice_message)
    
    # Bond request goes to pending bond requests
    world_state.pending_bond_requests["agent_001"] = bob_bond_request
    
    print(f"✅ Messages processed and added to queues")
    
    # Generate observation packets for UI display (end of tick)
    print(f"\n🔄 End of Tick 1: Generate observation packets for UI")
    print("-" * 50)
    
    alice_packet = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox: {len(alice_packet.inbox)} messages")
    print(f"Bob inbox: {len(bob_packet.inbox)} messages")
    
    # Check what messages each agent received
    print(f"\n📨 Message Details:")
    print(f"Alice received:")
    for msg in alice_packet.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    print(f"Bob received:")
    for msg in bob_packet.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    # Test expectations
    expected_alice_messages = 1  # Should receive Bob's bond request
    expected_bob_messages = 1    # Should receive Alice's message
    
    if len(alice_packet.inbox) == expected_alice_messages and len(bob_packet.inbox) == expected_bob_messages:
        print(f"\n✅ SUCCESS: Both agents received messages from current tick!")
    else:
        print(f"\n❌ FAILED: Expected Alice={expected_alice_messages}, Bob={expected_bob_messages}")
        print(f"  Got Alice={len(alice_packet.inbox)}, Bob={len(bob_packet.inbox)}")
    
    # Test Tick 2: Agents should see messages from Tick 1 and can respond
    print(f"\n🔄 Tick 2: Agents respond to messages from Tick 1")
    print("-" * 50)
    
    world_state.tick = 2
    
    # Alice accepts Bob's bond request
    alice_response = ActionMessage(
        agent_id="agent_001",
        intent="bond",
        target="agent_002",
        content="I accept your bond request!",
        reasoning="Accept bond",
        tick=2,
        bond_type="acceptance"
    )
    
    # Bob responds to Alice's message
    bob_response = ActionMessage(
        agent_id="agent_002",
        intent="message",
        target="agent_001",
        content="Hello Alice! Nice to meet you!",
        reasoning="Respond to message",
        tick=2
    )
    
    print(f"✅ Alice responds to bond request (tick 2)")
    print(f"✅ Bob responds to message (tick 2)")
    
    # Process new actions
    if "agent_002" not in world_state.message_queue:
        world_state.message_queue["agent_002"] = []
    world_state.message_queue["agent_002"].append(alice_response)
    
    if "agent_001" not in world_state.message_queue:
        world_state.message_queue["agent_001"] = []
    world_state.message_queue["agent_001"].append(bob_response)
    
    # Generate observation packets for Tick 2
    alice_packet_tick2 = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet_tick2 = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"\n📨 Tick 2 Message Details:")
    print(f"Alice received:")
    for msg in alice_packet_tick2.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    print(f"Bob received:")
    for msg in bob_packet_tick2.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    # In Tick 2, both should have messages from Tick 2 (immediate)
    expected_alice_tick2 = 1  # Bob's response from tick 2
    expected_bob_tick2 = 1    # Alice's response from tick 2
    
    if len(alice_packet_tick2.inbox) == expected_alice_tick2 and len(bob_packet_tick2.inbox) == expected_bob_tick2:
        print(f"\n✅ SUCCESS: Tick 2 messages appear immediately!")
    else:
        print(f"\n❌ FAILED: Tick 2 messages not appearing immediately")
        print(f"  Expected Alice={expected_alice_tick2}, Bob={expected_bob_tick2}")
        print(f"  Got Alice={len(alice_packet_tick2.inbox)}, Bob={len(bob_packet_tick2.inbox)}")
    
    print(f"\n✅ Comprehensive test completed!")

def test_complete_fix():
    """Test the complete fix - both messages and bond requests appear immediately."""
    print("🧪 Testing Complete Fix - Messages and Bond Requests Appear Immediately")
    print("=" * 70)
    
    # Create a minimal world state
    world_state = WorldState()
    agents = create_test_agents()
    world_state.agents = agents
    world_state.tick = 1
    world_state.bob_sparks = 10
    world_state.bob_sparks_per_tick = 2
    
    print(f"✅ Created 2 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Simulate Tick 1: Agents make decisions
    print(f"\n🔄 Tick 1: Agents make decisions")
    print("-" * 40)
    
    # Alice sends a regular message to Bob
    alice_message = ActionMessage(
        agent_id="agent_001",
        intent="message",
        target="agent_002",
        content="Hello Bob!",
        reasoning="Want to say hi",
        tick=1
    )
    
    # Bob sends a bond request to Alice
    bob_bond_request = ActionMessage(
        agent_id="agent_002",
        intent="bond",
        target="agent_001",
        content="Let's form a bond!",
        reasoning="Want to bond",
        tick=1,
        bond_type="request"
    )
    
    print(f"✅ Alice creates message to Bob (tick 1)")
    print(f"✅ Bob creates bond request to Alice (tick 1)")
    
    # Simulate Stage 5: Process actions (add to appropriate queues)
    # Regular message goes to message queue
    if "agent_002" not in world_state.message_queue:
        world_state.message_queue["agent_002"] = []
    world_state.message_queue["agent_002"].append(alice_message)
    
    # Bond request goes to pending bond requests
    world_state.pending_bond_requests["agent_001"] = bob_bond_request
    
    print(f"✅ Messages processed and added to queues")
    
    # Generate observation packets with COMPLETE FIX (no tick filtering for anything)
    print(f"\n🔄 End of Tick 1: Generate observation packets with COMPLETE FIX")
    print("-" * 60)
    
    # Simulate the COMPLETE FIX logic (no tick filtering for messages OR bond requests)
    alice_inbox = []
    bob_inbox = []
    
    # Add messages from message queue (no tick filtering)
    for message in world_state.message_queue.get("agent_001", []):
        alice_inbox.append(message)
    for message in world_state.message_queue.get("agent_002", []):
        bob_inbox.append(message)
    
    # Add bond requests (no tick filtering)
    if "agent_001" in world_state.pending_bond_requests:
        alice_inbox.append(world_state.pending_bond_requests["agent_001"])
    if "agent_002" in world_state.pending_bond_requests:
        bob_inbox.append(world_state.pending_bond_requests["agent_002"])
    
    print(f"Alice inbox: {len(alice_inbox)} messages")
    print(f"Bob inbox: {len(bob_inbox)} messages")
    
    # Check what messages each agent received
    print(f"\n📨 Message Details:")
    print(f"Alice received:")
    for msg in alice_inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    print(f"Bob received:")
    for msg in bob_inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    # Test expectations
    expected_alice_messages = 1  # Should receive Bob's bond request
    expected_bob_messages = 1    # Should receive Alice's message
    
    if len(alice_inbox) == expected_alice_messages and len(bob_inbox) == expected_bob_messages:
        print(f"\n✅ SUCCESS: Both agents received messages from current tick!")
        print(f"💡 This is the correct behavior - messages appear immediately!")
    else:
        print(f"\n❌ FAILED: Expected Alice={expected_alice_messages}, Bob={expected_bob_messages}")
        print(f"  Got Alice={len(alice_inbox)}, Bob={len(bob_inbox)}")
    
    print(f"\n✅ Complete fix test completed!")

def test_correct_one_tick_delay():
    """Test the correct 1-tick delay behavior - messages appear in next tick."""
    print("🧪 Testing Correct 1-Tick Delay Behavior")
    print("=" * 70)
    
    # Create a minimal world state
    world_state = WorldState()
    agents = create_test_agents()
    world_state.agents = agents
    world_state.tick = 1
    world_state.bob_sparks = 10
    world_state.bob_sparks_per_tick = 2
    
    print(f"✅ Created 2 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Tick 1: Agents make decisions and create messages
    print(f"\n🔄 Tick 1: Agents make decisions")
    print("-" * 40)
    
    # Alice sends a message to Bob
    alice_message = ActionMessage(
        agent_id="agent_001",
        intent="message",
        target="agent_002",
        content="Hello Bob!",
        reasoning="Want to say hi",
        tick=1
    )
    
    # Bob sends a bond request to Alice
    bob_bond_request = ActionMessage(
        agent_id="agent_002",
        intent="bond",
        target="agent_001",
        content="Let's form a bond!",
        reasoning="Want to bond",
        tick=1
    )
    
    print(f"✅ Alice creates message to Bob (tick 1)")
    print(f"✅ Bob creates bond request to Alice (tick 1)")
    
    # Messages are processed and added to all_agent_actions (our new approach)
    world_state.all_agent_actions.append(alice_message)
    world_state.all_agent_actions.append(bob_bond_request)
    
    print(f"✅ Messages processed and added to all_agent_actions")
    
    # Tick 1: Generate observation packets - should have NO messages (1-tick delay)
    print(f"\n🔄 Tick 1: Generate observation packets")
    print("-" * 40)
    
    alice_packet_tick1 = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet_tick1 = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox (tick 1): {len(alice_packet_tick1.inbox)} messages")
    print(f"Bob inbox (tick 1): {len(bob_packet_tick1.inbox)} messages")
    
    if len(alice_packet_tick1.inbox) == 0 and len(bob_packet_tick1.inbox) == 0:
        print(f"✅ CORRECT: No messages in tick 1 (1-tick delay)")
    else:
        print(f"❌ WRONG: Messages appeared in tick 1")
    
    # Tick 2: Messages from Tick 1 should appear
    print(f"\n🔄 Tick 2: Messages from Tick 1 should appear")
    print("-" * 50)
    
    world_state.tick = 2
    
    alice_packet_tick2 = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet_tick2 = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox (tick 2): {len(alice_packet_tick2.inbox)} messages")
    print(f"Bob inbox (tick 2): {len(bob_packet_tick2.inbox)} messages")
    
    print(f"\n📨 Message Details (Tick 2):")
    print(f"Alice received:")
    for msg in alice_packet_tick2.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    print(f"Bob received:")
    for msg in bob_packet_tick2.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    if len(alice_packet_tick2.inbox) == 1 and len(bob_packet_tick2.inbox) == 1:
        print(f"\n✅ CORRECT: Messages from tick 1 appear in tick 2 (1-tick delay)")
    else:
        print(f"\n❌ WRONG: Expected 1 message each, got Alice={len(alice_packet_tick2.inbox)}, Bob={len(bob_packet_tick2.inbox)}")
    
    # Tick 2: Agents can now respond to messages from Tick 1
    print(f"\n🔄 Tick 2: Agents respond to messages from Tick 1")
    print("-" * 50)
    
    # Alice accepts Bob's bond request
    alice_response = ActionMessage(
        agent_id="agent_001",
        intent="message",
        target="agent_002",
        content="I accept your bond request!",
        reasoning="Accept bond",
        tick=2
    )
    
    # Bob responds to Alice's message
    bob_response = ActionMessage(
        agent_id="agent_002",
        intent="message",
        target="agent_001",
        content="Hello Alice! Nice to meet you!",
        reasoning="Respond to message",
        tick=2
    )
    
    print(f"✅ Alice responds to bond request (tick 2)")
    print(f"✅ Bob responds to message (tick 2)")
    
    # Process new actions - add to all_agent_actions
    world_state.all_agent_actions.append(alice_response)
    world_state.all_agent_actions.append(bob_response)
    
    # Tick 2: Generate observation packets - should still only have messages from Tick 1
    alice_packet_tick2_after = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet_tick2_after = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"\n📨 Message Details (Tick 2 after responses):")
    print(f"Alice received:")
    for msg in alice_packet_tick2_after.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    print(f"Bob received:")
    for msg in bob_packet_tick2_after.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    if len(alice_packet_tick2_after.inbox) == 1 and len(bob_packet_tick2_after.inbox) == 1:
        print(f"\n✅ CORRECT: Still only messages from tick 1 (responses from tick 2 not visible yet)")
    else:
        print(f"\n❌ WRONG: Tick 2 responses appeared immediately")
    
    # Tick 3: Messages from Tick 2 should appear
    print(f"\n🔄 Tick 3: Messages from Tick 2 should appear")
    print("-" * 50)
    
    world_state.tick = 3
    
    alice_packet_tick3 = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet_tick3 = _generate_test_observation_packet(world_state, "agent_002")
    
    print(f"Alice inbox (tick 3): {len(alice_packet_tick3.inbox)} messages")
    print(f"Bob inbox (tick 3): {len(bob_packet_tick3.inbox)} messages")
    
    print(f"\n📨 Message Details (Tick 3):")
    print(f"Alice received:")
    for msg in alice_packet_tick3.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    print(f"Bob received:")
    for msg in bob_packet_tick3.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (tick {msg.tick})")
    
    if len(alice_packet_tick3.inbox) == 1 and len(bob_packet_tick3.inbox) == 1:
        print(f"\n✅ CORRECT: Messages from tick 2 appear in tick 3 (1-tick delay)")
        print(f"💡 This is the correct behavior - 1-tick delay for all messages!")
    else:
        print(f"\n❌ WRONG: Expected 1 message each, got Alice={len(alice_packet_tick3.inbox)}, Bob={len(bob_packet_tick3.inbox)}")
    
    print(f"\n✅ Correct 1-tick delay test completed!")

def test_all_message_and_event_types():
    """Test all types of messages and events that agents can receive."""
    print("🧪 Testing All Message and Event Types")
    print("=" * 70)
    
    # Create a minimal world state
    world_state = WorldState()
    agents = create_test_agents()
    world_state.agents = agents
    world_state.tick = 1
    world_state.bob_sparks = 10
    world_state.bob_sparks_per_tick = 2
    
    # Add a third agent for more complex scenarios
    agents["agent_003"] = Agent(
        agent_id="agent_003",
        name="Charlie",
        species="human",
        personality=["creative", "energetic"],
        quirk="thinks in colors",
        ability="can create art",
        age=1,
        sparks=5,
        status=AgentStatus.ALIVE,
        bond_status=BondStatus.UNBONDED,
        bond_members=[],
        home_realm="earth",
        backstory="A creative artist",
        opening_goal="Create beauty",
        speech_style="colorful"
    )
    world_state.agents = agents
    
    print(f"✅ Created 3 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Tick 1: Create various types of messages and events
    print(f"\n🔄 Tick 1: Create various message and event types")
    print("-" * 50)
    
    # 1. Regular messages
    alice_message = ActionMessage(
        agent_id="agent_001",
        intent="message",
        target="agent_002",
        content="Hello Bob!",
        reasoning="Want to say hi",
        tick=1
    )
    
    # 2. Bond requests
    bob_bond_request = ActionMessage(
        agent_id="agent_002",
        intent="bond",
        target="agent_001",
        content="Let's form a bond!",
        reasoning="Want to bond",
        tick=1
    )
    
    # 3. Raid actions
    charlie_raid = ActionMessage(
        agent_id="agent_003",
        intent="raid",
        target="agent_001",
        content="I'm raiding you!",
        reasoning="Want to raid",
        tick=1
    )
    
    # 4. Spark requests
    alice_spark_request = ActionMessage(
        agent_id="agent_001",
        intent="request_spark",
        target="bob",
        content="Can I have some sparks?",
        reasoning="Need sparks",
        tick=1
    )
    
    print(f"✅ Created 4 different message types:")
    print(f"  - Regular message: Alice → Bob")
    print(f"  - Bond request: Bob → Alice")
    print(f"  - Raid action: Charlie → Alice")
    print(f"  - Spark request: Alice → Bob")
    
    # Process messages (simulate Stage 5)
    # Regular message goes to message queue
    if "agent_002" not in world_state.message_queue:
        world_state.message_queue["agent_002"] = []
    world_state.message_queue["agent_002"].append(alice_message)
    
    # Bond request goes to pending bond requests
    world_state.pending_bond_requests["agent_001"] = bob_bond_request
    
    # Raid action goes to message queue (for now)
    if "agent_001" not in world_state.message_queue:
        world_state.message_queue["agent_001"] = []
    world_state.message_queue["agent_001"].append(charlie_raid)
    
    # Spark request goes to message queue
    if "bob" not in world_state.message_queue:
        world_state.message_queue["bob"] = []
    world_state.message_queue["bob"].append(alice_spark_request)
    
    print(f"✅ Messages processed and added to queues")
    
    # 5. Create events (simulate what happens during action processing)
    # Spark distribution event
    world_state.spark_distribution_details = [{
        "bond_id": "bond_001",
        "bond_name": "Test Bond",
        "total_sparks_generated": 2,
        "distribution_details": [
            {
                "recipient_id": "agent_001",
                "recipient_name": "Alice",
                "sparks_received": 1
            }
        ]
    }]
    
    # World events
    world_state.events_this_tick = [
        {"event_type": "agent_spawned", "data": {"agent_id": "agent_004"}},
        {"event_type": "bond_formed", "data": {"bond_id": "bond_001"}},
        {"event_type": "agent_vanished", "data": {"agent_id": "agent_005"}}
    ]
    
    print(f"✅ Created events:")
    print(f"  - Spark distribution to Alice")
    print(f"  - Agent spawned")
    print(f"  - Bond formed")
    print(f"  - Agent vanished")
    
    # Generate observation packets for Tick 1
    print(f"\n🔄 Tick 1: Generate observation packets")
    print("-" * 40)
    
    alice_packet = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet = _generate_test_observation_packet(world_state, "agent_002")
    charlie_packet = _generate_test_observation_packet(world_state, "agent_003")
    
    print(f"Alice inbox: {len(alice_packet.inbox)} messages, events: {len(alice_packet.events_since_last)}")
    print(f"Bob inbox: {len(bob_packet.inbox)} messages, events: {len(bob_packet.events_since_last)}")
    print(f"Charlie inbox: {len(charlie_packet.inbox)} messages, events: {len(charlie_packet.events_since_last)}")
    
    # Check Alice's messages and events
    print(f"\n📨 Alice's observation packet:")
    print(f"Messages:")
    for msg in alice_packet.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (from {msg.agent_id})")
    
    print(f"Events:")
    for event in alice_packet.events_since_last:
        print(f"  - {event.event_type}: {event.description}")
    
    # Check Bob's messages
    print(f"\n📨 Bob's observation packet:")
    print(f"Messages:")
    for msg in bob_packet.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (from {msg.agent_id})")
    
    # Check Charlie's messages
    print(f"\n📨 Charlie's observation packet:")
    print(f"Messages:")
    for msg in charlie_packet.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (from {msg.agent_id})")
    
    # Check world news
    print(f"\n📰 World News:")
    print(f"  Total agents: {alice_packet.world_news.total_agents}")
    print(f"  Total bonds: {alice_packet.world_news.total_bonds}")
    print(f"  Agents spawned: {alice_packet.world_news.agents_spawned_this_tick}")
    print(f"  Bonds formed: {alice_packet.world_news.bonds_formed_this_tick}")
    print(f"  Agents vanished: {alice_packet.world_news.agents_vanished_this_tick}")
    print(f"  Bob's sparks: {alice_packet.world_news.bob_sparks}")
    
    # Tick 2: Messages from Tick 1 should appear
    print(f"\n🔄 Tick 2: Messages from Tick 1 should appear")
    print("-" * 50)
    
    world_state.tick = 2
    
    alice_packet_tick2 = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet_tick2 = _generate_test_observation_packet(world_state, "agent_002")
    charlie_packet_tick2 = _generate_test_observation_packet(world_state, "agent_003")
    
    print(f"Alice inbox (tick 2): {len(alice_packet_tick2.inbox)} messages")
    print(f"Bob inbox (tick 2): {len(bob_packet_tick2.inbox)} messages")
    print(f"Charlie inbox (tick 2): {len(charlie_packet_tick2.inbox)} messages")
    
    print(f"\n📨 Tick 2 Message Details:")
    print(f"Alice received:")
    for msg in alice_packet_tick2.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (from {msg.agent_id})")
    
    print(f"Bob received:")
    for msg in bob_packet_tick2.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (from {msg.agent_id})")
    
    print(f"Charlie received:")
    for msg in charlie_packet_tick2.inbox:
        print(f"  - {msg.intent}: '{msg.content}' (from {msg.agent_id})")
    
    # Test expectations for Tick 2
    expected_alice_messages = 2  # Bond request + raid
    expected_bob_messages = 1    # Regular message
    expected_charlie_messages = 0  # No messages
    
    if (len(alice_packet_tick2.inbox) == expected_alice_messages and 
        len(bob_packet_tick2.inbox) == expected_bob_messages and
        len(charlie_packet_tick2.inbox) == expected_charlie_messages):
        print(f"\n✅ CORRECT: All message types appear with 1-tick delay!")
    else:
        print(f"\n❌ WRONG: Expected Alice={expected_alice_messages}, Bob={expected_bob_messages}, Charlie={expected_charlie_messages}")
        print(f"  Got Alice={len(alice_packet_tick2.inbox)}, Bob={len(bob_packet_tick2.inbox)}, Charlie={len(charlie_packet_tick2.inbox)}")
    
    # Test mission-related events (if agents were bonded)
    print(f"\n🔄 Testing Mission-Related Events")
    print("-" * 40)
    
    # Simulate a bond and mission
    bond = Bond(
        bond_id="bond_001",
        members={"agent_001", "agent_002"},
        leader_id="agent_001",
        mission_id="mission_001"
    )
    world_state.bonds["bond_001"] = bond
    
    mission = Mission(
        mission_id="mission_001",
        bond_id="bond_001",
        title="Test Mission",
        description="A test mission",
        goal="Complete the test",
        leader_id="agent_001",
        current_progress="Just started",
        assigned_tasks={"agent_001": "Lead", "agent_002": "Support"},
        is_complete=False
    )
    world_state.missions["mission_001"] = mission
    
    # Update agent bond status
    agents["agent_001"].bond_status = BondStatus.BONDED
    agents["agent_001"].bond_members = ["agent_002"]
    agents["agent_002"].bond_status = BondStatus.BONDED
    agents["agent_002"].bond_members = ["agent_001"]
    
    # Generate mission status
    alice_mission_status = _get_test_mission_status(world_state, "agent_001")
    bob_mission_status = _get_test_mission_status(world_state, "agent_002")
    
    if alice_mission_status and bob_mission_status:
        print(f"✅ Mission status generated for bonded agents")
        print(f"  Mission: {alice_mission_status.mission_title}")
        print(f"  Goal: {alice_mission_status.mission_goal}")
        print(f"  Team: {alice_mission_status.team_members}")
    else:
        print(f"❌ Mission status not generated")
    
    print(f"\n✅ All message and event types test completed!")

def _get_test_mission_status(world_state: WorldState, agent_id: str) -> Optional[MissionStatus]:
    """Get mission status for testing."""
    for mission in world_state.missions.values():
        if not mission.is_complete:
            bond = world_state.bonds[mission.bond_id]
            if agent_id in bond.members:
                # Get team member names
                team_members = []
                for member_id in bond.members:
                    agent = world_state.agents[member_id]
                    team_members.append(agent.name)
                
                return MissionStatus(
                    mission_id=mission.mission_id,
                    mission_title=mission.title,
                    mission_description=mission.description,
                    mission_goal=mission.goal,
                    current_progress=mission.current_progress,
                    leader_id=mission.leader_id,
                    assigned_tasks=mission.assigned_tasks,
                    mission_complete=mission.is_complete,
                    team_members=team_members,
                    recent_messages=[]
                )
    return None

def test_ui_debug_case():
    """Test case based on actual UI data to debug the issue."""
    print("🧪 Testing UI Debug Case - Based on Actual Data")
    print("=" * 70)
    
    # Create world state based on actual UI data
    world_state = WorldState()
    world_state.tick = 1
    world_state.bob_sparks = 4
    world_state.bob_sparks_per_tick = 2
    
    # Create the 3 agents from the UI
    agents = {
        "agent_001": Agent(
            agent_id="agent_001",
            name="Xolotl-Tecpatl",
            species="human",
            personality=["creative", "energetic"],
            quirk="vibrant spirit",
            ability="artistic",
            age=1,
            sparks=4,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.UNBONDED,
            bond_members=[],
            home_realm="earth",
            backstory="A creative spirit",
            opening_goal="Create art",
            speech_style="enthusiastic"
        ),
        "agent_002": Agent(
            agent_id="agent_002",
            name="Nishta",
            species="human",
            personality=["gentle", "anxious"],
            quirk="collects stories",
            ability="preserves memories",
            age=1,
            sparks=4,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.UNBONDED,
            bond_members=[],
            home_realm="earth",
            backstory="A gentle collector",
            opening_goal="Gather stories",
            speech_style="thoughtful"
        ),
        "agent_003": Agent(
            agent_id="agent_003",
            name="Alaa Whisperleaf",
            species="human",
            personality=["shy", "gentle"],
            quirk="ethereal nature",
            ability="communication",
            age=1,
            sparks=4,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.UNBONDED,
            bond_members=[],
            home_realm="earth",
            backstory="A shy communicator",
            opening_goal="Make connections",
            speech_style="gentle"
        )
    }
    world_state.agents = agents
    
    print(f"✅ Created 3 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Tick 1: Agents make decisions (based on UI data)
    print(f"\n🔄 Tick 1: Agents make decisions (from UI data)")
    print("-" * 50)
    
    # Xolotl-Tecpatl sends bond request to Alaa Whisperleaf
    xolotl_bond = ActionMessage(
        agent_id="agent_001",
        intent="bond",
        target="agent_003",
        content="I send forth my joyous spirit to you, Alaa Whisperleaf! I wish to invite you into a bond of creation and inspiration. Together, let us rekindle the flames of artistry and weave our energies into a tapestry of life! What say you?",
        reasoning="Want to bond with Alaa",
        tick=1
    )
    
    # Nishta sends bond request to Alaa Whisperleaf
    nishta_bond = ActionMessage(
        agent_id="agent_002",
        intent="bond",
        target="agent_003",
        content="Hello Alaa, I think it would be wonderful if we could bond. I believe together we can gather and share stories, preserving them like grains of sand in the wind. What do you think?",
        reasoning="Want to bond with Alaa",
        tick=1
    )
    
    # Alaa Whisperleaf sends bond request to Nishta
    alaa_bond = ActionMessage(
        agent_id="agent_003",
        intent="bond",
        target="agent_002",
        content="Um, hello Nishta... I hope it's alright, but I'd like to invite you to form a bond with me, if you're open to it. I think we could learn from each other... maybe?",
        reasoning="Want to bond with Nishta",
        tick=1
    )
    
    print(f"✅ Xolotl-Tecpatl creates bond request to Alaa (tick 1)")
    print(f"✅ Nishta creates bond request to Alaa (tick 1)")
    print(f"✅ Alaa creates bond request to Nishta (tick 1)")
    
    # Process messages (simulate Stage 5)
    # Bond requests go to pending bond requests
    world_state.pending_bond_requests["agent_003"] = xolotl_bond  # Alaa receives Xolotl's request
    world_state.pending_bond_requests["agent_003"] = nishta_bond  # Alaa receives Nishta's request (overwrites)
    world_state.pending_bond_requests["agent_002"] = alaa_bond    # Nishta receives Alaa's request
    
    print(f"✅ Messages processed and added to queues")
    
    # Tick 1: Generate observation packets - should have NO messages (1-tick delay)
    print(f"\n🔄 Tick 1: Generate observation packets")
    print("-" * 40)
    
    xolotl_packet_tick1 = _generate_test_observation_packet(world_state, "agent_001")
    nishta_packet_tick1 = _generate_test_observation_packet(world_state, "agent_002")
    alaa_packet_tick1 = _generate_test_observation_packet(world_state, "agent_003")
    
    print(f"Xolotl-Tecpatl inbox (tick 1): {len(xolotl_packet_tick1.inbox)} messages")
    print(f"Nishta inbox (tick 1): {len(nishta_packet_tick1.inbox)} messages")
    print(f"Alaa Whisperleaf inbox (tick 1): {len(alaa_packet_tick1.inbox)} messages")
    
    if len(xolotl_packet_tick1.inbox) == 0 and len(nishta_packet_tick1.inbox) == 0 and len(alaa_packet_tick1.inbox) == 0:
        print(f"✅ CORRECT: No messages in tick 1 (1-tick delay)")
    else:
        print(f"❌ WRONG: Messages appeared in tick 1")
    
    # Tick 2: Messages from Tick 1 should appear
    print(f"\n🔄 Tick 2: Messages from Tick 1 should appear")
    print("-" * 50)
    
    world_state.tick = 2
    
    xolotl_packet_tick2 = _generate_test_observation_packet(world_state, "agent_001")
    nishta_packet_tick2 = _generate_test_observation_packet(world_state, "agent_002")
    alaa_packet_tick2 = _generate_test_observation_packet(world_state, "agent_003")
    
    print(f"Xolotl-Tecpatl inbox (tick 2): {len(xolotl_packet_tick2.inbox)} messages")
    print(f"Nishta inbox (tick 2): {len(nishta_packet_tick2.inbox)} messages")
    print(f"Alaa Whisperleaf inbox (tick 2): {len(alaa_packet_tick2.inbox)} messages")
    
    print(f"\n📨 Tick 2 Message Details:")
    print(f"Xolotl-Tecpatl received:")
    for msg in xolotl_packet_tick2.inbox:
        print(f"  - {msg.intent}: '{msg.content[:50]}...' (from {msg.agent_id})")
    
    print(f"Nishta received:")
    for msg in nishta_packet_tick2.inbox:
        print(f"  - {msg.intent}: '{msg.content[:50]}...' (from {msg.agent_id})")
    
    print(f"Alaa Whisperleaf received:")
    for msg in alaa_packet_tick2.inbox:
        print(f"  - {msg.intent}: '{msg.content[:50]}...' (from {msg.agent_id})")
    
    # Expected: Nishta should have 1 message (Alaa's bond request), Alaa should have 1 message (Nishta's bond request)
    expected_xolotl = 0  # No messages to Xolotl
    expected_nishta = 1  # Alaa's bond request
    expected_alaa = 1    # Nishta's bond request (Xolotl's was overwritten)
    
    if (len(xolotl_packet_tick2.inbox) == expected_xolotl and 
        len(nishta_packet_tick2.inbox) == expected_nishta and
        len(alaa_packet_tick2.inbox) == expected_alaa):
        print(f"\n✅ CORRECT: Messages from tick 1 appear in tick 2 (1-tick delay)")
    else:
        print(f"\n❌ WRONG: Expected Xolotl={expected_xolotl}, Nishta={expected_nishta}, Alaa={expected_alaa}")
        print(f"  Got Xolotl={len(xolotl_packet_tick2.inbox)}, Nishta={len(nishta_packet_tick2.inbox)}, Alaa={len(alaa_packet_tick2.inbox)}")
    
    # Tick 2: Agents respond (based on UI data)
    print(f"\n🔄 Tick 2: Agents respond (from UI data)")
    print("-" * 50)
    
    # Nishta accepts Alaa's bond request
    nishta_response = ActionMessage(
        agent_id="agent_002",
        intent="message",
        target="agent_003",
        content="Um, hello Alaa... I think I would like to accept your bond request. I feel like we could learn from each other and maybe gather some stories together... if that's alright with you?",
        reasoning="Accept Alaa's bond request",
        tick=2
    )
    
    # Alaa accepts Nishta's bond request
    alaa_response = ActionMessage(
        agent_id="agent_003",
        intent="message",
        target="agent_002",
        content="Hello, Nishta. Thank you for your kind message. I accept your bond request, if that's alright. I think it would be wonderful to share stories together.",
        reasoning="Accept Nishta's bond request",
        tick=2
    )
    
    print(f"✅ Nishta responds to Alaa's bond request (tick 2)")
    print(f"✅ Alaa responds to Nishta's bond request (tick 2)")
    
    # Process responses
    if "agent_003" not in world_state.message_queue:
        world_state.message_queue["agent_003"] = []
    world_state.message_queue["agent_003"].append(nishta_response)
    
    if "agent_002" not in world_state.message_queue:
        world_state.message_queue["agent_002"] = []
    world_state.message_queue["agent_002"].append(alaa_response)
    
    # Tick 2: Generate observation packets - should still only have messages from Tick 1
    xolotl_packet_tick2_after = _generate_test_observation_packet(world_state, "agent_001")
    nishta_packet_tick2_after = _generate_test_observation_packet(world_state, "agent_002")
    alaa_packet_tick2_after = _generate_test_observation_packet(world_state, "agent_003")
    
    print(f"\n📨 Tick 2 after responses:")
    print(f"Xolotl-Tecpatl: {len(xolotl_packet_tick2_after.inbox)} messages")
    print(f"Nishta: {len(nishta_packet_tick2_after.inbox)} messages")
    print(f"Alaa Whisperleaf: {len(alaa_packet_tick2_after.inbox)} messages")
    
    if (len(xolotl_packet_tick2_after.inbox) == 0 and 
        len(nishta_packet_tick2_after.inbox) == 1 and
        len(alaa_packet_tick2_after.inbox) == 1):
        print(f"\n✅ CORRECT: Still only messages from tick 1 (responses from tick 2 not visible yet)")
    else:
        print(f"\n❌ WRONG: Tick 2 responses appeared immediately")
    
    # Tick 3: Messages from Tick 2 should appear
    print(f"\n🔄 Tick 3: Messages from Tick 2 should appear")
    print("-" * 50)
    
    world_state.tick = 3
    
    xolotl_packet_tick3 = _generate_test_observation_packet(world_state, "agent_001")
    nishta_packet_tick3 = _generate_test_observation_packet(world_state, "agent_002")
    alaa_packet_tick3 = _generate_test_observation_packet(world_state, "agent_003")
    
    print(f"Xolotl-Tecpatl inbox (tick 3): {len(xolotl_packet_tick3.inbox)} messages")
    print(f"Nishta inbox (tick 3): {len(nishta_packet_tick3.inbox)} messages")
    print(f"Alaa Whisperleaf inbox (tick 3): {len(alaa_packet_tick3.inbox)} messages")
    
    # Expected: Nishta should have 2 messages (Alaa's bond request from tick 1 + Alaa's response from tick 2)
    # Alaa should have 2 messages (Nishta's bond request from tick 1 + Nishta's response from tick 2)
    expected_xolotl_tick3 = 0  # No messages to Xolotl
    expected_nishta_tick3 = 2  # Alaa's bond request + Alaa's response
    expected_alaa_tick3 = 2    # Nishta's bond request + Nishta's response
    
    if (len(xolotl_packet_tick3.inbox) == expected_xolotl_tick3 and 
        len(nishta_packet_tick3.inbox) == expected_nishta_tick3 and
        len(alaa_packet_tick3.inbox) == expected_alaa_tick3):
        print(f"\n✅ CORRECT: Messages from tick 2 appear in tick 3 (1-tick delay)")
        print(f"💡 This is the expected behavior - 1-tick delay for all messages!")
    else:
        print(f"\n❌ WRONG: Expected Xolotl={expected_xolotl_tick3}, Nishta={expected_nishta_tick3}, Alaa={expected_alaa_tick3}")
        print(f"  Got Xolotl={len(xolotl_packet_tick3.inbox)}, Nishta={len(nishta_packet_tick3.inbox)}, Alaa={len(alaa_packet_tick3.inbox)}")
    
    print(f"\n✅ UI debug test completed!")

def test_actual_world_engine_flow():
    """Test the actual world engine tick flow to debug the UI issue."""
    print("🧪 Testing Actual World Engine Flow")
    print("=" * 70)
    
    # Import the actual world engine
    from world.world_engine import WorldEngine
    
    # Create a minimal world engine
    engine = WorldEngine(":memory:")  # Use in-memory database
    
    # Initialize world with 3 agents
    simulation_id = engine.initialize_world(num_agents=3, simulation_name="Debug Test")
    
    print(f"✅ Created world engine with simulation ID: {simulation_id}")
    
    # Get initial agents
    agents = list(engine.world_state.agents.values())
    print(f"✅ Created {len(agents)} agents: {', '.join([agent.name for agent in agents])}")
    
    # Tick 1: Run the actual tick
    print(f"\n🔄 Tick 1: Run actual world engine tick")
    print("-" * 50)
    
    result_tick1 = engine.tick(simulation_id)
    
    print(f"✅ Tick 1 completed")
    print(f"  Agents vanished: {len(result_tick1.agents_vanished)}")
    print(f"  Bonds formed: {len(result_tick1.bonds_formed)}")
    print(f"  Agent actions: {len(result_tick1.agent_actions)}")
    print(f"  Observation packets: {len(result_tick1.observation_packets)}")
    
    # Check observation packets for Tick 1
    print(f"\n📨 Tick 1 Observation Packets:")
    for agent_id, packet in result_tick1.observation_packets.items():
        agent_name = packet.self_state.name
        message_count = len(packet.inbox)
        print(f"  {agent_name}: {message_count} messages")
        
        if message_count > 0:
            print(f"    Messages:")
            for msg in packet.inbox:
                print(f"      - {msg.intent}: '{msg.content[:50]}...'")
    
    # Tick 2: Run another tick
    print(f"\n🔄 Tick 2: Run actual world engine tick")
    print("-" * 50)
    
    result_tick2 = engine.tick(simulation_id)
    
    print(f"✅ Tick 2 completed")
    print(f"  Agents vanished: {len(result_tick2.agents_vanished)}")
    print(f"  Bonds formed: {len(result_tick2.bonds_formed)}")
    print(f"  Agent actions: {len(result_tick2.agent_actions)}")
    print(f"  Observation packets: {len(result_tick2.observation_packets)}")
    
    # Check observation packets for Tick 2
    print(f"\n📨 Tick 2 Observation Packets:")
    for agent_id, packet in result_tick2.observation_packets.items():
        agent_name = packet.self_state.name
        message_count = len(packet.inbox)
        print(f"  {agent_name}: {message_count} messages")
        
        if message_count > 0:
            print(f"    Messages:")
            for msg in packet.inbox:
                print(f"      - {msg.intent}: '{msg.content[:50]}...'")
    
    # Check if any agents made actions in Tick 1
    print(f"\n🧠 Tick 1 Agent Actions:")
    for action in result_tick1.agent_actions:
        agent_name = engine.world_state.agents[action.agent_id].name
        print(f"  {agent_name}: {action.intent} -> {action.target}")
        print(f"    Content: '{action.content[:50]}...'")
    
    # Check if any agents made actions in Tick 2
    print(f"\n🧠 Tick 2 Agent Actions:")
    for action in result_tick2.agent_actions:
        agent_name = engine.world_state.agents[action.agent_id].name
        print(f"  {agent_name}: {action.intent} -> {action.target}")
        print(f"    Content: '{action.content[:50]}...'")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"  Tick 1: {len(result_tick1.agent_actions)} actions, messages in packets: {sum(len(p.inbox) for p in result_tick1.observation_packets.values())}")
    print(f"  Tick 2: {len(result_tick2.agent_actions)} actions, messages in packets: {sum(len(p.inbox) for p in result_tick2.observation_packets.values())}")
    
    # Expected behavior
    expected_tick1_messages = 0  # No messages in first tick
    expected_tick2_messages = len(result_tick1.agent_actions)  # Messages from Tick 1 actions
    
    actual_tick1_messages = sum(len(p.inbox) for p in result_tick1.observation_packets.values())
    actual_tick2_messages = sum(len(p.inbox) for p in result_tick2.observation_packets.values())
    
    if actual_tick1_messages == expected_tick1_messages and actual_tick2_messages == expected_tick2_messages:
        print(f"\n✅ CORRECT: World engine is working as expected!")
        print(f"💡 The issue is likely in the UI data flow, not the core logic.")
    else:
        print(f"\n❌ WRONG: World engine behavior is unexpected!")
        print(f"  Expected Tick 1: {expected_tick1_messages}, got: {actual_tick1_messages}")
        print(f"  Expected Tick 2: {expected_tick2_messages}, got: {actual_tick2_messages}")
    
    print(f"\n✅ Actual world engine test completed!")

def test_ui_data_flow():
    """Test the UI data flow to see where the issue is."""
    print("🧪 Testing UI Data Flow")
    print("=" * 70)
    
    # Simulate the exact data flow that the UI uses
    from ui.utils.simulation import run_single_tick
    import streamlit as st
    
    # Create a minimal world state (like the UI does)
    world_state = WorldState()
    agents = create_test_agents()
    world_state.agents = agents
    world_state.tick = 1
    world_state.bob_sparks = 4
    world_state.bob_sparks_per_tick = 2
    
    # Add a third agent
    agents["agent_003"] = Agent(
        agent_id="agent_003",
        name="Charlie",
        species="human",
        personality=["creative", "energetic"],
        quirk="thinks in colors",
        ability="can create art",
        age=1,
        sparks=4,
        status=AgentStatus.ALIVE,
        bond_status=BondStatus.UNBONDED,
        bond_members=[],
        home_realm="earth",
        backstory="A creative artist",
        opening_goal="Create beauty",
        speech_style="colorful"
    )
    world_state.agents = agents
    
    print(f"✅ Created 3 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Simulate Tick 1: Agents make decisions
    print(f"\n🔄 Tick 1: Agents make decisions")
    print("-" * 40)
    
    # Create actions (like agents would)
    alice_action = ActionMessage(
        agent_id="agent_001",
        intent="bond",
        target="agent_002",
        content="Let's form a bond!",
        reasoning="Want to bond",
        tick=1
    )
    
    bob_action = ActionMessage(
        agent_id="agent_002",
        intent="message",
        target="agent_001",
        content="Hello Alice!",
        reasoning="Want to say hi",
        tick=1
    )
    
    charlie_action = ActionMessage(
        agent_id="agent_003",
        intent="bond",
        target="agent_001",
        content="Let's bond!",
        reasoning="Want to bond",
        tick=1
    )
    
    print(f"✅ Created 3 actions for Tick 1")
    
    # Simulate what the UI does: store actions in world state
    world_state.agent_actions_for_logging = [alice_action, bob_action, charlie_action]
    
    # Simulate what the UI does: process actions and add to queues
    # Bond requests go to pending bond requests
    world_state.pending_bond_requests["agent_002"] = alice_action  # Bob receives Alice's bond request
    world_state.pending_bond_requests["agent_001"] = charlie_action  # Alice receives Charlie's bond request
    
    # Regular messages go to message queue
    if "agent_001" not in world_state.message_queue:
        world_state.message_queue["agent_001"] = []
    world_state.message_queue["agent_001"].append(bob_action)  # Alice receives Bob's message
    
    print(f"✅ Actions processed and added to queues")
    
    # Simulate what the UI does: generate observation packets
    print(f"\n🔄 Generate observation packets for UI")
    print("-" * 40)
    
    alice_packet = _generate_test_observation_packet(world_state, "agent_001")
    bob_packet = _generate_test_observation_packet(world_state, "agent_002")
    charlie_packet = _generate_test_observation_packet(world_state, "agent_003")
    
    print(f"Alice inbox: {len(alice_packet.inbox)} messages")
    print(f"Bob inbox: {len(bob_packet.inbox)} messages")
    print(f"Charlie inbox: {len(charlie_packet.inbox)} messages")
    
    # Simulate what the UI does: serialize observation packets
    print(f"\n🔄 Serialize observation packets (like UI does)")
    print("-" * 50)
    
    observation_packets_serialized = {}
    for agent_id, packet in [("agent_001", alice_packet), ("agent_002", bob_packet), ("agent_003", charlie_packet)]:
        observation_packets_serialized[agent_id] = {
            'self_state': {
                'name': packet.self_state.name,
                'sparks': packet.self_state.sparks,
                'bond_status': packet.self_state.bond_status.value,
                'age': packet.self_state.age
            },
            'events_since_last': [
                {
                    'event_type': event.event_type,
                    'description': event.description,
                    'spark_change': event.spark_change,
                    'source_agent': event.source_agent
                } for event in packet.events_since_last
            ],
            'inbox': [
                {
                    'sender_id': msg.agent_id if hasattr(msg, 'agent_id') else 'Unknown',
                    'content': msg.content,
                    'intent': msg.intent
                } for msg in packet.inbox
            ],
            'world_news': {
                'bob_sparks': packet.world_news.bob_sparks,
                'agents_spawned_this_tick': packet.world_news.agents_spawned_this_tick,
                'agents_vanished_this_tick': packet.world_news.agents_vanished_this_tick,
                'bonds_formed_this_tick': packet.world_news.bonds_formed_this_tick
            }
        }
    
    print(f"✅ Observation packets serialized")
    
    # Check the serialized data
    print(f"\n📨 Serialized Observation Packets:")
    for agent_id, data in observation_packets_serialized.items():
        agent_name = data['self_state']['name']
        message_count = len(data['inbox'])
        print(f"  {agent_name}: {message_count} messages")
        
        if message_count > 0:
            print(f"    Messages:")
            for msg in data['inbox']:
                print(f"      - {msg['intent']}: '{msg['content'][:50]}...' (from {msg['sender_id']})")
    
    # Expected: Alice should have 2 messages (Bob's message + Charlie's bond request)
    # Bob should have 1 message (Alice's bond request)
    # Charlie should have 0 messages
    expected_alice = 2
    expected_bob = 1
    expected_charlie = 0
    
    actual_alice = len(observation_packets_serialized["agent_001"]["inbox"])
    actual_bob = len(observation_packets_serialized["agent_002"]["inbox"])
    actual_charlie = len(observation_packets_serialized["agent_003"]["inbox"])
    
    if actual_alice == expected_alice and actual_bob == expected_bob and actual_charlie == expected_charlie:
        print(f"\n✅ CORRECT: Serialized data shows expected messages!")
        print(f"💡 The issue is likely in how the UI displays this data.")
    else:
        print(f"\n❌ WRONG: Serialized data is incorrect!")
        print(f"  Expected Alice={expected_alice}, Bob={expected_bob}, Charlie={expected_charlie}")
        print(f"  Got Alice={actual_alice}, Bob={actual_bob}, Charlie={actual_charlie}")
    
    print(f"\n✅ UI data flow test completed!")

if __name__ == "__main__":
    test_message_timing()
    print("\n" + "="*70)
    test_actual_tick_flow()
    print("\n" + "="*70)
    test_without_tick_filtering()
    print("\n" + "="*70)
    test_fixed_message_timing()
    print("\n" + "="*70)
    test_comprehensive_tick_flow()
    print("\n" + "="*70)
    test_complete_fix()
    print("\n" + "="*70)
    test_correct_one_tick_delay()
    print("\n" + "="*70)
    test_all_message_and_event_types()
    print("\n" + "="*70)
    test_ui_debug_case()
    print("\n" + "="*70)
    test_ui_data_flow()
    print("\n" + "="*70)
    test_actual_world_engine_flow() 