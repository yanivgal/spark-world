# 🌌 Spark‑World

*Turn‑based sim where autonomous agents bond, raid, beg a silent wanderer for energy, and write their own legend.*

---

## What is Spark‑World?
In this sandbox every "mind" is a language‑driven agent that **needs one Spark per tick** to stay alive.  
Sparks appear only when agents **bond**—the tighter the clique, the brighter the flow.  
Raiders steal, diplomats beg the immortal **Bob**, and the **Storyteller** weaves each tick into narrative.  
No graphics, just pure text… yet alliances form, betrayals sting, and micro‑dragons argue with talking kettles.

---

## Why should I care?

* **Emergent drama** – personalities collide in a rules‑light economy.  
* **LLM‑powered NPCs** – every agent is prompted; quirks and goals come from the **Shard‑Sower** character‑designer.  
* **Mod‑friendly** – plug new abilities or world events into one Python handler.  
* **Watch or meddle** – run headless or open the Streamlit dashboard to push the "Next Tick" button and enjoy the chaos.

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

**Implementation Note:** This is a conceptual design. The actual implementation will include:
- Independent LLM agents with unique personalities
- A World Engine to coordinate the 6-stage tick process
- A Storyteller to convert events into narrative
- Mission generation and management systems
- Bob's renewable Spark economy
