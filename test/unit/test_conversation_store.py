from market_truth_agent.storage.conversation_store import ConversationStore


def test_save_and_load_conversation(tmp_path, sample_conversation):
    store = ConversationStore(tmp_path / "test.db")
    store.save(sample_conversation)
    loaded = store.load(sample_conversation.conversation_id)
    assert loaded is not None
    assert len(loaded.turns) == 3
    assert loaded.turns[1].speaker == "user"
    assert store.list_ids() == [sample_conversation.conversation_id]
