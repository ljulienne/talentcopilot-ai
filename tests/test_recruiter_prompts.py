from talentcopilot.ai.recruiter_context import build_recruiter_context
from talentcopilot.ai.recruiter_prompts import (
    SYSTEM_PROMPT,
    build_recruiter_prompt,
    detect_prompt_type,
)


def test_detect_prompt_type_general():
    assert detect_prompt_type("Who is the best candidate?") == "general"


def test_detect_prompt_type_comparison():
    assert detect_prompt_type("Compare Emma and John") == "comparison"


def test_detect_prompt_type_budget():
    assert detect_prompt_type("Which candidates are above budget?") == "budget"


def test_detect_prompt_type_interview():
    assert detect_prompt_type("Who should I interview first?") == "interview"


def test_detect_prompt_type_skills():
    assert detect_prompt_type("Who has Workday experience?") == "skills"


def test_build_recruiter_prompt():
    context = build_recruiter_context(
        question="Compare Emma and John",
        talents=[
            {
                "name": "Emma Martin",
                "talent_score": 95,
                "average_score": 91,
                "highest_score": 97,
                "average_confidence": 94,
            },
            {
                "name": "John Smith",
                "talent_score": 82,
                "average_score": 80,
                "highest_score": 85,
                "average_confidence": 88,
            },
        ],
        local_response={
            "title": "Talent Comparison",
            "answer": "Emma appears stronger based on the Talent Score.",
        },
    )

    prompt = build_recruiter_prompt(context)

    assert prompt["prompt_type"] == "comparison"
    assert "TalentCopilot" in prompt["system_prompt"]
    assert "Compare Emma and John" in prompt["user_prompt"]
    assert "Emma Martin" in prompt["user_prompt"]
    assert "John Smith" in prompt["user_prompt"]
    assert "Recommendation" in prompt["user_prompt"]


def test_system_prompt_contains_safety_rules():
    assert "avoid inventing candidate information" in SYSTEM_PROMPT
    assert "use only the provided TalentCopilot context" in SYSTEM_PROMPT
