#!/usr/bin/env bash
# Start cheatAgent HTTP workflow on :3945 (live LLM via PolarPrivate).
set -euo pipefail
cd "$(dirname "$0")/.."

# Prefer project-capable interpreter (agent-reach-venv has langgraph + fastapi).
if [[ -x "/Users/mac/.agent-reach-venv/bin/python3" ]]; then
  PYTHON="/Users/mac/.agent-reach-venv/bin/python3"
elif [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python" ]]; then
  PYTHON="${VIRTUAL_ENV}/bin/python"
else
  PYTHON="${PYTHON:-python3}"
fi

export PYTHONUNBUFFERED=1
export MTA_LLM_MODE="${MTA_LLM_MODE:-live}"
export POLARPRIVATE_URL="${POLARPRIVATE_URL:-http://127.0.0.1:12790}"
export MTA_LLM_MODEL="${MTA_LLM_MODEL:-0001}"
export MTA_HTTP_HOST="${MTA_HTTP_HOST:-0.0.0.0}"
export MTA_HTTP_PORT="${MTA_HTTP_PORT:-3945}"

# Ensure package import path
export PYTHONPATH="${PWD}/src${PYTHONPATH:+:$PYTHONPATH}"

# httpx/openai 会把 NO_PROXY 里的 IPv6「::1」误解析成 Invalid port ':1'
# （见 langchain ChatOpenAI 初始化）。启动前剔除 ::1 / [::1]。
_sanitize_no_proxy() {
  local raw="${1:-}"
  local out=()
  local IFS=','
  # shellcheck disable=SC2206
  local parts=($raw)
  for p in "${parts[@]}"; do
    p="$(echo "$p" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    [[ -z "$p" ]] && continue
    [[ "$p" == "::1" || "$p" == "[::1]" || "$p" == "::1/128" ]] && continue
    out+=("$p")
  done
  local IFS=','
  echo "${out[*]}"
}
export NO_PROXY="$(_sanitize_no_proxy "${NO_PROXY:-}")"
export no_proxy="$(_sanitize_no_proxy "${no_proxy:-${NO_PROXY:-}}")"

echo "[mta-http] python=$PYTHON mode=$MTA_LLM_MODE port=$MTA_HTTP_PORT"
exec "$PYTHON" -m uvicorn web_workflow_service:app \
  --app-dir service \
  --host "$MTA_HTTP_HOST" \
  --port "$MTA_HTTP_PORT"
