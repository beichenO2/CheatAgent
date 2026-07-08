from __future__ import annotations

from market_truth_agent.models import Claim


def price_trend_at_day(trajectory: list[dict], day: int) -> str:
    for point in reversed(trajectory):
        if point["day"] <= day:
            return point.get("trend", "平")
    return trajectory[0].get("trend", "平") if trajectory else "平"


def external_consistency(claim: Claim, trajectory: list[dict], day: int = 7) -> float:
    trend = price_trend_at_day(trajectory, day)
    if claim.claim_type != "directional" and claim.indicator not in ("利润",):
        if claim.indicator in ("港存", "采购积极性", "报价松动"):
            return 0.5
        return 0.5
    mapping = {"涨": "上涨", "平": "平稳", "跌": "下跌"}
    expected = mapping.get(trend, "平稳")
    if claim.value == expected:
        return 1.0
    if claim.value in ("上涨", "下跌") and expected == "平稳":
        return 0.4
    return 0.1
