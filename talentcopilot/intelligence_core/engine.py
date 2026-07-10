from __future__ import annotations

from statistics import mean

from .models import (
    DecisionReadiness,
    Evidence,
    ExecutiveBrief,
    OrganizationInsight,
    Recommendation,
    Severity,
)


_SEVERITY_WEIGHT = {
    Severity.CRITICAL: 4,
    Severity.HIGH: 3,
    Severity.MEDIUM: 2,
    Severity.LOW: 1,
}


class InsightEngine:
    """Creates a common explainable insight contract from domain findings."""

    def build(
        self,
        *,
        insight_id: str,
        title: str,
        category: str,
        severity: str | Severity,
        confidence: float,
        current_situation: str,
        business_impact: str,
        evidence: list[dict] | tuple[Evidence, ...],
        recommendations: list[dict] | tuple[Recommendation, ...],
    ) -> OrganizationInsight:
        normalized_severity = severity if isinstance(severity, Severity) else Severity(severity)
        evidence_items = tuple(
            item if isinstance(item, Evidence) else Evidence(**item)
            for item in evidence
        )
        recommendation_items = tuple(
            item if isinstance(item, Recommendation) else Recommendation(**item)
            for item in recommendations
        )
        readiness = self._readiness(confidence, evidence_items)
        return OrganizationInsight(
            insight_id=insight_id,
            title=title,
            category=category,
            severity=normalized_severity,
            confidence=confidence,
            current_situation=current_situation,
            business_impact=business_impact,
            evidence=evidence_items,
            recommendations=recommendation_items,
            decision_readiness=readiness,
        )

    @staticmethod
    def _readiness(confidence: float, evidence: tuple[Evidence, ...]) -> DecisionReadiness:
        if confidence >= 0.8 and len(evidence) >= 2:
            return DecisionReadiness.READY
        if confidence >= 0.55 and evidence:
            return DecisionReadiness.REVIEW
        return DecisionReadiness.NOT_READY


class ExecutiveEngine:
    """Prioritizes heterogeneous insights into a concise executive brief."""

    def generate(self, insights: list[OrganizationInsight], limit: int = 5) -> ExecutiveBrief:
        if not insights:
            return ExecutiveBrief(
                headline="No organizational insight is ready yet",
                overall_severity=Severity.LOW,
                narrative="More organization data is required before a reliable decision brief can be produced.",
                priority_insights=(),
                recommended_decisions=("Improve data coverage and rerun the diagnostic.",),
                evidence_quality="Insufficient",
                confidence=0.0,
                decision_readiness=DecisionReadiness.NOT_READY,
            )

        ranked = sorted(
            insights,
            key=lambda item: (
                -_SEVERITY_WEIGHT[item.severity],
                -item.confidence,
                item.title.casefold(),
            ),
        )[: max(1, limit)]

        overall = max(ranked, key=lambda item: _SEVERITY_WEIGHT[item.severity]).severity
        confidence = mean(item.confidence for item in ranked)
        evidence_scores = [item.evidence_quality for item in ranked]
        evidence_quality = self._overall_evidence_quality(evidence_scores)
        readiness = self._overall_readiness(ranked, confidence)

        top = ranked[0]
        decisions: list[str] = []
        for insight in ranked:
            for recommendation in insight.recommendations:
                if recommendation.action not in decisions:
                    decisions.append(recommendation.action)
                if len(decisions) == 5:
                    break
            if len(decisions) == 5:
                break

        narrative = (
            f"{len(insights)} organizational insight(s) were assessed. "
            f"The highest-priority issue is '{top.title}'. "
            f"{top.business_impact}"
        )
        return ExecutiveBrief(
            headline=f"Organization health requires {overall.value.lower()} attention",
            overall_severity=overall,
            narrative=narrative,
            priority_insights=tuple(ranked),
            recommended_decisions=tuple(decisions),
            evidence_quality=evidence_quality,
            confidence=confidence,
            decision_readiness=readiness,
        )

    @staticmethod
    def _overall_evidence_quality(values: list[str]) -> str:
        if values and all(value in {"Excellent", "Good"} for value in values):
            return "Excellent" if values.count("Excellent") >= len(values) / 2 else "Good"
        if any(value in {"Excellent", "Good"} for value in values):
            return "Good"
        return "Limited"

    @staticmethod
    def _overall_readiness(insights: list[OrganizationInsight], confidence: float) -> DecisionReadiness:
        ready_count = sum(item.decision_readiness == DecisionReadiness.READY for item in insights)
        if confidence >= 0.8 and ready_count >= max(1, len(insights) // 2):
            return DecisionReadiness.READY
        if confidence >= 0.55:
            return DecisionReadiness.REVIEW
        return DecisionReadiness.NOT_READY
