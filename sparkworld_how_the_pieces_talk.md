## How the Pieces Talk — A Plain‑Language Tour

**Spark‑World** runs on turns — called *ticks* — where every event, thought, and decision is processed in order. Each tick is a heartbeat of the world. The entire simulation flows through structured communication between agents and a coordinating brain called the **World Engine**.

---

### 1. Observation Packets — What Agents See

Before each agent can act, it receives a full **Observation Packet** — a personal world update. Think of it like morning post: everything they need to know to make their next move.

Each packet includes:

- `tick`: current tick number.
- `self_state`: current Spark count, age, bond status, leadership, etc.
- `events_since_last`: what happened to you since your last action (e.g., Spark loss, raid result, bond success/failure).
- `inbox`: direct messages from other agents.
- `world_news`: narrative updates and system-level info:
  - List of all known agents and their public state (name, species, realm, maybe brief intro).
  - New agents that spawned this tick.
  - Agents that disappeared.
  - Bond formations or dissolutions.
  - Rare global changes (e.g., “a strange fog covered the northern reach…”).

> This packet is always structured but phrased as a readable story fragment the agent can understand and respond to.

---

### 2. Agent Responses — Thoughtful, Structured, and Logged

Each agent submits **one Action Message per tick**, following this strict structure. **Note:** Bond requests are two-step - the target agent receives the request in the next tick and can choose to accept or decline.

```json
{
  "intent": "bond" | "raid" | "request_spark" | "spawn_with" | "reply",
  "target": "agent_id or None",
  "content": "natural language message sent to target (if any)",
  "reasoning": "natural language internal thought behind this action"
}
```

- `intent` defines what the agent is trying to do.
- `target` (if any) is who the message is for.
- `content` is what the agent says aloud or sends.
- `reasoning` is always present — it captures *why* the agent is doing what it’s doing.

⚠️ Only `intent`, `target`, and `content` are visible to other agents.\
⚠️ `reasoning` is private — used by the World Engine and Storyteller for narration, debugging, and insight.

---

### 3. The World Engine — Router, Referee, and Clock

The **World Engine** is the central orchestrator. It is not an agent. It doesn’t think like them. It just runs the rules.

> You can imagine it as a single Python class:

```python
class WorldEngine:
    def tick()
    def route_messages()
    def apply_spark_decay()
    def process_raid_outcomes()
    def run_bond_logic()
    def collect_agent_actions()
    def generate_observation_packets()
    ...
```

What it does every tick:

- Delivers Observation Packets to all agents.
- Collects Agent Responses with actions and reasoning.
- Routes Messages to the proper inboxes (e.g., Blossom gets Serpons’ bond request).
- Executes All Game Logic:
  - Calculates Spark drain and minting.
  - Processes raid outcomes.
  - Handles Bob donation logic.
  - Forms or breaks bonds.
  - Spawns new agents if requested.
- Saves All Events for later replay and Storyteller use.
- Passes Everything to the Storyteller.

> Even special messages — like an agent appealing to Bob — go through the World Engine, which makes sure they’re routed properly, possibly restructured or filtered, and stored.

---

### 4. Storyteller — The Eye Behind the Curtain

Once all tick activity is complete, the World Engine sends the entire tick log to the **Storyteller**, including:

- All public events and private reasoning.
- All messages exchanged.
- Agent disappearances, raids, bond changes, outcomes.
- Environmental notes (if applicable).

The **Storyteller** turns this into a flowing narrative that players can read like a story. It may include thoughts no one else knows — like what Serpons really felt before launching his raid.

> This is the soul of Spark‑World’s emergent storytelling.

