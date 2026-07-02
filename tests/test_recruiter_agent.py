from talentcopilot.ai.recruiter_agent import RecruiterAgent


def test_best_candidate():
    talents = [
        {
            "name": "Emma",
            "talent_score": 95,
            "average_score": 91,
            "highest_score": 97,
            "average_confidence": 94,
        },
        {
            "name": "John",
            "talent_score": 82,
            "average_score": 80,
            "highest_score": 85,
            "average_confidence": 88,
        },
    ]

    agent = RecruiterAgent(talents)
    answer = agent.answer("Who is the best candidate?")

    assert answer["title"] == "Best Candidate"
    assert "Emma" in answer["answer"]
    assert "95%" in answer["answer"]


def test_budget_analysis():
    talents = [
        {
            "name": "John",
            "financial_data": {
                "expected_salary": 95000,
                "budget_max": 85000,
                "currency": "EUR",
            },
        },
        {
            "name": "Emma",
            "financial_data": {
                "expected_salary": 80000,
                "budget_max": 85000,
                "currency": "EUR",
            },
        },
    ]

    agent = RecruiterAgent(talents)
    answer = agent.answer("Which candidates are above budget?")

    assert answer["title"] == "Budget Analysis"
    assert "John" in answer["answer"]
    assert "above budget" in answer["answer"]
    assert "Emma" in answer["answer"]
    assert "within budget" in answer["answer"]


def test_skills_summary():
    talents = [
        {
            "name": "Emma",
            "detected_skills": {
                "HRIS": ["workday", "successfactors"],
                "Data": ["power bi"],
            },
        }
    ]

    agent = RecruiterAgent(talents)
    answer = agent.answer("What skills are available?")

    assert answer["title"] == "Skills Summary"
    assert "HRIS" in answer["answer"]
    assert "workday" in answer["answer"]


def test_interview_priority():
    talents = [
        {"name": "John", "talent_score": 82},
        {"name": "Emma", "talent_score": 95},
    ]

    agent = RecruiterAgent(talents)
    answer = agent.answer("Who should I interview first?")

    assert answer["title"] == "Interview Priority"
    assert "Emma" in answer["answer"]


def test_risk_summary():
    talents = [
        {
            "name": "John",
            "average_score": 68,
            "average_confidence": 72,
        }
    ]

    agent = RecruiterAgent(talents)
    answer = agent.answer("Show me risks")

    assert answer["title"] == "Risk Summary"
    assert "John" in answer["answer"]


def test_unknown_question():
    agent = RecruiterAgent([])
    answer = agent.answer("hello")

    assert answer["title"] == "Question not understood"
