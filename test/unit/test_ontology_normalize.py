from market_truth_agent.analysis.ontology import normalize_value


def test_normalize_hai_keyi():
    assert normalize_value("我们这边港口情况还可以", "港存") == "中"
