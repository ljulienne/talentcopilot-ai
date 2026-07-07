
from talentcopilot.ai.decision_engine import DecisionEngine
from talentcopilot.models.decision import HiringRecommendation


def test_decision_engine_outputs_recommendation_without_governance():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Stakeholder Management"],
    }

    job = {
        "title": "Transformation Lead",
        "required_skills": ["Project Management", "Stakeholder Management"],
    }

    decision = DecisionEngine().make_decision(
        candidate=candidate,
        job=job,
        match_score=90,
        governance_report=None,
    )

    assert decision.candidate_name == "Alice Martin"
    assert decision.role_title == "Transformation Lead"
    assert decision.decision_score > 0
    assert decision.recommendation in set(HiringRecommendation)
    assert len(decision.signals) == 5


def test_decision_engine_handles_missing_governance_report():
    candidate = {"name": "Unknown"}
    job = {"title": "Data Engineer", "required_skills": ["Python"]}

    decision = DecisionEngine().make_decision(
        candidate=candidate,
        job=job,
        match_score=45,
        governance_report=None,
    )

    assert decision.candidate_name == "Unknown"
    assert decision.role_title == "Data Engineer"
    assert decision.decision_score >= 0
    assert decision.recommendation in set(HiringRecommendation)


def test_decision_engine_respects_custom_weights():
    candidate = {"name": "Alice"}
    job = {"title": "Role"}

    decision = DecisionEngine().make_decision(
        candidate=candidate,
        job=job,
        match_score=100,
        governance_report=None,
        weights={
            "match": 1.0,
            "confidence": 0.0,
            "evidence_quality": 0.0,
            "risk": 0.0,
            "uncertainty": 0.0,
        },
    )

    assert decision.signals[0].weight == 1.0
    assert decision.decision_score == 100.0
