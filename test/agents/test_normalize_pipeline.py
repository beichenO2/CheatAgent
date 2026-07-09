from market_truth_agent.agents.eval.analysis_metrics import (
    evaluate_session,
    run_ablation_suite,
    slot_metrics,
)
from market_truth_agent.analysis.normalize import NormalizeLayer, slots_to_claims
from market_truth_agent.analysis.pipeline import AnalysisPipeline, PipelineConfig
from market_truth_agent.models import ConversationTurn
from market_truth_agent.recon.core import ReConEngine, ReConThought


def test_normalize_layer_mock():
    layer = NormalizeLayer()
    recon = ReConThought(
        formulation="F",
        first_order="一阶",
        refinement="R",
        second_order="二阶",
        deception_score=0.3,
        signals=[],
    )
    turn = ConversationTurn(1, "user", "青岛港港存偏高，采购还可以。", "ts")
    result = layer.normalize_turn(
        turn,
        recon=recon,
        conversation_context=[{"speaker": "agent", "text": "港存怎么样？"}],
        default_region="青岛港",
        week="2026-W27",
    )
    assert len(result.slots) >= 1
    claims = slots_to_claims(
        result, source_id="U1", conversation_id="S1", week="2026-W27"
    )
    assert claims[0].indicator in ("港存", "采购积极性")
    assert claims[0].value in ("高", "中", "低", "积极", "消极", "中性")


def test_pipeline_recon_before_normalize(sample_conversation, sample_persona):
    pipeline = AnalysisPipeline(config=PipelineConfig(enable_normalize=True))
    result = pipeline.run(sample_conversation, sample_persona)
    assert len(result.claims) >= 1
    assert result.claims[0].deception is not None
    meta = pipeline.last_run_meta
    assert meta is not None
    assert meta.enable_normalize is True
    assert len(meta.turn_traces) >= 1
    assert meta.turn_traces[0].recon is not None


def test_ablate_normalize(sample_conversation, sample_persona):
    full = AnalysisPipeline(config=PipelineConfig(enable_normalize=True))
    ablated = AnalysisPipeline(config=PipelineConfig(enable_normalize=False))
    r_full = full.run(sample_conversation, sample_persona)
    r_ab = ablated.run(sample_conversation, sample_persona)
    assert full.last_run_meta.enable_normalize is True
    assert ablated.last_run_meta.enable_normalize is False
    assert isinstance(r_full.claims, list)
    assert isinstance(r_ab.claims, list)


def test_ablate_turns(sample_conversation, sample_persona):
    short = AnalysisPipeline(config=PipelineConfig(enable_normalize=True, max_turns=4))
    full = AnalysisPipeline(config=PipelineConfig(enable_normalize=True))
    r_short = short.run(sample_conversation, sample_persona)
    r_full = full.run(sample_conversation, sample_persona)
    assert len(r_short.claims) <= len(r_full.claims)


def test_slot_metrics_recall_precision():
    from market_truth_agent.models import Claim, ClaimProvenance

    latent = [{"region": "青岛港", "indicator": "港存", "value": "高"}]
    claims = [
        Claim(
            claim_id="1", source_id="U", conversation_id="S", time="t",
            region="青岛港", market_object="铁矿石", indicator="港存", value="高",
            claim_type="ordinal", provenance=ClaimProvenance("", 0),
        )
    ]
    m = slot_metrics(claims, latent)
    assert m["slot_recall"] == 1.0
    assert m["prediction_accuracy"] == 1.0


def test_ablation_suite_runs(sample_conversation, sample_persona):
    latent = [{"region": "青岛港", "indicator": "港存", "value": "高"}]
    out = run_ablation_suite(
        sample_conversation,
        sample_persona,
        latent,
        week="2026-W27",
        price_trajectory=[{"day": 1, "price": 820, "trend": "平"}],
        turn_limits=[4, 8],
    )
    names = {a["variant"] for a in out["ablations"]}
    assert "full" in names
    assert "ablate_normalize" in names
    assert "turns_4" in names
