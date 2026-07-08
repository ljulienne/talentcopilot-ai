from talentcopilot.ai_core.llm_router import LLMRouter
from talentcopilot.ai_core.models import AIRequest
from talentcopilot.services.ai_platform_status_service import AIPlatformStatusService


def test_router_records_cost_and_events():
    router = LLMRouter()
    router.run(AIRequest(task="test", prompt_id="candidate.extract.v1", input_text="Alice HRIS"))

    assert router.cost_tracker.summary().calls == 1
    assert router.observability.count() == 1


def test_router_cache_hit():
    router = LLMRouter()
    first = router.run(AIRequest(task="test", prompt_id="candidate.extract.v1", input_text="Alice HRIS"))
    second = router.run(AIRequest(task="test", prompt_id="candidate.extract.v1", input_text="Alice HRIS"))

    assert first.structured_data == second.structured_data
    assert second.usage.cache_hit is True


def test_ai_platform_status_service():
    status = AIPlatformStatusService().build()

    assert status.model_count >= 1
    assert status.prompt_count >= 1
    assert status.sample_status == "OK"
