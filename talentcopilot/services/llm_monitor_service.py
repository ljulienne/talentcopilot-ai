from dataclasses import dataclass
from talentcopilot.llm_extraction.cache import LLMExtractionCache

@dataclass
class LLMMonitorStatus:
    cache_entries: int
    cache_size_bytes: int
    cache_dir: str

class LLMMonitorService:
    def status(self) -> LLMMonitorStatus:
        stats = LLMExtractionCache().stats()
        return LLMMonitorStatus(stats["entries"], stats["size_bytes"], stats["cache_dir"])

    def clear_cache(self) -> int:
        return LLMExtractionCache().clear()
