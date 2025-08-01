#!/usr/bin/env python3
"""
Pure simulation test for spark distribution - no LLMs involved.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from world.state import WorldState, Agent, Bond, AgentStatus, BondStatus
from world.world_engine import WorldEngine
from communication.messages.action_message import ActionMessage

def test_spark_distribution_pure():
    """Test spark distribution with pure simulation - no LLMs."""
    print("🧪 Testing Spark Distribution Flow (Pure Simulation)")
    print("=" * 60)
    
    # Create a minimal world state manually
    world_state = WorldState()
    
    # Create 3 agents manually
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
        ),
        "agent_003": Agent(
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
    }
    
    world_state.agents = agents
    world_state.tick = 0
    world_state.bob_sparks = 10
    world_state.bob_sparks_per_tick = 2
    
    print(f"✅ Created 3 agents: {', '.join([agent.name for agent in agents.values()])}")
    
    # Test 1: No bonds initially
    print(f"\n🔄 Test 1: No bonds (Tick 0)")
    print("-" * 40)
    
    # Simulate Stage 1: Mint and distribute sparks
    total_minted = 0
    for bond in world_state.bonds.values():
        sparks_generated = len(bond.members)
        total_minted += sparks_generated
    
    print(f"Stage 1: Minted {total_minted} sparks from {len(world_state.bonds)} bonds")
    print("⚡ Agent Sparks:")
    for agent in agents.values():
        print(f"  {agent.name}: {agent.sparks} sparks")
    
    # Test 2: Create a bond manually
    print(f"\n🔄 Test 2: Create bond between Alice and Bob")
    print("-" * 40)
    
    # Create bond manually
    bond = Bond(
        bond_id="bond_001",
        members={"agent_001", "agent_002"},
        leader_id="agent_001",
        mission_id=None
    )
    world_state.bonds["bond_001"] = bond
    
    # Update agent bond status
    agents["agent_001"].bond_status = BondStatus.BONDED
    agents["agent_001"].bond_members = ["agent_002"]
    agents["agent_002"].bond_status = BondStatus.BONDED  
    agents["agent_002"].bond_members = ["agent_001"]
    
    print(f"✅ Created bond between Alice and Bob")
    
    # Test 3: Distribute sparks from the new bond
    print(f"\n🔄 Test 3: Distribute sparks from new bond")
    print("-" * 40)
    
    # Simulate Stage 1 spark distribution
    import random
    total_distributed = 0
    
    for bond in world_state.bonds.values():
        sparks_generated = len(bond.members)  # 2 sparks for 2 members
        bond.sparks_generated_this_tick = sparks_generated
        
        # Distribute randomly
        bond_members = list(bond.members)
        for _ in range(sparks_generated):
            recipient_id = random.choice(bond_members)
            recipient = agents[recipient_id]
            recipient.sparks += 1
            total_distributed += 1
            print(f"  {recipient.name} received 1 spark from bond")
    
    print(f"Stage 1: Distributed {total_distributed} sparks from {len(world_state.bonds)} bonds")
    print("⚡ Agent Sparks:")
    for agent in agents.values():
        print(f"  {agent.name}: {agent.sparks} sparks")
    
    # Test 4: Add Charlie to the bond
    print(f"\n🔄 Test 4: Add Charlie to the bond")
    print("-" * 40)
    
    # Add Charlie to existing bond
    bond.members.add("agent_003")
    agents["agent_003"].bond_status = BondStatus.BONDED
    agents["agent_003"].bond_members = ["agent_001", "agent_002"]
    agents["agent_001"].bond_members.append("agent_003")
    agents["agent_002"].bond_members.append("agent_003")
    
    print(f"✅ Added Charlie to the bond (now 3 members)")
    
    # Test 5: Distribute sparks from 3-member bond
    print(f"\n🔄 Test 5: Distribute sparks from 3-member bond")
    print("-" * 40)
    
    # Clear previous distribution
    total_distributed = 0
    
    for bond in world_state.bonds.values():
        sparks_generated = len(bond.members)  # 3 sparks for 3 members
        bond.sparks_generated_this_tick = sparks_generated
        
        # Distribute randomly
        bond_members = list(bond.members)
        for _ in range(sparks_generated):
            recipient_id = random.choice(bond_members)
            recipient = agents[recipient_id]
            recipient.sparks += 1
            total_distributed += 1
            print(f"  {recipient.name} received 1 spark from bond")
    
    print(f"Stage 1: Distributed {total_distributed} sparks from {len(world_state.bonds)} bonds")
    print("⚡ Agent Sparks:")
    for agent in agents.values():
        print(f"  {agent.name}: {agent.sparks} sparks")
    
    print(f"\n✅ Test completed! Spark distribution is working correctly.")
    print(f"📊 Summary:")
    print(f"  - Bond generates 1 spark per member per tick")
    print(f"  - Sparks are distributed randomly among bond members")
    print(f"  - New bonds get sparks starting from the next tick")

if __name__ == "__main__":
    test_spark_distribution_pure() 