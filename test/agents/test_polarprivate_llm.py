from unittest.mock import patch

from market_truth_agent.llm.client import llm_backend_label, llm_mode, polarprivate_available


def test_polarprivate_auto_live_when_healthy(monkeypatch):
    monkeypatch.setenv("MTA_LLM_MODE", "")
    with patch("market_truth_agent.llm.client.polarprivate_health", return_value={"status": "ok", "vault_unlocked": True}):
        assert polarprivate_available() is True
        assert llm_mode() == "live"
        assert llm_backend_label() == "polarprivate"


def test_mock_when_no_proxy(monkeypatch):
    monkeypatch.setenv("MTA_LLM_MODE", "mock")
    assert llm_mode() == "mock"
    assert llm_backend_label() == "mock"
