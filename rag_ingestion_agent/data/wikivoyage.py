"""Fetch and parse travel articles from Wikivoyage via MediaWiki API."""

import json
import re
import time
import urllib.request
from dataclasses import dataclass

API_URL = "https://en.wikivoyage.org/w/api.php"
USER_AGENT = "TravelRAGBot/1.0 (educational project; travel-rag-agent)"

# Sections relevant for travel inspiration
TRAVEL_SECTIONS = {
    "Understand", "See", "Do", "Eat", "Drink", "Sleep",
    "Buy", "Learn", "Get in", "Get around", "Stay safe", "Go next",
}

# Seed destinations — diverse global coverage
SEED_DESTINATIONS = [
    # Europe
    "Paris", "Barcelona", "Rome", "Amsterdam", "Prague",
    "Lisbon", "Istanbul", "Dubrovnik", "Santorini", "Edinburgh",
    # Asia
    "Tokyo", "Bangkok", "Bali", "Kyoto", "Seoul",
    "Hanoi", "Singapore",
    # Americas
    "New York City", "Buenos Aires", "Mexico City",
    "Rio de Janeiro", "Cusco", "Havana",
    # Africa & Middle East
    "Marrakech", "Cape Town", "Nairobi",
    # Oceania
    "Sydney", "Queenstown",
]


@dataclass
class WikiSection:
    """A parsed section from a Wikivoyage article."""

    title: str
    level: int  # 2 = ==, 3 = ===, etc.
    content: str
    images: list[str]


def fetch_article(page: str) -> dict | None:
    """Fetch a Wikivoyage article's wikitext and images."""
    params = {
        "action": "parse",
        "page": page,
        "prop": "wikitext|images",
        "format": "json",
    }
    query = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
    url = f"{API_URL}?{query}"

    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            if "error" in data:
                print(f"  API error for '{page}': {data['error'].get('info', 'unknown')}")
                return None
            return data["parse"]
    except Exception as e:
        print(f"  Failed to fetch '{page}': {e}")
        return None


def parse_sections(wikitext: str) -> list[WikiSection]:
    """Parse wikitext into sections, extracting text and image references."""
    lines = wikitext.split("\n")
    sections: list[WikiSection] = []
    current_title = "overview"
    current_level = 1
    current_lines: list[str] = []

    for line in lines:
        # Detect section headers: == Title == or === Subtitle ===
        header_match = re.match(r"^(={2,})\s*(.+?)\s*=+\s*$", line)
        if header_match:
            # Save previous section
            if current_lines:
                content, images = _clean_wikitext(current_lines)
                if content.strip():
                    sections.append(WikiSection(
                        title=current_title,
                        level=current_level,
                        content=content,
                        images=images,
                    ))
            current_level = len(header_match.group(1))
            current_title = header_match.group(2).strip()
            current_lines = []
        else:
            current_lines.append(line)

    # Save last section
    if current_lines:
        content, images = _clean_wikitext(current_lines)
        if content.strip():
            sections.append(WikiSection(
                title=current_title,
                level=current_level,
                content=content,
                images=images,
            ))

    return sections


def _clean_wikitext(lines: list[str]) -> tuple[str, list[str]]:
    """Clean wikitext markup, returning plain text and extracted image filenames."""
    images = []
    cleaned = []

    for line in lines:
        # Extract image filenames
        for m in re.finditer(r"\[\[File:([^|\]]+)", line):
            images.append(m.group(1))

        # Skip template-only lines (mapframes, infoboxes that span one line)
        if re.match(r"^\{\{(Mapframe|SeeDistricts|marker\b)", line):
            continue

        # Clean wiki markup
        text = line
        # Remove file embeds
        text = re.sub(r"\[\[File:[^\]]+\]\]", "", text)
        # Extract marker names: {{marker|...|name=Name}} -> Name
        text = re.sub(
            r"\{\{marker\|[^}]*\|name=\[\[[^\]]*\|([^\]]+)\]\]\}\}",
            r"\1",
            text,
        )
        text = re.sub(r"\{\{marker\|[^}]*\|name=([^|}]+)[^}]*\}\}", r"\1", text)
        # Convert wiki links [[target|display]] -> display, [[target]] -> target
        text = re.sub(r"\[\[[^|\]]*\|([^\]]+)\]\]", r"\1", text)
        text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
        # Remove external links [url text] -> text
        text = re.sub(r"\[https?://\S+\s+([^\]]+)\]", r"\1", text)
        text = re.sub(r"\[https?://\S+\]", "", text)
        # Remove remaining templates {{...}} (simple, non-nested)
        text = re.sub(r"\{\{[^}]+\}\}", "", text)
        # Remove bold/italic markup
        text = re.sub(r"'{2,5}", "", text)
        # Clean extra whitespace
        text = re.sub(r"  +", " ", text).strip()

        if text:
            cleaned.append(text)

    return "\n".join(cleaned), images


def build_image_url(filename: str) -> str:
    """Build a Wikimedia Commons thumbnail URL from a filename."""
    import hashlib
    name = filename.replace(" ", "_")
    md5 = hashlib.md5(name.encode()).hexdigest()
    encoded = urllib.parse.quote(name)
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{md5[0]}/{md5[:2]}/{encoded}/640px-{encoded}"


def fetch_destinations(
    destinations: list[str] | None = None,
    delay: float = 1.0,
) -> list[dict]:
    """Fetch and parse multiple Wikivoyage articles.

    Returns a list of dicts with destination info and parsed sections.
    """
    destinations = destinations or SEED_DESTINATIONS
    results = []

    for i, dest in enumerate(destinations):
        print(f"[{i + 1}/{len(destinations)}] Fetching: {dest}")
        article = fetch_article(dest)
        if not article:
            continue

        wikitext = article["wikitext"]["*"]
        all_images = [img for img in article.get("images", []) if _is_photo(img)]
        sections = parse_sections(wikitext)

        # Filter to travel-relevant sections
        travel_sections = []
        for section in sections:
            normalized = section.title.strip()
            if normalized in TRAVEL_SECTIONS or section.level == 1:
                travel_sections.append(section)
            elif section.level >= 3:
                # Include subsections of travel sections
                parent = _find_parent_section(sections, section)
                if parent and parent.title in TRAVEL_SECTIONS:
                    travel_sections.append(section)

        results.append({
            "destination": dest,
            "sections": travel_sections,
            "images": [build_image_url(img) for img in all_images[:10]],
        })

        if i < len(destinations) - 1:
            time.sleep(delay)

    return results


def _find_parent_section(
    sections: list[WikiSection], target: WikiSection
) -> WikiSection | None:
    """Find the parent (lower level) section of a given section."""
    idx = sections.index(target)
    for i in range(idx - 1, -1, -1):
        if sections[i].level < target.level:
            return sections[i]
    return None


def _is_photo(filename: str) -> bool:
    """Filter out icons, flags, SVGs — keep actual photos."""
    lower = filename.lower()
    if any(lower.endswith(ext) for ext in (".svg", ".png")):
        return False
    if any(kw in lower for kw in ("flag_of", "icon", "logo", "tabliczka")):
        return False
    return True
