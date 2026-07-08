from __future__ import annotations

from collections import Counter, defaultdict

from market_truth_agent.models import BucketTruth, Claim


DEFAULT_WEIGHTS = {
    "reliability": 0.25,
    "evidence": 0.20,
    "independence": 0.15,
    "external": 0.15,
    "incentive": 0.15,
    "deception": 0.10,
}


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


class TruthDiscoveryEngine:
    def __init__(self, iterations: int = 5) -> None:
        self.iterations = iterations
        self.reliability: dict[str, float] = defaultdict(lambda: 0.5)

    def _independence(self, claim: Claim, bucket_claims: list[Claim]) -> float:
        same_conv = sum(
            1 for c in bucket_claims if c.source_id == claim.source_id
        )
        if same_conv > 1:
            return 0.5
        return 1.0

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

        bucket_truths: dict[str, BucketTruth] = {}

        for bucket_key, bucket_claims in buckets.items():
            for _ in range(self.iterations):
                value_scores: Counter[str] = Counter()
                for claim in bucket_claims:
                    r = self.reliability[claim.source_id]
                    indep = self._independence(claim, bucket_claims)
                    ext = external_consistency_fn(claim)
                    claim.claim_score = compute_claim_score(claim, r, indep, ext)
                    value_scores[claim.value] += max(claim.claim_score, 0.01)

                if not value_scores:
                    continue
                best_value, best_score = value_scores.most_common(1)[0]
                total = sum(value_scores.values()) or 1.0

                for source_id in {c.source_id for c in bucket_claims}:
                    user_claims = [c for c in bucket_claims if c.source_id == source_id]
                    if not user_claims:
                        continue
                    agree = sum(1 for c in user_claims if c.value == best_value)
                    base = agree / len(user_claims)
                    penalty = sum(c.incentive_risk + (c.deception.score if c.deception else 0) for c in user_claims)
                    penalty /= len(user_claims) * 2
                    self.reliability[source_id] = max(0.05, min(0.95, base * (1 - penalty * 0.3) + 0.1))

                bucket_truths[bucket_key] = BucketTruth(
                    bucket_key=bucket_key,
                    value=best_value,
                    confidence=best_score / total,
                    supporting_sources=[
                        c.source_id for c in bucket_claims if c.value == best_value
                    ],
                )

        return bucket_truths, dict(self.reliability)

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
