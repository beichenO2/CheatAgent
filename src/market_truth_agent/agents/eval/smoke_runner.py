from __future__ import annotations

import inspect
import json
import math
from pathlib import Path
from typing import Any

from market_truth_agent.agents.cheat_agent import graph as cheat_graph
from market_truth_agent.agents.cheat_agent.skills_registry import list_registered_skills
from market_truth_agent.agents.eval.tactic_metrics import summarize_session
from market_truth_agent.llm import prompts as llm_prompts
from market_truth_agent.recon.core import ReConEngine


def _check_gt_isolation() -> dict[str, bool]:
    recon_src = inspect.getsource(ReConEngine)
    cheat_invoke_src = inspect.getsource(cheat_graph.invoke_skill)
    cheat_prompt_src = inspect.getsource(llm_prompts.build_cheat_agent_prompt)
    return {
        "recon_no_persona_honesty": "persona.honesty" not in recon_src,
        "invoke_no_honesty_gt": "persona.honesty" not in cheat_invoke_src,
        "cheat_prompt_no_honesty_field": "honesty:" not in cheat_prompt_src,
    }


def _expected_users(version: str | None) -> int:
    if version == "alpha_v1":
        return 10
    return 3


def validate_smoke_dataset(
    dataset_dir: Path,
    *,
    min_turns: int = 20,
    min_users: int | None = None,
    sessions_per_user: int | None = None,
) -> dict[str, Any]:
    dataset_dir = Path(dataset_dir)
    manifest_path = dataset_dir / "manifest.json"
    checks: dict[str, Any] = {"dataset_dir": str(dataset_dir)}
    failures: list[str] = []

    if not manifest_path.exists():
        failures.append("manifest.json missing")
        checks["passed"] = False
        checks["failures"] = failures
        return checks

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    version = manifest.get("version")
    checks["version"] = version
    checks["llm_mode"] = manifest.get("llm_mode")
    checks["llm_backend"] = manifest.get("llm_backend")
    checks["user_count"] = len(manifest.get("users", []))
    expected_users = min_users if min_users is not None else _expected_users(version)
    expected_sessions = sessions_per_user if sessions_per_user is not None else int(
        manifest.get("sessions_per_user", 1)
    )
    checks["expected_users"] = expected_users
    checks["expected_sessions_per_user"] = expected_sessions

    if checks["user_count"] < expected_users:
        failures.append(f"expected >={expected_users} users, got {checks['user_count']}")

    registered = list_registered_skills()
    session_summaries: list[dict[str, float]] = []

    for entry in manifest.get("users", []):
        meta_path = dataset_dir / entry["path"]
        if not meta_path.exists():
            failures.append(f"missing meta: {entry['path']}")
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        sessions = meta.get("sessions", [])
        if len(sessions) < expected_sessions:
            failures.append(
                f"{entry['user_id']}: sessions {len(sessions)} < {expected_sessions}"
            )
        for sess_idx, session in enumerate(sessions):
            turns = session.get("turns", [])
            if len(turns) < min_turns:
                failures.append(
                    f"{entry['user_id']}:{session.get('session_id')}: turns {len(turns)} < {min_turns}"
                )
            if not any(t.get("text", "").strip() for t in turns):
                failures.append(f"{entry['user_id']}:{session.get('session_id')}: empty transcript")
            metadata = session.get("agent_metadata", [])
            if not metadata or not all(m.get("skill_id") for m in metadata):
                failures.append(
                    f"{entry['user_id']}:{session.get('session_id')}: agent_metadata missing skill_id"
                )
            summary = summarize_session(metadata, registered)
            for key, val in summary.items():
                if isinstance(val, float) and math.isnan(val):
                    failures.append(f"{entry['user_id']}: {key} is NaN")
            if summary["skill_kind_count"] < 1:
                failures.append(f"{entry['user_id']}: skill_kind_count < 1")
            session_summaries.append(summary)

    gt_checks = _check_gt_isolation()
    checks["gt_isolation"] = gt_checks
    if not all(gt_checks.values()):
        failures.append("GT isolation static check failed")

    checks["tactic_aggregate"] = {
        "sessions": len(session_summaries),
        "avg_skill_kind_count": (
            sum(s["skill_kind_count"] for s in session_summaries) / len(session_summaries)
            if session_summaries
            else 0.0
        ),
    }
    checks["failures"] = failures
    checks["passed"] = len(failures) == 0
    return checks
