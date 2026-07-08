from market_truth_agent.analysis.truth_discovery import TruthDiscoveryEngine
from market_truth_agent.benchmark.tier_a_data import GROUND_TRUTH, TIER_A_CONFLICTS
from market_truth_agent.models import Claim, ClaimProvenance, DeceptionInfo


def test_tier_a_em_beats_majority_voting():
    engine = TruthDiscoveryEngine(iterations=5)
    claims = []
    for row in TIER_A_CONFLICTS:
        bucket = f"2026-W27|青岛港|铁矿石|{row['bucket']}"
        deception = max(0.05, 1 - row["honesty"])
        claims.append(Claim(
            claim_id=f"{row['source']}-{row['bucket']}",
            source_id=row["source"],
            conversation_id="tier_a",
            time="t",
            region="青岛港",
            market_object="铁矿石",
            indicator=row["bucket"],
            value=row["value"],
            claim_type="ordinal",
            bucket_key=bucket,
            canonical_key=bucket,
            evidence_strength=row["honesty"],
            incentive_risk=deception * 0.5,
            provenance=ClaimProvenance("x", 0),
            deception=DeceptionInfo(deception),
        ))
    truths, rel = engine.infer(claims, lambda c: 0.5)
    em_pred = {row["bucket"]: truths[f"2026-W27|青岛港|铁矿石|{row['bucket']}"].value for row in TIER_A_CONFLICTS[:2]}
    # unique buckets
    em_pred = {}
    for k, v in truths.items():
        short = k.split("|")[-1]
        em_pred[short] = v.value
    mv_pred = engine.majority_voting_baseline(claims)
    mv_short = {k.split("|")[-1]: v for k, v in mv_pred.items()}
    assert engine.bucket_error_rate(em_pred, GROUND_TRUTH) <= engine.bucket_error_rate(mv_short, GROUND_TRUTH)
