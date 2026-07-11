from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CheckStatus(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: CheckStatus
    message: str
    details: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_failure(self) -> bool:
        return self.status is CheckStatus.FAIL

    @property
    def is_warning(self) -> bool:
        return self.status is CheckStatus.WARN


@dataclass(frozen=True)
class DoctorReport:
    checks: tuple[DoctorCheck, ...]

    @property
    def failures(self) -> tuple[DoctorCheck, ...]:
        return tuple(check for check in self.checks if check.is_failure)

    @property
    def warnings(self) -> tuple[DoctorCheck, ...]:
        return tuple(check for check in self.checks if check.is_warning)

    @property
    def passed(self) -> tuple[DoctorCheck, ...]:
        return tuple(check for check in self.checks if check.status is CheckStatus.PASS)

    @property
    def healthy(self) -> bool:
        return not self.failures

    def to_dict(self) -> dict[str, Any]:
        return {
            "healthy": self.healthy,
            "summary": {
                "passed": len(self.passed),
                "warnings": len(self.warnings),
                "failures": len(self.failures),
            },
            "checks": [
                {
                    "name": check.name,
                    "status": check.status.value,
                    "message": check.message,
                    "details": list(check.details),
                    "metadata": check.metadata,
                }
                for check in self.checks
            ],
        }
