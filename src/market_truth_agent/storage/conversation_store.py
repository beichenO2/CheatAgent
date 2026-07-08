from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from market_truth_agent.models import Conversation, ConversationTurn


class ConversationStore:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    scenario TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    data_json TEXT NOT NULL
                )
                """
            )

    def save(self, conversation: Conversation) -> None:
        payload = {
            "conversation_id": conversation.conversation_id,
            "user_id": conversation.user_id,
            "scenario": conversation.scenario,
            "started_at": conversation.started_at,
            "turns": [
                {
                    "turn_index": t.turn_index,
                    "speaker": t.speaker,
                    "text": t.text,
                    "timestamp": t.timestamp,
                    "phase": t.phase,
                    "tactic": t.tactic,
                    "elicitation_goal": t.elicitation_goal,
                    "metadata": t.metadata,
                }
                for t in conversation.turns
            ],
        }
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO conversations
                (conversation_id, user_id, scenario, started_at, data_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    conversation.conversation_id,
                    conversation.user_id,
                    conversation.scenario,
                    conversation.started_at,
                    json.dumps(payload, ensure_ascii=False),
                ),
            )

    def load(self, conversation_id: str) -> Conversation | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT data_json FROM conversations WHERE conversation_id = ?",
                (conversation_id,),
            ).fetchone()
        if not row:
            return None
        data = json.loads(row["data_json"])
        turns = [
            ConversationTurn(
                turn_index=t["turn_index"],
                speaker=t["speaker"],
                text=t["text"],
                timestamp=t["timestamp"],
                phase=t.get("phase"),
                tactic=t.get("tactic"),
                elicitation_goal=t.get("elicitation_goal"),
                metadata=t.get("metadata", {}),
            )
            for t in data["turns"]
        ]
        return Conversation(
            conversation_id=data["conversation_id"],
            user_id=data["user_id"],
            scenario=data["scenario"],
            started_at=data["started_at"],
            turns=turns,
        )

    def list_ids(self) -> list[str]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT conversation_id FROM conversations ORDER BY started_at"
            ).fetchall()
        return [r["conversation_id"] for r in rows]
