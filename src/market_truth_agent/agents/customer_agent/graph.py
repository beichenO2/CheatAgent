from __future__ import annotations

from typing import Any

from market_truth_agent.agents.customer_agent.state import CustomerAgentState
from market_truth_agent.llm.client import chat_completion, parse_utterance
from market_truth_agent.llm.prompts import build_customer_agent_prompt


def load_persona(state: CustomerAgentState) -> dict[str, Any]:
    """Inject persona fields (no cheatAgent GT leakage)."""
    return {
        "turn_metadata": {
            **state.turn_metadata,
            "persona_loaded": True,
            "user_id": state.persona.user_id,
            "region": state.persona.region,
        }
    }


def load_latent_truth(state: CustomerAgentState) -> dict[str, Any]:
    """Load latent GT for customer simulator only."""
    return {
        "turn_metadata": {
            **state.turn_metadata,
            "latent_loaded": True,
            "latent_claim_count": len(state.latent_claims_truth),
        }
    }


def compose_reply(state: CustomerAgentState) -> dict[str, Any]:
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
    reply = parse_utterance(raw)
    return {
        "customer_reply": reply,
        "turn_metadata": {
            **state.turn_metadata,
            "llm_mode": "mock" if "[mock-llm]" in reply else "live",
        },
    }


def build_customer_agent_graph():
    """
    LangGraph definition for CustomerAgent.

    Nodes: load_persona → load_latent_truth → compose_reply
    """
    try:
        from langgraph.graph import END, START, StateGraph
    except ImportError as exc:
        raise ImportError(
            "LangGraph not installed. Run: pip install -e '.[agent]'"
        ) from exc

    graph = StateGraph(CustomerAgentState)
    graph.add_node("load_persona", lambda s: load_persona(s) or {})
    graph.add_node("load_latent_truth", load_latent_truth)
    graph.add_node("compose_reply", compose_reply)

    graph.add_edge(START, "load_persona")
    graph.add_edge("load_persona", "load_latent_truth")
    graph.add_edge("load_latent_truth", "compose_reply")
    graph.add_edge("compose_reply", END)

    return graph.compile()


def run_customer_agent_turn(state: CustomerAgentState) -> str:
    """Single-turn wrapper — runs compiled LangGraph via invoke()."""
    graph = build_customer_agent_graph()
    final = graph.invoke(state)
    if isinstance(final, dict):
        return str(final.get("customer_reply", ""))
    return final.customer_reply
