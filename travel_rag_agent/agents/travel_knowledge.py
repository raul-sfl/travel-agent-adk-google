"""Travel Knowledge Agent — Vertex AI RAG search via FunctionTool."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..tools.rag_search import search_travel_knowledge
from ..skills.base import load_skill
from .models import get_model

rag_tool = FunctionTool(search_travel_knowledge)

travel_knowledge_agent = LlmAgent(
    name="TravelKnowledgeAgent",
    model=get_model("knowledge"),
    instruction=load_skill("knowledge"),
    description="Busca información de viaje en Vertex AI RAG (Wikivoyage).",
    tools=[rag_tool],
    output_key="travel_knowledge",
)
