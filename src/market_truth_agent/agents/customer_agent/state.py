from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CustomerPersona:
    user_id: str
    role: str
    region: str
    position: str
    personality: str
    honesty: float  # GT: disclosure strategy, NOT visible to cheatAgent
    resistance: float = 0.3
    knowledge_depth: float = 0.8


@dataclass
class CustomerAgentState:
    persona: CustomerPersona
    latent_claims_truth: list[dict[str, Any]]
    price_snapshot: dict[str, Any]
    cheat_agent_utterance: str
    conversation_history: list[dict[str, str]] = field(default_factory=list)
    customer_reply: str = ""
    turn_metadata: dict[str, Any] = field(default_factory=dict)
