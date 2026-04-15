"""Travel RAG Agent — Multi-agent pipeline with per-agent model selection.

Architecture:
  root_agent (LlmAgent)           → MODEL_ROOT  [recommend_destinations tool]
    └── ResearchPipeline (SequentialAgent)
        ├── TravelKnowledgeAgent  → MODEL_KNOWLEDGE  [Vertex AI RAG] (first — our data)
        ├── ParallelBooking (ParallelAgent)
        │   ├── HotelSearchAgent  → MODEL_HOTELS     [Trivago MCP]
        │   └── FlightSearchAgent → MODEL_FLIGHTS    [Google Search]
        └── TravelAdvisorAgent    → MODEL_ADVISOR    [Synthesizer]

Model configuration via env vars (see agents/models.py).
"""

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, ParallelAgent, SequentialAgent
from google.adk.tools import FunctionTool

load_dotenv(override=True)

from .agents.travel_knowledge import travel_knowledge_agent
from .agents.hotel_search import hotel_search_agent
from .agents.flight_search import flight_search_agent
from .agents.travel_advisor import travel_advisor
from .agents.models import get_model
from .skills.base import load_skill
from .tools.destinations import recommend_destinations

recommend_tool = FunctionTool(recommend_destinations)

# ============================================================
# Parallel: Hotels + Flights (booking data, both external)
# ============================================================

parallel_booking = ParallelAgent(
    name="ParallelBookingAgent",
    sub_agents=[hotel_search_agent, flight_search_agent],
    description="Busca hoteles y vuelos en paralelo.",
)

# ============================================================
# Research Pipeline: RAG first → then hotels+flights → advisor
# ============================================================

research_pipeline = SequentialAgent(
    name="ResearchPipeline",
    sub_agents=[travel_knowledge_agent, parallel_booking, travel_advisor],
    description="Pipeline: RAG (nuestros datos) → hoteles+vuelos en paralelo → propuesta.",
)

# ============================================================
# Root Agent
# ============================================================

root_agent = LlmAgent(
    name="travel_planner",
    model=get_model("root"),
    instruction=load_skill("root"),
    description="Asesor de viajes: entrevista al usuario, delega investigación, gestiona cambios.",
    tools=[recommend_tool],
    sub_agents=[research_pipeline],
)
