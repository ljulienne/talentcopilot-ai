from talentcopilot.ai_core.models import AIModelSpec


class ModelRegistry:
    def __init__(self):
        self._models = {
            "default-extraction": AIModelSpec(
                provider="mock",
                model="mock-structured-extractor",
                purpose="structured_extraction",
                input_cost_per_1k_tokens=0.0,
                output_cost_per_1k_tokens=0.0,
                supports_structured_output=True,
            ),
            "default-reasoning": AIModelSpec(
                provider="mock",
                model="mock-reasoning-model",
                purpose="reasoning",
                input_cost_per_1k_tokens=0.0,
                output_cost_per_1k_tokens=0.0,
                supports_structured_output=True,
            ),
        }

    def get(self, model_key: str) -> AIModelSpec:
        return self._models.get(model_key) or self._models["default-extraction"]

    def list_models(self) -> list[AIModelSpec]:
        return list(self._models.values())

    def register(self, key: str, spec: AIModelSpec) -> None:
        self._models[key] = spec
