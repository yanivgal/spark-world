"""
Simulation Logic

Handles simulation execution and tick processing.
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any


def run_single_tick():
    """Run a single tick of the simulation with spinner and storyteller tracking."""
    if not st.session_state.engine or not st.session_state.simulation_id:
        return
    
    try:
        # Execute tick without blocking spinner
        result = st.session_state.engine.tick(st.session_state.simulation_id)
        
        # Get storyteller output
        world_state = st.session_state.engine.world_state
        storyteller_output = None
        if hasattr(world_state, 'storyteller_output') and world_state.storyteller_output:
            storyteller_output = world_state.storyteller_output
        
        # Capture detailed tick information like the human logger does
        tick_details = {
            'tick': st.session_state.current_tick + 1,
            'timestamp': datetime.now(),
            'living_agents': len([a for a in world_state.agents.values() if a.status.value == 'alive']),
            'total_sparks': sum(a.sparks for a in world_state.agents.values() if a.status.value == 'alive'),
            'bob_sparks': world_state.bob_sparks,
            'active_bonds': len(world_state.bonds),
            'agents_vanished': len(result.agents_vanished) if result.agents_vanished else 0,
            'agents_spawned': len(result.agents_spawned) if result.agents_spawned else 0,
            'bonds_formed': len(result.bonds_formed) if result.bonds_formed else 0,
            'bonds_dissolved': len(result.bonds_dissolved) if result.bonds_dissolved else 0,
            'storyteller_output': storyteller_output,
            'bob_responses': world_state.bob_responses_this_tick.copy() if hasattr(world_state, 'bob_responses_this_tick') else [],
            
            # Capture detailed agent information
            'agent_status': {},
            'bond_requests': {},
            'agent_decisions': [],
            'bond_formations': [],
            'bond_dissolutions': [],
            'spark_changes': {},
            'raid_attempts': [],
            'bob_donations': []
        }
        
        # Capture agent status and spark changes
        for agent_id, agent in world_state.agents.items():
            tick_details['agent_status'][agent_id] = {
                'name': agent.name,
                'species': agent.species,
                'sparks': agent.sparks,
                'age': agent.age,
                'status': agent.status.value,
                'bond_status': agent.bond_status.value,
                'home_realm': agent.home_realm,
                'personality': agent.personality,
                'quirk': agent.quirk,
                'ability': agent.ability,
                'opening_goal': agent.opening_goal,
                'backstory': agent.backstory
            }
        
        # Capture bond requests for display
        if hasattr(world_state, 'bond_requests_for_display') and world_state.bond_requests_for_display:
            for target_id, request in world_state.bond_requests_for_display.items():
                tick_details['bond_requests'][target_id] = {
                    'requester_id': request.agent_id,
                    'requester_name': world_state.agents[request.agent_id].name,
                    'target_id': target_id,
                    'target_name': world_state.agents[target_id].name,
                    'content': request.content,
                    'reasoning': request.reasoning
                }
        
        # Capture bond formations
        if result.bonds_formed:
            for bond_id in result.bonds_formed:
                bond = world_state.bonds.get(bond_id)
                if bond:
                    member_names = [world_state.agents[member_id].name for member_id in bond.members]
                    tick_details['bond_formations'].append({
                        'bond_id': bond_id,
                        'members': bond.members,
                        'member_names': member_names,
                        'leader_id': bond.leader_id,
                        'leader_name': world_state.agents[bond.leader_id].name,
                        'sparks_generated': bond.sparks_generated_this_tick
                    })
        
        # Capture bond dissolutions
        if result.bonds_dissolved:
            for bond_id in result.bonds_dissolved:
                tick_details['bond_dissolutions'].append({
                    'bond_id': bond_id
                })
        
        # Capture agent decisions (if available in the result)
        if hasattr(result, 'agent_actions') and result.agent_actions:
            for action in result.agent_actions:
                agent = world_state.agents[action.agent_id]
                decision = {
                    'agent_id': action.agent_id,
                    'agent_name': agent.name,
                    'intent': action.intent,
                    'target': action.target,
                    'content': action.content,
                    'reasoning': action.reasoning
                }
                tick_details['agent_decisions'].append(decision)
        
        # Also capture from world state if available
        if hasattr(world_state, 'agent_actions_for_logging') and world_state.agent_actions_for_logging:
            for action in world_state.agent_actions_for_logging:
                agent = world_state.agents[action.agent_id]
                decision = {
                    'agent_id': action.agent_id,
                    'agent_name': agent.name,
                    'intent': action.intent,
                    'target': action.target,
                    'content': action.content,
                    'reasoning': action.reasoning
                }
                # Avoid duplicates
                if decision not in tick_details['agent_decisions']:
                    tick_details['agent_decisions'].append(decision)
        
        # Capture Bob donations
        if hasattr(world_state, 'bob_donations') and world_state.bob_donations:
            for donation in world_state.bob_donations:
                tick_details['bob_donations'].append(donation)
        
        # Store tick data
        st.session_state.simulation_data.append(tick_details)
        
        # Store storyteller history
        if storyteller_output:
            story_entry = {
                'tick': st.session_state.current_tick + 1,
                'chapter_title': getattr(storyteller_output, 'chapter_title', 'Unknown Chapter'),
                'narrative_text': getattr(storyteller_output, 'narrative_text', 'No narrative available'),
                'themes_explored': getattr(storyteller_output, 'themes_explored', []),
                'character_insights': getattr(storyteller_output, 'character_insights', []),
                'emotional_arcs': getattr(storyteller_output, 'emotional_arcs', []),
                'storyteller_voice': getattr(storyteller_output, 'storyteller_voice', 'Unknown voice')
            }
            st.session_state.storyteller_history.append(story_entry)
        
        st.session_state.current_tick += 1
        
        return result
        
    except Exception as e:
        st.error(f"❌ Error running tick: {e}")
        return None


def initialize_simulation():
    """Initialize the simulation with game-like feedback."""
    st.markdown("## 🌟 Initializing Your Spark-World...")
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Create temporary database
        status_text.text("🔧 Setting up the world...")
        progress_bar.progress(20)
        import time
        time.sleep(0.5)
        
        import tempfile
        import os
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "game_simulation.db")
        
        # Step 2: Initialize World Engine
        status_text.text("🚀 Awakening the storyteller...")
        progress_bar.progress(40)
        time.sleep(0.5)
        
        from world.world_engine import WorldEngine
        engine = WorldEngine(db_path=db_path)
        engine.reset_all_modules()
        engine.storyteller.personality = st.session_state.selected_storyteller
        
        # Step 3: Initialize world
        status_text.text("🌟 Creating your agents...")
        progress_bar.progress(60)
        time.sleep(0.5)
        
        simulation_id = engine.initialize_world(
            num_agents=st.session_state.num_agents,
            simulation_name=f"Game Adventure ({st.session_state.selected_storyteller})"
        )
        
        # Step 4: Initialize logger
        status_text.text("📖 Preparing the narrative...")
        progress_bar.progress(80)
        time.sleep(0.5)
        
        from world.human_logger import HumanLogger
        logger = HumanLogger()
        
        # Step 5: Complete
        status_text.text("✨ Your Spark-World is ready!")
        progress_bar.progress(100)
        time.sleep(1)
        
        st.session_state.engine = engine
        st.session_state.logger = logger
        st.session_state.simulation_id = simulation_id
        
        # Run the first tick to generate initial storyteller output
        status_text.text("📖 Running the first tick...")
        st.session_state.current_tick = 0  # Start at 0, will become 1 after the tick
        result = run_single_tick()
        if result:
            st.session_state.current_tick = 1  # Now it's 1 after the first tick
        else:
            st.session_state.current_tick = 0  # Reset if there was an error
        
        st.session_state.game_state = "paused"
        
        st.success("🎉 Your Spark-World adventure begins!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error creating your world: {e}")
        st.session_state.game_state = "setup" 