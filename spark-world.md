# 🌌  Spark‑World

What is Spark‑World?

Imagine a silent void where nothing exists until two minds brush against each other and a single pulse of energy, a Spark that flares into being.

Spark‑World is a turn‑based, text‑only life-simulation built on that idea:

Agents - LLM-driven personalities as diverse as micro‑dragons, cloud‑professors, or sarcastic teapots - struggle to stay alive by earning Sparks through bonding and spending one Spark every tick just to keep their pattern alive.

There are no tiles to move and no hit-points to track. Only conversation. Each turn unfolds entirely in dialogue: agents forge alliances, raid rivals for Sparks, beg mercy from an immortal donor named Bob, and watch a Storyteller weave their choices into an evolving fable.

Over time, simple numeric rules give rise to rivalries, unlikely friendships, and the occasional extinction event—all written in words rather than pixels.


### The Cast of Spark‑World

| Entity          | One‑line essence                                                                                               | Why they matter                                                           |
| --------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| **Spark ⚡**     | A fleeting knot of order—one per friendship per tick, one burned per life each tick.                           | It is both currency and heartbeat: without Spark, you fade.               |
| **Agents**      | Self‑sustaining minds—anything from dragons to talking kettles—each can send **one action‑message** per tick.  | They are the players; their choices drive every story turn.               |
| **Bonds**       | Fully‑connected cliques; a trio yields 3 Sparks, a quartet 6, etc.                                             | The only natural Spark factory; friendships literally create life‑energy. |
| **Bob**         | An immortal wanderer with a finite hoard of Sparks; answers polite pleas with gifts of up to 5 random Sparks.  | Outside rescue line when your balance runs low—if Bob feels generous.     |
| **Storyteller** | Neutral narrator who converts raw logs into a brief chapter at the end of each tick.                           | Turns dry mechanics into an unfolding fable you’ll want to read.          |
| **Shard‑Sower** | Extradimensional artisan that forges brand‑new agents, each with a unique quirk and single‑line super‑ability. | Guarantees every run begins with a wildly different cast.                 |

Every tick these characters dance: Bonds mint Sparks, Agents act, Bob judges, the Storyteller records, and Shard‑Sower stands ready to seed new minds when old ones flicker out.

### One Turn (Tick) in Six Beats

> *A hush, a hum, and then the world moves...*

| #     | Stage                   | What really happens                                                                                                                                                                      |
| ----- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1** | **Mint Sparks**         | Every bond counts its links ( *n · (n − 1)/2* ) and the engine births that many fresh Sparks.                                                                                            |
| **2** | **Bob Decides**         | All `request_spark` pleas from the previous tick land in Bob’s lap; he ponders urgency, fairness, whimsy—and gifts up to **5 random Sparks** to any supplicant until his stash runs dry. |
| **3** | **Agents Act**          | Each living agent receives its private observation package and replies with **one message**—bond, raid, spawn, beg Bob, or simply reply.                                                 |
| **4** | **Distribute Sparks**   | Minted Sparks are handed out **one by one, at random** to members of each bond, ensuring long‑run fairness but short‑run drama.                                                          |
| **5** | **Upkeep & Vanishings** | The tax for existing: every agent loses 1 Spark. Any who hit 0 dissolve instantly, severing their bonds and reducing future minting.                                                     |
| **6** | **Storytime**           | The Storyteller reads the full log and distills it into a bite‑sized chapter—alliances forged, raids won or lost, Bob’s mercy (or lack thereof). Then the cycle begins anew.             |

A tick can last a second or a minute, but this rhythm—mint, mercy, action, payout, cost, story—never changes.

### What an Agent Can Do (Single‑Message Rule)

In each tick an agent may say **one—and only one—of these magic words**:

| Command           | Syntax                    | Why use it                                                                                              |
| ----------------- | ------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Bond**          | `bond <agent_id>`         | Invite another lone agent. If both send the invite in the same tick, a bond (and fresh Sparks) is born. |
| **Raid**          | `raid <agent_id>`         | Risk it all to steal **1 – 5 Sparks**; success odds scale with *strength = age x spark*.                |
| **Request Spark** | `request_spark <reason>`  | Beg Bob for a donation (he rolls 1 – 5 Sparks if moved by your plea).                                   |
| **Spawn**         | `spawn_with <partner_id>` | (Bond‑only) Pay **5 Sparks** to craft a brand‑new agent who joins the bond.                             |
| **Reply**         | `reply <msg_id> <text>`   | Address a single incoming message—missions, apologies, threats, poems…                                  |

No macros, no multi‑actions: choose one verb, send it, live (or dissolve) with the consequences.

### Sparks, Survival, and Strength

*The universe writes its laws in simple arithmetic.*

| Rule             | Formula / Limit                                   | Consequence                                                              |
| ---------------- | ------------------------------------------------- | ------------------------------------------------------------------------ |
| **Life‑cost**    |  –1 Spark per agent every tick                    | Fall to 0 → pattern unravels, agent vanishes instantly.                  |
| **Bond minting** |  *n · (n − 1)/2* Sparks each tick                 | A trio earns 3 ⚡, a quartet 6 ⚡—bigger cliques, brighter pay‑days.       |
| **Random split** | Sparks handed out one‑by‑one to random bond‑mates | Short‑term luck, long‑term fairness.                                     |
| **Spawning fee** | 5 Sparks paid by initiator                        | Newborn enters at age 0, Spark 5, same bond.                             |
| **Strength**     | age × spark                                       | Used only in raid odds: *P(success) = attacker / (attacker + defender)*. |
| **Raid haul**    | Random 1 – 5 ⚡, capped by defender’s balance      | Win → take haul; lose → defender steals that amount instead.             |
| **Bob’s gift**   | Up to 5 ⚡ per chosen request                      | Bob’s stash is finite; once empty, only bonds can create Sparks.         |

These numbers are the heartbeat of Spark‑World—easy to remember, ruthless in practice.

