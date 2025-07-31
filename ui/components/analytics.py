"""
Analytics Component

Analytics display with game-like charts and visualizations.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_analytics_charts(simulation_data):
    """Create game-like charts for analytics."""
    if not simulation_data:
        st.info("No simulation data yet. Start the simulation to see analytics.")
        return
    
    # Create DataFrame for plotting
    df = pd.DataFrame(simulation_data)
    
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
    
    return fig


def display_analytics_page():
    """Display analytics in a game-like format."""
    st.markdown("## 📊 Your World's Statistics")
    
    if not st.session_state.simulation_data:
        st.info("No simulation data yet. Start the simulation to see analytics.")
        return
    
    # Create and display charts
    fig = create_analytics_charts(st.session_state.simulation_data)
    st.plotly_chart(fig, use_container_width=True) 