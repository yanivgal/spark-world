from dataclasses import dataclass


@dataclass
class RaidResult:
    """
    Outcome of a raid action in Spark-World.
    
    Raid mechanics:
    - Attacker risks 1 spark to attempt raid
    - Success probability: P(success) = attacker_strength / (attacker_strength + defender_strength)
    - Success: Attacker steals 1-5 sparks (capped by defender's balance)
    - Failure: Defender steals 1 spark from attacker
    
    Attributes:
        attacker_id: ID of the agent who initiated the raid
        defender_id: ID of the agent who was raided
        success: Whether the raid succeeded
        attacker_strength: Attacker's strength (age + sparks)
        defender_strength: Defender's strength (age + sparks)
        sparks_transferred: How many sparks changed hands (positive = attacker gained, negative = attacker lost)
        reasoning: Why the raid succeeded or failed
        attacker_spark_cost: Always 1 (the cost to attempt raid)
    """
    attacker_id: str
    defender_id: str
    success: bool
    attacker_strength: int
    defender_strength: int
    sparks_transferred: int  # Positive = attacker gained, negative = attacker lost
    reasoning: str  # Why the raid succeeded or failed
    attacker_spark_cost: int = 1  # Always 1 spark to attempt raid


@dataclass
class SparkTransaction:
    """
    A spark transfer between entities in Spark-World.
    
    Used for raids, bond spark generation, Bob donations, spawning costs,
    and upkeep costs. Tracks all spark movements in the simulation.
    
    Attributes:
        from_entity: Source entity (agent_id, "bob", "bond", "upkeep")
        to_entity: Target entity (agent_id, "bob", "bond", "upkeep")
        amount: Number of sparks transferred (positive)
        transaction_type: Type of transaction (raid, bond_minting, bob_donation, spawn_cost, upkeep)
        reason: Why this transaction occurred
        tick: When this transaction occurred
    """
    from_entity: str
    to_entity: str
    amount: int
    transaction_type: str  # "raid", "bond_minting", "bob_donation", "spawn_cost", "upkeep"
    reason: str
    tick: int


@dataclass
class BobResponse:
    """
    Bob's response to a spark request from an agent.
    
    Bob mechanics:
    - Bob has finite sparks that regenerate per tick
    - Bob grants 1-5 sparks per request (random)
    - Bob's generosity is finite but renewable
    - Bob ignores requests when he has 0 sparks
    - Bob's decision is based on urgency, fairness, whimsy, worthiness
    
    Attributes:
        requesting_agent_id: ID of the agent who requested sparks
        request_content: The original request message/reason
        sparks_granted: Number of sparks granted (0-5, 0 if ignored)
        bob_sparks_before: Bob's spark count before this response
        bob_sparks_after: Bob's spark count after this response
        reasoning: Why Bob granted or denied the request
        tick: When this response was given
    """
    requesting_agent_id: str
    request_content: str
    sparks_granted: int  # 0-5, or 0 if Bob ignored request
    bob_sparks_before: int
    bob_sparks_after: int
    reasoning: str  # Why Bob granted or denied
    tick: int 