#!/usr/bin/env python3
"""Evaluate generated dataset — analysis + tactic metrics. GT only used here."""
import json
import sys
from pathlib import Path

from market_truth_agent.agents.cheat_agent.skills_registry import list_registered_skills
from market_truth_agent.agents.eval.claim_metrics import (
    claim_f1_vs_latent,
    em_vs_mv_errors,
    pearson_reliability_honesty,
)
from market_truth_agent.agents.eval.smoke_runner import validate_smoke_dataset
from market_truth_agent.agents.eval.tactic_metrics import summarize_session
from market_truth_agent.analysis.external_validator import external_consistency
from market_truth_agent.models import Conversation, ConversationTurn, Persona
from market_truth_agent.analysis.pipeline import AnalysisPipeline
from market_truth_agent.benchmark.tier_b.price_data import PRICE_TRAJECTORY


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


def main() -> None:
    dataset_dir = Path("benchmark/datasets/smoke_v1")
    registered = list_registered_skills()
    smoke = validate_smoke_dataset(dataset_dir)
    manifest = json.loads((dataset_dir / "manifest.json").read_text(encoding="utf-8"))
    pipeline = AnalysisPipeline(price_trajectory=PRICE_TRAJECTORY)
    report = {
        "smoke_gate": smoke,
        "users": [],
        "tactic_summary": [],
        "analysis_aggregate": {},
    }

    for entry in manifest["users"]:
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
        session = meta["sessions"][0]
        week = session.get("week", "2026-W27")
        conv = meta_to_conversation(meta, session)
        result = pipeline.run(conv, persona, week=week)
        latent_claims = meta.get("latent", {}).get("claims_truth", [])

        ext_fn = lambda c, traj=pipeline.price_trajectory: external_consistency(c, traj)
        claim_metrics = claim_f1_vs_latent(result.claims, latent_claims)
        bucket_metrics = em_vs_mv_errors(result.claims, latent_claims, week, ext_fn)
        tactic = summarize_session(session.get("agent_metadata", []), registered)
        reliability = result.user_reliability.get(persona.user_id)

        report["users"].append({
            "user_id": persona.user_id,
            "honesty_gt": persona.honesty,
            "reliability_est": reliability,
            "claim_count": len(result.claims),
            "claim_f1": claim_metrics,
            "bucket_error": bucket_metrics,
            "tactic": tactic,
        })
        report["tactic_summary"].append(tactic)

    report["analysis_aggregate"] = {
        "claim_f1_mean": (
            sum(u["claim_f1"]["f1"] for u in report["users"]) / len(report["users"])
            if report["users"]
            else 0.0
        ),
        "claim_count_total": sum(u["claim_count"] for u in report["users"]),
        "pearson_reliability_honesty": pearson_reliability_honesty(report["users"]),
        "em_error_mean": (
            sum(u["bucket_error"]["em_error"] for u in report["users"]) / len(report["users"])
            if report["users"]
            else 0.0
        ),
        "mv_error_mean": (
            sum(u["bucket_error"]["mv_error"] for u in report["users"]) / len(report["users"])
            if report["users"]
            else 0.0
        ),
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not smoke.get("passed"):
        sys.exit(1)


if __name__ == "__main__":
    main()
