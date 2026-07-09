from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from market_truth_agent.analysis.ontology import (
    INDICATORS,
    ORDINAL_MAP,
    REGIONS,
    canonicalize,
    detect_all_indicators,
    detect_region,
    infer_claim_type,
    normalize_value,
)
from market_truth_agent.llm.client import normalize_model, tool_completion
from market_truth_agent.llm.prompts import build_normalize_prompt
from market_truth_agent.models import Claim, ClaimProvenance, ConversationTurn
from market_truth_agent.recon.core import ReConThought


@dataclass
class NormalizedSlot:
    region: str
    indicator: str
    value: str
    confidence: float = 0.75
    evidence_span: str = ""
    normalize_rationale: str = ""
    recon_adjusted: bool = False


@dataclass
class NormalizeResult:
    utterance: str
    turn_index: int
    slots: list[NormalizedSlot] = field(default_factory=list)
    recon_deception: float = 0.0
    recon_signals: list[str] = field(default_factory=list)


def _normalize_tool_schema() -> dict[str, Any]:
    """Strict enum schema — function calling enforces canonical values at source."""
    return {
        "type": "object",
        "properties": {
            "normalized_slots": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "region": {"type": "string", "enum": list(REGIONS)},
                        "indicator": {"type": "string", "enum": list(INDICATORS)},
                        "value": {
                            "type": "string",
                            "enum": [
                                "高", "中", "低",
                                "积极", "消极", "中性",
                                "是", "否",
                                "上涨", "下跌", "平稳",
                            ],
                        },
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "evidence_span": {"type": "string"},
                        "normalize_rationale": {"type": "string"},
                    },
                    "required": ["region", "indicator", "value", "confidence", "evidence_span"],
                },
            }
        },
        "required": ["normalized_slots"],
    }


class NormalizeLayer:
    """Context-aware translation: raw utterance + ReCon → canonical ontology slots."""

    def normalize_turn(
        self,
        turn: ConversationTurn,
        *,
        recon: ReConThought,
        conversation_context: list[dict[str, str]],
        default_region: str,
        week: str,
    ) -> NormalizeResult:
        if turn.speaker != "user":
            return NormalizeResult(utterance=turn.text, turn_index=turn.turn_index)

        system, user = build_normalize_prompt(
            utterance=turn.text,
            turn_index=turn.turn_index,
            default_region=default_region,
            week=week,
            recon={
                "deception_score": recon.deception_score,
                "signals": recon.signals,
                "first_order": recon.first_order,
                "second_order": recon.second_order,
            },
            conversation_context=conversation_context,
        )
        payload = tool_completion(
            system,
            user,
            tool_name="emit_normalized_slots",
            tool_description=(
                "输出本句 user utterance 归一化后的 canonical 槽位。"
                "只为用户本人明确断言的指标建槽；用户未表态/打太极时输出空数组。"
            ),
            parameters_schema=_normalize_tool_schema(),
            temperature=0.1,
            model=normalize_model(),
        )
        slots = self._slots_from_payload(payload, turn.text, default_region, recon)
        return NormalizeResult(
            utterance=turn.text,
            turn_index=turn.turn_index,
            slots=slots,
            recon_deception=recon.deception_score,
            recon_signals=list(recon.signals),
        )

    def _slots_from_payload(
        self,
        payload: dict[str, Any] | None,
        utterance: str,
        default_region: str,
        recon: ReConThought,
    ) -> list[NormalizedSlot]:
        if payload is None:
            return self._rule_slots(utterance, default_region, recon)
        items = payload.get("normalized_slots", [])
        if not isinstance(items, list):
            return []
        slot_map: dict[tuple[str, str], NormalizedSlot] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            slot = self._item_to_slot(item, utterance, default_region, recon)
            if slot is None:
                continue
            slot_map[(slot.region, slot.indicator)] = slot
        return list(slot_map.values())

    def _item_to_slot(
        self,
        item: dict[str, Any],
        utterance: str,
        default_region: str,
        recon: ReConThought,
    ) -> NormalizedSlot | None:
        # Trust the LLM value verbatim (function-calling enum enforced upstream).
        # NO keyword re-mapping over the full utterance — that override corrupted
        # correct LLM output (wrongway/04: 「中性」→「中」→ dropped).
        region = str(item.get("region", default_region))
        if region not in REGIONS:
            region = default_region
        # Region-drift guard: a non-default region must be spoken by the user
        # themselves, not inherited from the agent's probing about other ports.
        if region != default_region and region not in utterance:
            region = default_region
        indicator = str(item.get("indicator", ""))
        if indicator not in INDICATORS:
            return None
        value = str(item.get("value", "")).strip()
        # Soft remap common LLM slip under enum: 采购积极性 "中" → "中性"
        if indicator == "采购积极性" and value == "中":
            value = "中性"
        if not self._valid_value(indicator, value):
            return None

        confidence = float(item.get("confidence", 0.75))
        if recon.deception_score > 0.6:
            confidence = max(0.2, confidence - 0.15)
        if "rebuttal_language" in recon.signals:
            confidence = min(1.0, confidence + 0.1)

        return NormalizedSlot(
            region=region,
            indicator=indicator,
            value=value,
            confidence=min(max(confidence, 0.0), 1.0),
            evidence_span=str(item.get("evidence_span", "")),
            normalize_rationale=str(item.get("normalize_rationale", "")),
            recon_adjusted=recon.deception_score > 0.5,
        )

    @staticmethod
    def _valid_value(indicator: str, value: str) -> bool:
        if indicator == "采购积极性":
            return value in {"积极", "消极", "中性"}
        if indicator == "报价松动":
            return value in {"是", "否"}
        return value in {"高", "中", "低", "上涨", "下跌", "平稳"}

    def _rule_slots(
        self, utterance: str, default_region: str, recon: ReConThought
    ) -> list[NormalizedSlot]:
        """Deterministic fallback / mock path."""
        region = detect_region(utterance, default_region)
        slots: list[NormalizedSlot] = []
        for indicator in detect_all_indicators(utterance):
            value = normalize_value(utterance, indicator)
            if not value or not self._valid_value(indicator, value):
                continue
            conf = 0.8
            if recon.deception_score > 0.6:
                conf -= 0.15
            slots.append(
                NormalizedSlot(
                    region=region,
                    indicator=indicator,
                    value=value,
                    confidence=conf,
                    evidence_span=utterance[:40],
                    normalize_rationale="rule/mock fallback",
                )
            )
        return slots


def slots_to_claims(
    result: NormalizeResult,
    *,
    source_id: str,
    conversation_id: str,
    week: str,
    elicitation_channel: str = "direct",
) -> list[Claim]:
    """Materialize NormalizedSlot list into Claim objects."""
    utterance = result.utterance
    is_rebuttal = any(w in utterance for w in ("谁说的", "不对", "不是", "其实", "纠正"))
    channel = "bias_triggered" if is_rebuttal else elicitation_channel
    claims: list[Claim] = []
    for slot in result.slots:
        canonical_key, bucket_key = canonicalize(
            slot.region, "铁矿石", slot.indicator, week
        )
        claims.append(
            Claim(
                claim_id=str(uuid.uuid4()),
                source_id=source_id,
                conversation_id=conversation_id,
                time=datetime.now(timezone.utc).isoformat(),
                region=slot.region,
                market_object="铁矿石",
                indicator=slot.indicator,
                value=slot.value,
                claim_type=infer_claim_type(slot.indicator, slot.value),
                canonical_key=canonical_key,
                bucket_key=bucket_key,
                provenance=ClaimProvenance(
                    utterance=utterance,
                    turn_index=result.turn_index,
                    elicitation_channel=channel,
                    is_rebuttal=is_rebuttal,
                ),
                extractor_confidence=slot.confidence,
            )
        )
    return claims


def mock_normalize_from_user_prompt(user: str) -> str:
    """CI mock for Normalize layer."""
    utterance = ""
    default_region = "青岛港"
    deception = 0.2
    if "utterance:" in user:
        utterance = user.split("utterance:", 1)[1].split("\n", 1)[0].strip()
    if "default_region:" in user:
        default_region = user.split("default_region:", 1)[1].split("\n", 1)[0].strip()
    if "deception_score:" in user:
        try:
            deception = float(user.split("deception_score:", 1)[1].split("\n", 1)[0].strip())
        except ValueError:
            deception = 0.2

    layer = NormalizeLayer()
    recon = ReConThought(
        formulation="mock",
        first_order="mock",
        refinement="mock",
        second_order="mock",
        deception_score=deception,
        signals=["rebuttal_language"] if "不对" in utterance else [],
    )
    slots = layer._rule_slots(utterance, default_region, recon)
    payload = {
        "normalized_slots": [
            {
                "region": s.region,
                "indicator": s.indicator,
                "value": s.value,
                "confidence": s.confidence,
                "evidence_span": s.evidence_span,
                "normalize_rationale": s.normalize_rationale,
            }
            for s in slots
        ]
    }
    return json.dumps(payload, ensure_ascii=False)


# Re-export translation reference for docs/tests
TRANSLATION_RULES: dict[str, Any] = {
    "regions": REGIONS,
    "indicators": INDICATORS,
    "ordinal_map": ORDINAL_MAP,
    "value_sets": {
        "level": ["高", "中", "低"],
        "procurement": ["积极", "消极", "中性"],
        "quote_loosen": ["是", "否"],
        "trend": ["上涨", "下跌", "平稳"],
    },
}
