"""
Shared Mission Meeting Component

Compact mission meeting display used across different UI components.
"""

import streamlit as st
from typing import List, Dict, Optional


def format_agent_name(sender_id: str) -> str:
    """Resolve agent name from sender_id."""
    if hasattr(st.session_state, 'engine') and st.session_state.engine:
        world_state = st.session_state.engine.world_state
        if sender_id in world_state.agents:
            return world_state.agents[sender_id].name
        elif sender_id == "bob":
            return "Bob"
    return sender_id


def format_message_type(message_type: str) -> str:
    """Format message type with appropriate emoji and styling."""
    type_emojis = {
        "leader_introduction": "👑",
        "leader_opening": "🗣️", 
        "agent_response": "💬",
        "task_assignment": "📋"
    }
    emoji = type_emojis.get(message_type, "💭")
    
    type_names = {
        "leader_introduction": "Mission Introduction",
        "leader_opening": "Leader's Opening",
        "agent_response": "Agent Response", 
        "task_assignment": "Task Assignment"
    }
    name = type_names.get(message_type, message_type.replace("_", " ").title())
    
    return f"{emoji} {name}"


def create_mission_message_card(message_data: Dict) -> None:
    """Create a compact mission message card."""
    sender_name = format_agent_name(message_data['sender_id'])
    message_type = format_message_type(message_data['message_type'])
    content = message_data['content']
    
    # Determine card color based on message type
    color_gradients = {
        "leader_introduction": "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)",  # Gold
        "leader_opening": "linear-gradient(135deg, #4A90E2 0%, #357ABD 100%)",      # Blue
        "agent_response": "linear-gradient(135deg, #50C878 0%, #3CB371 100%)",      # Green
        "task_assignment": "linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%)"      # Purple
    }
    
    gradient = color_gradients.get(message_data['message_type'], "linear-gradient(135deg, #95A5A6 0%, #7F8C8D 100%)")
    
    # Create compact card
    card_content = f"""
    <div style="
        background: {gradient};
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-size: 0.9rem;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="font-weight: bold;">{sender_name}</div>
            <div style="font-size: 0.8rem; opacity: 0.9;">{message_type}</div>
        </div>
        <div style="font-style: italic; line-height: 1.4;">"{content}"</div>
    </div>
    """
    
    st.markdown(card_content, unsafe_allow_html=True)


def create_mission_meeting_section(mission_messages: List[Dict]) -> None:
    """Create the mission meeting section for all messages."""
    if not mission_messages:
        return
    
    st.markdown("### 🧩 Mission Meetings")
    st.markdown("*Bonded agents collaborate on shared goals through structured meetings*")
    st.markdown("---")
    
    # Group messages by mission_id
    missions = {}
    for message in mission_messages:
        mission_id = message['mission_id']
        if mission_id not in missions:
            missions[mission_id] = []
        missions[mission_id].append(message)
    
    # Display each mission's meeting
    for i, (mission_id, messages) in enumerate(missions.items()):
        # Add separator between missions (but not before the first one)
        if i > 0:
            st.markdown("---")  # Separator between different missions
        
        # Get mission and bond details if available
        mission_title = f"Mission {mission_id}"
        mission_description = ""
        mission_goal = ""
        bond_name = f"Bond {mission_id}"
        
        if hasattr(st.session_state, 'engine') and st.session_state.engine:
            world_state = st.session_state.engine.world_state
            if mission_id in world_state.missions:
                mission = world_state.missions[mission_id]
                mission_title = mission.title
                mission_description = mission.description
                mission_goal = mission.goal
                
                # Create bond name from member names
                if mission.bond_id in world_state.bonds:
                    bond = world_state.bonds[mission.bond_id]
                    member_names = []
                    for agent_id in bond.members:
                        if agent_id in world_state.agents:
                            member_names.append(world_state.agents[agent_id].name)
                    bond_name = " & ".join(member_names) + " Bond"
        
        # Create comprehensive mission header
        st.markdown(f"**🎯 {mission_title}**")
        st.markdown(f"*{bond_name}*")
        st.markdown(f"**📋 Goal:** {mission_goal}")
        st.markdown(f"*{mission_description}*")
        
        # Sort messages by type to show logical flow
        message_order = ["leader_introduction", "leader_opening", "agent_response", "task_assignment"]
        sorted_messages = sorted(messages, key=lambda x: message_order.index(x['message_type']) if x['message_type'] in message_order else 999)
        
        # Display messages
        for message in sorted_messages:
            create_mission_message_card(message) 