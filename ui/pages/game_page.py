"""
Game Page

Page logic for the main game interface and page routing.
"""

import streamlit as st
from ui.components.navigation import create_navigation
from ui.components.story import display_story_page
from ui.components.home import display_home_page
from ui.components.agents import display_agents_page
from ui.components.analytics import display_analytics_page
from ui.components.controls import create_game_controls
from ui.utils.simulation import run_single_tick


def render_game_page():
    """Render the main game page with navigation and content."""
    # Show navigation
    create_navigation()
    
    # Display current page
    if st.session_state.current_page == "home":
        display_home_page()
    elif st.session_state.current_page == "story":
        display_story_page()
    elif st.session_state.current_page == "agents":
        display_agents_page()
    elif st.session_state.current_page == "analytics":
        display_analytics_page()
    elif st.session_state.current_page == "controls":
        create_game_controls()
    
    # Auto-run if playing - with better control
    if st.session_state.game_state == "playing":
        if st.session_state.current_tick < st.session_state.num_ticks:
            # Show processing status
            st.info("🔄 Processing next tick...")
            
            # Run tick without auto-rerun
            result = run_single_tick()
            if result:
                st.success(f"✅ Tick {st.session_state.current_tick} completed!")
                # Don't auto-rerun, let user control
                st.session_state.game_state = "paused"
            else:
                st.error("❌ Error during simulation")
                st.session_state.game_state = "paused"
        else:
            st.success("🏁 Your Spark-World adventure is complete!")
            st.session_state.game_state = "completed" 