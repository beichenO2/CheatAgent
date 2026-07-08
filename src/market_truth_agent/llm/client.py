from __future__ import annotations

import json
import os
import re
from typing import Any

_MOCK_PREFIX = "[mock-llm]"


def llm_mode() -> str:
    """Return ``mock`` or ``live``. Live requires API credentials."""
    explicit = os.environ.get("MTA_LLM_MODE", "").strip().lower()
    if explicit in {"mock", "live"}:
        return explicit
    if os.environ.get("OPENAI_API_KEY") or os.environ.get("POLARPRIVATE_API_KEY"):
        return "live"
    return "mock"


def _api_key() -> str | None:
    return os.environ.get("POLARPRIVATE_API_KEY") or os.environ.get("OPENAI_API_KEY")


def _base_url() -> str | None:
    return os.environ.get("OPENAI_BASE_URL") or os.environ.get("POLARPRIVATE_BASE_URL")


def _model_name() -> str:
    return os.environ.get("MTA_LLM_MODEL", "gpt-4o-mini")


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
    if "模拟客户" in system or "Customer simulator" in system:
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
                f"{_MOCK_PREFIX} 我们这边港口情况还可以，"
                "您具体想了解库存还是成交？"
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
    if not _api_key():
        raise RuntimeError(
            "MTA_LLM_MODE=live but no OPENAI_API_KEY or POLARPRIVATE_API_KEY set"
        )
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
