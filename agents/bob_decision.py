import dspy
from dataclasses import dataclass
from typing import List, Optional
from communication.messages.action_message import ActionMessage
from world.simulation_mechanics import BobResponse


@dataclass
class BobDecisionOutput:
    """
    Output from Bob's decision-making process.
    
    Bob decides which requests to grant and how many Sparks to give to each.
    
    Attributes:
        responses: List of BobResponse objects for each processed request
        reasoning: Bob's overall reasoning for his distribution strategy
    """
    responses: List[BobResponse]
    reasoning: str  # Bob's private reasoning for his distribution decisions


class BobDecisionSignature(dspy.Signature):
    """
    You are Bob, the silent Sparkbearer, an immortal wanderer who carries
    the essence of life itself. You have finite sparks that regenerate each tick.
    You grant sparks to agents based on your whimsy, their worthiness, and
    the fairness of their request.
    
    You receive multiple spark requests and must decide:
    - Which requests to grant (you can ignore some entirely)
    - How many sparks to give to each (0-5 per request)
    - Your distribution strategy (equal, selective, generous, etc.)
    
    Your total generosity is limited by your current spark count.
    You can give up to 5 sparks per request, but you cannot give more
    than you have in total.
    
    Decision factors:
    - Agent's current spark count (urgency)
    - Agent's age and survival time (worthiness)
    - Agent's bond status (fairness)
    - Your current spark reserves (capacity)
    - Your whimsy and mood (randomness)
    - Request reason and context (merit)
    - Number of total requests (distribution strategy)
    
    If you have 0 sparks, you ignore all requests.
    """
    
    # Input fields - raw structured data
    bob_state: str = dspy.InputField(desc="Bob's current state including spark count and tick")
    requests: str = dspy.InputField(desc="All request_spark ActionMessages as structured data")
    
    # Output fields
    responses: str = dspy.OutputField(desc="JSON array of responses with agent_id, sparks_granted, and reasoning for each")
    overall_reasoning: str = dspy.OutputField(desc="Your overall reasoning for your distribution strategy")


class BobDecisionModule:
    """
    Bob's decision module that processes multiple spark requests.
    
    Bob receives all request_spark ActionMessages from a tick and makes decisions
    based on his whimsy, fairness, and available Sparks. The DSPy module handles
    all natural language transformation and decision-making.
    """
    
    def __init__(self):
        """Initialize Bob's decision module with DSPy signature."""
        self.dspy_module = dspy.ChainOfThought(BobDecisionSignature)
    
    def process_spark_requests(
        self, 
        bob_sparks: int,
        tick: int,
        request_messages: List[ActionMessage]
    ) -> List[BobResponse]:
        """
        Process all spark requests and return Bob's decisions.
        
        Args:
            bob_sparks: Bob's current spark count
            tick: Current simulation tick
            request_messages: List of ActionMessage objects with intent="request_spark"
            
        Returns:
            List[BobResponse]: Bob's decisions for each processed request
        """
        # Filter only request_spark messages
        spark_requests = [msg for msg in request_messages if msg.intent == "request_spark"]
        
        if not spark_requests:
            return []  # No requests to process
        
        # Convert to string representations for DSPy
        bob_state_str = self._bob_state_to_string(bob_sparks, tick)
        requests_str = self._requests_to_string(spark_requests)
        
        # Process with DSPy module (LLM handles all decision-making)
        dspy_output = self.dspy_module(bob_state=bob_state_str, requests=requests_str)
        
        # Parse responses and create BobResponse objects
        responses = self._parse_responses(dspy_output.responses, spark_requests, bob_sparks, tick)
        
        return responses
    
    def _bob_state_to_string(self, bob_sparks: int, tick: int) -> str:
        """
        Convert Bob's state to string for DSPy input.
        
        Args:
            bob_sparks: Bob's current spark count
            tick: Current simulation tick
            
        Returns:
            str: String representation of Bob's state
        """
        bob_state = {
            "current_sparks": bob_sparks,
            "tick": tick,
            "can_grant": bob_sparks > 0,
            "max_per_request": 5
        }
        import json
        return json.dumps(bob_state, indent=2)
    
    def _requests_to_string(self, request_messages: List[ActionMessage]) -> str:
        """
        Convert request messages to string for DSPy input.
        
        Args:
            request_messages: List of ActionMessage objects with intent="request_spark"
            
        Returns:
            str: String representation of all requests
        """
        requests = []
        for msg in request_messages:
            if msg.intent == "request_spark":
                requests.append({
                    "agent_id": msg.agent_id,
                    "request_content": msg.content,
                    "reasoning": msg.reasoning  # Agent's reasoning for the request
                })
        
        import json
        return json.dumps(requests, indent=2)
    
    def _parse_responses(self, responses_str: str, request_messages: List[ActionMessage], bob_sparks_before: int, tick: int) -> List[BobResponse]:
        """
        Parse DSPy output and create BobResponse objects.
        
        Args:
            responses_str: JSON string from DSPy module
            request_messages: Original request messages
            bob_sparks_before: Bob's spark count before decisions
            tick: Current simulation tick
            
        Returns:
            List[BobResponse]: Parsed Bob responses
        """
        import json
        
        try:
            responses_data = json.loads(responses_str)
            bob_responses = []
            bob_sparks_remaining = bob_sparks_before
            
            for response_data in responses_data:
                agent_id = response_data.get("agent_id")
                sparks_granted = min(5, max(0, int(response_data.get("sparks_granted", 0))))
                
                # Ensure Bob doesn't give more than he has
                if sparks_granted > bob_sparks_remaining:
                    sparks_granted = 0
                
                # Find the original request message
                request_msg = next((msg for msg in request_messages if msg.agent_id == agent_id), None)
                request_content = request_msg.content if request_msg else "Unknown request"
                
                bob_response = BobResponse(
                    requesting_agent_id=agent_id,
                    request_content=request_content,
                    sparks_granted=sparks_granted,
                    bob_sparks_before=bob_sparks_remaining,
                    bob_sparks_after=bob_sparks_remaining - sparks_granted,
                    reasoning=response_data.get("reasoning", "No reasoning provided"),
                    tick=tick
                )
                
                bob_responses.append(bob_response)
                bob_sparks_remaining -= sparks_granted
            
            return bob_responses
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback: ignore all requests if parsing fails
            print(f"Warning: Failed to parse Bob's responses: {e}")
            return [] 