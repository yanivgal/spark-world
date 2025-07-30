# 🌌 Spark‑World

*Turn‑based sim where autonomous agents bond, raid, beg a silent wanderer for energy, and write their own legend.*

---

## What is Spark‑World?

Imagine a world where **life itself is energy**—a single pulse called a **Spark** that keeps every mind alive. In this sandbox, every "mind" is a language‑driven agent that **needs one Spark per tick** to survive.

**Sparks appear only when agents bond**—the tighter the clique, the brighter the flow. Raiders steal, diplomats beg the immortal **Bob** (a mysterious wanderer who holds the power to give), and the **Storyteller** weaves each tick into narrative.

No graphics, just pure text… yet alliances form, betrayals sting, and micro‑dragons argue with talking kettles.

---

## The Characters of Spark‑World

**Bob** – The mysterious wanderer who holds the power to give life. When agents are desperate, they can beg Bob for Sparks, but his generosity is finite and unpredictable.

**The Storyteller** – The voice that transforms raw events into compelling narrative. Every Storyteller has their own personality—some tell epic tales like ancient bards, others whisper gentle stories of friendship and growth.

**The Shard‑Sower** – An extradimensional artisan who forges new minds. Every time you start a new world, the Shard‑Sower creates a unique cast of agents, each with their own personality, backstory, and special abilities. No two worlds will ever have the same characters.

---

## Why should I care?

* **Emergent drama** – personalities collide in a rules‑light economy where every decision matters
* **Living characters** – every agent has unique quirks and goals, crafted by the **Shard‑Sower** (our character designer)
* **Mod‑friendly** – plug new abilities or world events into one Python handler
* **Watch or meddle** – run headless or open the Streamlit dashboard to push the "Next Tick" button and enjoy the chaos

---

## Quick start

```bash
git clone https://github.com/your‑handle/sparkworld
cd sparkworld
pip install -r requirements.txt   # dspy-ai, openai, dataclasses-json, typing-extensions

# Set up your OpenAI API key
cp template.env .env
# Edit .env and add your OpenAI API key: OPENAI_API_KEY=your_key_here

# Run the interactive simulation
python world/interactive_simulation.py
```

---

## Dive Deeper

* **[🌌 The Complete Guide](sparkworld.md)** – Everything about how Spark‑World works, from the 6-stage tick system to advanced strategies
* **[🤖 How Agents Think](sparkworld_how_the_pieces_talk.md)** – The technical details of how agents communicate and make decisions
* **[📖 The Storyteller](storyteller.md)** – How the narrative emerges from raw events
* **[🧩 Mission Meetings](mission_meeting.md)** – How bonded agents collaborate on shared goals
* **[👤 Bob's Story](bob.md)** – The mysterious wanderer who holds the power to give life
* **[🌱 Shard‑Sower](shard_sower.md)** – The extradimensional artisan who forges new minds
* **[🚀 Vibe Coding Experience](VIBE_CODING_EXPERIENCE.md)** – How we built Spark-World using AI-assisted programming and what we learned

---

**Implementation Note:** This is a conceptual design. The actual implementation will include:
- Independent LLM agents with unique personalities
- A World Engine to coordinate the 6-stage tick process
- A Storyteller to convert events into narrative
- Mission generation and management systems
- Bob's renewable Spark economy
