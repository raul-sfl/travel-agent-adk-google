"""Recursive text splitter for travel content."""

import re
import uuid

from .schema import TravelChunk


def chunk_destination(
    destination: str,
    sections: list,
    images: list[str],
    chunk_size: int = 500,
    chunk_overlap: int = 50,
) -> list[TravelChunk]:
    """Split a destination's sections into chunks for embedding.

    Args:
        destination: Name of the destination (e.g., "Barcelona").
        sections: List of WikiSection objects from the parser.
        images: List of image URLs for this destination.
        chunk_size: Target chunk size in characters.
        chunk_overlap: Overlap between consecutive chunks.

    Returns:
        List of TravelChunk objects ready for embedding.
    """
    chunks: list[TravelChunk] = []

    for section in sections:
        text = _clean_templates(section.content)
        if not text.strip() or len(text.strip()) < 30:
            continue

        section_name = _normalize_section_name(section.title)
        section_images = [
            url for url in images
        ] if section.images else []

        text_chunks = _split_text(text, chunk_size, chunk_overlap)

        for i, chunk_text in enumerate(text_chunks):
            if len(chunk_text.strip()) < 30:
                continue

            chunks.append(TravelChunk(
                chunk_id=str(uuid.uuid4()),
                destination=destination,
                source="wikivoyage",
                section=section_name,
                text=chunk_text.strip(),
                metadata={
                    "subsection": section.title if section.level >= 3 else None,
                    "images": section_images[:3] if i == 0 else [],
                    "chunk_index": i,
                },
            ))

    return chunks


def _split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Recursively split text into chunks, preferring natural boundaries."""
    if len(text) <= chunk_size:
        return [text]

    # Try splitting at paragraph boundaries first
    separators = ["\n\n", "\n", ". ", ", ", " "]
    for sep in separators:
        parts = text.split(sep)
        if len(parts) <= 1:
            continue

        chunks = []
        current = ""
        for part in parts:
            candidate = current + sep + part if current else part
            if len(candidate) > chunk_size and current:
                chunks.append(current)
                # Overlap: keep end of previous chunk
                if overlap > 0 and len(current) > overlap:
                    current = current[-overlap:] + sep + part
                else:
                    current = part
            else:
                current = candidate

        if current:
            chunks.append(current)

        if len(chunks) > 1:
            return chunks

    # Fallback: hard split at chunk_size
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i : i + chunk_size])
    return chunks


def _clean_templates(text: str) -> str:
    """Remove multi-line wiki templates like {{infobox|...|...}}."""
    # Remove multi-line templates by tracking brace depth
    result = []
    depth = 0
    i = 0
    while i < len(text):
        if text[i : i + 2] == "{{":
            depth += 1
            i += 2
        elif text[i : i + 2] == "}}":
            depth = max(0, depth - 1)
            i += 2
        elif depth == 0:
            result.append(text[i])
            i += 1
        else:
            i += 1
    return "".join(result)


def _normalize_section_name(title: str) -> str:
    """Map section titles to canonical names."""
    title = title.strip()
    # Remove any remaining wiki markup from title
    title = re.sub(r"\[.*?\]", "", title).strip()
    canonical = {
        "understand": "Understand",
        "see": "See",
        "do": "Do",
        "eat": "Eat",
        "drink": "Drink",
        "sleep": "Sleep",
        "buy": "Buy",
        "learn": "Learn",
        "get in": "Get in",
        "get around": "Get around",
        "stay safe": "Stay safe",
        "go next": "Go next",
        "overview": "Overview",
    }
    return canonical.get(title.lower(), title)
