"""Session-level claim fusion (Readme §Claim 融合路线分歧, 2026-07-09).

Within-user fusion answers: given one user's multi-turn claims in a session,
what is their final stance per (region, indicator) slot?

Three modes (ablation-comparable):
- llm       LLM semantic fusion — reads the whole dialogue (incl. agent probes),
            resolves semantic equivalence (还行=按需=中性) and genuine retractions,
            outputs final slots with evidence_turns. Primary mode.
- voting    Confidence-weighted vote over per-turn claims. Deterministic baseline.
- last_wins Legacy behavior (the last claim per slot wins). Regression baseline.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

from market_truth_agent.analysis.ontology import INDICATORS, REGIONS
from market_truth_agent.llm.client import llm_mode, normalize_model, tool_completion
from market_truth_agent.llm.prompts import build_fusion_prompt
from market_truth_agent.models import Claim, Conversation

FUSION_MODES = ("llm", "voting", "last_wins")

_VALUE_ENUM = [
    "高", "中", "低",
    "积极", "消极", "中性",
    "是", "否",
    "上涨", "下跌", "平稳",
]


@dataclass
class FusedSlot:
    region: str
    indicator: str
    value: str
    confidence: float = 0.75
    evidence_turns: list[int] = field(default_factory=list)
    rationale: str = ""


SlotKey = tuple[str, str]  # (region, indicator)


def fuse_last_wins(claims: list[Claim]) -> dict[SlotKey, FusedSlot]:
    out: dict[SlotKey, FusedSlot] = {}
    for c in claims:
        turn = c.provenance.turn_index if c.provenance else -1
        out[(c.region, c.indicator)] = FusedSlot(
            region=c.region,
            indicator=c.indicator,
            value=c.value,
            confidence=c.extractor_confidence,
            evidence_turns=[turn] if turn >= 0 else [],
            rationale="last-wins baseline",
        )
    return out


def fuse_voting(claims: list[Claim]) -> dict[SlotKey, FusedSlot]:
    """Confidence-weighted vote per slot; late claims break ties."""
    grouped: dict[SlotKey, list[Claim]] = defaultdict(list)
    for c in claims:
        grouped[(c.region, c.indicator)].append(c)

    out: dict[SlotKey, FusedSlot] = {}
    for key, slot_claims in grouped.items():
        weights: dict[str, float] = defaultdict(float)
        latest_turn: dict[str, int] = defaultdict(int)
        for c in slot_claims:
            weights[c.value] += max(c.extractor_confidence, 0.05)
            turn = c.provenance.turn_index if c.provenance else 0
            latest_turn[c.value] = max(latest_turn[c.value], turn)
        best_value = max(weights, key=lambda v: (weights[v], latest_turn[v]))
        total = sum(weights.values()) or 1.0
        out[key] = FusedSlot(
            region=key[0],
            indicator=key[1],
            value=best_value,
            confidence=weights[best_value] / total,
            evidence_turns=sorted(
                {
                    c.provenance.turn_index
                    for c in slot_claims
                    if c.value == best_value and c.provenance
                }
            ),
            rationale=f"weighted vote {dict(weights)}",
        )
    return out


def _fusion_tool_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "final_slots": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "enum": list(REGIONS)},
                        "indicator": {"type": "string", "enum": list(INDICATORS)},
                        "value": {"type": "string", "enum": _VALUE_ENUM},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "evidence_turns": {
                            "type": "array",
                            "items": {"type": "integer"},
                        },
                        "rationale": {"type": "string"},
                    },
                    "required": [
                        "region",
                        "indicator",
                        "value",
                        "confidence",
                        "evidence_turns",
                    ],
                },
            }
        },
        "required": ["final_slots"],
    }


def fuse_llm(
    conversation: Conversation,
    claims: list[Claim],
    *,
    default_region: str,
    week: str,
) -> dict[SlotKey, FusedSlot]:
    """One LLM pass over the full dialogue → final slots with evidence.

    Mock mode and hard failures fall back to voting (deterministic CI).
    """
    if llm_mode() == "mock" or not claims:
        return fuse_voting(claims)

    per_turn = [
        {
            "turn_index": c.provenance.turn_index if c.provenance else -1,
            "region": c.region,
            "indicator": c.indicator,
            "value": c.value,
            "confidence": c.extractor_confidence,
        }
        for c in claims
    ]
    system, user = build_fusion_prompt(
        turns=[
            {"turn_index": t.turn_index, "speaker": t.speaker, "text": t.text}
            for t in conversation.turns
        ],
        per_turn_claims=per_turn,
        default_region=default_region,
        week=week,
    )
    payload = tool_completion(
        system,
        user,
        tool_name="emit_final_slots",
        tool_description=(
            "综合整个 session 的对话与逐轮 claim，输出该用户对每个指标的最终立场。"
            "语义等价表述（还行=按需=随行就市=中性）合并；追问后的澄清优先于早期模糊表述；"
            "打太极/未表态的指标不输出。每个槽必须引用 evidence_turns。"
        ),
        parameters_schema=_fusion_tool_schema(),
        temperature=0.1,
        model=normalize_model(),
    )
    if not payload:
        return fuse_voting(claims)
    items = payload.get("final_slots", [])
    if not isinstance(items, list):
        return fuse_voting(claims)

    out: dict[SlotKey, FusedSlot] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        region = str(item.get("region", default_region))
        indicator = str(item.get("indicator", ""))
        value = str(item.get("value", "")).strip()
        if indicator == "采购积极性" and value == "中":
            value = "中性"
        if region not in REGIONS or indicator not in INDICATORS:
            continue
        if not _valid_fused_value(indicator, value):
            continue
        evidence = item.get("evidence_turns", [])
        if not isinstance(evidence, list):
            evidence = []
        out[(region, indicator)] = FusedSlot(
            region=region,
            indicator=indicator,
            value=value,
            confidence=float(item.get("confidence", 0.75)),
            evidence_turns=[int(t) for t in evidence if isinstance(t, (int, float))],
            rationale=str(item.get("rationale", "")),
        )
    return out if out else fuse_voting(claims)


def fuse_session(
    conversation: Conversation,
    claims: list[Claim],
    *,
    mode: str = "llm",
    default_region: str = "青岛港",
    week: str = "2026-W27",
) -> dict[SlotKey, FusedSlot]:
    if mode == "last_wins":
        return fuse_last_wins(claims)
    if mode == "voting":
        return fuse_voting(claims)
    if mode == "llm":
        return fuse_llm(conversation, claims, default_region=default_region, week=week)
    raise ValueError(f"unknown fusion mode: {mode} (expected one of {FUSION_MODES})")


def fused_to_slot_dict(fused: dict[SlotKey, FusedSlot]) -> dict[SlotKey, str]:
    """Flatten FusedSlot map to (region, indicator) → value for metrics."""
    return {k: s.value for k, s in fused.items()}


def _valid_fused_value(indicator: str, value: str) -> bool:
    if indicator == "采购积极性":
        return value in {"积极", "消极", "中性"}
    if indicator == "报价松动":
        return value in {"是", "否"}
    return value in {"高", "中", "低", "上涨", "下跌", "平稳"}


def mock_fusion_from_user_prompt(user: str) -> str:
    """CI mock: collapse per-turn claims via voting-equivalent last-seen."""
    import json
    import re

    claims: list[dict[str, Any]] = []
    for line in user.splitlines():
        # - turn=3 青岛港/港存=中 (conf=0.80)
        m = re.search(
            r"turn=(\d+)\s+(\S+)/(\S+)=(\S+)\s+\(conf=([0-9.]+)\)",
            line,
        )
        if not m:
            continue
        claims.append(
            {
                "turn_index": int(m.group(1)),
                "region": m.group(2),
                "indicator": m.group(3),
                "value": m.group(4),
                "confidence": float(m.group(5)),
            }
        )
    # last-wins on parsed lines (deterministic)
    slot_map: dict[tuple[str, str], dict[str, Any]] = {}
    for c in claims:
        value = c["value"]
        if c["indicator"] == "采购积极性" and value == "中":
            value = "中性"
        if not _valid_fused_value(c["indicator"], value):
            continue
        slot_map[(c["region"], c["indicator"])] = {
            "region": c["region"],
            "indicator": c["indicator"],
            "value": value,
            "confidence": c["confidence"],
            "evidence_turns": [c["turn_index"]],
            "rationale": "mock fusion last-wins",
        }
    return json.dumps({"final_slots": list(slot_map.values())}, ensure_ascii=False)
