from talentcopilot.ai.reasoning_engine import ReasoningEngine
from talentcopilot.ai.interview_intelligence import (
    InterviewGuide,
    InterviewIntelligenceEngine,
    InterviewQuestion,
)


def _build_sample_report():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Stakeholder Management"],
        "years_experience": 8,
        "achievements": ["Reduced processing time by 35%"],
    }

    job = {
        "title": "Operations Transformation Lead",
        "required_skills": ["Project Management", "Stakeholder Management"],
        "preferred_skills": ["Change Management"],
        "years_experience": 6,
    }

    evidence = [
        {"text": "Led a team of 8 people and reduced processing time by 35%."},
        {"text": "Familiar with change management methods."},
    ]

    reasoning = ReasoningEngine()
    return reasoning.build_report(
        candidate=candidate,
        job=job,
        evidence=evidence,
        match_result={"score": 86},
    )


def test_interview_intelligence_builds_guide():
    report = _build_sample_report()

    engine = InterviewIntelligenceEngine()
    guide = engine.build_guide(report)

    assert isinstance(guide, InterviewGuide)
    assert guide.candidate_name == "Alice Martin"
    assert guide.role_title == "Operations Transformation Lead"
    assert guide.interview_focus
    assert guide.questions
    assert guide.closing_recommendation


def test_interview_questions_are_structured():
    report = _build_sample_report()

    engine = InterviewIntelligenceEngine()
    guide = engine.build_guide(report)

    question = guide.questions[0]

    assert isinstance(question, InterviewQuestion)
    assert question.question
    assert question.objective
    assert question.strong_answer_should_include
    assert question.positive_signals
    assert question.red_flags
    assert question.follow_up_questions
    assert question.evaluation_criteria


def test_interview_guide_is_evidence_based():
    report = _build_sample_report()

    engine = InterviewIntelligenceEngine()
    guide = engine.build_guide(report)

    all_evidence = []
    for question in guide.questions:
        all_evidence.extend(question.evidence_to_validate)

    assert all_evidence


def test_interview_intelligence_remains_generic():
    candidate = {
        "name": "Maria Garcia",
        "skills": ["Customer Service", "Team Leadership"],
        "years_experience": 4,
    }

    job = {
        "title": "Restaurant Manager",
        "required_skills": ["Customer Service", "Team Leadership"],
        "years_experience": 3,
    }

    reasoning = ReasoningEngine()
    report = reasoning.build_report(candidate=candidate, job=job, match_result={"score": 81})

    engine = InterviewIntelligenceEngine()
    guide = engine.build_guide(report)

    combined_text = " ".join(
        [guide.interview_focus, guide.closing_recommendation]
        + [question.question for question in guide.questions]
    )

    assert "HRIS" not in combined_text
    assert "SIRH" not in combined_text
    assert guide.role_title == "Restaurant Manager"
