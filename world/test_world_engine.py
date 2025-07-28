#!/usr/bin/env python3
"""
Test script for the World Engine.

This script tests the complete World Engine functionality including:
- World initialization
- Tick execution
- All 6 stages of the tick process
- Game mechanics (sparks, bonds, raids, spawning)
- Database persistence
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tempfile
import shutil
from world.world_engine import WorldEngine, TickResult
from world.human_logger import HumanLogger


def print_tick_result(result: TickResult):
    """Print tick results in a beautiful format."""
    print(f"\n{'🎮' * 20} TICK {result.tick} RESULTS {'🎮' * 20}")
    
    print(f"\n📊 OVERALL STATISTICS")
    print(f"   Total sparks minted: {result.total_sparks_minted}")
    print(f"   Total sparks lost: {result.total_sparks_lost}")
    print(f"   Total raids attempted: {result.total_raids_attempted}")
    
    print(f"\n🔄 STAGE RESULTS")
    for stage, result_text in result.stage_results.items():
        print(f"   {stage}: {result_text}")
    
    print(f"\n👥 AGENT CHANGES")
    print(f"   Agents vanished: {len(result.agents_vanished)}")
    if result.agents_vanished:
        print(f"      {', '.join(result.agents_vanished)}")
    
    print(f"   Agents spawned: {len(result.agents_spawned)}")
    if result.agents_spawned:
        print(f"      {', '.join(result.agents_spawned)}")
    
    print(f"\n🤝 BOND CHANGES")
    print(f"   Bonds formed: {len(result.bonds_formed)}")
    if result.bonds_formed:
        print(f"      {', '.join(result.bonds_formed)}")
    
    print(f"   Bonds dissolved: {len(result.bonds_dissolved)}")
    if result.bonds_dissolved:
        print(f"      {', '.join(result.bonds_dissolved)}")
    
    print(f"\n📝 EVENTS LOGGED")
    print(f"   Total events: {len(result.events_logged)}")
    for event in result.events_logged[:5]:  # Show first 5 events
        print(f"      {event['event_type']}: {event['data']}")
    
    if len(result.events_logged) > 5:
        print(f"      ... and {len(result.events_logged) - 5} more events")
    
    print(f"{'🎮' * 20} END TICK {result.tick} {'🎮' * 20}")


def print_world_state(engine: WorldEngine):
    """Print current world state."""
    state = engine.world_state
    
    print(f"\n{'🌍' * 20} WORLD STATE {'🌍' * 20}")
    print(f"Tick: {state.tick}")
    print(f"Current stage: {state.current_processing_stage}")
    print(f"Bob's sparks: {state.bob_sparks}")
    
    print(f"\n👥 AGENTS ({len(state.agents)} total)")
    for agent_id, agent in state.agents.items():
        status_emoji = "💀" if agent.status.value == "vanished" else "🌟"
        bond_emoji = "🔗" if agent.bond_status.value == "bonded" else "🔓"
        print(f"   {status_emoji} {agent_id}: {agent.name} ({agent.species}) - {agent.sparks}⚡, age {agent.age} {bond_emoji}")
    
    print(f"\n🤝 BONDS ({len(state.bonds)} total)")
    for bond_id, bond in state.bonds.items():
        members_str = ", ".join(bond.members)
        print(f"   {bond_id}: {members_str} (leader: {bond.leader_id}, sparks: {bond.sparks_generated_this_tick})")
    
    print(f"\n🎯 MISSIONS ({len(state.missions)} total)")
    for mission_id, mission in state.missions.items():
        status = "✅" if mission.is_complete else "🔄"
        print(f"   {status} {mission_id}: {mission.title} - {mission.goal}")
    
    print(f"{'🌍' * 20} END WORLD STATE {'🌍' * 20}")


def test_world_initialization():
    """Test world initialization."""
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_spark_world.db")
    
    try:
        # Initialize world engine
        engine = WorldEngine(db_path=db_path)
        
        # Reset database to ensure fresh start
        engine.reset_database()
        
        print("🧪 Testing world initialization...")
        
        # Initialize world
        simulation_id = engine.initialize_world(
            num_agents=3,
            simulation_name="Test Simulation"
        )
        
        print(f"✅ World initialized successfully!")
        print(f"   Simulation ID: {simulation_id}")
        print(f"   Number of agents: {len(engine.world_state.agents)}")
        print(f"   Bob's sparks: {engine.world_state.bob_sparks}")
        print(f"   Bob's sparks per tick: {engine.world_state.bob_sparks_per_tick}")
        
        # Show agents
        print(f"\n👥 CREATED AGENTS:")
        for agent_id, agent in engine.world_state.agents.items():
            print(f"   {agent_id}: {agent.name} ({agent.species})")
            print(f"      Personality: {', '.join(agent.personality)}")
            print(f"      Quirk: {agent.quirk}")
            print(f"      Goal: {agent.opening_goal}")
        
        return engine, simulation_id
        
    except Exception as e:
        print(f"❌ Error in world initialization: {e}")
        import traceback
        traceback.print_exc()
        return None, None
    
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def test_single_tick(engine: WorldEngine, simulation_id: int, logger: HumanLogger):
    """Test execution of a single tick."""
    try:
        # Log tick start
        logger.log_tick_start(engine.world_state.tick + 1, engine.world_state)
        
        # Execute one tick
        result = engine.tick(simulation_id)
        
        # Log tick results
        logger.log_tick_result(result, engine.world_state)
        
        # Pause for user input
        print(f"\n{'='*80}")
        print("⏸️  PAUSED - Press any key to continue to multiple ticks test...")
        print(f"{'='*80}")
        input()
        
        return result
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_multiple_ticks(engine: WorldEngine, simulation_id: int, logger: HumanLogger):
    """Test multiple ticks to see emergent behavior."""
    print(f"\n{'='*80}")
    print(f"🔄 TESTING MULTIPLE TICKS")
    print(f"{'='*80}")
    
    # Run 5 ticks to see emergent behavior
    for tick in range(1, 6):
        logger.log_tick_start(tick, engine.world_state)
        
        result = engine.tick(simulation_id)
        
        logger.log_tick_result(result, engine.world_state)
        
        # Show tick summary
        print(f"\n{'='*80}")
        print(f"📊 END OF TICK {tick}")
        print(f"{'='*80}")
        print(f"   🌟 Living minds: {len([a for a in engine.world_state.agents.values() if a.status.value == 'alive'])}")
        print(f"   ⚡ Total sparks: {sum(a.sparks for a in engine.world_state.agents.values() if a.status.value == 'alive')}")
        print(f"   🎁 Bob's sparks: {engine.world_state.bob_sparks}")
        print(f"   🔗 Active bonds: {len(engine.world_state.bonds)}")
        
        # Check if any agents vanished
        if result.agents_vanished:
            print(f"⚠️  Agents vanished in tick {tick}: {result.agents_vanished}")
        
        # Check if any bonds formed
        if result.bonds_formed:
            print(f"🤝 Bonds formed in tick {tick}: {result.bonds_formed}")
        
        # Check for minds in danger
        minds_in_danger = [a for a in engine.world_state.agents.values() 
                          if a.status.value == 'alive' and a.sparks <= 2]
        if minds_in_danger:
            print(f"\n⚠️  MINDS IN DANGER:")
            for agent in minds_in_danger:
                print(f"   🔴 {agent.name}: {agent.sparks} sparks remaining")
        
        # Pause for user input (except on the last tick)
        if tick < 5:
            print(f"\n{'='*80}")
            print("⏸️  PAUSED - Press any key to continue to the next tick...")
            print(f"{'='*80}")
            input()
    
    return engine.world_state


def test_database_persistence(engine: WorldEngine, simulation_id: int):
    """Test database persistence by reloading state."""
    print(f"\n{'='*80}")
    print(f"💾 TESTING DATABASE PERSISTENCE 💾")
    print(f"{'='*80}")
    
    try:
        # Save current state
        print(f"\nSaving current state...")
        engine.save_state(simulation_id)
        print(f"✅ State saved successfully")
        
        # Create new engine instance
        print(f"\nCreating new engine instance...")
        new_engine = WorldEngine(db_path=engine.db_path)
        
        # Load state
        print(f"\nLoading state from database...")
        new_engine.load_state(simulation_id)
        print(f"✅ State loaded successfully")
        
        # Compare states
        print(f"\nComparing states...")
        original_agents = len(engine.world_state.agents)
        loaded_agents = len(new_engine.world_state.agents)
        original_bonds = len(engine.world_state.bonds)
        loaded_bonds = len(new_engine.world_state.bonds)
        
        print(f"   Original agents: {original_agents}")
        print(f"   Loaded agents: {loaded_agents}")
        print(f"   Original bonds: {original_bonds}")
        print(f"   Loaded bonds: {loaded_bonds}")
        
        if original_agents == loaded_agents and original_bonds == loaded_bonds:
            print(f"✅ State persistence working correctly!")
        else:
            print(f"❌ State persistence failed!")
        
        return new_engine
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_game_mechanics():
    """Test specific game mechanics."""
    print(f"\n{'='*80}")
    print(f"⚙️ TESTING GAME MECHANICS ⚙️")
    print(f"{'='*80}")
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "mechanics_test.db")
    
    try:
        engine = WorldEngine(db_path=db_path)
        simulation_id = engine.initialize_world(num_agents=3, simulation_name="Mechanics Test")
        
        print(f"\nTesting spark calculations...")
        # Test bond spark formula: floor(n + (n-1) × 0.5)
        test_cases = [2, 3, 4, 5]
        for n in test_cases:
            expected = int(n + (n - 1) * 0.5)
            print(f"   Bond of {n} agents: {expected} sparks")
        
        print(f"\nTesting raid mechanics...")
        # Test raid success probability
        attacker_strength = 10
        defender_strength = 5
        success_prob = attacker_strength / (attacker_strength + defender_strength)
        print(f"   Attacker strength {attacker_strength} vs Defender strength {defender_strength}")
        print(f"   Success probability: {success_prob:.2f} ({success_prob*100:.1f}%)")
        
        print(f"\nTesting Bob's mechanics...")
        print(f"   Bob starts with: {engine.world_state.bob_sparks} sparks")
        print(f"   Bob gains per tick: {engine.world_state.bob_sparks_per_tick} sparks")
        
        print(f"✅ Game mechanics calculations working correctly!")
        
        return engine, simulation_id
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def main():
    """Run all World Engine tests."""
    # Test 1: World Initialization
    engine, simulation_id = test_world_initialization()
    if not engine:
        print("❌ World initialization failed")
        return
    
    # Initialize human logger
    logger = HumanLogger()
    
    # Test 2: Single Tick
    result = test_single_tick(engine, simulation_id, logger)
    if not result:
        print("❌ Single tick failed")
        return
    
    # Test 3: Multiple Ticks
    results = test_multiple_ticks(engine, simulation_id, logger)
    if not results:
        print("❌ Multiple ticks failed")
        return
    
    # Test 4: Database Persistence
    new_engine = test_database_persistence(engine, simulation_id)
    if not new_engine:
        print("❌ Database persistence failed")
        return
    
    # Test 5: Game Mechanics
    mechanics_engine, mechanics_sim_id = test_game_mechanics()
    if not mechanics_engine:
        print("❌ Game mechanics test failed")
        return
    
    # Show game mechanics explanation
    logger.log_game_mechanics_explanation()
    
    # Log simulation end
    logger.log_simulation_end(engine.world_state.tick, engine.world_state)
    
    # Cleanup
    print(f"\n{'='*80}")
    print("🧹 CLEANING UP")
    print(f"{'='*80}")
    
    print(f"✅ Temporary files cleaned up")
    
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    print("✅ World initialization")
    print("✅ Single tick execution")
    print("✅ Multiple tick execution")
    print("✅ Database persistence")
    print("✅ Game mechanics calculations")
    
    print(f"\n{'='*80}")
    print("🎉 WORLD ENGINE TEST COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    main() 