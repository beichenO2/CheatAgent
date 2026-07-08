import inspect

from market_truth_agent.agents.customer_agent.personas import SMOKE_PERSONAS
from market_truth_agent.agents.eval.tactic_metrics import summarize_session
from market_truth_agent.agents.simulation.runner import SimulationRunner
from market_truth_agent.recon.core import ReConEngine
from market_truth_agent.models import ConversationTurn, Persona
from datetime import datetime, timezone


def test_recon_does_not_read_honesty_gt():
    """T-050: GT isolation — recon must not use persona.honesty."""
    source = inspect.getsource(ReConEngine)
    assert "persona.honesty" not in source
    assert "(1 - persona.honesty)" not in source


def test_smoke_dataset_generation(tmp_path):
    """T-060/T-061: 3 users × 20 turns."""
    runner = SimulationRunner(tmp_path / "smoke_v1", memory_root=tmp_path / "memory")
    out = runner.write_smoke_dataset(SMOKE_PERSONAS, min_turns=20)
    manifest = (out / "manifest.json").read_text(encoding="utf-8")
    assert "U001" in manifest
    assert "U002" in manifest
    assert "U003" in manifest
    for persona in SMOKE_PERSONAS:
        meta_path = out / "users" / persona.user_id / "meta.json"
        assert meta_path.exists()
        import json
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        session = meta["sessions"][0]
        assert session["turn_count"] >= 20


def test_agent_metadata_has_skill_ids(tmp_path):
    runner = SimulationRunner(tmp_path / "smoke_v1", memory_root=tmp_path / "memory")
    runner.write_smoke_dataset(SMOKE_PERSONAS[:1], min_turns=20)
    import json
    meta = json.loads((tmp_path / "smoke_v1/users/U001/meta.json").read_text(encoding="utf-8"))
    metadata = meta["sessions"][0]["agent_metadata"]
    assert len(metadata) >= 10
    assert all(m.get("skill_id") for m in metadata)


def test_tactic_metrics(tmp_path):
    runner = SimulationRunner(tmp_path / "smoke_v1", memory_root=tmp_path / "memory")
    runner.write_smoke_dataset(SMOKE_PERSONAS[:1], min_turns=20)
    import json
    meta = json.loads((tmp_path / "smoke_v1/users/U001/meta.json").read_text(encoding="utf-8"))
    summary = summarize_session(meta["sessions"][0]["agent_metadata"], ["cover-qa", "clarification-probe"])
    assert summary["skill_kind_count"] >= 1
    assert summary["skill_invoke_count"] >= 10
    assert summary["skill_richness"] >= -1e-9


def test_deception_independent_of_honesty_gt():
    """T-051: same utterance, different honesty GT → same deception."""
    engine = ReConEngine()
    turn = ConversationTurn(0, "user", "听说库存大概还可以吧", datetime.now(timezone.utc).isoformat())
    high = Persona("U1", "厂长", "谨慎型", "long", 0.9, "青岛港")
    low = Persona("U1", "厂长", "谨慎型", "long", 0.1, "青岛港")
    d_high = engine.analyze_turn(turn, high).deception_score
    engine.reset()
    d_low = engine.analyze_turn(turn, low).deception_score
    assert d_high == d_low
