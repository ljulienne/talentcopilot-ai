from __future__ import annotations

from statistics import mean

from talentcopilot.intelligence_core.models import DecisionQueue, OrganizationInsight

from .evidence_registry import EvidenceRegistry
from .models import DecisionTraceStep, ExecutiveAnswer
from .prioritizer import InsightPrioritizer


class ExecutiveReasoningEngine:
    """Orchestrates domain outputs without reimplementing domain analysis."""

    def __init__(self) -> None:
        self.registry = EvidenceRegistry()
        self.prioritizer = InsightPrioritizer()

    def reason(
        self,
        insights: list[OrganizationInsight],
        decision_queue: DecisionQueue | None = None,
        *,
        expected_engines: tuple[str, ...] = (
            "Knowledge",
            "Organization Graph",
            "Collaboration",
            "Skills",
            "Workforce",
        ),
    ) -> ExecutiveAnswer:
        ranked = self.prioritizer.rank(insights)
        evidence = self.registry.register(ranked)
        sources = tuple(dict.fromkeys(item.category for item in ranked if item.category))
        coverage = len(set(sources).intersection(expected_engines)) / len(expected_engines)
        missing = tuple(engine for engine in expected_engines if engine not in sources)

        if not ranked:
            return ExecutiveAnswer(
                summary="No executive conclusion is ready because no domain insight was supplied.",
                priority=self.prioritizer.answer_priority([]),
                confidence=0.0,
                evidence=(),
                recommendations=("Improve data coverage and rerun the diagnostics.",),
                actions=(),
                risks=(),
                sources=(),
                missing_data=expected_engines,
                assumptions=("No conclusion is inferred without domain evidence.",),
                decision_trace=(),
                engine_coverage=0.0,
                evidence_quality="Insufficient",
            )

        top = ranked[0]
        recommendations = self._recommendations(ranked)
        actions = self._actions(decision_queue, recommendations)
        risks = tuple(item.title for item in ranked[:5])
        confidence = mean(item.confidence for item in ranked[:5])
        trace = self._trace(ranked, evidence)

        summary = (
            f"{top.title} is the highest-priority organizational issue. "
            f"{top.current_situation} {top.business_impact}"
        )
        return ExecutiveAnswer(
            summary=summary,
            priority=self.prioritizer.answer_priority(ranked),
            confidence=confidence,
            evidence=evidence,
            recommendations=recommendations,
            actions=actions,
            risks=risks,
            sources=sources,
            missing_data=missing,
            assumptions=(
                "Domain engines remain the source of truth.",
                "The reasoning layer only aggregates and prioritizes supplied findings.",
            ),
            decision_trace=trace,
            engine_coverage=coverage,
            evidence_quality=self._evidence_quality(evidence),
        )

    @staticmethod
    def _recommendations(insights: list[OrganizationInsight]) -> tuple[str, ...]:
        actions: list[str] = []
        for insight in insights:
            for recommendation in insight.recommendations:
                if recommendation.action not in actions:
                    actions.append(recommendation.action)
                if len(actions) >= 5:
                    return tuple(actions)
        return tuple(actions)

    @staticmethod
    def _actions(queue: DecisionQueue | None, fallback: tuple[str, ...]) -> tuple[str, ...]:
        if queue and queue.decisions:
            return tuple(item.title for item in queue.decisions[:5])
        return fallback

    @staticmethod
    def _trace(
        insights: list[OrganizationInsight],
        evidence,
    ) -> tuple[DecisionTraceStep, ...]:
        evidence_by_source: dict[str, list[str]] = {}
        for item in evidence:
            evidence_by_source.setdefault(item.source_engine, []).append(item.evidence_id)

        steps: list[DecisionTraceStep] = []
        for order, source in enumerate(dict.fromkeys(item.category for item in insights), start=1):
            count = sum(1 for item in insights if item.category == source)
            steps.append(
                DecisionTraceStep(
                    order=order,
                    source_engine=source,
                    contribution=f"Contributed {count} prioritized insight(s).",
                    evidence_ids=tuple(evidence_by_source.get(source, ())),
                )
            )
        return tuple(steps)

    @staticmethod
    def _evidence_quality(evidence) -> str:
        if not evidence:
            return "Insufficient"
        avg = mean(item.confidence for item in evidence)
        if len(evidence) >= 6 and avg >= 0.75:
            return "Excellent"
        if len(evidence) >= 3 and avg >= 0.55:
            return "Good"
        return "Limited"
