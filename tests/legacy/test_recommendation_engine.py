from talentcopilot.ai.reasoning_engine import ReasoningEngine
from talentcopilot.ai.recommendation_engine import (
    RecommendationEngine,
    RecommendationReport,
)


def _build_report(name, skills, evidence, score):
    candidate = {
        "name": name,
        "skills": skills,
        "years_experience": 8,
        "achievements": ["Delivered measurable impact"],
    }

    job = {
        "title": "Transformation Lead",
        "required_skills": ["Project Management", "Stakeholder Management"],
        "preferred_skills": ["Change Management"],
        "years_experience": 5,
    }

    return ReasoningEngine().build_report(
        candidate=candidate,
        job=job,
        evidence=evidence,
        match_result={"score": score},
    )


def test_recommendation_engine_builds_report():
    alice = _build_report(
        name="Alice Martin",
        skills=["Project Management", "Stakeholder Management"],
        evidence=[
            {"text": "Led a transformation project across 4 countries."},
            {"text": "Managed executive stakeholders."},
        ],
        score=88,
    )

    bob = _build_report(
        name="Bob Lee",
        skills=["Project Management"],
        evidence=[
            {"text": "Participated in several transformation workshops."},
        ],
        score=74,
    )

    report = RecommendationEngine().build_recommendation([alice, bob])

    assert isinstance(report, RecommendationReport)
    assert report.role_title == "Transformation Lead"
    assert report.recommended_candidate
    assert report.executive_summary
    assert report.ranking
    assert report.trade_offs
    assert report.decision_risks
    assert report.alternative_scenarios
    assert report.challenge
    assert report.interview_priorities
    assert report.evidence_trace


def test_recommendation_engine_ranks_candidates():
    alice = _build_report(
        name="Alice Martin",
        skills=["Project Management", "Stakeholder Management"],
        evidence=[
            {"text": "Led a transformation project and improved adoption by 35%."},
        ],
        score=88,
    )

    bob = _build_report(
        name="Bob Lee",
        skills=["Project Management"],
        evidence=[
            {"text": "Familiar with stakeholder management."},
        ],
        score=70,
    )

    report = RecommendationEngine().build_recommendation([alice, bob])

    assert report.ranking[0].decision_score >= report.ranking[1].decision_score
    assert report.recommended_candidate == report.ranking[0].candidate_name


def test_recommendation_engine_handles_single_candidate():
    alice = _build_report(
        name="Alice Martin",
        skills=["Project Management"],
        evidence=[
            {"text": "Led a project and delivered measurable impact."},
        ],
        score=82,
    )

    report = RecommendationEngine().build_recommendation([alice])

    assert report.recommended_candidate == "Alice Martin"
    assert report.trade_offs
    assert "Single-candidate" in report.trade_offs[0].title


def test_recommendation_engine_rejects_empty_input():
    try:
        RecommendationEngine().build_recommendation([])
        assert False
    except ValueError:
        assert True


def test_recommendation_engine_remains_generic():
    report_a = _build_report(
        name="Maria Garcia",
        skills=["Project Management", "Stakeholder Management"],
        evidence=[
            {"text": "Managed restaurant operations across 3 locations."},
        ],
        score=84,
    )

    recommendation = RecommendationEngine().build_recommendation([report_a])

    combined_text = " ".join(
        [
            recommendation.executive_summary,
            recommendation.challenge,
            *recommendation.evidence_trace,
        ]
    )

    assert "HRIS" not in combined_text
    assert "SIRH" not in combined_text
