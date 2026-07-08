from dataclasses import dataclass

from talentcopilot.ai_core.models import AIModelSpec, AIUsage


@dataclass
class CostSummary:
    calls: int
    total_input_tokens: int
    total_output_tokens: int
    total_estimated_cost: float


class CostTracker:
    def __init__(self):
        self._usages: list[AIUsage] = []

    def estimate(self, model: AIModelSpec, input_tokens: int, output_tokens: int) -> float:
        return round(
            (input_tokens / 1000) * model.input_cost_per_1k_tokens
            + (output_tokens / 1000) * model.output_cost_per_1k_tokens,
            6,
        )

    def record(self, usage: AIUsage) -> None:
        self._usages.append(usage)

    def summary(self) -> CostSummary:
        return CostSummary(
            calls=len(self._usages),
            total_input_tokens=sum(item.input_tokens for item in self._usages),
            total_output_tokens=sum(item.output_tokens for item in self._usages),
            total_estimated_cost=round(sum(item.estimated_cost for item in self._usages), 6),
        )
