from __future__ import annotations

from typing import Any

from market_truth_agent.agents.eval.claim_metrics import (
    claim_f1_vs_latent,
    em_vs_mv_errors,
    pearson_correlation,
)
from market_truth_agent.analysis.external_validator import external_consistency
from market_truth_agent.analysis.fusion import FUSION_MODES, fuse_session, fused_to_slot_dict
from market_truth_agent.analysis.pipeline import AnalysisPipeline, PipelineConfig
from market_truth_agent.models import AnalysisResult, Claim, Conversation, Persona
from market_truth_agent.utils.progress import progress


def slot_metrics(
    claims: list[Claim],
    latent_claims: list[dict[str, Any]],
    *,
    pred: dict[tuple[str, str], str] | None = None,
) -> dict[str, float | int]:
    """Normalize/Claim slot-level: recall & precision (prediction accuracy)."""
    m = claim_f1_vs_latent(claims, latent_claims, pred=pred)
    return {
        "tp": m["tp"],
        "fp": m["fp"],
        "fn": m["fn"],
        "recall": m["recall"],
        "precision": m["precision"],
        "f1": m["f1"],
        "slot_recall": m["recall"],
        "slot_precision": m["precision"],
        "prediction_accuracy": m["precision"],
        "gt_slots": m["gt_slots"],
        "pred_slots": m["pred_slots"],
    }


def fusion_slot_metrics(
    conversation: Conversation,
    claims: list[Claim],
    latent_claims: list[dict[str, Any]],
    *,
    week: str,
    default_region: str = "青岛港",
    modes: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    """Ablation: llm / voting / last_wins slot metrics for one session."""
    run_modes = modes or FUSION_MODES
    out: dict[str, Any] = {}
    for mode in run_modes:
        fused = fuse_session(
            conversation,
            claims,
            mode=mode,
            default_region=default_region,
            week=week,
        )
        pred = fused_to_slot_dict(fused)
        metrics = slot_metrics(claims, latent_claims, pred=pred)
        out[mode] = {
            **metrics,
            "fused_slots": {
                f"{r}/{i}": {
                    "value": s.value,
                    "confidence": s.confidence,
                    "evidence_turns": s.evidence_turns,
                }
                for (r, i), s in fused.items()
            },
        }
    return out


def veracity_metrics(
    result: AnalysisResult,
    latent_claims: list[dict[str, Any]],
    week: str,
    price_trajectory: list[dict],
) -> dict[str, float]:
    """Truth Discovery bucket-level veracity vs latent."""
    ext_fn = lambda c: external_consistency(c, price_trajectory)
    bucket_err = em_vs_mv_errors(result.claims, latent_claims, week, ext_fn)
    em_acc = 1.0 - bucket_err["em_error"]
    mv_acc = 1.0 - bucket_err["mv_error"]
    return {
        "em_error": bucket_err["em_error"],
        "mv_error": bucket_err["mv_error"],
        "bucket_veracity_accuracy": em_acc,
        "mv_baseline_accuracy": mv_acc,
    }


def recon_honesty_correlation(
    mean_deception: float,
    honesty_gt: float,
) -> dict[str, float | None]:
    """Single-user helper; aggregate via recon_honesty_pearson."""
    return {
        "mean_deception": mean_deception,
        "honesty_gt": honesty_gt,
        "deception_inverse_honesty_gap": abs(mean_deception - (1.0 - honesty_gt)),
    }


def recon_honesty_pearson(rows: list[dict[str, Any]]) -> dict[str, float | int | None]:
    """Expect negative correlation: high honesty → low deception."""
    pairs = [
        (float(r["mean_deception"]), float(r["honesty_gt"]))
        for r in rows
        if r.get("mean_deception") is not None
    ]
    if len(pairs) < 2:
        return {"pearson_r": None, "n": len(pairs)}
    xs, ys = zip(*pairs)
    return {"pearson_r": pearson_correlation(list(xs), list(ys)), "n": len(pairs)}


def external_metrics(claims: list[Claim], price_trajectory: list[dict]) -> dict[str, float]:
    if not claims:
        return {"external_consistency_mean": 0.0}
    scores = [external_consistency(c, price_trajectory) for c in claims]
    return {"external_consistency_mean": sum(scores) / len(scores)}


def escalation_metrics(result: AnalysisResult, claim_count: int) -> dict[str, float | int]:
    flagged = len(result.escalation_flags)
    return {
        "escalation_count": flagged,
        "escalation_rate": flagged / claim_count if claim_count else 0.0,
    }


def reliability_metrics(
    result: AnalysisResult,
    persona: Persona,
) -> dict[str, float | None]:
    rel = result.user_reliability.get(persona.user_id)
    return {
        "reliability_est": rel,
        "honesty_gt": persona.honesty,
    }


def _default_region_for_persona(persona: Persona) -> str:
    return getattr(persona, "region", None) or "青岛港"


def evaluate_session(
    conversation: Conversation,
    persona: Persona,
    latent_claims: list[dict[str, Any]],
    *,
    week: str,
    price_trajectory: list[dict],
    pipeline_config: PipelineConfig | None = None,
    fusion_mode: str = "llm",
    run_fusion_ablation: bool = True,
) -> dict[str, Any]:
    """Full metric bundle for one session.

    Primary slot_metrics use ``fusion_mode`` (default llm). When
    ``run_fusion_ablation`` is True, also report llm/voting/last_wins side-by-side.
    """
    pipeline = AnalysisPipeline(price_trajectory=price_trajectory, config=pipeline_config)
    result = pipeline.run(conversation, persona, week=week)
    meta = pipeline.last_run_meta
    default_region = _default_region_for_persona(persona)

    fusion_all = fusion_slot_metrics(
        conversation,
        result.claims,
        latent_claims,
        week=week,
        default_region=default_region,
        modes=FUSION_MODES if run_fusion_ablation else (fusion_mode,),
    )
    primary = fusion_all.get(fusion_mode) or next(iter(fusion_all.values()))
    slots = {k: v for k, v in primary.items() if k != "fused_slots"}

    veracity = veracity_metrics(result, latent_claims, week, price_trajectory)
    ext = external_metrics(result.claims, price_trajectory)
    esc = escalation_metrics(result, len(result.claims))
    rel = reliability_metrics(result, persona)
    recon_row = recon_honesty_correlation(
        meta.mean_deception if meta else 0.0,
        persona.honesty,
    )
    return {
        "session_id": conversation.conversation_id,
        "claim_count": len(result.claims),
        "pipeline": {
            "enable_normalize": pipeline.config.enable_normalize,
            "max_turns": pipeline.config.max_turns,
            "mean_deception": meta.mean_deception if meta else 0.0,
            "fusion_mode": fusion_mode,
        },
        "slot_metrics": slots,
        "fusion_ablation": fusion_all if run_fusion_ablation else None,
        "veracity": veracity,
        "external": ext,
        "escalation": esc,
        "reliability": rel,
        "recon": recon_row,
    }


def run_ablation_suite(
    conversation: Conversation,
    persona: Persona,
    latent_claims: list[dict[str, Any]],
    *,
    week: str,
    price_trajectory: list[dict],
    turn_limits: list[int | None] | None = None,
) -> dict[str, Any]:
    """Ablation: full vs no-normalize vs turn truncation."""
    limits = turn_limits or [None, 6, 12, 20]
    variants: list[dict[str, Any]] = []

    configs = [
        ("full", PipelineConfig(enable_normalize=True, max_turns=None)),
        ("ablate_normalize", PipelineConfig(enable_normalize=False, max_turns=None)),
    ]
    for name, cfg in configs:
        progress(f"[ablation] variant={name} normalize={cfg.enable_normalize} max_turns={cfg.max_turns}")
        report = evaluate_session(
            conversation, persona, latent_claims,
            week=week, price_trajectory=price_trajectory, pipeline_config=cfg,
            run_fusion_ablation=False,
        )
        variants.append({"variant": name, **report})

    for limit in limits:
        if limit is None:
            continue
        cfg = PipelineConfig(enable_normalize=True, max_turns=limit)
        progress(f"[ablation] variant=turns_{limit} max_turns={limit}")
        report = evaluate_session(
            conversation, persona, latent_claims,
            week=week, price_trajectory=price_trajectory, pipeline_config=cfg,
            run_fusion_ablation=False,
        )
        variants.append({
            "variant": f"turns_{limit}",
            **report,
        })

    return {"ablations": variants}
