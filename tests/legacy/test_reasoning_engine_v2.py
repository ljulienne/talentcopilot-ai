from talentcopilot.ai.reasoning_engine import ReasoningEngine


def test_reasoning_engine_assesses_evidence_strength():
    engine = ReasoningEngine()

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

    report = engine.build_report(candidate=candidate, job=job, evidence=evidence, match_result={"score": 86})

    strengths_text = " ".join(item.title for item in report.strengths)
    uncertainty_text = " ".join(item.title for item in report.uncertainties)

    assert report.evidence_assessment
    assert report.evidence_assessment[0].strength == "strong"
    assert report.evidence_assessment[1].strength == "weak"
    assert "Concrete evidence" in strengths_text
    assert "weak evidence" in uncertainty_text


def test_reasoning_engine_distinguishes_mentioned_from_demonstrated():
    engine = ReasoningEngine()

    candidate = {
        "name": "Bob Lee",
        "skills": ["Python", "SQL"],
        "years_experience": 4,
    }

    job = {
        "title": "Data Analyst",
        "required_skills": ["Python", "SQL"],
        "years_experience": 3,
    }

    report = engine.build_report(candidate=candidate, job=job, evidence=[])

    statuses = {item.skill: item.status for item in report.skill_assessment}

    assert statuses["Python"] == "mentioned"
    assert statuses["SQL"] == "mentioned"
    assert report.missing_information


def test_reasoning_engine_identifies_missing_skills():
    engine = ReasoningEngine()

    candidate = {
        "name": "Maria Garcia",
        "skills": ["Customer Service"],
        "years_experience": 2,
    }

    job = {
        "title": "Restaurant Manager",
        "required_skills": ["Customer Service", "Team Leadership"],
        "years_experience": 3,
    }

    report = engine.build_report(candidate=candidate, job=job)

    statuses = {item.skill: item.status for item in report.skill_assessment}

    assert statuses["Customer Service"] == "mentioned"
    assert statuses["Team Leadership"] == "missing"
    assert "Experience level may be below expectation" in [risk.title for risk in report.risks]


def test_reasoning_engine_remains_generic_and_human_led():
    engine = ReasoningEngine()

    candidate = {
        "name": "John Smith",
        "skills": ["Safety Compliance", "Team Leadership"],
        "years_experience": 10,
    }

    job = {
        "title": "Airport Operations Supervisor",
        "required_skills": ["Safety Compliance", "Team Leadership"],
        "years_experience": 8,
    }

    report = engine.build_report(candidate=candidate, job=job, match_result={"score": 82})

    assert "HRIS" not in report.executive_summary
    assert "SIRH" not in report.executive_summary
    assert "must not replace recruiter judgment" in report.executive_summary
    assert report.challenge
