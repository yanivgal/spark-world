#!/usr/bin/env python3
"""
Spark-World Interactive Game UI (Refactored)

A beautiful, game-like Streamlit interface for running Spark-World simulations
with immersive storyteller narratives and user-friendly controls.
"""

import streamlit as st
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import UI components
from ui.components.header import create_game_header
from ui.pages.setup_page import render_setup_page, render_starting_page
from ui.pages.game_page import render_game_page
from ui.utils.session_state import initialize_session_state


def main():
    """Main function to run the game."""
    # Initialize session state
    initialize_session_state()
    
    # Create game header
    create_game_header()
    
    # Game state machine
    if st.session_state.game_state == "setup":
        render_setup_page()
    elif st.session_state.game_state == "setup_agents":
        render_setup_page()
    elif st.session_state.game_state == "initializing":
        render_setup_page()
    elif st.session_state.game_state == "ready":
        render_setup_page()
    elif st.session_state.game_state == "starting":
        render_starting_page()
    elif st.session_state.game_state in ["playing", "paused", "completed"]:
        render_game_page()


if __name__ == "__main__":
    main() 