import inspect

import pytest

from market_truth_agent.agents.cheat_agent.router import route_skill, route_skill_rules
from market_truth_agent.agents.cheat_agent.state import (
    CheatAgentState,
    KnownIdentity,
    SessionContext,
    TurnRecord,
    UserModelSnapshot,
)
from market_truth_agent.agents.customer_agent.graph import build_customer_agent_graph
from market_truth_agent.analysis.claim_extractor import ClaimExtractor
from market_truth_agent.llm.prompts import build_claim_extraction_prompt, build_recon_prompt, build_router_prompt
from market_truth_agent.models import ConversationTurn
from market_truth_agent.recon.core import ReConEngine


def test_route_skill_llm_mock_returns_valid_skill():
    state = CheatAgentState(
        known_identity=KnownIdentity("U001", "厂长", "青岛港", "long"),
        session=SessionContext("S001", "2026-03-01", "2026-W09", {"price": 820, "trend": "平"}),
        user_model=UserModelSnapshot("U001", resistance_level=0.7),
        conversation_history=[],
    )
    result = route_skill(state)
    assert result["selected_skill_id"] == "cover-qa"
    assert result["selected_phase"] == "RECOVER"
    assert result["turn_metadata"].get("router_source") in {"mock-llm", "live", "rule-fallback"}


def test_graph_route_skill_delegates_to_llm_router():
    from market_truth_agent.agents.cheat_agent import router as router_mod

    assert hasattr(router_mod, "route_skill")
    assert "chat_completion" in inspect.getsource(router_mod.route_skill)


def test_claim_extractor_llm_mock():
    extractor = ClaimExtractor(use_llm=True)
    turn = ConversationTurn(1, "user", "青岛港港存中等，采购积极性一般，报价还没松动。", "ts")
    claims = extractor.extract_from_turn(turn, source_id="U1", conversation_id="S1")
    indicators = {c.indicator for c in claims}
    assert "港存" in indicators
    assert len(claims) >= 2


def test_recon_llm_mock(sample_persona):
    engine = ReConEngine()
    turn = ConversationTurn(0, "user", "听说库存大概还可以吧", "ts")
    thought = engine.analyze_turn(turn, sample_persona)
    assert 0 <= thought.deception_score <= 1
    assert thought.formulation.startswith("Formulation")
    assert thought.refinement.startswith("Refinement")


def test_build_customer_agent_graph_compiles():
    graph = build_customer_agent_graph()
    assert graph is not None


def test_router_prompt_excludes_honesty():
    system, user = build_router_prompt(
        router_markdown="# router",
        registered_skills=["cover-qa"],
        router_input={"inferred_gaps": [], "partial_claims": [], "resistance_level": 0.1, "turn_count": 1},
    )
    assert "honesty" not in (system + user).lower() or "禁止" in system


def test_claim_and_recon_prompts_exist():
    s, u = build_claim_extraction_prompt(utterance="港存高", turn_index=0, default_region="青岛港", week="W1")
    assert "ClaimExtractor" in s
    s2, u2 = build_recon_prompt(utterance="可能吧", persona_context={"region": "青岛港"}, history=[])
    assert "ReCon" in s2


def test_route_skill_rules_high_resistance():
    route = route_skill_rules(
        inferred_gaps=[],
        partial_claims=[],
        resistance_level=0.8,
        turn_count=3,
        last_user="",
        has_price=True,
    )
    assert route["skill_id"] == "cover-qa"
    assert route["phase"] == "RECOVER"
