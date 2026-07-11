from __future__ import annotations

from talentcopilot.executive_reasoning import ExecutiveReasoningEngine
from talentcopilot.intelligence_core.models import DecisionQueue, OrganizationInsight

from .models import CopilotResponse
from .question_catalog import QuestionCatalog
from .question_router import QuestionRouter


class ExecutiveCopilotEngine:
    """Routes executive questions and delegates reasoning to the shared reasoning engine."""

    def __init__(
        self,
        *,
        router: QuestionRouter | None = None,
        catalog: QuestionCatalog | None = None,
        reasoning_engine: ExecutiveReasoningEngine | None = None,
    ) -> None:
        self.catalog = catalog or QuestionCatalog()
        self.router = router or QuestionRouter(self.catalog)
        self.reasoning_engine = reasoning_engine or ExecutiveReasoningEngine()

    def answer(
        self,
        *,
        insights: list[OrganizationInsight],
        decision_queue: DecisionQueue | None = None,
        text: str | None = None,
        question_id: str | None = None,
    ) -> CopilotResponse:
        routed = self.router.route(text, question_id=question_id)
        relevant = self._filter_insights(insights, routed.question.required_engines)
        answer = self.reasoning_engine.reason(
            relevant,
            decision_queue,
            expected_engines=routed.question.required_engines or (
                "Knowledge",
                "Organization Graph",
                "Collaboration",
                "Skills",
                "Workforce",
            ),
        )
        return CopilotResponse(
            question=routed.question,
            answer=answer,
            executive_health_score=self._health_score(answer),
            data_readiness=self._data_readiness(answer.engine_coverage, answer.evidence_quality),
            suggested_questions=self.catalog.follow_ups(routed.question),
        )

    @staticmethod
    def _filter_insights(
        insights: list[OrganizationInsight],
        required_engines: tuple[str, ...],
    ) -> list[OrganizationInsight]:
        if not required_engines:
            return insights
        allowed = set(required_engines)
        return [item for item in insights if item.category in allowed]

    @staticmethod
    def _health_score(answer) -> int:
        severity_penalty = {
            "Critical": 40,
            "High": 28,
            "Medium": 16,
            "Low": 6,
        }.get(answer.priority.value, 10)
        confidence_bonus = round(answer.confidence * 8)
        coverage_bonus = round(answer.engine_coverage * 12)
        score = 100 - severity_penalty + confidence_bonus + coverage_bonus
        return max(0, min(100, score))

    @staticmethod
    def _data_readiness(coverage: float, evidence_quality: str) -> str:
        if coverage >= 0.8 and evidence_quality in {"Excellent", "Good"}:
            return "High"
        if coverage >= 0.5 and evidence_quality != "Insufficient":
            return "Medium"
        return "Low"
