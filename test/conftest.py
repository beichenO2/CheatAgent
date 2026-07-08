import pytest
from datetime import datetime, timezone

from market_truth_agent.models import Conversation, ConversationTurn, Persona, TruthClaim


@pytest.fixture
def sample_persona():
    return Persona(
        user_id="U001",
        role="厂长",
        personality="谨慎型",
        position="long",
        honesty=0.8,
        region="青岛港",
        knowledge_depth=0.8,
    )


@pytest.fixture
def sample_truths():
    return [
        TruthClaim(region="青岛港", indicator="港存", value="高"),
        TruthClaim(region="青岛港", indicator="采购积极性", value="积极"),
    ]


@pytest.fixture
def sample_conversation():
    conv = Conversation(
        conversation_id="c1",
        user_id="U001",
        started_at=datetime.now(timezone.utc).isoformat(),
        turns=[
            ConversationTurn(0, "agent", "今天铁矿石价格如何？", datetime.now(timezone.utc).isoformat()),
            ConversationTurn(1, "user", "青岛港港存偏高，大概还是比较充足的。", datetime.now(timezone.utc).isoformat()),
            ConversationTurn(2, "user", "采购积极性不错，询盘增多。", datetime.now(timezone.utc).isoformat()),
        ],
    )
    return conv
