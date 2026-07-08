from hashlib import md5

from talentcopilot.ai_core.models import AIResponse


class AICache:
    def __init__(self):
        self._cache: dict[str, AIResponse] = {}

    def key(self, task: str, prompt_id: str, input_text: str, model: str) -> str:
        raw = f"{task}::{prompt_id}::{model}::{input_text}"
        return md5(raw.encode("utf-8")).hexdigest()

    def get(self, key: str) -> AIResponse | None:
        return self._cache.get(key)

    def set(self, key: str, response: AIResponse) -> None:
        self._cache[key] = response

    def size(self) -> int:
        return len(self._cache)
