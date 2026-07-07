from typing import Any, Dict, Iterable, List, Optional

from talentcopilot.models.decision import (
    DecisionConcern,
    DecisionConfidence,
    DecisionReport,
    DecisionSignal,
    DecisionStrength,
    HiringRecommendation,
    HumanValidationLevel,
)


class DecisionEngine:
    """
    Consolidates TalentCopilot intelligence layers into an explainable hiring decision.

    Inputs are deliberately flexible:
    - dicts,
    - dataclass instances,
    - existing TalentCopilot reports.

    The engine does not require LLM calls.
    """

    DEFAULT_WEIGHTS = {
        "match": 0.35,
        "confidence": 0.25,
        "evidence_quality": 0.20,
        "risk": 0.10,
        "uncertainty": 0.10,
    }

    def make_decision(
        self,
        candidate: Any,
        job: Any,
        match_score: float = 0.0,
        governance_report: Any = None,
        reasoning_report: Any = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> DecisionReport:
        weights = self._normalize_weights(weights or self.DEFAULT_WEIGHTS)

        confidence_score = self._extract_confidence(governance_report)
        evidence_quality_score = self._extract_evidence_quality(governance_report)
        risk_score = self._risk_to_score(self._extract_risk_level(governance_report))
        uncertainty_score = self._uncertainty_to_score(self._extract_uncertainty_level(governance_report))

        signals = [
            DecisionSignal(
                name="Match",
                score=self._bounded(match_score),
                weight=weights["match"],
                explanation="Overall candidate-to-role match signal.",
            ),
            DecisionSignal(
                name="Confidence",
                score=confidence_score,
                weight=weights["confidence"],
                explanation="Reliability of the underlying AI assessment.",
            ),
            DecisionSignal(
                name="Evidence Quality",
                score=evidence_quality_score,
                weight=weights["evidence_quality"],
                explanation="Specificity, measurability and strength of supporting evidence.",
            ),
            DecisionSignal(
                name="Risk Control",
                score=risk_score,
                weight=weights["risk"],
                explanation="Higher score means lower detected risk.",
            ),
            DecisionSignal(
                name="Uncertainty Control",
                score=uncertainty_score,
                weight=weights["uncertainty"],
                explanation="Higher score means lower uncertainty.",
            ),
        ]

        decision_score = round(sum(signal.weighted_score for signal in signals), 2)
        recommendation = self._recommendation(decision_score, governance_report)
        confidence = self._decision_confidence(decision_score, confidence_score, evidence_quality_score)
        human_validation = self._human_validation(governance_report, confidence)

        strengths = self._extract_strengths(governance_report, signals)
        concerns = self._extract_concerns(governance_report, decision_score)
        interview_focus = self._extract_interview_focus(governance_report, concerns)
        missing_information = self._extract_missing_information(governance_report)
        next_steps = self._next_steps(recommendation, human_validation, concerns)

        executive_summary = self._executive_summary(
            recommendation=recommendation,
            decision_score=decision_score,
            confidence=confidence,
            human_validation=human_validation,
            concerns=concerns,
        )

        return DecisionReport(
            candidate_name=self._candidate_name(candidate),
            role_title=self._role_title(job),
            recommendation=recommendation,
            decision_score=decision_score,
            confidence=confidence,
            human_validation=human_validation,
            executive_summary=executive_summary,
            signals=signals,
            strengths=strengths,
            concerns=concerns,
            interview_focus=interview_focus,
            missing_information=missing_information,
            next_steps=next_steps,
        )

    def _recommendation(self, decision_score: float, governance_report: Any) -> HiringRecommendation:
        risk_level = self._extract_risk_level(governance_report)
        uncertainty_level = self._extract_uncertainty_level(governance_report)

        if decision_score >= 85 and risk_level != "High" and uncertainty_level != "High":
            return HiringRecommendation.STRONG_HIRE
        if decision_score >= 70 and risk_level != "High":
            return HiringRecommendation.HIRE
        if decision_score >= 58:
            return HiringRecommendation.REVIEW
        if decision_score >= 45:
            return HiringRecommendation.HOLD
        return HiringRecommendation.NOT_RECOMMENDED

    def _decision_confidence(
        self,
        decision_score: float,
        confidence_score: float,
        evidence_quality_score: float,
    ) -> DecisionConfidence:
        combined = (decision_score * 0.40) + (confidence_score * 0.35) + (evidence_quality_score * 0.25)
        if combined >= 80:
            return DecisionConfidence.HIGH
        if combined >= 60:
            return DecisionConfidence.MEDIUM
        return DecisionConfidence.LOW

    def _human_validation(self, governance_report: Any, confidence: DecisionConfidence) -> HumanValidationLevel:
        risk_level = self._extract_risk_level(governance_report)
        uncertainty_level = self._extract_uncertainty_level(governance_report)

        if risk_level == "High" or uncertainty_level == "High" or confidence == DecisionConfidence.LOW:
            return HumanValidationLevel.STRONGLY_RECOMMENDED
        if risk_level == "Medium" or uncertainty_level == "Medium" or confidence == DecisionConfidence.MEDIUM:
            return HumanValidationLevel.RECOMMENDED
        return HumanValidationLevel.STANDARD_REVIEW

    def _extract_strengths(self, governance_report: Any, signals: List[DecisionSignal]) -> List[DecisionStrength]:
        strengths: List[DecisionStrength] = []

        for signal in signals:
            if signal.score >= 80:
                strengths.append(
                    DecisionStrength(
                        title=f"Strong {signal.name}",
                        explanation=f"{signal.name} contributes positively with a score of {signal.score}/100.",
                    )
                )

        decision_card = self._get(governance_report, "decision_card")
        for item in self._as_list(self._get(decision_card, "strengths"))[:5]:
            strengths.append(DecisionStrength(title=str(item), explanation=str(item)))

        return strengths[:7]

    def _extract_concerns(self, governance_report: Any, decision_score: float) -> List[DecisionConcern]:
        concerns: List[DecisionConcern] = []

        if decision_score < 60:
            concerns.append(
                DecisionConcern(
                    title="Low decision score",
                    severity="High",
                    explanation="The consolidated decision score is below the recommended threshold.",
                    mitigation="Review candidate evidence and compare with alternative candidates.",
                )
            )

        risk = self._get(governance_report, "risk")
        for risk_item in self._as_list(self._get(risk, "risks")):
            concerns.append(
                DecisionConcern(
                    title=self._get(risk_item, "competency", default="Risk"),
                    severity=self._get(risk_item, "risk_level", default="Medium"),
                    explanation=self._get(risk_item, "reason", default=str(risk_item)),
                    mitigation=self._get(risk_item, "mitigation", default="Validate during interview."),
                )
            )

        return concerns[:10]

    def _extract_interview_focus(self, governance_report: Any, concerns: List[DecisionConcern]) -> List[str]:
        decision_card = self._get(governance_report, "decision_card")
        focus = self._as_list(self._get(decision_card, "interview_focus"))

        for concern in concerns:
            if concern.mitigation:
                focus.append(concern.mitigation)

        return list(dict.fromkeys(str(item) for item in focus if item))[:8]

    def _extract_missing_information(self, governance_report: Any) -> List[str]:
        decision_card = self._get(governance_report, "decision_card")
        missing = self._as_list(self._get(decision_card, "missing_information"))
        uncertainty = self._get(governance_report, "uncertainty")

        for item in self._as_list(self._get(uncertainty, "uncertainties")):
            missing.extend(self._as_list(self._get(item, "missing_information")))

        return list(dict.fromkeys(str(item) for item in missing if item))[:8]

    def _next_steps(
        self,
        recommendation: HiringRecommendation,
        human_validation: HumanValidationLevel,
        concerns: List[DecisionConcern],
    ) -> List[str]:
        if recommendation == HiringRecommendation.STRONG_HIRE:
            steps = ["Move candidate to the next stage."]
        elif recommendation == HiringRecommendation.HIRE:
            steps = ["Continue the process and validate key assumptions."]
        elif recommendation == HiringRecommendation.REVIEW:
            steps = ["Perform a structured review before progressing."]
        elif recommendation == HiringRecommendation.HOLD:
            steps = ["Keep candidate in reserve and compare against stronger profiles."]
        else:
            steps = ["Do not progress unless new evidence becomes available."]

        if human_validation != HumanValidationLevel.STANDARD_REVIEW:
            steps.append("Ask a human recruiter to validate the AI recommendation.")

        if concerns:
            steps.append("Use interview focus points to verify the main concerns.")

        return steps

    def _executive_summary(
        self,
        recommendation: HiringRecommendation,
        decision_score: float,
        confidence: DecisionConfidence,
        human_validation: HumanValidationLevel,
        concerns: List[DecisionConcern],
    ) -> str:
        concern_text = f"{len(concerns)} concern(s) detected" if concerns else "no major concern detected"
        return (
            f"Recommendation: {recommendation.value}. Decision score is {decision_score}/100. "
            f"Decision confidence is {confidence.value}. Human validation: {human_validation.value}. "
            f"There are {concern_text}."
        )

    def _extract_confidence(self, governance_report: Any) -> float:
        direct = self._get(self._get(governance_report, "decision_card"), "confidence_score")
        if direct is not None:
            return self._bounded(direct)
        return self._bounded(self._get(self._get(governance_report, "confidence"), "overall_confidence", 0.0))

    def _extract_evidence_quality(self, governance_report: Any) -> float:
        direct = self._get(self._get(governance_report, "decision_card"), "evidence_quality_score")
        if direct is not None:
            return self._bounded(direct)
        return self._bounded(self._get(self._get(governance_report, "evidence_quality"), "overall_quality_score", 0.0))

    def _extract_risk_level(self, governance_report: Any) -> str:
        direct = self._get(self._get(governance_report, "decision_card"), "risk_level")
        if direct:
            return str(direct)
        return str(self._get(self._get(governance_report, "risk"), "overall_risk_level", "Low"))

    def _extract_uncertainty_level(self, governance_report: Any) -> str:
        direct = self._get(self._get(governance_report, "decision_card"), "uncertainty_level")
        if direct:
            return str(direct)
        return str(self._get(self._get(governance_report, "uncertainty"), "uncertainty_level", "Low"))

    def _risk_to_score(self, risk_level: str) -> float:
        return {"Low": 90.0, "Medium": 60.0, "High": 25.0}.get(risk_level, 70.0)

    def _uncertainty_to_score(self, uncertainty_level: str) -> float:
        return {"Low": 90.0, "Medium": 60.0, "High": 25.0}.get(uncertainty_level, 70.0)

    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        merged = dict(self.DEFAULT_WEIGHTS)
        merged.update(weights)
        total = sum(max(0.0, float(v)) for v in merged.values()) or 1.0
        return {key: max(0.0, float(value)) / total for key, value in merged.items()}

    def _candidate_name(self, candidate: Any) -> str:
        return str(self._get(candidate, "name", "Candidate"))

    def _role_title(self, job: Any) -> str:
        return str(self._get(job, "title", "Role"))

    def _bounded(self, value: Any) -> float:
        try:
            return round(max(0.0, min(100.0, float(value))), 2)
        except (TypeError, ValueError):
            return 0.0

    def _get(self, obj: Any, key: str, default: Any = None) -> Any:
        if obj is None:
            return default
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    def _as_list(self, value: Any) -> List[Any]:
        if value is None:
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, tuple):
            return list(value)
        if isinstance(value, set):
            return list(value)
        return [value]
