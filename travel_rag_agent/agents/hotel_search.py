"""Hotel Search Agent — Trivago MCP with error resilience."""

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from ..skills.base import load_skill
from .models import get_model

trivago_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://mcp.trivago.com/mcp",
        timeout=30,
        sse_read_timeout=30,
    ),
)

hotel_search_agent = LlmAgent(
    name="HotelSearchAgent",
    model=get_model("hotels"),
    instruction=load_skill("hotels"),
    description="Busca hoteles en Trivago para el destino.",
    tools=[trivago_toolset],
    output_key="hotel_results",
)
