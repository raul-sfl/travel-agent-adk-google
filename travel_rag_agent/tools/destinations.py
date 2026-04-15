"""Tool to recommend destinations from our knowledge base based on what the user describes."""

import os
from pathlib import Path

import vertexai
from vertexai import rag
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)
load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)

CORPUS = os.getenv("RAG_CORPUS", "projects/616890188730/locations/europe-west1/ragCorpora/6917529027641081856")


def recommend_destinations(description: str) -> str:
    """Search our travel knowledge base to recommend destinations matching a description.

    Use this tool when the user describes a type of trip, shows an image of a place,
    or asks for recommendations WITHOUT naming a specific destination.

    Examples:
    - "tropical beach with palm trees" → searches for beach destinations we have
    - "old European city with history" → searches for historic European cities
    - "Asian street food and temples" → searches for Asian destinations

    Args:
        description: What the user is looking for — landscape type, activities,
                     climate, mood, or any travel preference.

    Returns:
        Matching destinations from our knowledge base with relevant details.
    """
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west1")
    vertexai.init(project=project, location=location)

    response = rag.retrieval_query(
        text=description,
        rag_resources=[rag.RagResource(rag_corpus=CORPUS)],
        rag_retrieval_config=rag.RagRetrievalConfig(top_k=10),
    )

    if not response.contexts.contexts:
        return "No encontre destinos que coincidan. Nuestros destinos incluyen: Paris, Barcelona, Rome, Amsterdam, Tokyo, Bangkok, Bali, Santorini, Istanbul, New York City, Buenos Aires, y mas."

    # Extract unique destinations from results
    seen = {}
    for ctx in response.contexts.contexts:
        text = ctx.text[:300] if ctx.text else ""
        # The destination name is in the section header "## Destination — Section"
        if "—" in text[:100]:
            dest = text.split("—")[0].replace("##", "").strip()
            if dest and dest not in seen:
                seen[dest] = text[:200]

    if not seen:
        return "No encontre destinos que coincidan con esa descripcion."

    lines = ["Basandome en lo que describes, te recomiendo estos destinos de nuestra base de conocimiento:\n"]
    for dest, preview in list(seen.items())[:5]:
        lines.append(f"- **{dest}**: {preview.split(chr(10))[0][:150]}")

    lines.append("\nDime cual te interesa y te preparo el viaje completo.")
    return "\n".join(lines)
