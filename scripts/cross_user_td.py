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
from market_truth_agent.analysis.truth_discovery import TruthDiscoveryEngine, majority_vote
from market_truth_agent.models import Claim

CORE3 = frozenset({"港存", "采购积极性", "报价松动"})


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


def load_union_gt(
    preset: str,
    honesty: dict[str, float],
) -> dict[str, list[dict[str, Any]]]:
    """Per-bucket union of session claims_truth — no shared world_truth required.

    Each user-session may assert different slots/values; same bucket can hold
    multiple GT values (one per contributing session). This is the normal case
    when 30 users × 5 sessions talk about overlapping (week, region, indicator).
    """
    dataset_dir = Path("benchmark/datasets") / preset
    union: dict[str, list[dict[str, Any]]] = {}
    for meta_path in sorted(dataset_dir.glob("users/*/meta.json")):
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        uid = meta["persona"]["user_id"]
        for session in meta.get("sessions", []):
            week = session.get("week", "2026-W27")
            sid = session.get("session_id", "")
            for c in session.get("claims_truth", []) or []:
                region = c.get("region", "")
                indicator = c.get("indicator", "")
                value = str(c.get("value", ""))
                if not region or not indicator or not value:
                    continue
                _, bkey = canonicalize(
                    region, c.get("market_object", "铁矿石"), indicator, week,
                )
                union.setdefault(bkey, []).append({
                    "user_id": uid,
                    "session_id": sid,
                    "week": week,
                    "region": region,
                    "indicator": indicator,
                    "value": value,
                    "honesty_gt": honesty.get(uid),
                    "core3": indicator in CORE3,
                })
    return union


def _alignment_rate(
    bucket_truths: dict[str, Any],
    union_gt: dict[str, list[dict[str, Any]]],
    *,
    core3_only: bool = False,
    honesty_weighted: bool = False,
) -> tuple[float | None, int]:
    """TD value vs union GT entries: mean I(td == gt_i) over all union pairs."""
    hits = 0.0
    total = 0.0
    for bkey, entries in union_gt.items():
        bt = bucket_truths.get(bkey)
        if not bt or not bt.value:
            continue
        td_val = bt.value
        for e in entries:
            if core3_only and not e.get("core3"):
                continue
            total += 1.0
            match = 1.0 if td_val == e["value"] else 0.0
            if honesty_weighted:
                w = float(e.get("honesty_gt") or 0.5)
                hits += w * match
            else:
                hits += match
    if total == 0:
        return None, 0
    return hits / total, int(total)


def _plurality_accuracy(
    bucket_truths: dict[str, Any],
    union_gt: dict[str, list[dict[str, Any]]],
    *,
    core3_only: bool = False,
) -> tuple[float | None, int]:
    """Per bucket: TD vs plurality of union GT values; mean over judged buckets."""
    correct = 0
    judged = 0
    for bkey, entries in union_gt.items():
        bt = bucket_truths.get(bkey)
        if not bt or not bt.value:
            continue
        vals = [e["value"] for e in entries if not core3_only or e.get("core3")]
        if not vals:
            continue
        judged += 1
        if bt.value == majority_vote(vals):
            correct += 1
    if judged == 0:
        return None, 0
    return correct / judged, judged


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
    union_gt = load_union_gt(args.preset, honesty)

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
        gt_entries = union_gt.get(bkey, [])
        gt_values = [e["value"] for e in gt_entries]
        plurality = majority_vote(gt_values) if gt_values else None
        row: dict[str, Any] = {
            "bucket": bkey,
            "n_sources": len(sources),
            "n_claims": len(bclaims),
            "td_value": bt.value if bt else None,
            "td_confidence": round(bt.confidence, 4) if bt else None,
            "values": sorted({c.value for c in bclaims}),
            "union_gt_n": len(gt_entries),
            "union_gt_values": sorted(set(gt_values)),
            "union_gt_plurality": plurality,
        }
        if gt_entries and bt and bt.value:
            row["td_union_matches"] = sum(1 for e in gt_entries if e["value"] == bt.value)
            row["td_union_alignment"] = round(row["td_union_matches"] / len(gt_entries), 4)
            row["td_plurality_match"] = bool(plurality and bt.value == plurality)
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

    # Shared world_truth (beta_v2): single canonical answer per bucket
    judged = [r for r in bucket_rows if "td_correct" in r]
    td_acc = (sum(1 for r in judged if r["td_correct"]) / len(judged)) if judged else None

    # Union GT (beta_v1+): per-user session claims_truth merged per bucket
    union_align, union_n = _alignment_rate(bucket_truths, union_gt)
    union_align_core3, union_n_core3 = _alignment_rate(
        bucket_truths, union_gt, core3_only=True,
    )
    union_align_honest, _ = _alignment_rate(
        bucket_truths, union_gt, honesty_weighted=True,
    )
    plurality_acc, plurality_n = _plurality_accuracy(bucket_truths, union_gt)
    plurality_acc_core3, plurality_n_core3 = _plurality_accuracy(
        bucket_truths, union_gt, core3_only=True,
    )

    if judged:
        calib_note = "world_truth present — shared-bucket calibration valid"
    else:
        calib_note = (
            "union GT: session claims_truth 按桶取并集（允许同桶多值）；"
            "td_union_gt_alignment = TD 与每条用户 GT 的一致率。"
            "beta_v2 另提供 td_world_truth_accuracy（共享世界态）。"
        )

    out = {
        "preset": args.preset,
        "fusion_mode": args.fusion_mode,
        "n_users": len(users),
        "n_claims": len(claims),
        "n_buckets": len(by_bucket),
        "n_multi_source_buckets": multi_source,
        "n_union_gt_buckets": sum(1 for v in union_gt.values() if v),
        "n_union_gt_pairs": union_n,
        "reliability_pearson": {"pearson_r": pearson, "n": len(xs)},
        "td_world_truth_accuracy": td_acc,
        "world_truth_buckets_judged": len(judged),
        "td_union_gt_alignment": round(union_align, 4) if union_align is not None else None,
        "td_union_gt_alignment_core3": (
            round(union_align_core3, 4) if union_align_core3 is not None else None
        ),
        "td_union_gt_alignment_honesty_weighted": (
            round(union_align_honest, 4) if union_align_honest is not None else None
        ),
        "td_plurality_gt_accuracy": (
            round(plurality_acc, 4) if plurality_acc is not None else None
        ),
        "td_plurality_gt_accuracy_core3": (
            round(plurality_acc_core3, 4) if plurality_acc_core3 is not None else None
        ),
        "union_gt_pairs_judged": union_n,
        "union_gt_buckets_plurality_judged": plurality_n,
        "union_gt_scope": "session claims_truth union per (week, region, indicator)",
        "note": calib_note,
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
