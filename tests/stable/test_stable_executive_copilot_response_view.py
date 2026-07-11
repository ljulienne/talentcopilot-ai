from talentcopilot.executive_copilot import (
    CopilotResponse,
    QuestionCatalog,
    build_response_view,
)
from talentcopilot.executive_reasoning import (
    DecisionTraceStep,
    ExecutiveAnswer,
    ExecutivePriority,
    RegisteredEvidence,
)
from talentcopilot.ui.executive import render_copilot_response


def _response() -> CopilotResponse:
    question = QuestionCatalog().get("HR-RISK-001")
    assert question is not None
    answer = ExecutiveAnswer(
        summary="Payroll continuity requires executive attention.",
        priority=ExecutivePriority.HIGH,
        confidence=0.88,
        evidence=(
            RegisteredEvidence(
                evidence_id="ev-1",
                source_engine="Workforce",
                label="No ready successor",
                detail="The role has no internal successor above the readiness threshold.",
                confidence=0.91,
                severity="High",
            ),
        ),
        recommendations=("Build a succession plan",),
        actions=("Cross-train a payroll backup",),
        risks=("Payroll continuity",),
        sources=("Workforce",),
        missing_data=(),
        assumptions=("Current role data is up to date.",),
        decision_trace=(
            DecisionTraceStep(
                order=1,
                source_engine="Workforce",
                contribution="Identified succession exposure.",
                evidence_ids=("ev-1",),
            ),
        ),
        engine_coverage=0.8,
        evidence_quality="Good",
    )
    return CopilotResponse(
        question=question,
        answer=answer,
        executive_health_score=72,
        data_readiness="High",
        suggested_questions=QuestionCatalog().follow_ups(question),
    )


def test_response_view_maps_executive_answer():
    view = build_response_view(_response())
    assert view.question_id == "HR-RISK-001"
    assert view.priority == "High"
    assert view.confidence_percent == 88
    assert view.coverage_percent == 80
    assert view.business_impact == "High"
    assert view.evidence[0].source_engine == "Workforce"
    assert view.actions[0].title == "Cross-train a payroll backup"


def test_response_view_exposes_readiness_and_follow_ups():
    view = build_response_view(_response())
    assert view.is_decision_ready is True
    assert view.health_status == "Watch"
    assert len(view.suggested_questions) == 3


def test_response_renderer_is_import_safe():
    assert callable(render_copilot_response)
