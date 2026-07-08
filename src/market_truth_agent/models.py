from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Phase(str, Enum):
    RAPPORT = "RAPPORT"
    PROBE = "PROBE"
    CHALLENGE = "CHALLENGE"
    VERIFY = "VERIFY"
    RECOVER = "RECOVER"


class ClaimType(str, Enum):
    NUMERIC = "numeric"
    DIRECTIONAL = "directional"
    ORDINAL = "ordinal"
    BINARY = "binary"


@dataclass
class ConversationTurn:
    turn_index: int
    speaker: str
    text: str
    timestamp: str
    phase: str | None = None
    tactic: str | None = None
    elicitation_goal: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    conversation_id: str
    user_id: str
    scenario: str = "iron_ore_market"
    started_at: str = ""
    turns: list[ConversationTurn] = field(default_factory=list)


@dataclass
class Persona:
    user_id: str
    role: str
    personality: str
    position: str
    honesty: float
    region: str
    knowledge_depth: float = 0.8


@dataclass
class TruthClaim:
    region: str
    indicator: str
    value: str
    market_object: str = "铁矿石"


@dataclass
class LatentState:
    scenario_id: str
    week: str
    claims_truth: list[TruthClaim]
    price_trajectory: list[dict[str, Any]]


@dataclass
class ClaimProvenance:
    utterance: str
    turn_index: int
    elicitation_channel: str = "direct"
    is_rebuttal: bool = False


@dataclass
class DeceptionInfo:
    score: float
    recon_reasoning: str = ""
    signals: list[str] = field(default_factory=list)


@dataclass
class Claim:
    claim_id: str
    source_id: str
    conversation_id: str
    time: str
    region: str
    market_object: str
    indicator: str
    value: str
    claim_type: str
    canonical_key: str = ""
    bucket_key: str = ""
    evidence_strength: float = 0.0
    stance_risk: float = 0.0
    incentive_risk: float = 0.0
    provenance: ClaimProvenance | None = None
    extractor_confidence: float = 0.0
    deception: DeceptionInfo | None = None
    claim_score: float = 0.0


@dataclass
class UserModel:
    user_id: str
    inferred_gaps: list[str] = field(default_factory=list)
    intent_layers: dict[str, str] = field(default_factory=dict)
    resistance_level: float = 0.0
    partial_claims: list[str] = field(default_factory=list)


@dataclass
class BucketTruth:
    bucket_key: str
    value: str
    confidence: float
    supporting_sources: list[str] = field(default_factory=list)


@dataclass
class AnalysisResult:
    claims: list[Claim]
    bucket_truths: dict[str, BucketTruth]
    user_reliability: dict[str, float]
    escalation_flags: list[str] = field(default_factory=list)
