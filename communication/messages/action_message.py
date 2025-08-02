from dataclasses import dataclass
from typing import Optional


@dataclass
class ActionMessage:
    """
    The primary communication structure for agent actions in Spark-World.
    
    This is the core message type that agents use to communicate with the world
    and other agents. Every agent action flows through this structure.
    
    Attributes:
        agent_id: Unique identifier of the agent sending the message
        intent: The type of action being performed (bond, raid, request_spark, spawn, reply)
        target: Target agent_id if the action is directed at someone, None otherwise
        content: The actual message content that other agents will see
        reasoning: The agent's internal thought process (for debugging and storytelling)
        tick: The tick number when this action was created (for filtering in observation packets)
        bond_type: Type of bond action ("request" or "acceptance") - only used when intent is "bond"
    """
    agent_id: str
    intent: str  # "bond", "raid", "request_spark", "spawn", "reply"
    target: Optional[str]  # target agent_id or None
    content: str  # the actual message content
    reasoning: str  # what the agent was thinking when making this decision
    tick: int = 0  # the tick when this action was created
    bond_type: Optional[str] = None  # "request" or "acceptance" - only used when intent is "bond" 