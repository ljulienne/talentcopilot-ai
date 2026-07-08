from talentcopilot.ai.evidence_intelligence import EvidenceIntelligenceEngine


def test_evidence_intelligence_rates_strong_evidence():
    engine = EvidenceIntelligenceEngine()

    report = engine.analyze([
        "Led HRIS rollout across 5 countries and improved adoption by 35%."
    ])

    item = report.evidence_items[0]

    assert report.overall_quality_score >= 70
    assert item.quality.level in {"strong", "exceptional"}
    assert "Project Management" in item.inferred_competencies
    assert "Business Impact" in item.inferred_competencies


def test_evidence_intelligence_detects_weak_evidence():
    engine = EvidenceIntelligenceEngine()

    report = engine.analyze([
        "Participated in HR projects."
    ])

    item = report.evidence_items[0]

    assert item.quality.score < 70
    assert item.limitations
    assert item.claim_type == "participation"


def test_evidence_intelligence_handles_empty_input():
    engine = EvidenceIntelligenceEngine()

    report = engine.analyze([])

    assert report.overall_quality_score == 0
    assert report.overall_quality_level == "unknown"
    assert report.evidence_items == []
