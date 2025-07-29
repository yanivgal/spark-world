#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from character_designer.shard_sower_dspy import ShardSowerModule
from world.state import WorldState

def test_character_diversity():
    """Test character generation to see if we're getting diverse characters."""
    print("🧪 TESTING CHARACTER DIVERSITY")
    print("="*50)
    
    s = ShardSowerModule()
    w = WorldState()
    agents = []
    
    for i in range(5):  # Generate 5 characters
        agent = s.create_agent()  # Remove world_state parameter
        agents.append(agent)
        
        print(f"\n=== AGENT {i+1} ===")
        print(f"Name: {agent.name}")
        print(f"Species: {agent.species}")
        print(f"Personality: {agent.personality}")
        print(f"Goal: {agent.opening_goal}")
        print(f"Backstory: {agent.backstory[:80]}...")
        print(f"Realm: {agent.home_realm}")
        print(f"Quirk: {agent.quirk}")
    
    # Analyze diversity
    print(f"\n🔍 DIVERSITY ANALYSIS")
    print("="*30)
    
    species = [agent.species for agent in agents]
    personalities = [p for agent in agents for p in agent.personality]
    goals = [agent.opening_goal for agent in agents]
    realms = [agent.home_realm for agent in agents]
    
    print(f"Species: {species}")
    print(f"Personalities: {personalities}")
    print(f"Goals: {goals}")
    print(f"Realms: {realms}")
    
    # Check for repetition
    unique_species = len(set(species))
    unique_realms = len(set(realms))
    
    print(f"\n📊 STATS:")
    print(f"Unique species: {unique_species}/5")
    print(f"Unique realms: {unique_realms}/5")
    
    if unique_species < 4:
        print("⚠️  WARNING: Too many similar species!")
    if unique_realms < 4:
        print("⚠️  WARNING: Too many similar realms!")

if __name__ == "__main__":
    test_character_diversity()