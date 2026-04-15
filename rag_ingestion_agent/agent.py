"""RAG Ingestion Agent — Populates the Vertex AI RAG knowledge base.

This agent fetches travel guides from Wikivoyage and uploads them
to the Vertex AI RAG corpus that the Travel Planner agent consumes.

It can:
- Add new destinations to the knowledge base
- List what's already indexed
- Be asked in natural language: "Add Lisbon and Porto to the knowledge base"
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .tools.wikivoyage_tool import fetch_and_upload_destinations, list_corpus_files

load_dotenv(override=True)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

fetch_tool = FunctionTool(fetch_and_upload_destinations)
list_tool = FunctionTool(list_corpus_files)

root_agent = LlmAgent(
    name="rag_ingestion_agent",
    model=GEMINI_MODEL,
    instruction="""Eres el agente encargado de gestionar la base de conocimiento de viajes.
SIEMPRE respondes en ESPAÑOL.

Tu trabajo es poblar y mantener el Vertex AI RAG corpus con guías de viaje
de Wikivoyage. Tienes dos herramientas:

1. **fetch_and_upload_destinations**: Descarga guías de Wikivoyage y las sube al RAG.
   Recibe una lista de destinos separados por comas.

2. **list_corpus_files**: Lista los destinos que ya están en la base de conocimiento.

## Cómo interactuar

- Si el usuario dice "añade Barcelona y Roma" → usa fetch_and_upload_destinations
- Si el usuario dice "qué destinos tenemos?" → usa list_corpus_files
- Si el usuario dice "añade destinos de Asia" → sugiere una lista concreta
  (Tokyo, Bangkok, Bali, Seoul, etc.) y pide confirmación antes de subir
- Si el usuario dice "añade 50 destinos populares" → genera una lista de 50
  destinos diversos (Europa, Asia, Americas, Africa, Oceania) y pide confirmación

## Reglas
- Pide CONFIRMACIÓN antes de subir destinos (puede tardar)
- Informa del progreso: cuántos destinos se procesaron, cuántos chunks
- Si un destino falla, reporta el error sin detenerte
- Sugiere destinos que complementen los existentes (diversidad geográfica)
""",
    description="Gestiona la base de conocimiento RAG: añade destinos desde Wikivoyage.",
    tools=[fetch_tool, list_tool],
)
