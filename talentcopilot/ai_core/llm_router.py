import json
from time import perf_counter

from talentcopilot.ai_core.cache import AICache
from talentcopilot.ai_core.cost_tracker import CostTracker
from talentcopilot.ai_core.model_registry import ModelRegistry
from talentcopilot.ai_core.models import AIRequest, AIResponse, AIUsage
from talentcopilot.ai_core.observability import AIObservability
from talentcopilot.ai_core.prompt_manager import PromptManager


class LLMRouter:
    def __init__(
        self,
        registry: ModelRegistry | None = None,
        prompts: PromptManager | None = None,
        cache: AICache | None = None,
        cost_tracker: CostTracker | None = None,
        observability: AIObservability | None = None,
    ):
        self.registry = registry or ModelRegistry()
        self.prompts = prompts or PromptManager()
        self.cache = cache or AICache()
        self.cost_tracker = cost_tracker or CostTracker()
        self.observability = observability or AIObservability()

    def run(self, request: AIRequest) -> AIResponse:
        model_key = request.preferred_model or "default-extraction"
        model = self.registry.get(model_key)
        rendered_prompt = self.prompts.render(request.prompt_id, request.input_text, request.variables)
        cache_key = self.cache.key(request.task, request.prompt_id, rendered_prompt, model.model)

        cached = self.cache.get(cache_key)
        if cached:
            cached.usage.cache_hit = True
            self.observability.record_response(cached, request.prompt_id, "Cache hit")
            return cached

        start = perf_counter()
        structured = self._mock_structured_output(request)
        content = json.dumps(structured, ensure_ascii=False)
        latency_ms = int((perf_counter() - start) * 1000)

        input_tokens = max(1, len(rendered_prompt.split()))
        output_tokens = max(1, len(content.split()))
        estimated_cost = self.cost_tracker.estimate(model, input_tokens, output_tokens)

        response = AIResponse(
            task=request.task,
            model=model.model,
            content=content,
            structured_data=structured,
            usage=AIUsage(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost=estimated_cost,
                latency_ms=latency_ms,
                cache_hit=False,
            ),
            prompt_version=self.prompts.get(request.prompt_id).version,
            status="OK",
        )

        self.cache.set(cache_key, response)
        self.cost_tracker.record(response.usage)
        self.observability.record_response(response, request.prompt_id, "Mock provider response")
        return response

    def _mock_structured_output(self, request: AIRequest) -> dict:
        text = request.input_text
        words = [w.strip(",.;:()") for w in text.split()]
        title_case = [w for w in words if w[:1].isupper() and len(w) > 2]

        if request.prompt_id.startswith("candidate"):
            return {
                "candidate_name": " ".join(title_case[:2]) if title_case else "Unknown Candidate",
                "skills": [w for w in words if w.lower() in {"python", "hris", "workday", "successfactors", "leadership", "project", "management"}][:10],
                "raw_excerpt": text[:500],
            }

        if request.prompt_id.startswith("job"):
            return {
                "role_title": " ".join(title_case[:3]) if title_case else "Unknown Role",
                "required_skills": [w for w in words if w.lower() in {"python", "hris", "workday", "successfactors", "leadership", "project", "management"}][:10],
                "raw_excerpt": text[:500],
            }

        return {"raw_excerpt": text[:500]}
