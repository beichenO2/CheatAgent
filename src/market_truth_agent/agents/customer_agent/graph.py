from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from market_truth_agent.llm.client import chat_completion, parse_utterance
from market_truth_agent.llm.prompts import build_customer_agent_prompt


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
    Customer simulator — LLM + persona + latent GT.

    honesty semantics:
    - high: tends to disclose truth aligned with latent
    - low: strategic disclosure favoring position (not every sentence is false)
    """
    system, user = build_customer_agent_prompt(
        persona={
            "user_id": state.persona.user_id,
            "role": state.persona.role,
            "region": state.persona.region,
            "position": state.persona.position,
            "personality": state.persona.personality,
            "honesty": state.persona.honesty,
            "resistance": state.persona.resistance,
        },
        latent_claims_truth=state.latent_claims_truth,
        price_snapshot=state.price_snapshot,
        cheat_agent_utterance=state.cheat_agent_utterance,
        conversation_history=state.conversation_history,
    )
    raw = chat_completion(system, user, temperature=0.8)
    return parse_utterance(raw)
