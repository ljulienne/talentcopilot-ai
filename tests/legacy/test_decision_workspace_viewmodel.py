from talentcopilot.ai.reasoning_engine import ReasoningEngine
from talentcopilot.ai.interview_intelligence import InterviewIntelligenceEngine
from talentcopilot.ai.recommendation_engine import RecommendationEngine
from talentcopilot.viewmodels.decision_workspace import (
    DecisionWorkspaceBuilder,
    DecisionWorkspaceViewModel,
)


def _build_reports():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Stakeholder Management"],
        "years_experience": 8,
        "achievements": ["Reduced processing time by 35%"],
    }

    job = {
        "title": "Transformation Lead",
        "required_skills": ["Project Management", "Stakeholder Management"],
        "preferred_skills": ["Change Management"],
        "years_experience": 5,
    }

    evidence = [
        {"text": "Led a transformation project across 4 countries."},
        {"text": "Managed executive stakeholders."},
    ]

    reasoning = ReasoningEngine().build_report(
        candidate=candidate,
        job=job,
        evidence=evidence,
        match_result={"score": 88},
    )

    interview = InterviewIntelligenceEngine().build_guide(reasoning)
    recommendation = RecommendationEngine().build_recommendation([reasoning])

    return reasoning, interview, recommendation


def test_decision_workspace_builder_creates_viewmodel():
    reasoning, interview, recommendation = _build_reports()

    view_model = DecisionWorkspaceBuilder().build(
        reasoning_report=reasoning,
        interview_guide=interview,
        recommendation_report=recommendation,
    )

    assert isinstance(view_model, DecisionWorkspaceViewModel)
    assert view_model.candidate_name == "Alice Martin"
    assert view_model.role_title == "Transformation Lead"
    assert view_model.executive_summary
    assert view_model.recommendation
    assert 0 <= view_model.decision_confidence <= 100
    assert 0 <= view_model.decision_readiness <= 100
    assert view_model.timeline
    assert view_model.metrics


def test_decision_workspace_timeline_contains_framework_steps():
    reasoning, interview, recommendation = _build_reports()

    view_model = DecisionWorkspaceBuilder().build(reasoning, interview, recommendation)

    step_names = [step.name for step in view_model.timeline]

    assert "Evidence" in step_names
    assert "Competencies" in step_names
    assert "Interview" in step_names
    assert "Recommendation" in step_names
    assert "Challenge" in step_names


def test_decision_workspace_remains_generic():
    reasoning, interview, recommendation = _build_reports()

    view_model = DecisionWorkspaceBuilder().build(reasoning, interview, recommendation)

    combined_text = " ".join(
        [
            view_model.candidate_name,
            view_model.role_title,
            view_model.executive_summary,
            view_model.recommendation,
        ]
    )

    assert "HRIS" not in combined_text
    assert "SIRH" not in combined_text
