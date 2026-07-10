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
from market_truth_agent.agents.cheat_agent.router import route_skill
from market_truth_agent.llm.client import chat_completion, parse_utterance
from market_truth_agent.llm.prompts import build_cheat_agent_prompt, load_skill_markdown
from market_truth_agent.agents.cheat_agent.memory import persist_turn_memory

PROJECT_ROOT = Path(__file__).resolve().parents[4]
SKILLS_DIR = PROJECT_ROOT / "skills" / "cheat-agent"


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


def _last_user_turn(state: CheatAgentState) -> str:
    for turn in reversed(state.conversation_history):
        if turn.speaker == "user":
            return turn.text
    return ""


def invoke_skill(state: CheatAgentState) -> dict[str, Any]:
    """Load selected skill markdown and generate utterance via LLM."""
    skill_id = state.selected_skill_id or "cover-qa"
    phase = state.selected_phase or "PROBE"
    skill_path = SKILLS_DIR / f"SKILL-{skill_id}.md"
    skill_markdown = load_skill_markdown(skill_id)

    history = [
        {"speaker": t.speaker, "text": t.text}
        for t in state.conversation_history
    ]
    system, user = build_cheat_agent_prompt(
        skill_id=skill_id,
        skill_markdown=skill_markdown,
        phase=phase,
        known_identity={
            "role": state.known_identity.role,
            "region": state.known_identity.region,
            "position": state.known_identity.position,
        },
        session={
            "session_date": state.session.session_date,
            "turn_count": state.session.turn_count,
            "price_snapshot": state.session.price_snapshot,
        },
        user_model={
            "inferred_gaps": state.user_model.inferred_gaps,
            "partial_claims": state.user_model.partial_claims,
            "resistance_level": state.user_model.resistance_level,
        },
        conversation_history=history,
        route_rationale=state.route_rationale,
        extra_context=state.extra_context or "",
    )
    raw = chat_completion(system, user, temperature=0.7)
    utterance = parse_utterance(raw)

    rel_skill = skill_path.relative_to(PROJECT_ROOT) if skill_path.exists() else skill_path.name

    metadata = {
        "skill_id": skill_id,
        "phase": phase,
        "route_rationale": state.route_rationale,
        "skill_file": str(rel_skill),
        "llm_mode": "mock" if "[mock-llm]" in utterance else "live",
    }
    return {"agent_utterance": utterance, "turn_metadata": metadata}


def write_memory(state: CheatAgentState) -> dict[str, Any]:
    """Persist L1 session, L2 user model, L3 episodic turns."""
    root = Path(state.turn_metadata.get("memory_root", "memory"))
    return persist_turn_memory(
        state,
        root=root,
        last_user_text=_last_user_turn(state),
    )


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


def _final_state(final: Any, fallback: CheatAgentState) -> CheatAgentState:
    if isinstance(final, CheatAgentState):
        return final
    if isinstance(final, dict):
        for key, val in final.items():
            if hasattr(fallback, key):
                setattr(fallback, key, val)
    return fallback


def run_cheat_agent_turn(
    *,
    known_identity: KnownIdentity,
    session: SessionContext,
    user_model: UserModelSnapshot,
    conversation_history: list[TurnRecord],
    memory_root: Path | str | None = None,
    extra_context: str = "",
) -> tuple[str, dict[str, Any], UserModelSnapshot]:
    """Single-turn wrapper — runs compiled LangGraph via invoke()."""
    state = CheatAgentState(
        known_identity=known_identity,
        session=session,
        user_model=user_model,
        conversation_history=conversation_history,
        extra_context=extra_context or "",
    )
    if memory_root is not None:
        state.turn_metadata["memory_root"] = str(memory_root)

    graph = build_cheat_agent_graph()
    final = _final_state(graph.invoke(state), state)
    return final.agent_utterance, final.turn_metadata, final.user_model
