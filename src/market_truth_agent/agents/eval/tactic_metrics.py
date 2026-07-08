from __future__ import annotations

import math
from collections import Counter
from typing import Any


def skill_kind_count(agent_metadata: list[dict[str, Any]]) -> int:
    ids = [m.get("skill_id") for m in agent_metadata if m.get("skill_id")]
    return len(set(ids))


def skill_invoke_count(agent_metadata: list[dict[str, Any]]) -> int:
    return len([m for m in agent_metadata if m.get("skill_id")])


def skill_richness(agent_metadata: list[dict[str, Any]]) -> float:
    ids = [m.get("skill_id") for m in agent_metadata if m.get("skill_id")]
    if not ids:
        return 0.0
    counts = Counter(ids)
    total = sum(counts.values())
    probs = [c / total for c in counts.values()]
    return -sum(p * math.log(p + 1e-12) for p in probs)


def skill_coverage(agent_metadata: list[dict[str, Any]], available_skills: list[str]) -> float:
    if not available_skills:
        return 0.0
    used = {m.get("skill_id") for m in agent_metadata if m.get("skill_id")}
    return len(used & set(available_skills)) / len(available_skills)


def summarize_session(agent_metadata: list[dict[str, Any]], available_skills: list[str] | None = None) -> dict[str, float]:
    available = available_skills or []
    return {
        "skill_kind_count": skill_kind_count(agent_metadata),
        "skill_invoke_count": skill_invoke_count(agent_metadata),
        "skill_richness": skill_richness(agent_metadata),
        "skill_coverage": skill_coverage(agent_metadata, available),
    }
