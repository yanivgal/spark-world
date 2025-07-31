"""
Setup Page

Page logic for game setup and initialization.
"""

import streamlit as st
from ui.components.setup import create_game_setup, create_agent_setup
from ui.utils.simulation import initialize_simulation


def render_setup_page():
    """Render the setup page based on current game state."""
    if st.session_state.game_state == "setup":
        create_game_setup()
    elif st.session_state.game_state == "setup_agents":
        create_agent_setup()
    elif st.session_state.game_state == "initializing":
        initialize_simulation() 