"""
Navigation Component

Game-like navigation between different pages.
"""

import streamlit as st


def create_navigation():
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📖 Overview", use_container_width=True):
            st.session_state.current_page = "overview"
            st.rerun()
    
    with col2:
        if st.button("🤖 Characters", use_container_width=True):
            st.session_state.current_page = "agents"
            st.rerun()
    
    with col3:
        if st.button("📊 Statistics", use_container_width=True):
            st.session_state.current_page = "analytics"
            st.rerun()
    
    with col4:
        if st.button("🎮 Controls", use_container_width=True):
            st.session_state.current_page = "controls"
            st.rerun() 