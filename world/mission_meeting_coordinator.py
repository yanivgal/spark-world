import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from character_designer.dspy_init import get_dspy
import dspy
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

from world.state import Mission, Bond, Agent, WorldState
from communication.messages.mission_meeting_message import MissionMeetingMessage
from communication.messages.action_message import ActionMessage


@dataclass
class LeaderIntroductionSignature(dspy.Signature):
    """
    Generate the leader's introduction message for a new mission.
    
    This happens only once when a mission is first created.
    The leader introduces the mission goal and team members.
    """
    
    # Input: Mission and team information
    mission_details: str = dspy.InputField(desc="Mission title, description, and goal")
    team_members: str = dspy.InputField(desc="List of bonded agents with their names, species, and personalities")
    leader_info: str = dspy.InputField(desc="Leader's name, species, and personality")
    
    # Output: Introduction message
    introduction_message: str = dspy.OutputField(desc="Leader's introduction of the mission and team")


@dataclass
class LeaderOpeningSignature(dspy.Signature):
    """
    Generate the leader's opening message for each mission meeting.
    
    This happens every tick. The leader reflects on previous actions
    and prompts the team for input on next steps.
    """
    
    # Input: Mission and previous actions
    mission_details: str = dspy.InputField(desc="Mission title, description, and goal")
    previous_actions: str = dspy.InputField(desc="What the team did in the previous tick")
    current_progress: str = dspy.InputField(desc="Current progress toward the mission goal")
    team_members: str = dspy.InputField(desc="List of bonded agents")
    leader_info: str = dspy.InputField(desc="Leader's name and personality")
    
    # Output: Opening message
    opening_message: str = dspy.OutputField(desc="Leader's opening message prompting team input")


@dataclass
class AgentResponseSignature(dspy.Signature):
    """
    Generate an agent's response during a mission meeting.
    
    Each bonded agent provides their opinion, suggestions, and preferences
    based on their personality and the current situation.
    """
    
    # Input: Agent and meeting context
    agent_info: str = dspy.InputField(desc="Agent's name, species, personality, and current state")
    mission_details: str = dspy.InputField(desc="Mission title, description, and goal")
    leader_message: str = dspy.InputField(desc="Leader's opening message or introduction")
    previous_actions: str = dspy.InputField(desc="What the team did in the previous tick")
    current_progress: str = dspy.InputField(desc="Current progress toward the mission goal")
    
    # Output: Agent's response
    response_message: str = dspy.OutputField(desc="Agent's opinion, suggestion, or strategy")
    preferred_role: str = dspy.OutputField(desc="What role the agent would like to take (optional)")
    reasoning: str = dspy.OutputField(desc="Why the agent thinks this way")


@dataclass
class TaskAssignmentSignature(dspy.Signature):
    """
    Generate the leader's task assignments based on team responses.
    
    The leader processes all team member responses and creates
    a structured plan with specific tasks for each agent.
    """
    
    # Input: Mission and team responses
    mission_details: str = dspy.InputField(desc="Mission title, description, and goal")
    team_responses: str = dspy.InputField(desc="All team member responses and preferences")
    current_progress: str = dspy.InputField(desc="Current progress toward the mission goal")
    leader_info: str = dspy.InputField(desc="Leader's name and personality")
    
    # Output: Task assignments
    task_assignments: str = dspy.OutputField(desc="Specific tasks for each team member")
    coordination_notes: str = dspy.OutputField(desc="Notes about coordination and timing")
    encouragement: str = dspy.OutputField(desc="Encouragement or motivation for the team")


class MissionMeetingCoordinator:
    """
    Coordinates mission meetings between bonded agents.
    
    This system manages the structured meeting flow:
    1. Leader introduction (first tick only)
    2. Leader opening message (each tick)
    3. Agent responses
    4. Task assignments
    """
    
    def __init__(self):
        """Initialize the meeting coordinator with DSPy modules."""
        get_dspy()  # Configure DSPy
        
        self.leader_intro = dspy.ChainOfThought(LeaderIntroductionSignature)
        self.leader_opening = dspy.ChainOfThought(LeaderOpeningSignature)
        self.agent_response = dspy.ChainOfThought(AgentResponseSignature)
        self.task_assignment = dspy.ChainOfThought(TaskAssignmentSignature)
    
    def conduct_mission_meeting(self, mission: Mission, bond: Bond, agents: Dict[str, Agent], 
                               tick: int, previous_actions: List[str] = None) -> List[MissionMeetingMessage]:
        """
        Conduct a complete mission meeting for a bond.
        
        Args:
            mission: The active mission
            bond: The bond conducting the meeting
            agents: All agents in the world
            tick: Current tick number
            previous_actions: Actions taken by bonded agents in previous tick
            
        Returns:
            List[MissionMeetingMessage]: All messages exchanged during the meeting
        """
        meeting_messages = []
        
        # Get team member information
        team_members = [agents[agent_id] for agent_id in bond.members]
        leader = agents[mission.leader_id]
        
        # Step 1: Leader Introduction (first tick only)
        if tick == mission.created_tick:
            intro_message = self._generate_leader_introduction(mission, team_members, leader)
            meeting_messages.append(intro_message)
        
        # Step 2: Leader Opening Message (each tick)
        opening_message = self._generate_leader_opening(mission, team_members, leader, previous_actions or [])
        meeting_messages.append(opening_message)
        
        # Step 3: Agent Responses
        agent_responses = []
        for agent in team_members:
            if agent.agent_id != mission.leader_id:  # Leader doesn't respond to their own opening
                response = self._generate_agent_response(agent, mission, opening_message.content, previous_actions or [])
                meeting_messages.append(response)
                agent_responses.append(response)
        
        # Step 4: Task Assignment
        if agent_responses:  # Only if there are responses to process
            task_message = self._generate_task_assignment(mission, leader, agent_responses)
            meeting_messages.append(task_message)
        
        return meeting_messages
    
    def _generate_leader_introduction(self, mission: Mission, team_members: List[Agent], leader: Agent) -> MissionMeetingMessage:
        """Generate the leader's introduction message for a new mission."""
        
        # Prepare mission details
        mission_details = f"Title: {mission.title}\nDescription: {mission.description}\nGoal: {mission.goal}"
        
        # Prepare team member information
        team_info = []
        for agent in team_members:
            team_info.append(f"{agent.name} ({agent.species}) - {', '.join(agent.personality)}")
        team_members_str = "\n".join(team_info)
        
        # Prepare leader information
        leader_info = f"{leader.name} ({leader.species}) - {', '.join(leader.personality)}"
        
        # Generate introduction using DSPy
        intro_output = self.leader_intro(
            mission_details=mission_details,
            team_members=team_members_str,
            leader_info=leader_info
        )
        
        return MissionMeetingMessage(
            sender_id=leader.agent_id,
            message_type="leader_introduction",
            content=intro_output.introduction_message,
            reasoning=f"Introducing the mission to the team as the designated leader",
            tick=mission.created_tick,
            mission_id=mission.mission_id
        )
    
    def _generate_leader_opening(self, mission: Mission, team_members: List[Agent], leader: Agent, 
                                previous_actions: List[str]) -> MissionMeetingMessage:
        """Generate the leader's opening message for each meeting."""
        
        # Prepare inputs
        mission_details = f"Title: {mission.title}\nDescription: {mission.description}\nGoal: {mission.goal}"
        previous_actions_str = "\n".join([f"- {action}" for action in previous_actions]) if previous_actions else "No actions taken"
        current_progress = mission.current_progress
        
        team_info = []
        for agent in team_members:
            team_info.append(f"{agent.name} ({agent.species})")
        team_members_str = "\n".join(team_info)
        
        leader_info = f"{leader.name} ({leader.species}) - {', '.join(leader.personality)}"
        
        # Generate opening using DSPy
        opening_output = self.leader_opening(
            mission_details=mission_details,
            previous_actions=previous_actions_str,
            current_progress=current_progress,
            team_members=team_members_str,
            leader_info=leader_info
        )
        
        return MissionMeetingMessage(
            sender_id=leader.agent_id,
            message_type="leader_opening",
            content=opening_output.opening_message,
            reasoning=f"Opening the mission meeting and prompting team input",
            tick=mission.created_tick,  # Will be updated by caller
            mission_id=mission.mission_id
        )
    
    def _generate_agent_response(self, agent: Agent, mission: Mission, leader_message: str, 
                                previous_actions: List[str]) -> MissionMeetingMessage:
        """Generate an agent's response during the meeting."""
        
        # Prepare agent information
        agent_info = f"{agent.name} ({agent.species}) - {', '.join(agent.personality)} - Sparks: {agent.sparks}, Age: {agent.age}"
        
        # Prepare mission details
        mission_details = f"Title: {mission.title}\nDescription: {mission.description}\nGoal: {mission.goal}"
        
        # Prepare previous actions
        previous_actions_str = "\n".join([f"- {action}" for action in previous_actions]) if previous_actions else "No actions taken"
        
        # Generate response using DSPy
        response_output = self.agent_response(
            agent_info=agent_info,
            mission_details=mission_details,
            leader_message=leader_message,
            previous_actions=previous_actions_str,
            current_progress=mission.current_progress
        )
        
        return MissionMeetingMessage(
            sender_id=agent.agent_id,
            message_type="agent_response",
            content=response_output.response_message,
            reasoning=response_output.reasoning,
            tick=mission.created_tick,  # Will be updated by caller
            mission_id=mission.mission_id
        )
    
    def _generate_task_assignment(self, mission: Mission, leader: Agent, 
                                 agent_responses: List[MissionMeetingMessage]) -> MissionMeetingMessage:
        """Generate the leader's task assignments based on team responses."""
        
        # Prepare mission details
        mission_details = f"Title: {mission.title}\nDescription: {mission.description}\nGoal: {mission.goal}"
        
        # Prepare team responses
        responses_str = ""
        for response in agent_responses:
            responses_str += f"{response.sender_id}: {response.content}\n"
        
        # Prepare leader information
        leader_info = f"{leader.name} ({leader.species}) - {', '.join(leader.personality)}"
        
        # Generate task assignment using DSPy
        task_output = self.task_assignment(
            mission_details=mission_details,
            team_responses=responses_str,
            current_progress=mission.current_progress,
            leader_info=leader_info
        )
        
        return MissionMeetingMessage(
            sender_id=leader.agent_id,
            message_type="task_assignment",
            content=f"{task_output.task_assignments}\n\n{task_output.coordination_notes}\n\n{task_output.encouragement}",
            reasoning=f"Assigning tasks based on team member responses and mission needs",
            tick=mission.created_tick,  # Will be updated by caller
            mission_id=mission.mission_id
        ) 