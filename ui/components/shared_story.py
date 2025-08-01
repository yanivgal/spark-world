"""
Shared Story Component

Common story display logic used by both story and home components.
"""

import streamlit as st


def create_story_card_header(story_entry):
    """Create the story card header with title."""
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


def create_story_narrative(story_entry):
    """Create the story narrative section."""
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


def create_story_tooltips(story_entry):
    """Create the tooltip section for themes and character insights."""
    has_themes = story_entry.get('themes_explored')
    has_insights = story_entry.get('character_insights')
    
    if has_themes or has_insights:
        # Create a single horizontal line with all elements
        elements = []
        
        if has_themes:
            themes_text = " • ".join(story_entry['themes_explored'])
            elements.append(("themes", f"🎯 Themes: {themes_text}"))
            elements.append(("?", f"🎯 Themes: {themes_text}"))
        
        if has_themes and has_insights:
            elements.append(("|", ""))
        
        if has_insights:
            # Format character insights for tooltip
            insights_text = ""
            for insight in story_entry['character_insights']:
                if isinstance(insight, dict):
                    agent_name = insight.get('agent_name', 'Unknown')
                    motivation = insight.get('motivation', '')
                    emotional_state = insight.get('emotional_state', '')
                    growth = insight.get('growth', '')
                    potential = insight.get('potential', '')
                    
                    insights_text += f"👤 {agent_name}:\\n"
                    if motivation:
                        insights_text += f"💭 {motivation[:100]}{'...' if len(motivation) > 100 else ''}\\n"
                    if emotional_state:
                        insights_text += f"💖 {emotional_state[:100]}{'...' if len(emotional_state) > 100 else ''}\\n"
                    if growth:
                        insights_text += f"🌱 {growth[:100]}{'...' if len(growth) > 100 else ''}\\n"
                    if potential:
                        insights_text += f"🚀 {potential[:100]}{'...' if len(potential) > 100 else ''}\\n\\n"
                else:
                    insights_text += f"• {str(insight)[:100]}{'...' if len(str(insight)) > 100 else ''}\\n"
            
            elements.append(("character insights", f"👥 Character Insights:\\n{insights_text}"))
            elements.append(("?", f"👥 Character Insights:\\n{insights_text}"))
        
        # Create the horizontal line with tooltips
        if elements:
            tooltip_html = ""
            for text, help_text in elements:
                if help_text:
                    if text == "?":
                        tooltip_html += f'<span style="cursor: pointer; display: inline-block; width: 16px; height: 16px; border-radius: 50%; background: rgba(255,255,255,0.2); text-align: center; line-height: 16px; font-size: 10px; margin: 0 2px;" title="{help_text}">{text}</span>'
                    else:
                        tooltip_html += f'<span style="cursor: pointer;" title="{help_text}">{text}</span> '
                else:
                    tooltip_html += f'<span style="margin: 0 2px;">{text}</span>'
            
            st.markdown(
                f"""
                <div style="text-align: left; margin-top: 0px; font-size: 0.8rem; opacity: 0.7; display: flex; align-items: center; gap: 1px;">
                    {tooltip_html}
                </div>
                """,
                unsafe_allow_html=True
            )


def create_story_card_footer():
    """Close the story card."""
    st.markdown("</div>", unsafe_allow_html=True) 