from talentcopilot.ai.reasoning_engine import ReasoningEngine


def test_reasoning_engine_outputs_competency_arguments():
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
        "preferred_skills": ["Budget Management"],
        "years_experience": 5,
    }

    evidence = [
        {"text": "Led HRIS rollout across 5 countries and improved adoption by 35%."},
        {"text": "Managed executive stakeholders during transformation workshops."},
    ]

    report = engine.build_report(candidate=candidate, job=job, evidence=evidence)

    assert report.competency_arguments
    competencies = [arg.competency for arg in report.competency_arguments]
    assert "Project Management" in competencies
    assert "Stakeholder Management" in competencies
    assert "Budget Management" in competencies

    budget = [arg for arg in report.competency_arguments if arg.competency == "Budget Management"][0]
    assert budget.conclusion == "not demonstrated"
    assert budget.interview_validation
