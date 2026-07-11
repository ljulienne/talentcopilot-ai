from __future__ import annotations

from talentcopilot.intelligence_core.models import OrganizationInsight, Severity

from .models import ExecutivePriority


_SEVERITY_SCORE = {
    Severity.CRITICAL: 4,
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
}


class InsightPrioritizer:
    def rank(self, insights: list[OrganizationInsight]) -> list[OrganizationInsight]:
        return sorted(
            insights,
            key=lambda item: (
                -_SEVERITY_SCORE[item.severity],
                -item.confidence,
                item.title.casefold(),
            ),
        )

    def answer_priority(self, insights: list[OrganizationInsight]) -> ExecutivePriority:
        if not insights:
            return ExecutivePriority.LOW
        top = self.rank(insights)[0].severity
        return ExecutivePriority(top.value)
