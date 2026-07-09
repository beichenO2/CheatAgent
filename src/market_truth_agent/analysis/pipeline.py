from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from market_truth_agent.analysis.claim_extractor import ClaimExtractor
from market_truth_agent.analysis.claim_extractor import ClaimEnricher
from market_truth_agent.analysis.external_validator import external_consistency
from market_truth_agent.analysis.normalize import NormalizeLayer, slots_to_claims
from market_truth_agent.analysis.truth_discovery import TruthDiscoveryEngine
from market_truth_agent.models import (
    AnalysisResult,
    Claim,
    Conversation,
    ConversationTurn,
    DeceptionInfo,
    Persona,
)
from market_truth_agent.recon.core import ReConEngine, ReConThought
from market_truth_agent.utils.progress import progress


@dataclass
class PipelineConfig:
    enable_normalize: bool = True
    max_turns: int | None = None


@dataclass
class TurnTrace:
    turn_index: int
    utterance: str
    recon: ReConThought | None = None
    normalize_slot_count: int = 0
    claim_count: int = 0


@dataclass
class PipelineRunMeta:
    enable_normalize: bool = True
    max_turns: int | None = None
    turn_traces: list[TurnTrace] = field(default_factory=list)
    mean_deception: float = 0.0


class AnalysisPipeline:
    """
    Analysis chain (Readme / ADR-009):

    RAW user turn → ReCon → Normalize → Claim → Enricher → Truth Discovery
    """

    def __init__(
        self,
        price_trajectory: list[dict] | None = None,
        *,
        config: PipelineConfig | None = None,
    ) -> None:
        self.config = config or PipelineConfig()
        self.recon = ReConEngine()
        self.normalize = NormalizeLayer()
        self.legacy_extractor = ClaimExtractor(use_llm=True)
        self.enricher = ClaimEnricher()
        self.truth_engine = TruthDiscoveryEngine()
        self.price_trajectory = price_trajectory or [
            {"day": 1, "price": 820, "trend": "平"},
            {"day": 3, "price": 835, "trend": "涨"},
            {"day": 7, "price": 848, "trend": "涨"},
        ]
        self.last_run_meta: PipelineRunMeta | None = None

    def run(
        self,
        conversation: Conversation,
        persona: Persona | None = None,
        week: str = "2026-W27",
    ) -> AnalysisResult:
        self.recon.reset()
        default_region = persona.region if persona else "青岛港"
        turns = self._select_turns(conversation.turns)
        context_window: list[dict[str, str]] = []
        claims: list[Claim] = []
        traces: list[TurnTrace] = []
        deception_scores: list[float] = []

        user_turns = [t for t in turns if t.speaker == "user"]
        user_turn_num = 0
        for turn in turns:
            if turn.speaker != "user":
                context_window.append({"speaker": turn.speaker, "text": turn.text})
                continue

            user_turn_num += 1
            progress(
                f"[pipeline] {conversation.user_id} user turn "
                f"{user_turn_num}/{len(user_turns)} idx={turn.turn_index} "
                f"normalize={'on' if self.config.enable_normalize else 'off'}"
            )
            thought = self.recon.analyze_turn(turn, persona)
            deception_scores.append(thought.deception_score)

            if self.config.enable_normalize:
                norm = self.normalize.normalize_turn(
                    turn,
                    recon=thought,
                    conversation_context=context_window[-8:],
                    default_region=default_region,
                    week=week,
                )
                turn_claims = slots_to_claims(
                    norm,
                    source_id=conversation.user_id,
                    conversation_id=conversation.conversation_id,
                    week=week,
                )
                trace = TurnTrace(
                    turn_index=turn.turn_index,
                    utterance=turn.text,
                    recon=thought,
                    normalize_slot_count=len(norm.slots),
                    claim_count=len(turn_claims),
                )
            else:
                turn_claims = self.legacy_extractor.extract_from_turn(
                    turn,
                    source_id=conversation.user_id,
                    conversation_id=conversation.conversation_id,
                    week=week,
                    default_region=default_region,
                )
                trace = TurnTrace(
                    turn_index=turn.turn_index,
                    utterance=turn.text,
                    recon=thought,
                    normalize_slot_count=0,
                    claim_count=len(turn_claims),
                )

            for claim in turn_claims:
                self.enricher.enrich(claim, position=persona.position if persona else "long")
                claim.deception = DeceptionInfo(
                    score=thought.deception_score,
                    recon_reasoning=f"{thought.formulation} | {thought.refinement}",
                    signals=thought.signals,
                )
                claims.append(claim)

            traces.append(trace)
            context_window.append({"speaker": turn.speaker, "text": turn.text})

        ext_fn = lambda c: external_consistency(c, self.price_trajectory)
        bucket_truths, reliability = self.truth_engine.infer(claims, ext_fn)

        flags = [
            c.claim_id
            for c in claims
            if c.deception and c.deception.score > 0.7 and c.incentive_risk > 0.6
        ]

        self.last_run_meta = PipelineRunMeta(
            enable_normalize=self.config.enable_normalize,
            max_turns=self.config.max_turns,
            turn_traces=traces,
            mean_deception=(
                sum(deception_scores) / len(deception_scores) if deception_scores else 0.0
            ),
        )

        return AnalysisResult(
            claims=claims,
            bucket_truths=bucket_truths,
            user_reliability=reliability,
            escalation_flags=flags,
        )

    def _select_turns(self, turns: list[ConversationTurn]) -> list[ConversationTurn]:
        if self.config.max_turns is None:
            return turns
        return turns[: self.config.max_turns]
