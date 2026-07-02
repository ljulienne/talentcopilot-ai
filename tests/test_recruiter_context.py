from talentcopilot.ai.recruiter_context import (
    build_recruiter_context,
    format_context_for_prompt,
    summarize_talent,
)


def test_summarize_talent():
    talent = {
        "name": "Emma Martin",
        "candidate_key": "emma-martin",
        "talent_score": 95,
        "average_score": 91,
        "highest_score": 97,
        "average_confidence": 94,
        "application_count": 2,
        "progression_trend": "Improving",
        "last_recruitment_title": "HRIS Manager",
        "detected_skills": {
            "HRIS": ["workday"],
            "Data": ["power bi"],
        },
        "financial_data": {
            "budget_min": 70000,
            "budget_max": 85000,
            "expected_salary": 82000,
            "currency": "EUR",
        },
    }

    summary = summarize_talent(talent)

    assert summary["name"] == "Emma Martin"
    assert summary["talent_score"] == 95
    assert summary["skills"]["HRIS"] == ["workday"]
    assert summary["financial_data"]["expected_salary"] == 82000


def test_build_recruiter_context():
    talents = [
        {"name": "Emma Martin", "talent_score": 95},
        {"name": "John Smith", "talent_score": 82},
    ]

    local_response = {
        "title": "Best Candidate",
        "answer": "Emma Martin is the strongest talent.",
    }

    context = build_recruiter_context(
        question="Who is the best candidate?",
        talents=talents,
        local_response=local_response,
    )

    assert context["question"] == "Who is the best candidate?"
    assert context["talent_count"] == 2
    assert context["selected_talent_count"] == 2
    assert len(context["talents"]) == 2
    assert context["local_response"]["title"] == "Best Candidate"
    assert context["instructions"]["role"] == "Senior Recruitment Consultant"


def test_context_uses_semantic_search_when_relevant():
    talents = [
        {
            "name": "Emma Martin",
            "talent_score": 95,
            "detected_skills": {"HRIS": ["Workday"]},
        },
        {
            "name": "John Smith",
            "talent_score": 82,
            "detected_skills": {"Payroll": ["SAP Payroll"]},
        },
    ]

    context = build_recruiter_context(
        question="Find Workday candidates",
        talents=talents,
    )

    assert context["talent_count"] == 2
    assert context["selected_talent_count"] == 1
    assert context["talents"][0]["name"] == "Emma Martin"


def test_format_context_for_prompt():
    context = build_recruiter_context(
        question="Who is the best candidate?",
        talents=[
            {
                "name": "Emma Martin",
                "talent_score": 95,
                "average_score": 91,
                "highest_score": 97,
                "average_confidence": 94,
                "application_count": 2,
                "progression_trend": "Improving",
                "detected_skills": {"HRIS": ["workday"]},
            }
        ],
        local_response={
            "title": "Best Candidate",
            "answer": "Emma Martin is the strongest talent.",
        },
    )

    prompt = format_context_for_prompt(context)

    assert "TalentCopilot" in prompt
    assert "Emma Martin" in prompt
    assert "Best Candidate" in prompt
    assert "Relevant talents selected" in prompt
    assert "Do not invent candidate information." in prompt
