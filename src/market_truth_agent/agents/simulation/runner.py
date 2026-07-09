from __future__ import annotations

import hashlib
import json
import sys
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
from market_truth_agent.agents.customer_agent.graph import CustomerAgentState, run_customer_agent_turn
from market_truth_agent.agents.customer_agent.state import CustomerPersona
from market_truth_agent.benchmark.tier_b.price_data import PRICE_TRAJECTORY, TRUTH_VARIANTS
from market_truth_agent.llm.client import llm_backend_label, llm_mode
from market_truth_agent.utils.progress import progress


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


def world_truth_for(region: str, week: str) -> list[dict[str, Any]]:
    """Shared world state per (region, week) — ADR-010 L2 / beta_v2.

    Every user in the same region+week gets the SAME latent truth; only
    honesty decides whether they report it faithfully. Deterministic via md5
    (Python's hash() is salted per process, unusable for reproducibility).
    """
    digest = hashlib.md5(f"{region}|{week}".encode("utf-8")).hexdigest()
    variant = TRUTH_VARIANTS[int(digest, 16) % len(TRUTH_VARIANTS)]
    return [
        {"region": region, "indicator": ind, "value": val, "market_object": "铁矿石"}
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
        *,
        world_state: bool = False,
    ) -> None:
        self.output_dir = output_dir or Path("benchmark/datasets/smoke_v1")
        self.memory_root = memory_root or Path("memory")
        # world_state=True: latent truth shared per (region, week) — beta_v2
        self.world_state = world_state

    def _latent_for_session(
        self, persona: CustomerPersona, week: str
    ) -> list[dict[str, Any]]:
        if self.world_state:
            return world_truth_for(persona.region, week)
        return latent_for_persona(persona)

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
        latent_claims = self._latent_for_session(persona, week)

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
            progress(
                f"[sim] {persona.user_id} {session_id} turn {turn_idx + 1}/{min_turns}"
            )
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
        if self.world_state:
            # Per-session world truth = veracity GT for this week (ADR-010 L2)
            session["world_truth"] = latent_claims
        print(
            f"[sim] {persona.user_id} session {session_index + 1}/{session_id} "
            f"turns={len(history)} llm={llm_mode()}",
            file=sys.stderr,
            flush=True,
        )
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
            "latent": self._latent_block(persona, sessions),
            "sessions": sessions,
        }

    def _latent_block(
        self, persona: CustomerPersona, sessions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if not self.world_state:
            return {
                "claims_truth": latent_for_persona(persona),
                "price_trajectory": PRICE_TRAJECTORY,
            }
        # World-state dataset: user-level claims_truth is week 1 world truth
        # (compat for smoke gate); authoritative GT lives in session.world_truth.
        first_week = sessions[0]["week"] if sessions else session_schedule(0)[1]
        return {
            "claims_truth": world_truth_for(persona.region, first_week),
            "world_state": True,
            "world_truth_by_week": {
                s["week"]: s.get("world_truth", []) for s in sessions
            },
            "price_trajectory": PRICE_TRAJECTORY,
        }

    def _user_meta_path(self, persona: CustomerPersona) -> Path:
        return self.output_dir / "users" / persona.user_id / "meta.json"

    def _load_completed_sessions(
        self, persona: CustomerPersona, *, min_turns: int
    ) -> list[dict[str, Any]]:
        path = self._user_meta_path(persona)
        if not path.exists():
            return []
        try:
            meta = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        sessions: list[dict[str, Any]] = []
        for session in meta.get("sessions", []):
            turns = session.get("turns", [])
            if len(turns) >= min_turns and session.get("agent_metadata"):
                sessions.append(session)
            else:
                progress(
                    f"[sim] {persona.user_id} drop partial session "
                    f"{session.get('session_id', '?')} turns={len(turns)}"
                )
                break
        return sessions

    def _write_user_checkpoint(
        self,
        persona: CustomerPersona,
        sessions: list[dict[str, Any]],
    ) -> Path:
        user_dir = self._user_meta_path(persona).parent
        user_dir.mkdir(parents=True, exist_ok=True)
        meta = {
            "persona": asdict(persona),
            "latent": self._latent_block(persona, sessions),
            "sessions": sessions,
        }
        meta_path = self._user_meta_path(persona)
        meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return meta_path

    def write_user_resumable(
        self,
        persona: CustomerPersona,
        *,
        sessions_per_user: int = 1,
        min_turns: int = 20,
    ) -> list[dict[str, Any]]:
        """Generate sessions for one user; resume from last completed session."""
        from market_truth_agent.utils.retry import retry_call

        sessions = self._load_completed_sessions(persona, min_turns=min_turns)
        if len(sessions) >= sessions_per_user:
            progress(
                f"[sim] resume skip {persona.user_id} "
                f"({len(sessions)}/{sessions_per_user} sessions complete)"
            )
            return sessions

        user_model = load_or_create_l2(persona.user_id, self.memory_root)
        for session_index in range(len(sessions), sessions_per_user):
            progress(
                f"[sim] {persona.user_id} session {session_index + 1}/{sessions_per_user} "
                f"(resume from {len(sessions)})"
            )

            def _run_one(
                si: int = session_index,
                um: Any = user_model,
            ) -> tuple[dict[str, Any], Any]:
                return self.run_session(
                    persona,
                    min_turns=min_turns,
                    session_index=si,
                    user_model=um,
                )

            session, user_model = retry_call(
                _run_one,
                label=f"sim:{persona.user_id}:S{session_index + 1}",
            )
            sessions.append(session)
            meta_path = self._write_user_checkpoint(persona, sessions)
            progress(f"[sim] checkpoint {persona.user_id} → {meta_path} sessions={len(sessions)}")
        return sessions

    def write_dataset(
        self,
        personas: list[CustomerPersona],
        *,
        version: str = "smoke_v1",
        min_turns: int = 20,
        sessions_per_user: int = 1,
        resume: bool = False,
    ) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = self.output_dir / "manifest.json"
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["llm_mode"] = llm_mode()
            manifest["llm_backend"] = llm_backend_label()
        else:
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
        manifest["version"] = version
        manifest["min_turns"] = min_turns
        manifest["sessions_per_user"] = sessions_per_user

        existing_by_id = {u["user_id"]: u for u in manifest.get("users", [])}

        for user_idx, persona in enumerate(personas, start=1):
            progress(
                f"[sim] generating {persona.user_id} ({user_idx}/{len(personas)}) "
                f"sessions={sessions_per_user} turns={min_turns} resume={resume}"
            )
            if resume:
                sessions = self.write_user_resumable(
                    persona,
                    sessions_per_user=sessions_per_user,
                    min_turns=min_turns,
                )
            else:
                sessions = self.run_user_sessions(
                    persona,
                    sessions_per_user=sessions_per_user,
                    min_turns=min_turns,
                )
                self._write_user_checkpoint(persona, sessions)

            meta_path = self._user_meta_path(persona)
            entry = {
                "user_id": persona.user_id,
                "path": str(meta_path.relative_to(self.output_dir)),
                "session_count": len(sessions),
            }
            existing_by_id[persona.user_id] = entry
            manifest["users"] = [
                existing_by_id[k] for k in sorted(existing_by_id.keys())
            ]
            print(
                f"[sim] wrote {persona.user_id} ({len(sessions)} sessions) → {meta_path}",
                file=sys.stderr,
                flush=True,
            )
            manifest_path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return self.output_dir

    def rebuild_manifest(
        self,
        personas: list[CustomerPersona],
        *,
        version: str,
        min_turns: int,
        sessions_per_user: int,
    ) -> Path:
        """Rebuild manifest.json from on-disk user meta files."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        users: list[dict[str, Any]] = []
        for persona in personas:
            meta_path = self._user_meta_path(persona)
            if not meta_path.exists():
                continue
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            users.append({
                "user_id": persona.user_id,
                "path": str(meta_path.relative_to(self.output_dir)),
                "session_count": len(meta.get("sessions", [])),
            })
        manifest = {
            "version": version,
            "users": users,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "llm_mode": llm_mode(),
            "llm_backend": llm_backend_label(),
            "registered_skills": list_registered_skills(),
            "min_turns": min_turns,
            "sessions_per_user": sessions_per_user,
        }
        manifest_path = self.output_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return manifest_path

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

    def write_beta_dataset(self, personas: list[CustomerPersona], *, min_turns: int = 20) -> Path:
        return self.write_dataset(
            personas,
            version="beta_v1",
            min_turns=min_turns,
            sessions_per_user=5,
            resume=True,
        )
