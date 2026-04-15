"""Model configuration per agent.

Assign different models to different agents based on their needs:
- Cheap/fast models for simple tool-calling agents
- Powerful models for synthesis and conversation
"""

import os

# Each agent can have its own model via env var, with fallback
MODELS = {
    # Root: conversational, needs to be natural and follow instructions well
    "root": os.getenv("MODEL_ROOT", "gemini-2.5-flash"),

    # Knowledge: RAG search, simple tool calling — fast model is fine
    "knowledge": os.getenv("MODEL_KNOWLEDGE", "gemini-2.5-flash"),

    # Hotels: Trivago MCP tool calling — fast model is fine
    "hotels": os.getenv("MODEL_HOTELS", "gemini-2.5-flash"),

    # Flights: Google Search grounding — fast model is fine
    "flights": os.getenv("MODEL_FLIGHTS", "gemini-2.5-flash"),

    # Advisor: synthesis of all data into ONE proposal — needs quality
    "advisor": os.getenv("MODEL_ADVISOR", "gemini-2.5-flash"),
}


def get_model(agent_name: str) -> str:
    """Get the model for a specific agent."""
    return MODELS.get(agent_name, os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
