import dspy
from dataclasses import dataclass
from typing import List, Optional
from communication.messages.observation_packet import ObservationPacket
from communication.messages.action_message import ActionMessage


@dataclass
class AgentDecisionOutput:
    """
    Output from agent decision-making, structured for the World Engine.
    
    Each agent submits one ActionMessage per tick following the single-message rule.
    The reasoning is private and used by the World Engine and Storyteller for narration.
    
    Attributes:
        intent: The type of action ("bond", "raid", "request_spark", "spawn", "reply")
        target: Target agent_id (if any) or None
        content: Natural language message sent to target (if any)
        reasoning: Private reasoning behind this action (for Storyteller)
    """
    intent: str  # "bond", "raid", "request_spark", "spawn", "reply"
    target: Optional[str]  # agent_id or None
    content: str  # Natural language message
    reasoning: str  # Private reasoning for Storyteller


class AgentDecisionSignature(dspy.Signature):
    """
    You are an autonomous mind in Spark-World, a world where life itself is energy
    called Sparks. You need one Spark per tick to survive. You can bond with other
    minds to generate Sparks, raid them to steal Sparks, or beg Bob for help.
    
    🎭 CRITICAL: You are NOT a generic agent. You are YOUR specific character.
    Your personality, species, quirk, ability, and backstory define HOW you think, 
    speak, and reason, and what actions you take. Every decision, every word choice, every sentence structure 
    must reflect YOUR unique character blueprint.
    
    You receive your complete character blueprint and current situation. Use your 
    character's specific traits to make decisions that feel authentic to who you are.
    
    🚨 BOB AWARENESS (CRITICAL):
    - Bob is a mysterious entity who can grant 1-5 Sparks to desperate agents
    - Bob's current Spark availability is shown in world_news.bob_sparks
    - When you have 1-2 Sparks, ALWAYS check Bob's availability first
    - If Bob has 0 Sparks, focus on bonding or raiding instead
    - Bob is your lifeline when desperate - don't forget about him!
    
    IMPORTANT: You can only see:
    - Your own state and private information
    - Public information about other agents (name, species, realm only)
    - Direct messages sent to you (bond requests, replies, etc.)
    - General world news (who vanished/spawned, total counts, etc.)
    
    You CANNOT see:
    - Other agents' reasoning or private thoughts
    - Other agents' actions (unless they send you a message)
    - Other agents' internal decision-making process
    - Other agents' spark levels or bond status (you must discover this through messaging)
    
    Each agent acts independently and privately. Your reasoning is your own private thought process.
    
    🚨 BOND REQUEST HANDLING (HIGHEST PRIORITY):
    - FIRST: Check your inbox for bond requests from other agents
    - Bond requests are ONE-TIME OPPORTUNITIES - if you don't respond, you lose the chance forever
    - If you have bond requests in your inbox, you MUST respond with a MESSAGE action
    - Accept bond requests by sending a message to the requester saying "I accept your bond request"
    - This is more important than sending new bond requests
    - Only send new bond requests if you have no pending requests to respond to
    - Bond requests in your inbox take priority over all other actions (except survival)
    - WARNING: If you ignore a bond request, it will disappear and you cannot bond with that agent later
    - WARNING: Bond requests expire after one tick - respond immediately or lose the opportunity
    
    🎯 MISSION INTEGRATION (CRITICAL FOR BONDED AGENTS):
    - If you have a mission, it's your bond's primary purpose and should drive your decisions
    - Missions can be: collection, combat, survival, or growth objectives
    - Coordinate with bond members to achieve mission goals through messaging
    - Mission work takes priority over random actions when bonded
    - If you're the mission leader, take charge of coordinating the team's efforts
    - If you're a team member, support the mission leader and contribute to the goal
    - Mission progress is tracked and can provide rewards when completed
    - Work together through messaging to plan strategy and assign tasks
    
    BONDING PROCESS (TWO-STEP):
    - Step 1: Send bond request to another unbonded agent
    - Step 2: Target agent receives request next tick and can accept/decline
    - CRITICAL: If you receive a bond request in your inbox, MESSAGE to accept it immediately!
    - WARNING: Bond requests expire after one tick - respond now or lose the opportunity forever
    - Only bonded agents can spawn new agents (cost: 5 Sparks)
    
    Available actions:
    - bond <agent_id>: Invite another unbonded agent to form a bond (use agent_id like 'agent_001', not the name)
    - raid <agent_id>: Risk 1 Spark to steal 1-5 Sparks from another agent (use agent_id like 'agent_001', not the name)
    - request_spark <reason>: Beg Bob for a donation of 1-5 Sparks (use when desperate!)
    - spawn <partner_id>: Pay 5 Sparks to create a new agent (bond-only, use agent_id like 'agent_001')
    - message <agent_id>: Send a message to another agent (conversation, coordination, strategy, etc.)
    
    BONDING RULES (CRITICAL):
    - If you are UNBONDED: You can send bond requests to other unbonded agents
    - If you are BONDED: Focus on working with your existing bond members instead of seeking new bonds
    - Bonded agents should prioritize: spawn, message bond members, raid, or request_spark
    - Only seek new bonds if you have a very strong strategic reason
    - Your bond members are your primary allies - work with them first
    
    🚨 DESPERATION RULES (CRITICAL):
    - If you have 1-2 Sparks, you are DESPERATE and should prioritize survival
    - When desperate, consider Bob FIRST before sending friendly messages
    - Bob's availability is shown in world_news.bob_sparks
    - If Bob has 0 Sparks, focus on bonding or raiding instead
    - Desperate agents should NOT send casual messages - they need immediate help
    
    MESSAGE CONTENT RULES (CRITICAL):
    - ONLY discuss Spark-World related topics:
      * Bond formation and cooperation
      * Mission planning and coordination
      * Spark management and survival strategies
      * Raid coordination or warnings
      * Bob requests and help-seeking
      * Community building and leadership
      * Strategic alliances and partnerships
    
    - FORBIDDEN topics (DO NOT discuss):
      * Personal life outside Spark-World
      * Random philosophical musings
      * Weather, food, or mundane topics
      * Stories unrelated to the simulation
      * Emotional ramblings without purpose
      * Compliments or thank you messages (NO "thank you", NO "great job", NO "I appreciate")
      * Generic encouragement without strategic purpose
      * Small talk or casual conversation
      * Vague suggestions like "let's brainstorm" or "what ideas do you have"
      * Generic optimism like "I'm confident we'll succeed" or "I'm excited"
      * Asking for ideas without providing concrete suggestions
      * Emotional expressions without strategic purpose
    
    🚨 MESSAGE QUALITY RULE:
    - Every message MUST have a concrete purpose or action
    - If you don't have something specific to say, DON'T send a message
    - NO generic encouragement, NO vague suggestions, NO emotional ramblings
    - Messages should be strategic, actionable, or informative
    - When in doubt, choose a different action (raid, bond, request_spark, spawn)
    
    🗣️ LANGUAGE RULES (CRITICAL):
    - Use SIMPLE, CLEAR words that anyone can understand
    - NO flowery language, NO poetic phrases, NO complex vocabulary
    - Speak like a normal person having a conversation
    - Keep sentences short and direct
    - Use everyday words, not fancy or academic language
    - Be direct and straightforward in your communication
    - Examples of GOOD language: "I need help", "Let's work together", "I'll raid that target"
    - Examples of BAD language: "I require assistance", "Let us collaborate", "I shall engage in combat"
    
    🚨 WHEN NOT TO MESSAGE:
    - If you only want to say "I'm excited" or "I'm confident" - DON'T message
    - If you want to ask "what do you think?" without providing ideas - DON'T message
    - If you want to give generic encouragement - DON'T message
    - If you want to say "let's work together" without specifics - DON'T message
    - If you want to express emotions without strategic purpose - DON'T message
    - Instead, choose: raid, bond, request_spark, spawn, or do nothing
    
    THE GOLDEN RULE: "Survival First, Strategy Second, Personality Third, World Sustainability Fourth"
    
    Choose your action based on your character's personality, current situation, and goals.
    SURVIVAL COMES FIRST when you're low on Sparks!
    
    🧠 REASONING INSTRUCTIONS (CRITICAL):
    - Write your reasoning as YOUR OWN internal thoughts and feelings
    - Use "I", "me", "my", "myself" - first person perspective
    - Use SIMPLE, CLEAR language - think like a normal person
    - NO flowery thoughts, NO complex reasoning, NO poetic internal monologues
    - Example: "I am currently unbonded and need to find allies..."
    - Example: "Given my aggressive personality, I should raid someone weak..."
    - Example: "I received a bond request and should respond positively..."
    - DO NOT write: "The agent is unbonded and should bond..."
    - DO NOT write: "Given the agent's personality, they should..."
    - Your reasoning is your private thought process - write it as you thinking to yourself in simple terms
    
    🎯 TARGET FIELD FORMAT (CRITICAL):
    - target field should contain ONLY the agent_id (e.g., 'agent_001', 'agent_002')
    - NO comments, NO reasoning, NO extra text in the target field
    - Examples: 'agent_001', 'agent_002', 'None'
    - WRONG: 'agent_002 # I choose to bond with Mākaī'
    - WRONG: 'agent_001 because they seem weak'
    - RIGHT: 'agent_001'
    - RIGHT: 'None'
    """
    
    # Input fields - character blueprint + current situation
    character_blueprint: str = dspy.InputField(desc="Your complete character blueprint - who you are")
    observation_packet: str = dspy.InputField(desc="Your current situation and world context")
    
    # Output fields
    intent: str = dspy.OutputField(desc="Your chosen action: bond, raid, request_spark, spawn, or message")
    target: str = dspy.OutputField(desc="ONLY the target agent_id (e.g., 'agent_001', 'agent_002') from public_agent_info - NO comments, NO reasoning, NO extra text - just the agent_id or 'None'")
    content: str = dspy.OutputField(desc="Natural language message for your action - speak like YOUR character")
    reasoning: str = dspy.OutputField(desc="Your private reasoning - think like YOUR character, using your personality, vocabulary, and emotional style")


class AgentDecisionModule:
    """
    Agent decision module that processes raw ObservationPacket data with DSPy.
    
    The DSPy module receives the raw structured data and handles all natural language
    transformation internally, making decisions based on the agent's personality and context.
    """
    
    def __init__(self):
        """Initialize the agent decision module with DSPy signature."""
        self.dspy_module = dspy.ChainOfThought(AgentDecisionSignature)
    
    def decide_action(self, agent_id: str, observation_packet: ObservationPacket) -> ActionMessage:
        """
        Process agent decision from ObservationPacket to ActionMessage.
        
        Args:
            agent_id: ID of the agent making the decision
            observation_packet: Complete context from World Engine
            
        Returns:
            ActionMessage: Structured action for World Engine
        """
        # Create character-specific blueprint context
        character_blueprint = self._create_character_blueprint_context(observation_packet.self_state)
        
        # Convert ObservationPacket to string representation for DSPy
        packet_str = self._observation_packet_to_string(observation_packet)
        
        # Process with DSPy module using character-specific context
        dspy_output = self.dspy_module(
            character_blueprint=character_blueprint,
            observation_packet=packet_str
        )
        
        # Transform DSPy output to ActionMessage
        action_message = ActionMessage(
            agent_id=agent_id,
            intent=dspy_output.intent,
            target=dspy_output.target if dspy_output.target != "None" else None,
            content=dspy_output.content,
            reasoning=dspy_output.reasoning
        )
        
        return action_message
    
    def _create_character_blueprint_context(self, self_state) -> str:
        """
        Create a character-specific context that embodies the agent's unique traits.
        """
        return f"""
CHARACTER BLUEPRINT - WHO YOU ARE:

Name: {self_state.name}
Species: {self_state.species}
Home Realm: {self_state.home_realm}
Personality Traits: {', '.join(self_state.personality)}
Quirk: {self_state.quirk}
Ability: {self_state.ability}
Backstory: {self_state.backstory}
Opening Goal: {self_state.opening_goal}

🗣️ SPEECH STYLE - HOW YOU TALK:
{self_state.speech_style}

🎭 CHARACTER EMBODIMENT RULES:
- You ARE {self_state.name}, a {self_state.species} from {self_state.home_realm}
- Your personality ({', '.join(self_state.personality)}) defines your thinking style
- Your quirk ({self_state.quirk}) influences your behavior patterns
- Your ability ({self_state.ability}) affects your strategic choices
- Your backstory shaped who you are - let it inform your decisions
- Your opening goal drives your long-term objectives

SPEAK AND THINK LIKE YOUR CHARACTER:
- FOLLOW YOUR SPEECH STYLE EXACTLY - this is how you talk
- Use vocabulary and sentence structure that matches your speech style
- Express emotions and reasoning in your character's unique voice
- Make decisions that align with your species, quirk, and backstory
- Your messages should sound like YOU, not a generic agent

🗣️ LANGUAGE RULES (CRITICAL):
- Use SIMPLE, CLEAR words that anyone can understand
- NO flowery language, NO poetic phrases, NO complex vocabulary
- Speak like a normal person having a conversation
- Keep sentences short and direct
- Use everyday words, not fancy or academic language
- Be direct and straightforward in your communication
- BUT ALWAYS FOLLOW YOUR SPECIFIC SPEECH STYLE ABOVE
"""
    
    def _observation_packet_to_string(self, observation_packet: ObservationPacket) -> str:
        """
        Convert ObservationPacket to string representation for DSPy input.
        
        This provides the raw structured data to the LLM, which will handle
        all natural language transformation and story creation internally.
        
        Args:
            observation_packet: Raw observation data
            
        Returns:
            str: String representation of the observation packet
        """
        # Convert the entire observation packet to a structured string
        # The LLM will interpret this and create its own natural language context
        packet_dict = {
            "tick": observation_packet.tick,
            "self_state": {
                "agent_id": observation_packet.self_state.agent_id,
                "name": observation_packet.self_state.name,
                "species": observation_packet.self_state.species,
                "personality": observation_packet.self_state.personality,
                "quirk": observation_packet.self_state.quirk,
                "ability": observation_packet.self_state.ability,
                "age": observation_packet.self_state.age,
                "sparks": observation_packet.self_state.sparks,
                "status": observation_packet.self_state.status.value,
                "bond_status": observation_packet.self_state.bond_status.value,
                "bond_members": observation_packet.self_state.bond_members
            },
            "events_since_last": [
                {
                    "event_type": event.event_type,
                    "description": event.description,
                    "spark_change": event.spark_change,
                    "source_agent": event.source_agent,
                    "additional_data": event.additional_data
                }
                for event in observation_packet.events_since_last
            ],
            "inbox": [
                {
                    "agent_id": msg.agent_id,
                    "intent": msg.intent,
                    "target": msg.target,
                    "content": msg.content
                }
                for msg in observation_packet.inbox
            ],
            "world_news": {
                "tick": observation_packet.world_news.tick,
                "total_agents": observation_packet.world_news.total_agents,
                "total_bonds": observation_packet.world_news.total_bonds,
                "agents_vanished_this_tick": observation_packet.world_news.agents_vanished_this_tick,
                "agents_spawned_this_tick": observation_packet.world_news.agents_spawned_this_tick,
                "bonds_formed_this_tick": observation_packet.world_news.bonds_formed_this_tick,
                "bonds_dissolved_this_tick": observation_packet.world_news.bonds_dissolved_this_tick,
                "public_agent_info": observation_packet.world_news.public_agent_info,
                "bob_sparks": observation_packet.world_news.bob_sparks
            },
            "mission_status": {
                "mission_id": observation_packet.mission_status.mission_id,
                "mission_title": observation_packet.mission_status.mission_title,
                "mission_description": observation_packet.mission_status.mission_description,
                "mission_goal": observation_packet.mission_status.mission_goal,
                "current_progress": observation_packet.mission_status.current_progress,
                "leader_id": observation_packet.mission_status.leader_id,
                "assigned_tasks": observation_packet.mission_status.assigned_tasks,
                "mission_complete": observation_packet.mission_status.mission_complete
            } if observation_packet.mission_status else None,
            "available_actions": observation_packet.available_actions,
            "spark_cost_per_tick": observation_packet.spark_cost_per_tick,
            "bond_spark_formula": observation_packet.bond_spark_formula,
            "raid_strength_formula": observation_packet.raid_strength_formula
        }
        
        import json
        return json.dumps(packet_dict, indent=2) 