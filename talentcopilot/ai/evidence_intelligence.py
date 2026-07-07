from dataclasses import dataclass, field
from typing import List


@dataclass
class EvidenceQuality:
    clarity: int
    responsibility: int
    impact: int
    measurement: int
    context: int

    @property
    def score(self) -> int:
        return round(
            (self.clarity + self.responsibility + self.impact + self.measurement + self.context) / 5
        )

    @property
    def level(self) -> str:
        if self.score >= 85:
            return "exceptional"
        if self.score >= 70:
            return "strong"
        if self.score >= 50:
            return "moderate"
        return "weak"


@dataclass
class StructuredEvidence:
    text: str
    claim_type: str
    observed_action: str
    inferred_competencies: List[str] = field(default_factory=list)
    quality: EvidenceQuality | None = None
    explanation: str = ""
    limitations: List[str] = field(default_factory=list)


@dataclass
class EvidenceIntelligenceReport:
    evidence_items: List[StructuredEvidence]
    overall_quality_score: int
    overall_quality_level: str
    summary: str


class EvidenceIntelligenceEngine:
    """
    Extracts and evaluates evidence from candidate text.

    The engine does not make hiring decisions.
    It only evaluates the quality and usefulness of observed evidence.
    """

    def analyze(self, evidence_texts: List[str]) -> EvidenceIntelligenceReport:
        items = [
            self._analyze_single(text)
            for text in evidence_texts
            if text and str(text).strip()
        ]

        if not items:
            return EvidenceIntelligenceReport(
                evidence_items=[],
                overall_quality_score=0,
                overall_quality_level="unknown",
                summary="No usable evidence was provided.",
            )

        overall_score = round(sum(item.quality.score for item in items if item.quality) / len(items))
        overall_level = self._quality_level(overall_score)

        return EvidenceIntelligenceReport(
            evidence_items=items,
            overall_quality_score=overall_score,
            overall_quality_level=overall_level,
            summary=self._build_summary(items, overall_score, overall_level),
        )

    def _analyze_single(self, text: str) -> StructuredEvidence:
        text = str(text).strip()
        lower = text.lower()

        quality = EvidenceQuality(
            clarity=self._score_clarity(lower),
            responsibility=self._score_responsibility(lower),
            impact=self._score_impact(lower),
            measurement=self._score_measurement(lower),
            context=self._score_context(lower),
        )

        return StructuredEvidence(
            text=text,
            claim_type=self._detect_claim_type(lower),
            observed_action=self._detect_action(lower),
            inferred_competencies=self._infer_competencies(lower),
            quality=quality,
            explanation=self._explain_quality(quality),
            limitations=self._detect_limitations(lower),
        )

    def _score_clarity(self, lower: str) -> int:
        if any(word in lower for word in ["led", "managed", "owned", "implemented", "delivered"]):
            return 90
        if any(word in lower for word in ["supported", "participated", "contributed"]):
            return 55
        return 40

    def _score_responsibility(self, lower: str) -> int:
        if any(word in lower for word in ["owned", "led", "managed", "responsible for"]):
            return 90
        if any(word in lower for word in ["supported", "participated", "assisted"]):
            return 45
        return 50

    def _score_impact(self, lower: str) -> int:
        if any(word in lower for word in ["reduced", "increased", "improved", "saved", "generated", "delivered"]):
            return 85
        return 45

    def _score_measurement(self, lower: str) -> int:
        if any(char.isdigit() for char in lower) or "%" in lower or "€" in lower or "$" in lower:
            return 90
        return 35

    def _score_context(self, lower: str) -> int:
        if any(word in lower for word in ["countries", "regions", "employees", "users", "stakeholders", "teams", "departments"]):
            return 85
        if any(word in lower for word in ["project", "program", "rollout", "implementation"]):
            return 65
        return 45

    def _quality_level(self, score: int) -> str:
        if score >= 85:
            return "exceptional"
        if score >= 70:
            return "strong"
        if score >= 50:
            return "moderate"
        return "weak"

    def _detect_claim_type(self, lower: str) -> str:
        if any(word in lower for word in ["reduced", "increased", "improved", "saved", "generated"]):
            return "impact"
        if any(word in lower for word in ["led", "managed", "owned", "responsible"]):
            return "responsibility"
        if any(word in lower for word in ["supported", "participated", "assisted"]):
            return "participation"
        return "general"

    def _detect_action(self, lower: str) -> str:
        for action in ["led", "managed", "owned", "implemented", "delivered", "supported", "participated"]:
            if action in lower:
                return action
        return "not explicit"

    def _infer_competencies(self, lower: str) -> List[str]:
        competencies = []

        if any(word in lower for word in ["led", "managed", "team", "stakeholders"]):
            competencies.append("Leadership")

        if any(word in lower for word in ["project", "program", "implementation", "rollout", "delivered"]):
            competencies.append("Project Management")

        if any(word in lower for word in ["stakeholder", "executive", "business"]):
            competencies.append("Stakeholder Management")

        if any(word in lower for word in ["change", "transformation", "adoption"]):
            competencies.append("Change Management")

        if any(word in lower for word in ["reduced", "increased", "improved", "saved"]):
            competencies.append("Business Impact")

        return competencies

    def _detect_limitations(self, lower: str) -> List[str]:
        limitations = []

        if not any(char.isdigit() for char in lower) and "%" not in lower:
            limitations.append("No measurable result is provided.")

        if not any(word in lower for word in ["owned", "led", "managed", "responsible"]):
            limitations.append("The level of personal ownership is not fully explicit.")

        if not any(word in lower for word in ["employees", "users", "countries", "budget", "team"]):
            limitations.append("The scale or scope is not fully documented.")

        return limitations

    def _explain_quality(self, quality: EvidenceQuality) -> str:
        return (
            f"Evidence quality is {quality.level} ({quality.score}/100). "
            f"Clarity={quality.clarity}, responsibility={quality.responsibility}, "
            f"impact={quality.impact}, measurement={quality.measurement}, context={quality.context}."
        )

    def _build_summary(self, items: List[StructuredEvidence], score: int, level: str) -> str:
        strong_items = len([item for item in items if item.quality and item.quality.score >= 70])
        weak_items = len([item for item in items if item.quality and item.quality.score < 50])

        return (
            f"The evidence set is rated {level} with an overall quality score of {score}/100. "
            f"{strong_items} evidence item(s) are strong or better, while {weak_items} require caution. "
            "The recruiter should prioritize high-quality evidence and validate weak or incomplete claims."
        )
