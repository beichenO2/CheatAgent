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


def run_customer_agent_turn(state: CustomerAgentState) -> str:
    """
    Customer simulator — WILL use LLM + persona + latent GT.
    Scaffold: minimal placeholder until LLM wired.

    honesty semantics:
    - high: tends to disclose truth aligned with latent
    - low: strategic disclosure favoring position (not every sentence is false)
    """
    # TODO(M7): LLM with persona prompt + latent claims_truth
    price = state.price_snapshot.get("price", 820)
    return (
        f"[customer:{state.persona.user_id}] "
        f"主力{price}附近，我们{state.persona.region}这边情况还可以，您想了解哪方面？"
    )
