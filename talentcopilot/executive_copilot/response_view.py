from __future__ import annotations

from dataclasses import dataclass, field

from .models import CopilotResponse


@dataclass(frozen=True)
class EvidenceView:
    title: str
    detail: str
    source_engine: str
    confidence_percent: int
    severity: str


@dataclass(frozen=True)
class ActionView:
    title: str
    impact: str
    rationale: str = ""


@dataclass(frozen=True)
class TraceView:
    order: int
    source_engine: str
    contribution: str
    evidence_count: int
    included: bool


@dataclass(frozen=True)
class ExecutiveResponseView:
    question_id: str
    question_title: str
    question_domain: str
    summary: str
    priority: str
    confidence_percent: int
    coverage_percent: int
    evidence_quality: str
    executive_health_score: int
    health_status: str
    data_readiness: str
    business_impact: str
    evidence: tuple[EvidenceView, ...] = field(default_factory=tuple)
    actions: tuple[ActionView, ...] = field(default_factory=tuple)
    risks: tuple[str, ...] = field(default_factory=tuple)
    missing_data: tuple[str, ...] = field(default_factory=tuple)
    assumptions: tuple[str, ...] = field(default_factory=tuple)
    trace: tuple[TraceView, ...] = field(default_factory=tuple)
    suggested_questions: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    @property
    def has_evidence(self) -> bool:
        return bool(self.evidence)

    @property
    def is_decision_ready(self) -> bool:
        return (
            self.confidence_percent >= 70
            and self.coverage_percent >= 50
            and self.evidence_quality != "Insufficient"
        )


def build_response_view(response: CopilotResponse) -> ExecutiveResponseView:
    answer = response.answer

    evidence = tuple(
        EvidenceView(
            title=item.label,
            detail=item.detail,
            source_engine=item.source_engine,
            confidence_percent=round(item.confidence * 100),
            severity=item.severity,
        )
        for item in answer.evidence
    )

    recommendations = answer.actions or answer.recommendations
    actions = tuple(
        ActionView(
            title=action,
            impact=_impact_from_priority(answer.priority.value),
            rationale=(
                "Supported by the available executive evidence."
                if answer.evidence
                else "More evidence is required before execution."
            ),
        )
        for action in recommendations
    )

    trace = tuple(
        TraceView(
            order=step.order,
            source_engine=step.source_engine,
            contribution=step.contribution,
            evidence_count=len(step.evidence_ids),
            included=step.included,
        )
        for step in sorted(answer.decision_trace, key=lambda item: item.order)
    )

    return ExecutiveResponseView(
        question_id=response.question.question_id,
        question_title=response.question.title,
        question_domain=response.question.domain.value,
        summary=answer.summary,
        priority=answer.priority.value,
        confidence_percent=answer.confidence_percent,
        coverage_percent=answer.coverage_percent,
        evidence_quality=answer.evidence_quality,
        executive_health_score=response.executive_health_score,
        health_status=_health_status(response.executive_health_score),
        data_readiness=response.data_readiness,
        business_impact=_impact_from_priority(answer.priority.value),
        evidence=evidence,
        actions=actions,
        risks=answer.risks,
        missing_data=answer.missing_data,
        assumptions=answer.assumptions,
        trace=trace,
        suggested_questions=tuple(
            (item.question_id, item.title)
            for item in response.suggested_questions
        ),
    )


def _health_status(score: int) -> str:
    if score >= 80:
        return "Strong"
    if score >= 60:
        return "Watch"
    return "At risk"


def _impact_from_priority(priority: str) -> str:
    normalized = priority.strip().lower()
    if normalized == "critical":
        return "Very high"
    if normalized == "high":
        return "High"
    if normalized == "medium":
        return "Medium"
    return "Low"
