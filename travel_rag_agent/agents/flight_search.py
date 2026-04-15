"""Flight Search Agent — Google Search grounding for real-time flight data."""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search

from ..skills.base import load_skill
from .models import get_model

flight_search_agent = LlmAgent(
    name="FlightSearchAgent",
    model=get_model("flights"),
    instruction=load_skill("flights"),
    description="Busca vuelos usando Google Search.",
    tools=[google_search],
    output_key="flight_results",
)
