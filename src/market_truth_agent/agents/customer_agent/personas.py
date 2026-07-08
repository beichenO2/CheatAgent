"""Smoke-test persona presets for dataset generation."""

from market_truth_agent.agents.customer_agent.graph import CustomerPersona

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
        honesty=0.25,  # strategic, position-driven — not "always lie"
        resistance=0.6,
    ),
]
