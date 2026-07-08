"""Tier B price trajectory and latent truth variants."""

# Weekly snapshots — expandable toward 5-month coverage (Alpha uses first 5)
PRICE_TRAJECTORY = [
    {"day": 1, "price": 820, "trend": "平", "week": "2026-W09"},
    {"day": 28, "price": 835, "trend": "涨", "week": "2026-W13"},
    {"day": 56, "price": 842, "trend": "涨", "week": "2026-W17"},
    {"day": 84, "price": 848, "trend": "涨", "week": "2026-W21"},
    {"day": 112, "price": 855, "trend": "涨", "week": "2026-W25"},
    {"day": 140, "price": 850, "trend": "平", "week": "2026-W29"},
    {"day": 168, "price": 838, "trend": "跌", "week": "2026-W33"},
]

ROLES = ["厂长", "贸易员", "仓库负责人"]
PERSONALITIES = ["谨慎型", "健谈型", "防御型", "投机型"]
REGIONS = ["青岛港", "日照港", "唐山"]

TRUTH_VARIANTS = [
    [("港存", "高"), ("采购积极性", "积极"), ("报价松动", "否")],
    [("港存", "中"), ("采购积极性", "中性"), ("报价松动", "否")],
    [("港存", "低"), ("采购积极性", "积极"), ("报价松动", "是")],
    [("港存", "高"), ("采购积极性", "消极"), ("报价松动", "是")],
    [("港存", "中"), ("采购积极性", "积极"), ("报价松动", "否")],
]
