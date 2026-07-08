from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

_MOCK_PREFIX = "[mock-llm]"
_DEFAULT_POLARPRIVATE_PORT = "12790"


def _polarprivate_host_port() -> tuple[str, str]:
    url = os.environ.get("POLARPRIVATE_URL", "").strip().rstrip("/")
    if url:
        # Accept http://127.0.0.1:12790 or .../v1
        cleaned = url.replace("/v1", "")
        if "://" in cleaned:
            from urllib.parse import urlparse

            parsed = urlparse(cleaned)
            host = parsed.hostname or "127.0.0.1"
            port = str(parsed.port or _DEFAULT_POLARPRIVATE_PORT)
            return host, port
    port = os.environ.get("POLARPRIVATE_PORT", _DEFAULT_POLARPRIVATE_PORT)
    return "127.0.0.1", port


def polarprivate_health() -> dict[str, Any] | None:
    """Return health JSON if PolarPrivate responds; else None."""
    host, port = _polarprivate_host_port()
    try:
        with urlopen(f"http://{host}:{port}/health", timeout=2) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, OSError, json.JSONDecodeError, TimeoutError):
        return None


def polarprivate_available() -> bool:
    health = polarprivate_health()
    return bool(health and health.get("status") == "ok" and health.get("vault_unlocked"))


def polarprivate_base_url() -> str | None:
    explicit = os.environ.get("POLARPRIVATE_URL", "").strip().rstrip("/")
    backend = os.environ.get("MTA_LLM_BACKEND", "").strip().lower()
    if explicit:
        return explicit if explicit.endswith("/v1") else f"{explicit}/v1"
    if backend == "polarprivate" or polarprivate_available():
        host, port = _polarprivate_host_port()
        return f"http://{host}:{port}/v1"
    return None


def llm_mode() -> str:
    """Return ``mock`` or ``live``."""
    explicit = os.environ.get("MTA_LLM_MODE", "").strip().lower()
    if explicit in {"mock", "live"}:
        return explicit
    if polarprivate_available():
        return "live"
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("POLARPRIVATE_API_KEY"):
        return "live"
    return "mock"


def _api_key() -> str:
    if polarprivate_base_url():
        return os.environ.get("POLARPRIVATE_API_KEY") or os.environ.get("OPENAI_API_KEY") or "local"
    key = os.environ.get("POLARPRIVATE_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError(
            "MTA_LLM_MODE=live but no PolarPrivate proxy and no OPENAI_API_KEY set"
        )
    return key


def _base_url() -> str | None:
    pp = polarprivate_base_url()
    if pp:
        return pp
    return os.environ.get("OPENAI_BASE_URL") or os.environ.get("POLARPRIVATE_BASE_URL")


def _model_name() -> str:
    return os.environ.get("MTA_LLM_MODEL", "0001")


def llm_backend_label() -> str:
    if llm_mode() == "mock":
        return "mock"
    if polarprivate_base_url():
        return "polarprivate"
    return "openai-compatible"


def extract_json_object(text: str) -> dict[str, Any]:
    """Parse JSON object from LLM output, tolerating fenced code blocks."""
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, re.DOTALL)
    if fence:
        stripped = fence.group(1)
    else:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start != -1 and end != -1 and end > start:
            stripped = stripped[start : end + 1]
    return json.loads(stripped)


def _mock_completion(system: str, user: str) -> str:
    """Deterministic stub for CI — not used as production dialogue."""
    role = "agent"
    if any(k in system for k in ("模拟客户", "客户模拟器", "Customer simulator", "CustomerAgent")):
        role = "customer"
    if role == "agent":
        skill_id = "cover-qa"
        for token in (
            "clarification-probe",
            "info-seeking-inference",
            "bayesian-tom",
            "implicit-user-modeling",
            "reactance-biased-statement",
            "socratic-probe",
            "trap-question",
            "info-design-disclosure",
            "info-manipulation-bias",
            "cognitive-conflict-probe",
            "cover-qa",
        ):
            if token in system:
                skill_id = token
                break
        return json.dumps(
            {
                "utterance": (
                    f"{_MOCK_PREFIX} [{skill_id}] 您好，想了解下您这边最近铁矿石经营情况，"
                    "港口库存和采购节奏方便聊聊吗？"
                ),
                "phase": "PROBE",
            },
            ensure_ascii=False,
        )
    return json.dumps(
        {
            "utterance": (
                f"{_MOCK_PREFIX} 青岛港这边港存中等，采购积极性一般，"
                "报价暂时还没明显松动。"
            )
        },
        ensure_ascii=False,
    )


def _live_completion(system: str, user: str, *, temperature: float) -> str:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_openai import ChatOpenAI

    kwargs: dict[str, Any] = {
        "model": _model_name(),
        "temperature": temperature,
        "api_key": _api_key(),
    }
    base_url = _base_url()
    if base_url:
        kwargs["base_url"] = base_url

    model = ChatOpenAI(**kwargs)
    response = model.invoke([SystemMessage(content=system), HumanMessage(content=user)])
    content = getattr(response, "content", str(response))
    if isinstance(content, list):
        content = "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


def chat_completion(system: str, user: str, *, temperature: float = 0.7) -> str:
    if llm_mode() == "mock":
        return _mock_completion(system, user)
    return _live_completion(system, user, temperature=temperature)


def parse_utterance(raw: str) -> str:
    """Extract ``utterance`` field when model returns JSON; else return trimmed text."""
    text = raw.strip()
    if text.startswith("{"):
        try:
            payload = extract_json_object(text)
            utterance = payload.get("utterance")
            if isinstance(utterance, str) and utterance.strip():
                return utterance.strip()
        except json.JSONDecodeError:
            pass
    return text
