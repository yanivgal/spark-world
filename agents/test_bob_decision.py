#!/usr/bin/env python3
"""
Test script for the Bob Decision Module.

This script tests Bob's decision-making process with various scenarios
to ensure the module works correctly and produces expected outputs.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize DSPy first
from character_designer.dspy_init import get_dspy
get_dspy()  # This will configure DSPy with the LLM

from agents.bob_decision import BobDecisionModule
from communication.messages.action_message import ActionMessage
from world.simulation_mechanics import BobResponse


def create_test_spark_requests(scenario: str = "basic") -> list[ActionMessage]:
    """
    Create test spark requests for different scenarios.
    
    Args:
        scenario: Type of scenario to test ("basic", "multiple", "desperate", "mixed")
        
    Returns:
        List[ActionMessage]: Test spark request messages
    """
    
    if scenario == "basic":
        # Basic scenario - single request
        return [
            ActionMessage(
                agent_id="test_agent_001",
                intent="request_spark",
                target=None,
                content="I need help to survive",
                reasoning="I'm running low on sparks and need assistance"
            )
        ]
    
    elif scenario == "multiple":
        # Multiple agents requesting
        return [
            ActionMessage(
                agent_id="agent_001",
                intent="request_spark",
                target=None,
                content="Please help me, I'm desperate",
                reasoning="I only have 1 spark left and need help to survive"
            ),
            ActionMessage(
                agent_id="agent_002",
                intent="request_spark",
                target=None,
                content="I would appreciate some sparks for my mission",
                reasoning="I'm working on an important mission and need extra sparks"
            ),
            ActionMessage(
                agent_id="agent_003",
                intent="request_spark",
                target=None,
                content="Can you spare a few sparks?",
                reasoning="I'm doing okay but could use a boost"
            )
        ]
    
    elif scenario == "desperate":
        # Desperate agents with urgent requests
        return [
            ActionMessage(
                agent_id="desperate_001",
                intent="request_spark",
                target=None,
                content="I'm about to vanish! Please help!",
                reasoning="I have 0 sparks and will vanish next tick without help"
            ),
            ActionMessage(
                agent_id="desperate_002",
                intent="request_spark",
                target=None,
                content="I'm begging for your mercy",
                reasoning="I only have 1 spark left and am very scared"
            ),
            ActionMessage(
                agent_id="desperate_003",
                intent="request_spark",
                target=None,
                content="Help me survive another day",
                reasoning="I have 2 sparks and need help to continue"
            )
        ]
    
    elif scenario == "mixed":
        # Mixed scenario with different types of requests
        return [
            ActionMessage(
                agent_id="noble_001",
                intent="request_spark",
                target=None,
                content="I seek your wisdom and generosity",
                reasoning="I am a noble being seeking to help others"
            ),
            ActionMessage(
                agent_id="greedy_001",
                intent="request_spark",
                target=None,
                content="Give me all your sparks!",
                reasoning="I want more power and don't care about others"
            ),
            ActionMessage(
                agent_id="humble_001",
                intent="request_spark",
                target=None,
                content="If you can spare any, I would be grateful",
                reasoning="I'm humble and will accept whatever you can give"
            ),
            ActionMessage(
                agent_id="mission_001",
                intent="request_spark",
                target=None,
                content="I need sparks to complete my mission",
                reasoning="I'm on an important mission to help my bond"
            )
        ]
    
    else:
        raise ValueError(f"Unknown scenario: {scenario}")


def print_bob_understanding(bob_sparks: int, tick: int, requests: list[ActionMessage]):
    """
    Print a beautiful explanation of Bob's understanding of the situation.
    
    Args:
        bob_sparks: Bob's current spark count
        tick: Current simulation tick
        requests: List of spark requests
    """
    
    print(f"\n{'🌟' * 20} BOB'S UNDERSTANDING {'🌟' * 20}")
    
    # Bob's State
    print(f"\n👤 WHO AM I?")
    print(f"   I am Bob, the silent Sparkbearer, an immortal wanderer.")
    print(f"   I carry the essence of life itself in my hands.")
    print(f"   I cannot use sparks for myself - I can only give.")
    print(f"   I am currently at tick {tick} of the simulation.")
    
    # Bob's Resources
    print(f"\n⚡ MY CURRENT STATE")
    print(f"   I have {bob_sparks} sparks in my possession.")
    if bob_sparks > 0:
        print(f"   I can grant up to 5 sparks per request.")
        print(f"   I can choose which requests to grant and how much to give.")
    else:
        print(f"   I have no sparks to give - I must ignore all requests.")
    
    # Requests Analysis
    print(f"\n🙏 REQUESTS I RECEIVED")
    print(f"   {len(requests)} agents have asked for my help:")
    
    for i, request in enumerate(requests, 1):
        print(f"   {i}. {request.agent_id}: \"{request.content}\"")
        print(f"      Reasoning: {request.reasoning}")
    
    # Decision Factors
    print(f"\n🧠 WHAT I MUST CONSIDER")
    print(f"   • Urgency: How desperate is each agent?")
    print(f"   • Fairness: Are some more worthy than others?")
    print(f"   • Whimsy: My mysterious, unpredictable nature")
    print(f"   • Capacity: I can only give what I have")
    print(f"   • Distribution: How should I spread my generosity?")
    
    # Possible Strategies
    print(f"\n🎯 POSSIBLE STRATEGIES")
    if bob_sparks > 0:
        print(f"   • Equal distribution: Give {bob_sparks // len(requests)} to each")
        print(f"   • Selective giving: Choose the most deserving")
        print(f"   • Generous giving: Give maximum to those in need")
        print(f"   • Conservative giving: Give minimum to many")
        print(f"   • Ignore some: Focus on a few chosen ones")
    else:
        print(f"   • I must ignore all requests until I gain more sparks")
    
    print(f"\n{'🌟' * 20} END OF BOB'S UNDERSTANDING {'🌟' * 20}")


def print_bob_decisions(responses: list[BobResponse], bob_sparks_before: int):
    """
    Print Bob's decisions in a beautiful format.
    
    Args:
        responses: Bob's responses to requests
        bob_sparks_before: Bob's spark count before decisions
    """
    
    print(f"\n{'🎁' * 20} BOB'S DECISIONS {'🎁' * 20}")
    
    total_granted = sum(response.sparks_granted for response in responses)
    bob_sparks_after = bob_sparks_before - total_granted
    
    print(f"\n📊 OVERALL SUMMARY")
    print(f"   Bob started with: {bob_sparks_before} sparks")
    print(f"   Bob granted: {total_granted} sparks total")
    print(f"   Bob has remaining: {bob_sparks_after} sparks")
    print(f"   Requests processed: {len(responses)}")
    
    # Individual Decisions
    print(f"\n🎯 INDIVIDUAL DECISIONS")
    for i, response in enumerate(responses, 1):
        status = "✅ GRANTED" if response.sparks_granted > 0 else "❌ IGNORED"
        print(f"   {i}. {response.requesting_agent_id}: {status}")
        print(f"      Request: \"{response.request_content}\"")
        print(f"      Sparks granted: {response.sparks_granted}")
        print(f"      Bob's reasoning: {response.reasoning}")
        print(f"      Bob's sparks: {response.bob_sparks_before} → {response.bob_sparks_after}")
        print()
    
    # Analysis
    print(f"\n📈 DECISION ANALYSIS")
    granted_count = sum(1 for r in responses if r.sparks_granted > 0)
    ignored_count = len(responses) - granted_count
    
    print(f"   Requests granted: {granted_count}")
    print(f"   Requests ignored: {ignored_count}")
    
    if granted_count > 0:
        avg_granted = total_granted / granted_count
        print(f"   Average sparks per granted request: {avg_granted:.1f}")
        
        max_granted = max(r.sparks_granted for r in responses)
        min_granted = min(r.sparks_granted for r in responses if r.sparks_granted > 0)
        print(f"   Maximum granted to single agent: {max_granted}")
        print(f"   Minimum granted to single agent: {min_granted}")
    
    print(f"\n{'🎁' * 20} END OF BOB'S DECISIONS {'🎁' * 20}")


def test_bob_decision(scenario: str = "basic", bob_sparks: int = 10, tick: int = 5):
    """
    Test Bob's decision module with a specific scenario.
    
    Args:
        scenario: Scenario to test
        bob_sparks: Bob's current spark count
        tick: Current simulation tick
    """
    print(f"\n{'='*80}")
    print(f"🌟 TESTING BOB SCENARIO: {scenario.upper()} 🌟")
    print(f"{'='*80}")
    
    # Create test requests
    requests = create_test_spark_requests(scenario)
    
    # Show Bob's understanding
    print_bob_understanding(bob_sparks, tick, requests)
    
    # Initialize Bob decision module
    print(f"\n{'='*50}")
    print("🤖 PROCESSING BOB'S DECISIONS...")
    print(f"{'='*50}")
    
    try:
        bob_decision_module = BobDecisionModule()
        responses = bob_decision_module.process_spark_requests(
            bob_sparks=bob_sparks,
            tick=tick,
            request_messages=requests
        )
        
        # Show Bob's decisions
        print_bob_decisions(responses, bob_sparks)
        
        return responses
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_bob_edge_cases():
    """Test Bob's behavior in edge cases."""
    print(f"\n{'='*80}")
    print(f"🔍 TESTING BOB EDGE CASES 🔍")
    print(f"{'='*80}")
    
    # Test 1: Bob has 0 sparks
    print(f"\n--- EDGE CASE 1: Bob has 0 sparks ---")
    test_bob_decision("desperate", bob_sparks=0, tick=10)
    
    # Test 2: Bob has exactly 5 sparks for 3 requests
    print(f"\n--- EDGE CASE 2: Bob has exactly 5 sparks for 3 requests ---")
    test_bob_decision("multiple", bob_sparks=5, tick=10)
    
    # Test 3: Bob has 20 sparks for 2 requests
    print(f"\n--- EDGE CASE 3: Bob has 20 sparks for 2 requests ---")
    test_bob_decision("basic", bob_sparks=20, tick=10)
    
    # Test 4: No requests
    print(f"\n--- EDGE CASE 4: No requests ---")
    test_bob_decision("basic", bob_sparks=10, tick=10)
    # This will return empty list


def main():
    """Run all test scenarios."""
    print("🌟 SPARK-WORLD BOB DECISION MODULE TEST 🌟")
    print("=" * 80)
    
    scenarios = ["basic", "multiple", "desperate", "mixed"]
    
    results = {}
    for scenario in scenarios:
        try:
            result = test_bob_decision(scenario, bob_sparks=15, tick=10)
            results[scenario] = result
        except Exception as e:
            print(f"Failed to test scenario {scenario}: {e}")
            results[scenario] = None
    
    # Test edge cases
    test_bob_edge_cases()
    
    print(f"\n{'='*80}")
    print("📊 TEST SUMMARY")
    print(f"{'='*80}")
    
    for scenario, result in results.items():
        if result is None:
            status = "❌ FAILED"
            granted_count = 0
        else:
            status = "✅ PASSED"
            granted_count = sum(1 for r in result if r.sparks_granted > 0)
        
        print(f"{scenario.upper()}: {status}")
        if result:
            total_granted = sum(r.sparks_granted for r in result)
            print(f"  Requests: {len(result)}, Granted: {granted_count}, Total sparks: {total_granted}")
    
    print(f"\n{'='*80}")
    print("🎉 BOB DECISION MODULE TEST COMPLETE")
    print(f"{'='*80}")


if __name__ == "__main__":
    main() 