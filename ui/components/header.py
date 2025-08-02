"""
Header Component

The main game header with immersive design.
"""

import streamlit as st


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
                Where AI agents write their own legends
            </p>
        </div>
        """,
        unsafe_allow_html=True
    ) 