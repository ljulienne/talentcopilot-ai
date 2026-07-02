from talentcopilot.ai.openai_recruiter import is_openai_available, generate_openai_recruiter_answer


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
    assert "OpenAI is not configured" in response["answer"]
