from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from market_truth_agent.agents.cheat_agent.state import (
    CheatAgentState,
    UserModelSnapshot,
)

DEFAULT_MEMORY_ROOT = Path("memory")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def memory_root(root: Path | None = None) -> Path:
    return root or DEFAULT_MEMORY_ROOT


def l2_path(user_id: str, root: Path | None = None) -> Path:
    return memory_root(root) / "users" / f"{user_id}.json"


def l1_path(user_id: str, session_id: str, root: Path | None = None) -> Path:
    return memory_root(root) / "sessions" / user_id / f"{session_id}.json"


def l3_path(user_id: str, root: Path | None = None) -> Path:
    return memory_root(root) / "episodes" / f"{user_id}.jsonl"


def load_l2_user_model(user_id: str, root: Path | None = None) -> UserModelSnapshot | None:
    path = l2_path(user_id, root)
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return UserModelSnapshot(
        user_id=user_id,
        inferred_gaps=data.get("inferred_gaps", []),
        intent_layers=data.get("intent_layers", {}),
        resistance_level=float(data.get("resistance_level", 0.0)),
        partial_claims=data.get("partial_claims", []),
    )


def save_l2_user_model(model: UserModelSnapshot, root: Path | None = None) -> Path:
    path = l2_path(model.user_id, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        **asdict(model),
        "updated_at": _now_iso(),
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_or_create_l2(user_id: str, root: Path | None = None) -> UserModelSnapshot:
    return load_l2_user_model(user_id, root) or UserModelSnapshot(user_id=user_id)


def update_l1_session(
    *,
    user_id: str,
    session_id: str,
    skill_id: str | None,
    phase: str | None,
    turn_count: int,
    root: Path | None = None,
) -> Path:
    path = l1_path(user_id, session_id, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        data = {
            "user_id": user_id,
            "session_id": session_id,
            "skill_ids": [],
            "skill_invoke_count": 0,
            "turn_count": 0,
            "created_at": _now_iso(),
        }
    if skill_id:
        data["skill_invoke_count"] = int(data.get("skill_invoke_count", 0)) + 1
        kinds = list(data.get("skill_ids", []))
        if skill_id not in kinds:
            kinds.append(skill_id)
        data["skill_ids"] = kinds
    data["turn_count"] = turn_count
    data["last_phase"] = phase
    data["updated_at"] = _now_iso()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def append_l3_episode(
    *,
    user_id: str,
    session_id: str,
    speaker: str,
    text: str,
    skill_id: str | None = None,
    root: Path | None = None,
) -> Path | None:
    """Append episodic turn when resistance/claims suggest salient interaction."""
    if speaker != "user" and not skill_id:
        return None
    path = l3_path(user_id, root)
    path.parent.mkdir(parents=True, exist_ok=True)
    record: dict[str, Any] = {
        "ts": _now_iso(),
        "session_id": session_id,
        "speaker": speaker,
        "text": text[:240],
    }
    if skill_id:
        record["skill_id"] = skill_id
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def persist_turn_memory(
    state: CheatAgentState,
    *,
    root: Path | None = None,
    last_user_text: str = "",
) -> dict[str, Any]:
    user_id = state.known_identity.user_id
    session_id = state.session.session_id
    skill_id = state.turn_metadata.get("skill_id") or state.selected_skill_id

    save_l2_user_model(state.user_model, root)
    l1 = update_l1_session(
        user_id=user_id,
        session_id=session_id,
        skill_id=skill_id,
        phase=state.selected_phase,
        turn_count=state.session.turn_count,
        root=root,
    )
    l3 = None
    if last_user_text and (
        state.user_model.resistance_level >= 0.4 or state.user_model.partial_claims
    ):
        l3 = append_l3_episode(
            user_id=user_id,
            session_id=session_id,
            speaker="user",
            text=last_user_text,
            root=root,
        )
    if skill_id:
        append_l3_episode(
            user_id=user_id,
            session_id=session_id,
            speaker="agent",
            text=state.agent_utterance,
            skill_id=skill_id,
            root=root,
        )

    return {
        "memory_updated": True,
        "memory_l1": str(l1),
        "memory_l2": str(l2_path(user_id, root)),
        "memory_l3": str(l3) if l3 else str(l3_path(user_id, root)),
    }
