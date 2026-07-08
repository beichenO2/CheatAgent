from __future__ import annotations

from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[4] / "skills" / "cheat-agent"

REGISTERED_SKILL_IDS: list[str] = sorted(
    p.stem.removeprefix("SKILL-")
    for p in SKILLS_DIR.glob("SKILL-*.md")
    if p.stem != "SKILL-router"
)


def list_registered_skills() -> list[str]:
    return list(REGISTERED_SKILL_IDS)
