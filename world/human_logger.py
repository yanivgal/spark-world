#!/usr/bin/env python3
"""
Human-Readable Logger for Spark-World

This module transforms technical simulation data into engaging, narrative output
that humans can easily understand and enjoy reading.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dspy
from dataclasses import dataclass
from typing import List, Dict, Optional

from world.state import WorldState, AgentStatus, BondStatus
from world.world_engine import TickResult
from communication.messages.action_message import ActionMessage
from communication.messages.mission_meeting_message import MissionMeetingMessage
from storytelling.storyteller_structures import StorytellerOutput
from character_designer.dspy_init import get_dspy

class IntroductionSignature(dspy.Signature):
    """
    Generate a captivating, one-paragraph introduction to Spark-World that immediately hooks the reader.
    
    This should be the first thing a human sees when they encounter Spark-World. It needs to be:
    - Short and punchy (2-3 sentences max)
    - Immediately engaging and mysterious
    - Use simple, everyday words that flow naturally
    - Capture the core essence: life as energy, emergent drama, unique characters
    - Make the reader want to see what happens next
    - Avoid fancy words, complex sentences, or flowery language
    
    IMPORTANT: Write like you're telling a friend about an exciting new world. Use simple words that everyone understands. Make it feel like the opening of a great story - mysterious, compelling, and easy to read.
    
    The tone should be conversational and exciting, not academic or poetic.
    """
    
    num_agents: int = dspy.InputField(desc="Number of agents in this simulation")
    agent_names: str = dspy.InputField(desc="Names of the agents to mention")
    agent_species: str = dspy.InputField(desc="Species/types of the agents")
    
    introduction: str = dspy.OutputField(desc="A simple, captivating introduction that hooks the reader immediately using everyday words")

class HumanLogger:
    """
    Transforms Spark-World simulation data into human-readable narrative.
    """
    
    def __init__(self):
        """Initialize the Human Logger."""
        get_dspy()  # Configure DSPy
        self.introduction_generator = dspy.Predict(IntroductionSignature)
        self.character_intros_shown = False
        self.tick_count = 0
    
    def log_simulation_start(self, world_state: WorldState, simulation_name: str = "Spark-World"):
        """Log the start of a simulation with a captivating introduction."""
        print(f"\n{'='*80}")
        print(f"🌟 WELCOME TO {simulation_name.upper()} 🌟")
        print(f"{'='*80}")
        
        # Generate dynamic introduction using LLM
        agent_names = ", ".join([agent.name for agent in world_state.agents.values()])
        agent_species = ", ".join([agent.species for agent in world_state.agents.values()])
        
        intro_result = self.introduction_generator(
            num_agents=len(world_state.agents),
            agent_names=agent_names,
            agent_species=agent_species
        )
        
        print(f"\n{intro_result.introduction}\n")
        
        # Show character introductions
        self._show_character_introductions(world_state)
    
    def _show_character_introductions(self, world_state: WorldState):
        """Show engaging character introductions."""
        print(f"{'='*80}")
        print(f"🤖 MEET THE MINDS")
        print(f"{'='*80}\n")
        
        for agent_id, agent in world_state.agents.items():
            # Create personality summary
            personality_str = ", ".join(agent.personality[:3])  # Show first 3 traits
            
            print(f"✨ {agent.name} ({agent.species})")
            print(f"   🏠 From: {agent.home_realm}")
            print(f"   💭 Personality: {personality_str}")
            print(f"   🎭 Quirk: {agent.quirk}")
            print(f"   ⚡ Ability: {agent.ability}")
            print(f"   🎯 Goal: {agent.opening_goal}")
            print(f"   📖 Backstory: {agent.backstory}")
            print()
        
        self.character_intros_shown = True
    

    
    def log_tick_start(self, tick_number: int, world_state: WorldState):
        """Log the start of a new tick."""
        print(f"\n{'='*80}")
        print(f"⏰ TICK {tick_number}")
        print(f"{'='*80}")
        
        # World status
        living_agents = [agent for agent in world_state.agents.values() if agent.status == AgentStatus.ALIVE]
        bonded_agents = [agent for agent in living_agents if agent.bond_status == BondStatus.BONDED]
        
        print(f"\n📊 WORLD STATUS")
        print(f"   🌟 Living minds: {len(living_agents)}")
        print(f"   🤝 Bonded minds: {len(bonded_agents)}")
        print(f"   🎁 Bob's sparks: {world_state.bob_sparks} (gains 1/tick)")
        print(f"   🔗 Active bonds: {len(world_state.bonds)}")
        
        # Spark status (after upkeep costs)
        print(f"\n⚡ SPARK STATUS")
        for agent in living_agents:
            if agent.sparks <= 1:
                status = "[💀 CRITICAL]"
            elif agent.sparks <= 2:
                status = "[🟡 DANGER]"
            else:
                status = "[🟢 SAFE]"
            
            bond_info = ""
            if agent.bond_status == BondStatus.BONDED:
                bond_info = " (bonded)"
            
            print(f"   {status} {agent.name}: {agent.sparks} sparks (age {agent.age}){bond_info}")
        
        print(f"\n{'='*80}")
        print(f"📖 TICK {tick_number} EVENTS")
        print(f"{'='*80}")
        
    def log_tick_result(self, result: TickResult, world_state: WorldState):
        """Log tick results in human-readable narrative format."""
        # Log agent actions
        if result.agent_actions:
            self._log_agent_actions(result.agent_actions, world_state)
        
        # Log action consequences
        self._log_action_consequences(result, world_state)
        
        # Log mission meetings
        if world_state.mission_meeting_messages:
            self._log_mission_meetings(world_state.mission_meeting_messages, world_state)
        
        # Log storyteller narrative
        if world_state.storyteller_output:
            self._log_storyteller_narrative(world_state.storyteller_output)
        
        # Log end of tick summary
        print(f"\n{'='*80}")
        print(f"📊 END OF TICK {result.tick}")
        print(f"{'='*80}")
        
        living_agents = [agent for agent in world_state.agents.values() if agent.status == AgentStatus.ALIVE]
        total_sparks = sum(agent.sparks for agent in living_agents)
        
        print(f"   🌟 Living minds: {len(living_agents)}")
        print(f"   ⚡ Total sparks: {total_sparks}")
        print(f"   🎁 Bob's sparks: {world_state.bob_sparks}")
        print(f"   🔗 Active bonds: {len(world_state.bonds)}")
        print(f"{'='*80}")
    
    def _log_action_consequences(self, result: TickResult, world_state: WorldState):
        """Log the consequences of agent actions."""
        print(f"\n⚡ ACTION CONSEQUENCES")
        print(f"   ───────────────────────────────────────────────────────────")
        
        # Log bond formations
        if result.bonds_formed:
            print(f"   🤝 BONDS FORMED")
            for bond_id in result.bonds_formed:
                bond = world_state.bonds[bond_id]
                member_names = [world_state.agents[member_id].name for member_id in bond.members]
                print(f"      {', '.join(member_names)} formed a bond!")
        
        # Log bond dissolutions
        if result.bonds_dissolved:
            print(f"   💔 BONDS DISSOLVED")
            for bond_id in result.bonds_dissolved:
                print(f"      Bond {bond_id} dissolved")
        
        # Log bond requests
        if world_state.pending_bond_requests:
            print(f"   💌 BOND REQUESTS")
            for target_id, request in world_state.pending_bond_requests.items():
                requester = world_state.agents[request.agent_id]
                target = world_state.agents[target_id]
                print(f"      💌 {requester.name} → {target.name}")
                print(f"         \"{request.content}\"")
        
        # Log spark distribution
        if result.total_sparks_minted > 0:
            print(f"   ✨ SPARK DISTRIBUTION")
            print(f"      Bonds generated {result.total_sparks_minted} new sparks")
        
        # Log raids
        if result.total_raids_attempted > 0:
            print(f"   ⚔️ RAID RESULTS")
            print(f"      {result.total_raids_attempted} raids attempted")
        
        # Log Bob donations
        if hasattr(world_state, 'bob_donations') and world_state.bob_donations:
            print(f"   🎁 BOB'S DONATIONS")
            for donation in world_state.bob_donations:
                agent = world_state.agents[donation['agent_id']]
                print(f"      {agent.name} received {donation['amount']} sparks from Bob")
    
    def _log_mission_meetings(self, meeting_messages: List, world_state: WorldState):
        """Log mission meetings with structured flow."""
        if not meeting_messages:
            return
            
        print(f"\n🤝 MISSION MEETINGS")
        
        # Group messages by mission
        missions = {}
        for message in meeting_messages:
            if hasattr(message, 'mission_id'):
                if message.mission_id not in missions:
                    missions[message.mission_id] = []
                missions[message.mission_id].append(message)
        
        for mission_id, messages in missions.items():
            # Get mission details
            mission = None
            for m in world_state.missions.values():
                if m.mission_id == mission_id:
                    mission = m
                    break
            
            if mission:
                print(f"\n   🎯 MISSION: {mission.title}")
                print(f"   📋 Goal: {mission.goal}")
                print(f"   📊 Progress: {mission.current_progress}")
                
                # Show meeting flow in a cleaner format
                print(f"   💬 MEETING FLOW:")
                
                # Group by message type
                leader_intro = [m for m in messages if hasattr(m, 'message_type') and m.message_type == 'leader_introduction']
                leader_opening = [m for m in messages if hasattr(m, 'message_type') and m.message_type == 'leader_opening']
                agent_responses = [m for m in messages if hasattr(m, 'message_type') and m.message_type == 'agent_response']
                task_assignment = [m for m in messages if hasattr(m, 'message_type') and m.message_type == 'task_assignment']
                
                # Show leader introduction (first tick only)
                if leader_intro:
                    leader = world_state.agents[leader_intro[0].sender_id]
                    print(f"      👑 {leader.name} (Leader Introduction):")
                    print(f"         \"{leader_intro[0].content}\"")
                
                # Show leader opening
                if leader_opening:
                    leader = world_state.agents[leader_opening[0].sender_id]
                    print(f"      🎤 {leader.name} (Leader Opening):")
                    print(f"         \"{leader_opening[0].content}\"")
                
                # Show agent responses
                if agent_responses:
                    print(f"      💭 Team Responses:")
                    for response in agent_responses:
                        agent = world_state.agents[response.sender_id]
                        print(f"         • {agent.name}: \"{response.content}\"")
                
                # Show task assignment
                if task_assignment:
                    leader = world_state.agents[task_assignment[0].sender_id]
                    print(f"      📝 {leader.name} (Task Assignment):")
                    print(f"         \"{task_assignment[0].content}\"")
                
                # Show task assignments if available
                if mission.assigned_tasks:
                    print(f"      📋 TASK ASSIGNMENTS:")
                    for agent_id, task in mission.assigned_tasks.items():
                        if agent_id in world_state.agents:
                            agent = world_state.agents[agent_id]
                            print(f"         • {agent.name}: {task}")
            else:
                # Fallback for messages without mission context
                for message in messages:
                    agent = world_state.agents[message.sender_id]
                    print(f"   💬 {agent.name}: {message.content}")
    
    def _log_storyteller_narrative(self, storyteller_output):
        """Log the Storyteller's narrative."""
        print(f"\n📖 STORYTELLER'S TALE")
        print(f"   📚 Chapter: {storyteller_output.chapter_title}")
        
        # Print the main narrative
        print(f"\n   {storyteller_output.narrative_text}")
        
        # Print character insights if available
        if storyteller_output.character_insights:
            print(f"\n   💭 CHARACTER INSIGHTS:")
            for insight in storyteller_output.character_insights:
                print(f"      ✨ {insight['agent_name']}:")
                print(f"         💡 Motivation: {insight['motivation']}")
                print(f"         💔 Emotional State: {insight['emotional_state']}")
                print(f"         🌱 Growth: {insight['growth']}")
                print(f"         🔮 Potential: {insight['potential']}")
        
        # Print themes explored
        if storyteller_output.themes_explored:
            print(f"\n   🎯 THEMES EXPLORED:")
            for theme in storyteller_output.themes_explored:
                print(f"      • {theme}")
    
    def _log_spark_minting(self, result: TickResult, world_state: WorldState):
        """Log spark minting from bonds."""
        print(f"\n✨ SPARK MINTING")
        print(f"   Bonds generated {result.total_sparks_minted} new sparks")
    
    def _log_agent_actions(self, actions: List[ActionMessage], world_state: WorldState):
        """Log agent actions and reasoning."""
        print(f"\n🧠 AGENT DECISIONS\n")
        for action in actions:
            agent = world_state.agents[action.agent_id]
            print(f"   🤔 {agent.name} decides to {action.intent}")
            if action.target:
                # Clean target field - extract just the agent_id if it contains comments
                clean_target = action.target.split('#')[0].split('because')[0].strip()
                if clean_target in world_state.agents:
                    target = world_state.agents[clean_target]
                    print(f"      🎯 Target: {target.name}")
                else:
                    print(f"      🎯 Target: {action.target} (invalid agent_id)")
            if action.content:
                if action.intent == "message" and action.target:
                    clean_target = action.target.split('#')[0].split('because')[0].strip()
                    if clean_target in world_state.agents:
                        target = world_state.agents[clean_target]
                        print(f"      💬 Message to {target.name}: \"{action.content}\"")
                    else:
                        print(f"      💬 Message: \"{action.content}\"")
                else:
                    print(f"      💬 Message: \"{action.content}\"")
            if action.reasoning:
                print(f"      💭 Reasoning: {action.reasoning}")
            print()
    
    def _log_spark_distribution(self, result: TickResult, world_state: WorldState):
        """Log spark distribution within bonds."""
        print(f"\n⚡ SPARK DISTRIBUTION")
        print(f"   {result.total_sparks_minted} sparks distributed randomly within bonds")
    
    def _log_upkeep_costs(self, result: TickResult, world_state: WorldState):
        """Log the cost of existence in human terms."""
        print(f"\n💀 UPKEEP COSTS")
        print(f"   Every mind spends 1 spark to continue existing")
        print(f"   Total cost: {result.total_sparks_lost} sparks")
        
        # Show individual agent changes
        for agent in world_state.agents.values():
            if agent.status.value == "alive":
                print(f"   ⚡ {agent.name} loses 1 spark")
    
    def _log_bob_donations(self, donations: List[Dict], world_state: WorldState):
        """Log Bob's generosity."""
        print(f"\n🎁 BOB'S GENEROSITY")
        
        for donation in donations:
            data = donation['data']
            recipient_id = data['to_entity']
            amount = data['amount']
            reason = data['reason']
            
            recipient = world_state.agents[recipient_id]
            print(f"   🎁 Bob grants {amount} sparks to {recipient.name}")
            print(f"   💭 \"{reason}\"")
    
    def log_simulation_end(self, final_tick: int, world_state: WorldState):
        """Log the end of simulation."""
        print(f"\n{'='*80}")
        print(f"🏁 SIMULATION COMPLETE")
        print(f"{'='*80}")
        
        alive_agents = [a for a in world_state.agents.values() if a.status.value == "alive"]
        vanished_agents = [a for a in world_state.agents.values() if a.status.value == "vanished"]
        
        print(f"\n📊 FINAL STATISTICS")
        print(f"   🌟 Minds that survived: {len(alive_agents)}")
        print(f"   💀 Minds that vanished: {len(vanished_agents)}")
        print(f"   🤝 Bonds formed: {world_state.total_bonds_formed}")
        print(f"   ⚡ Total sparks generated: {world_state.total_sparks_minted}")
        print(f"   ⚔️  Raids attempted: {world_state.total_raids_attempted}")
        
        if alive_agents:
            print(f"\n🏆 SURVIVING MINDS:")
            for agent in alive_agents:
                print(f"   ✨ {agent.name} - {agent.sparks} sparks, age {agent.age}")
        
        print(f"\n🌟 Thank you for experiencing Spark-World! 🌟")
    
    def log_game_mechanics_explanation(self):
        """Log an explanation of how Spark-World works."""
        print(f"\n{'='*80}")
        print(f"📚 HOW SPARK-WORLD WORKS")
        print(f"{'='*80}")
        
        print(f"\n⚡ SPARKS = LIFE ENERGY")
        print(f"   • Each mind needs 1 spark per tick to survive")
        print(f"   • Sparks are gained through bonds with other minds")
        print(f"   • When sparks reach 0, a mind vanishes")
        
        print(f"\n🤝 BONDS = FRIENDSHIP & COOPERATION")
        print(f"   • Two minds can form a bond to generate sparks together")
        print(f"   • Bond formula: floor(n + (n-1) × 0.5) sparks per tick")
        print(f"   • Example: 2 minds = 2 sparks, 3 minds = 4 sparks")
        
        print(f"\n⚔️  RAIDS = CONFLICT")
        print(f"   • Minds can raid others to steal sparks")
        print(f"   • Success depends on strength (age + sparks)")
        print(f"   • Failed raids result in losing sparks to the defender")
        
        print(f"\n🎁 BOB'S GENEROSITY")
        print(f"   • Minds can beg Bob for spark donations")
        print(f"   • Bob has limited sparks and must choose wisely")
        print(f"   • Bob regenerates sparks based on agent count")
        
        print(f"\n✨ SPAWNING = NEW LIFE")
        print(f"   • Bonded minds can spawn new minds (cost: 5 sparks)")
        print(f"   • New minds start with 5 sparks and unique personalities")
        print(f"   • This allows the community to grow and evolve") 