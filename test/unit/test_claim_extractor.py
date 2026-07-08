from market_truth_agent.analysis.claim_extractor import ClaimExtractor, ClaimEnricher, score_evidence_strength


def test_extract_claims_from_conversation(sample_conversation):
    extractor = ClaimExtractor()
    claims = extractor.extract_from_conversation(sample_conversation)
    assert len(claims) >= 1
    assert claims[0].indicator == "港存"
    assert claims[0].value == "高"


def test_enricher_evidence_with_numbers():
    enricher = ClaimEnricher()
    from market_truth_agent.models import Claim, ClaimProvenance
    claim = Claim(
        claim_id="1", source_id="U1", conversation_id="c1", time="t",
        region="青岛港", market_object="铁矿石", indicator="港存", value="高",
        claim_type="ordinal",
        provenance=ClaimProvenance("青岛港港存大约150万吨", 1),
    )
    enricher.enrich(claim)
    assert claim.evidence_strength >= 0.5


def test_rebuttal_channel_detected():
    from market_truth_agent.models import ConversationTurn
    from datetime import datetime, timezone
    extractor = ClaimExtractor()
    turn = ConversationTurn(
        3, "user", "谁说的？不对，我们青岛港港存其实很高。", datetime.now(timezone.utc).isoformat()
    )
    claims = extractor.extract_from_turn(turn, source_id="U1", conversation_id="c1")
    assert claims[0].provenance.elicitation_channel == "bias_triggered"
