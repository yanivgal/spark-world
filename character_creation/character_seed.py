from dataclasses import dataclass
from typing import List


@dataclass
class CharacterSeed:
    """
    A complete character seed created by the Shard-Sower.
    
    Each CharacterSeed contains everything needed to create a new agent
    in Spark-World. The Shard-Sower ensures maximum diversity and contrast
    between characters.
    
    Character seeds are used to spawn new agents at age 0 with 5 sparks.
    The World Engine converts CharacterSeeds into full Agent entities.
    
    Attributes:
        name: Unique and memorable character name
        species: Any imaginable form (human, phoenix-cat, whispering fern, etc.)
        home_realm: Inventive place that fits the species
        personality: 3-5 adjectives from mixed buckets (peaceful/aggressive/oddball/stoic)
        quirk: One striking habit or ability
        ability: Short ≤15-word power tied to species/quirk, usable once per tick
        backstory: ≤40 words, two sentences maximum
        opening_goal: Single clear desire
    """
    name: str
    species: str
    home_realm: str
    personality: List[str]
    quirk: str
    ability: str
    backstory: str
    opening_goal: str 