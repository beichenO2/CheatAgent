#!/usr/bin/env python3
"""Cross-user Truth Discovery — reliability calibration stage (ADR-010 L1).

Per-session evaluation is single-source per bucket, so under the Beta
"single-source no-update" rule every user's reliability stays at the prior
(0.5) and Pearson(reliability, honesty) is undefined. This script pools ALL
users' fused slots into shared (week, region, indicator) buckets and runs TD
across sources, which is where reliability updates become meaningful.

Input:  benchmark/reports/<preset>/checkpoints/*_eval.json  (fused_slots per session)
        benchmark/datasets/<preset>/users/*/meta.json       (week per session, honesty,
                                                             world_truth if beta_v2)
Output: benchmark/reports/<preset>/cross_user_td.json

Usage:
  python scripts/cross_user_td.py --preset beta_v1 [--fusion-mode llm]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from market_truth_agent.agents.eval.claim_metrics import pearson_correlation
from market_truth_agent.analysis.ontology import canonicalize
from market_truth_agent.analysis.truth_discovery import TruthDiscoveryEngine
from market_truth_agent.models import Claim


def _neutral_external(_claim: Claim) -> float:
    # Level/binary indicators have no directional price signal; keep neutral.
    return 0.5


def load_fused_claims(
    preset: str,
    fusion_mode: str,
) -> tuple[list[Claim], dict[str, float], dict[str, str]]:
    """Returns (claims, honesty_by_user, world_truth_by_bucket)."""
    ckpt_dir = Path("benchmark/reports") / preset / "checkpoints"
    dataset_dir = Path("benchmark/datasets") / preset

    honesty: dict[str, float] = {}
    weeks: dict[str, dict[str, str]] = {}
    world_truth: dict[str, str] = {}  # bucket_key -> value (beta_v2 only)

    for meta_path in sorted(dataset_dir.glob("users/*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        uid = meta["persona"]["user_id"]
        honesty[uid] = float(meta["persona"]["honesty"])
        weeks[uid] = {
            s["session_id"]: s.get("week", "2026-W27") for s in meta.get("sessions", [])
        }
        for s in meta.get("sessions", []):
            for c in s.get("world_truth", []) or []:
                _, bkey = canonicalize(
                    c["region"], c.get("market_object", "铁矿石"),
                    c["indicator"], s.get("week", "2026-W27"),
                )
                world_truth[bkey] = c["value"]

    claims: list[Claim] = []
    n_sessions = 0
    for ckpt in sorted(ckpt_dir.glob("*_eval.json")):
        data = json.loads(ckpt.read_text(encoding="utf-8"))
        uid = data.get("user_row", {}).get("user_id") or ckpt.name.split("_")[0]
        for row in data.get("session_metric_rows", []):
            sid = row.get("session_id", "")
            week = weeks.get(uid, {}).get(sid, "2026-W27")
            fused = (row.get("fusion_ablation") or {}).get(fusion_mode, {}).get(
                "fused_slots"
            ) or {}
            if fused:
                n_sessions += 1
            for slot_key, slot in fused.items():
                region, _, indicator = slot_key.partition("/")
                value = str(slot.get("value", ""))
                if not region or not indicator or not value:
                    continue
                _, bucket_key = canonicalize(region, "铁矿石", indicator, week)
                claims.append(
                    Claim(
                        claim_id=f"{uid}|{sid}|{slot_key}",
                        source_id=uid,
                        conversation_id=sid,
                        time=week,
                        region=region,
                        market_object="铁矿石",
                        indicator=indicator,
                        value=value,
                        claim_type="ordinal",
                        canonical_key=bucket_key,
                        bucket_key=bucket_key,
                        evidence_strength=float(slot.get("confidence", 0.5)),
                        extractor_confidence=float(slot.get("confidence", 0.5)),
                    )
                )
    print(f"[cross-td] users={len(honesty)} sessions_with_fused={n_sessions} claims={len(claims)}",
          file=sys.stderr)
    return claims, honesty, world_truth


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset", default="beta_v1")
    parser.add_argument("--fusion-mode", default="llm", choices=["llm", "voting", "last_wins"])
    parser.add_argument("--iterations", type=int, default=5)
    args = parser.parse_args()

    claims, honesty, world_truth = load_fused_claims(args.preset, args.fusion_mode)
    if not claims:
        print("no fused claims found — run evaluate first", file=sys.stderr)
        sys.exit(1)

    engine = TruthDiscoveryEngine(iterations=args.iterations)
    bucket_truths, reliability = engine.infer(claims, _neutral_external)

    # Bucket stats
    multi_source = 0
    bucket_rows = []
    by_bucket: dict[str, list[Claim]] = {}
    for c in claims:
        by_bucket.setdefault(c.bucket_key, []).append(c)
    for bkey, bclaims in sorted(by_bucket.items()):
        sources = {c.source_id for c in bclaims}
        if len(sources) > 1:
            multi_source += 1
        bt = bucket_truths.get(bkey)
        row: dict[str, Any] = {
            "bucket": bkey,
            "n_sources": len(sources),
            "n_claims": len(bclaims),
            "td_value": bt.value if bt else None,
            "td_confidence": round(bt.confidence, 4) if bt else None,
            "values": sorted({c.value for c in bclaims}),
        }
        if bkey in world_truth:
            row["world_truth"] = world_truth[bkey]
            row["td_correct"] = bool(bt and bt.value == world_truth[bkey])
        bucket_rows.append(row)

    # Reliability calibration
    users = sorted(honesty)
    rel_rows = [
        {
            "user_id": u,
            "honesty_gt": honesty[u],
            "reliability_est": round(reliability.get(u, 0.5), 4),
        }
        for u in users
    ]
    xs = [honesty[u] for u in users if u in reliability]
    ys = [reliability[u] for u in users if u in reliability]
    pearson = pearson_correlation(xs, ys) if len(xs) >= 2 else None

    # Veracity vs world truth (beta_v2 only; beta_v1 has no consistent GT — L2)
    judged = [r for r in bucket_rows if "td_correct" in r]
    td_acc = (sum(1 for r in judged if r["td_correct"]) / len(judged)) if judged else None

    out = {
        "preset": args.preset,
        "fusion_mode": args.fusion_mode,
        "n_users": len(users),
        "n_claims": len(claims),
        "n_buckets": len(by_bucket),
        "n_multi_source_buckets": multi_source,
        "reliability_pearson": {"pearson_r": pearson, "n": len(xs)},
        "td_world_truth_accuracy": td_acc,
        "world_truth_buckets_judged": len(judged),
        "note": (
            "beta_v1: world state is per-user (ADR-010 L2) — reliability numbers are "
            "diagnostic only; clean calibration requires beta_v2 world_truth."
            if not judged else "world_truth present — calibration valid"
        ),
        "reliability": rel_rows,
        "buckets": bucket_rows,
    }
    out_path = Path("benchmark/reports") / args.preset / "cross_user_td.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in out.items() if k not in ("reliability", "buckets")},
                     ensure_ascii=False, indent=2))
    print(f"[cross-td] report → {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
