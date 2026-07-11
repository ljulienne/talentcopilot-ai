from talentcopilot.executive_reasoning import ExecutivePriority, ExecutiveReasoningEngine
from talentcopilot.intelligence_core.engine import DecisionEngine, InsightEngine


def _insight(identifier: str, category: str, severity: str, confidence: float):
    return InsightEngine().build(
        insight_id=identifier,
        title=f"{category} exposure",
        category=category,
        severity=severity,
        confidence=confidence,
        current_situation=f"A {category.lower()} issue was detected.",
        business_impact="Business continuity may be affected.",
        evidence=[
            {"label": "Signal", "detail": "Detected", "strength": 0.9},
            {"label": "Coverage", "detail": "Limited", "strength": 0.8},
        ],
        recommendations=[
            {
                "action": f"Address {category.lower()} exposure",
                "priority": "Immediate",
                "timeframe": "30 days",
                "business_value": "Continuity",
            }
        ],
    )


def test_reasoning_engine_prioritizes_and_traces_sources():
    insights = [
        _insight("skills-1", "Skills", "High", 0.9),
        _insight("workforce-1", "Workforce", "Critical", 0.85),
        _insight("collab-1", "Collaboration", "Medium", 0.75),
    ]
    queue = DecisionEngine().generate(insights)
    answer = ExecutiveReasoningEngine().reason(insights, queue)

    assert answer.priority == ExecutivePriority.CRITICAL
    assert answer.confidence > 0
    assert answer.evidence
    assert answer.actions
    assert set(answer.sources) == {"Skills", "Workforce", "Collaboration"}
    assert len(answer.decision_trace) == 3
    assert 0 < answer.engine_coverage <= 1


def test_reasoning_engine_deduplicates_evidence_and_recommendations():
    insight = _insight("skills-1", "Skills", "High", 0.9)
    answer = ExecutiveReasoningEngine().reason([insight, insight])
    assert len(answer.recommendations) == 1
    assert len(answer.evidence) == 2


def test_reasoning_engine_handles_empty_input_without_invention():
    answer = ExecutiveReasoningEngine().reason([])
    assert answer.priority == ExecutivePriority.LOW
    assert answer.confidence == 0
    assert answer.evidence == ()
    assert answer.missing_data
    assert "No executive conclusion" in answer.summary
