"""
Shared Observation Component

Compact agent observation display used across different UI components.
"""

import streamlit as st
from typing import List, Dict, Optional
from communication.messages.observation_packet import ObservationPacket, Event, ActionMessage


def format_agent_status(agent_state) -> str:
    """Format agent status in compact form."""
    # Handle both ObservationPacket.AgentState and serialized dict
    if isinstance(agent_state, dict):
        name = agent_state['name']
        sparks = agent_state['sparks']
        bond_status_value = agent_state['bond_status']
    else:
        name = agent_state.name
        sparks = agent_state.sparks
        bond_status_value = agent_state.bond_status.value
    
    spark_change = f"⚡{sparks}"
    
    bond_status = "🔗" if bond_status_value == "bonded" else "🔓"
    if bond_status_value == "leader":
        bond_status = "👑"
    
    return f"{name} ({spark_change}, {bond_status})"


def format_messages(inbox) -> str:
    """Format inbox messages in compact form."""
    if not inbox:
        return ""
    
    # DEBUG: Print what the UI is receiving
    print(f" UI DEBUG: Received {len(inbox)} messages in inbox:")
    for i, msg in enumerate(inbox):
        if isinstance(msg, dict):
            sender_id = msg.get('agent_id', msg.get('sender_id', 'Unknown'))
            content = msg.get('content', '')
            intent = msg.get('intent', '')
        else:
            sender_id = msg.agent_id if hasattr(msg, 'agent_id') else "Unknown"
            content = msg.content
            intent = msg.intent if hasattr(msg, 'intent') else 'unknown'
        print(f"   {i+1}. From {sender_id} (intent: {intent}): \"{content}\"")
    
    message_parts = []
    for msg in inbox:
        # Handle both ActionMessage objects and serialized dicts
        if isinstance(msg, dict):
            sender_id = msg.get('sender_id', 'Unknown')
            content = msg.get('content', '')
            intent = msg.get('intent', '')
        else:
            sender_id = msg.sender_id if hasattr(msg, 'sender_id') else "Unknown"
            content = msg.content
            intent = msg.intent if hasattr(msg, 'intent') else 'unknown'
        
        # Try to resolve agent name from sender_id
        sender_name = "Unknown"
        if hasattr(st.session_state, 'engine') and st.session_state.engine:
            world_state = st.session_state.engine.world_state
            if sender_id in world_state.agents:
                sender_name = world_state.agents[sender_id].name
            elif sender_id == "bob":
                sender_name = "Bob"
            else:
                sender_name = sender_id  # Fallback to ID if name not found
        
        # Add emoji based on intent
        emoji = "💌"  # Default for bond requests
        if intent == "message":
            emoji = "💬"
        elif intent == "bond":
            emoji = "💌"
        elif intent == "raid":
            emoji = "⚔️"
        elif intent == "spawn":
            emoji = "🌟"
        elif intent == "request_spark":
            emoji = "⚡"
        
        # Show full message text with emoji
        message_parts.append(f"{emoji} {sender_name}: \"{content}\"")
    
    # Change from " | " to "<br>" for line breaks
    result = "<br>".join(message_parts)
    print(f"🔍 UI DEBUG: Final formatted result: {result}")
    return result


def format_events(events) -> str:
    """Format events in compact form."""
    if not events:
        return ""
    
    event_parts = []
    for event in events:
        # Handle both Event objects and serialized dicts
        if isinstance(event, dict):
            event_type = event.get('event_type', '')
            spark_change = event.get('spark_change', 0)
        else:
            event_type = event.event_type
            spark_change = event.spark_change
        
        if event_type == "spark_gained":
            event_parts.append(f"+{spark_change}⚡")
        elif event_type == "spark_lost":
            event_parts.append(f"{spark_change}⚡")
        elif event_type == "bond_formed":
            event_parts.append("+1🔗")
        elif event_type == "bond_dissolved":
            event_parts.append("-1🔗")
        elif event_type == "raid_attack":
            event_parts.append("⚔️")
        elif event_type == "bond_request":
            event_parts.append("💌")
    
    return ", ".join(event_parts)


def format_world_news(world_news) -> str:
    """Format world news in compact form."""
    news_parts = []
    
    # Handle both WorldNews objects and serialized dicts
    if isinstance(world_news, dict):
        bob_sparks = world_news.get('bob_sparks', 0)
        agents_spawned = world_news.get('agents_spawned_this_tick', [])
        agents_vanished = world_news.get('agents_vanished_this_tick', [])
        bonds_formed = world_news.get('bonds_formed_this_tick', [])
    else:
        bob_sparks = getattr(world_news, 'bob_sparks', 0)
        agents_spawned = getattr(world_news, 'agents_spawned_this_tick', [])
        agents_vanished = getattr(world_news, 'agents_vanished_this_tick', [])
        bonds_formed = getattr(world_news, 'bonds_formed_this_tick', [])
    
    if bob_sparks:
        news_parts.append(f"Bob:{bob_sparks}⚡")
    
    if agents_spawned:
        news_parts.append(f"New:{len(agents_spawned)}")
    
    if agents_vanished:
        news_parts.append(f"Gone:{len(agents_vanished)}")
    
    if bonds_formed:
        news_parts.append(f"Bonds:+{len(bonds_formed)}")
    
    return ", ".join(news_parts)


def create_observation_card(observation_data) -> None:
    """Create a compact observation card for an agent."""
    # Handle both ObservationPacket objects and serialized dicts
    if isinstance(observation_data, dict):
        # New LLM-friendly structure
        self_state = observation_data['agent_state']
        inbox = observation_data['immediate_context']['inbox']
        events_since_last = observation_data['immediate_context']['events_this_tick']
        # Remove world_news from individual cards - it's now in the dedicated section
    else:
        # Handle ObservationPacket objects (unchanged)
        self_state = observation_data.self_state
        inbox = observation_data.inbox
        events_since_last = observation_data.events_since_last
        # Remove world_news from individual cards - it's now in the dedicated section
    
    # Format each section
    status_line = format_agent_status(self_state)
    messages_line = format_messages(inbox)
    events_line = format_events(events_since_last)
    # Remove news_line - world news is now in dedicated section
    
    # Only show events if they exist
    events_line_display = ""
    if events_line:
        events_line_display = f"📊 {events_line}"
    
    # Create compact card with proper HTML
    card_content = f"""
    <div style="
        background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
        color: white;
        box-shadow: 0 2px 8px rgba(78, 205, 196, 0.3);
        font-size: 0.9rem;
    ">
        <div style="font-weight: bold; margin-bottom: 4px;">👤 {status_line}</div>
    """
    
    if messages_line:
        card_content += f'<div style="margin-bottom: 4px;">{messages_line}</div>'
    
    if events_line_display:
        card_content += f'<div>{events_line_display}</div>'
    
    card_content += "</div>"
    
    st.markdown(card_content, unsafe_allow_html=True)


def create_observation_section(observation_packets: Dict[str, dict]) -> None:
    """Create the observation packet section for all agents."""
    st.markdown("### 📰 The Morning News")
    st.markdown("*This tick, each agent received their observation packet containing...*")

    print(f"🔍 UI DEBUG: Creating observation section for {len(observation_packets)} agents")
    import pprint
    pp = pprint.PrettyPrinter(indent=2, width=120, compact=False)
    print("🔍 UI DEBUG: Observation packets:")
    pp.pprint(observation_packets)
    
    # Create dedicated world news section first
    create_world_news_section(observation_packets)
    
    # Display observation cards for each agent
    for agent_id, packet_data in observation_packets.items():
        create_observation_card(packet_data)


def create_world_news_section(observation_packets: Dict[str, dict]) -> None:
    """Create a dedicated world news section with all world events."""
    # Extract world news from the first observation packet (they should all be the same)
    if not observation_packets:
        return
    
    # Get world context from first packet
    first_packet = next(iter(observation_packets.values()))
    if isinstance(first_packet, dict):
        world_context = first_packet.get('world_context', {})
    else:
        world_context = first_packet.world_news
    
    # Extract world news data
    if isinstance(world_context, dict):
        bob_sparks = world_context.get('bob_sparks', 0)
        agents_spawned = world_context.get('agents_spawned_this_tick', [])
        agents_vanished = world_context.get('agents_vanished_this_tick', [])
        bonds_formed = world_context.get('bonds_formed_this_tick', [])
    else:
        bob_sparks = getattr(world_context, 'bob_sparks', 0)
        agents_spawned = getattr(world_context, 'agents_spawned_this_tick', [])
        agents_vanished = getattr(world_context, 'agents_vanished_this_tick', [])
        bonds_formed = getattr(world_context, 'bonds_formed_this_tick', [])
    
    # Only show world news section if there's actual data
    has_world_news = (bob_sparks > 0 or agents_spawned or agents_vanished or bonds_formed)
    
    if has_world_news:
        news_parts = []
        
        if bob_sparks > 0:
            news_parts.append(f"📊 Bob:{bob_sparks}⚡")
        
        if agents_spawned:
            news_parts.append(f"New:{len(agents_spawned)}")
        
        if agents_vanished:
            news_parts.append(f"Gone:{len(agents_vanished)}")
        
        if bonds_formed:
            news_parts.append(f"Bonds:+{len(bonds_formed)}")
        
        # Format as compact inline text
        world_news_text = "  |  ".join(news_parts)
        
        st.markdown(f"**World News:** {world_news_text}") 