from talentcopilot.ai.reasoning_engine import ReasoningEngine, CandidateReasoningReport


def test_reasoning_engine_builds_report():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Change Management", "Data Analysis"],
        "years_experience": 8,
        "achievements": ["Led a transformation project across 3 countries"],
    }

    job = {
        "title": "Transformation Manager",
        "required_skills": ["Project Management", "Change Management", "Stakeholder Management"],
        "preferred_skills": ["Data Analysis"],
        "years_experience": 6,
    }

    evidence = [
        {
            "text": "Led a transformation project across 3 countries",
            "confidence": "high",
        }
    ]

    match_result = {
        "score": 84
    }

    engine = ReasoningEngine()
    report = engine.build_report(
        candidate=candidate,
        job=job,
        match_result=match_result,
        evidence=evidence,
    )

    assert isinstance(report, CandidateReasoningReport)
    assert report.candidate_name == "Alice Martin"
    assert report.role_title == "Transformation Manager"
    assert report.executive_summary
    assert report.strengths
    assert report.risks
    assert report.transferable_skills
    assert report.uncertainties
    assert report.recommendation
    assert report.challenge


def test_reasoning_engine_detects_missing_required_skills():
    candidate = {
        "name": "Bob Lee",
        "skills": ["Python"],
        "years_experience": 2,
    }

    job = {
        "title": "Senior Data Analyst",
        "required_skills": ["Python", "SQL", "Stakeholder Management"],
        "years_experience": 5,
    }

    engine = ReasoningEngine()
    report = engine.build_report(candidate=candidate, job=job)

    risk_evidence = []
    for risk in report.risks:
        risk_evidence.extend(risk.evidence)

    assert "SQL" in risk_evidence
    assert "Stakeholder Management" in risk_evidence
    assert "Experience level may be below expectation" in [
        risk.title for risk in report.risks
    ]


def test_reasoning_engine_remains_generic():
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

    engine = ReasoningEngine()
    report = engine.build_report(candidate=candidate, job=job)

    assert report.role_title == "Restaurant Manager"
    assert "HRIS" not in report.executive_summary
    assert "SIRH" not in report.executive_summary
