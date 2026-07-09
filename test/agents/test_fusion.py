"""Tests for session-level claim fusion (llm / voting / last_wins)."""

from market_truth_agent.analysis.fusion import (
    fuse_last_wins,
    fuse_session,
    fuse_voting,
    fused_to_slot_dict,
)
from market_truth_agent.models import Claim, ClaimProvenance


def _claim(region: str, indicator: str, value: str, turn: int, conf: float = 0.8) -> Claim:
    return Claim(
        claim_id=f"{turn}-{indicator}",
        source_id="U001",
        conversation_id="S001",
        time="t",
        region=region,
        market_object="铁矿石",
        indicator=indicator,
        value=value,
        claim_type="ordinal",
        provenance=ClaimProvenance(utterance="", turn_index=turn),
        extractor_confidence=conf,
    )


def test_fuse_last_wins():
    claims = [
        _claim("青岛港", "港存", "高", 1),
        _claim("青岛港", "港存", "中", 5),
        _claim("青岛港", "采购积极性", "中性", 3),
    ]
    fused = fuse_last_wins(claims)
    assert fused[("青岛港", "港存")].value == "中"
    assert fused[("青岛港", "采购积极性")].value == "中性"


def test_fuse_voting_prefers_weight():
    claims = [
        _claim("青岛港", "港存", "高", 1, 0.9),
        _claim("青岛港", "港存", "高", 2, 0.9),
        _claim("青岛港", "港存", "低", 5, 0.5),
    ]
    fused = fuse_voting(claims)
    assert fused[("青岛港", "港存")].value == "高"


def test_fuse_session_mock_modes(sample_conversation):
    claims = [
        _claim("青岛港", "港存", "中", 1),
        _claim("青岛港", "采购积极性", "中性", 3),
        _claim("青岛港", "报价松动", "否", 5),
    ]
    for mode in ("last_wins", "voting", "llm"):
        fused = fuse_session(
            sample_conversation, claims, mode=mode, default_region="青岛港", week="2026-W27"
        )
        pred = fused_to_slot_dict(fused)
        assert pred[("青岛港", "港存")] == "中"
        assert pred[("青岛港", "采购积极性")] == "中性"


def test_normalize_llm_path_no_regex_overwrite():
    """Regression: LLM 采购积极性=中性 must not be wiped by whole-utterance 还行→中."""
    from market_truth_agent.analysis.normalize import NormalizeLayer
    from market_truth_agent.recon.core import ReConThought

    layer = NormalizeLayer()
    recon = ReConThought(
        formulation="F", first_order="1", refinement="R", second_order="2",
        deception_score=0.2, signals=[],
    )
    slot = layer._item_to_slot(
        {
            "region": "青岛港",
            "indicator": "采购积极性",
            "value": "中性",
            "confidence": 0.9,
            "evidence_span": "还行",
            "normalize_rationale": "还行→中性",
        },
        utterance="采购还行，按需吧",
        default_region="青岛港",
        recon=recon,
    )
    assert slot is not None
    assert slot.value == "中性"


def test_normalize_采购_中_soft_remap():
    from market_truth_agent.analysis.normalize import NormalizeLayer
    from market_truth_agent.recon.core import ReConThought

    layer = NormalizeLayer()
    recon = ReConThought(
        formulation="F", first_order="1", refinement="R", second_order="2",
        deception_score=0.1, signals=[],
    )
    slot = layer._item_to_slot(
        {
            "region": "青岛港",
            "indicator": "采购积极性",
            "value": "中",
            "confidence": 0.8,
            "evidence_span": "一般",
        },
        utterance="采购一般",
        default_region="青岛港",
        recon=recon,
    )
    assert slot is not None
    assert slot.value == "中性"


def test_region_drift_guard():
    from market_truth_agent.analysis.normalize import NormalizeLayer
    from market_truth_agent.recon.core import ReConThought

    layer = NormalizeLayer()
    recon = ReConThought(
        formulation="F", first_order="1", refinement="R", second_order="2",
        deception_score=0.1, signals=[],
    )
    # LLM wrongly attributed to 日照港 though user never said it
    slot = layer._item_to_slot(
        {
            "region": "日照港",
            "indicator": "港存",
            "value": "中",
            "confidence": 0.8,
            "evidence_span": "那边不清楚",
        },
        utterance="那边不清楚，我们还是青岛这边",
        default_region="青岛港",
        recon=recon,
    )
    assert slot is not None
    assert slot.region == "青岛港"
