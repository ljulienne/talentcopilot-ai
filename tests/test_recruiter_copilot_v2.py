from talentcopilot.ai.recruiter_copilot_engine import RecruiterCopilotEngine
from talentcopilot.models.decision import (
    DecisionConcern,
    DecisionConfidence,
    DecisionReport,
    HiringRecommendation,
    HumanValidationLevel,
)


def test_recruiter_copilot_generates_actions_and_questions():
    decision = DecisionReport(
        candidate_name="Alice Martin",
        role_title="Transformation Lead",
        recommendation=HiringRecommendation.HIRE,
        decision_score=78,
        confidence=DecisionConfidence.MEDIUM,
        human_validation=HumanValidationLevel.RECOMMENDED,
        executive_summary="Continue process.",
        concerns=[
            DecisionConcern(
                title="Cloud",
                severity="Medium",
                explanation="Cloud evidence is limited.",
                mitigation="Validate cloud project depth.",
            )
        ],
        interview_focus=["Validate stakeholder management depth."],
    )

    report = RecruiterCopilotEngine().advise(
        candidate={"name": "Alice Martin"},
        job={"title": "Transformation Lead"},
        decision_report=decision,
    )

    assert report.candidate_name == "Alice Martin"
    assert report.role_title == "Transformation Lead"
    assert report.action_count >= 1
    assert len(report.interview_questions) >= 1
    assert "Recommendation" in report.recruiter_summary


def test_recruiter_copilot_handles_minimal_decision_report_dict():
    decision = {
        "candidate_name": "Bob",
        "role_title": "Data Engineer",
        "recommendation": "Review Carefully",
        "decision_score": 62,
        "confidence": "Low",
        "human_validation": "Strongly Recommended",
        "concerns": [],
        "missing_information": ["Recent Python evidence"],
        "interview_focus": [],
    }

    report = RecruiterCopilotEngine().advise(
        candidate={},
        job={},
        decision_report=decision,
    )

    assert report.candidate_name == "Bob"
    assert report.role_title == "Data Engineer"
    assert report.has_high_priority_alerts is True
    assert len(report.actions) >= 1
