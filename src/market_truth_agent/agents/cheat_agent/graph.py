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


def _user_asked_question(text: str) -> bool:
    return "?" in text or "？" in text


def _hypothesis_question(text: str) -> bool:
    return any(w in text for w in ("是不是", "有没有", "会不会", "已经", "到了", "破"))


def route_skill(state: CheatAgentState) -> dict[str, Any]:
    """
    Rule-based router aligned with skills/cheat-agent/SKILL-router.md (M6).
    LLM routing deferred to M7.
    """
    gaps = state.user_model.inferred_gaps
    resistance = state.user_model.resistance_level
    claims = state.user_model.partial_claims
    turn_count = state.session.turn_count
    last_user = _last_user_turn(state)
    has_price = bool(state.session.price_snapshot)

    meta = state.turn_metadata or {}
    consecutive_challenge = int(meta.get("consecutive_challenge_count", 0))

    skill_id = "clarification-probe"
    phase = "PROBE"
    rationale = "default clarification"
    secondary: list[str] = []

    if resistance > 0.6 or consecutive_challenge >= 3:
        skill_id, phase = "cover-qa", "RECOVER"
        rationale = "high resistance or too many challenges → recover reciprocity"
    elif _user_asked_question(last_user):
        skill_id, phase = "info-seeking-inference", "PROBE"
        rationale = "user asked → infer gaps from question"
        if _hypothesis_question(last_user):
            skill_id = "trap-question" if has_price else "reactance-biased-statement"
            phase = "VERIFY" if has_price else "CHALLENGE"
            rationale = "hypothesis-style question → verify or provoke correction"
            secondary = ["info-seeking-inference"]
    elif turn_count <= 2 and not gaps and not claims:
        skill_id, phase = "clarification-probe", "RAPPORT"
        rationale = "early turn, intent unclear"
    elif claims and has_price:
        skill_id, phase = "trap-question", "VERIFY"
        rationale = "partial claim + price anchor → trapping verification"
    elif claims:
        skill_id, phase = "reactance-biased-statement", "CHALLENGE"
        rationale = "partial claim without quant → biased statement"
        secondary = ["socratic-probe"]
    elif turn_count >= 4:
        skill_id, phase = "implicit-user-modeling", "PROBE"
        rationale = "multi-turn → implicit intent modeling"
        secondary = ["bayesian-tom"]
    elif "港存" not in gaps:
        skill_id, phase = "reactance-biased-statement", "CHALLENGE"
        rationale = "no inventory gap filled yet"

    return {
        "selected_skill_id": skill_id,
        "selected_phase": phase,
        "route_rationale": rationale,
        "turn_metadata": {
            **meta,
            "secondary_skills": secondary,
            "consecutive_challenge_count": consecutive_challenge + (1 if phase == "CHALLENGE" else 0),
        },
    }


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


def run_cheat_agent_turn(
    *,
    known_identity: KnownIdentity,
    session: SessionContext,
    user_model: UserModelSnapshot,
    conversation_history: list[TurnRecord],
    memory_root: Path | str | None = None,
) -> tuple[str, dict[str, Any], UserModelSnapshot]:
    """Single-turn convenience wrapper."""
    state = CheatAgentState(
        known_identity=known_identity,
        session=session,
        user_model=user_model,
        conversation_history=conversation_history,
    )
    if memory_root is not None:
        state.turn_metadata["memory_root"] = str(memory_root)

    for step in (
        update_user_model,
        route_skill,
        invoke_skill,
        write_memory,
    ):
        updates = step(state)
        for k, v in updates.items():
            if k == "turn_metadata" and isinstance(v, dict):
                state.turn_metadata.update(v)
            else:
                setattr(state, k, v)
    return state.agent_utterance, state.turn_metadata, state.user_model
