from market_truth_agent.analysis.external_validator import external_consistency
from market_truth_agent.models import Claim


def test_price_consistency_direction():
    trajectory = [{"day": 7, "price": 848, "trend": "涨"}]
    claim = Claim(
        claim_id="1", source_id="U1", conversation_id="c", time="t",
        region="青岛港", market_object="铁矿石", indicator="利润", value="上涨",
        claim_type="directional",
    )
    assert external_consistency(claim, trajectory) >= 0.9


def test_price_mismatch_low_consistency():
    trajectory = [{"day": 7, "price": 848, "trend": "涨"}]
    claim = Claim(
        claim_id="2", source_id="U1", conversation_id="c", time="t",
        region="青岛港", market_object="铁矿石", indicator="利润", value="下跌",
        claim_type="directional",
    )
    assert external_consistency(claim, trajectory) <= 0.2
