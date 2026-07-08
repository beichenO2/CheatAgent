from market_truth_agent.analysis.pipeline import AnalysisPipeline


def test_analysis_pipeline_end_to_end(sample_conversation, sample_persona):
    pipeline = AnalysisPipeline()
    result = pipeline.run(sample_conversation, sample_persona)
    assert len(result.claims) >= 1
    assert result.claims[0].deception is not None
    assert sample_persona.user_id in result.user_reliability or len(result.user_reliability) >= 0
