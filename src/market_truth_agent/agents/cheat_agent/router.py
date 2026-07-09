from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from market_truth_agent.agents.cheat_agent.skills_registry import list_registered_skills
from market_truth_agent.agents.cheat_agent.state import CheatAgentState
from market_truth_agent.llm.client import chat_completion, extract_json_object, llm_mode
from market_truth_agent.llm.prompts import build_router_prompt

PROJECT_ROOT = Path(__file__).resolve().parents[4]
ROUTER_SKILL_PATH = PROJECT_ROOT / "skills" / "cheat-agent" / "SKILL-router.md"

VALID_PHASES = {"RAPPORT", "PROBE", "CHALLENGE", "VERIFY", "RECOVER"}


def _last_user_turn(state: CheatAgentState) -> str:
    for turn in reversed(state.conversation_history):
        if turn.speaker == "user":
            return turn.text
    return ""


def _user_asked_question(text: str) -> bool:
    return "?" in text or "？" in text


def _hypothesis_question(text: str) -> bool:
    return any(w in text for w in ("是不是", "有没有", "会不会", "已经", "到了", "破"))


def route_skill_rules(
    *,
    inferred_gaps: list[str],
    partial_claims: list[str],
    resistance_level: float,
    turn_count: int,
    last_user: str,
    has_price: bool,
    consecutive_challenge: int = 0,
) -> dict[str, Any]:
    """Deterministic fallback aligned with SKILL-router.md — used for mock + LLM validation."""
    skill_id = "clarification-probe"
    phase = "PROBE"
    rationale = "default clarification"
    secondary: list[str] = []

    if resistance_level > 0.6 or consecutive_challenge >= 3:
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
    elif turn_count <= 2 and not inferred_gaps and not partial_claims:
        skill_id, phase = "clarification-probe", "RAPPORT"
        rationale = "early turn, intent unclear"
    elif partial_claims and has_price:
        skill_id, phase = "trap-question", "VERIFY"
        rationale = "partial claim + price anchor → trapping verification"
    elif partial_claims:
        skill_id, phase = "reactance-biased-statement", "CHALLENGE"
        rationale = "partial claim without quant → biased statement"
        secondary = ["socratic-probe"]
    elif turn_count >= 4:
        skill_id, phase = "implicit-user-modeling", "PROBE"
        rationale = "multi-turn → implicit intent modeling"
        secondary = ["bayesian-tom"]
    elif "港存" not in inferred_gaps:
        skill_id, phase = "reactance-biased-statement", "CHALLENGE"
        rationale = "no inventory gap filled yet"

    return {
        "skill_id": skill_id,
        "phase": phase,
        "rationale": rationale,
        "secondary_skills": secondary,
    }


def _state_to_router_input(state: CheatAgentState) -> dict[str, Any]:
    meta = state.turn_metadata or {}
    return {
        "inferred_gaps": state.user_model.inferred_gaps,
        "partial_claims": state.user_model.partial_claims,
        "resistance_level": state.user_model.resistance_level,
        "turn_count": state.session.turn_count,
        "last_user": _last_user_turn(state),
        "has_price": bool(state.session.price_snapshot),
        "consecutive_challenge": int(meta.get("consecutive_challenge_count", 0)),
        "known_identity": {
            "role": state.known_identity.role,
            "region": state.known_identity.region,
            "position": state.known_identity.position,
        },
        "price_snapshot": state.session.price_snapshot,
        "conversation_history": [
            {"speaker": t.speaker, "text": t.text} for t in state.conversation_history[-6:]
        ],
    }


def _validate_route(payload: dict[str, Any]) -> dict[str, Any]:
    registered = set(list_registered_skills())
    skill_id = str(payload.get("skill_id", "clarification-probe"))
    if skill_id not in registered:
        skill_id = "clarification-probe"
    phase = str(payload.get("phase", "PROBE")).upper()
    if phase not in VALID_PHASES:
        phase = "PROBE"
    rationale = str(payload.get("rationale", "")) or "llm route"
    secondary = payload.get("secondary_skills", [])
    if not isinstance(secondary, list):
        secondary = []
    secondary = [s for s in secondary if isinstance(s, str) and s in registered]
    return {
        "skill_id": skill_id,
        "phase": phase,
        "rationale": rationale,
        "secondary_skills": secondary,
    }


def mock_route_from_user_prompt(user: str) -> str:
    """Parse router user prompt and return deterministic JSON (CI mock)."""
    inp = _parse_router_user_prompt(user)
    route = route_skill_rules(**inp)
    return json.dumps(route, ensure_ascii=False)


def _parse_router_user_prompt(user: str) -> dict[str, Any]:
    """Best-effort parse of build_router_prompt user block."""
    def _extract_list(key: str) -> list[str]:
        marker = f"{key}:"
        if marker not in user:
            return []
        line = user.split(marker, 1)[1].split("\n", 1)[0].strip()
        try:
            val = json.loads(line)
            return val if isinstance(val, list) else []
        except json.JSONDecodeError:
            return []

    resistance = 0.0
    if "resistance_level:" in user:
        try:
            resistance = float(user.split("resistance_level:", 1)[1].split("\n", 1)[0].strip())
        except ValueError:
            resistance = 0.0
    turn_count = 0
    if "turn_count:" in user:
        try:
            turn_count = int(user.split("turn_count:", 1)[1].split("\n", 1)[0].strip())
        except ValueError:
            turn_count = 0
    consecutive = 0
    if "consecutive_challenge_count:" in user:
        try:
            consecutive = int(
                user.split("consecutive_challenge_count:", 1)[1].split("\n", 1)[0].strip()
            )
        except ValueError:
            consecutive = 0
    last_user = ""
    if "last_user_utterance:" in user:
        last_user = user.split("last_user_utterance:", 1)[1].split("\n", 1)[0].strip()
    has_price = "price_snapshot: {}" not in user and "price_snapshot:" in user
    return {
        "inferred_gaps": _extract_list("inferred_gaps"),
        "partial_claims": _extract_list("partial_claims"),
        "resistance_level": resistance,
        "turn_count": turn_count,
        "last_user": last_user,
        "has_price": has_price,
        "consecutive_challenge": consecutive,
    }


def route_skill(state: CheatAgentState) -> dict[str, Any]:
    """LLM router via SKILL-router.md; rule fallback on parse/validation failure."""
    inp = _state_to_router_input(state)
    meta = state.turn_metadata or {}
    consecutive_challenge = inp["consecutive_challenge"]

    router_md = (
        ROUTER_SKILL_PATH.read_text(encoding="utf-8")
        if ROUTER_SKILL_PATH.exists()
        else ""
    )
    system, user = build_router_prompt(
        router_markdown=router_md,
        registered_skills=list_registered_skills(),
        router_input=inp,
    )
    raw = chat_completion(system, user, temperature=0.2)
    try:
        payload = extract_json_object(raw)
        route = _validate_route(payload)
        llm_source = "live" if llm_mode() == "live" else "mock-llm"
    except (json.JSONDecodeError, KeyError, TypeError):
        route = route_skill_rules(
            inferred_gaps=inp["inferred_gaps"],
            partial_claims=inp["partial_claims"],
            resistance_level=inp["resistance_level"],
            turn_count=inp["turn_count"],
            last_user=inp["last_user"],
            has_price=inp["has_price"],
            consecutive_challenge=consecutive_challenge,
        )
        llm_source = "rule-fallback"

    phase = route["phase"]
    return {
        "selected_skill_id": route["skill_id"],
        "selected_phase": phase,
        "route_rationale": route["rationale"],
        "turn_metadata": {
            **meta,
            "secondary_skills": route.get("secondary_skills", []),
            "consecutive_challenge_count": consecutive_challenge + (1 if phase == "CHALLENGE" else 0),
            "router_source": llm_source,
        },
    }
