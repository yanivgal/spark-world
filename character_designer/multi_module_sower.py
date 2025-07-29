#!/usr/bin/env python3

import dspy
import random
import time
from typing import List, Dict, Set
from world.state import Agent
from communication.messages.observation_packet import AgentStatus, BondStatus
from character_designer.dspy_init import get_dspy

# ============================================================================
# SPECIALIZED MODULES
# ============================================================================

class NameGeneratorSignature(dspy.Signature):
    """Generate diverse character names with varied patterns."""
    
    existing_names: str = dspy.InputField(desc="List of existing names to avoid")
    name_pattern: str = dspy.InputField(desc="Required pattern: 'single', 'double', 'triple', or 'titled'")
    cultural_origin: str = dspy.InputField(desc="Cultural origin: 'nordic', 'celtic', 'elvish', 'ancient', 'modern', 'alien'")
    
    name: str = dspy.OutputField(desc="A unique character name following the specified pattern")

class SpeciesGeneratorSignature(dspy.Signature):
    """Generate diverse species types."""
    
    excluded_categories: str = dspy.InputField(desc="Species categories to avoid (ethereal, luminous, etc.)")
    required_category: str = dspy.InputField(desc="Required category: 'bright', 'dark', 'natural', 'artificial', 'elemental', 'ethereal'")
    
    species: str = dspy.OutputField(desc="A unique species with 1-2 sentence description")
    category: str = dspy.OutputField(desc="The category this species belongs to")

class PersonalityGeneratorSignature(dspy.Signature):
    """Generate diverse personality trait combinations."""
    
    excluded_traits: str = dspy.InputField(desc="Personality traits to avoid")
    emotional_baseline: str = dspy.InputField(desc="Primary emotional tone: 'optimistic', 'melancholic', 'aggressive', 'calm', 'anxious', 'confident', 'shy', 'playful'")
    
    personality: List[str] = dspy.OutputField(desc="3-5 unique personality traits")
    complexity: str = dspy.OutputField(desc="Internal contradiction or complexity")

class GoalGeneratorSignature(dspy.Signature):
    """Generate diverse character goals."""
    
    excluded_verbs: str = dspy.InputField(desc="Goal verbs to avoid")
    goal_type: str = dspy.InputField(desc="Goal type: 'selfish', 'selfless', 'discovery', 'achievement', 'destruction', 'creation'")
    
    goal: str = dspy.OutputField(desc="A unique character goal")
    motivation: str = dspy.OutputField(desc="The underlying motivation")

class QuirkGeneratorSignature(dspy.Signature):
    """Generate diverse character quirks."""
    
    excluded_types: str = dspy.InputField(desc="Quirk types to avoid")
    quirk_category: str = dspy.InputField(desc="Quirk category: 'physical', 'mental', 'social', 'magical', 'habitual'")
    
    quirk: str = dspy.OutputField(desc="A unique character quirk")
    quirk_type: str = dspy.OutputField(desc="The type of quirk")

class BackstoryGeneratorSignature(dspy.Signature):
    """Generate diverse character backstories."""
    
    character_info: str = dspy.InputField(desc="Character name, species, personality, and goal")
    experience_type: str = dspy.InputField(desc="Experience type: 'triumph', 'loss', 'discovery', 'challenge', 'connection', 'betrayal', 'wonder', 'responsibility'")
    
    backstory: str = dspy.OutputField(desc="A unique 2-3 sentence backstory (max 70 words)")

# ============================================================================
# MULTI-MODULE SHARD SOWER
# ============================================================================

class MultiModuleShardSower:
    """
    Multi-module character generation system for maximum diversity.
    
    This approach splits character generation across specialized modules,
    each responsible for one aspect of character creation. This ensures
    better diversity by preventing the LLM from falling into patterns.
    """
    
    def __init__(self):
        """Initialize all specialized modules."""
        get_dspy()
        
        # Initialize specialized modules
        self.name_generator = dspy.Predict(NameGeneratorSignature)
        self.species_generator = dspy.Predict(SpeciesGeneratorSignature)
        self.personality_generator = dspy.Predict(PersonalityGeneratorSignature)
        self.goal_generator = dspy.Predict(GoalGeneratorSignature)
        self.quirk_generator = dspy.Predict(QuirkGeneratorSignature)
        self.backstory_generator = dspy.Predict(BackstoryGeneratorSignature)
        
        # Diversity tracking
        self.diversity_tracker = {
            'names_used': set(),
            'species_categories': [],
            'personality_traits': set(),
            'goal_verbs': set(),
            'quirk_types': set(),
            'experience_types': [],
            'name_patterns': set(),
            'emotional_baselines': set()
        }
    
    def reset(self):
        """Reset for a fresh simulation run."""
        self.diversity_tracker = {
            'names_used': set(),
            'species_categories': [],
            'personality_traits': set(),
            'goal_verbs': set(),
            'quirk_types': set(),
            'experience_types': [],
            'name_patterns': set(),
            'emotional_baselines': set()
        }
    
    def _get_next_name_pattern(self) -> str:
        """Get the next required name pattern."""
        patterns = ['single', 'double', 'triple', 'titled']
        used_patterns = self.diversity_tracker['name_patterns']
        
        for pattern in patterns:
            if pattern not in used_patterns:
                return pattern
        
        # If all patterns used, reset and start over
        self.diversity_tracker['name_patterns'].clear()
        return 'single'
    
    def _get_next_species_category(self) -> str:
        """Get the next required species category."""
        categories = ['bright', 'dark', 'natural', 'artificial', 'elemental', 'ethereal']
        used_categories = self.diversity_tracker['species_categories']
        
        # Don't allow more than 1 ethereal/luminous in a row
        if len(used_categories) >= 2:
            last_two = used_categories[-2:]
            if all(cat in ['bright', 'ethereal'] for cat in last_two):
                categories = [cat for cat in categories if cat not in ['bright', 'ethereal']]
        
        for category in categories:
            if category not in used_categories[-2:]:  # Don't repeat last 2
                return category
        
        return random.choice(categories)
    
    def _get_next_emotional_baseline(self) -> str:
        """Get the next emotional baseline."""
        baselines = ['optimistic', 'melancholic', 'aggressive', 'calm', 'anxious', 'confident', 'shy', 'playful']
        used_baselines = self.diversity_tracker['emotional_baselines']
        
        for baseline in baselines:
            if baseline not in used_baselines:
                return baseline
        
        # If all used, reset and start over
        self.diversity_tracker['emotional_baselines'].clear()
        return 'optimistic'
    
    def _get_next_goal_type(self) -> str:
        """Get the next goal type."""
        goal_types = ['selfish', 'selfless', 'discovery', 'achievement', 'destruction', 'creation']
        used_goals = [goal.split()[0].lower() for goal in self.diversity_tracker.get('goal_verbs', [])]
        
        # Map goal types to common verbs
        goal_verb_map = {
            'selfish': ['control', 'dominate', 'destroy', 'conquer'],
            'selfless': ['help', 'protect', 'save', 'guide'],
            'discovery': ['explore', 'find', 'discover', 'learn'],
            'achievement': ['master', 'achieve', 'create', 'build'],
            'destruction': ['destroy', 'eliminate', 'remove', 'break'],
            'creation': ['create', 'build', 'make', 'form']
        }
        
        for goal_type in goal_types:
            verbs = goal_verb_map[goal_type]
            if not any(verb in used_goals for verb in verbs):
                return goal_type
        
        return random.choice(goal_types)
    
    def _get_next_quirk_category(self) -> str:
        """Get the next quirk category."""
        categories = ['physical', 'mental', 'social', 'magical', 'habitual']
        used_types = self.diversity_tracker['quirk_types']
        
        for category in categories:
            if category not in used_types:
                return category
        
        return random.choice(categories)
    
    def _get_next_experience_type(self) -> str:
        """Get the next experience type."""
        types = ['triumph', 'loss', 'discovery', 'challenge', 'connection', 'betrayal', 'wonder', 'responsibility']
        used_types = self.diversity_tracker['experience_types']
        
        for exp_type in types:
            if exp_type not in used_types:
                return exp_type
        
        return random.choice(types)
    
    def create_agent(self) -> Agent:
        """
        Create a character using the multi-module approach.
        
        Returns:
            Agent: A new agent with maximum diversity
        """
        # Step 1: Generate name
        name_pattern = self._get_next_name_pattern()
        cultural_origin = random.choice(['nordic', 'celtic', 'elvish', 'ancient', 'modern', 'alien'])
        
        name_result = self.name_generator(
            existing_names=list(self.diversity_tracker['names_used']),
            name_pattern=name_pattern,
            cultural_origin=cultural_origin
        )
        name = name_result.name
        self.diversity_tracker['names_used'].add(name)
        self.diversity_tracker['name_patterns'].add(name_pattern)
        
        # Step 2: Generate species
        species_category = self._get_next_species_category()
        excluded_categories = []
        if len(self.diversity_tracker['species_categories']) >= 2:
            excluded_categories = self.diversity_tracker['species_categories'][-2:]
        
        species_result = self.species_generator(
            excluded_categories=", ".join(excluded_categories),
            required_category=species_category
        )
        species = species_result.species
        self.diversity_tracker['species_categories'].append(species_category)
        
        # Step 3: Generate personality
        emotional_baseline = self._get_next_emotional_baseline()
        excluded_traits = list(self.diversity_tracker['personality_traits'])
        
        personality_result = self.personality_generator(
            excluded_traits=", ".join(excluded_traits),
            emotional_baseline=emotional_baseline
        )
        personality = personality_result.personality
        self.diversity_tracker['personality_traits'].update([trait.lower() for trait in personality])
        self.diversity_tracker['emotional_baselines'].add(emotional_baseline)
        
        # Step 4: Generate goal
        goal_type = self._get_next_goal_type()
        excluded_verbs = list(self.diversity_tracker['goal_verbs'])
        
        goal_result = self.goal_generator(
            excluded_verbs=", ".join(excluded_verbs),
            goal_type=goal_type
        )
        goal = goal_result.goal
        goal_verb = goal.split()[0].lower()
        self.diversity_tracker['goal_verbs'].add(goal_verb)
        
        # Step 5: Generate quirk
        quirk_category = self._get_next_quirk_category()
        excluded_types = list(self.diversity_tracker['quirk_types'])
        
        quirk_result = self.quirk_generator(
            excluded_types=", ".join(excluded_types),
            quirk_category=quirk_category
        )
        quirk = quirk_result.quirk
        self.diversity_tracker['quirk_types'].add(quirk_category)
        
        # Step 6: Generate backstory
        experience_type = self._get_next_experience_type()
        character_info = f"Name: {name}, Species: {species}, Personality: {personality}, Goal: {goal}"
        
        backstory_result = self.backstory_generator(
            character_info=character_info,
            experience_type=experience_type
        )
        backstory = backstory_result.backstory
        self.diversity_tracker['experience_types'].append(experience_type)
        
        # Step 7: Generate ability (simple template-based)
        ability = self._generate_ability(species, quirk)
        
        # Step 8: Generate realm (simple template-based)
        realm = self._generate_realm(species_category)
        
        # Create and return agent
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
            home_realm=realm,
            backstory=backstory,
            opening_goal=goal
        )
        
        return agent
    
    def _generate_ability(self, species: str, quirk: str) -> str:
        """Generate a simple ability based on species and quirk."""
        abilities = [
            "Can manipulate shadows and darkness",
            "Able to create and control light",
            "Can communicate with animals",
            "Able to sense emotions of others",
            "Can transform into different forms",
            "Able to heal minor wounds",
            "Can create illusions and mirages",
            "Able to control elemental forces",
            "Can read thoughts and memories",
            "Able to teleport short distances"
        ]
        return random.choice(abilities)
    
    def _generate_realm(self, species_category: str) -> str:
        """Generate a realm based on species category."""
        realm_templates = {
            'bright': ['The Radiant Plains', 'Sunlit Meadows', 'Golden Valley', 'Luminous Heights'],
            'dark': ['The Shadowed Depths', 'Twilight Hollow', 'Darkened Woods', 'Veil of Night'],
            'natural': ['The Ancient Forest', 'Whispering Grove', 'Mystic Woods', 'Wild Meadows'],
            'artificial': ['The Iron Citadel', 'Crystal Spires', 'Mechanical Gardens', 'Steel Forge'],
            'elemental': ['The Storm Peaks', 'Flame Valley', 'Ice Caverns', 'Thunder Plains'],
            'ethereal': ['The Dream Realm', 'Spirit World', 'Ethereal Veil', 'Mystic Realm']
        }
        
        templates = realm_templates.get(species_category, ['The Mysterious Realm'])
        return random.choice(templates)