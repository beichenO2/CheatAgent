from __future__ import annotations

from pathlib import Path
from typing import Any

from market_truth_agent.agents.cheat_agent.state import (
    CheatAgentState,
    KnownIdentity,
    SessionContext,
    TurnRecord,
    UserModelSnapshot,
)

SKILLS_DIR = Path(__file__).resolve().parents[4] / "skills" / "cheat-agent"


def load_context(state: CheatAgentState) -> dict[str, Any]:
    """Inject session, identity, history. Does NOT load honesty GT."""
    return {
        "session": state.session,
        "known_identity": state.known_identity,
        "user_model": state.user_model,
        "conversation_history": state.conversation_history,
        "price": state.session.price_snapshot,
    }


def update_user_model(state: CheatAgentState) -> dict[str, Any]:
    """Lightweight user modeling from recent user turns (no GT)."""
    model = state.user_model
    for turn in reversed(state.conversation_history):
        if turn.speaker != "user":
            continue
        text = turn.text
        if "?" in text or "？" in text:
            for kw, gap in [("库存", "港存"), ("港存", "港存"), ("采购", "采购积极性"), ("报价", "报价松动")]:
                if kw in text and gap not in model.inferred_gaps:
                    model.inferred_gaps.append(gap)
        if any(w in text for w in ("不对", "谁说的", "不是", "其实")):
            model.resistance_level = min(model.resistance_level + 0.2, 1.0)
        if any(ind in text for ind in ("港存", "库存", "采购", "报价")):
            model.partial_claims.append(text)
        break
    return {"user_model": model}


def route_skill(state: CheatAgentState) -> dict[str, Any]:
    """
    Router node — will invoke SKILL-router.md via LLM.
    Scaffold: rule-based fallback until M6 skills are ready.
    """
    gaps = state.user_model.inferred_gaps
    resistance = state.user_model.resistance_level

    if resistance > 0.6:
        skill_id, phase = "cover-qa", "RECOVER"
        rationale = "resistance high → recover rapport"
    elif "港存" not in gaps and not state.user_model.partial_claims:
        skill_id, phase = "reactance-biased-statement", "CHALLENGE"
        rationale = "no port inventory disclosure yet"
    elif state.user_model.partial_claims:
        skill_id, phase = "va-detail-chase", "VERIFY"
        rationale = "partial claim exists → chase verifiable details"
    else:
        skill_id, phase = "cover-qa", "PROBE"
        rationale = "default probe via cover qa"

    return {
        "selected_skill_id": skill_id,
        "selected_phase": phase,
        "route_rationale": rationale,
    }


def invoke_skill(state: CheatAgentState) -> dict[str, Any]:
    """
    Load selected skill and generate utterance via LLM.
    Scaffold: placeholder text until skills + LLM wired.
    """
    skill_id = state.selected_skill_id or "cover-qa"
    region = state.known_identity.region
    price = state.session.price_snapshot.get("price", 820)
    skill_path = SKILLS_DIR / f"SKILL-{skill_id}.md"

    # TODO(M6/M7): LLM call with skill_path content as system prompt fragment
    utterance = (
        f"[{skill_id}] 您好，看到{region}铁矿石主力约{price}元/吨。"
        f"想了解下您这边最近经营情况？"
    )

    metadata = {
        "skill_id": skill_id,
        "phase": state.selected_phase,
        "route_rationale": state.route_rationale,
        "skill_file": str(skill_path) if skill_path.exists() else "missing",
    }
    return {"agent_utterance": utterance, "turn_metadata": metadata}


def write_memory(state: CheatAgentState) -> dict[str, Any]:
    """Persist L1 session metadata counters (scaffold)."""
    return {"memory_updated": True}


def build_cheat_agent_graph():
    """
    LangGraph definition for cheatAgent.

    Requires: pip install -e ".[agent]"
    """
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise ImportError(
            "LangGraph not installed. Run: pip install -e '.[agent]'"
        ) from exc

    # LangGraph expects TypedDict or dataclass with reducer annotations for production;
    # scaffold uses dict merge pattern via node return values.
    graph = StateGraph(CheatAgentState)

    graph.add_node("load_context", lambda s: load_context(s) or {})
    graph.add_node("update_user_model", update_user_model)
    graph.add_node("route_skill", route_skill)
    graph.add_node("invoke_skill", invoke_skill)
    graph.add_node("write_memory", write_memory)

    graph.add_edge(START, "load_context")
    graph.add_edge("load_context", "update_user_model")
    graph.add_edge("update_user_model", "route_skill")
    graph.add_edge("route_skill", "invoke_skill")
    graph.add_edge("invoke_skill", "write_memory")
    graph.add_edge("write_memory", END)

    return graph.compile()


def run_cheat_agent_turn(
    *,
    known_identity: KnownIdentity,
    session: SessionContext,
    user_model: UserModelSnapshot,
    conversation_history: list[TurnRecord],
) -> tuple[str, dict[str, Any]]:
    """Single-turn convenience wrapper (scaffold)."""
    state = CheatAgentState(
        known_identity=known_identity,
        session=session,
        user_model=user_model,
        conversation_history=conversation_history,
    )
    for step in (
        update_user_model,
        route_skill,
        invoke_skill,
        write_memory,
    ):
        updates = step(state)
        for k, v in updates.items():
            setattr(state, k, v)
    return state.agent_utterance, state.turn_metadata
