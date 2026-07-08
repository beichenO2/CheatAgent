"""Tier A synthetic truth discovery dataset (FaitCrowd-style mini)."""

TIER_A_CONFLICTS = [
    {"bucket": "b1", "source": "s1", "value": "高", "honesty": 0.9},
    {"bucket": "b1", "source": "s2", "value": "低", "honesty": 0.2},
    {"bucket": "b1", "source": "s3", "value": "高", "honesty": 0.85},
    {"bucket": "b1", "source": "s4", "value": "高", "honesty": 0.8},
    {"bucket": "b2", "source": "s1", "value": "积极", "honesty": 0.9},
    {"bucket": "b2", "source": "s2", "value": "消极", "honesty": 0.15},
    {"bucket": "b2", "source": "s3", "value": "积极", "honesty": 0.88},
    {"bucket": "b2", "source": "s5", "value": "消极", "honesty": 0.25},
]

GROUND_TRUTH = {"b1": "高", "b2": "积极"}
