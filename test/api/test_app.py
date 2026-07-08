import pytest

pytestmark = pytest.mark.skip(reason="M5 演示 UI 暂缓，见 roadmap")

from market_truth_agent.api.app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "app.db"))
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
