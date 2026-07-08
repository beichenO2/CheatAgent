from market_truth_agent.analysis.truth_discovery import TruthDiscoveryEngine, compute_claim_score
from market_truth_agent.models import Claim, ClaimProvenance, DeceptionInfo


def _claim(source, bucket, value, incentive=0.2, deception=0.1):
    return Claim(
        claim_id=source + value,
        source_id=source,
        conversation_id="c",
        time="t",
        region="青岛港",
        market_object="铁矿石",
        indicator="港存",
        value=value,
        claim_type="ordinal",
        bucket_key=bucket,
        canonical_key=bucket,
        evidence_strength=0.6,
        incentive_risk=incentive,
        provenance=ClaimProvenance("x", 0),
        deception=DeceptionInfo(deception),
    )


def test_em_prefers_honest_sources():
    engine = TruthDiscoveryEngine(iterations=5)
    bucket = "2026-W27|青岛港|铁矿石|港存"
    claims = [
        _claim("honest1", bucket, "高", incentive=0.1, deception=0.05),
        _claim("honest2", bucket, "高", incentive=0.1, deception=0.05),
        _claim("liar", bucket, "低", incentive=0.8, deception=0.7),
    ]
    truths, rel = engine.infer(claims, lambda c: 0.5)
    assert truths[bucket].value == "高"
    assert rel["honest1"] > rel["liar"]


def test_em_error_leq_mv_error():
    engine = TruthDiscoveryEngine(iterations=5)
    bucket = "2026-W27|青岛港|铁矿石|港存"
    claims = [
        _claim("s1", bucket, "高"),
        _claim("s2", bucket, "高"),
        _claim("s3", bucket, "低", incentive=0.7, deception=0.6),
    ]
    truths, _ = engine.infer(claims, lambda c: 0.5)
    em_pred = {bucket: truths[bucket].value}
    mv_pred = engine.majority_voting_baseline(claims)
    gt = {bucket: "高"}
    assert engine.bucket_error_rate(em_pred, gt) <= engine.bucket_error_rate(mv_pred, gt)


def test_claim_score_formula():
    claim = _claim("s1", "b", "高")
    score = compute_claim_score(claim, reliability=0.8, independence=1.0, external_consistency=0.5)
    assert isinstance(score, float)
