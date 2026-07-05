from dataclasses import dataclass, field
from typing import List


@dataclass
class Evidence:
    competency: str
    status: str
    score: int
    confidence: int
    excerpts: List[str] = field(default_factory=list)
    recommendation: str = ""
