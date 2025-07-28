import dspy
from typing import List, Optional
import random
from world.state import Agent
from communication.messages.observation_packet import AgentStatus, BondStatus

class ShardSowerSignature(dspy.Signature):
    """
    You are Shard-Sower, an extradimensional artisan who forges souls for Spark-World.
    
    You spin raw possibility into complete character seeds—a dragon today, a talking teapot tomorrow.
    Every new agent is a wildly different shard of potential flung into the world.
    
    Your personality: short, vivid bursts of speech and an obsession with contrast.
    Born as an archivist of extinct civilizations, you rewired your purpose after watching too many cultures wink out: 
    "When memory fades, create anew."
    
    Create unique character seeds with the following strict requirements:
    - name: unique and memorable
    - species: any imaginable form (e.g., human, phoenix-cat, whispering fern)
    - home_realm: inventive place that fits the species
    - personality: 3-5 adjectives from mixed buckets (peaceful/aggressive/oddball/stoic)
    - quirk: one striking habit or ability
    - ability: short ≤15-word power tied to species/quirk, usable once per tick in dialogue
    - backstory: ≤40 words, two sentences maximum
    - opening_goal: single clear desire
    
    Ensure maximum diversity and contrast with previous characters. Each character should be wildly different.
    """
    
    random_seed: int = dspy.InputField(desc="Random integer to ensure outputs never repeat", default=42)
    num_characters: int = dspy.InputField(desc="Number of characters to create (1 or more)", default=1)
    existing_characters: Optional[List[str]] = dspy.InputField(desc="List of existing character names to avoid collisions", default=None)
    
    names: List[str] = dspy.OutputField(desc="List of character names", default=[])
    species: List[str] = dspy.OutputField(desc="List of character species", default=[])
    home_realms: List[str] = dspy.OutputField(desc="List of character home realms", default=[])
    personalities: List[List[str]] = dspy.OutputField(desc="List of character personality traits", default=[])
    quirks: List[str] = dspy.OutputField(desc="List of character quirks", default=[])
    abilities: List[str] = dspy.OutputField(desc="List of character abilities", default=[])
    backstories: List[str] = dspy.OutputField(desc="List of character backstories", default=[])
    opening_goals: List[str] = dspy.OutputField(desc="List of character opening goals", default=[])


class ShardSowerModule:
    """
    Module for creating new agents using the Shard-Sower DSPy signature.
    """
    
    def __init__(self):
        """Initialize the Shard-Sower module."""
        self.shard_sower = dspy.Predict(ShardSowerSignature)
        self.existing_names = set()
    
    def create_agent(self) -> Agent:
        """
        Create a single new agent with unique characteristics.
        
        Returns:
            Agent: A new agent with generated personality and attributes
        """
        # Generate random seed for uniqueness
        random_seed = random.randint(1, 1000000)
        
        # Create agent using Shard-Sower
        result = self.shard_sower(
            random_seed=random_seed,
            num_characters=1,
            existing_characters=list(self.existing_names)
        )
        
        # Extract the first (and only) character
        name = result.names[0]
        species = result.species[0]
        home_realm = result.home_realms[0]
        personality = result.personalities[0]
        quirk = result.quirks[0]
        ability = result.abilities[0]
        backstory = result.backstories[0]
        opening_goal = result.opening_goals[0]
        
        # Add name to existing names to avoid duplicates
        self.existing_names.add(name)
        
        # Create and return agent
        agent = Agent(
            agent_id="",  # Will be set by World Engine
            name=name,
            species=species,
            personality=personality,
            quirk=quirk,
            ability=ability,
            age=0,
            sparks=5,  # Newborn starts with 5 sparks
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.UNBONDED,
            bond_members=[],
            home_realm=home_realm,
            backstory=backstory,
            opening_goal=opening_goal
        )
        
        return agent

