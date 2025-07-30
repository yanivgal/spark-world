#!/usr/bin/env python3
"""
Spark-World Interactive Game UI

A beautiful, game-like Streamlit interface for running Spark-World simulations
with immersive storyteller narratives and user-friendly controls.
"""

import streamlit as st
import sys
import os
import tempfile
import time
from datetime import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the simulation components
from world.world_engine import WorldEngine
from world.human_logger import HumanLogger


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
        st.session_state.current_page = "story"
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False


def create_game_header():
    """Create the main game header with immersive design."""
    st.set_page_config(
        page_title="Spark-World Game",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="collapsed"
    )
    
    # Game header with immersive design
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        ">
            <h1 style="
                color: #ffffff; 
                font-size: 4rem; 
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
                font-family: 'Arial Black', sans-serif;
            ">
                🌟 SPARK-WORLD 🌟
            </h1>
            <p style="
                color: #f0f0f0; 
                font-size: 1.4rem; 
                font-style: italic;
                margin-bottom: 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            ">
                Where magic flows like water and every creature tells a story
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def create_game_setup():
    """Create an immersive game setup experience."""
    st.markdown("## 🎮 Welcome to Spark-World!")
    
    # Game introduction
    st.markdown(
        """
        <div style="
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #FF6B6B;
            margin-bottom: 30px;
        ">
            <h3 style="color: #FF6B6B; margin-bottom: 15px;">🎭 Choose Your Storyteller</h3>
            <p style="color: #333; line-height: 1.6;">
                Your storyteller will be your guide through this magical world. They'll interpret every moment, 
                every choice, every emotion, and weave the tale of your Spark-World adventure.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Storyteller selection with enhanced descriptions
    storytellers = {
        "blip": {
            "name": "🤖 BLIP - The Savage Comedian",
            "description": "An android stand-up comic with razor-sharp wit and brutal sarcasm. Uses biting humor to process emotional confusion and delivers savage emotional gut-punches. Hates everything but secretly cares too much.",
            "style": "Dark humor, brutal honesty, savage wit",
            "color": "#FF6B6B"
        },
        "eloa": {
            "name": "🎨 ELOA - The Gentle Poet",
            "description": "A blind painter who feels and paints the world through memory, sound, and emotion. Gentle and soft-spoken, each sentence flows like brushstrokes on canvas. Sees beauty in everything.",
            "style": "Poetic, sensory, gentle storytelling",
            "color": "#4ECDC4"
        },
        "krunch": {
            "name": "⚔️ KRUNCH - The Wise Warrior",
            "description": "A barbarian who accidentally became a philosopher. Blunt, honest, and unintentionally profound. Talks like he fights: with impact. Sees straight to the heart of things with simple wisdom.",
            "style": "Direct, powerful insights, warrior wisdom",
            "color": "#45B7D1"
        }
    }
    
    # Create storyteller selection cards
    col1, col2, col3 = st.columns(3)
    
    selected_storyteller = None
    
    # Create storyteller cards with buttons
    for i, (key, storyteller) in enumerate(storytellers.items()):
        with [col1, col2, col3][i]:
            # Display the styled card
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, {storyteller['color']}20, {storyteller['color']}40);
                    padding: 20px;
                    border-radius: 15px;
                    border: 2px solid {storyteller['color']};
                    text-align: center;
                    transition: all 0.3s ease;
                    margin-bottom: 10px;
                ">
                    <h3 style="color: {storyteller['color']}; margin-bottom: 10px;">{storyteller['name']}</h3>
                    <p style="color: #333; font-size: 0.9rem; margin-bottom: 15px;">{storyteller['description']}</p>
                    <p style="color: {storyteller['color']}; font-weight: bold; font-size: 0.8rem;">{storyteller['style']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Create a simple button below each card
            if st.button(
                f"Choose {storyteller['name'].split(' - ')[1]}",
                key=f"storyteller_{key}",
                help=f"Click to choose {storyteller['name']}",
                use_container_width=True
            ):
                selected_storyteller = key
    
    if selected_storyteller:
        st.session_state.selected_storyteller = selected_storyteller
        st.success(f"✨ You chose {storytellers[selected_storyteller]['name']} as your storyteller!")
        st.session_state.game_state = "setup_agents"
        st.rerun()
    
    return selected_storyteller


def create_agent_setup():
    """Create the agent setup interface."""
    st.markdown("## 🤖 Configure Your World")
    
    st.markdown(
        """
        <div style="
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #4ECDC4;
            margin-bottom: 30px;
        ">
            <h3 style="color: #4ECDC4; margin-bottom: 15px;">🌟 Choose Your Adventure</h3>
            <p style="color: #333; line-height: 1.6;">
                Decide how many minds will inhabit your Spark-World and how long their story will unfold.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 👥 Number of Agents")
        num_agents = st.slider(
            "How many minds will inhabit your world?",
            min_value=1,
            max_value=10,
            value=3,
            help="More agents = more complex interactions and stories"
        )
        
        # Agent count description
        agent_descriptions = {
            1: "A solitary journey - one mind exploring the mysteries of Spark-World",
            2: "A duo's tale - two minds that will either bond or conflict",
            3: "A trio's adventure - the classic dynamic of three minds",
            4: "A quartet's symphony - four minds creating complex harmonies",
            5: "A quintet's dance - five minds in intricate patterns",
            6: "A sextet's chorus - six minds in rich interaction",
            7: "A septet's ensemble - seven minds in complex dynamics",
            8: "An octet's orchestra - eight minds in full harmony",
            9: "A nonet's symphony - nine minds in grand scale",
            10: "A decet's epic - ten minds in maximum complexity"
        }
        
        st.info(agent_descriptions[num_agents])
    
    with col2:
        st.markdown("### ⏰ Simulation Duration")
        num_ticks = st.slider(
            "How many ticks will your story unfold?",
            min_value=5,
            max_value=50,
            value=10,
            help="More ticks = longer story, more time for relationships to develop"
        )
        
        # Generate tick description based on ranges
        def get_tick_description(ticks):
            if ticks <= 8:
                return "A brief encounter - quick, intense interactions"
            elif ticks <= 15:
                return "A short tale - enough time for bonds to form"
            elif ticks <= 25:
                return "A moderate story - balanced development and resolution"
            elif ticks <= 35:
                return "A longer narrative - time for complex relationships"
            elif ticks <= 45:
                return "A lengthy saga - epic proportions"
            else:
                return "A legendary tale - the ultimate Spark-World experience"
        
        st.info(get_tick_description(num_ticks))
    
    # Start button
    if st.button("🚀 Begin Your Spark-World Adventure!", type="primary", use_container_width=True):
        st.session_state.num_agents = num_agents
        st.session_state.num_ticks = num_ticks
        st.session_state.game_state = "initializing"
        st.rerun()
    
    return num_agents, num_ticks


def initialize_simulation():
    """Initialize the simulation with game-like feedback."""
    st.markdown("## 🌟 Initializing Your Spark-World...")
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Create temporary database
        status_text.text("🔧 Setting up the world...")
        progress_bar.progress(20)
        time.sleep(0.5)
        
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "game_simulation.db")
        
        # Step 2: Initialize World Engine
        status_text.text("🚀 Awakening the storyteller...")
        progress_bar.progress(40)
        time.sleep(0.5)
        
        engine = WorldEngine(db_path=db_path)
        engine.reset_all_modules()
        engine.storyteller.personality = st.session_state.selected_storyteller
        
        # Step 3: Initialize world
        status_text.text("🌟 Creating your agents...")
        progress_bar.progress(60)
        time.sleep(0.5)
        
        simulation_id = engine.initialize_world(
            num_agents=st.session_state.num_agents,
            simulation_name=f"Game Adventure ({st.session_state.selected_storyteller})"
        )
        
        # Step 4: Initialize logger
        status_text.text("📖 Preparing the narrative...")
        progress_bar.progress(80)
        time.sleep(0.5)
        
        logger = HumanLogger()
        
        # Step 5: Complete
        status_text.text("✨ Your Spark-World is ready!")
        progress_bar.progress(100)
        time.sleep(1)
        
        st.session_state.engine = engine
        st.session_state.logger = logger
        st.session_state.simulation_id = simulation_id
        
        # Run the first tick to generate initial storyteller output
        status_text.text("📖 Running the first tick...")
        st.session_state.current_tick = 0  # Start at 0, will become 1 after the tick
        result = run_single_tick()
        if result:
            st.session_state.current_tick = 1  # Now it's 1 after the first tick
        else:
            st.session_state.current_tick = 0  # Reset if there was an error
        
        st.session_state.game_state = "paused"
        
        st.success("🎉 Your Spark-World adventure begins!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Error creating your world: {e}")
        st.session_state.game_state = "setup"





def display_story_page():
    """Display the main story page with storyteller narrative."""
    st.markdown("## 📖 The Story Unfolds...")
    
    if not st.session_state.engine:
        st.info("Please initialize the simulation first.")
        return
    
    # Get current storyteller output
    world_state = st.session_state.engine.world_state
    
    # Display current tick and controls
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(f"### ⏰ Tick {st.session_state.current_tick}")
    with col2:
        if st.button("⏭️ Next Tick", type="primary", use_container_width=True):
            if st.session_state.current_tick < st.session_state.num_ticks:
                with st.spinner("🔄 The storyteller is weaving your tale..."):
                    result = run_single_tick()
                    if result:
                        st.success(f"✅ Tick {st.session_state.current_tick} completed!")
                        st.rerun()
                    else:
                        st.error("❌ Error during tick")
            else:
                st.warning("🏁 Simulation completed!")
    
    # Create story container for current tick
    with st.container():
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
        
        # Display current storyteller narrative
        # First check if we have storyteller output in world state
        if hasattr(world_state, 'storyteller_output') and world_state.storyteller_output:
            storyteller_output = world_state.storyteller_output
            
            # Display chapter title
            if hasattr(storyteller_output, 'chapter_title'):
                st.markdown(f"#### 📚 {storyteller_output.chapter_title}")
            
            # Display narrative text
            if hasattr(storyteller_output, 'narrative_text'):
                st.markdown("#### 🎭 Your Storyteller's Tale")
                st.markdown(f"*{storyteller_output.narrative_text}*")
            
            # Display themes if available
            if hasattr(storyteller_output, 'themes_explored') and storyteller_output.themes_explored:
                st.markdown("#### 🎯 Themes Explored")
                themes_text = " • ".join(storyteller_output.themes_explored)
                st.markdown(f"*{themes_text}*")
            
            # Display character insights if available
            if hasattr(storyteller_output, 'character_insights') and storyteller_output.character_insights:
                st.markdown("#### 👥 Character Insights")
                for insight in storyteller_output.character_insights:
                    st.markdown(f"*{insight}*")
            
            # Display emotional arcs if available
            if hasattr(storyteller_output, 'emotional_arcs') and storyteller_output.emotional_arcs:
                st.markdown("#### 💫 Emotional Arcs")
                for arc in storyteller_output.emotional_arcs:
                    st.markdown(f"*{arc}*")
        

                
        else:
            st.markdown("#### 🎭 Awaiting the storyteller's words...")
            st.markdown("*The storyteller is gathering their thoughts...*")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Display storyteller history
    if st.session_state.storyteller_history:
        st.markdown("### 📚 Story History")
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📖 All Chapters", "🎯 Themes", "👥 Character Insights"])
        
        with tab1:
            # Display all chapters
            for i, story_entry in enumerate(reversed(st.session_state.storyteller_history)):
                with st.expander(f"📚 Tick {story_entry['tick']}: {story_entry['chapter_title']}", expanded=(i==0)):
                    st.markdown(f"**Chapter:** {story_entry['chapter_title']}")
                    st.markdown(f"**Narrative:** {story_entry['narrative_text']}")
                    if story_entry['themes_explored']:
                        st.markdown(f"**Themes:** {', '.join(story_entry['themes_explored'])}")
                    if story_entry['character_insights']:
                        st.markdown(f"**Insights:** {', '.join(story_entry['character_insights'])}")
        
        with tab2:
            # Display themes across all ticks
            all_themes = []
            for entry in st.session_state.storyteller_history:
                all_themes.extend(entry['themes_explored'])
            
            if all_themes:
                theme_counts = {}
                for theme in all_themes:
                    theme_counts[theme] = theme_counts.get(theme, 0) + 1
                
                st.markdown("#### 🎯 Recurring Themes")
                for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
                    st.markdown(f"**{theme}** (appeared {count} times)")
        
        with tab3:
            # Display character insights
            all_insights = []
            for entry in st.session_state.storyteller_history:
                all_insights.extend(entry['character_insights'])
            
            if all_insights:
                st.markdown("#### 👥 Character Development")
                for insight in all_insights:
                    st.markdown(f"*{insight}*")
    
    # World status in a more game-like format
    st.markdown("### 🌟 World Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        living_agents = len([a for a in world_state.agents.values() if a.status.value == 'alive'])
        st.metric("🌟 Living Minds", living_agents, delta=None)
    
    with col2:
        total_sparks = sum(a.sparks for a in world_state.agents.values() if a.status.value == 'alive')
        st.metric("⚡ Total Sparks", total_sparks, delta=None)
    
    with col3:
        st.metric("🎁 Bob's Sparks", world_state.bob_sparks, delta=None)
    
    with col4:
        st.metric("🔗 Active Bonds", len(world_state.bonds), delta=None)


def display_agents_page():
    """Display agents in a game-like format."""
    st.markdown("## 🤖 Meet Your Characters")
    
    if not st.session_state.engine:
        st.info("Please initialize the simulation first.")
        return
    
    world_state = st.session_state.engine.world_state
    
    # Display agents in a card format
    for agent_id, agent in world_state.agents.items():
        if agent.status.value == 'alive':
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
            
            # Create agent card
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    padding: 20px;
                    border-radius: 15px;
                    margin-bottom: 20px;
                    color: white;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                ">
                    <h3 style="margin-bottom: 10px;">{status_emoji} {agent.name}</h3>
                    <p style="font-style: italic; margin-bottom: 15px;">{agent.species}</p>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                        <span><strong>🏠 Home:</strong> {agent.home_realm}</span>
                        <span><strong>⚡ Sparks:</strong> {agent.sparks}</span>
                        <span><strong>📅 Age:</strong> {agent.age}</span>
                    </div>
                    <p><strong>💭 Personality:</strong> {', '.join(agent.personality)}</p>
                    <p><strong>🎭 Quirk:</strong> {agent.quirk}</p>
                    <p><strong>⚡ Ability:</strong> {agent.ability}</p>
                    <p><strong>🎯 Goal:</strong> {agent.opening_goal}</p>
                    <p><strong>📖 Backstory:</strong> {agent.backstory}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


def display_analytics_page():
    """Display analytics in a game-like format."""
    st.markdown("## 📊 Your World's Statistics")
    
    if not st.session_state.simulation_data:
        st.info("No simulation data yet. Start the simulation to see analytics.")
        return
    
    # Create DataFrame for plotting
    df = pd.DataFrame(st.session_state.simulation_data)
    
    # Create game-like charts
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Living Agents', 'Total Sparks', 'Bob\'s Sparks', 'Active Bonds'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    # Living agents
    fig.add_trace(
        go.Scatter(x=df['tick'], y=df['living_agents'], mode='lines+markers', 
                   name='Living Agents', line=dict(color='#FF6B6B', width=3)),
        row=1, col=1
    )
    
    # Total sparks
    fig.add_trace(
        go.Scatter(x=df['tick'], y=df['total_sparks'], mode='lines+markers',
                   name='Total Sparks', line=dict(color='#4ECDC4', width=3)),
        row=1, col=2
    )
    
    # Bob's sparks
    fig.add_trace(
        go.Scatter(x=df['tick'], y=df['bob_sparks'], mode='lines+markers',
                   name='Bob\'s Sparks', line=dict(color='#45B7D1', width=3)),
        row=2, col=1
    )
    
    # Active bonds
    fig.add_trace(
        go.Scatter(x=df['tick'], y=df['active_bonds'], mode='lines+markers',
                   name='Active Bonds', line=dict(color='#96CEB4', width=3)),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600, 
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def run_single_tick():
    """Run a single tick of the simulation with spinner and storyteller tracking."""
    if not st.session_state.engine or not st.session_state.simulation_id:
        return
    
    try:
        # Execute tick without blocking spinner
        result = st.session_state.engine.tick(st.session_state.simulation_id)
        
        # Get storyteller output
        world_state = st.session_state.engine.world_state
        storyteller_output = None
        if hasattr(world_state, 'storyteller_output') and world_state.storyteller_output:
            storyteller_output = world_state.storyteller_output
        
        # Store tick data
        tick_data = {
            'tick': st.session_state.current_tick + 1,
            'timestamp': datetime.now(),
            'living_agents': len([a for a in world_state.agents.values() if a.status.value == 'alive']),
            'total_sparks': sum(a.sparks for a in world_state.agents.values() if a.status.value == 'alive'),
            'bob_sparks': world_state.bob_sparks,
            'active_bonds': len(world_state.bonds),
            'agents_vanished': len(result.agents_vanished) if result.agents_vanished else 0,
            'agents_spawned': len(result.agents_spawned) if result.agents_spawned else 0,
            'bonds_formed': len(result.bonds_formed) if result.bonds_formed else 0,
            'bonds_dissolved': len(result.bonds_dissolved) if result.bonds_dissolved else 0,
            'storyteller_output': storyteller_output
        }
        
        st.session_state.simulation_data.append(tick_data)
        
        # Store storyteller history
        if storyteller_output:
            story_entry = {
                'tick': st.session_state.current_tick + 1,
                'chapter_title': getattr(storyteller_output, 'chapter_title', 'Unknown Chapter'),
                'narrative_text': getattr(storyteller_output, 'narrative_text', 'No narrative available'),
                'themes_explored': getattr(storyteller_output, 'themes_explored', []),
                'character_insights': getattr(storyteller_output, 'character_insights', []),
                'emotional_arcs': getattr(storyteller_output, 'emotional_arcs', []),
                'storyteller_voice': getattr(storyteller_output, 'storyteller_voice', 'Unknown voice')
            }
            st.session_state.storyteller_history.append(story_entry)
        
        st.session_state.current_tick += 1
        
        return result
        
    except Exception as e:
        st.error(f"❌ Error running tick: {e}")
        return None


def create_game_controls():
    """Create game-like controls."""
    st.markdown("## 🎮 Game Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("▶️ Start Adventure", type="primary", use_container_width=True):
            st.session_state.game_state = "playing"
            st.rerun()
    
    with col2:
        if st.button("⏸️ Pause", use_container_width=True):
            st.session_state.game_state = "paused"
            st.rerun()
    
    with col3:
        if st.button("⏭️ Next Chapter", use_container_width=True):
            if st.session_state.engine and st.session_state.simulation_id:
                result = run_single_tick()
                if result:
                    st.success(f"✅ Chapter {st.session_state.current_tick} completed!")
                    st.rerun()
    
    with col4:
        if st.button("🔄 New Game", use_container_width=True):
            st.session_state.game_state = "setup"
            st.session_state.current_tick = 0
            st.session_state.simulation_data = []
            st.session_state.storyteller_history = []
            st.session_state.engine = None
            st.session_state.logger = None
            st.session_state.simulation_id = None
            st.rerun()


def create_navigation():
    """Create game-like navigation."""
    st.markdown("## 🧭 Adventure Map")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📖 Story", use_container_width=True):
            st.session_state.current_page = "story"
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


def main():
    """Main function to run the game."""
    initialize_session_state()
    create_game_header()
    
    # Game state machine
    if st.session_state.game_state == "setup":
        create_game_setup()
    
    elif st.session_state.game_state == "setup_agents":
        create_agent_setup()
    
    elif st.session_state.game_state == "initializing":
        initialize_simulation()
    
    elif st.session_state.game_state in ["playing", "paused", "completed"]:
        # Show navigation
        create_navigation()
        
        # Display current page
        if st.session_state.current_page == "story":
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


if __name__ == "__main__":
    main() 