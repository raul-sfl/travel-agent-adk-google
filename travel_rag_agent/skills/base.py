"""Skill loader — loads agent instructions from Markdown files with YAML frontmatter."""

from pathlib import Path
import yaml

SKILLS_DIR = Path(__file__).parent


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse a Markdown file with YAML frontmatter.

    Returns:
        Tuple of (metadata dict, body string).
    """
    if not text.startswith("---"):
        return {}, text

    parts = text.split("---", 2)
    # parts[0] is empty (before first ---), parts[1] is frontmatter, parts[2] is body
    meta = yaml.safe_load(parts[1]) or {}
    body = parts[2].strip()
    return meta, body


def load_skill(name: str) -> str:
    """Load an agent instruction from a Markdown skill file.

    The instruction is the body of the .md file (everything after the frontmatter).

    Args:
        name: Skill filename without extension (e.g., "root", "advisor").

    Returns:
        The instruction string for the agent.
    """
    path = SKILLS_DIR / f"{name}.md"
    text = path.read_text(encoding="utf-8")
    _, instruction = _parse_frontmatter(text)
    return instruction


def load_skill_meta(name: str) -> dict:
    """Load skill metadata from the frontmatter."""
    path = SKILLS_DIR / f"{name}.md"
    text = path.read_text(encoding="utf-8")
    meta, instruction = _parse_frontmatter(text)
    meta["instruction"] = instruction
    return meta


def list_skills() -> list[dict]:
    """List all available skills with their metadata."""
    skills = []
    for path in sorted(SKILLS_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        meta, _ = _parse_frontmatter(text)
        skills.append({
            "file": path.name,
            "name": meta.get("name", path.stem),
            "agent": meta.get("agent", "unknown"),
            "description": meta.get("description", ""),
            "version": meta.get("version", "1.0"),
        })
    return skills
