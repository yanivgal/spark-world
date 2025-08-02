"""
Home Component

Home page with current tick navigation, world status, and current iteration events.
"""

import streamlit as st
from ui.utils.simulation import run_single_tick
from ui.components.shared_story import (
    create_story_card_header,
    create_story_narrative,
    create_story_tooltips,
    create_story_card_footer
)
from ui.components.shared_observation import create_observation_section
from ui.components.shared_mission_meeting import create_mission_meeting_section, format_agent_name


def create_home_header():
    """Create the home page header with current tick and controls."""
    
    # Display current tick and controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    with col1:
        st.markdown(f"### ⏰ Tick {st.session_state.current_tick}")
    with col3:
        if st.button("⏮️ Previous Tick", use_container_width=True):
            if st.session_state.current_tick > 0:
                st.session_state.current_tick -= 1
                st.rerun()
            else:
                st.warning("🏁 Already at the beginning!")
    with col4:
        # Determine if next tick exists and set appropriate button text
        current_tick = st.session_state.current_tick
        next_tick = current_tick + 1
        
        if current_tick < st.session_state.num_ticks:
            if tick_exists(next_tick):
                button_text = "⏭️ Next Tick (Navigate)"
            else:
                button_text = "⏭️ Next Tick (Generate)"
        else:
            button_text = "⏭️ Next Tick"
            
        if st.button(button_text, type="primary", use_container_width=True):
            if st.session_state.current_tick < st.session_state.num_ticks:
                # Check if next tick already exists
                next_tick = st.session_state.current_tick + 1
                if tick_exists(next_tick):
                    # Just navigate to existing tick
                    st.session_state.current_tick = next_tick
                    st.rerun()
                else:
                    # Generate new tick
                    with st.spinner("🔄 The storyteller is weaving your tale..."):
                        result = run_single_tick()
                        if result:
                            st.success(f"✅ Tick {st.session_state.current_tick} completed!")
                            st.rerun()
                        else:
                            st.error("❌ Error during tick")
            else:
                st.warning("🏁 Simulation completed!")
    
    # Display progress right below navigation buttons
    st.progress(min(st.session_state.current_tick / st.session_state.num_ticks, 1.0))
    st.caption(f"Overall Progress: **{st.session_state.current_tick}** of {st.session_state.num_ticks} ticks")
    
    return True


def tick_exists(tick):
    """Check if a specific tick already exists in the simulation data or storyteller history."""
    # Check simulation data (for actual ticks)
    sim_exists = any(data['tick'] == tick for data in st.session_state.simulation_data)
    
    # Check storyteller history (for introduction and all ticks)
    story_exists = any(entry['tick'] == tick for entry in st.session_state.storyteller_history)
    
    # Debug info (can be removed later)
    if hasattr(st.session_state, 'debug_mode') and st.session_state.debug_mode:
        st.write(f"Debug: Tick {tick} - Sim: {sim_exists}, Story: {story_exists}")
    
    return sim_exists or story_exists


def get_world_state_for_tick(tick):
    """Get world state data for a specific tick from simulation history."""
    # Check simulation data for the tick
    for tick_data in st.session_state.simulation_data:
        if tick_data['tick'] == tick:
            return {
                'living_agents': tick_data.get('living_agents', 0),
                'total_sparks': tick_data.get('total_sparks', 0),
                'bob_sparks': tick_data.get('bob_sparks', 0),
                'active_bonds': tick_data.get('active_bonds', 0)
            }
    
    # If not found, return current world state
    world_state = st.session_state.engine.world_state
    return {
        'living_agents': len([a for a in world_state.agents.values() if a.status.value == 'alive']),
        'total_sparks': sum(a.sparks for a in world_state.agents.values() if a.status.value == 'alive'),
        'bob_sparks': world_state.bob_sparks,
        'active_bonds': len(world_state.bonds)
    }


def create_world_status_display(world_state):
    """Create world status display."""
    # Get world state for the current tick being viewed
    tick_data = get_world_state_for_tick(st.session_state.current_tick)
    
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 20px;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
        """,
        unsafe_allow_html=True
    )

    # World status in a more game-like format
    st.markdown("### 🌟 World Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌟 Living Minds", tick_data['living_agents'], delta=None)
    
    with col2:
        st.metric("⚡ Total Sparks", tick_data['total_sparks'], delta=None)
    
    with col3:
        st.metric("🎁 Bob's Sparks", tick_data['bob_sparks'], delta=None)
    
    with col4:
        st.metric("🔗 Active Bonds", tick_data['active_bonds'], delta=None)
    
    st.markdown("</div>", unsafe_allow_html=True)


def create_current_iteration_events():
    """Create the list of events for the current iteration only."""
    current_events = []
    current_tick = st.session_state.current_tick
    
    # Add current storyteller entry
    for story_entry in st.session_state.storyteller_history:
        if story_entry['tick'] == current_tick:
            current_events.append({
                'type': 'story',
                'tick': story_entry['tick'],
                'data': story_entry
            })
            break
    
    # Add current mission events
    world_state = st.session_state.engine.world_state
    if hasattr(world_state, 'missions') and world_state.missions:
        for mission_id, mission in world_state.missions.items():
            # Only show missions created in the current tick
            if mission.created_tick == current_tick:
                current_events.append({
                    'type': 'mission',
                    'tick': current_tick,
                    'data': mission
                })
    
    # Add current tick's simulation data
    for tick_data in st.session_state.simulation_data:
        if tick_data['tick'] == current_tick:
            # Add agent decisions
            if 'agent_decisions' in tick_data and tick_data['agent_decisions']:
                for decision in tick_data['agent_decisions']:
                    current_events.append({
                        'type': 'agent_decision',
                        'tick': current_tick,
                        'data': decision
                    })
            
            # Add bond formations
            if 'bond_formations' in tick_data and tick_data['bond_formations']:
                for formation in tick_data['bond_formations']:
                    current_events.append({
                        'type': 'bond_formation',
                        'tick': current_tick,
                        'data': formation
                    })
            break
    
    return current_events


def display_home_event(event, world_state):
    """Display a single home event."""
    if event['type'] == 'story':
        display_story_entry(event['data'], world_state)
    # elif event['type'] == 'mission':
    #     display_mission_event(event['data'], world_state)
    # elif event['type'] == 'bond_formation':
    #     display_bond_formation_event(event['data'])


def display_story_entry(story_entry, world_state):
    """Display a single story entry."""
    # Find corresponding tick data for this story entry
    tick_data = None
    for data in st.session_state.simulation_data:
        if data['tick'] == story_entry['tick']:
            tick_data = data
            break
    
    # Use shared components for consistent story display
    create_story_card_header(story_entry)
    create_story_narrative(story_entry)
    create_story_tooltips(story_entry)
    
    # Add a subtle separator between story and observation packets
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
    
    # Display observation packets right above "What Happened This Iteration"
    if tick_data and 'observation_packets' in tick_data and tick_data['observation_packets']:
        create_observation_section(tick_data['observation_packets'])
        
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
    
    # Add separator between observation packets and mission meetings
    if tick_data and 'observation_packets' in tick_data and tick_data['observation_packets'] and tick_data.get('mission_meeting_messages'):
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
    
    # Display mission meetings
    if tick_data and 'mission_meeting_messages' in tick_data and tick_data['mission_meeting_messages']:
        create_mission_meeting_section(tick_data['mission_meeting_messages'])
    
    # Add separator between mission meetings and "What Happened This Iteration"
    if tick_data and tick_data.get('mission_meeting_messages'):
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
    
    # Display agent decisions
    if tick_data:
        display_agent_decisions(tick_data)
    
    # Add separator between agent decisions and post-tick events
    if tick_data and (tick_data.get('bob_responses') or tick_data.get('raid_events')):
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
    
    # Display post-tick events (Bob's decisions, raids, etc.)
    if tick_data:
        display_post_tick_events(tick_data)
    
    create_story_card_footer()


def display_tick_world_status(tick_data):
    """Display world status for a specific tick."""
    st.markdown("### 🌟 World Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌟 Living Minds", tick_data['living_agents'], delta=None)
    
    with col2:
        st.metric("⚡ Total Sparks", tick_data['total_sparks'], delta=None)
    
    with col3:
        st.metric("🎁 Bob's Sparks", tick_data['bob_sparks'], delta=None)
    
    with col4:
        st.metric("🔗 Active Bonds", tick_data['active_bonds'], delta=None)
    
    # Display agent spark status
    if tick_data['agent_status']:
        st.markdown("### ⚡ Spark Status")
        for agent_id, agent_info in tick_data['agent_status'].items():
            if agent_info['status'] == 'alive':
                # Determine status color and emoji
                if agent_info['sparks'] <= 2:
                    status_emoji = "🔴"
                    status_text = "IN DANGER"
                elif agent_info['sparks'] <= 4:
                    status_emoji = "🟡"
                    status_text = "CAUTIOUS"
                else:
                    status_emoji = "🟢"
                    status_text = "SAFE"
                
                bond_emoji = "🔗" if agent_info['bond_status'] == 'bonded' else "🔓"
                
                st.markdown(
                    f"   [{status_emoji} {status_text}] {agent_info['name']}: {agent_info['sparks']} sparks (age {agent_info['age']}) {bond_emoji}"
                )


def display_agent_decisions(tick_data):
    """Display agent decisions for a tick."""
    if tick_data['agent_decisions']:
        st.markdown("### 🧠 Agent Decisions")
        st.markdown("*Agents process their observations and make choices about their next actions...*")
        
        for decision in tick_data['agent_decisions']:
            # Define color gradients for different action types
            action_colors = {
                "bond": "linear-gradient(135deg, #E3BF00 0%, #E09000 100%)",      # Darker Gold/Orange
                "raid": "linear-gradient(135deg, #FF6B6B 0%, #EE5A52 100%)",     # Red
                "request_spark": "linear-gradient(135deg, #3498DB 0%, #2980B9 100%)",  # Blue
                "spawn": "linear-gradient(135deg, #A8E6CF 0%, #7FCDCD 100%)",    # Mint
                "message": "linear-gradient(135deg, #9B59B6 0%, #8E44AD 100%)",  # Purple
                "reply": "linear-gradient(135deg, #3498DB 0%, #2980B9 100%)"     # Blue
            }
            
            # Get gradient for this action type, default to teal if not found
            gradient = action_colors.get(decision['intent'], "linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%)")
            
            # Get target name for display
            target_name = ""
            if decision['target']:
                clean_target = decision['target'].split('#')[0].split('because')[0].strip()
                if clean_target in tick_data['agent_status']:
                    target_name = tick_data['agent_status'][clean_target]['name']
            
            # Set text colors based on action type
            if decision['intent'] == 'bond':
                text_color = "#2C2C2C"  # Very dark grey for bond cards
                reasoning_color = "#666666"  # Lighter grey for reasoning
            else:
                text_color = "white"  # White for other action types
                reasoning_color = "rgba(255,255,255,0.9)"  # White with opacity for reasoning

            # Choose icon and header format based on action type
            icon = "🧠"
            header = f"{decision['agent_name']}"
            if decision['intent'] == 'bond':
                bond_type = decision.get('bond_type', 'request')  # Default to request for backward compatibility
                if bond_type == 'acceptance':
                    icon = "✅"
                    header = f"{decision['agent_name']} → {target_name} (Accept)"
                else:
                    icon = "💌"
                    header = f"{decision['agent_name']} → {target_name} (Request)"
            elif decision['intent'] == 'message':
                icon = "💬"
                if target_name:
                    header = f"{decision['agent_name']} → {target_name}"
                else:
                    header = f"{decision['agent_name']}"
            elif decision['intent'] == 'raid':
                icon = "⚔️"
                if target_name:
                    header = f"{decision['agent_name']} → {target_name}"
                else:
                    header = f"{decision['agent_name']}"
            elif decision['intent'] == 'request_spark':
                icon = "⚡"
                header = f"{decision['agent_name']}"
            elif decision['intent'] == 'spawn':
                icon = "🌟"
                header = f"{decision['agent_name']}"
            elif decision['intent'] == 'reply':
                icon = "🔁"
                if target_name:
                    header = f"{decision['agent_name']} → {target_name}"
                else:
                    header = f"{decision['agent_name']}"

            # Create minimal card with correct icon and header
            card_content = f"""
            <div style="
                background: {gradient};
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 8px;
                color: {text_color};
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                font-size: 0.9rem;
            ">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                    <div style="display: flex; align-items: center;">
                        <span style="font-size: 1.0rem; margin-right: 5px;">{icon}</span>
                        <strong style="font-size: 0.9rem; color: {text_color};">{header}</strong>
                    </div>
                    <div style="font-size: 0.8rem; opacity: 0.9; color: {text_color};">{decision['intent'].title()}</div>
                </div>
            """
            
            # Add message content (without "Message:" prefix)
            if decision['content']:
                card_content += f'<p style="font-style: italic; margin-bottom: 5px; font-size: 0.8rem; color: {text_color};">"{decision["content"]}"</p>'
            
            # Add reasoning
            if decision['reasoning']:
                if decision['intent'] == 'bond':
                    card_content += f'<div style="font-style: italic; opacity: 0.9; font-size: 0.8rem; color: {reasoning_color};"><span style="font-weight: bold;">Reasoning:</span> {decision["reasoning"]}</div>'
                else:
                    card_content += f'<div style="font-style: italic; opacity: 0.9; font-size: 0.8rem; color: {reasoning_color};">💭 {decision["reasoning"]}</div>'
            
            card_content += "</div>"
            
            st.markdown(card_content, unsafe_allow_html=True)


def display_post_tick_events(tick_data):
    """Display post-tick events including Bob's decisions, raids, bond formations, and other world events."""
    current_tick = tick_data['tick']
    
    # Filter Bob's responses for this specific tick
    bob_responses_this_tick = []
    if tick_data.get('bob_responses'):
        for bob_response in tick_data['bob_responses']:
            if bob_response.tick == current_tick:
                bob_responses_this_tick.append(bob_response)
    
    # Filter bond formations for this specific tick
    bond_formations_this_tick = []
    if tick_data.get('bond_formations'):
        for formation in tick_data['bond_formations']:
            if formation.get('tick', current_tick) == current_tick:
                bond_formations_this_tick.append(formation)
    
    has_bob_responses = len(bob_responses_this_tick) > 0
    has_raid_events = tick_data.get('raid_events') and len(tick_data['raid_events']) > 0
    has_bond_formations = len(bond_formations_this_tick) > 0
    
    if has_bob_responses or has_raid_events or has_bond_formations:
        st.markdown("### 🌊 The Tides of Fate")
        st.markdown("*As the dust settles, the currents of destiny reveal their course...*")
        
        # Display Bob's decisions
        if has_bob_responses:
            for bob_response in bob_responses_this_tick:
                display_bob_event(bob_response, None)  # world_state not needed for Bob display
        
        # Display bond formations with mission information
        if has_bond_formations:
            for formation in bond_formations_this_tick:
                display_comprehensive_bond_formation(formation)
        
        # Display raid events (placeholder for future implementation)
        if has_raid_events:
            for raid_event in tick_data['raid_events']:
                display_raid_event(raid_event)


def display_raid_event(raid_event):
    """Display a raid event."""
    # Placeholder for raid event display - can be expanded later
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #FF6B6B 0%, #EE5A52 100%);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            color: white;
            box-shadow: 0 2px 8px rgba(255, 107, 107, 0.3);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.2rem; margin-right: 8px;">⚔️</span>
                <strong style="font-size: 1rem;">Raid Event</strong>
                <span style="margin-left: auto; font-size: 1.0rem;">Tick {raid_event.get('tick', 'Unknown')}</span>
            </div>
            <p style="font-style: italic; margin-bottom: 8px; font-size: 0.9rem;">{raid_event.get('description', 'A raid occurred')}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_action_consequences(tick_data):
    """Display action consequences for a tick."""
    st.markdown("### ⚡ Action Consequences")
    st.markdown("   ───────────────────────────────────────────────────────────")
    
    # Bond requests
    if tick_data['bond_requests']:
        st.markdown("**💌 BOND REQUESTS**")
        for target_id, request in tick_data['bond_requests'].items():
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%);
                    padding: 10px;
                    border-radius: 8px;
                    margin-bottom: 8px;
                    color: #2C1810;
                    box-shadow: 0 2px 8px rgba(255, 215, 0, 0.3);
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 5px;">
                        <span style="font-size: 1.0rem; margin-right: 5px;">💌</span>
                        <strong style="font-size: 0.9rem; color: #2C1810;">{request['requester_name']} → {request['target_name']}</strong>
                    </div>
                    <p style="font-style: italic; margin-bottom: 5px; font-size: 0.8rem; color: #2C1810;">"{request['content']}"</p>
                </div>
                """,
                unsafe_allow_html=True
            )


def display_end_of_tick_summary(tick_data):
    """Display end of tick summary."""
    st.markdown("### 📊 End of Tick Summary")
    st.markdown("   ───────────────────────────────────────────────────────────")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌟 Living minds", tick_data['living_agents'], delta=None)
    
    with col2:
        st.metric("⚡ Total sparks", tick_data['total_sparks'], delta=None)
    
    with col3:
        st.metric("🎁 Bob's sparks", tick_data['bob_sparks'], delta=None)
    
    with col4:
        st.metric("🔗 Active bonds", tick_data['active_bonds'], delta=None)
    
    # Show bond formations summary
    if tick_data['bond_formations']:
        st.markdown("**🤝 Bonds formed in tick {tick_data['tick']}:**")
        for formation in tick_data['bond_formations']:
            member_names = ", ".join(formation['member_names'])
            st.markdown(f"   • {member_names}")


def display_mission_event(mission, world_state):
    """Display a mission event."""
    # Mission container with purple theme
    status_emoji = "✅" if mission.is_complete else "🔄"
    status_text = "COMPLETED" if mission.is_complete else "IN PROGRESS"
    status_color = "#8B5CF6" if mission.is_complete else "#A855F7"
    
    # Get bond members from the associated bond
    bond = world_state.bonds.get(mission.bond_id)
    member_count = len(bond.members) if bond else 0
    
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #8B5CF6 0%, #A855F7 50%, #C084FC 100%);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            color: white;
            box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
            border-left: 4px solid {status_color};
        ">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.2rem; margin-right: 8px;">{status_emoji}</span>
                <strong style="font-size: 1rem;">🎯 {mission.title}</strong>
                <span style="margin-left: auto; font-size: 1.0rem;">Tick {mission.created_tick}</span>
            </div>
            <p style="font-style: italic; margin-bottom: 8px; font-size: 0.9rem;">{mission.goal}</p>
            <div style="display: flex; justify-content: space-between; font-size: 1.0rem; opacity: 0.9;">
                <span>👑 {mission.leader_id}</span>
                <span>👥 {member_count} members</span>
                <span>{status_text}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def format_agent_name_for_bob(agent_id: str) -> str:
    """Format agent name for Bob display."""
    if hasattr(st.session_state, 'engine') and st.session_state.engine:
        world_state = st.session_state.engine.world_state
        if agent_id in world_state.agents:
            return world_state.agents[agent_id].name
        elif agent_id == "bob":
            return "Bob"
    return agent_id


def display_bob_event(bob_response, world_state):
    """Display a Bob interaction event."""
    # Bob interaction container with golden theme
    if bob_response.sparks_granted > 0:
        status_emoji = "🎁"
        status_text = "GRANTED"
        status_color = "#FFD700"  # Gold for granted
    else:
        status_emoji = "🚫"
        status_text = "DENIED"
        status_color = "#FF6B6B"  # Red for denied
    
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #FFD700 0%, #FFA500 50%, #FF8C00 100%);
            padding: 5px;
            border-radius: 16px;
            margin-bottom: 15px;
            box-shadow: 0 4px 8px rgba(255, 215, 0, 0.3);
            display: flex;
        ">
            <div style="
                background: rgba(255,255,255,0.95);
                border-radius: 12px;
                padding: 15px 18px;
                width: 100%;
                color: #2C1810;
                box-sizing: border-box;
                display: flex;
                flex-direction: column;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="font-size: 1.2rem; margin-right: 8px;">{status_emoji}</span>
                    <strong style="font-size: 1rem; color: #2C1810;">Bob → 👤 {format_agent_name_for_bob(bob_response.requesting_agent_id)}</strong>
                    <span style="margin-left: auto; font-size: 1.0rem; color: #2C1810;">Tick {bob_response.tick}</span>
                </div>
                <div style="font-style: italic; margin-bottom: 8px; font-size: 0.8rem; color: #2C1810; opacity: 0.8; padding-left: 10px; border-left: 4px solid rgba(44, 24, 16, 0.3);">
                    "{bob_response.request_content}"
                </div>
                <div style="font-size: 1.0rem; margin-bottom: 8px; color: #2C1810; opacity: 0.9; font-weight: bold;">
                    "{bob_response.reasoning}"
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 1.0rem; color: #2C1810; margin-top: 8px; padding-top: 8px; border-top: 2px solid rgba(44, 24, 16, 0.2);">
                    <span>👤 {format_agent_name_for_bob(bob_response.requesting_agent_id)}</span>
                    <span>⚡ {bob_response.sparks_granted} sparks</span>
                    <span>{status_text}</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_agent_decision_event(decision):
    """Display an agent decision event."""
    # Agent decision container with blue theme
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #4ECDC4 0%, #44A08D 100%);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            color: white;
            box-shadow: 0 2px 8px rgba(78, 205, 196, 0.3);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.2rem; margin-right: 8px;">🤔</span>
                <strong style="font-size: 1rem;">{decision['agent_name']} decides to {decision['intent']}</strong>
                <span style="margin-left: auto; font-size: 1.0rem;">Tick {decision.get('tick', 'Unknown')}</span>
            </div>
        """,
        unsafe_allow_html=True
    )
    
    if decision['target']:
        # Clean target field - extract just the agent_id if it contains comments
        clean_target = decision['target'].split('#')[0].split('because')[0].strip()
        st.markdown(f"**🎯 Target:** {clean_target}")
    
    if decision['content']:
        if decision['intent'] == "message" and decision['target']:
            clean_target = decision['target'].split('#')[0].split('because')[0].strip()
            st.markdown(f"**💬 Message to {clean_target}:** \"{decision['content']}\"")
        else:
            st.markdown(f"**💬 Message:** \"{decision['content']}\"")
    
    if decision['reasoning']:
        st.markdown(f"**💭 Reasoning:** {decision['reasoning']}")
    
    st.markdown("</div>", unsafe_allow_html=True)


def display_bond_formation_event(formation):
    """Display a bond formation event."""
    # Bond formation container with green theme
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #96CEB4 0%, #FFEAA7 100%);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            color: #2C1810;
            box-shadow: 0 2px 8px rgba(150, 206, 180, 0.3);
        ">
            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                <span style="font-size: 1.2rem; margin-right: 8px;">🤝</span>
                <strong style="font-size: 1rem; color: #2C1810;">Bond Formed</strong>
                <span style="margin-left: auto; font-size: 1.0rem; color: #2C1810;">Tick {formation.get('tick', 'Unknown')}</span>
            </div>
            <p style="font-size: 1.0rem; color: #2C1810; font-weight: bold;">🤝 {', '.join(formation['member_names'])} formed a bond!</p>
            <p style="font-size: 1.0rem; margin-top: 8px; color: #2C1810; opacity: 0.9;">👑 Leader: {formation['leader_name']}</p>
            <p style="font-size: 1.0rem; color: #2C1810; opacity: 0.9;">⚡ Sparks generated: {formation['sparks_generated']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def display_comprehensive_bond_formation(formation):
    """Display a comprehensive bond formation with mission information."""
    # Get mission information if available
    mission_info = None
    if hasattr(st.session_state, 'engine') and st.session_state.engine:
        world_state = st.session_state.engine.world_state
        bond_id = formation.get('bond_id')
        if bond_id and bond_id in world_state.bonds:
            bond = world_state.bonds[bond_id]
            if bond.mission_id and bond.mission_id in world_state.missions:
                mission = world_state.missions[bond.mission_id]
                mission_info = {
                    'title': mission.title,
                    'goal': mission.goal,
                    'description': mission.description
                }
    
    # Create the bond formation card with gradient border
    if mission_info:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #8B5CF6 0%, #A855F7 50%, #C084FC 100%);
                padding: 3px;
                border-radius: 16px;
                margin-bottom: 15px;
                box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
            ">
                <div style="
                    background: rgba(0, 0, 0, 0.95);
                    border-radius: 13px;
                    padding: 15px 18px;
                    width: 100%;
                    color: white;
                    box-sizing: border-box;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 1.2rem; margin-right: 8px;">🤝</span>
                        <strong style="font-size: 1rem; color: white;">New Bond Forged</strong>
                        <span style="margin-left: auto; font-size: 1.0rem; color: white; opacity: 0.9;">Tick {formation.get('tick', 'Unknown')}</span>
                    </div>
                    <div style="font-size: 1.0rem; margin-bottom: 8px; color: white;">
                        🤝 {', '.join(formation['member_names'])} have united!
                    </div>
                    <div style="font-size: 1.0rem; margin-bottom: 8px; color: white; opacity: 0.9;">
                        👑 <strong>Leader:</strong> {formation['leader_name']}
                    </div>
                    <div style="font-size: 1.0rem; margin-bottom: 8px; color: white; opacity: 0.9;">
                        ⚡ <strong>Sparks Generated:</strong> {formation['sparks_generated']}
                    </div>
                    <div style="
                        border-top: 2px solid rgba(255, 255, 255, 0.2);
                        padding-top: 8px;
                        margin-top: 8px;
                    ">
                        <div style="font-size: 1.0rem; margin-bottom: 5px; color: #FFD700; font-weight: bold;">
                            🎯 Mission Assigned
                        </div>
                        <div style="font-size: 0.9rem; margin-bottom: 5px; color: white; font-weight: bold;">
                            {mission_info['title']}
                        </div>
                        <div style="font-size: 0.8rem; margin-bottom: 5px; color: white; opacity: 0.9;">
                            {mission_info['description']}
                        </div>
                        <div style="font-size: 0.8rem; color: white; opacity: 0.8; font-style: italic;">
                            <strong>Goal:</strong> {mission_info['goal']}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #8B5CF6 0%, #A855F7 50%, #C084FC 100%);
                padding: 3px;
                border-radius: 16px;
                margin-bottom: 15px;
                box-shadow: 0 4px 12px rgba(139, 92, 246, 0.4);
            ">
                <div style="
                    background: rgba(0, 0, 0, 0.95);
                    border-radius: 13px;
                    padding: 15px 18px;
                    width: 100%;
                    color: white;
                    box-sizing: border-box;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 1.2rem; margin-right: 8px;">🤝</span>
                        <strong style="font-size: 1rem; color: white;">New Bond Forged</strong>
                        <span style="margin-left: auto; font-size: 1.0rem; color: white; opacity: 0.9;">Tick {formation.get('tick', 'Unknown')}</span>
                    </div>
                    <div style="font-size: 1.0rem; margin-bottom: 8px; color: white;">
                        🤝 {', '.join(formation['member_names'])} have united!
                    </div>
                    <div style="font-size: 1.0rem; margin-bottom: 8px; color: white; opacity: 0.9;">
                        👑 <strong>Leader:</strong> {formation['leader_name']}
                    </div>
                    <div style="font-size: 1.0rem; margin-bottom: 8px; color: white; opacity: 0.9;">
                        ⚡ <strong>Sparks Generated:</strong> {formation['sparks_generated']}
                    </div>
                    <div style="
                        border-top: 2px solid rgba(255, 255, 255, 0.2);
                        padding-top: 8px;
                        margin-top: 8px;
                    ">
                        <div style="font-size: 1.0rem; margin-bottom: 5px; color: #10B981; font-weight: bold;">
                            🌟 Bond Established
                        </div>
                        <div style="font-size: 0.8rem; color: white; opacity: 0.9;">
                            This bond will generate sparks and may receive a mission in the future.
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def create_home_analysis_tabs(world_state):
    """Create home analysis tabs."""
    st.markdown("### 📊 Current Iteration Analysis")
    tab1, tab2, tab3 = st.tabs(["🎯 Current Themes", "👥 Current Insights", "🎯 Current Missions"])
    
    with tab1:
        # Display themes from current tick only
        current_themes = []
        for entry in st.session_state.storyteller_history:
            if entry['tick'] == st.session_state.current_tick:
                current_themes.extend(entry['themes_explored'])
                break
        
        if current_themes:
            st.markdown("#### 🎯 Themes This Iteration")
            for theme in current_themes:
                st.markdown(f"**{theme}**")
        else:
            st.info("No themes identified in this iteration yet.")
    
    with tab2:
        # Display character insights from current tick only
        current_insights = []
        for entry in st.session_state.storyteller_history:
            if entry['tick'] == st.session_state.current_tick:
                current_insights.extend(entry['character_insights'])
                break
        
        if current_insights:
            st.markdown("#### 👥 Character Insights This Iteration")
            for insight in current_insights:
                st.markdown(f"*{insight}*")
        else:
            st.info("No character insights in this iteration yet.")
    
    with tab3:
        # Display missions created in current tick only
        current_missions = []
        if hasattr(world_state, 'missions') and world_state.missions:
            for mission_id, mission in world_state.missions.items():
                if mission.created_tick == st.session_state.current_tick:
                    current_missions.append(mission)
        
        if current_missions:
            st.markdown("#### 🎯 Missions Created This Iteration")
            for mission in current_missions:
                status_emoji = "✅" if mission.is_complete else "🔄"
                status_text = "COMPLETED" if mission.is_complete else "IN PROGRESS"
                
                st.markdown(
                    f"""
                    <div style="
                        background: linear-gradient(135deg, #8B5CF6 0%, #A855F7 50%, #C084FC 100%);
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 10px;
                        color: white;
                        box-shadow: 0 2px 8px rgba(139, 92, 246, 0.3);
                    ">
                        <div style="display: flex; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 1.2rem; margin-right: 8px;">{status_emoji}</span>
                            <strong style="font-size: 1rem;">{mission.title}</strong>
                            <span style="margin-left: auto; font-size: 1.0rem;">Tick {mission.created_tick}</span>
                        </div>
                        <p style="font-style: italic; margin-bottom: 8px; font-size: 0.9rem;">{mission.goal}</p>
                        <div style="display: flex; justify-content: space-between; font-size: 1.0rem; opacity: 0.9;">
                            <span>👑 {mission.leader_id}</span>
                            <span>👥 {len(world_state.bonds.get(mission.bond_id, {}).members) if world_state.bonds.get(mission.bond_id) else 0} members</span>
                            <span>{status_text}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.info("No missions created in this iteration yet.")


def display_home_page():
    """Display the main home page with current tick information."""
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
    
    # Create home header
    if not create_home_header():
        return
    
    world_state = st.session_state.engine.world_state
    
    # Create world status display
    create_world_status_display(world_state)
    
    # Display the current iteration events only
    if st.session_state.storyteller_history:
        # Get current iteration events only
        current_events = create_current_iteration_events()
        
        if current_events:
            # Display the current iteration events
            for event in current_events:
                display_home_event(event, world_state)
        else:
            st.info("📚 No events for the current iteration yet. Run a tick to see what happens!")
        
 