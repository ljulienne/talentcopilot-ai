from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ReadinessLevel(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    PARTIAL = "Partial"
    NOT_READY = "Not Ready"


class ReadinessSeverity(str, Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


@dataclass
class ReadinessCheck:
    name: str
    passed: bool
    severity: ReadinessSeverity
    message: str
    recommendation: str = ""


@dataclass
class ProductReadinessReport:
    product_name: str
    version: str
    readiness_score: float
    readiness_level: ReadinessLevel
    checks: List[ReadinessCheck] = field(default_factory=list)
    summary: str = ""

    @property
    def passed_count(self) -> int:
        return len([check for check in self.checks if check.passed])

    @property
    def failed_count(self) -> int:
        return len([check for check in self.checks if not check.passed])

    @property
    def critical_count(self) -> int:
        return len([
            check for check in self.checks
            if not check.passed and check.severity == ReadinessSeverity.CRITICAL
        ])
