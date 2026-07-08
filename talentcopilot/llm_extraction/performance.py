from dataclasses import dataclass, field
from time import perf_counter

@dataclass
class LLMExtractionMetric:
    extraction_type: str
    cache_hit: bool
    duration_ms: int
    status: str = "OK"

@dataclass
class LLMPerformanceReport:
    metrics: list[LLMExtractionMetric] = field(default_factory=list)

    @property
    def calls(self) -> int:
        return len(self.metrics)

    @property
    def cache_hits(self) -> int:
        return sum(1 for metric in self.metrics if metric.cache_hit)

    @property
    def cache_misses(self) -> int:
        return self.calls - self.cache_hits

    @property
    def total_duration_ms(self) -> int:
        return sum(metric.duration_ms for metric in self.metrics)

    @property
    def cache_hit_rate(self) -> float:
        return 0.0 if not self.calls else round(self.cache_hits / self.calls, 2)

class Timer:
    def __enter__(self):
        self.start = perf_counter()
        self.duration_ms = 0
        return self

    def __exit__(self, exc_type, exc, tb):
        self.duration_ms = int((perf_counter() - self.start) * 1000)
