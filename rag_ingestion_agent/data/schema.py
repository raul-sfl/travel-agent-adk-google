"""Pydantic models for travel data."""

from pydantic import BaseModel


class TravelChunk(BaseModel):
    """A chunk of travel content ready for embedding and retrieval."""

    chunk_id: str
    destination: str
    source: str  # "wikivoyage" | "opentripmap"
    section: str  # "See" | "Do" | "Eat" | "Sleep" | "Get in" | "overview" | etc.
    text: str
    metadata: dict = {}  # lat/lon, images, categories, urls, etc.

    def to_embedding_text(self) -> str:
        """Text representation used for generating embeddings."""
        return f"{self.destination} - {self.section}: {self.text}"
