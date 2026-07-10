from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class KnownIdentity:
    """业务系统预先已知，cheatAgent 不问用户。"""

    user_id: str
    role: str
    region: str
    position: str
    personality: str = ""


@dataclass
class SessionContext:
    session_id: str
    session_date: str
    week: str
    price_snapshot: dict[str, Any]
    turn_count: int = 0


@dataclass
class UserModelSnapshot:
    """L2 用户建模快照 — 不含 honesty GT。"""

    user_id: str
    inferred_gaps: list[str] = field(default_factory=list)
    intent_layers: dict[str, str] = field(default_factory=dict)
    resistance_level: float = 0.0
    partial_claims: list[str] = field(default_factory=list)


@dataclass
class TurnRecord:
    speaker: str
    text: str
    timestamp: str
    skill_id: str | None = None
    phase: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CheatAgentState:
    """LangGraph state for cheatAgent."""

    known_identity: KnownIdentity
    session: SessionContext
    user_model: UserModelSnapshot
    conversation_history: list[TurnRecord] = field(default_factory=list)

    # Router output
    selected_skill_id: str | None = None
    selected_phase: str | None = None
    route_rationale: str = ""

    # Generation output
    agent_utterance: str = ""
    turn_metadata: dict[str, Any] = field(default_factory=dict)

    # Optional Web/memory background (HTTP workflow injects memoryPayload here)
    extra_context: str = ""

    # Memory write flags
    memory_updated: bool = False
