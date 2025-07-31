from dataclasses import dataclass
from typing import List


@dataclass
class CharacterBlueprint:
    """
    A complete character blueprint forged by the Shard-Sower.
    
    Each CharacterBlueprint contains everything needed to create a new agent
    in Spark-World. The Shard-Sower ensures maximum diversity and contrast
    between characters.
    
    Character blueprints are used to spawn new agents at age 0 with 5 sparks.
    The World Engine converts CharacterBlueprints into full Agent entities.
    
    Attributes:
        name: Unique and memorable character name
        species: Any imaginable form (human, phoenix-cat, whispering fern, etc.)
        home_realm: Inventive place that fits the species
        personality: 3-5 adjectives from mixed buckets (peaceful/aggressive/oddball/stoic)
        quirk: One striking habit or ability
        ability: Short ≤15-word power tied to species/quirk, usable once per tick
        backstory: ≤40 words, two sentences maximum
        opening_goal: Single clear desire
        speech_style: How this character speaks and expresses themselves
    """
    name: str
    species: str
    home_realm: str
    personality: List[str]
    quirk: str
    ability: str
    backstory: str
    opening_goal: str
    speech_style: str 