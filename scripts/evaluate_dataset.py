#!/usr/bin/env python3
"""Evaluate generated dataset — analysis + tactic metrics + ablations. GT only used here."""
import argparse
import json
import sys
from pathlib import Path

from market_truth_agent.agents.cheat_agent.skills_registry import list_registered_skills
from market_truth_agent.agents.eval.analysis_metrics import (
    evaluate_session,
    recon_honesty_pearson,
    run_ablation_suite,
)
from market_truth_agent.agents.eval.claim_metrics import pearson_reliability_honesty
from market_truth_agent.agents.eval.smoke_runner import validate_smoke_dataset
from market_truth_agent.agents.eval.tactic_metrics import summarize_session
from market_truth_agent.analysis.pipeline import PipelineConfig
from market_truth_agent.benchmark.tier_b.price_data import PRICE_TRAJECTORY
from market_truth_agent.llm.client import normalize_model
from market_truth_agent.models import Conversation, ConversationTurn, Persona
from market_truth_agent.utils.progress import progress


def load_user_meta(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def meta_to_conversation(meta: dict, session: dict) -> Conversation:
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate Tier B agent dataset")
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=Path("benchmark/datasets/smoke_v1"),
        help="Dataset directory containing manifest.json",
    )
    parser.add_argument(
        "--ablate-normalize",
        action="store_true",
        help="Skip Normalize layer (legacy ClaimExtractor path)",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        default=None,
        help="Truncate conversation turns for ablation",
    )
    parser.add_argument(
        "--ablation-report",
        action="store_true",
        help="Run full + ablate_normalize + turn ablations on first user/session",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable streaming progress logs on stderr",
    )
    parser.add_argument(
        "--users",
        type=str,
        default=None,
        help="Comma-separated user IDs to evaluate (default: all in manifest)",
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=None,
        help="Write JSON report to file (progress stays on stderr)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip users that already have eval checkpoint files",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=None,
        help="Per-user eval checkpoints (default: benchmark/reports/<dataset>/checkpoints)",
    )
    args = parser.parse_args()

    if args.no_progress:
        import os
        os.environ["MTA_PROGRESS"] = "0"

    dataset_dir = args.dataset_dir
    registered = list_registered_skills()
    smoke = validate_smoke_dataset(dataset_dir)
    manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))

    user_filter: set[str] | None = None
    if args.users:
        user_filter = {u.strip() for u in args.users.split(",") if u.strip()}

    checkpoint_dir = args.checkpoint_dir
    if checkpoint_dir is None:
        checkpoint_dir = Path("benchmark/reports") / dataset_dir.name / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    manifest_users = manifest.get("users", [])
    if user_filter is not None:
        manifest_users = [e for e in manifest_users if e["user_id"] in user_filter]

    pipeline_config = PipelineConfig(
        enable_normalize=not args.ablate_normalize,
        max_turns=args.max_turns,
    )

    report: dict = {
        "dataset_dir": str(dataset_dir),
        "smoke_gate": smoke,
        "pipeline_config": {
            "enable_normalize": pipeline_config.enable_normalize,
            "max_turns": pipeline_config.max_turns,
            "normalize_model": normalize_model(),
        },
        "users": [],
        "tactic_summary": [],
        "session_metrics": [],
        "analysis_aggregate": {},
    }

    recon_rows: list[dict] = []
    reliability_rows: list[dict] = []
    session_metric_rows: list[dict] = []
    user_total = len(manifest_users)

    progress(
        f"[eval] start dataset={dataset_dir.name} users={user_total} "
        f"normalize={pipeline_config.enable_normalize} model={normalize_model()}"
    )

    for user_idx, entry in enumerate(manifest_users, start=1):
        ckpt_path = checkpoint_dir / f"{entry['user_id']}_eval.json"
        if args.resume and ckpt_path.exists():
            progress(f"[eval] resume skip {entry['user_id']} (checkpoint exists)")
            cached = json.loads(ckpt_path.read_text(encoding="utf-8"))
            report["users"].append(cached["user_row"])
            for sr in cached.get("session_metric_rows", []):
                session_metric_rows.append(sr)
            for tr in cached.get("tactic_rows", []):
                report["tactic_summary"].append(tr)
            recon_rows.extend(cached.get("recon_rows", []))
            reliability_rows.append(cached.get("reliability_row", {}))
            continue

        meta_path = dataset_dir / entry["path"]
        meta = load_user_meta(meta_path)
        persona_data = meta["persona"]
        persona = Persona(
            user_id=persona_data["user_id"],
            role=persona_data["role"],
            personality=persona_data["personality"],
            position=persona_data["position"],
            honesty=persona_data["honesty"],
            region=persona_data["region"],
            knowledge_depth=persona_data.get("knowledge_depth", 0.8),
        )
        latent_claims = meta.get("latent", {}).get("claims_truth", [])
        # World-truth GT for veracity (core three, ADR-010 L3)
        core_latent = meta.get("latent", {}).get("core_claims_truth") or [
            c for c in latent_claims
            if c.get("indicator") in ("港存", "采购积极性", "报价松动")
            and c.get("region") == persona.region
        ]

        session_results = []
        reliability_est = None
        total_claims = 0

        progress(f"[eval] user {persona.user_id} ({user_idx}/{user_total}) sessions={len(meta['sessions'])}")
        for session_idx, session in enumerate(meta["sessions"], start=1):
            week = session.get("week", "2026-W27")
            conv = meta_to_conversation(meta, session)
            # Prefer per-session GT (dialogue-aligned); fall back to user-level latent
            session_latent = session.get("claims_truth") or latent_claims
            progress(
                f"[eval]   session {session['session_id']} ({session_idx}/{len(meta['sessions'])}) "
                f"turns={len(session.get('turns', []))} gt_slots={len(session_latent)}"
            )
            eval_report = evaluate_session(
                conv,
                persona,
                session_latent,
                week=week,
                price_trajectory=PRICE_TRAJECTORY,
                pipeline_config=pipeline_config,
                veracity_claims=session.get("world_truth") or core_latent,
            )
            tactic = summarize_session(session.get("agent_metadata", []), registered)
            report["tactic_summary"].append(tactic)
            total_claims += eval_report["claim_count"]
            eval_report["_user_id"] = persona.user_id
            session_metric_rows.append(eval_report)
            sm = eval_report["slot_metrics"]
            progress(
                f"[eval]   done {session['session_id']} claims={eval_report['claim_count']} "
                f"slot_f1={sm['f1']:.3f} recall={sm['recall']:.3f} prec={sm['precision']:.3f}"
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
                "user_id": persona.user_id,
                "mean_deception": eval_report["recon"]["mean_deception"],
                "honesty_gt": persona.honesty,
            })
            rel = eval_report["reliability"].get("reliability_est")
            if rel is not None:
                reliability_est = rel

        reliability_rows.append({
            "user_id": persona.user_id,
            "honesty_gt": persona.honesty,
            "reliability_est": reliability_est,
        })

        user_row = {
            "user_id": persona.user_id,
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
        progress(
            f"[eval] user {persona.user_id} complete claims={total_claims} "
            f"slot_recall={user_row['slot_recall_mean']:.3f}"
        )

        user_session_rows = [r for r in session_metric_rows if r.get("_user_id") == persona.user_id]
        ckpt_payload = {
            "user_row": user_row,
            "session_metric_rows": [{k: v for k, v in r.items() if not k.startswith("_")} for r in user_session_rows],
            "tactic_rows": [s["tactic"] for s in session_results],
            "recon_rows": [
                {
                    "user_id": persona.user_id,
                    "mean_deception": s["recon"]["mean_deception"],
                    "honesty_gt": persona.honesty,
                }
                for s in session_results
            ],
            "reliability_row": {
                "user_id": persona.user_id,
                "honesty_gt": persona.honesty,
                "reliability_est": reliability_est,
            },
        }
        ckpt_path.write_text(json.dumps(ckpt_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        progress(f"[eval] checkpoint → {ckpt_path}")

    report["session_metrics"] = [
        {k: v for k, v in r.items() if k != "result" and not k.startswith("_")}
        for r in session_metric_rows
    ]
    report["analysis_aggregate"] = {
        **_aggregate(session_metric_rows),
        "reliability_pearson": pearson_reliability_honesty(reliability_rows),
        "recon_honesty_pearson": recon_honesty_pearson(recon_rows),
    }

    if args.ablation_report and manifest.get("users"):
        progress("[eval] ablation suite on first user/session …")
        first = manifest["users"][0]
        meta = load_user_meta(dataset_dir / first["path"])
        persona_data = meta["persona"]
        persona = Persona(
            user_id=persona_data["user_id"],
            role=persona_data["role"],
            personality=persona_data["personality"],
            position=persona_data["position"],
            honesty=persona_data["honesty"],
            region=persona_data["region"],
        )
        session = meta["sessions"][0]
        conv = meta_to_conversation(meta, session)
        latent = meta.get("latent", {}).get("claims_truth", [])
        report["ablation"] = run_ablation_suite(
            conv,
            persona,
            latent,
            week=session.get("week", "2026-W27"),
            price_trajectory=PRICE_TRAJECTORY,
            turn_limits=[6, 12, 20],
        )
        progress(f"[eval] ablation complete variants={len(report['ablation']['ablations'])}")

    progress("[eval] writing final JSON report …")
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(payload, encoding="utf-8")
        progress(f"[eval] report saved → {args.report_out}")
    print(payload)
    if not smoke.get("passed"):
        sys.exit(1)


if __name__ == "__main__":
    main()
