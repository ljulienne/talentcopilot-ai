from talentcopilot.ai.reasoning_engine import ReasoningEngine


def test_reasoning_engine_uses_evidence_intelligence_quality():
    engine = ReasoningEngine()

    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Stakeholder Management"],
        "years_experience": 8,
        "achievements": ["Improved adoption by 35%"],
    }

    job = {
        "title": "Transformation Lead",
        "required_skills": ["Project Management", "Stakeholder Management"],
        "preferred_skills": ["Change Management"],
        "years_experience": 5,
    }

    evidence = [
        {"text": "Led HRIS rollout across 5 countries and improved adoption by 35%."}
    ]

    report = engine.build_report(candidate=candidate, job=job, evidence=evidence)

    assert report.evidence_assessment
    assert report.evidence_assessment[0].strength == "strong"
    assert "Evidence quality" in report.evidence_assessment[0].interpretation
    assert "Inferred competencies" in report.evidence_assessment[0].interpretation
