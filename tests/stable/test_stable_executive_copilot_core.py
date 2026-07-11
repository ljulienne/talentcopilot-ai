from talentcopilot.executive_copilot import ExecutiveCopilotEngine, QuestionCatalog, QuestionRouter
from talentcopilot.intelligence_core.engine import DecisionEngine, InsightEngine


def _insight(identifier: str, category: str, severity: str = "High"):
    return InsightEngine().build(
        insight_id=identifier,
        title=f"{category} exposure",
        category=category,
        severity=severity,
        confidence=0.86,
        current_situation=f"A {category.lower()} issue was detected.",
        business_impact="Business continuity may be affected.",
        evidence=[{"label": "Signal", "detail": "Detected", "strength": 0.9}],
        recommendations=[{
            "action": f"Address {category.lower()} exposure",
            "priority": "Immediate",
            "timeframe": "30 days",
            "business_value": "Continuity",
        }],
    )


def test_catalog_exposes_known_questions_and_followups():
    catalog = QuestionCatalog()
    question = catalog.get("HR-RISK-001")
    assert question is not None
    assert question.required_engines
    assert catalog.follow_ups(question)


def test_router_matches_skills_question_and_defaults_to_overview():
    router = QuestionRouter()
    assert router.route("Which skills are rare?").question.question_id == "HR-SKILL-001"
    assert router.route("").question.question_id == "HR-OVERVIEW-001"


def test_copilot_filters_sources_and_returns_structured_response():
    insights = [
        _insight("skills-1", "Skills"),
        _insight("workforce-1", "Workforce", "Critical"),
        _insight("collab-1", "Collaboration", "Medium"),
    ]
    queue = DecisionEngine().generate(insights)
    response = ExecutiveCopilotEngine().answer(
        insights=insights,
        decision_queue=queue,
        question_id="HR-SKILL-001",
    )
    assert response.question.question_id == "HR-SKILL-001"
    assert set(response.answer.sources).issubset({"Skills", "Knowledge"})
    assert 0 <= response.executive_health_score <= 100
    assert response.data_readiness in {"High", "Medium", "Low"}
    assert response.suggested_questions


def test_copilot_does_not_invent_when_relevant_data_is_missing():
    response = ExecutiveCopilotEngine().answer(
        insights=[_insight("collab-1", "Collaboration")],
        question_id="HR-SKILL-001",
    )
    assert response.answer.confidence == 0
    assert response.data_readiness == "Low"
    assert "No executive conclusion" in response.answer.summary
