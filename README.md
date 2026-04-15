# Travel Agent PoC — Google AI Hackathon

![Travel Planner](assets/travel-planner-hakaton-bp.png)

> Multi-agent travel planner built with **Google ADK**, **Vertex AI RAG**, **Gemini 2.5 Flash**, and the **A2A protocol**.

A user sees a photo of Barcelona on Instagram, pastes the image into the agent, and gets back a complete travel proposal: flight, hotel, day-by-day itinerary, and budget — all in one go.

---

## How it works

```
User sends image/text
        │
        ▼
┌─────────────────────────────────────────────────┐
│  travel_planner  (root LlmAgent)                │
│  • Identifies destination from image (Gemini)   │
│  • Smart interview — asks only what it needs    │
│  • Transfers to ResearchPipeline when ready     │
└──────────────┬──────────────────────────────────┘
               │  transfer_to_agent
               ▼
┌─────────────────────────────────────────────────┐
│  ResearchPipeline  (SequentialAgent)            │
│                                                 │
│  1. TravelKnowledgeAgent  ──→  Vertex AI RAG    │
│                                                 │
│  2. ParallelBookingAgent                        │
│     ├── HotelSearchAgent  ──→  Trivago MCP      │
│     └── FlightSearchAgent ──→  Google Search    │
│                                                 │
│  3. TravelAdvisorAgent    ──→  Synthesizer      │
└──────────────┬──────────────────────────────────┘
               │
               ▼
     ONE unified proposal:
     flight + hotel + itinerary + budget + booking links
```

### Agent breakdown

| Agent | Model | Tools | Output |
|-------|-------|-------|--------|
| `travel_planner` | `MODEL_ROOT` | `recommend_destinations` (FunctionTool) | Conversational root |
| `TravelKnowledgeAgent` | `MODEL_KNOWLEDGE` | Vertex AI RAG search | `travel_knowledge` |
| `HotelSearchAgent` | `MODEL_HOTELS` | Trivago MCP (StreamableHTTP) | `hotel_results` |
| `FlightSearchAgent` | `MODEL_FLIGHTS` | Google Search (Gemini Grounding) | `flight_results` |
| `TravelAdvisorAgent` | `MODEL_ADVISOR` | None (synthesizer) | Final proposal |

Each agent uses its own model (configurable via env vars) because Vertex AI does not allow mixing `google_search` with `FunctionTool` on the same agent.

---

## Project structure

```
.
├── travel_rag_agent/          # Main agent — production (Cloud Run + A2A)
│   ├── agent.py               # Multi-agent composition
│   ├── a2a_server.py          # A2A server (port 8001)
│   ├── requirements.txt
│   ├── agents/
│   │   ├── models.py          # Per-agent model selection (env vars)
│   │   ├── travel_knowledge.py
│   │   ├── hotel_search.py
│   │   ├── flight_search.py
│   │   └── travel_advisor.py
│   ├── skills/                # Agent behaviour as editable Markdown
│   │   ├── base.py            # Frontmatter loader
│   │   ├── root.md
│   │   ├── knowledge.md
│   │   ├── hotels.md
│   │   ├── flights.md
│   │   └── advisor.md
│   └── tools/
│       └── destinations.py
│
├── rag_ingestion_agent/       # Offline — populates Vertex AI RAG
│   ├── agent.py               # "Add Barcelona and Rome"
│   ├── data/
│   │   ├── schema.py          # TravelChunk (Pydantic)
│   │   ├── wikivoyage.py      # MediaWiki API fetcher
│   │   └── chunker.py         # Recursive text splitter (500 chars)
│   ├── pipeline/
│   │   └── ingest.py
│   └── tools/
│       └── wikivoyage_tool.py
│
└── a2a_client_example/        # Demo: social media bot consuming the planner via A2A
    └── agent.py
```

---

## Skills system

Agent behaviour lives in Markdown files with YAML frontmatter — editable without touching Python:

```markdown
---
name: Travel Advisor Senior
description: Synthesises research into ONE proposal
agent: TravelAdvisorAgent
version: "1.0"
---

(Agent instruction is the body of this file)
```

---

## RAG knowledge base

| | |
|-|-|
| Backend | Vertex AI RAG Engine (managed) |
| Region | `europe-west1` |
| Destinations | 27 (global) |
| Embedding model | `text-embedding-004` (768 dims) |
| Source | Wikivoyage API |

**Covered destinations** — Europe: Paris, Barcelona, Rome, Amsterdam, Prague, Lisbon, Istanbul, Dubrovnik, Santorini, Edinburgh · Asia: Tokyo, Bangkok, Bali, Kyoto, Seoul, Hanoi, Singapore · Americas: New York City, Buenos Aires, Mexico City, Rio de Janeiro, Havana · Africa/Middle East: Marrakech, Cape Town, Nairobi · Oceania: Sydney, Queenstown

---

## A2A Protocol

The travel planner is exposed as an A2A server so any external agent can consume it:

```python
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

travel_planner = RemoteA2aAgent(
    name="travel_planner",
    agent_card="http://host:8001/.well-known/agent-card.json",
)
```

Agent Card published at `/.well-known/agent-card.json`:
- **Skills**: Travel Planning
- **Input modes**: `text/plain`, `image/*`
- **Protocol**: JSON-RPC v0.3.0

---

## Session Memory

Conversations persist in a dedicated Vertex AI RAG corpus so the agent remembers past trips across sessions.

```bash
adk web --memory_service_uri "rag://7991637538768945152" .
```

---

## Setup

### Prerequisites

```bash
gcloud auth application-default login
gcloud services enable aiplatform.googleapis.com run.googleapis.com \
  --project=YOUR_PROJECT
```

### Environment variables

Copy `.env.example` to `.env` in each sub-project and fill in your values:

```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=europe-west1
GEMINI_MODEL=gemini-2.5-flash
RAG_CORPUS=projects/YOUR_PROJECT_NUMBER/locations/europe-west1/ragCorpora/YOUR_CORPUS_ID

# Per-agent model overrides (optional — all default to GEMINI_MODEL)
MODEL_ROOT=gemini-2.5-flash
MODEL_KNOWLEDGE=gemini-2.5-flash
MODEL_HOTELS=gemini-2.5-flash
MODEL_FLIGHTS=gemini-2.5-flash
MODEL_ADVISOR=gemini-2.5-flash
```

### Install dependencies

```bash
pip install -r travel_rag_agent/requirements.txt
```

### Populate the RAG knowledge base (one-time)

```bash
adk web .
# Select rag_ingestion_agent
# → "Add Vienna, Budapest and Prague"
```

### Run locally

```bash
# Travel planner with session memory
adk web --memory_service_uri "rag://YOUR_MEMORY_CORPUS_ID" .
# → http://localhost:8000  (select travel_rag_agent)
```

### Run the A2A server

```bash
uvicorn travel_rag_agent.a2a_server:a2a_app --host 0.0.0.0 --port 8001
# Agent Card: http://localhost:8001/.well-known/agent-card.json
```

### Deploy to Cloud Run

```bash
adk deploy cloud_run \
  --project=YOUR_PROJECT \
  --region=europe-west1 \
  --with_ui \
  travel_rag_agent \
  -- --allow-unauthenticated
```

---

## Tech stack

| Layer | Technology | Version |
|-------|-----------|---------|
| Orchestration | Google ADK | 1.25.0 |
| LLM | Gemini 2.5 Flash (Vertex AI) | `gemini-2.5-flash` |
| RAG | Vertex AI RAG Engine (managed) | `europe-west1` |
| Hotels | Trivago MCP (StreamableHTTP) | — |
| Flights | Google Search (Gemini Grounding) | — |
| Interop | Agent2Agent Protocol (A2A) | v0.3.0 |
| Memory | Vertex AI RAG Memory Service | `europe-west1` |
| Runtime | Python | 3.12+ |
| Deploy | Cloud Run | `europe-west1` |

---

## Known limitations

- Flight prices come from Google Search (approximate, not a real airline API)
- Trivago MCP can occasionally time out
- No real booking — only reservation links are provided
- Queenstown has limited RAG coverage (1 chunk)
