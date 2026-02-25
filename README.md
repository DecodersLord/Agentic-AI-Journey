# 🤖 Agentic AI Journey

My hands-on journey into **Agentic AI** — building real agents from scratch, one phase at a time.

📖 **Blog Series:** [AI Agent VS Chatbot (Phase 1)](https://dev.to/decoders_lord/ai-agent-vs-chatbot-156i)
� **Status:** Phase 2 complete — first working agent built

---

## Phase 1 — Mental Model ✅

Built a solid mental model of what AI agents actually are and how they work. Documented everything in detailed notes.

**Key concepts covered:**
- Chatbots vs AI Agents — why LLMs changed everything
- Agent Lifecycle — Observe → Think → Plan → Act → Repeat
- Three layers of an agent — Reasoning (LLM), Action (Tools), Control (Orchestrator)

📄 [Read the notes](Phase%20-%201%20-%20Mental%20Model/notes.md)

---

## Phase 2 — Tool-Using Agents ✅

Built a **Code Analyzer Agent** from scratch — no frameworks, just Python + Google Gemini's function calling API.

**What the agent does:**
- Takes code input from the user
- Gemini decides whether to use a tool or respond directly
- Calls a local `analyze_code` tool (counts lines, functions, classes)
- Returns the analysis result

**What I learned building it:**
- LLMs are smart enough to skip your tools — system instructions guide tool usage
- Function declarations are contracts between your code and the LLM
- Dynamic tool dispatch (`available_tools[name]`) scales to multi-tool agents
- Every API call costs quota — design your agent loop to minimize round-trips

### Run it yourself

```bash
cd "Phase - 2 - HuggingFace Learning to build agents/Dummy Agent v1"
pip install -r requirements.txt
echo GEMINI_AI_API=your_api_key_here > .env
python main.py
```

### Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Google Gemini (`google-genai`) |
| Language | Python 3.10+ |
| Config | `python-dotenv` |

📁 [Explore the code](Phase%20-%202%20-%20HuggingFace%20Learning%20to%20build%20agents/Dummy%20Agent%20v1/)

---
