from market_truth_agent.agents.customer_agent.personas import ALPHA_PERSONAS
from market_truth_agent.agents.eval.smoke_runner import validate_smoke_dataset
from market_truth_agent.agents.simulation.runner import SimulationRunner


def test_alpha_dataset_structure(tmp_path):
    runner = SimulationRunner(
        tmp_path / "alpha_v1",
        memory_root=tmp_path / "memory",
    )
    # Mini alpha: first 2 users, 2 sessions, 6 turns for speed
    mini = ALPHA_PERSONAS[:2]
    out = runner.write_dataset(mini, version="alpha_v1", min_turns=6, sessions_per_user=2)
    gate = validate_smoke_dataset(out, min_turns=6, min_users=2, sessions_per_user=2)
    assert gate["passed"] is True, gate.get("failures")
