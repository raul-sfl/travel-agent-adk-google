"""A2A Server — Exposes the travel planner agent via Agent2Agent protocol.

Run with:
    uvicorn travel_rag_agent.a2a_server:a2a_app --host 0.0.0.0 --port 8001

Agent Card available at:
    http://localhost:8001/.well-known/agent-card.json

Any A2A-compatible agent can now consume this travel planner as a remote agent.
"""

from dotenv import load_dotenv

load_dotenv(override=True)

from a2a.types import AgentCard, AgentCapabilities, AgentSkill
from google.adk.a2a.utils.agent_to_a2a import to_a2a

from .agent import root_agent

agent_card = AgentCard(
    name="Travel Planner Agent",
    url="http://localhost:8001",
    description=(
        "Agente de planificación de viajes que, dada una imagen o destino, "
        "genera un plan completo con vuelos (Google Search), hoteles (Trivago), "
        "itinerario personalizado (RAG sobre Wikivoyage) y presupuesto estimado. "
        "Conversacional en español."
    ),
    version="1.0.0",
    capabilities=AgentCapabilities(),
    skills=[
        AgentSkill(
            id="travel-planning",
            name="Travel Planning",
            description="Plan a complete trip from an image or destination name",
            tags=["travel", "flights", "hotels", "itinerary", "RAG"],
            examples=[
                "Quiero viajar a Barcelona",
                "Plan a trip to Tokyo for 5 days",
                "Busca vuelos y hoteles para Roma en julio",
            ],
        ),
    ],
    default_input_modes=["text/plain", "image/*"],
    default_output_modes=["text/plain"],
    supports_authenticated_extended_card=False,
)

a2a_app = to_a2a(root_agent, port=8001, agent_card=agent_card)
