"""Data ingestion pipeline: fetch -> chunk -> embed -> persist."""

import sys
import time
from pathlib import Path

from dotenv import load_dotenv

# Load env vars before importing modules that need them
load_dotenv(Path(__file__).parent.parent / ".env", override=True)

from ..data.chunker import chunk_destination
from ..data.wikivoyage import fetch_destinations, SEED_DESTINATIONS
from ..rag.embeddings import embed_texts
from ..rag.vector_store import VectorStore


def run(destinations: list[str] | None = None) -> None:
    """Run the full ingestion pipeline.

    1. Fetch articles from Wikivoyage
    2. Chunk the content
    3. Generate embeddings
    4. Save to disk
    """
    destinations = destinations or SEED_DESTINATIONS
    store = VectorStore()

    # Step 1: Fetch
    print(f"\n{'='*60}")
    print(f"Step 1: Fetching {len(destinations)} destinations from Wikivoyage")
    print(f"{'='*60}")
    start = time.time()
    articles = fetch_destinations(destinations, delay=1.0)
    print(f"  Fetched {len(articles)} articles in {time.time() - start:.1f}s")

    # Step 2: Chunk
    print(f"\n{'='*60}")
    print(f"Step 2: Chunking content")
    print(f"{'='*60}")
    all_chunks = []
    for article in articles:
        chunks = chunk_destination(
            destination=article["destination"],
            sections=article["sections"],
            images=article["images"],
            chunk_size=500,
            chunk_overlap=50,
        )
        all_chunks.extend(chunks)
        print(f"  {article['destination']}: {len(chunks)} chunks")

    print(f"  Total: {len(all_chunks)} chunks")

    if not all_chunks:
        print("No chunks generated. Exiting.")
        return

    # Step 3: Embed
    print(f"\n{'='*60}")
    print(f"Step 3: Generating embeddings")
    print(f"{'='*60}")
    texts = [chunk.to_embedding_text() for chunk in all_chunks]
    start = time.time()
    embeddings = embed_texts(texts, show_progress=True)
    print(f"  Generated {embeddings.shape} embeddings in {time.time() - start:.1f}s")

    # Step 4: Save
    print(f"\n{'='*60}")
    print(f"Step 4: Saving to data store")
    print(f"{'='*60}")
    store.save(embeddings, all_chunks)

    # Summary
    print(f"\n{'='*60}")
    print(f"Pipeline complete!")
    print(f"  Destinations: {len(articles)}")
    print(f"  Chunks: {len(all_chunks)}")
    print(f"  Embedding dimensions: {embeddings.shape[1]}")
    print(f"{'='*60}")


if __name__ == "__main__":
    # Allow passing specific destinations as CLI args
    if len(sys.argv) > 1:
        run(sys.argv[1:])
    else:
        run()
