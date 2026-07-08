#!/usr/bin/env python3
"""Generate smoke dataset: 3 users × 20 turns via dual-agent simulation."""
import json
import sys
from pathlib import Path

from market_truth_agent.agents.customer_agent.personas import SMOKE_PERSONAS
from market_truth_agent.agents.eval.smoke_runner import validate_smoke_dataset
from market_truth_agent.agents.simulation.runner import SimulationRunner


def main() -> None:
    out = SimulationRunner(Path("benchmark/datasets/smoke_v1")).write_smoke_dataset(
        SMOKE_PERSONAS,
        min_turns=20,
    )
    smoke = validate_smoke_dataset(out)
    payload = {
        "output_dir": str(out),
        "users": len(SMOKE_PERSONAS),
        "turns_per_user": 20,
        "smoke_gate": smoke,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not smoke.get("passed"):
        sys.exit(1)


if __name__ == "__main__":
    main()
