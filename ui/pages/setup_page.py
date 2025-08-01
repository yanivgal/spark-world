"""
Setup Page

Page logic for game setup and initialization.
"""

import streamlit as st
from ui.components.setup import create_game_setup, create_agent_setup
from ui.utils.simulation import initialize_simulation


def render_starting_page():
    """Render the starting page to execute the first tick."""
    st.markdown("## 🚀 Starting Your Adventure...")
    
    # Show progress
    with st.spinner("🔄 The storyteller is weaving your tale..."):
        from ui.utils.simulation import run_single_tick
        
        # Run the first actual simulation tick (tick 1)
        result = run_single_tick()
        
        if result:
            # Success! Move to playing state and set current tick to 1 (the first tick to view)
            st.session_state.current_tick = 1  # Start viewing at tick 1
            st.session_state.game_state = "paused"  # Start paused so user can control
            st.success("✅ Your adventure has begun!")
            st.rerun()
        else:
            # Error occurred
            st.error("❌ Error starting your adventure")
            st.session_state.game_state = "ready"  # Go back to ready state
            st.rerun()


def render_ready_page():
    """Render the ready page when world is initialized but no ticks have been run."""
    st.markdown("## 🎮 Your Spark-World is Ready!")
    
    # Add captivating description of Spark-World
    st.markdown("""
    ### 🌌 Welcome to Spark-World
    
    Imagine a world where **life itself is energy**—a single pulse called a **Spark** that keeps every mind alive. 
    In this living sandbox, autonomous agents bond together to survive, raid each other for precious energy, 
    and beg the mysterious wanderer **Bob** for mercy when desperate.
    
    Your agents are unique characters with their own personalities, backstories, and goals. They'll form alliances, 
    betray each other, and write their own legend through every decision they make. The **Storyteller** will weave 
    their actions into compelling narrative, turning raw events into epic tales of survival and drama.
    
    *The stage is set, the characters are waiting, and the storyteller is ready to begin your adventure.*
    """)
    
    # Display world info
    world_state = st.session_state.engine.world_state
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 🌟 World Overview")
        st.markdown(f"**Storyteller:** {st.session_state.selected_storyteller.title()}")
        st.markdown(f"**Agents Created:** {len(world_state.agents)}")
        st.markdown(f"**Simulation ID:** {st.session_state.simulation_id}")
        st.markdown(f"**Total Ticks Planned:** {st.session_state.num_ticks}")
        
        # Show agent preview
        st.markdown("### 👥 Your Characters")
        for agent_id, agent in world_state.agents.items():
            st.markdown(f"**{agent.name}** ({agent.species}) - {', '.join(agent.personality)}")
            st.markdown(f"*{agent.backstory}*")
            st.markdown("---")
    
    with col2:
        st.markdown("### 🎯 Ready to Begin?")
        st.markdown("*Click the button below to start your adventure with the first tick.*")
        
        if st.button("🚀 Start Adventure", type="primary", use_container_width=True):
            st.session_state.game_state = "starting"
            st.rerun()
        
        st.markdown("---")
        st.markdown("### ⚙️ Need to Change Settings?")
        if st.button("🔧 Back to Setup", use_container_width=True):
            st.session_state.game_state = "setup"
            st.rerun()


def render_setup_page():
    """Render the setup page based on current game state."""
    # CRITICAL DEBUG: Check if we're in a rerun cycle
    if 'last_game_state' not in st.session_state:
        st.session_state.last_game_state = None
    
    # Prevent multiple calls in the same render cycle
    if 'render_cycle' not in st.session_state:
        st.session_state.render_cycle = 0
    
    # Check if we're already in the middle of rendering this state
    current_render_key = f"{st.session_state.game_state}_{st.session_state.render_cycle}"
    if 'current_render' in st.session_state and st.session_state.current_render == current_render_key:
        return
    
    st.session_state.current_render = current_render_key
    st.session_state.render_cycle += 1
    
    # Use a key based on game_state to force complete re-render
    container_key = f"setup_container_{st.session_state.game_state}"
    
    with st.container(key=container_key):
        if st.session_state.game_state == "setup":
            create_game_setup()
        elif st.session_state.game_state == "setup_agents":
            create_agent_setup()
        elif st.session_state.game_state == "initializing":
            initialize_simulation()
        elif st.session_state.game_state == "ready":
            render_ready_page()
    
    # Update the last game state
    st.session_state.last_game_state = st.session_state.game_state 