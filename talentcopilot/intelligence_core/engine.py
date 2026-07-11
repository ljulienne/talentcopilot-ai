from __future__ import annotations

from statistics import mean

from .models import (
    AIDecision,
    DecisionEffort,
    DecisionPriority,
    DecisionQueue,
    DecisionReadiness,
    DecisionStatus,
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


class DecisionEngine:
    """Transforms explainable organization insights into a prioritized action queue."""

    _priority_weight = {
        DecisionPriority.DO_NOW: 3,
        DecisionPriority.PLAN: 2,
        DecisionPriority.MONITOR: 1,
    }

    def generate(self, insights: list[OrganizationInsight], limit: int = 10) -> DecisionQueue:
        decisions: list[AIDecision] = []
        seen_actions: set[str] = set()

        for insight in insights:
            for index, recommendation in enumerate(insight.recommendations, start=1):
                normalized_action = " ".join(recommendation.action.casefold().split())
                if not normalized_action or normalized_action in seen_actions:
                    continue
                seen_actions.add(normalized_action)
                decisions.append(self._from_recommendation(insight, recommendation, index))

        ranked = sorted(
            decisions,
            key=lambda item: (
                -self._priority_weight[item.priority],
                -item.confidence,
                item.effort.value,
                item.title.casefold(),
            ),
        )[: max(1, limit)]
        return DecisionQueue(decisions=tuple(ranked))

    def _from_recommendation(
        self,
        insight: OrganizationInsight,
        recommendation: Recommendation,
        index: int,
    ) -> AIDecision:
        priority = self._priority(insight, recommendation)
        effort = self._effort(recommendation.action)
        evidence = tuple(
            f"{item.label}: {item.detail}"
            for item in insight.evidence[:4]
        )
        return AIDecision(
            decision_id=f"{insight.insight_id}-decision-{index}",
            title=recommendation.action,
            priority=priority,
            status=DecisionStatus.PROPOSED,
            business_impact=insight.business_impact,
            effort=effort,
            horizon=recommendation.timeframe,
            confidence=insight.confidence,
            source_insight_id=insight.insight_id,
            source_insight_title=insight.title,
            rationale=insight.current_situation,
            evidence=evidence,
            business_value=recommendation.business_value,
        )

    @staticmethod
    def _priority(
        insight: OrganizationInsight,
        recommendation: Recommendation,
    ) -> DecisionPriority:
        recommendation_priority = recommendation.priority.casefold()
        if (
            insight.severity in {Severity.CRITICAL, Severity.HIGH}
            and insight.decision_readiness == DecisionReadiness.READY
        ) or recommendation_priority in {"immediate", "critical", "urgent"}:
            return DecisionPriority.DO_NOW
        if insight.severity == Severity.LOW or insight.decision_readiness == DecisionReadiness.NOT_READY:
            return DecisionPriority.MONITOR
        return DecisionPriority.PLAN

    @staticmethod
    def _effort(action: str) -> DecisionEffort:
        text = action.casefold()
        high_markers = ("reorgan", "restructure", "recruit", "implement", "redesign")
        low_markers = ("document", "validate", "review", "identify", "name a liaison")
        if any(marker in text for marker in high_markers):
            return DecisionEffort.HIGH
        if any(marker in text for marker in low_markers):
            return DecisionEffort.LOW
        return DecisionEffort.MEDIUM
