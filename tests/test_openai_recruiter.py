from talentcopilot.ai.openai_recruiter import (
    DEFAULT_MODEL,
    generate_openai_recruiter_answer,
    is_openai_available,
)


def test_is_openai_available_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert is_openai_available() is False


def test_generate_openai_recruiter_answer_without_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    response = generate_openai_recruiter_answer(
        {
            "question": "Who is the best candidate?",
            "talents": [],
            "local_response": {},
        }
    )

    assert response["source"] == "local"
    assert response["prompt_type"] == "fallback"
    assert "OpenAI is not configured" in response["answer"]


def test_default_model_is_configurable_string():
    assert isinstance(DEFAULT_MODEL, str)
    assert len(DEFAULT_MODEL) > 0
