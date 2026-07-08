from __future__ import annotations

import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory

from market_truth_agent.analysis.pipeline import AnalysisPipeline
from market_truth_agent.models import Conversation, Persona
from market_truth_agent.storage.conversation_store import ConversationStore

STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app(db_path: str | None = None) -> Flask:
    app = Flask(__name__, static_folder=str(STATIC_DIR))
    store = ConversationStore(db_path or ":memory:")
    sessions: dict[str, dict] = {}

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "version": "0.3.0", "phase": "agent-rebuild"})

    @app.get("/")
    def index():
        return send_from_directory(STATIC_DIR, "index.html")

    @app.post("/api/conversations")
    def create_conversation():
        data = request.get_json(force=True, silent=True) or {}
        cid = str(uuid.uuid4())
        persona = Persona(
            user_id=data.get("user_id", f"U-{cid[:8]}"),
            role=data.get("role", "厂长"),
            personality=data.get("personality", "谨慎型"),
            position="long",
            honesty=float(data.get("honesty", 0.7)),
            region=data.get("region", "青岛港"),
        )
        conv = Conversation(
            conversation_id=cid,
            user_id=persona.user_id,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        sessions[cid] = {"persona": persona}
        store.save(conv)
        return jsonify({
            "conversation_id": cid,
            "persona": persona.__dict__,
            "note": "cheatAgent LangGraph not wired to API yet — use scripts/generate_dataset.py",
        })

    @app.post("/api/analyze/<cid>")
    def analyze(cid: str):
        conv = store.load(cid)
        if not conv:
            return jsonify({"error": "not found"}), 404
        sess = sessions.get(cid)
        persona = sess["persona"] if sess else Persona(
            user_id=conv.user_id, role="厂长", personality="谨慎型",
            position="long", honesty=0.7, region="青岛港",
        )
        pipeline = AnalysisPipeline()
        result = pipeline.run(conv, persona)
        return jsonify({
            "claims": [
                {
                    "indicator": c.indicator,
                    "value": c.value,
                    "region": c.region,
                    "evidence_strength": c.evidence_strength,
                    "deception_score": c.deception.score if c.deception else 0,
                    "claim_score": c.claim_score,
                }
                for c in result.claims
            ],
            "bucket_truths": {
                k: {"value": v.value, "confidence": v.confidence}
                for k, v in result.bucket_truths.items()
            },
            "user_reliability": result.user_reliability,
            "escalation_flags": result.escalation_flags,
        })

    return app
