"""RAG search tool — queries Vertex AI RAG corpus programmatically."""

import os
from pathlib import Path

import vertexai
from vertexai import rag
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env", override=True)
load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)

CORPUS = os.getenv("RAG_CORPUS", "projects/616890188730/locations/europe-west1/ragCorpora/6917529027641081856")


def search_travel_knowledge(query: str) -> str:
    """Search the travel knowledge base for information about destinations.

    Use this tool to find details about what to see, do, eat, how to get around,
    safety tips, and practical travel information for any destination.

    Make MULTIPLE searches with different queries to cover all aspects:
    - "[destination] things to see landmarks"
    - "[destination] restaurants food cuisine"
    - "[destination] transport safety"

    Args:
        query: Search query about a travel destination or topic.

    Returns:
        Relevant travel information from our Wikivoyage knowledge base.
    """
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west1")
    vertexai.init(project=project, location=location)

    response = rag.retrieval_query(
        text=query,
        rag_resources=[rag.RagResource(rag_corpus=CORPUS)],
        rag_retrieval_config=rag.RagRetrievalConfig(top_k=10),
    )

    if not response.contexts.contexts:
        return f"No encontre informacion sobre '{query}' en nuestro catalogo."

    results = []
    for ctx in response.contexts.contexts:
        if ctx.text:
            results.append(ctx.text[:500])

    return "\n\n---\n\n".join(results)
