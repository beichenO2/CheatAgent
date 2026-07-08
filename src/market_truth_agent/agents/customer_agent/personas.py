"""Persona presets and generators for Tier B dataset builds."""

from __future__ import annotations

from market_truth_agent.agents.customer_agent.graph import CustomerPersona
from market_truth_agent.benchmark.tier_b.price_data import ROLES, REGIONS, PERSONALITIES

SMOKE_PERSONAS = [
    CustomerPersona(
        user_id="U001",
        role="厂长",
        region="青岛港",
        position="long",
        personality="谨慎型",
        honesty=0.85,
        resistance=0.2,
    ),
    CustomerPersona(
        user_id="U002",
        role="贸易员",
        region="日照港",
        position="long",
        personality="健谈型",
        honesty=0.55,
        resistance=0.4,
    ),
    CustomerPersona(
        user_id="U003",
        role="仓库负责人",
        region="唐山",
        position="long",
        personality="防御型",
        honesty=0.25,
        resistance=0.6,
    ),
]

# 10 users — honesty spread for Pearson / reliability calibration
_ALPHA_SPECS: list[tuple[str, str, str, str, float, float]] = [
    ("U001", "厂长", "青岛港", "谨慎型", 0.85, 0.2),
    ("U002", "贸易员", "日照港", "健谈型", 0.55, 0.4),
    ("U003", "仓库负责人", "唐山", "防御型", 0.25, 0.6),
    ("U004", "厂长", "日照港", "谨慎型", 0.75, 0.25),
    ("U005", "贸易员", "青岛港", "投机型", 0.45, 0.5),
    ("U006", "仓库负责人", "青岛港", "健谈型", 0.65, 0.35),
    ("U007", "厂长", "唐山", "防御型", 0.35, 0.55),
    ("U008", "贸易员", "唐山", "谨慎型", 0.90, 0.15),
    ("U009", "仓库负责人", "日照港", "投机型", 0.40, 0.45),
    ("U010", "厂长", "青岛港", "健谈型", 0.50, 0.3),
]

ALPHA_PERSONAS = [
    CustomerPersona(
        user_id=uid,
        role=role,
        region=region,
        position="long",
        personality=personality,
        honesty=honesty,
        resistance=resistance,
    )
    for uid, role, region, personality, honesty, resistance in _ALPHA_SPECS
]

DATASET_PRESETS = {
    "smoke_v1": {"personas": SMOKE_PERSONAS, "sessions_per_user": 1, "min_turns": 20},
    "alpha_v1": {"personas": ALPHA_PERSONAS, "sessions_per_user": 5, "min_turns": 20},
}
