#!/usr/bin/env python3
"""Generate Tier B dataset via dual-agent simulation (smoke or alpha preset)."""
import argparse
import json
import sys
from pathlib import Path

from market_truth_agent.agents.customer_agent.personas import DATASET_PRESETS
from market_truth_agent.agents.eval.smoke_runner import validate_smoke_dataset
from market_truth_agent.agents.simulation.runner import SimulationRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Tier B agent dataset")
    parser.add_argument(
        "--preset",
        choices=sorted(DATASET_PRESETS),
        default="smoke_v1",
        help="Dataset preset (smoke_v1 or alpha_v1)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output directory (default: benchmark/datasets/<preset>)",
    )
    args = parser.parse_args()

    preset = DATASET_PRESETS[args.preset]
    out_dir = args.output or Path("benchmark/datasets") / args.preset
    runner = SimulationRunner(out_dir)
    out = runner.write_dataset(
        preset["personas"],
        version=args.preset,
        min_turns=preset["min_turns"],
        sessions_per_user=preset["sessions_per_user"],
    )
    gate = validate_smoke_dataset(out)
    payload = {
        "preset": args.preset,
        "output_dir": str(out),
        "users": len(preset["personas"]),
        "sessions_per_user": preset["sessions_per_user"],
        "turns_per_session": preset["min_turns"],
        "smoke_gate": gate,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if not gate.get("passed"):
        sys.exit(1)


if __name__ == "__main__":
    main()
