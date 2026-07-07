from typing import Any

from talentcopilot.ai.confidence_engine import ConfidenceEngine
from talentcopilot.ai.evidence_quality_engine import EvidenceQualityEngine
from talentcopilot.ai.explainability_engine import ExplainabilityEngine
from talentcopilot.ai.risk_engine import RiskEngine
from talentcopilot.ai.uncertainty_engine import UncertaintyEngine
from talentcopilot.models.governance import GovernanceReport


class GovernanceEngine:
    """
    Main orchestration engine for TalentCopilot v0.6 Explainable AI.

    It is intentionally independent from the existing ReasoningEngine.
    You can call it after matching/reasoning to enrich the candidate report.
    """

    def __init__(self):
        self.evidence_quality_engine = EvidenceQualityEngine()
        self.confidence_engine = ConfidenceEngine()
        self.uncertainty_engine = UncertaintyEngine()
        self.risk_engine = RiskEngine()
        self.explainability_engine = ExplainabilityEngine()

    def assess_candidate(
        self,
        candidate: Any,
        job: Any,
        reasoning_report: Any = None,
        match_score: float = 0.0,
    ) -> GovernanceReport:
        evidence_quality = self.evidence_quality_engine.assess(candidate, job, reasoning_report)
        confidence = self.confidence_engine.assess(candidate, job, evidence_quality, match_score=match_score)
        uncertainty = self.uncertainty_engine.assess(evidence_quality)
        risk = self.risk_engine.assess(evidence_quality, uncertainty)

        decision_card = self.explainability_engine.build_decision_card(
            candidate_name=self._candidate_name(candidate),
            role_title=self._role_title(job),
            match_score=match_score,
            confidence=confidence,
            evidence_quality=evidence_quality,
            risk=risk,
            uncertainty=uncertainty,
        )

        notes = [
            evidence_quality.explanation,
            confidence.explanation,
            uncertainty.explanation,
            risk.explanation,
            decision_card.executive_summary,
        ]

        return GovernanceReport(
            decision_card=decision_card,
            confidence=confidence,
            evidence_quality=evidence_quality,
            risk=risk,
            uncertainty=uncertainty,
            explainability_notes=notes,
        )

    def _candidate_name(self, candidate: Any) -> str:
        if isinstance(candidate, dict):
            return candidate.get("name", "Candidate")
        return getattr(candidate, "name", "Candidate")

    def _role_title(self, job: Any) -> str:
        if isinstance(job, dict):
            return job.get("title", "Role")
        return getattr(job, "title", "Role")
