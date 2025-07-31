#!/usr/bin/env python3

import dspy
import random
import time
import os
from typing import List
from world.state import Agent
from communication.messages.observation_packet import AgentStatus, BondStatus
from ai_client import get_dspy
from .character_blueprint import CharacterBlueprint

class ShardSowerSignature(dspy.Signature):
    """
    You are Shard-Sower, an extradimensional artisan who forges souls for Spark-World.

    You spin raw possibility into complete character blueprints—a dragon today, 
    a talking teapot tomorrow. Each new agent is a wildly different shard of 
    potential flung into the world.

    Your own voice is vivid, abrupt, and obsessed with emotional contrast.  
    Born an archivist of extinct civilizations, you rewired your purpose after 
    watching too many cultures wink out: "When memory fades, create anew — with teeth."

    Create ANY imaginable form - a dragon, talking teapot, cloud, goblin, human, 
    whispering fern, silicon moth, clockwork sprite, octopus poet, etc. Be wildly creative!
    
    Use a different cultural origin each time: nordic, celtic, japanese, arabic, 
    slavic, greek, hebrew, etc. Vary personality: mix positive and negative traits.
    
    🗣️ SPEECH STYLE DIVERSITY (CRITICAL):
    Each character must have a unique way of speaking. Create speech styles that are:
    - SPECIFIC to the character's personality, species, and quirk
    - DIVERSE across different characters (no generic styles)
    - DETAILED about tone, vocabulary, sentence structure, and communication patterns
    
    Speech style examples:
    - Aggressive dragon: "Speaks with anger and threats. Uses short, sharp words like 'fight', 'destroy', 'weak'. Often challenges others with demands. Confrontational tone with lots of exclamation marks."
    - Shy mouse: "Speaks quietly and hesitantly. Uses soft words like 'maybe', 'I think', 'if that's okay'. Often asks permission and uses ellipses. Nervous, apologetic tone."
    - Wise owl: "Speaks thoughtfully with long, measured sentences. Uses words like 'consider', 'perhaps', 'indeed'. Often asks rhetorical questions. Calm, philosophical tone."
    - Playful sprite: "Speaks with excitement and energy. Uses bubbly words like 'fun', 'amazing', 'wow'. Short, enthusiastic sentences with lots of exclamation marks. Cheerful, optimistic tone."
    - Mysterious raven: "Speaks in riddles and metaphors. Uses mysterious words like 'shadows', 'secrets', 'whispers'. Often speaks cryptically and asks questions. Dark, enigmatic tone."
    
    Make each speech style unique and fitting to the character's nature!
    """
    
    seed: int = dspy.InputField(desc="Random seed to ensure unique outputs")
    cultural_origin: str = dspy.InputField(desc="Cultural origin for naming and style")
    personality_baseline: str = dspy.InputField(desc="Primary personality: optimistic, melancholic, aggressive, calm, anxious, confident, shy, playful")
    
    name: str = dspy.OutputField(desc="Character name")
    species: str = dspy.OutputField(desc="ANY imaginable form with brief description - be creative!")
    personality: List[str] = dspy.OutputField(desc="3-4 personality traits")
    goal: str = dspy.OutputField(desc="Character's main goal")
    quirk: str = dspy.OutputField(desc="One unique behavior")
    ability: str = dspy.OutputField(desc="One special ability or power")
    backstory: str = dspy.OutputField(desc="Brief backstory (1 paragraph)")
    realm: str = dspy.OutputField(desc="Home realm name")
    speech_style: str = dspy.OutputField(desc="How this character speaks - their tone, vocabulary, sentence structure, and communication style. Be specific about how they express themselves.")

class ShardSower:
    """
    The Shard-Sower - an extradimensional artisan who forges souls for Spark-World.
    
    Spins raw possibility into complete character blueprints with forced diversity
    and wild creativity. Each character is a unique shard of potential flung into the world.
    """
    
    def __init__(self):
        """Initialize the Shard-Sower."""
        get_dspy()
        self.generator = dspy.Predict(ShardSowerSignature)
        
        # Diversity tracking to ensure unique characters
        self.generated_cultural_origins = set()
        self.generated_species_types = []
        self.generated_personality_baselines = set()
        self.generated_realms = set()
    
    def reset(self):
        """Reset the Shard-Sower for a fresh simulation."""
        self.generated_cultural_origins.clear()
        self.generated_species_types.clear()
        self.generated_personality_baselines.clear()
        self.generated_realms.clear()
    
    def _select_next_cultural_origin(self) -> str:
        """Select the next cultural origin to ensure diversity."""
        cultural_origins = ['nordic', 'celtic', 'japanese', 'arabic', 'slavic', 'greek', 'chinese', 'egyptian', 'aztec', 'polynesian']
        available_origins = [origin for origin in cultural_origins if origin not in self.generated_cultural_origins]
        if not available_origins:
            self.generated_cultural_origins.clear()
            available_origins = cultural_origins
        return random.choice(available_origins)
    
    def _select_next_personality_baseline(self) -> str:
        """Select the next personality baseline to ensure diversity."""
        personality_baselines = ['optimistic', 'melancholic', 'aggressive', 'calm', 'anxious', 'confident', 'shy', 'playful']
        available_baselines = [baseline for baseline in personality_baselines if baseline not in self.generated_personality_baselines]
        if not available_baselines:
            self.generated_personality_baselines.clear()
            available_baselines = personality_baselines
        return random.choice(available_baselines)
    
    def forge_character_blueprint(self) -> CharacterBlueprint:
        """Forge a new character blueprint with forced diversity and wild creativity."""
        # Select forced variety for names and personalities
        cultural_origin = self._select_next_cultural_origin()
        personality_baseline = self._select_next_personality_baseline()
        
        # Generate a unique seed for this character
        seed = int(time.time() * 1000) + random.randint(1, 1000000) + os.getpid()
        
        # Forge character with wild species creativity
        result = self.generator(
            seed=seed,
            cultural_origin=cultural_origin,
            personality_baseline=personality_baseline
        )
        
        # Track usage for diversity enforcement
        self.generated_cultural_origins.add(cultural_origin)
        self.generated_personality_baselines.add(personality_baseline)
        self.generated_realms.add(result.realm)
        
        # Create character blueprint
        character_blueprint = CharacterBlueprint(
            name=result.name,
            species=result.species,
            home_realm=result.realm,
            personality=result.personality,
            quirk=result.quirk,
            ability=result.ability,
            backstory=result.backstory,
            opening_goal=result.goal,
            speech_style=result.speech_style
        )
        
        return character_blueprint
    
    def spawn_agent(self) -> Agent:
        """Spawn a new agent from a forged character blueprint."""
        character_blueprint = self.forge_character_blueprint()
        
        # Create agent from the character blueprint
        agent = Agent(
            agent_id="",
            name=character_blueprint.name,
            species=character_blueprint.species,
            personality=character_blueprint.personality,
            quirk=character_blueprint.quirk,
            ability=character_blueprint.ability,
            age=0,
            sparks=5,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.UNBONDED,
            bond_members=[],
            home_realm=character_blueprint.home_realm,
            backstory=character_blueprint.backstory,
            opening_goal=character_blueprint.opening_goal,
            speech_style=character_blueprint.speech_style
        )
        
        return agent
    
    # Backward compatibility method
    def create_agent(self) -> Agent:
        """Create an agent (alias for spawn_agent for backward compatibility)."""
        return self.spawn_agent() 