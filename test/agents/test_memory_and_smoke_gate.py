import json
from pathlib import Path

import pytest

from market_truth_agent.agents.cheat_agent.memory import (
    load_l2_user_model,
    load_or_create_l2,
    persist_turn_memory,
)
from market_truth_agent.agents.cheat_agent.state import (
    CheatAgentState,
    KnownIdentity,
    SessionContext,
    TurnRecord,
    UserModelSnapshot,
)
from market_truth_agent.agents.eval.smoke_runner import validate_smoke_dataset


def test_l2_memory_roundtrip(tmp_path):
    model = UserModelSnapshot(
        user_id="U001",
        inferred_gaps=["港存"],
        resistance_level=0.3,
        partial_claims=["库存还可以"],
    )
    from market_truth_agent.agents.cheat_agent.memory import save_l2_user_model

    save_l2_user_model(model, tmp_path)
    loaded = load_l2_user_model("U001", tmp_path)
    assert loaded is not None
    assert loaded.inferred_gaps == ["港存"]
    assert loaded.resistance_level == 0.3


def test_persist_turn_memory_writes_l1_l2_l3(tmp_path):
    state = CheatAgentState(
        known_identity=KnownIdentity("U001", "厂长", "青岛港", "long"),
        session=SessionContext("S001", "2026-03-01", "2026-W09", {"price": 820}),
        user_model=UserModelSnapshot("U001", inferred_gaps=["港存"], resistance_level=0.5),
        conversation_history=[
            TurnRecord("user", "不对，谁说的库存高？", "2026-03-01T00:00:00Z"),
        ],
        selected_skill_id="cover-qa",
        selected_phase="RECOVER",
        agent_utterance="先跟您对齐下港口情况",
        turn_metadata={"skill_id": "cover-qa", "memory_root": str(tmp_path)},
    )
    result = persist_turn_memory(state, root=tmp_path, last_user_text="不对，谁说的库存高？")
    assert result["memory_updated"] is True
    assert (tmp_path / "users" / "U001.json").exists()
    assert (tmp_path / "sessions" / "U001" / "S001.json").exists()
    assert (tmp_path / "episodes" / "U001.jsonl").exists()


def test_smoke_gate_on_generated_dataset(tmp_path):
    from market_truth_agent.agents.customer_agent.personas import SMOKE_PERSONAS
    from market_truth_agent.agents.simulation.runner import SimulationRunner

    out = SimulationRunner(tmp_path / "smoke_v1", memory_root=tmp_path / "memory").write_smoke_dataset(
        SMOKE_PERSONAS,
        min_turns=20,
    )
    gate = validate_smoke_dataset(out)
    assert gate["passed"] is True, gate.get("failures")
