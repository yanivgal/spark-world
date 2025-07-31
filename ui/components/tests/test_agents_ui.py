#!/usr/bin/env python3
"""
Quick Test Script for Agents UI

This script creates mock data to test the agents UI components without running the full simulation.
"""

import streamlit as st
import sys
import os

# Add the project root to the path (go up 4 levels: tests -> components -> ui -> project_root)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(project_root)

# Import the agents component
from ui.components.agents import display_agents_page

# Mock agent data for testing
class MockAgent:
    def __init__(self, name, species, sparks, age, home_realm, personality, quirk, ability, goal, backstory):
        self.name = name
        self.species = species
        self.sparks = sparks
        self.age = age
        self.home_realm = home_realm
        self.personality = personality
        self.quirk = quirk
        self.ability = ability
        self.opening_goal = goal
        self.backstory = backstory
        self.status = MockStatus('alive')

class MockStatus:
    def __init__(self, value):
        self.value = value

class MockWorldState:
    def __init__(self):
        self.agents = {
            'agent_1': MockAgent(
                name="Zara the Mystic",
                species="Ethereal Being",
                sparks=5,
                age=127,
                home_realm="Crystal Spires",
                personality=["Wise", "Mysterious", "Protective"],
                quirk="Speaks in riddles",
                ability="Can see through time",
                goal="Protect the ancient knowledge",
                backstory="Born from starlight, Zara has guarded the secrets of the universe for centuries."
            ),
            'agent_2': MockAgent(
                name="Krax the Warrior",
                species="Stone Golem",
                sparks=3,
                age=89,
                home_realm="Iron Mountains",
                personality=["Brave", "Loyal", "Stubborn"],
                quirk="Collects shiny objects",
                ability="Unbreakable skin",
                goal="Find the legendary forge",
                backstory="Carved from living stone, Krax seeks to become the greatest blacksmith. Carved from living stone, Krax seeks to become the greatest blacksmith.\nCarved from living stone, Krax seeks to become the greatest blacksmith."
            ),
            'agent_3': MockAgent(
                name="Luna the Dreamer",
                species="Moon Sprite",
                sparks=7,
                age=23,
                home_realm="Silver Meadows",
                personality=["Creative", "Optimistic", "Curious"],
                quirk="Glows in the dark",
                ability="Can enter dreams",
                goal="Paint the most beautiful picture",
                backstory="Born during a lunar eclipse, Luna brings beauty to the world through art."
            ),
            'agent_4': MockAgent(
                name="Thorn the Hunter",
                species="Forest Elf",
                sparks=2,
                age=156,
                home_realm="Whispering Woods",
                personality=["Stealthy", "Determined", "Solitary"],
                quirk="Can talk to animals",
                ability="Perfect camouflage",
                goal="Track the legendary beast",
                backstory="Raised by wolves, Thorn has become the greatest tracker in the realm."
            ),
            'agent_5': MockAgent(
                name="Blitz the Inventor",
                species="Clockwork Automaton",
                sparks=6,
                age=45,
                home_realm="Steam City",
                personality=["Innovative", "Energetic", "Chaotic"],
                quirk="Constantly tinkering",
                ability="Can build anything",
                goal="Create the perfect machine",
                backstory="Built by a mad scientist, Blitz seeks to improve upon his own design."
            ),
            'agent_6': MockAgent(
                name="Mira the Healer",
                species="Crystal Fairy",
                sparks=4,
                age=67,
                home_realm="Healing Springs",
                personality=["Compassionate", "Patient", "Wise"],
                quirk="Cries healing tears",
                ability="Can cure any ailment",
                goal="Heal the world's suffering",
                backstory="Born from a healing crystal, Mira has dedicated her life to helping others."
            )
        }

class MockEngine:
    def __init__(self):
        self.world_state = MockWorldState()

def main():
    """Test the agents UI with mock data."""
    st.set_page_config(
        page_title="Agents UI Test",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Agents UI Test")
    st.markdown("Testing the 3-column agent layout with mock data")
    
    # Set up mock session state
    if 'engine' not in st.session_state:
        st.session_state.engine = MockEngine()
    
    # Display the agents page
    display_agents_page()

if __name__ == "__main__":
    main() 