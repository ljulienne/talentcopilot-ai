from typing import Any, Dict, Iterable, List

from talentcopilot.models.governance import EvidenceQualityAssessment, EvidenceQualitySummary


class EvidenceQualityEngine:
    """
    Scores the quality of evidence supporting each competency.

    This engine is deliberately deterministic and dependency-free.
    It can receive candidates/jobs/reasoning reports as dicts or objects.
    """

    ACTION_WORDS = {
        "led", "managed", "implemented", "delivered", "deployed", "improved",
        "built", "designed", "created", "launched", "optimized", "reduced",
        "increased", "coordinated", "supervised", "owned", "drove"
    }

    METRIC_HINTS = {"%", "€", "$", "kpi", "reduced", "increased", "improved", "growth", "saved"}

    def assess(self, candidate: Any, job: Any, reasoning_report: Any = None) -> EvidenceQualitySummary:
        competencies = self._required_competencies(job)
        assessments = []

        for competency in competencies:
            evidence_items = self._evidence_for_competency(candidate, competency, reasoning_report)
            assessments.append(self._assess_competency(competency, evidence_items))

        if not assessments:
            overall = 0.0
            explanation = "No competency evidence could be evaluated."
        else:
            overall = round(sum(a.quality_score for a in assessments) / len(assessments), 2)
            explanation = f"Overall evidence quality is {overall}/100 across {len(assessments)} competencies."

        return EvidenceQualitySummary(
            overall_quality_score=overall,
            assessments=assessments,
            explanation=explanation,
        )

    def _assess_competency(self, competency: str, evidence_items: List[str]) -> EvidenceQualityAssessment:
        strengths = []
        weaknesses = []

        evidence_count = len(evidence_items)
        if evidence_count == 0:
            return EvidenceQualityAssessment(
                competency=competency,
                quality_score=0.0,
                evidence_count=0,
                weaknesses=["No evidence found"],
                explanation=f"No evidence was found for {competency}.",
            )

        count_score = min(30, evidence_count * 10)
        specificity_score = self._specificity_score(evidence_items)
        measurability_score = self._measurability_score(evidence_items)
        action_score = self._action_score(evidence_items)
        impact_score = self._impact_score(evidence_items)

        quality = round(count_score + specificity_score + measurability_score + action_score + impact_score, 2)
        quality = max(0.0, min(100.0, quality))

        if evidence_count >= 3:
            strengths.append("Multiple evidence points")
        else:
            weaknesses.append("Limited number of evidence points")

        if measurability_score >= 15:
            strengths.append("Measurable achievements detected")
        else:
            weaknesses.append("Few measurable outcomes detected")

        if action_score >= 15:
            strengths.append("Action-oriented evidence")
        else:
            weaknesses.append("Evidence is mostly descriptive")

        explanation = f"{competency} has {evidence_count} evidence point(s), with quality score {quality}/100."

        return EvidenceQualityAssessment(
            competency=competency,
            quality_score=quality,
            evidence_count=evidence_count,
            strengths=strengths,
            weaknesses=weaknesses,
            explanation=explanation,
        )

    def _specificity_score(self, items: List[str]) -> float:
        avg_len = sum(len(i.split()) for i in items) / max(1, len(items))
        return min(20.0, avg_len * 1.2)

    def _measurability_score(self, items: List[str]) -> float:
        text = " ".join(items).lower()
        score = 0
        if any(char.isdigit() for char in text):
            score += 12
        if any(hint in text for hint in self.METRIC_HINTS):
            score += 8
        return min(20.0, score)

    def _action_score(self, items: List[str]) -> float:
        text = " ".join(items).lower()
        hits = sum(1 for word in self.ACTION_WORDS if word in text)
        return min(15.0, hits * 3)

    def _impact_score(self, items: List[str]) -> float:
        text = " ".join(items).lower()
        impact_terms = ["impact", "result", "outcome", "adoption", "efficiency", "performance", "saving"]
        hits = sum(1 for term in impact_terms if term in text)
        return min(15.0, hits * 5)

    def _required_competencies(self, job: Any) -> List[str]:
        if isinstance(job, dict):
            return list(job.get("required_skills") or job.get("competencies") or job.get("skills") or [])
        return list(getattr(job, "required_skills", None) or getattr(job, "competencies", None) or [])

    def _evidence_for_competency(self, candidate: Any, competency: str, reasoning_report: Any = None) -> List[str]:
        evidence = []

        report_evidence = self._extract_report_evidence(reasoning_report, competency)
        evidence.extend(report_evidence)

        if isinstance(candidate, dict):
            for key in ("achievements", "experience", "experiences", "summary", "skills"):
                value = candidate.get(key)
                evidence.extend(self._flatten_text(value))
        else:
            for key in ("achievements", "experience", "experiences", "summary", "skills"):
                evidence.extend(self._flatten_text(getattr(candidate, key, None)))

        comp = competency.lower()
        filtered = [e for e in evidence if comp in e.lower()]
        return filtered if filtered else evidence[:3]

    def _extract_report_evidence(self, report: Any, competency: str) -> List[str]:
        if report is None:
            return []
        items = []

        if isinstance(report, dict):
            for key in ("evidence", "competency_arguments", "arguments", "reasoning"):
                items.extend(self._flatten_text(report.get(key)))
        else:
            for key in ("evidence", "competency_arguments", "arguments", "reasoning"):
                items.extend(self._flatten_text(getattr(report, key, None)))

        comp = competency.lower()
        return [item for item in items if comp in item.lower()] or items

    def _flatten_text(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        if isinstance(value, dict):
            return [str(v) for v in value.values() if v]
        if isinstance(value, Iterable):
            return [str(v) for v in value if v]
        return [str(value)]
