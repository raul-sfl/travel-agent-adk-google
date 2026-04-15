# Contenido para las Slides del Hackathon

> Copia y pega cada seccion en su slide correspondiente

---

## SLIDE 1 — Presentacion

### Agent Name
Travel Planner AI

### Short Description + Whatever you want to share
AI travel agent that turns a social media photo into a complete trip plan.

Drop an image from Instagram, and the agent identifies the destination, interviews you step-by-step (origin, dates, budget, interests), then searches flights, hotels, and attractions IN PARALLEL — delivering ONE unified proposal with booking links and a day-by-day itinerary.

Built entirely on Google ADK with 5 specialized sub-agents, Vertex AI RAG, MCP Protocol (Trivago), Google Search grounding, A2A Protocol, and a configurable Skills system — all deployed on Cloud Run.

### Business Impact (KPIs)

Target Market: Online Travel Agency (OTA) market
- Europe: $196B | USA: $67.7B (2025)

Revenue Model (4 streams):
- Hotel affiliate: 3.75-6% per booking (Booking.com/Trivago)
- Flight affiliate: $5-15 per booking (Skyscanner/Kayak)
- Premium subscription: $9.99/month
- B2B SaaS white-label: $499-1,999/month

Projections:
- Year 1: $500K revenue | 15,000 users
- Year 3: $8.3M revenue | 200,000 users
- Year 5: $18.5M revenue | 700,000 users

Unit Economics:
- Cost per session: $0.08 (Gemini Flash + RAG)
- Revenue per user/month: $3.50 (conservative)
- Gross margin: 89%

### Project Team
(Tu nombre aqui)

---

## SLIDE 2 — Arquitectura + Tech Stack

### Agent Architecture / Tech Stack

```
                    travel_planner (LlmAgent)
                    Conversational interview + refinement
                    Model: configurable via MODEL_ROOT
                    Skill: root.md (Markdown + frontmatter)
                              |
                    ResearchPipeline (SequentialAgent)
                    ┌─────────┼─────────┐
                    |         |         |
          TravelKnowledge  HotelSearch  FlightSearch
          Vertex AI RAG    Trivago MCP  Google Search
          MODEL_KNOWLEDGE  MODEL_HOTELS MODEL_FLIGHTS
          knowledge.md     hotels.md    flights.md
                    |         |         |
                    └─────────┼─────────┘
                              |
                    TravelAdvisorAgent
                    Synthesizes → ONE proposal + booking links
                    MODEL_ADVISOR | advisor.md
```

Google Cloud Services:
- ADK 1.25.0 — Multi-agent orchestration (Sequential + Parallel)
- ADK Skills — Agent behavior in editable .md files with YAML frontmatter
- Vertex AI RAG Engine — 27 destinations from Wikivoyage (managed, europe-west1)
- Vertex AI RAG Memory — Session memory persists across conversations
- Gemini 2.5 Flash — Multimodal (image → destination identification)
- MCP Protocol — Trivago hotel search (StreamableHTTP, real prices + booking links)
- Google Search — Flight search via Gemini Grounding (real-time prices)
- A2A Protocol — Agent exposed as A2A server, consumable by any A2A-compatible agent
- Cloud Run — Production deployment (europe-west1)

Key Design Decisions:
- 1 tool per agent (Vertex AI limitation: google_search can't mix with FunctionTool)
- Each agent has its own model (configurable via env vars)
- Skills loaded from Markdown files (non-developers can tune behavior)
- ONE proposal, not 10 options (avoids choice paralysis)
- Smart interview (skips questions already answered implicitly)

Separate Projects:
- travel_rag_agent → Production agent (Cloud Run)
- rag_ingestion_agent → Populates Vertex AI RAG from Wikivoyage (local)
- a2a_client_example → Demo: social media bot consuming travel planner via A2A

### Demo Script (4-5 min)

1. Open Cloud Run URL → select travel_rag_agent
2. Paste image of Barcelona from Instagram
3. Agent: "Parece Barcelona! Desde que ciudad sales?"
4. Answer questions one by one (agent skips what it already knows)
5. Agent confirms summary → "Todo correcto?"
6. "Si" → Agent searches in PARALLEL (RAG + Trivago + Google Search)
7. TravelAdvisor presents ONE unified proposal:
   - YOUR flight (airline, price, booking link)
   - YOUR hotel (name, price, Trivago link)
   - YOUR itinerary (day by day)
   - Total budget
8. "No me gusta el hotel" → Agent asks what to change → re-searches
9. Show A2A: another agent consuming ours via Agent Card
10. Show Skills: edit advisor.md → change agent behavior without code

---

## Notas para la presentacion

### Puntos que maximizan la puntuacion:

**Tech Stack & Complexity (40%)** — Enfatizar:
- ADK multi-agent (SequentialAgent + ParallelAgent)
- ADK Skills system (Markdown editables)
- 5 modelos configurables independientemente
- Vertex AI RAG Engine (managed, not in-memory)
- MCP Protocol (Trivago — real hotel data)
- A2A Protocol (server + client)
- Vertex AI RAG Memory (session persistence)

**Business Impact (40%)** — Enfatizar:
- $264B addressable market (Europe + USA)
- 89% gross margin ($0.08/session cost)
- 4 revenue streams (not just one)
- Year 3 projection: $8.3M
- Go-to-market: Spain first (agent already speaks Spanish)

**Creativity (20%)** — Enfatizar:
- Social media image as entry point (the hackathon premise!)
- Smart interview (doesn't repeat questions)
- ONE proposal instead of 10 options
- Skills system (non-developers can tune agents)
- Separate ingestion agent (data pipeline as an agent)

**Bonus Deployment (+0.5pt):**
- Already deployed on Cloud Run: https://adk-default-service-name-616890188730.europe-west1.run.app

**Bonus Social Media (+0.5pt):**
- Push repo to GitHub
- Share with #GCPAIinnovators26
