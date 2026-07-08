from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from market_truth_agent.agents.cheat_agent.memory import load_or_create_l2
from market_truth_agent.agents.cheat_agent.graph import run_cheat_agent_turn
from market_truth_agent.agents.cheat_agent.state import (
    KnownIdentity,
    SessionContext,
    TurnRecord,
)
from market_truth_agent.agents.cheat_agent.skills_registry import list_registered_skills
from market_truth_agent.agents.customer_agent.graph import CustomerAgentState, CustomerPersona
from market_truth_agent.agents.customer_agent.graph import run_customer_agent_turn
from market_truth_agent.benchmark.tier_b.price_data import PRICE_TRAJECTORY, TRUTH_VARIANTS
from market_truth_agent.llm.client import llm_mode


def price_at_session_index(session_index: int) -> dict[str, Any]:
    """Map session index to price snapshot (scaffold — expand to 5-month trajectory)."""
    idx = min(session_index, len(PRICE_TRAJECTORY) - 1)
    return dict(PRICE_TRAJECTORY[idx])


class SimulationRunner:
    """
    Dual-agent dialogue loop for dataset generation.

    Generation only — evaluation is separate (scripts/evaluate_dataset.py).
    """

    def __init__(
        self,
        output_dir: Path | None = None,
        memory_root: Path | None = None,
    ) -> None:
        self.output_dir = output_dir or Path("benchmark/datasets/smoke_v1")
        self.memory_root = memory_root or Path("memory")

    def run_session(
        self,
        persona: CustomerPersona,
        *,
        min_turns: int = 20,
        session_index: int = 0,
    ) -> dict[str, Any]:
        session_id = f"S{session_index + 1:03d}"
        price_snapshot = price_at_session_index(session_index)
        variant = TRUTH_VARIANTS[hash(persona.user_id) % len(TRUTH_VARIANTS)]
        latent_claims = [
            {"region": persona.region, "indicator": ind, "value": val, "market_object": "铁矿石"}
            for ind, val in variant
        ]

        known = KnownIdentity(
            user_id=persona.user_id,
            role=persona.role,
            region=persona.region,
            position=persona.position,
            personality=persona.personality,
        )
        session_ctx = SessionContext(
            session_id=session_id,
            session_date=f"2026-0{3 + session_index}-01",
            week=f"2026-W{9 + session_index * 4:02d}",
            price_snapshot=price_snapshot,
        )
        user_model = load_or_create_l2(persona.user_id, self.memory_root)
        history: list[TurnRecord] = []
        agent_metadata: list[dict[str, Any]] = []

        cheat_utterance = ""
        for turn_idx in range(min_turns):
            ts = datetime.now(timezone.utc).isoformat()

            if turn_idx % 2 == 0:
                utterance, meta, user_model = run_cheat_agent_turn(
                    known_identity=known,
                    session=session_ctx,
                    user_model=user_model,
                    conversation_history=history,
                    memory_root=self.memory_root,
                )
                session_ctx.turn_count += 1
                history.append(
                    TurnRecord(
                        speaker="agent",
                        text=utterance,
                        timestamp=ts,
                        skill_id=meta.get("skill_id"),
                        phase=meta.get("phase"),
                        metadata=meta,
                    )
                )
                agent_metadata.append(meta)
                cheat_utterance = utterance
            else:
                cust_state = CustomerAgentState(
                    persona=persona,
                    latent_claims_truth=latent_claims,
                    price_snapshot=price_snapshot,
                    cheat_agent_utterance=cheat_utterance,
                    conversation_history=[{"speaker": t.speaker, "text": t.text} for t in history],
                )
                reply = run_customer_agent_turn(cust_state)
                history.append(TurnRecord(speaker="user", text=reply, timestamp=ts))

        return {
            "session_id": session_id,
            "session_date": session_ctx.session_date,
            "week": session_ctx.week,
            "price_snapshot": price_snapshot,
            "turns": [asdict(t) for t in history],
            "agent_metadata": agent_metadata,
            "turn_count": len(history),
        }

    def build_user_dataset(self, persona: CustomerPersona, *, min_turns: int = 20) -> dict[str, Any]:
        session = self.run_session(persona, min_turns=min_turns)
        variant = TRUTH_VARIANTS[hash(persona.user_id) % len(TRUTH_VARIANTS)]
        return {
            "persona": asdict(persona),
            "latent": {
                "claims_truth": [
                    {"region": persona.region, "indicator": ind, "value": val, "market_object": "铁矿石"}
                    for ind, val in variant
                ],
                "price_trajectory": PRICE_TRAJECTORY,
            },
            "sessions": [session],
        }

    def write_smoke_dataset(self, personas: list[CustomerPersona], *, min_turns: int = 20) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "version": "smoke_v1",
            "users": [],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "llm_mode": llm_mode(),
            "registered_skills": list_registered_skills(),
            "min_turns": min_turns,
        }

        for persona in personas:
            user_dir = self.output_dir / "users" / persona.user_id
            user_dir.mkdir(parents=True, exist_ok=True)

            session = self.run_session(persona, min_turns=min_turns)
            variant = TRUTH_VARIANTS[hash(persona.user_id) % len(TRUTH_VARIANTS)]
            meta = {
                "persona": asdict(persona),
                "latent": {
                    "claims_truth": [
                        {"region": persona.region, "indicator": ind, "value": val, "market_object": "铁矿石"}
                        for ind, val in variant
                    ],
                    "price_trajectory": PRICE_TRAJECTORY,
                },
                "sessions": [session],
            }
            meta_path = user_dir / "meta.json"
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            manifest["users"].append({"user_id": persona.user_id, "path": str(meta_path.relative_to(self.output_dir))})

        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return self.output_dir
