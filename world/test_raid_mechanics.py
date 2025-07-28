#!/usr/bin/env python3
"""
Test script specifically for raid mechanics.
Creates a scenario where agents are more likely to raid each other.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world.world_engine import WorldEngine
from world.human_logger import HumanLogger
from communication.messages.observation_packet import BondStatus
import dspy
from dspy.teleprompt import BootstrapFewShot

# Configure DSPy (using the same configuration as other modules)
dspy.settings.configure(lm="gpt-4o-mini")

def test_raid_mechanics():
    """Test raid mechanics with aggressive agents."""
    print("="*80)
    print("⚔️  TESTING RAID MECHANICS ⚔️")
    print("="*80)
    
    # Initialize world engine
    engine = WorldEngine("test_raid.db")
    
    # Initialize human logger
    logger = HumanLogger()
    
    # Create a new simulation
    simulation_id = engine.initialize_world(num_agents=3, simulation_name="Raid Test")
    
    # Log simulation start
    logger.log_simulation_start(engine.world_state, "Raid Mechanics Test")
    
    print("\n" + "="*80)
    print("🎯 CREATING RAID SCENARIO")
    print("="*80)
    
    # Manually adjust agent sparks to create tension
    agents = list(engine.world_state.agents.values())
    
    # Create a scenario where agents are desperate and likely to raid
    agents[0].sparks = 0  # Extremely desperate agent (will vanish next tick!)
    agents[1].sparks = 1  # Desperate agent (likely to raid)
    agents[2].sparks = 8  # Rich target agent (has lots of sparks to steal)
    
    print(f"   💀 {agents[0].name}: {agents[0].sparks} sparks (WILL VANISH!)")
    print(f"   🔴 {agents[1].name}: {agents[1].sparks} sparks (DESPERATE)")
    print(f"   🟢 {agents[2].name}: {agents[2].sparks} sparks (RICH TARGET)")
    
    # Also make them unbonded to prevent cooperation
    for agent in agents:
        agent.bond_status = BondStatus.UNBONDED
        agent.bond_members = []
    
    # Run a few ticks to see raid behavior
    for tick in range(1, 4):
        print(f"\n{'='*80}")
        print(f"⏰ TICK {tick}")
        print(f"{'='*80}")
        
        logger.log_tick_start(tick, engine.world_state)
        
        result = engine.tick(simulation_id)
        
        logger.log_tick_result(result, engine.world_state)
        
        # Show raid statistics
        if result.total_raids_attempted > 0:
            print(f"\n⚔️  RAID STATISTICS:")
            print(f"   Total raids attempted: {result.total_raids_attempted}")
        
        # Check for vanished agents
        if result.agents_vanished:
            print(f"\n💀 AGENTS VANISHED: {result.agents_vanished}")
    
    print(f"\n{'='*80}")
    print("🏁 RAID TEST COMPLETE")
    print(f"{'='*80}")
    
    # Final statistics
    alive_agents = [a for a in engine.world_state.agents.values() if a.status.value == "alive"]
    print(f"   🌟 Surviving agents: {len(alive_agents)}")
    print(f"   ⚔️  Total raids attempted: {engine.world_state.total_raids_attempted}")
    
    for agent in alive_agents:
        print(f"   ✨ {agent.name}: {agent.sparks} sparks")
    
    # Clean up
    if os.path.exists("test_raid.db"):
        os.remove("test_raid.db")

if __name__ == "__main__":
    test_raid_mechanics() 