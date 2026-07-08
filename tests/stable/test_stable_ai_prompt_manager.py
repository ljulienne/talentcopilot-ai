from talentcopilot.ai_core.models import PromptTemplate
from talentcopilot.ai_core.prompt_manager import PromptManager
from talentcopilot.ai_core.structured_outputs import StructuredOutputValidator


def test_prompt_manager_renders_prompt():
    manager = PromptManager()
    rendered = manager.render("candidate.extract.v1", "Alice has HRIS experience.")

    assert "Alice has HRIS experience" in rendered
    assert manager.get("candidate.extract.v1").version == "1.0"


def test_prompt_manager_register_prompt():
    manager = PromptManager()
    manager.register(PromptTemplate("x.test.v1", "1.0", "test", "Hello {input_text}"))

    assert manager.render("x.test.v1", "World") == "Hello World"


def test_structured_output_validator():
    envelope = StructuredOutputValidator().validate_required_fields(
        "CandidateProfile",
        {"candidate_name": "Alice Martin"},
        ["candidate_name", "skills"],
    )

    assert envelope.validation_status == "Invalid"
    assert envelope.errors
