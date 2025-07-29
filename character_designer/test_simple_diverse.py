#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from character_designer.simple_diverse_sower import SimpleDiverseSower

def test_simple_diverse():
    """Test the simple diverse character generation."""
    print("🧪 TESTING SIMPLE DIVERSE CHARACTER GENERATION")
    print("="*60)
    
    s = SimpleDiverseSower()
    agents = []
    
    for i in range(5):
        agent = s.create_agent()
        agents.append(agent)
        
        print(f"\n=== AGENT {i+1} ===")
        print(f"Name: {agent.name}")
        print(f"Species: {agent.species}")
        print(f"Personality: {agent.personality}")
        print(f"Goal: {agent.opening_goal}")
        print(f"Quirk: {agent.quirk}")
        print(f"Realm: {agent.home_realm}")
        print(f"Backstory: {agent.backstory[:80]}...")
    
    # Analysis
    print(f"\n🔍 DIVERSITY ANALYSIS")
    print("="*30)
    
    names = [agent.name for agent in agents]
    species = [agent.species for agent in agents]
    personalities = [p for agent in agents for p in agent.personality]
    goals = [agent.opening_goal for agent in agents]
    realms = [agent.home_realm for agent in agents]
    
    print(f"Names: {names}")
    print(f"Name patterns: {[len(name.split()) for name in names]}")
    print(f"Cultures used: {list(s.used_cultures)}")
    print(f"Species types: {s.used_species}")
    print(f"Personalities: {list(s.used_personalities)}")
    print(f"Goals: {goals}")
    print(f"Realms: {realms}")
    
    # Check diversity
    unique_names = len(set(names))
    unique_realms = len(set(realms))
    unique_cultures = len(s.used_cultures)
    
    print(f"\n📊 STATS:")
    print(f"Unique names: {unique_names}/5")
    print(f"Unique realms: {unique_realms}/5")
    print(f"Unique cultures: {unique_cultures}/5")
    
    if unique_names < 5:
        print("⚠️  WARNING: Name repetition!")
    if unique_realms < 4:
        print("⚠️  WARNING: Realm repetition!")
    if unique_cultures < 4:
        print("⚠️  WARNING: Cultural repetition!")

if __name__ == "__main__":
    test_simple_diverse()