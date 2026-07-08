from market_truth_agent.agents.eval.tactic_metrics import (
    skill_coverage,
    skill_invoke_count,
    skill_kind_count,
    skill_richness,
    summarize_session,
)


def test_skill_metrics():
    metadata = [
        {"skill_id": "cover-qa"},
        {"skill_id": "cover-qa"},
        {"skill_id": "reactance-biased-statement"},
    ]
    assert skill_kind_count(metadata) == 2
    assert skill_invoke_count(metadata) == 3
    assert skill_richness(metadata) > 0
    assert skill_coverage(metadata, ["cover-qa", "va-detail-chase"]) == 0.5
    summary = summarize_session(metadata, ["cover-qa", "reactance-biased-statement", "va-detail-chase"])
    assert summary["skill_kind_count"] == 2
