import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_client import get_dspy
import dspy
from dataclasses import dataclass
from typing import List, Dict, Optional
import uuid
import random

from world.state import Mission, Bond, Agent
from communication.messages.mission_meeting_message import MissionMeetingMessage


@dataclass
class MissionGenerationSignature(dspy.Signature):
    """
    Generate a unique mission for a newly formed bond.
    
    The mission should be collaborative, achievable, and interesting.
    It should give bonded agents a shared goal beyond just generating Sparks.
    """
    
    # Input: Bond information
    bond_members: str = dspy.InputField(desc="List of bonded agents with their names, species, and personalities")
    bond_size: str = dspy.InputField(desc="Number of agents in the bond")
    world_context: str = dspy.InputField(desc="Current state of Spark-World (tick, total agents, etc.)")
    
    # Output: Mission details
    mission_title: str = dspy.OutputField(desc="Short, catchy title for the mission")
    mission_description: str = dspy.OutputField(desc="Detailed description of what the mission involves")
    mission_goal: str = dspy.OutputField(desc="Clear, specific objective that can be measured")
    mission_strategy: str = dspy.OutputField(desc="Suggested approach for completing the mission")
    estimated_difficulty: str = dspy.OutputField(desc="How challenging this mission will be (easy/medium/hard)")


@dataclass
class MissionProgressSignature(dspy.Signature):
    """
    Evaluate mission progress and determine if it's complete.
    
    Based on agent actions and current world state, determine if the mission
    objective has been achieved.
    """
    
    # Input: Mission and progress data
    mission_details: str = dspy.InputField(desc="Mission title, description, and goal")
    agent_actions: str = dspy.InputField(desc="Actions taken by bonded agents this tick")
    current_world_state: str = dspy.InputField(desc="Current state of agents, bonds, and world")
    mission_history: str = dspy.InputField(desc="Previous actions and progress toward mission")
    
    # Output: Progress evaluation
    is_complete: str = dspy.OutputField(desc="Whether the mission objective has been achieved (yes/no)")
    progress_summary: str = dspy.OutputField(desc="Summary of progress made toward the goal")
    completion_reasoning: str = dspy.OutputField(desc="Why the mission is or isn't complete")


class MissionSystem:
    """
    Manages mission generation, progress tracking, and completion evaluation.
    
    This system creates missions when bonds form and evaluates their progress
    based on agent actions and world state.
    """
    
    def __init__(self):
        """Initialize the mission system with DSPy modules."""
        get_dspy()  # Configure DSPy
        
        self.mission_generator = dspy.ChainOfThought(MissionGenerationSignature)
        self.progress_evaluator = dspy.ChainOfThought(MissionProgressSignature)
    
    def generate_mission_for_bond(self, bond: Bond, agents: Dict[str, Agent], world_context: str) -> Mission:
        """
        Generate a unique mission for a newly formed bond.
        
        Args:
            bond: The bond that just formed
            agents: All agents in the world
            world_context: Current world state information
            
        Returns:
            Mission: A new mission for the bond
        """
        # Prepare bond member information
        member_info = []
        for agent_id in bond.members:
            agent = agents[agent_id]
            member_info.append(f"{agent.name} ({agent.species}) - {', '.join(agent.personality)}")
        
        bond_members_str = "\n".join(member_info)
        bond_size_str = f"{len(bond.members)} agents"
        
        # Generate mission using DSPy
        mission_output = self.mission_generator(
            bond_members=bond_members_str,
            bond_size=bond_size_str,
            world_context=world_context
        )
        
        # Create mission object
        mission = Mission(
            mission_id=str(uuid.uuid4()),
            bond_id=bond.bond_id,
            title=mission_output.mission_title,
            description=mission_output.mission_description,
            goal=mission_output.mission_goal,
            current_progress="Mission just started",
            leader_id=bond.leader_id,
            assigned_tasks={},
            is_complete=False,
            created_tick=0  # Will be set by World Engine
        )
        
        return mission
    
    def evaluate_mission_progress(self, mission: Mission, agent_actions: List, world_state: str, mission_history: str) -> Dict:
        """
        Evaluate whether a mission has been completed based on agent actions.
        
        Args:
            mission: The mission to evaluate
            agent_actions: Actions taken by bonded agents
            world_state: Current world state
            mission_history: Previous mission progress
            
        Returns:
            Dict: Evaluation results including completion status
        """
        # Prepare mission details
        mission_details = f"Title: {mission.title}\nDescription: {mission.description}\nGoal: {mission.goal}"
        
        # Format agent actions
        actions_str = "\n".join([f"- {action}" for action in agent_actions]) if agent_actions else "No actions taken"
        
        # Evaluate progress using DSPy
        evaluation = self.progress_evaluator(
            mission_details=mission_details,
            agent_actions=actions_str,
            current_world_state=world_state,
            mission_history=mission_history
        )
        
        return {
            "is_complete": evaluation.is_complete.lower() == "yes",
            "progress_summary": evaluation.progress_summary,
            "completion_reasoning": evaluation.completion_reasoning
        }
    
    def select_mission_leader(self, bond_members: List[str]) -> str:
        """
        Randomly select a mission leader from bond members.
        
        Args:
            bond_members: List of agent IDs in the bond
            
        Returns:
            str: Selected leader agent ID
        """
        return random.choice(bond_members) 