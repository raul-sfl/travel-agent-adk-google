"""A2A Client Example — An agent that consumes the Travel Planner via A2A.

This demonstrates how ANY agent (from another team, framework, or service)
can discover and use our Travel Planner as a remote sub-agent via A2A protocol.

Prerequisites:
    1. Travel Planner A2A server running:
       uvicorn travel_rag_agent.a2a_server:a2a_app --port 8001

    2. This agent running:
       adk web .
       → Select a2a_client_example
"""

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

load_dotenv(override=True)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Remote Travel Planner agent via A2A
TRAVEL_PLANNER_URL = os.getenv(
    "TRAVEL_PLANNER_A2A_URL",
    "http://localhost:8001",
)

travel_planner_remote = RemoteA2aAgent(
    name="travel_planner",
    description=(
        "Remote travel planning agent. Given a destination or image, "
        "it plans a complete trip with flights, hotels, itinerary, and budget. "
        "Responds in Spanish."
    ),
    agent_card=f"{TRAVEL_PLANNER_URL}/.well-known/agent-card.json",
)

# Root agent — a social media assistant that delegates travel to the remote agent
root_agent = LlmAgent(
    name="social_media_travel_bot",
    model=GEMINI_MODEL,
    instruction="""You are a social media assistant that helps users plan trips
based on travel content they find on social media.

When a user shares a travel post, image, or mentions wanting to visit a destination:
1. Extract the destination and any context from their message
2. Delegate to the travel_planner agent, which is a remote specialist
3. Relay the travel planner's response back to the user

You can also help with:
- Summarizing the travel plan
- Comparing multiple destinations
- Answering follow-up questions about the trip

Always delegate actual travel planning (flights, hotels, itineraries) to the
travel_planner agent — it has access to real-time data.
""",
    description="Social media bot that delegates travel planning to a remote A2A agent.",
    sub_agents=[travel_planner_remote],
)
