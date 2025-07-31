"""
Agents Component

Agent display in a game-like format.
"""

import streamlit as st


def create_agent_card(agent_id, agent):
    """Create a single agent card with improved structure using Streamlit components."""
    # Determine status color and emoji
    if agent.sparks <= 2:
        status_emoji = "🔴"
        status_text = "IN DANGER"
        status_color = "#FF4444"
    elif agent.sparks <= 4:
        status_emoji = "🟡"
        status_text = "CAUTIOUS"
        status_color = "#FFAA00"
    else:
        status_emoji = "🟢"
        status_text = "SAFE"
        status_color = "#00AA00"
    
    # Create card container with custom CSS
    st.markdown(
        f"""
        <style>
        .agent-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 20px;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .agent-header {{
            border-bottom: 2px solid rgba(255,255,255,0.2);
            padding-bottom: 15px;
            margin-bottom: 15px;
        }}
        .agent-stats {{
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 12px;
            margin-bottom: 15px;
        }}
        .agent-trait {{
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 8px;
        }}
        .agent-story {{
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 8px;
        }}
        .backstory-box {{
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            padding: 10px;
            height: 120px;
            overflow-y: auto;
            font-size: 0.9rem;
            line-height: 1.4;
        }}
        .backstory-box::-webkit-scrollbar {{
            width: 6px;
        }}
        .backstory-box::-webkit-scrollbar-track {{
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
        }}
        .backstory-box::-webkit-scrollbar-thumb {{
            background: rgba(255,255,255,0.3);
            border-radius: 3px;
        }}
        .backstory-box::-webkit-scrollbar-thumb:hover {{
            background: rgba(255,255,255,0.5);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Start the card
    with st.container():
        st.markdown('<div class="agent-card">', unsafe_allow_html=True)
        
        st.markdown(f"### {agent.name}")
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            st.markdown(f"⚡ **{agent.sparks}**  &nbsp;&nbsp;&nbsp; |  &nbsp;&nbsp;&nbsp; 📅 **{agent.age}**")
        with col4:
            st.markdown(f'<div style="background: {status_color}; padding: 4px 8px; border-radius: 12px; text-align: center; font-size: 0.8rem; font-weight: bold;">{status_emoji} {status_text}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown(f"🏷️ **Species:** {agent.species}")
        st.markdown(f"🏠 **Home:** {agent.home_realm}")
        st.markdown(f"💭 **Personality:** {', '.join(agent.personality)}")
        st.markdown(f"🎭 **Quirk:** {agent.quirk}")
        st.markdown(f"⚡ **Ability:** {agent.ability}")
        st.markdown(f"🎯 **Goal:** *{agent.opening_goal}*")
        st.markdown(f"🗣️ **Speech Style:** *{agent.speech_style}*")
        
        st.markdown("**📚 Backstory:**")
        st.markdown(f'<div class="backstory-box">{agent.backstory}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)


def display_agents_page():
    """Display agents in a game-like format."""
    st.markdown("## 🤖 Meet Your Characters")
    
    if not st.session_state.engine:
        st.info("Please initialize the simulation first.")
        return
    
    world_state = st.session_state.engine.world_state
    
    # Get all living agents
    living_agents = [(agent_id, agent) for agent_id, agent in world_state.agents.items() 
                     if agent.status.value == 'alive']
    
    # Display agents in a 3-column layout
    for i in range(0, len(living_agents), 3):
        # Create a row with up to 3 columns
        row_agents = living_agents[i:i+3]
        cols = st.columns(len(row_agents))
        
        for j, (agent_id, agent) in enumerate(row_agents):
            with cols[j]:
                create_agent_card(agent_id, agent) 