#!/usr/bin/env python3
"""
Human-Readable Logger for Spark-World

This module transforms technical simulation data into engaging, narrative output
that humans can easily understand and enjoy reading.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional
from world.state import WorldState, Agent, Bond, Mission
from world.world_engine import TickResult
from communication.messages.action_message import ActionMessage


class HumanLogger:
    """
    Transforms Spark-World simulation data into human-readable narrative.
    """
    
    def __init__(self):
        """Initialize the human logger."""
        self.simulation_name = "Spark-World"
        self.tick_count = 0
        self.character_intros_shown = False
    
    def log_simulation_start(self, world_state: WorldState, simulation_name: str = "Spark-World"):
        """Log the beginning of a new simulation."""
        self.simulation_name = simulation_name
        self.tick_count = 0
        
        print(f"\n{'='*80}")
        print(f"🌟 WELCOME TO {simulation_name.upper()} 🌟")
        print(f"{'='*80}")
        print(f"\nA realm where minds exist as pure energy, seeking connection and survival through bonds.")
        print(f"Each mind needs sparks to survive, and sparks are created through friendship and cooperation.")
        print(f"Watch as these unique personalities navigate the challenges of existence together!\n")
        
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
            print(f"   🎯 Goal: {agent.opening_goal}")
            print(f"   📖 Backstory: {agent.backstory}")
            print()
        
        self.character_intros_shown = True
    

    
    def log_tick_start(self, tick_number: int, world_state: WorldState):
        """Log the start of a new tick with narrative context."""
        self.tick_count = tick_number
        
        print(f"\n{'='*80}")
        print(f"⏰ TICK {tick_number}")
        print(f"{'='*80}")
        
        # Show current world status in human terms
        alive_agents = [a for a in world_state.agents.values() if a.status.value == "alive"]
        bonded_agents = [a for a in alive_agents if a.bond_status.value == "bonded"]
        
        print(f"\n📊 WORLD STATUS")
        print(f"   🌟 Living minds: {len(alive_agents)}")
        print(f"   🤝 Bonded minds: {len(bonded_agents)}")
        print(f"   🎁 Bob's sparks: {world_state.bob_sparks} (gains {world_state.bob_sparks_per_tick}/tick)")
        print(f"   🔗 Active bonds: {len(world_state.bonds)}")
        
        # Show spark status for each agent
        print(f"\n⚡ SPARK STATUS")
        for agent in alive_agents:
            if agent.sparks > 3:
                status_emoji = "🟢"
                status = "SAFE"
            elif agent.sparks > 1:
                status_emoji = "🟡"
                status = "LOW"
            else:
                status_emoji = "🔴"
                status = "CRITICAL"
            print(f"   {status_emoji} {agent.name}: {agent.sparks} sparks (age {agent.age}) - {status}")
    
    def log_tick_result(self, result: TickResult, world_state: WorldState):
        """Log tick results in human-readable narrative format."""
        print(f"\n{'='*80}")
        print(f"📖 TICK {result.tick} EVENTS")
        print(f"{'='*80}")
        
        # Log mission meetings (if any)
        if hasattr(world_state, 'mission_meeting_messages') and world_state.mission_meeting_messages:
            self._log_mission_meetings(world_state.mission_meeting_messages, world_state)
        
        # Log Storyteller narrative (if available)
        if hasattr(world_state, 'storyteller_output') and world_state.storyteller_output:
            self._log_storyteller_narrative(world_state.storyteller_output)
        
        # Log spark minting
        if result.total_sparks_minted > 0:
            self._log_spark_minting(result, world_state)
        
        # Log Bob's decisions
        bob_donations = [e for e in result.events_logged if e['event_type'] == 'bob_donation']
        if bob_donations:
            self._log_bob_donations(bob_donations, world_state)
        
        # Log agent actions and reasoning
        if hasattr(world_state, 'pending_actions') and world_state.pending_actions:
            self._log_agent_actions(world_state.pending_actions, world_state)
        
        # Log spark distribution
        if result.total_sparks_minted > 0:
            self._log_spark_distribution(result, world_state)
        
        # Log upkeep costs (cost of existence)
        if result.total_sparks_lost > 0:
            self._log_upkeep_costs(result, world_state)
        
        # Log bond requests
        bond_requests = [e for e in result.events_logged if e['event_type'] == 'bond_request']
        if bond_requests:
            self._log_bond_requests(bond_requests, world_state)
        
        # Log raids
        raids = [e for e in result.events_logged if e['event_type'] == 'raid']
        if raids:
            self._log_raids(raids, world_state)
        
        # Log failed raid attempts
        failed_raids = [e for e in result.events_logged if e['event_type'] == 'raid_failed_no_sparks']
        if failed_raids:
            self._log_failed_raid_attempts(failed_raids, world_state)
        
        # Log agent changes
        if result.agents_vanished:
            self._log_agent_vanishing(result.agents_vanished, world_state)
        
        if result.agents_spawned:
            self._log_agent_spawning(result.agents_spawned, world_state)
        
        # Log bond changes
        if result.bonds_formed:
            self._log_bond_formation(result.bonds_formed, world_state)
        
        if result.bonds_dissolved:
            self._log_bond_dissolution(result.bonds_dissolved, world_state)
        
        # Show final status
        self._log_final_status(result, world_state)
    
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
                
                # Show meeting flow
                print(f"   💬 MEETING FLOW:")
                
                # Group by message type
                leader_intro = [m for m in messages if hasattr(m, 'message_type') and m.message_type == 'LEADER_INTRODUCTION']
                leader_opening = [m for m in messages if hasattr(m, 'message_type') and m.message_type == 'LEADER_OPENING']
                agent_responses = [m for m in messages if hasattr(m, 'message_type') and m.message_type == 'AGENT_RESPONSE']
                task_assignment = [m for m in messages if hasattr(m, 'message_type') and m.message_type == 'TASK_ASSIGNMENT']
                
                # Show leader introduction (first tick only)
                if leader_intro:
                    leader = world_state.agents[leader_intro[0].sender_id]
                    print(f"      👑 {leader.name} (Leader): \"{leader_intro[0].content}\"")
                
                # Show leader opening
                if leader_opening:
                    leader = world_state.agents[leader_opening[0].sender_id]
                    print(f"      🎤 {leader.name} (Leader): \"{leader_opening[0].content}\"")
                
                # Show agent responses
                for response in agent_responses:
                    agent = world_state.agents[response.sender_id]
                    print(f"      💭 {agent.name}: \"{response.content}\"")
                
                # Show task assignment
                if task_assignment:
                    leader = world_state.agents[task_assignment[0].sender_id]
                    print(f"      📝 {leader.name} (Leader): \"{task_assignment[0].content}\"")
                
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
        print(f"   🎭 Voice: {storyteller_output.storyteller_voice}")
        
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
        print(f"\n🧠 AGENT DECISIONS")
        for action in actions:
            agent = world_state.agents[action.agent_id]
            print(f"   🤔 {agent.name} decides to {action.intent}")
            if action.target:
                target = world_state.agents[action.target]
                print(f"      🎯 Target: {target.name}")
            if action.content:
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
    
    def _log_bond_requests(self, bond_requests: List[Dict], world_state: WorldState):
        """Log bond requests as conversations."""
        print(f"\n🤝 BOND REQUESTS")
        
        for request in bond_requests:
            requester_id = request['data']['requester_id']
            target_id = request['data']['target_id']
            content = request['data']['content']
            
            requester = world_state.agents[requester_id]
            target = world_state.agents[target_id]
            
            print(f"   💌 {requester.name} → {target.name}")
            print(f"      \"{content}\"")
    
    def _log_raids(self, raids: List[Dict], world_state: WorldState):
        """Log raids as dramatic confrontations."""
        print(f"\n⚔️  RAIDS")
        
        for raid in raids:
            data = raid['data']
            attacker_id = data['attacker_id']
            defender_id = data['defender_id']
            success = data['success']
            sparks_transferred = data['sparks_transferred']
            
            attacker = world_state.agents[attacker_id]
            defender = world_state.agents[defender_id]
            
            if success:
                print(f"   ⚔️  {attacker.name} raids {defender.name} successfully!")
                print(f"   💰 {sparks_transferred} sparks stolen")
            else:
                print(f"   🛡️  {attacker.name} raids {defender.name} but fails!")
                print(f"   💪 {defender.name} gains 1 spark")
    
    def _log_failed_raid_attempts(self, failed_raids: List[Dict], world_state: WorldState):
        """Log failed raid attempts due to insufficient sparks."""
        print(f"\n❌ FAILED RAID ATTEMPTS")
        
        for raid in failed_raids:
            data = raid['data']
            attacker_id = data['attacker_id']
            defender_id = data['defender_id']
            
            attacker = world_state.agents[attacker_id]
            defender = world_state.agents[defender_id]
            
            print(f"   💀 {attacker.name} tries to raid {defender.name} but has no sparks to risk!")
    
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
    
    def _log_agent_vanishing(self, vanished_ids: List[str], world_state: WorldState):
        """Log agent vanishing as dramatic moments."""
        print(f"\n💀 MINDS FADE AWAY")
        
        for agent_id in vanished_ids:
            agent = world_state.agents[agent_id]
            print(f"   💨 {agent.name} runs out of sparks and vanishes...")
    
    def _log_agent_spawning(self, spawned_ids: List[str], world_state: WorldState):
        """Log new agent creation as magical moments."""
        print(f"\n✨ NEW MINDS EMERGE")
        
        for agent_id in spawned_ids:
            agent = world_state.agents[agent_id]
            print(f"   🌟 {agent.name} is born with 5 sparks!")
    
    def _log_bond_formation(self, bond_ids: List[str], world_state: WorldState):
        """Log bond formation as friendship moments."""
        print(f"\n🤝 FRIENDSHIPS BLOSSOM")
        
        for bond_id in bond_ids:
            bond = world_state.bonds[bond_id]
            member_names = [world_state.agents[member_id].name for member_id in bond.members]
            
            print(f"   💕 {', '.join(member_names)} form a bond!")
    
    def _log_bond_dissolution(self, bond_ids: List[str], world_state: WorldState):
        """Log bond dissolution as sad moments."""
        print(f"\n💔 BONDS BREAK")
        
        for bond_id in bond_ids:
            print(f"   💔 A bond dissolves...")
    
    def _log_spark_generation(self, result: TickResult, world_state: WorldState):
        """Log spark generation as magical moments."""
        print(f"\n✨ SPARKS OF FRIENDSHIP")
        print(f"   Bonds generate {result.total_sparks_minted} new sparks!")
        print(f"   Sparks distributed randomly among bond members")
    
    def _log_final_status(self, result: TickResult, world_state: WorldState):
        """Log final status in human terms."""
        print(f"\n{'='*80}")
        print(f"📊 END OF TICK {result.tick}")
        print(f"{'='*80}")
        
        alive_agents = [a for a in world_state.agents.values() if a.status.value == "alive"]
        total_sparks = sum(agent.sparks for agent in alive_agents)
        
        print(f"   🌟 Living minds: {len(alive_agents)}")
        print(f"   ⚡ Total sparks: {total_sparks}")
        print(f"   🎁 Bob's sparks: {world_state.bob_sparks}")
        print(f"   🔗 Active bonds: {len(world_state.bonds)}")
        
        # Show any urgent situations
        low_spark_agents = [a for a in alive_agents if a.sparks <= 2]
        if low_spark_agents:
            print(f"\n⚠️  MINDS IN DANGER:")
            for agent in low_spark_agents:
                print(f"   🔴 {agent.name}: {agent.sparks} sparks remaining")
    
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
        
        print(f"\n🌟 Thank you for experiencing {self.simulation_name}! 🌟")
    
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