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
from market_truth_agent.llm.client import llm_backend_label, llm_mode


def price_at_session_index(session_index: int) -> dict[str, Any]:
    idx = min(session_index, len(PRICE_TRAJECTORY) - 1)
    return dict(PRICE_TRAJECTORY[idx])


def session_schedule(session_index: int) -> tuple[str, str, dict[str, Any]]:
    snap = price_at_session_index(session_index)
    month = 3 + session_index
    session_date = f"2026-{month:02d}-01"
    week = snap.get("week", f"2026-W{9 + session_index * 4:02d}")
    return session_date, week, snap


def latent_for_persona(persona: CustomerPersona) -> list[dict[str, Any]]:
    variant = TRUTH_VARIANTS[hash(persona.user_id) % len(TRUTH_VARIANTS)]
    return [
        {"region": persona.region, "indicator": ind, "value": val, "market_object": "铁矿石"}
        for ind, val in variant
    ]


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
        user_model=None,
    ) -> tuple[dict[str, Any], Any]:
        session_id = f"S{session_index + 1:03d}"
        session_date, week, price_snapshot = session_schedule(session_index)
        latent_claims = latent_for_persona(persona)

        known = KnownIdentity(
            user_id=persona.user_id,
            role=persona.role,
            region=persona.region,
            position=persona.position,
            personality=persona.personality,
        )
        session_ctx = SessionContext(
            session_id=session_id,
            session_date=session_date,
            week=week,
            price_snapshot=price_snapshot,
        )
        if user_model is None:
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

        session = {
            "session_id": session_id,
            "session_date": session_date,
            "week": week,
            "price_snapshot": price_snapshot,
            "turns": [asdict(t) for t in history],
            "agent_metadata": agent_metadata,
            "turn_count": len(history),
        }
        return session, user_model

    def run_user_sessions(
        self,
        persona: CustomerPersona,
        *,
        sessions_per_user: int = 1,
        min_turns: int = 20,
    ) -> list[dict[str, Any]]:
        user_model = load_or_create_l2(persona.user_id, self.memory_root)
        sessions: list[dict[str, Any]] = []
        for session_index in range(sessions_per_user):
            session, user_model = self.run_session(
                persona,
                min_turns=min_turns,
                session_index=session_index,
                user_model=user_model,
            )
            sessions.append(session)
        return sessions

    def build_user_dataset(
        self,
        persona: CustomerPersona,
        *,
        min_turns: int = 20,
        sessions_per_user: int = 1,
    ) -> dict[str, Any]:
        sessions = self.run_user_sessions(
            persona, sessions_per_user=sessions_per_user, min_turns=min_turns
        )
        return {
            "persona": asdict(persona),
            "latent": {
                "claims_truth": latent_for_persona(persona),
                "price_trajectory": PRICE_TRAJECTORY,
            },
            "sessions": sessions,
        }

    def write_dataset(
        self,
        personas: list[CustomerPersona],
        *,
        version: str = "smoke_v1",
        min_turns: int = 20,
        sessions_per_user: int = 1,
    ) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "version": version,
            "users": [],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "llm_mode": llm_mode(),
            "llm_backend": llm_backend_label(),
            "registered_skills": list_registered_skills(),
            "min_turns": min_turns,
            "sessions_per_user": sessions_per_user,
        }

        for persona in personas:
            user_dir = self.output_dir / "users" / persona.user_id
            user_dir.mkdir(parents=True, exist_ok=True)

            sessions = self.run_user_sessions(
                persona,
                sessions_per_user=sessions_per_user,
                min_turns=min_turns,
            )
            meta = {
                "persona": asdict(persona),
                "latent": {
                    "claims_truth": latent_for_persona(persona),
                    "price_trajectory": PRICE_TRAJECTORY,
                },
                "sessions": sessions,
            }
            meta_path = user_dir / "meta.json"
            meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
            manifest["users"].append({
                "user_id": persona.user_id,
                "path": str(meta_path.relative_to(self.output_dir)),
                "session_count": len(sessions),
            })

        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return self.output_dir

    def write_smoke_dataset(self, personas: list[CustomerPersona], *, min_turns: int = 20) -> Path:
        return self.write_dataset(
            personas,
            version="smoke_v1",
            min_turns=min_turns,
            sessions_per_user=1,
        )

    def write_alpha_dataset(self, personas: list[CustomerPersona], *, min_turns: int = 20) -> Path:
        return self.write_dataset(
            personas,
            version="alpha_v1",
            min_turns=min_turns,
            sessions_per_user=5,
        )
