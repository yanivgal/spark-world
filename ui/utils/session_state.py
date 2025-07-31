"""
Session State Management

Handles all Streamlit session state initialization and management.
"""

import streamlit as st
from typing import Optional


def initialize_session_state():
    """Initialize session state variables."""
    if 'game_state' not in st.session_state:
        st.session_state.game_state = "setup"  # setup, playing, paused, completed
    if 'current_tick' not in st.session_state:
        st.session_state.current_tick = 0
    if 'simulation_data' not in st.session_state:
        st.session_state.simulation_data = []
    if 'engine' not in st.session_state:
        st.session_state.engine = None
    if 'logger' not in st.session_state:
        st.session_state.logger = None
    if 'simulation_id' not in st.session_state:
        st.session_state.simulation_id = None
    if 'storyteller_output' not in st.session_state:
        st.session_state.storyteller_output = []
    if 'storyteller_history' not in st.session_state:
        st.session_state.storyteller_history = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "home"
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False


def get_game_state() -> str:
    """Get current game state."""
    return st.session_state.get('game_state', 'setup')


def set_game_state(state: str):
    """Set game state."""
    st.session_state.game_state = state


def get_current_tick() -> int:
    """Get current tick number."""
    return st.session_state.get('current_tick', 0)


def set_current_tick(tick: int):
    """Set current tick number."""
    st.session_state.current_tick = tick


def get_current_page() -> str:
    """Get current page."""
    return st.session_state.get('current_page', 'home')


def set_current_page(page: str):
    """Set current page."""
    st.session_state.current_page = page


def get_engine():
    """Get the world engine instance."""
    return st.session_state.get('engine')


def set_engine(engine):
    """Set the world engine instance."""
    st.session_state.engine = engine


def get_simulation_id() -> Optional[str]:
    """Get simulation ID."""
    return st.session_state.get('simulation_id')


def set_simulation_id(simulation_id: str):
    """Set simulation ID."""
    st.session_state.simulation_id = simulation_id


def reset_simulation_state():
    """Reset all simulation-related state."""
    st.session_state.current_tick = 0
    st.session_state.simulation_data = []
    st.session_state.storyteller_history = []
    st.session_state.engine = None
    st.session_state.logger = None
    st.session_state.simulation_id = None 