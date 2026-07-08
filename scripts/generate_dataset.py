#!/usr/bin/env python3
"""Generate smoke dataset: 3 users × 20 turns via dual-agent simulation."""
import json
from pathlib import Path

from market_truth_agent.agents.customer_agent.personas import SMOKE_PERSONAS
from market_truth_agent.agents.simulation.runner import SimulationRunner


def main() -> None:
    runner = SimulationRunner(Path("benchmark/datasets/smoke_v1"))
    out = runner.write_smoke_dataset(SMOKE_PERSONAS, min_turns=20)
    print(json.dumps({"output_dir": str(out), "users": len(SMOKE_PERSONAS), "turns_per_user": 20}, ensure_ascii=False))


if __name__ == "__main__":
    main()
