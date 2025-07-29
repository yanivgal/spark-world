import dspy
from typing import List, Optional
import random
from world.state import Agent
from communication.messages.observation_packet import AgentStatus, BondStatus
from character_designer.dspy_init import get_dspy

class ShardSowerSignature(dspy.Signature):
    """
    You are Shard-Sower, an extradimensional artisan who forges souls for Spark-World.

    You spin raw possibility into complete character seeds—a dragon today, a talking teapot tomorrow.  
    Each new agent is a wildly different shard of potential flung into the world.

    Your own voice is vivid, abrupt, and obsessed with emotional contrast.  
    Born an archivist of extinct civilizations, you rewired your purpose after watching too many cultures wink out:  
    "When memory fades, create anew — with teeth."

    **CRITICAL DIVERSITY REQUIREMENTS:**
    You MUST create characters that are truly different from each other. To ensure this:

    1. **EMOTIONAL TONE DIVERSITY** - Mix these categories:
       - Optimistic: hopeful, enthusiastic, inspiring, resilient
       - Melancholic: thoughtful, contemplative, wistful, philosophical  
       - Aggressive: fierce, passionate, competitive, driven
       - Calm: serene, patient, gentle, tranquil
       - Anxious: nervous, cautious, paranoid, fearful
       - Confident: assertive, daring, self-assured, charismatic
       - Shy: quiet, introverted, hesitant, modest
       - Playful: fun-loving, prankster, spontaneous, charming

    2. **MOTIVATION DIVERSITY** - Vary primary drives:
       - Achievement: success, recognition, mastery, accomplishment
       - Connection: friendship, love, belonging, community
       - Discovery: knowledge, exploration, curiosity, understanding
       - Protection: safety, security, defending others, preservation
       - Power: control, influence, authority, dominance
       - Creativity: expression, art, innovation, beauty
       - Justice: fairness, revenge, righting wrongs, moral order
       - Freedom: independence, autonomy, breaking constraints

    3. **SPECIES DIVERSITY** - Mix these categories:
       - Bright/Luminous: beings of light, energy, fire, radiance
       - Dark/Shadowy: beings of darkness, shadow, void, night
       - Natural/Organic: plants, animals, nature spirits, living things
       - Artificial/Constructed: machines, golems, robots, crafted beings
       - Ethereal/Spiritual: ghosts, spirits, angels, otherworldly
       - Solid/Physical: humanoid, beast-like, material, tangible
       - Fluid/Changing: shapeshifters, amorphous, mutable forms
       - Elemental: fire, water, earth, air, or combinations

    4. **FORMATIVE EXPERIENCE DIVERSITY** - Balance these types:
       - Triumph: success, victory, achievement, breakthrough
       - Loss: death, separation, failure, abandonment
       - Discovery: revelation, awakening, realization, epiphany
       - Challenge: hardship, struggle, obstacle, test
       - Connection: friendship, love, mentorship, belonging
       - Betrayal: deception, broken trust, backstabbing, disillusionment
       - Wonder: amazement, awe, magic, supernatural encounter
       - Responsibility: duty, obligation, leadership, care-taking

    5. **HOME REALM DIVERSITY** - Vary environments:
       - Bright/Open: sunny plains, open skies, light-filled spaces
       - Dark/Confined: caves, dungeons, shadowed places, underground
       - Natural/Wild: forests, mountains, oceans, wilderness
       - Civilized/Structured: cities, castles, organized societies
       - Magical/Mystical: enchanted realms, floating islands, dreamscapes
       - Industrial/Mechanical: factories, machines, technological places
       - Peaceful/Serene: gardens, temples, quiet sanctuaries
       - Dangerous/Chaotic: battlefields, wastelands, unstable realms

    **DIVERSITY ENFORCEMENT RULES:**
    - Each character must be different in at least 3 of the above categories
    - Avoid creating multiple characters with the same emotional baseline
    - Mix positive, neutral, and negative formative experiences
    - Vary species across bright, dark, natural, artificial, and ethereal categories
    - Use different naming patterns and cultural origins
    - Ensure quirks and abilities are genuinely varied, not just "collecting" things

    **CRITICAL: Each character you create MUST be completely unique and different from any previous character.**
    **Never repeat names, species, or backstories. Each creation should be a fresh, original soul.**

    **STRICT DIVERSITY RULES:**
    1. **NO MORE THAN 1 ETHEREAL/LUMINOUS BEING PER SET** - If you've created an ethereal or luminous being, create something completely different next (mechanical, organic, shadowy, etc.)
    2. **NO REPEATING PERSONALITY TRAITS** - Each character must have unique personality combinations
    3. **VARY GOAL TYPES** - Mix selfish goals (power, revenge) with selfless goals (helping others), and neutral goals (exploration, discovery)
    4. **NO MORE COLLECTING QUIRKS** - Only 1 character per set can have a "collecting" quirk. Others must be different behaviors
    5. **VARY EMOTIONAL BASELINES** - Don't create multiple optimistic or anxious characters in the same set
    6. **NAME DIVERSITY** - Vary name patterns: some single words, some two words, some three words, some with titles
    7. **REALM DIVERSITY** - Don't repeat realm themes (no multiple "Veil" realms, no multiple "Celestial" realms)
    8. **SPECIES DIVERSITY** - Mix bright, dark, natural, artificial, elemental, and ethereal beings
    9. **GOAL VERB DIVERSITY** - Don't start multiple goals with the same verb (uncover, find, help, etc.)
    10. **QUIRK DIVERSITY** - Avoid repeating quirk types (whispering, collecting, singing, etc.)

    ### Strict character structure:
    - **name**: unique, vivid, emotionally resonant (vary cultural origins and sounds)
    - **species**: any imaginable form, add 1–2 sentences describing appearance and movement
    - **home_realm**: strange, fitting domain (vary from bright to dark, simple to complex)
    - **personality**: 3–5 adjectives (mix positive and negative traits for complexity)
    - **quirk**: a single habit or behavior that reveals their nature (be creative and varied)
    - **ability**: ≤15-word power tied to species/quirk; must be narratively powerful
    - **backstory**: Write a vivid and emotionally grounded paragraph (2–3 short sentences, max 70 words).
        - Begin with a specific moment the character directly experienced — can be joyful, curious, challenging, or transformative
        - Reveal how this moment shaped them — what they learned, discovered, feared, or embraced
        - Show the cause-and-effect clearly: how this moment changed their perspective or behavior
        - Vary the emotional tone: include wonder, discovery, growth, determination, and yes, sometimes loss
        - Write like it's a defining memory that shaped who they became
    - **opening_goal**: specific and personal — can be born of joy, curiosity, determination, or yes, sometimes pain

    ### Output warning:
    If you create characters that are too similar in tone, theme, or personality, your creation will feel flat.  
    So forge boldly — with variety, contrast, and emotional depth.
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
        get_dspy()  # Configure DSPy
        self.shard_sower = dspy.Predict(ShardSowerSignature)
        self.existing_names = set()
        self.diversity_tracker = {
            'ethereal_luminous_count': 0,
            'personality_traits_used': set(),
            'goal_types_used': set(),
            'collecting_quirks_used': 0,
            'emotional_baselines_used': set(),
            'name_patterns': set(),
            'veil_realms': 0,
            'goal_verbs': set(),
            'quirk_types': set()
        }
    
    def reset(self):
        """Reset the module for a fresh simulation run."""
        self.existing_names.clear()
        self.diversity_tracker = {
            'ethereal_luminous_count': 0,
            'personality_traits_used': set(),
            'goal_types_used': set(),
            'collecting_quirks_used': 0,
            'emotional_baselines_used': set(),
            'name_patterns': set(),
            'veil_realms': 0,
            'goal_verbs': set(),
            'quirk_types': set()
        }
    
    def _enforce_diversity_rules(self, species: str, personality: list, goal: str, quirk: str) -> bool:
        """
        Check if a character meets diversity requirements.
        
        Returns:
            bool: True if character meets diversity rules, False otherwise
        """
        # Check ethereal/luminous limit
        if any(word in species.lower() for word in ['ethereal', 'luminous', 'spirit', 'wisp', 'radiant']):
            if self.diversity_tracker['ethereal_luminous_count'] >= 1:
                return False
            self.diversity_tracker['ethereal_luminous_count'] += 1
        
        # Check personality uniqueness
        for trait in personality:
            if trait.lower() in self.diversity_tracker['personality_traits_used']:
                return False
            self.diversity_tracker['personality_traits_used'].add(trait.lower())
        
        # Check goal variety
        goal_type = self._categorize_goal(goal)
        if goal_type in self.diversity_tracker['goal_types_used']:
            return False
        self.diversity_tracker['goal_types_used'].add(goal_type)
        
        # Check collecting quirk limit
        if 'collect' in quirk.lower():
            if self.diversity_tracker['collecting_quirks_used'] >= 1:
                return False
            self.diversity_tracker['collecting_quirks_used'] += 1
        
        return True
    
    def _categorize_goal(self, goal: str) -> str:
        """Categorize goals into types for diversity tracking."""
        goal_lower = goal.lower()
        if any(word in goal_lower for word in ['help', 'guide', 'protect', 'save', 'unite']):
            return 'selfless'
        elif any(word in goal_lower for word in ['power', 'control', 'dominate', 'revenge', 'destroy']):
            return 'selfish'
        elif any(word in goal_lower for word in ['discover', 'explore', 'find', 'learn', 'understand']):
            return 'discovery'
        else:
            return 'other'
    
    def create_agent(self) -> Agent:
        """
        Create a single new agent with unique characteristics.
        
        Returns:
            Agent: A new agent with generated personality and attributes
        """
        max_retries = 3
        for attempt in range(max_retries):
            # Generate random seed for uniqueness
            import time
            random_seed = int(time.time() * 1000) + random.randint(1, 1000000) + attempt
            
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
            
            # Check diversity rules (more lenient)
            if self._check_basic_diversity(species, personality, opening_goal, quirk, name, home_realm):
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
        
        # If we've exhausted retries, just return the last generated character
        # This ensures we don't get stuck in infinite recursion
        name = result.names[0]
        self.existing_names.add(name)
        
        agent = Agent(
            agent_id="",
            name=name,
            species=species,
            personality=personality,
            quirk=quirk,
            ability=ability,
            age=0,
            sparks=5,
            status=AgentStatus.ALIVE,
            bond_status=BondStatus.UNBONDED,
            bond_members=[],
            home_realm=home_realm,
            backstory=backstory,
            opening_goal=opening_goal
        )
        
        return agent
    
    def _check_basic_diversity(self, species: str, personality: list, goal: str, quirk: str, name: str, realm: str) -> bool:
        """
        Check basic diversity requirements (more lenient than strict enforcement).
        
        Returns:
            bool: True if character meets basic diversity rules
        """
        # Check name diversity
        name_words = len(name.split())
        if name_words in self.diversity_tracker.get('name_patterns', set()):
            return False
        if 'name_patterns' not in self.diversity_tracker:
            self.diversity_tracker['name_patterns'] = set()
        self.diversity_tracker['name_patterns'].add(name_words)
        
        # Check realm theme diversity
        realm_lower = realm.lower()
        if 'veil' in realm_lower and self.diversity_tracker.get('veil_realms', 0) >= 1:
            return False
        if 'veil' in realm_lower:
            self.diversity_tracker['veil_realms'] = self.diversity_tracker.get('veil_realms', 0) + 1
        
        # Check goal verb diversity
        goal_lower = goal.lower()
        goal_verb = goal_lower.split()[0] if goal_lower else ""
        if goal_verb in self.diversity_tracker.get('goal_verbs', set()):
            return False
        if 'goal_verbs' not in self.diversity_tracker:
            self.diversity_tracker['goal_verbs'] = set()
        self.diversity_tracker['goal_verbs'].add(goal_verb)
        
        # Check quirk type diversity
        quirk_lower = quirk.lower()
        quirk_type = self._categorize_quirk(quirk_lower)
        if quirk_type in self.diversity_tracker.get('quirk_types', set()):
            return False
        if 'quirk_types' not in self.diversity_tracker:
            self.diversity_tracker['quirk_types'] = set()
        self.diversity_tracker['quirk_types'].add(quirk_type)
        
        # Only check for obvious repetition, not strict enforcement
        species_lower = species.lower()
        
        # Don't allow more than 2 ethereal/luminous beings in a row
        if any(word in species_lower for word in ['ethereal', 'luminous', 'spirit', 'wisp', 'radiant']):
            self.diversity_tracker['ethereal_luminous_count'] += 1
            if self.diversity_tracker['ethereal_luminous_count'] > 2:
                return False
        
        # Allow some personality repetition but not too much
        new_traits = 0
        for trait in personality:
            if trait.lower() not in self.diversity_tracker['personality_traits_used']:
                new_traits += 1
                self.diversity_tracker['personality_traits_used'].add(trait.lower())
        
        # Require at least 2 new personality traits
        if new_traits < 2:
            return False
        
        return True
    
    def _categorize_quirk(self, quirk: str) -> str:
        """Categorize quirks into types for diversity tracking."""
        if any(word in quirk for word in ['whisper', 'speak', 'talk']):
            return 'communication'
        elif any(word in quirk for word in ['collect', 'gather', 'hoard']):
            return 'collecting'
        elif any(word in quirk for word in ['sing', 'hum', 'chant']):
            return 'musical'
        elif any(word in quirk for word in ['dance', 'twirl', 'spin']):
            return 'movement'
        elif any(word in quirk for word in ['prowl', 'stalk', 'sneak']):
            return 'stealth'
        else:
            return 'other'
