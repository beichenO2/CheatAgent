from market_truth_agent.analysis.ontology import canonicalize, normalize_value, detect_indicator


def test_canonicalize_inventory_phrase():
    val = normalize_value("港口库存很多", "港存")
    assert val == "高"


def test_detect_indicator_alias():
    assert detect_indicator("港口库存怎么样") == "港存"


def test_canonical_key_format():
    key, bucket = canonicalize("青岛港", "铁矿石", "港存", "2026-W27")
    assert key == "2026-W27|青岛港|铁矿石|港存"
    assert bucket == key
