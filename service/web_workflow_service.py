"""HTTP workflow service wrapping cheatAgent for market-truth-cs polar.

Contract: examples/http-workflow-demo/README.md
  POST /run  → { ok, reply, memory_delta? }
  GET  /health → { ok: true, ... }
"""
from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure src/ is importable when launched via uvicorn from service/
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Live LLM by default for this service (benchmark-compatible PolarPrivate).
os.environ.setdefault("MTA_LLM_MODE", "live")
os.environ.setdefault("POLARPRIVATE_URL", "http://127.0.0.1:12790")
os.environ.setdefault("MTA_LLM_MODEL", "0001")


def _sanitize_no_proxy_env() -> None:
    """Drop IPv6 localhost tokens that break httpx URLPattern (Invalid port ':1')."""
    drop = {"::1", "[::1]", "::1/128"}
    for key in ("NO_PROXY", "no_proxy"):
        raw = os.environ.get(key, "")
        if not raw:
            continue
        parts = [p.strip() for p in raw.split(",") if p.strip() and p.strip() not in drop]
        os.environ[key] = ",".join(parts)


_sanitize_no_proxy_env()

from fastapi import FastAPI
from pydantic import BaseModel, Field

from market_truth_agent.agents.cheat_agent.graph import run_cheat_agent_turn
from market_truth_agent.agents.cheat_agent.state import (
    KnownIdentity,
    SessionContext,
    TurnRecord,
    UserModelSnapshot,
)
from market_truth_agent.analysis.claim_extractor import ClaimExtractor
from market_truth_agent.benchmark.tier_b.price_data import PRICE_TRAJECTORY
from market_truth_agent.llm.client import llm_backend_label, llm_mode
from market_truth_agent.models import ConversationTurn

app = FastAPI(title="market-truth-agent HTTP workflow", version="0.1.0")

# In-process session store: sessionId → dialogue state
_SESSIONS: dict[str, dict[str, Any]] = {}
_MEMORY_ROOT = _ROOT / "memory" / "web_workflow"
_CLAIM_EXTRACTOR = ClaimExtractor(use_llm=False)


class RunInput(BaseModel):
    userId: str = "anonymous"
    scenarioId: str | None = None
    sessionId: str | None = None
    message: str = ""
    memoryPayload: dict[str, Any] = Field(default_factory=dict)
    config: dict[str, Any] = Field(default_factory=dict)
    workflowId: str = "mta-python"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _kv_lines(data: dict[str, Any] | None, *, skip: set[str] | None = None) -> list[str]:
    skip = skip or set()
    if not isinstance(data, dict):
        return []
    lines: list[str] = []
    for key, val in data.items():
        if key.startswith("_") or key in skip:
            continue
        if isinstance(val, (dict, list)):
            continue
        text = str(val).strip()
        if text:
            lines.append(f"{key}={text}")
    return lines


def _memory_context(memory_payload: dict[str, Any]) -> str:
    """Flatten user/scenario/session keypoints into prompt background."""
    user = memory_payload.get("user") or {}
    scenario = memory_payload.get("scenario") or {}
    session = memory_payload.get("session") or {}
    parts: list[str] = []
    user_lines = _kv_lines(user if isinstance(user, dict) else {})
    if user_lines:
        parts.append("用户层：" + "，".join(user_lines))
    scen_lines = _kv_lines(scenario if isinstance(scenario, dict) else {})
    if scen_lines:
        parts.append("情景层：" + "，".join(scen_lines))
    kps = session.get("keypoints") if isinstance(session, dict) else None
    if isinstance(kps, list) and kps:
        slot_bits: list[str] = []
        for item in kps:
            if isinstance(item, dict) and item.get("key") is not None:
                slot_bits.append(f"{item['key']}={item.get('value', '')}")
            elif isinstance(item, str):
                slot_bits.append(item)
        if slot_bits:
            parts.append("本会话已采集：" + "，".join(slot_bits))
    return "\n".join(parts)


def _pick_identity_field(user_mem: dict[str, Any], *keys: str, default: str) -> str:
    for key in keys:
        val = user_mem.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return default


def _get_or_create_session(
    *,
    session_id: str,
    user_id: str,
    memory_payload: dict[str, Any],
) -> dict[str, Any]:
    existing = _SESSIONS.get(session_id)
    if existing is not None:
        return existing

    user_mem = memory_payload.get("user") or {}
    if not isinstance(user_mem, dict):
        user_mem = {}

    region = _pick_identity_field(user_mem, "region", "区域", "港口", default="青岛港")
    role = _pick_identity_field(user_mem, "role", "角色", "职位", default="贸易员")
    position = _pick_identity_field(user_mem, "position", "头寸", default="long")
    personality = _pick_identity_field(user_mem, "personality", "性格", default="")

    price = dict(PRICE_TRAJECTORY[0])
    known = KnownIdentity(
        user_id=user_id,
        role=role,
        region=region,
        position=position,
        personality=personality,
    )
    session_ctx = SessionContext(
        session_id=session_id,
        session_date=datetime.now().strftime("%Y-%m-%d"),
        week=str(price.get("week", "2026-W09")),
        price_snapshot=price,
        turn_count=0,
    )
    state = {
        "known_identity": known,
        "session": session_ctx,
        "user_model": UserModelSnapshot(user_id=user_id),
        "history": [],
    }
    _SESSIONS[session_id] = state
    return state


def _claims_to_session_delta(
    message: str,
    *,
    user_id: str,
    session_id: str,
    default_region: str,
    week: str,
) -> dict[str, str]:
    turn = ConversationTurn(
        turn_index=0,
        speaker="user",
        text=message,
        timestamp=_now_iso(),
    )
    claims = _CLAIM_EXTRACTOR.extract_from_turn(
        turn,
        source_id=user_id,
        conversation_id=session_id,
        week=week,
        default_region=default_region,
    )
    delta: dict[str, str] = {}
    for claim in claims:
        delta[f"{claim.region}/{claim.indicator}"] = claim.value
    return delta


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "service": "mta-python",
        "llm_mode": llm_mode(),
        "llm_backend": llm_backend_label(),
        "sessions": len(_SESSIONS),
    }


@app.post("/run")
def run(body: RunInput) -> dict[str, Any]:
    message = (body.message or "").strip()
    if not message:
        return {"ok": False, "reply": "消息为空"}

    session_id = body.sessionId or f"anon-{body.userId}"
    user_id = body.userId or "anonymous"
    memory_payload = body.memoryPayload or {}
    extra_context = _memory_context(memory_payload)

    try:
        state = _get_or_create_session(
            session_id=session_id,
            user_id=user_id,
            memory_payload=memory_payload,
        )
        history: list[TurnRecord] = state["history"]
        session_ctx: SessionContext = state["session"]
        known: KnownIdentity = state["known_identity"]
        user_model: UserModelSnapshot = state["user_model"]

        ts = _now_iso()
        history.append(TurnRecord(speaker="user", text=message, timestamp=ts))

        utterance, meta, user_model = run_cheat_agent_turn(
            known_identity=known,
            session=session_ctx,
            user_model=user_model,
            conversation_history=history,
            memory_root=_MEMORY_ROOT,
            extra_context=extra_context,
        )
        session_ctx.turn_count += 1
        state["user_model"] = user_model

        agent_ts = _now_iso()
        history.append(
            TurnRecord(
                speaker="agent",
                text=utterance,
                timestamp=agent_ts,
                skill_id=meta.get("skill_id"),
                phase=meta.get("phase"),
                metadata=meta,
            )
        )

        session_delta = _claims_to_session_delta(
            message,
            user_id=user_id,
            session_id=session_id,
            default_region=known.region,
            week=session_ctx.week,
        )
        # Surface newly inferred gaps as soft session hints when no hard claim.
        if not session_delta and user_model.inferred_gaps:
            for gap in user_model.inferred_gaps[-3:]:
                session_delta[f"{known.region}/{gap}"] = "待确认"

        memory_delta: dict[str, Any] = {}
        if session_delta:
            memory_delta["session"] = session_delta

        if meta.get("llm_mode") == "mock" or (utterance or "").startswith("[mock-llm]"):
            return {
                "ok": False,
                "reply": (
                    "LLM 处于 mock 模式，未连上真实模型。"
                    "请确认 PolarPrivate 已启动且 MTA_LLM_MODE=live。"
                ),
                "memory_delta": memory_delta,
            }

        return {
            "ok": True,
            "reply": utterance,
            "memory_delta": memory_delta,
            "meta": {
                "skill_id": meta.get("skill_id"),
                "phase": meta.get("phase"),
                "llm_mode": meta.get("llm_mode"),
                "turn_count": session_ctx.turn_count,
            },
        }
    except Exception as exc:  # noqa: BLE001 — surface to polar as friendly reply
        return {
            "ok": False,
            "reply": f"Python 客服服务异常：{exc!s}",
        }


def main() -> None:
    import uvicorn

    host = os.environ.get("MTA_HTTP_HOST", "0.0.0.0")
    port = int(os.environ.get("MTA_HTTP_PORT", "3945"))
    uvicorn.run(
        "web_workflow_service:app",
        host=host,
        port=port,
        reload=False,
        app_dir=str(Path(__file__).resolve().parent),
    )


if __name__ == "__main__":
    main()
