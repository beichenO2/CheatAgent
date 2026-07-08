import os

import pytest


@pytest.fixture(autouse=True)
def _mock_llm_mode(monkeypatch):
    """Agent tests run without API credentials unless MTA_LLM_MODE already set."""
    if "MTA_LLM_MODE" not in os.environ:
        monkeypatch.setenv("MTA_LLM_MODE", "mock")
