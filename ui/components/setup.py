"""
Setup Components

Game setup and agent configuration UI components.
"""

import streamlit as st


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
                    <p style="color: {storyteller['color']}; font-weight: bold; font-size: 1.0rem;">{storyteller['style']}</p>
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