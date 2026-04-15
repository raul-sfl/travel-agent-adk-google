"""Travel Advisor Agent — Synthesizes all research into ONE best proposal."""

from google.adk.agents import LlmAgent

from ..skills.base import load_skill
from .models import get_model

travel_advisor = LlmAgent(
    name="TravelAdvisorAgent",
    model=get_model("advisor"),
    instruction=load_skill("advisor"),
    description="Sintetiza la investigación en UNA propuesta unificada con links de reserva.",
)
