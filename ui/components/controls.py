"""
Controls Component

Game-like controls for simulation management.
"""

import streamlit as st
from ui.utils.simulation import run_single_tick


def create_game_controls():
    """Create game-like controls."""
    st.markdown("## 🎮 Game Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶️ Start Adventure", type="primary", use_container_width=True):
            st.session_state.game_state = "playing"
            st.rerun()
    
    with col2:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.game_state = "paused"
            st.rerun()
    
    with col3:
        if st.button("⏭️ Next Chapter", use_container_width=True):
            if st.session_state.engine and st.session_state.simulation_id:
                result = run_single_tick()
                if result:
                    st.success(f"✅ Chapter {st.session_state.current_tick} completed!")
                    st.rerun()
    
    with col4:
        if st.button("🔄 New Game", use_container_width=True):
            st.session_state.game_state = "setup"
            st.session_state.current_tick = 0
            st.session_state.simulation_data = []
            st.session_state.storyteller_history = []
            st.session_state.engine = None
            st.session_state.logger = None
            st.session_state.simulation_id = None
            st.rerun() 