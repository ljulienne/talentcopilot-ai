from talentcopilot.ai_core.llm_router import LLMRouter
from talentcopilot.ai_core.models import AIRequest
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_llm_router_returns_structured_response():
    response = LLMRouter().run(
        AIRequest(
            task="test",
            prompt_id="candidate.extract.v1",
            input_text="Alice Martin has HRIS and Leadership experience.",
        )
    )

    assert response.status == "OK"
    assert response.structured_data
    assert response.prompt_version == "1.0"


def test_ai_platform_ui_imports():
    module = __import__("talentcopilot.ui.ai_platform", fromlist=["render_ai_platform"])
    assert hasattr(module, "render_ai_platform")


def test_ai_platform_navigation():
    page = get_page_by_label("AI Platform")
    assert page is not None
    assert page.module == "talentcopilot.ui.ai_platform"
