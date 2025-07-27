from dataclasses import dataclass
from typing import Optional


@dataclass
class MissionMeetingMessage:
    """
    Messages exchanged during mission meetings between bonded agents.
    
    Mission meetings happen before each tick for bonded agents with active missions.
    The flow includes: leader introduction, agent responses, and task assignments.
    
    Attributes:
        sender_id: ID of the agent sending the message
        message_type: Type of message (leader_introduction, leader_opening, agent_response, task_assignment)
        content: The message content
        reasoning: Why the agent sent this message
        tick: When this message was sent
        mission_id: ID of the mission this message relates to
        target_agent_id: For task assignments, which agent gets the task (None for broadcast messages)
        task_description: For task assignments, what the agent should do (None for other message types)
    """
    sender_id: str
    message_type: str  # "leader_introduction", "leader_opening", "agent_response", "task_assignment"
    content: str
    reasoning: str
    tick: int
    mission_id: str
    target_agent_id: Optional[str] = None  # For task assignments
    task_description: Optional[str] = None  # For task assignments 