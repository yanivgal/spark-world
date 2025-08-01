"""
Story Component

Story display with storyteller narrative and chronological story flow.
"""

import streamlit as st
from ui.components.shared_story import (
    create_story_card_header,
    create_story_narrative,
    create_story_tooltips,
    create_story_card_footer
)







def display_story_entry(story_entry):
    """Display a single story entry."""
    # Use shared components for consistent story display
    create_story_card_header(story_entry)
    create_story_narrative(story_entry)
    create_story_tooltips(story_entry)
    create_story_card_footer()





def display_story_page():
    """Display a dedicated page showing only storyteller iterations."""
    # Add custom CSS for better text styling
    st.markdown("""
        <style>
        .story-text {
            font-style: italic !important;
            font-size: 1.1rem !important;
            line-height: 1.6 !important;
            color: #f8f9fa !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Get storyteller name
    storyteller_name = st.session_state.selected_storyteller.title() if hasattr(st.session_state, 'selected_storyteller') and st.session_state.selected_storyteller else "The Storyteller"
    
    st.markdown(f"## 📖 Once Upon a Spark-World...")
    st.markdown(f"*A Story by {storyteller_name}* - Where every moment becomes a story, and every choice writes a new chapter*")
    
    if not st.session_state.engine:
        st.info("Please initialize the simulation first.")
        return
    
    # Display all storyteller iterations as cards
    if st.session_state.storyteller_history:
        
        for i, story_entry in enumerate(st.session_state.storyteller_history):
            # Display each story entry using the dedicated function
            display_story_entry(story_entry)
            
            # Add a subtle separator between iterations
            if i < len(st.session_state.storyteller_history) - 1:
                st.markdown(
                    """
                    <div style="
                        height: 2px;
                        background: linear-gradient(90deg, transparent, #667eea, transparent);
                        margin: 20px 0;
                        border-radius: 1px;
                    "></div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("📚 No storyteller iterations yet. Run some ticks to see the story unfold!") 


 