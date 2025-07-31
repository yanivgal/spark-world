"""
Shard-Sower - The extradimensional artisan who forges souls for Spark-World.

This package contains the character generation system that creates diverse,
unique characters (agents) that populate the Spark-World simulation.

The Shard-Sower spins raw possibility into complete character blueprints—
a dragon today, a talking teapot tomorrow—each a wildly different shard
of potential flung into the world.
"""

from .character_blueprint import CharacterBlueprint
from .shard_sower import ShardSower

__all__ = ['CharacterBlueprint', 'ShardSower'] 