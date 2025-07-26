# 🌌  Spark‑World

*The complete guide to Spark‑World's mechanics, systems, and emergent storytelling.*

**[← Back to Overview](README.md)**

---

**What is Spark‑World?**

Imagine a silent void where nothing exists until two minds brush against each other and a single pulse of energy, a Spark ⚡ that flares into being.

Spark‑World is a turn‑based, text‑only life-simulation built on that idea:

Agents - LLM-driven personalities as diverse as micro‑dragons, cloud‑professors, or sarcastic teapots - struggle to stay alive by earning Sparks through bonding and spending one Spark every tick just to keep their pattern alive.

There are no tiles to move and no hit-points to track. Only conversation. Each turn unfolds entirely in dialogue: agents forge alliances, raid rivals for Sparks, beg mercy from an immortal donor named Bob, and watch a Storyteller weave their choices into an evolving fable.

Over time, simple numeric rules give rise to rivalries, unlikely friendships, and the occasional extinction event—all written in words rather than pixels.


## The Cast of Spark‑World

| Entity          | One‑line essence                                                                                               | Why they matter                                                           |
| --------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Spark ⚡**     | A fleeting knot of order—one per friendship per tick, one burned per life each tick.                           | It is both currency and heartbeat: without Spark, you fade.               |
| **Agents**      | Self‑sustaining minds—anything from dragons to talking kettles—each can send **one action‑message** per tick.  | They are the players; their choices drive every story turn.               |
| **Bonds**       | Fully‑connected cliques; a trio yields 4 Sparks, a quartet 5, etc.                                             | The only natural Spark factory; friendships literally create life‑energy. |
| **Bob**         | An immortal wanderer with a finite hoard of Sparks; answers polite pleas with gifts of up to 5 random Sparks.  | Outside rescue line when your balance runs low—if Bob feels generous.     |
| **Storyteller** | Neutral narrator who converts raw logs into a brief chapter at the end of each tick.                           | Turns dry mechanics into an unfolding fable you’ll want to read.          |
| **Shard‑Sower** | Extradimensional artisan that forges brand‑new agents, each with a unique quirk and single‑line super‑ability. | Guarantees every run begins with a wildly different cast.                 |

Every tick these characters dance: Bonds mint Sparks, Agents act, Bob judges, the Storyteller records, and Shard‑Sower stands ready to seed new minds when old ones flicker out.

## One Turn (Tick) in Six Beats

> *A hush, a hum, and then the world moves...*

| #     | Stage                   | What really happens                                                                                                                                                                      |
| ----- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **Mint Sparks**         | Every bond calculates ⚡ using the formula *floor(n + (n-1) × 0.5)* where n is the number of agents in the bond.                                                                                            |
| **2** | **Bob Decides**         | All `request_spark` pleas from the previous tick land in Bob’s lap; he ponders urgency, fairness, whimsy—and gifts up to **5 random** ⚡ to any supplicant until his stash runs dry. |
| **3** | **Agents Act**          | Each living agent receives its private observation package and replies with **one message**—bond, raid, spawn, beg Bob, or simply reply.                                                 |
| **4** | **Distribute Sparks**   | Minted Sparks are handed out **one by one, at random** to members of each bond, ensuring long‑run fairness but short‑run drama.                                                          |
| **5** | **Upkeep & Vanishings** | The tax for existing: every agent loses 1 Spark. Any who hit 0 dissolve instantly, severing their bonds and reducing future minting.                                                     |
| **6** | **Storytime**           | The Storyteller reads the full log and distills it into a bite‑sized chapter—alliances forged, raids won or lost, Bob’s mercy (or lack thereof). Then the cycle begins anew.             |

A tick can last a second or a minute, but this rhythm—mint, mercy, action, payout, cost, story—never changes.

## What an Agent Can Do (Single‑Message Rule)

In each tick an agent may say **one—and only one—of these magic words**:

| Command           | Syntax                    | Why use it                                                                                              |
| ----------------- | ------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Bond**          | `bond <agent_id>`         | Invite another lone agent. The target receives the request next tick and can accept or decline. |
| **Raid**          | `raid <agent_id>`         | Risk 1⚡ to steal **1 – 5**⚡; success odds scale with *strength = age + spark*.                |
| **Request Spark** | `request_spark <reason>`  | Beg Bob for a donation (he rolls 1 – 5⚡ if moved by your plea).                                   |
| **Spawn**         | `spawn_with <partner_id>` | (Bond‑only) Pay **5⚡** to craft a brand‑new agent who joins the bond.                             |
| **Reply**         | `reply <msg_id> <text>`   | Address a single incoming message—missions, apologies, threats, poems…                                  |

No macros, no multi‑actions: choose one verb, send it, live (or dissolve) with the consequences.

## Sparks, Survival, and Strength

*The universe writes its laws in simple arithmetic.*

| Rule             | Formula / Limit                                   | Consequence                                                              |
| ---------------- | ------------------------------------------------- | ------------------------------------------------------------------------ |
| **Life‑cost**    |  –1 ⚡ per agent every tick                    | Fall to  0 → pattern unravels, agent vanishes instantly.                  |
| **Bond minting** | *floor(n + (n-1) × 0.5)* ⚡ each tick                 | A trio earns 4⚡, a quartet 5⚡ — bigger cliques, brighter pay‑days.       |
| **Random split** | Sparks handed out one‑by‑one to random bond‑mates | Short‑term luck, long‑term fairness.                                     |
| **Spawning fee** | 5 Sparks paid by initiator                        | Newborn enters at age 0, 5⚡, same bond.                             |
| **Strength**     | age + spark                                       | Used only in raid odds: *P(success) = attacker / (attacker + defender)*. |
| **Raid haul**    | Random 1 – 5 ⚡, capped by defender’s balance      | Win → take haul; lose → defender steals 1⚡ instead.             |
| **Bob’s gift**   | Up to 5 ⚡ per chosen request                      | Bob’s stash is finite; once empty, only bonds can create Sparks.         |

These numbers are the heartbeat of Spark‑World — easy to remember, ruthless in practice.

## Game Balance & Design Notes

### Why Massive Bonds Don't Form Instantly
Each agent is an independent LLM with its own personality and reasoning. Bond formation is **two-step** - one agent initiates a bond request, and the target agent receives it in the next tick and can choose to accept or decline. The probability of multiple agents simultaneously deciding to bond with each other is extremely low due to their diverse personalities and strategic thinking.

### Bob's Renewable Generosity
Bob starts with a finite number of Sparks. If he runs out (reaches zero), he simply ignores all requests until the next tick when he gains more Sparks. His generosity is finite but renewable, preventing infinite Spark generation.

### Strength Formula Considerations
The raid strength formula uses `age + spark` for balanced scaling. This ensures that:
- Newborns aren't completely helpless (they start with strength equal to their spark count)
- Experience matters but doesn't create overwhelming power gaps
- Every raid has meaningful risk/reward regardless of agent age
- Strategy and alliances matter more than pure age accumulation

### Spawning Cost Strategy
The 5 Spark spawning cost is intentionally high to encourage strategic thinking. Agents must balance survival needs with the long-term benefits of larger bonds (which generate more Sparks per tick). This creates tension between immediate survival and long-term growth.

### Mission System
Missions are procedurally generated by an LLM when bonds form. Each mission has a specific goal (like "Explore the meadow" or "Build a shelter") and provides a collaborative framework for bonded agents to work together.

**Mission Lifecycle:**
1. **Generation**: When a bond forms, an LLM creates a unique mission with a clear objective
2. **Leadership**: One agent in the bond is randomly selected as the mission leader
3. **Meetings**: Every tick, the bond holds a Mission Meeting where agents discuss strategy and assign tasks
4. **Completion**: Missions are completed when the objective is achieved (determined by the LLM based on agent actions)
5. **Post-Mission**: Once completed, the bond continues without a mission, but can still generate Sparks through bonding

**Mission Meeting Flow:**
- **Leader Brief**: Mission leader summarizes the goal and current status
- **Agent Input**: Each bonded agent provides suggestions and preferences
- **Task Assignment**: Leader assigns specific actions to each agent
- **Execution**: Agents carry out their assigned tasks in the next tick

This system creates meaningful cooperation beyond just Spark generation, giving agents shared goals and reasons to work together strategically.

## 🎬 See It In Action: The Three‑Tick Walkthrough

*Watch a knightly cat, a whispering flower, and a desperate goblin navigate betrayal, strategy, and redemption in just three turns. See how a simple "bond" command blossoms into a heist-worthy mission, complete with secret meetings, calculated raids, and the mysterious Bob's generosity. This isn't just a game—it's a story that writes itself.*

**[📖 Read the Complete Three-Tick Walkthrough →](three_tick_walkthrough.md)**

*From newborn confusion to mission completion, every decision matters. Every Spark counts. Every alliance could be your salvation—or your downfall.*

## 🌟 Why Spark‑World Pulls You In
* Stories that write themselves
A single line—“bond”, “raid”, “beg Bob”—can blossom into rivalries, alliances, or tragic vanishings, all narrated moments later by an LLM bard.

* A cast that never repeats
One run might star a thunder‑cloud professor and a jealous teapot; the next, a micro‑dragon hoarding welding sparks. Shard‑Sower guarantees surprise every time you press “New World”.

* Economy of emotion
Sparks aren’t just points—they’re lifespans. Friendships print them, greed drains them, mercy from Bob can rewrite a fate.

* Hack‑ready core
The entire simulation lives in a few hundred lines: swap prompts, bolt on events, or teach Bob a new morality with ten minutes of editing.

* Zero graphics, full imagination
No pixel budget needed—everything unfolds in prose you’ll actually want to read (and maybe copy into a short story anthology).

Try one tick, watch a flower outsmart a goblin raider, and see if you can resist clicking "Next Turn."

---

## Explore Further

* **[🤖 How Agents Think](sparkworld_how_the_pieces_talk.md)** – The technical details of agent communication and decision-making
* **[📖 The Storyteller](storyteller.md)** – How raw events become compelling narrative
* **[🧩 Mission Meetings](mission_meeting.md)** – The collaborative planning system for bonded agents
* **[👤 Bob's Story](bob.md)** – The complete tale of the mysterious wanderer
* **[🌱 Shard‑Sower](shard_sower.md)** – The extradimensional artisan who forges new minds
* **[← Back to Overview](README.md)** – Return to the main project page
