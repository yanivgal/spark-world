#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from character_designer.shard_sower_dspy import ShardSowerModule
from character_designer.multi_module_sower import MultiModuleShardSower
from world.state import WorldState

def test_multi_module_diversity():
    """Test the new multi-module character generation system."""
    print("🧪 TESTING MULTI-MODULE CHARACTER DIVERSITY")
    print("="*60)
    
    # Test the new multi-module approach
    multi_sower = MultiModuleShardSower()
    agents = []
    
    for i in range(5):  # Generate 5 characters
        agent = multi_sower.create_agent()
        agents.append(agent)
        
        print(f"\n=== AGENT {i+1} (Multi-Module) ===")
        print(f"Name: {agent.name}")
        print(f"Species: {agent.species}")
        print(f"Personality: {agent.personality}")
        print(f"Goal: {agent.opening_goal}")
        print(f"Backstory: {agent.backstory[:80]}...")
        print(f"Realm: {agent.home_realm}")
        print(f"Quirk: {agent.quirk}")
    
    # Analyze diversity
    print(f"\n🔍 MULTI-MODULE DIVERSITY ANALYSIS")
    print("="*40)
    
    species = [agent.species for agent in agents]
    personalities = [p for agent in agents for p in agent.personality]
    goals = [agent.opening_goal for agent in agents]
    realms = [agent.home_realm for agent in agents]
    names = [agent.name for agent in agents]
    quirks = [agent.quirk for agent in agents]
    
    print(f"Names: {names}")
    print(f"Species: {species}")
    print(f"Personalities: {personalities}")
    print(f"Goals: {goals}")
    print(f"Realms: {realms}")
    print(f"Quirks: {quirks}")
    
    # Check for repetition
    unique_species = len(set(species))
    unique_realms = len(set(realms))
    unique_names = len(set(names))
    
    print(f"\n📊 MULTI-MODULE STATS:")
    print(f"Unique names: {unique_names}/5")
    print(f"Unique species: {unique_species}/5")
    print(f"Unique realms: {unique_realms}/5")
    
    # Name pattern analysis
    name_patterns = [len(name.split()) for name in names]
    print(f"Name patterns: {name_patterns}")
    
    # Goal verb analysis
    goal_verbs = [goal.split()[0].lower() for goal in goals]
    print(f"Goal verbs: {goal_verbs}")
    
    # Personality repetition analysis
    personality_counts = {}
    for trait in personalities:
        trait_lower = trait.lower()
        personality_counts[trait_lower] = personality_counts.get(trait_lower, 0) + 1
    
    repeated_traits = {trait: count for trait, count in personality_counts.items() if count > 1}
    print(f"Repeated personality traits: {repeated_traits}")
    
    if unique_species < 4:
        print("⚠️  WARNING: Too many similar species!")
    if unique_realms < 4:
        print("⚠️  WARNING: Too many similar realms!")
    if len(repeated_traits) > 2:
        print("⚠️  WARNING: Too many repeated personality traits!")

def compare_approaches():
    """Compare the original vs multi-module approach."""
    print("\n" + "="*80)
    print("🔄 COMPARING ORIGINAL vs MULTI-MODULE APPROACH")
    print("="*80)
    
    # Test original approach
    print("\n📋 ORIGINAL SINGLE-MODULE APPROACH:")
    original_sower = ShardSowerModule()
    original_agents = []
    
    for i in range(3):
        agent = original_sower.create_agent()
        original_agents.append(agent)
        print(f"  {i+1}. {agent.name} ({len(agent.name.split())} words) - {agent.species[:30]}...")
    
    # Test multi-module approach
    print("\n🔧 MULTI-MODULE APPROACH:")
    multi_sower = MultiModuleShardSower()
    multi_agents = []
    
    for i in range(3):
        agent = multi_sower.create_agent()
        multi_agents.append(agent)
        print(f"  {i+1}. {agent.name} ({len(agent.name.split())} words) - {agent.species[:30]}...")
    
    # Compare diversity
    print("\n📊 DIVERSITY COMPARISON:")
    
    # Name patterns
    original_patterns = [len(agent.name.split()) for agent in original_agents]
    multi_patterns = [len(agent.name.split()) for agent in multi_agents]
    
    print(f"Original name patterns: {original_patterns}")
    print(f"Multi-module name patterns: {multi_patterns}")
    
    # Species variety
    original_species = [agent.species for agent in original_agents]
    multi_species = [agent.species for agent in multi_agents]
    
    print(f"Original species variety: {len(set(original_species))}/3")
    print(f"Multi-module species variety: {len(set(multi_species))}/3")
    
    # Goal variety
    original_goals = [agent.opening_goal.split()[0].lower() for agent in original_agents]
    multi_goals = [agent.opening_goal.split()[0].lower() for agent in multi_agents]
    
    print(f"Original goal verbs: {original_goals}")
    print(f"Multi-module goal verbs: {multi_goals}")

if __name__ == "__main__":
    test_multi_module_diversity()
    compare_approaches()