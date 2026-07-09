from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone

from market_truth_agent.analysis.ontology import (
    INDICATORS,
    REGIONS,
    canonicalize,
    detect_all_indicators,
    detect_region,
    infer_claim_type,
    normalize_value,
)
from market_truth_agent.llm.client import chat_completion, extract_json_object, llm_mode
from market_truth_agent.llm.prompts import build_claim_extraction_prompt
from market_truth_agent.models import Claim, ClaimProvenance, Conversation, ConversationTurn


class ClaimExtractor:
    """LLM-first claim extraction with ontology validation; rules only as mock/fallback."""

    def __init__(self, *, use_llm: bool | None = None) -> None:
        self.use_llm = use_llm if use_llm is not None else True

    def extract_from_turn(
        self,
        turn: ConversationTurn,
        *,
        source_id: str,
        conversation_id: str,
        week: str = "2026-W27",
        default_region: str = "青岛港",
        elicitation_channel: str = "direct",
    ) -> list[Claim]:
        if turn.speaker != "user":
            return []
        if self.use_llm:
            claims = self._extract_llm(
                turn,
                source_id=source_id,
                conversation_id=conversation_id,
                week=week,
                default_region=default_region,
                elicitation_channel=elicitation_channel,
            )
            if claims:
                return claims
        return self._extract_rules(
            turn,
            source_id=source_id,
            conversation_id=conversation_id,
            week=week,
            default_region=default_region,
            elicitation_channel=elicitation_channel,
        )

    def _extract_llm(
        self,
        turn: ConversationTurn,
        *,
        source_id: str,
        conversation_id: str,
        week: str,
        default_region: str,
        elicitation_channel: str,
    ) -> list[Claim]:
        system, user = build_claim_extraction_prompt(
            utterance=turn.text,
            turn_index=turn.turn_index,
            default_region=default_region,
            week=week,
        )
        raw = chat_completion(system, user, temperature=0.1)
        try:
            payload = extract_json_object(raw)
        except json.JSONDecodeError:
            return []
        items = payload.get("claims", [])
        if not isinstance(items, list):
            return []
        return self._claims_from_payload(
            items,
            turn=turn,
            source_id=source_id,
            conversation_id=conversation_id,
            week=week,
            default_region=default_region,
            elicitation_channel=elicitation_channel,
        )

    def _claims_from_payload(
        self,
        items: list[dict],
        *,
        turn: ConversationTurn,
        source_id: str,
        conversation_id: str,
        week: str,
        default_region: str,
        elicitation_channel: str,
    ) -> list[Claim]:
        text = turn.text
        claims: list[Claim] = []
        slot_seen: dict[tuple[str, str], Claim] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            region = str(item.get("region", default_region))
            if region not in REGIONS:
                region = detect_region(text, default_region)
            indicator = str(item.get("indicator", ""))
            if indicator not in INDICATORS:
                continue
            value = str(item.get("value", ""))
            normalized = normalize_value(text, indicator)
            if normalized:
                value = normalized
            elif not value:
                continue
            if indicator == "采购积极性" and value not in {"积极", "消极", "中性"}:
                continue
            if indicator == "报价松动" and value not in {"是", "否"}:
                continue
            if indicator not in {"采购积极性", "报价松动"} and value not in {
                "高", "中", "低", "上涨", "下跌", "平稳",
            }:
                continue
            is_rebuttal = bool(item.get("is_rebuttal")) or any(
                w in text for w in ("谁说的", "不对", "不是", "其实", "纠正")
            )
            channel = "bias_triggered" if is_rebuttal else elicitation_channel
            confidence = float(item.get("confidence", 0.75))
            canonical_key, bucket_key = canonicalize(region, "铁矿石", indicator, week)
            claim = Claim(
                claim_id=str(uuid.uuid4()),
                source_id=source_id,
                conversation_id=conversation_id,
                time=turn.timestamp or datetime.now(timezone.utc).isoformat(),
                region=region,
                market_object="铁矿石",
                indicator=indicator,
                value=value,
                claim_type=infer_claim_type(indicator, value),
                canonical_key=canonical_key,
                bucket_key=bucket_key,
                provenance=ClaimProvenance(
                    utterance=text,
                    turn_index=turn.turn_index,
                    elicitation_channel=channel,
                    is_rebuttal=is_rebuttal,
                ),
                extractor_confidence=min(max(confidence, 0.0), 1.0),
            )
            slot_seen[(region, indicator)] = claim
        return list(slot_seen.values())

    def _extract_rules(
        self,
        turn: ConversationTurn,
        *,
        source_id: str,
        conversation_id: str,
        week: str,
        default_region: str,
        elicitation_channel: str,
    ) -> list[Claim]:
        text = turn.text
        region = detect_region(text, default_region)
        market_object = "铁矿石"
        is_rebuttal = any(w in text for w in ("谁说的", "不对", "不是", "其实", "纠正"))
        channel = "bias_triggered" if is_rebuttal else elicitation_channel
        claims: list[Claim] = []
        for indicator in detect_all_indicators(text):
            value = normalize_value(text, indicator)
            if not value:
                continue
            canonical_key, bucket_key = canonicalize(region, market_object, indicator, week)
            claims.append(
                Claim(
                    claim_id=str(uuid.uuid4()),
                    source_id=source_id,
                    conversation_id=conversation_id,
                    time=turn.timestamp or datetime.now(timezone.utc).isoformat(),
                    region=region,
                    market_object=market_object,
                    indicator=indicator,
                    value=value,
                    claim_type=infer_claim_type(indicator, value),
                    canonical_key=canonical_key,
                    bucket_key=bucket_key,
                    provenance=ClaimProvenance(
                        utterance=text,
                        turn_index=turn.turn_index,
                        elicitation_channel=channel,
                        is_rebuttal=is_rebuttal,
                    ),
                    extractor_confidence=0.85,
                )
            )
        return claims

    def extract_from_conversation(
        self, conversation: Conversation, week: str = "2026-W27", default_region: str = "青岛港"
    ) -> list[Claim]:
        claims: list[Claim] = []
        for turn in conversation.turns:
            claims.extend(
                self.extract_from_turn(
                    turn,
                    source_id=conversation.user_id,
                    conversation_id=conversation.conversation_id,
                    week=week,
                    default_region=default_region,
                )
            )
        return claims


def mock_claims_from_user_prompt(user: str) -> str:
    """Deterministic mock LLM response for claim extraction (CI)."""
    utterance = ""
    turn_index = 0
    default_region = "青岛港"
    week = "2026-W27"
    if "utterance:" in user:
        utterance = user.split("utterance:", 1)[1].split("\n", 1)[0].strip()
    if "turn_index:" in user:
        try:
            turn_index = int(user.split("turn_index:", 1)[1].split("\n", 1)[0].strip())
        except ValueError:
            turn_index = 0
    if "default_region:" in user:
        default_region = user.split("default_region:", 1)[1].split("\n", 1)[0].strip()
    if "week:" in user:
        week = user.split("week:", 1)[1].split("\n", 1)[0].strip()

    extractor = ClaimExtractor(use_llm=False)
    turn = ConversationTurn(turn_index, "user", utterance, datetime.now(timezone.utc).isoformat())
    claims = extractor._extract_rules(
        turn,
        source_id="mock",
        conversation_id="mock",
        week=week,
        default_region=default_region,
        elicitation_channel="direct",
    )
    payload = {
        "claims": [
            {
                "region": c.region,
                "indicator": c.indicator,
                "value": c.value,
                "confidence": c.extractor_confidence,
                "is_rebuttal": c.provenance.is_rebuttal if c.provenance else False,
            }
            for c in claims
        ]
    }
    return json.dumps(payload, ensure_ascii=False)


def score_evidence_strength(text: str) -> float:
    score = 0.3
    if re.search(r"\d+", text):
        score += 0.35
    if any(w in text for w in ("万吨", "吨", "昨天", "上周", "本月")):
        score += 0.2
    if any(w in text for w in ("青岛港", "日照港", "唐山", "我们厂", "我这边")):
        score += 0.15
    return min(score, 1.0)


def score_incentive_risk(value: str, indicator: str, position: str = "long") -> float:
    if position != "long":
        return 0.2
    bullish = {
        ("港存", "低"), ("采购积极性", "积极"), ("报价松动", "否"),
        ("利润", "高"), ("发运", "高"),
    }
    bearish = {
        ("港存", "高"), ("采购积极性", "消极"), ("报价松动", "是"),
        ("利润", "低"),
    }
    pair = (indicator, value)
    if pair in bullish:
        return 0.7
    if pair in bearish:
        return 0.1
    return 0.3


class ClaimEnricher:
    def enrich(self, claim: Claim, *, position: str = "long") -> Claim:
        utterance = claim.provenance.utterance if claim.provenance else ""
        claim.evidence_strength = score_evidence_strength(utterance)
        claim.incentive_risk = score_incentive_risk(claim.value, claim.indicator, position)
        claim.stance_risk = claim.incentive_risk
        return claim
