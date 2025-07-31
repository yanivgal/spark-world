"""
Story Component

Story display with storyteller narrative and chronological story flow.
"""

import streamlit as st







def display_story_entry(story_entry):
    """Display a single story entry."""
    # Story chapter container
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            color: white;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            border-left: 5px solid #f093fb;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                <span style="font-size: 1.5rem; margin-right: 10px;">📚</span>
                <h3 style="margin: 0; color: white;">Tick {story_entry['tick']}: {story_entry['chapter_title']}</h3>
            </div>
        """,
        unsafe_allow_html=True
    )
    
    # Display the narrative text with the same styling as Story tab
    st.markdown(
        f"""
        <div style="
            background: rgba(255, 255, 255, 0.1);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            border-left: 3px solid #f093fb;
        ">
        """,
        unsafe_allow_html=True
    )
    
    # Use the same story-text CSS class for consistent styling
    st.markdown(f'<div class="story-text">{story_entry["narrative_text"]}</div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display themes if available
    if story_entry['themes_explored']:
        themes_text = " • ".join(story_entry['themes_explored'])
        st.markdown(f"**🎯 Themes:** *{themes_text}*")
    
    # Display character insights if available
    if story_entry['character_insights']:
        st.markdown("**👥 Character Insights:**")
        for insight in story_entry['character_insights']:
            st.markdown(f"*{insight}*")
    
    # Close the main card
    st.markdown("</div>", unsafe_allow_html=True)





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


 