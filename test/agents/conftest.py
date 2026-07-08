import os

import pytest


@pytest.fixture(autouse=True)
def _mock_llm_mode(monkeypatch):
    """Agent tests run without API credentials unless explicitly overridden."""
    monkeypatch.setenv("MTA_LLM_MODE", os.environ.get("MTA_LLM_MODE", "mock"))
