from __future__ import annotations

import math
from typing import Any

from market_truth_agent.analysis.ontology import normalize_value
from market_truth_agent.analysis.truth_discovery import TruthDiscoveryEngine
from market_truth_agent.models import Claim


ClaimSlot = tuple[str, str]  # (region, indicator)


def _norm_value(raw: str, indicator: str) -> str:
    val = normalize_value(raw, indicator) or raw.strip()
    return val


def latent_slots(latent_claims: list[dict[str, Any]]) -> dict[ClaimSlot, str]:
    out: dict[ClaimSlot, str] = {}
    for item in latent_claims:
        region = item.get("region", "")
        indicator = item.get("indicator", "")
        value = str(item.get("value", ""))
        if region and indicator and value:
            out[(region, indicator)] = value
    return out


def predicted_slots(claims: list[Claim]) -> dict[ClaimSlot, str]:
    """Last claim wins per (region, indicator) slot."""
    out: dict[ClaimSlot, str] = {}
    for claim in claims:
        out[(claim.region, claim.indicator)] = claim.value
    return out


def claim_f1_vs_latent(
    claims: list[Claim],
    latent_claims: list[dict[str, Any]],
) -> dict[str, float | int]:
    gt = latent_slots(latent_claims)
    pred = predicted_slots(claims)
    keys = set(gt) | set(pred)
    tp = fp = fn = 0
    for key in keys:
        g = gt.get(key)
        p = pred.get(key)
        if g is not None and p is not None:
            if p == g:
                tp += 1
            else:
                fp += 1
                fn += 1
        elif g is not None:
            fn += 1
        else:
            fp += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "gt_slots": len(gt),
        "pred_slots": len(pred),
    }


def pearson_correlation(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2 or len(ys) != n:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def pearson_reliability_honesty(
    users: list[dict[str, Any]],
) -> dict[str, float | int | None]:
    """users items need honesty_gt and reliability_est (float|None)."""
    pairs = [
        (float(u["honesty_gt"]), float(u["reliability_est"]))
        for u in users
        if u.get("reliability_est") is not None
    ]
    if len(pairs) < 2:
        return {"pearson_r": None, "n": len(pairs)}
    xs, ys = zip(*pairs)
    return {"pearson_r": pearson_correlation(list(xs), list(ys)), "n": len(pairs)}


def bucket_ground_truth(latent_claims: list[dict[str, Any]], week: str) -> dict[str, str]:
    from market_truth_agent.analysis.ontology import canonicalize

    out: dict[str, str] = {}
    for item in latent_claims:
        region = item.get("region", "青岛港")
        indicator = item.get("indicator", "")
        value = str(item.get("value", ""))
        market_object = item.get("market_object", "铁矿石")
        if not indicator or not value:
            continue
        _, bucket_key = canonicalize(region, market_object, indicator, week)
        out[bucket_key] = value
    return out


def em_vs_mv_errors(
    claims: list[Claim],
    latent_claims: list[dict[str, Any]],
    week: str,
    external_consistency_fn,
) -> dict[str, float]:
    gt = bucket_ground_truth(latent_claims, week)
    if not gt or not claims:
        return {"em_error": 0.0 if not gt else 1.0, "mv_error": 0.0 if not gt else 1.0}

    engine = TruthDiscoveryEngine()
    bucket_truths, _ = engine.infer(claims, external_consistency_fn)
    em_pred = {k: v.value for k, v in bucket_truths.items()}
    mv_pred = engine.majority_voting_baseline(claims)
    return {
        "em_error": engine.bucket_error_rate(em_pred, gt),
        "mv_error": engine.bucket_error_rate(mv_pred, gt),
    }
