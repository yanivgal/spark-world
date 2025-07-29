#!/usr/bin/env python3

import dspy
import random
from typing import List
from world.state import Agent
from communication.messages.observation_packet import AgentStatus, BondStatus
from character_designer.dspy_init import get_dspy

class SimpleDiverseSignature(dspy.Signature):
    """
    Create a unique character for Spark-World.
    
    Use a different cultural origin each time: nordic, celtic, japanese, arabic, slavic, greek, etc.
    Vary personality: mix positive and negative traits.
    
    For species: Create ANY imaginable form - a dragon, talking teapot, cloud, goblin, human, 
    whispering fern, silicon moth, clockwork sprite, octopus poet, etc. Be wildly creative!
    """
    
    seed: int = dspy.InputField(desc="Random seed to ensure unique outputs")
    cultural_origin: str = dspy.InputField(desc="Cultural origin for naming and style")
    personality_base: str = dspy.InputField(desc="Primary personality: optimistic, melancholic, aggressive, calm, anxious, confident, shy, playful")
    
    name: str = dspy.OutputField(desc="Character name")
    species: str = dspy.OutputField(desc="ANY imaginable form with brief description - be creative!")
    personality: List[str] = dspy.OutputField(desc="3-4 personality traits")
    goal: str = dspy.OutputField(desc="Character's main goal")
    quirk: str = dspy.OutputField(desc="One unique behavior")
    backstory: str = dspy.OutputField(desc="Brief backstory (2 sentences)")
    realm: str = dspy.OutputField(desc="Home realm name")

class SimpleDiverseSower:
    """
    Simple but effective character generation with forced diversity.
    
    Uses short prompts, explicit constraints, and template-based variety.
    """
    
    def __init__(self):
        """Initialize the simple diverse sower."""
        get_dspy()
        self.generator = dspy.Predict(SimpleDiverseSignature)
        
        # Simple tracking
        self.used_cultures = set()
        self.used_species = []
        self.used_personalities = set()
        self.used_realms = set()
    
    def reset(self):
        """Reset for fresh simulation."""
        self.used_cultures.clear()
        self.used_species.clear()
        self.used_personalities.clear()
        self.used_realms.clear()
    
    def _get_next_culture(self) -> str:
        """Get next cultural origin."""
        cultures = ['nordic', 'celtic', 'japanese', 'arabic', 'slavic', 'greek', 'chinese', 'egyptian', 'aztec', 'polynesian']
        available = [c for c in cultures if c not in self.used_cultures]
        if not available:
            self.used_cultures.clear()
            available = cultures
        return random.choice(available)
    
    def _get_next_personality(self) -> str:
        """Get next personality baseline."""
        personalities = ['optimistic', 'melancholic', 'aggressive', 'calm', 'anxious', 'confident', 'shy', 'playful']
        available = [p for p in personalities if p not in self.used_personalities]
        if not available:
            self.used_personalities.clear()
            available = personalities
        return random.choice(available)
    
    def create_agent(self) -> Agent:
        """Create a character with forced diversity but wild creativity for species."""
        # Get forced variety for names and personalities
        culture = self._get_next_culture()
        personality_base = self._get_next_personality()
        
        # Generate a unique seed for this character
        import time
        import os
        seed = int(time.time() * 1000) + random.randint(1, 1000000) + os.getpid()
        
        # Generate character with wild species creativity
        result = self.generator(
            seed=seed,
            cultural_origin=culture,
            personality_base=personality_base
        )
        
        # Track usage
        self.used_cultures.add(culture)
        self.used_personalities.add(personality_base)
        self.used_realms.add(result.realm)
        
        # Generate ability based on the actual species (not constrained categories)
        ability = self._generate_creative_ability(result.species, result.quirk)
        
        # Create agent
        agent = Agent(
            agent_id="",
            name=result.name,
            species=result.species,
            personality=result.personality,
            quirk=result.quirk,
            ability=ability,
            age=0,
            sparks=5,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.UNBONDED,
            bond_members=[],
            home_realm=result.realm,
            backstory=result.backstory,
            opening_goal=result.goal
        )
        
        return agent
    
    def _generate_creative_ability(self, species: str, quirk: str) -> str:
        """Generate a creative ability based on the actual species and quirk."""
        # Let the LLM be creative instead of using templates
        abilities = [
            "Can manipulate shadows and darkness",
            "Able to create and control light",
            "Can communicate with animals and plants",
            "Able to sense emotions of others",
            "Can transform into different forms",
            "Able to heal minor wounds",
            "Can create illusions and mirages",
            "Able to control elemental forces",
            "Can read thoughts and memories",
            "Able to teleport short distances",
            "Can brew magical potions",
            "Able to control time in small ways",
            "Can speak all languages",
            "Able to create music from thin air",
            "Can turn invisible at will",
            "Able to shapeshift into any form",
            "Can control the weather",
            "Able to see into the future",
            "Can create portals between realms",
            "Able to absorb and redirect energy"
        ]
        return random.choice(abilities)