#!/usr/bin/env python3
"""
Interactive Spark-World Simulation

This script runs a Spark-World simulation with pauses after each tick,
allowing you to read the output at your own pace.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world.world_engine import WorldEngine
from world.human_logger import HumanLogger
import tempfile


def run_interactive_simulation(num_agents: int = 3, num_ticks: int = 10, storyteller_personality: str = "blip"):
    """
    Run an interactive Spark-World simulation with pauses after each tick.
    
    Args:
        num_agents: Number of agents to start with
        num_ticks: Number of ticks to run
        storyteller_personality: Storyteller personality to use
    """
    
    # Create temporary database
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "interactive_simulation.db")
    
    try:
        # Initialize World Engine
        print("🚀 Initializing Spark-World...")
        engine = WorldEngine(db_path=db_path)
        
        # Reset all modules for fresh character generation
        engine.reset_all_modules()
        
        # Set storyteller personality
        engine.storyteller.personality = storyteller_personality
        
        # Initialize world
        simulation_id = engine.initialize_world(
            num_agents=num_agents, 
            simulation_name=f"Interactive Simulation ({storyteller_personality})"
        )
        
        # Initialize human logger
        logger = HumanLogger()
        
        # Show initial world state
        logger.log_simulation_start(engine.world_state)
        
        # Pause before starting
        print(f"\n{'='*80}")
        print("🎬 READY TO BEGIN SIMULATION")
        print(f"{'='*80}")
        print(f"   🌟 Starting with {num_agents} agents")
        print(f"   ⏰ Running for {num_ticks} ticks")
        print(f"   🎭 Storyteller: {storyteller_personality}")
        print(f"\n⏸️  Press any key to start the simulation...")
        print(f"{'='*80}")
        input()
        
        # Run simulation tick by tick
        for tick in range(1, num_ticks + 1):
            # Log tick start
            logger.log_tick_start(tick, engine.world_state)
            
            # Execute tick
            result = engine.tick(simulation_id)
            
            # Log tick result
            logger.log_tick_result(result, engine.world_state)
            
            # Show special events
            if result.agents_vanished:
                print(f"⚠️  Agents vanished in tick {tick}: {result.agents_vanished}")
            if result.agents_spawned:
                print(f"✨ Agents spawned in tick {tick}: {result.agents_spawned}")
            if result.bonds_formed:
                print(f"🤝 Bonds formed in tick {tick}:")
                for bond_id in result.bonds_formed:
                    bond = engine.world_state.bonds[bond_id]
                    member_names = [engine.world_state.agents[member_id].name for member_id in bond.members]
                    print(f"   • {', '.join(member_names)}")
            if result.bonds_dissolved:
                print(f"💔 Bonds dissolved in tick {tick}: {result.bonds_dissolved}")
            
            # Check for minds in danger
            minds_in_danger = [a for a in engine.world_state.agents.values() 
                              if a.status.value == 'alive' and a.sparks <= 2]
            if minds_in_danger:
                print(f"\n⚠️  MINDS IN DANGER:")
                for agent in minds_in_danger:
                    print(f"   🔴 {agent.name}: {agent.sparks} sparks remaining")
            
            # Check if simulation should end early
            alive_agents = [a for a in engine.world_state.agents.values() if a.status.value == 'alive']
            if len(alive_agents) == 0:
                print(f"\n💀 ALL MINDS HAVE VANISHED!")
                print(f"   The simulation ends early at tick {tick}")
                break
            
            # Pause for user input (except on the last tick)
            if tick < num_ticks:
                print(f"\n{'='*80}")
                print("⏸️  PAUSED - Press any key to continue to the next tick...")
                print(f"   (Or type 'quit' to end simulation early)")
                print(f"{'='*80}")
                user_input = input().strip().lower()
                if user_input == 'quit':
                    print(f"\n🛑 Simulation ended early by user at tick {tick}")
                    break
        
        # Show final statistics
        logger.log_simulation_end(engine.world_state.tick, engine.world_state)
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        try:
            import shutil
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Temporary files cleaned up")
        except:
            pass


def main():
    """Main function to run interactive simulation."""
    print("🌟 SPARK-WORLD INTERACTIVE SIMULATION 🌟")
    print("="*80)
    
    # Ask if user wants to start fresh
    print("\n🔄 DATABASE OPTIONS:")
    print("1. Start fresh (clear all previous data)")
    print("2. Continue with existing data")
    
    try:
        choice = input("\nChoose option (1 or 2): ").strip()
        if choice == "1":
            print("🗑️  Clearing database and starting fresh...")
            # This will be handled by the temporary database
        elif choice == "2":
            print("📚 Continuing with existing data...")
        else:
            print("⚠️  Invalid choice. Starting fresh.")
    except (EOFError, KeyboardInterrupt):
        print("\n⚠️  Starting fresh.")
    
    # Get user preferences
    print("\n🎛️  SIMULATION SETTINGS")
    print("="*40)
    
    # Number of agents
    try:
        num_agents = int(input("Number of agents (default 3): ") or "3")
        if num_agents < 1 or num_agents > 10:
            print("⚠️  Number of agents should be between 1-10. Using 3.")
            num_agents = 3
    except ValueError:
        print("⚠️  Invalid input. Using 3 agents.")
        num_agents = 3
    
    # Number of ticks
    try:
        num_ticks = int(input("Number of ticks (default 10): ") or "10")
        if num_ticks < 1 or num_ticks > 50:
            print("⚠️  Number of ticks should be between 1-50. Using 10.")
            num_ticks = 10
    except ValueError:
        print("⚠️  Invalid input. Using 10 ticks.")
        num_ticks = 10
    
    # Storyteller personality - THE HEART OF YOUR EXPERIENCE
    print(f"\n" + "="*60)
    print(f"🎭 CHOOSE YOUR STORYTELLER 🎭")
    print(f"="*60)
    print(f"Your storyteller will be your guide through Spark-World.")
    print(f"They'll interpret every moment, every choice, every emotion.")
    print(f"Choose the voice that speaks to your soul...")
    print()
    
    personalities = ["blip", "eloa", "krunch"]
    personality_descriptions = {
        "blip": "🤖 THE SAVAGE COMEDIAN\n   An android stand-up comic with razor-sharp wit and brutal sarcasm.\n   Uses biting humor to process emotional confusion and delivers savage\n   emotional gut-punches. Hates everything but secretly cares too much.\n   Perfect for: Dark humor lovers who appreciate brutal honesty.",
        "eloa": "🎨 THE GENTLE POET\n   A blind painter who feels and paints the world through memory,\n   sound, and emotion. Gentle and soft-spoken, each sentence flows\n   like brushstrokes on canvas. Sees beauty in everything.\n   Perfect for: Those who love poetic, sensory storytelling.",
        "krunch": "⚔️  THE WISE WARRIOR\n   A barbarian who accidentally became a philosopher. Blunt, honest,\n   and unintentionally profound. Talks like he fights: with impact.\n   Sees straight to the heart of things with simple wisdom.\n   Perfect for: Those who appreciate direct, powerful insights."
    }
    
    for i, personality in enumerate(personalities, 1):
        print(f"   {i}. {personality.upper()} - {personality_descriptions[personality]}")
        print()
    
    print(f"💭 Your storyteller will shape how you experience every moment...")
    print()
    
    try:
        choice = int(input("Choose your storyteller (1-3, default 1): ") or "1")
        if 1 <= choice <= 3:
            storyteller_personality = personalities[choice - 1]
            print(f"\n✨ You chose {storyteller_personality.upper()} as your storyteller!")
        else:
            print("⚠️  Invalid choice. Using blip.")
            storyteller_personality = "blip"
    except ValueError:
        print("⚠️  Invalid input. Using blip.")
        storyteller_personality = "blip"
    
    print(f"\n🎬 STARTING SIMULATION")
    print(f"   🌟 Agents: {num_agents}")
    print(f"   ⏰ Ticks: {num_ticks}")
    print(f"   🎭 Storyteller: {storyteller_personality}")
    
    # Run the simulation
    run_interactive_simulation(num_agents, num_ticks, storyteller_personality)


if __name__ == "__main__":
    main() 