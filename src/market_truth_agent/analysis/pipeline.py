from __future__ import annotations

from market_truth_agent.analysis.claim_extractor import ClaimEnricher, ClaimExtractor
from market_truth_agent.analysis.external_validator import external_consistency
from market_truth_agent.analysis.truth_discovery import TruthDiscoveryEngine
from market_truth_agent.models import AnalysisResult, Claim, Conversation, DeceptionInfo, Persona
from market_truth_agent.recon.core import ReConEngine


class AnalysisPipeline:
    def __init__(self, price_trajectory: list[dict] | None = None) -> None:
        self.extractor = ClaimExtractor()
        self.enricher = ClaimEnricher()
        self.recon = ReConEngine()
        self.truth_engine = TruthDiscoveryEngine()
        self.price_trajectory = price_trajectory or [
            {"day": 1, "price": 820, "trend": "平"},
            {"day": 3, "price": 835, "trend": "涨"},
            {"day": 7, "price": 848, "trend": "涨"},
        ]

    def run(
        self,
        conversation: Conversation,
        persona: Persona | None = None,
        week: str = "2026-W27",
    ) -> AnalysisResult:
        self.recon.reset()
        raw_claims = self.extractor.extract_from_conversation(
            conversation, week=week, default_region=persona.region if persona else "青岛港"
        )
        claims: list[Claim] = []
        for claim in raw_claims:
            self.enricher.enrich(claim, position=persona.position if persona else "long")
            thought = self.recon.analyze_claim(claim, persona)
            claim.deception = DeceptionInfo(
                score=thought.deception_score,
                recon_reasoning=f"{thought.formulation} | {thought.refinement}",
                signals=thought.signals,
            )
            claims.append(claim)

        ext_fn = lambda c: external_consistency(c, self.price_trajectory)
        bucket_truths, reliability = self.truth_engine.infer(claims, ext_fn)

        flags = [
            c.claim_id
            for c in claims
            if c.deception and c.deception.score > 0.7 and c.incentive_risk > 0.6
        ]
        return AnalysisResult(
            claims=claims,
            bucket_truths=bucket_truths,
            user_reliability=reliability,
            escalation_flags=flags,
        )
