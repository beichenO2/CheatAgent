from market_truth_agent.recon.core import ReConEngine
from market_truth_agent.models import ConversationTurn
from datetime import datetime, timezone


def test_recon_outputs_deception_score_in_range(sample_persona):
    engine = ReConEngine()
    turn = ConversationTurn(0, "user", "听说库存大概还可以吧", datetime.now(timezone.utc).isoformat())
    thought = engine.analyze_turn(turn, sample_persona)
    assert 0 <= thought.deception_score <= 1
    assert thought.formulation.startswith("Formulation")
    assert thought.refinement.startswith("Refinement")
    assert len(engine.history) == 1


def test_recon_history_accumulates():
    engine = ReConEngine()
    turn = ConversationTurn(0, "user", "可能吧", datetime.now(timezone.utc).isoformat())
    engine.analyze_turn(turn)
    engine.analyze_turn(turn)
    assert len(engine.history) == 2
