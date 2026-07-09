from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from market_truth_agent.models import BucketTruth, Claim


DEFAULT_WEIGHTS = {
    "reliability": 0.25,
    "evidence": 0.20,
    "independence": 0.15,
    "external": 0.15,
    "incentive": 0.15,
    "deception": 0.10,
}

# Mildly skeptical prior: mean = α/(α+β) = 0.5
_DEFAULT_ALPHA = 2.0
_DEFAULT_BETA = 2.0


def compute_claim_score(
    claim: Claim,
    reliability: float,
    independence: float,
    external_consistency: float,
    weights: dict[str, float] | None = None,
) -> float:
    w = weights or DEFAULT_WEIGHTS
    deception = claim.deception.score if claim.deception else 0.0
    score = (
        w["reliability"] * reliability
        + w["evidence"] * claim.evidence_strength
        + w["independence"] * independence
        + w["external"] * external_consistency
        - w["incentive"] * claim.incentive_risk
        - w["deception"] * deception
    )
    return score


def majority_vote(values: list[str]) -> str:
    if not values:
        return ""
    return Counter(values).most_common(1)[0][0]


@dataclass
class BetaPosterior:
    """Beta(α, β) over source reliability; mean = α/(α+β)."""

    alpha: float = _DEFAULT_ALPHA
    beta: float = _DEFAULT_BETA

    @property
    def mean(self) -> float:
        return self.alpha / (self.alpha + self.beta)

    def update(self, successes: float, failures: float) -> None:
        self.alpha += max(0.0, successes)
        self.beta += max(0.0, failures)


class TruthDiscoveryEngine:
    """Heuristic EM with Beta reliability prior.

    Key guard (Readme §票权): when a bucket has only one distinct source_id,
    do NOT update that source's reliability — agreement with self is not evidence.
    """

    def __init__(
        self,
        iterations: int = 5,
        *,
        prior_alpha: float = _DEFAULT_ALPHA,
        prior_beta: float = _DEFAULT_BETA,
    ) -> None:
        self.iterations = iterations
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self._posteriors: dict[str, BetaPosterior] = {}
        # Public view kept for callers that read engine.reliability[source]
        self.reliability: dict[str, float] = defaultdict(self._prior_mean)

    def _prior_mean(self) -> float:
        return self.prior_alpha / (self.prior_alpha + self.prior_beta)

    def _posterior(self, source_id: str) -> BetaPosterior:
        if source_id not in self._posteriors:
            self._posteriors[source_id] = BetaPosterior(self.prior_alpha, self.prior_beta)
            self.reliability[source_id] = self._posteriors[source_id].mean
        return self._posteriors[source_id]

    def _sync_reliability(self, source_id: str) -> float:
        mean = self._posterior(source_id).mean
        self.reliability[source_id] = mean
        return mean

    def _independence(self, claim: Claim, bucket_claims: list[Claim]) -> float:
        same_conv = sum(1 for c in bucket_claims if c.source_id == claim.source_id)
        if same_conv > 1:
            return 0.5
        return 1.0

    @staticmethod
    def _distinct_sources(bucket_claims: list[Claim]) -> set[str]:
        return {c.source_id for c in bucket_claims}

    def _update_reliability_from_bucket(
        self,
        bucket_claims: list[Claim],
        best_value: str,
    ) -> None:
        sources = self._distinct_sources(bucket_claims)
        # Single-source bucket: no cross-check → keep prior (do not update).
        if len(sources) < 2:
            return

        for source_id in sources:
            user_claims = [c for c in bucket_claims if c.source_id == source_id]
            if not user_claims:
                continue
            agree = sum(1 for c in user_claims if c.value == best_value)
            disagree = len(user_claims) - agree
            # Soften with incentive/deception: lying-aligned claims count less as success
            penalty = sum(
                c.incentive_risk + (c.deception.score if c.deception else 0.0)
                for c in user_claims
            ) / (len(user_claims) * 2)
            success_mass = agree * (1.0 - 0.3 * penalty)
            failure_mass = disagree + agree * (0.3 * penalty)
            post = self._posterior(source_id)
            post.update(success_mass, failure_mass)
            self._sync_reliability(source_id)

    def infer(
        self,
        claims: list[Claim],
        external_consistency_fn,
    ) -> tuple[dict[str, BucketTruth], dict[str, float]]:
        if not claims:
            return {}, {}

        buckets: dict[str, list[Claim]] = defaultdict(list)
        for c in claims:
            buckets[c.bucket_key].append(c)
            self._posterior(c.source_id)  # ensure prior registered

        bucket_truths: dict[str, BucketTruth] = {}

        for bucket_key, bucket_claims in buckets.items():
            for _ in range(self.iterations):
                value_scores: Counter[str] = Counter()
                for claim in bucket_claims:
                    r = self._sync_reliability(claim.source_id)
                    indep = self._independence(claim, bucket_claims)
                    ext = external_consistency_fn(claim)
                    claim.claim_score = compute_claim_score(claim, r, indep, ext)
                    value_scores[claim.value] += max(claim.claim_score, 0.01)

                if not value_scores:
                    continue
                best_value, best_score = value_scores.most_common(1)[0]
                total = sum(value_scores.values()) or 1.0

                self._update_reliability_from_bucket(bucket_claims, best_value)

                bucket_truths[bucket_key] = BucketTruth(
                    bucket_key=bucket_key,
                    value=best_value,
                    confidence=best_score / total,
                    supporting_sources=[
                        c.source_id for c in bucket_claims if c.value == best_value
                    ],
                )

        return bucket_truths, {sid: self._sync_reliability(sid) for sid in self._posteriors}

    def majority_voting_baseline(self, claims: list[Claim]) -> dict[str, str]:
        buckets: dict[str, list[str]] = defaultdict(list)
        for c in claims:
            buckets[c.bucket_key].append(c.value)
        return {k: majority_vote(v) for k, v in buckets.items()}

    def bucket_error_rate(
        self, predicted: dict[str, str], ground_truth: dict[str, str]
    ) -> float:
        if not ground_truth:
            return 0.0
        errors = sum(1 for k, v in ground_truth.items() if predicted.get(k) != v)
        return errors / len(ground_truth)
