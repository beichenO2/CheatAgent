from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone

from market_truth_agent.analysis.ontology import (
    canonicalize,
    detect_indicator,
    detect_region,
    infer_claim_type,
    normalize_value,
)
from market_truth_agent.models import Claim, ClaimProvenance, Conversation, ConversationTurn


class ClaimExtractor:
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
        text = turn.text
        indicator = detect_indicator(text)
        if not indicator:
            return []
        value = normalize_value(text, indicator)
        if not value:
            return []
        region = detect_region(text, default_region)
        market_object = "铁矿石"
        canonical_key, bucket_key = canonicalize(region, market_object, indicator, week)
        is_rebuttal = any(w in text for w in ("谁说的", "不对", "不是", "其实", "纠正"))
        channel = "bias_triggered" if is_rebuttal else elicitation_channel
        claim = Claim(
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
        return [claim]

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
