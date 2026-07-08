from talentcopilot.ai_core.models import AIEvent, AIResponse


class AIObservability:
    def __init__(self):
        self._events: list[AIEvent] = []

    def record_response(self, response: AIResponse, prompt_id: str, detail: str = "") -> None:
        self._events.append(
            AIEvent(
                event_type="AI_RESPONSE",
                task=response.task,
                model=response.model,
                prompt_id=prompt_id,
                status=response.status,
                cost=response.usage.estimated_cost,
                latency_ms=response.usage.latency_ms,
                detail=detail,
            )
        )

    def events(self) -> list[AIEvent]:
        return list(self._events)

    def count(self) -> int:
        return len(self._events)
