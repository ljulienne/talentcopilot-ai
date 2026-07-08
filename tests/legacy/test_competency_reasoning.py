from talentcopilot.ai.competency_reasoning import CompetencyReasoningEngine


def test_competency_reasoning_detects_demonstrated_competency():
    engine = CompetencyReasoningEngine()

    report = engine.analyze(
        evidence_texts=[
            "Led HRIS rollout across 5 countries and improved adoption by 35%.",
            "Managed executive stakeholders during transformation workshops.",
        ],
        target_competencies=["Project Management", "Stakeholder Management"],
    )

    arguments = {arg.competency: arg for arg in report.arguments}

    assert arguments["Project Management"].conclusion in {"demonstrated", "strongly demonstrated"}
    assert arguments["Project Management"].evidence
    assert arguments["Stakeholder Management"].evidence
    assert report.summary


def test_competency_reasoning_identifies_missing_competency():
    engine = CompetencyReasoningEngine()

    report = engine.analyze(
        evidence_texts=["Participated in HR projects."],
        target_competencies=["Budget Management"],
    )

    argument = report.arguments[0]

    assert argument.competency == "Budget Management"
    assert argument.conclusion == "not demonstrated"
    assert argument.limitations
    assert argument.interview_validation


def test_competency_reasoning_generates_validation_questions():
    engine = CompetencyReasoningEngine()

    report = engine.analyze(
        evidence_texts=["Led HRIS rollout across multiple countries."],
        target_competencies=["Project Management"],
    )

    argument = report.arguments[0]

    assert argument.interview_validation
