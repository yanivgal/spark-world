# 🌌 Spark‑World

*Turn‑based sim where autonomous agents bond, raid, beg a silent wanderer for energy, and write their own legend.*

---

## What is Spark‑World?

Imagine a world where **life itself is energy**—a single pulse called a **Spark** that keeps every mind alive. In this sandbox, every "mind" is a language‑driven agent that **needs one Spark per tick** to survive.

**Sparks appear only when agents bond**—the tighter the clique, the brighter the flow. Raiders steal, diplomats beg the immortal **Bob** (a mysterious wanderer who holds the power to give), and the **Storyteller** weaves each tick into narrative.

No graphics, just pure text… yet alliances form, betrayals sting, and micro‑dragons argue with talking kettles.

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
pip install -r requirements.txt   # langgraph, dspy, sqlmodel, streamlit…
python main.py                    # launches WorldEngine
streamlit run app.py              # (optional UI)
```

---

## Dive Deeper

* **[🌌 The Complete Guide](sparkworld.md)** – Everything about how Spark‑World works, from the 6-stage tick system to advanced strategies
* **[🤖 How Agents Think](sparkworld_how_the_pieces_talk.md)** – The technical details of how agents communicate and make decisions
* **[📖 The Storyteller](storyteller.md)** – How the narrative emerges from raw events
* **[🧩 Mission Meetings](mission_meeting.md)** – How bonded agents collaborate on shared goals
* **[👤 Bob's Story](bob.md)** – The mysterious wanderer who holds the power to give life

---

**Implementation Note:** This is a conceptual design. The actual implementation will include:
- Independent LLM agents with unique personalities
- A World Engine to coordinate the 6-stage tick process
- A Storyteller to convert events into narrative
- Mission generation and management systems
- Bob's renewable Spark economy
