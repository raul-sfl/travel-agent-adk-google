"""Tool to fetch travel data from Wikivoyage and upload to Vertex AI RAG."""

import json
import os
import tempfile

import vertexai
from vertexai import rag

from ..data.wikivoyage import fetch_destinations
from ..data.chunker import chunk_destination

# Vertex AI RAG corpus — shared with travel_rag_agent via RAG_CORPUS env var
CORPUS = os.getenv("RAG_CORPUS", "projects/616890188730/locations/europe-west1/ragCorpora/6917529027641081856")


def fetch_and_upload_destinations(destinations: str) -> str:
    """Fetch travel guides from Wikivoyage and upload them to the Vertex AI RAG knowledge base.

    Use this tool to add new destinations to the travel knowledge base.
    The data is fetched from Wikivoyage (free travel guides), chunked into
    sections, and uploaded to the Vertex AI RAG corpus.

    Args:
        destinations: Comma-separated list of destination names to add.
                      Example: "Lisbon, Porto, Valencia"

    Returns:
        Summary of what was fetched and uploaded.
    """
    dest_list = [d.strip() for d in destinations.split(",") if d.strip()]

    if not dest_list:
        return "No destinations provided. Give me a comma-separated list like: Paris, Tokyo, Bali"

    # Init Vertex AI
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west1")
    vertexai.init(project=project, location=location)

    # Fetch from Wikivoyage
    articles = fetch_destinations(dest_list, delay=1.0)

    if not articles:
        return f"Could not fetch any articles for: {', '.join(dest_list)}"

    results = []
    for article in articles:
        chunks = chunk_destination(
            destination=article["destination"],
            sections=article["sections"],
            images=article["images"],
        )

        if not chunks:
            results.append(f"- {article['destination']}: no content found")
            continue

        # Build text document from chunks
        lines = []
        for c in chunks:
            lines.append(f"## {c.destination} — {c.section}")
            lines.append(c.text)
            lines.append("")

        content = "\n".join(lines)

        # Upload to Vertex AI RAG
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False,
            prefix=f"{article['destination'].replace(' ', '_')}_",
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            rag_file = rag.upload_file(
                corpus_name=CORPUS,
                path=tmp_path,
                display_name=f"{article['destination']} Travel Guide",
                description=f"Wikivoyage travel guide for {article['destination']}",
            )
            results.append(
                f"- {article['destination']}: {len(chunks)} chunks uploaded ({len(content)} chars)"
            )
        except Exception as e:
            results.append(f"- {article['destination']}: ERROR — {e}")
        finally:
            os.unlink(tmp_path)

    summary = f"Processed {len(articles)}/{len(dest_list)} destinations:\n"
    summary += "\n".join(results)
    return summary


def list_corpus_files() -> str:
    """List all files currently in the Vertex AI RAG knowledge base.

    Use this tool to see what destinations are already indexed.

    Returns:
        List of files in the RAG corpus with their names.
    """
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west1")
    vertexai.init(project=project, location=location)

    files = list(rag.list_files(corpus_name=CORPUS))

    if not files:
        return "The knowledge base is empty. Use fetch_and_upload_destinations to add destinations."

    lines = [f"Knowledge base has {len(files)} files:"]
    for f in files:
        lines.append(f"- {f.display_name}")

    return "\n".join(lines)
