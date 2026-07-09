#!/usr/bin/env bash
# Long-running beta benchmark with live logs + auto-resume.
set -euo pipefail
cd "$(dirname "$0")/.."

PRESET="${1:-beta_v1}"
LOG_DIR="benchmark/logs"
LOG_FILE="${LOG_DIR}/${PRESET}_pipeline.log"
mkdir -p "$LOG_DIR" benchmark/reports benchmark/datasets/"$PRESET"

export PYTHONUNBUFFERED=1
export POLARPRIVATE_URL="${POLARPRIVATE_URL:-http://127.0.0.1:12790}"
export MTA_LLM_MODE="${MTA_LLM_MODE:-live}"
export MTA_LLM_MODEL="${MTA_LLM_MODEL:-0001}"
export MTA_NORMALIZE_MODEL="${MTA_NORMALIZE_MODEL:-qwen3.7-plus}"
export MTA_RETRY_MAX="${MTA_RETRY_MAX:-8}"
export MTA_RETRY_BASE_DELAY="${MTA_RETRY_BASE_DELAY:-3}"

echo "[$(date '+%F %T')] starting pipeline preset=$PRESET log=$LOG_FILE" | tee -a "$LOG_FILE"

python scripts/run_benchmark_pipeline.py \
  --preset "$PRESET" \
  --phase all \
  --resume \
  2>&1 | tee -a "$LOG_FILE"

echo "[$(date '+%F %T')] pipeline finished preset=$PRESET" | tee -a "$LOG_FILE"
