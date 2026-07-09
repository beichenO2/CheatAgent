#!/usr/bin/env python3
"""Resumable full benchmark pipeline: generate dialogues → evaluate → report.

Beta spec (ADR-001): 30 users × 5 sessions × 20 turns = 100 turns/user.

Usage:
  PYTHONUNBUFFERED=1 POLARPRIVATE_URL=http://127.0.0.1:12790 \\
    MTA_LLM_MODE=live MTA_LLM_MODEL=0001 MTA_NORMALIZE_MODEL=qwen3.7-plus \\
    python scripts/run_benchmark_pipeline.py --preset beta_v1

  # Resume after interruption:
  python scripts/run_benchmark_pipeline.py --preset beta_v1 --resume

  # Generation only / evaluation only:
  python scripts/run_benchmark_pipeline.py --preset beta_v1 --phase generate
  python scripts/run_benchmark_pipeline.py --preset beta_v1 --phase evaluate --resume
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from market_truth_agent.agents.customer_agent.personas import DATASET_PRESETS
from market_truth_agent.agents.eval.smoke_runner import validate_smoke_dataset
from market_truth_agent.agents.simulation.runner import SimulationRunner
from market_truth_agent.llm.client import llm_backend_label, llm_mode, polarprivate_available
from market_truth_agent.utils.progress import progress
from market_truth_agent.utils.retry import retry_call


def load_user_meta(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def meta_to_conversation(meta: dict, session: dict):
    from market_truth_agent.models import Conversation, ConversationTurn

    persona = meta["persona"]
    turns = []
    for i, t in enumerate(session["turns"]):
        turns.append(
            ConversationTurn(
                turn_index=i,
                speaker=t["speaker"],
                text=t["text"],
                timestamp=t["timestamp"],
                tactic=t.get("skill_id"),
                phase=t.get("phase"),
            )
        )
    return Conversation(
        conversation_id=session["session_id"],
        user_id=persona["user_id"],
        started_at=session.get("session_date", ""),
        turns=turns,
    )


def _aggregate(rows: list[dict]) -> dict:
    if not rows:
        return {}
    n = len(rows)
    return {
        "slot_recall_mean": sum(r["slot_metrics"]["slot_recall"] for r in rows) / n,
        "slot_precision_mean": sum(r["slot_metrics"]["slot_precision"] for r in rows) / n,
        "prediction_accuracy_mean": sum(r["slot_metrics"]["prediction_accuracy"] for r in rows) / n,
        "bucket_veracity_accuracy_mean": sum(
            r["veracity"]["bucket_veracity_accuracy"] for r in rows
        ) / n,
        "external_consistency_mean": sum(
            r["external"]["external_consistency_mean"] for r in rows
        ) / n,
        "escalation_rate_mean": sum(r["escalation"]["escalation_rate"] for r in rows) / n,
        "claim_count_total": sum(r["claim_count"] for r in rows),
    }


from market_truth_agent.agents.cheat_agent.skills_registry import list_registered_skills
from market_truth_agent.agents.eval.analysis_metrics import evaluate_session, recon_honesty_pearson
from market_truth_agent.agents.eval.claim_metrics import pearson_reliability_honesty
from market_truth_agent.agents.eval.tactic_metrics import summarize_session
from market_truth_agent.analysis.pipeline import PipelineConfig
from market_truth_agent.benchmark.tier_b.price_data import PRICE_TRAJECTORY
from market_truth_agent.llm.client import normalize_model
from market_truth_agent.models import Persona


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _state_path(dataset_dir: Path) -> Path:
    return dataset_dir / "pipeline_state.json"


def _load_state(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"users": {}, "phase": "pending", "updated_at": None}


def _save_state(path: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = _utc_now()
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _ensure_llm_ready() -> None:
    if llm_mode() != "live":
        raise RuntimeError("MTA_LLM_MODE must be live for benchmark pipeline")
    if not polarprivate_available():
        raise RuntimeError(
            "PolarPrivate unavailable (check POLARPRIVATE_URL / vault unlocked)"
        )
    progress(f"[pipeline] llm=live backend={llm_backend_label()} normalize={normalize_model()}")


def _user_generate_done(meta_path: Path, sessions_per_user: int, min_turns: int) -> bool:
    if not meta_path.exists():
        return False
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    sessions = meta.get("sessions", [])
    if len(sessions) < sessions_per_user:
        return False
    return all(len(s.get("turns", [])) >= min_turns for s in sessions)


def run_generate(
    *,
    preset: str,
    output_dir: Path,
    resume: bool,
    state: dict[str, Any],
    state_path: Path,
) -> None:
    spec = DATASET_PRESETS[preset]
    personas = spec["personas"]
    min_turns = spec["min_turns"]
    sessions_per_user = spec["sessions_per_user"]
    world_state = bool(spec.get("world_state", False))
    # Isolate cross-session memory per dataset so a regen never inherits
    # another dataset's L2 user models.
    memory_root = Path("memory") if preset in ("smoke_v1", "alpha_v1", "beta_v1") else Path(f"memory_{preset}")
    runner = SimulationRunner(output_dir, memory_root=memory_root, world_state=world_state)

    progress(
        f"[pipeline] generate {preset} users={len(personas)} "
        f"sessions={sessions_per_user} turns={min_turns} total_turns={len(personas)*sessions_per_user*min_turns}"
    )
    state["phase"] = "generate"
    _save_state(state_path, state)

    for idx, persona in enumerate(personas, start=1):
        uid = persona.user_id
        meta_path = output_dir / "users" / uid / "meta.json"
        if resume and _user_generate_done(meta_path, sessions_per_user, min_turns):
            progress(f"[pipeline] generate skip {uid} ({idx}/{len(personas)}) complete")
            state["users"].setdefault(uid, {})["generate"] = "done"
            _save_state(state_path, state)
            continue

        progress(f"[pipeline] generate user {uid} ({idx}/{len(personas)})")
        _ensure_llm_ready()

        def _gen_one() -> list[dict[str, Any]]:
            return runner.write_user_resumable(
                persona,
                sessions_per_user=sessions_per_user,
                min_turns=min_turns,
            )

        sessions = retry_call(_gen_one, label=f"generate:{uid}")
        runner.rebuild_manifest(
            personas,
            version=preset,
            min_turns=min_turns,
            sessions_per_user=sessions_per_user,
        )
        state["users"].setdefault(uid, {})["generate"] = "done"
        state["users"][uid]["sessions"] = len(sessions)
        _save_state(state_path, state)
        progress(f"[pipeline] generate done {uid} sessions={len(sessions)}")

    runner.rebuild_manifest(
        personas,
        version=preset,
        min_turns=min_turns,
        sessions_per_user=sessions_per_user,
    )
    gate = validate_smoke_dataset(output_dir)
    state["generate_gate"] = gate
    _save_state(state_path, state)
    if not gate.get("passed"):
        progress(f"[pipeline] generate gate FAILED: {gate.get('failures')}")
        sys.exit(1)
    progress("[pipeline] generate gate PASSED")


def _strip_eval_report(report: dict) -> dict:
    return {k: v for k, v in report.items() if k != "result"}


def run_evaluate(
    *,
    preset: str,
    output_dir: Path,
    resume: bool,
    state: dict[str, Any],
    state_path: Path,
    report_path: Path,
) -> dict[str, Any]:
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    checkpoint_dir = Path("benchmark/reports") / preset / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    registered = list_registered_skills()
    pipeline_config = PipelineConfig(enable_normalize=True)

    report: dict[str, Any] = {
        "dataset_dir": str(output_dir),
        "preset": preset,
        "pipeline_config": {
            "enable_normalize": True,
            "normalize_model": normalize_model(),
        },
        "users": [],
        "tactic_summary": [],
        "session_metrics": [],
        "analysis_aggregate": {},
        "generated_at": _utc_now(),
    }
    recon_rows: list[dict] = []
    reliability_rows: list[dict] = []
    session_metric_rows: list[dict] = []

    users = manifest.get("users", [])
    state["phase"] = "evaluate"
    _save_state(state_path, state)

    progress(f"[pipeline] evaluate {preset} users={len(users)}")
    for idx, entry in enumerate(users, start=1):
        uid = entry["user_id"]
        ckpt = checkpoint_dir / f"{uid}_eval.json"
        if resume and ckpt.exists():
            progress(f"[pipeline] evaluate skip {uid} ({idx}/{len(users)}) checkpoint")
            cached = json.loads(ckpt.read_text(encoding="utf-8"))
            report["users"].append(cached["user_row"])
            session_metric_rows.extend(cached.get("session_metric_rows", []))
            report["tactic_summary"].extend(cached.get("tactic_rows", []))
            recon_rows.extend(cached.get("recon_rows", []))
            reliability_rows.append(cached.get("reliability_row", {}))
            state["users"].setdefault(uid, {})["evaluate"] = "done"
            _save_state(state_path, state)
            continue

        _ensure_llm_ready()
        meta = load_user_meta(output_dir / entry["path"])
        p = meta["persona"]
        persona = Persona(
            user_id=p["user_id"],
            role=p["role"],
            personality=p["personality"],
            position=p["position"],
            honesty=p["honesty"],
            region=p["region"],
            knowledge_depth=p.get("knowledge_depth", 0.8),
        )
        latent = meta.get("latent", {}).get("claims_truth", [])
        # World-truth GT for veracity: core three slots, honesty-governed at
        # generation (ADR-010 L3). Falls back to filtering user-level latent.
        core_latent = meta.get("latent", {}).get("core_claims_truth") or [
            c for c in latent
            if c.get("indicator") in ("港存", "采购积极性", "报价松动")
            and c.get("region") == persona.region
        ]
        session_results = []
        reliability_est = None
        total_claims = 0
        user_metrics: list[dict] = []

        progress(f"[pipeline] evaluate user {uid} ({idx}/{len(users)}) sessions={len(meta['sessions'])}")
        for sidx, session in enumerate(meta["sessions"], start=1):
            progress(
                f"[pipeline]   {uid} session {session['session_id']} "
                f"({sidx}/{len(meta['sessions'])}) turns={len(session.get('turns', []))}"
            )

            def _eval_one(sess: dict = session) -> dict:
                conv = meta_to_conversation(meta, sess)
                session_latent = sess.get("claims_truth") or latent
                # world_truth (beta_v2, week-specific) > user-level core latent
                return evaluate_session(
                    conv,
                    persona,
                    session_latent,
                    week=sess.get("week", "2026-W27"),
                    price_trajectory=PRICE_TRAJECTORY,
                    pipeline_config=pipeline_config,
                    veracity_claims=sess.get("world_truth") or core_latent,
                )

            eval_report = retry_call(_eval_one, label=f"eval:{uid}:{session['session_id']}")
            tactic = summarize_session(session.get("agent_metadata", []), registered)
            report["tactic_summary"].append(tactic)
            total_claims += eval_report["claim_count"]
            user_metrics.append(eval_report)
            session_metric_rows.append(eval_report)
            sm = eval_report["slot_metrics"]
            progress(
                f"[pipeline]   done {session['session_id']} f1={sm['f1']:.3f} "
                f"recall={sm['recall']:.3f} prec={sm['precision']:.3f}"
            )
            session_results.append({
                "session_id": session["session_id"],
                "claim_count": eval_report["claim_count"],
                "slot_metrics": eval_report["slot_metrics"],
                "fusion_ablation": {
                    mode: {k: v for k, v in metrics.items() if k != "fused_slots"}
                    for mode, metrics in (eval_report.get("fusion_ablation") or {}).items()
                } or None,
                "veracity": eval_report["veracity"],
                "external": eval_report["external"],
                "escalation": eval_report["escalation"],
                "recon": eval_report["recon"],
                "pipeline": eval_report["pipeline"],
                "tactic": tactic,
            })
            recon_rows.append({
                "user_id": uid,
                "mean_deception": eval_report["recon"]["mean_deception"],
                "honesty_gt": persona.honesty,
            })
            rel = eval_report["reliability"].get("reliability_est")
            if rel is not None:
                reliability_est = rel
            partial = {
                "user_id": uid,
                "session_results": session_results,
                "user_metrics": user_metrics,
                "reliability_est": reliability_est,
                "total_claims": total_claims,
            }
            (checkpoint_dir / f"{uid}_partial.json").write_text(
                json.dumps(partial, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        user_row = {
            "user_id": uid,
            "honesty_gt": persona.honesty,
            "reliability_est": reliability_est,
            "claim_count": total_claims,
            "slot_recall_mean": (
                sum(s["slot_metrics"]["slot_recall"] for s in session_results) / len(session_results)
                if session_results else 0.0
            ),
            "slot_precision_mean": (
                sum(s["slot_metrics"]["slot_precision"] for s in session_results) / len(session_results)
                if session_results else 0.0
            ),
            "sessions": session_results,
        }
        report["users"].append(user_row)
        reliability_rows.append({
            "user_id": uid,
            "honesty_gt": persona.honesty,
            "reliability_est": reliability_est,
        })
        ckpt.write_text(
            json.dumps(
                {
                    "user_row": user_row,
                    "session_metric_rows": user_metrics,
                    "tactic_rows": [s["tactic"] for s in session_results],
                    "recon_rows": [
                        {
                            "user_id": uid,
                            "mean_deception": s["recon"]["mean_deception"],
                            "honesty_gt": persona.honesty,
                        }
                        for s in session_results
                    ],
                    "reliability_row": reliability_rows[-1],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        state["users"].setdefault(uid, {})["evaluate"] = "done"
        _save_state(state_path, state)
        partial_path = checkpoint_dir / f"{uid}_partial.json"
        if partial_path.exists():
            partial_path.unlink()
        progress(f"[pipeline] evaluate done {uid} slot_recall={user_row['slot_recall_mean']:.3f}")

    report["session_metrics"] = [
        {k: v for k, v in r.items() if k != "result"} for r in session_metric_rows
    ]
    report["analysis_aggregate"] = {
        **_aggregate(session_metric_rows),
        "reliability_pearson": pearson_reliability_honesty(reliability_rows),
        "recon_honesty_pearson": recon_honesty_pearson(recon_rows),
    }
    report["smoke_gate"] = validate_smoke_dataset(output_dir)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    state["phase"] = "done"
    state["report_path"] = str(report_path)
    _save_state(state_path, state)
    progress(f"[pipeline] report saved → {report_path}")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Resumable benchmark pipeline")
    parser.add_argument("--preset", choices=sorted(DATASET_PRESETS), default="beta_v1")
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Dataset dir (default benchmark/datasets/<preset>)",
    )
    parser.add_argument(
        "--phase",
        choices=["all", "generate", "evaluate"],
        default="all",
    )
    parser.add_argument("--resume", action="store_true", help="Skip completed users")
    parser.add_argument(
        "--report-out",
        type=Path,
        default=None,
        help="Eval report path (default benchmark/reports/<preset>_eval.json)",
    )
    args = parser.parse_args()

    output_dir = args.output or Path("benchmark/datasets") / args.preset
    report_path = args.report_out or Path("benchmark/reports") / f"{args.preset}_eval.json"
    state_path = _state_path(output_dir)
    state = _load_state(state_path)
    state.setdefault("preset", args.preset)
    state.setdefault("started_at", state.get("started_at") or _utc_now())
    state.setdefault("users", {})

    progress(f"[pipeline] start preset={args.preset} phase={args.phase} resume={args.resume}")
    started = time.time()

    if args.phase in ("all", "generate"):
        run_generate(
            preset=args.preset,
            output_dir=output_dir,
            resume=args.resume or args.phase == "all",
            state=state,
            state_path=state_path,
        )

    if args.phase in ("all", "evaluate"):
        report = run_evaluate(
            preset=args.preset,
            output_dir=output_dir,
            resume=args.resume or args.phase == "all",
            state=state,
            state_path=state_path,
            report_path=report_path,
        )
        agg = report.get("analysis_aggregate", {})
        progress(
            f"[pipeline] COMPLETE elapsed={time.time()-started:.0f}s "
            f"recall={agg.get('slot_recall_mean', 0):.3f} "
            f"prec={agg.get('slot_precision_mean', 0):.3f} "
            f"claims={agg.get('claim_count_total', 0)}"
        )


if __name__ == "__main__":
    main()
