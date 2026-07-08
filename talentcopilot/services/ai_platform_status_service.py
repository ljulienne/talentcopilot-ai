from dataclasses import dataclass

from talentcopilot.ai_core.llm_router import LLMRouter
from talentcopilot.ai_core.models import AIRequest


@dataclass
class AIPlatformStatus:
    model_count: int
    prompt_count: int
    cache_size: int
    event_count: int
    cost_calls: int
    sample_status: str
    sample_model: str


class AIPlatformStatusService:
    def build(self) -> AIPlatformStatus:
        router = LLMRouter()
        response = router.run(
            AIRequest(
                task="platform_status",
                prompt_id="candidate.extract.v1",
                input_text="Alice Martin has HRIS, Project Management and Leadership experience.",
            )
        )
        cost_summary = router.cost_tracker.summary()

        return AIPlatformStatus(
            model_count=len(router.registry.list_models()),
            prompt_count=len(router.prompts.list_prompts()),
            cache_size=router.cache.size(),
            event_count=router.observability.count(),
            cost_calls=cost_summary.calls,
            sample_status=response.status,
            sample_model=response.model,
        )
