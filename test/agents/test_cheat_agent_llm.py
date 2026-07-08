import inspect

import pytest

from market_truth_agent.agents.cheat_agent.graph import (
    build_cheat_agent_graph,
    invoke_skill,
    run_cheat_agent_turn,
)
from market_truth_agent.agents.cheat_agent.state import (
    KnownIdentity,
    SessionContext,
    TurnRecord,
    UserModelSnapshot,
)
from market_truth_agent.agents.customer_agent.graph import CustomerAgentState, CustomerPersona
from market_truth_agent.agents.customer_agent.graph import run_customer_agent_turn
from market_truth_agent.llm.prompts import build_cheat_agent_prompt, load_skill_markdown


def test_build_cheat_agent_graph_compiles():
    graph = build_cheat_agent_graph()
    assert graph is not None


def test_invoke_skill_loads_skill_file():
    state = __import__(
        "market_truth_agent.agents.cheat_agent.state", fromlist=["CheatAgentState"]
    ).CheatAgentState(
        known_identity=KnownIdentity("U001", "厂长", "青岛港", "long"),
        session=SessionContext("S001", "2026-03-01", "2026-W09", {"price": 820, "trend": "平"}),
        user_model=UserModelSnapshot("U001"),
        selected_skill_id="clarification-probe",
        selected_phase="RAPPORT",
    )
    result = invoke_skill(state)
    assert result["agent_utterance"]
    assert result["turn_metadata"]["skill_id"] == "clarification-probe"
    assert result["turn_metadata"]["skill_file"].endswith("SKILL-clarification-probe.md")


def test_cheat_agent_prompt_excludes_honesty_gt():
    skill_md = load_skill_markdown("cover-qa")
    system, user = build_cheat_agent_prompt(
        skill_id="cover-qa",
        skill_markdown=skill_md,
        phase="RECOVER",
        known_identity={"role": "厂长", "region": "青岛港", "position": "long"},
        session={"session_date": "2026-03-01", "turn_count": 1, "price_snapshot": {"price": 820}},
        user_model={"inferred_gaps": [], "partial_claims": [], "resistance_level": 0.7},
        conversation_history=[],
    )
    combined = system + user
    assert "honesty:" not in combined
    assert "0.85" not in combined
    assert "persona.honesty" not in combined


def test_single_turn_dialogue_mock_llm():
    known = KnownIdentity("U001", "厂长", "青岛港", "long", "谨慎型")
    session = SessionContext("S001", "2026-03-01", "2026-W09", {"price": 820, "trend": "平"})
    user_model = UserModelSnapshot("U001")

    utterance, meta = run_cheat_agent_turn(
        known_identity=known,
        session=session,
        user_model=user_model,
        conversation_history=[],
    )
    assert utterance
    assert meta.get("skill_id")

    persona = CustomerPersona(
        user_id="U001",
        role="厂长",
        region="青岛港",
        position="long",
        personality="谨慎型",
        honesty=0.85,
    )
    reply = run_customer_agent_turn(
        CustomerAgentState(
            persona=persona,
            latent_claims_truth=[
                {"region": "青岛港", "indicator": "港存", "value": "高", "market_object": "铁矿石"}
            ],
            price_snapshot={"price": 820, "trend": "平"},
            cheat_agent_utterance=utterance,
            conversation_history=[{"speaker": "agent", "text": utterance}],
        )
    )
    assert reply
    assert persona.user_id not in reply or "U001" not in reply


def test_invoke_skill_source_uses_llm_not_template():
    source = inspect.getsource(invoke_skill)
    assert "chat_completion" in source
    assert "load_skill_markdown" in source
    assert "想了解下您这边最近经营情况" not in source
