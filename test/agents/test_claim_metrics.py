from market_truth_agent.agents.eval.claim_metrics import (
    claim_f1_vs_latent,
    pearson_correlation,
    pearson_reliability_honesty,
)
from market_truth_agent.models import Claim, ClaimProvenance


def test_claim_f1_perfect_match():
    latent = [
        {"region": "青岛港", "indicator": "港存", "value": "高"},
        {"region": "青岛港", "indicator": "采购积极性", "value": "积极"},
    ]
    claims = [
        Claim(
            claim_id="1",
            source_id="U1",
            conversation_id="S1",
            time="t",
            region="青岛港",
            market_object="铁矿石",
            indicator="港存",
            value="高",
            claim_type="ordinal",
            provenance=ClaimProvenance("", 0),
        ),
        Claim(
            claim_id="2",
            source_id="U1",
            conversation_id="S1",
            time="t",
            region="青岛港",
            market_object="铁矿石",
            indicator="采购积极性",
            value="积极",
            claim_type="ordinal",
            provenance=ClaimProvenance("", 1),
        ),
    ]
    m = claim_f1_vs_latent(claims, latent)
    assert m["f1"] == 1.0
    assert m["tp"] == 2


def test_claim_f1_partial():
    latent = [{"region": "青岛港", "indicator": "港存", "value": "高"}]
    claims = [
        Claim(
            claim_id="1",
            source_id="U1",
            conversation_id="S1",
            time="t",
            region="青岛港",
            market_object="铁矿石",
            indicator="港存",
            value="低",
            claim_type="ordinal",
            provenance=ClaimProvenance("", 0),
        )
    ]
    m = claim_f1_vs_latent(claims, latent)
    assert m["tp"] == 0
    assert m["fp"] == 1
    assert m["fn"] == 1


def test_pearson():
    r = pearson_correlation([0.2, 0.5, 0.8], [0.3, 0.55, 0.85])
    assert r is not None
    assert r > 0.9


def test_pearson_reliability_honesty():
    out = pearson_reliability_honesty([
        {"honesty_gt": 0.9, "reliability_est": 0.8},
        {"honesty_gt": 0.5, "reliability_est": 0.5},
        {"honesty_gt": 0.2, "reliability_est": 0.3},
    ])
    assert out["n"] == 3
    assert out["pearson_r"] is not None
