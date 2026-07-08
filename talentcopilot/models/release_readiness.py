from dataclasses import dataclass, field
from typing import List


@dataclass
class ReadinessCheck:
    name: str
    status: str
    detail: str = ""


@dataclass
class ReleaseReadinessReport:
    score: int
    status: str
    checks: List[ReadinessCheck] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
