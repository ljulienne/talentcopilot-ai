from __future__ import annotations

import re
from typing import Dict, Iterable, List, Set, Tuple

from talentcopilot.mission_fit_v2.models import FitDimension, MissionFitResult
from talentcopilot.mission_fit_v2.ontology import CONCEPTS, DIMENSION_WEIGHTS, LABELS


class MissionFitEngineV2:
    """Explainable, weighted CV-to-mission matching.

    The engine reads the complete job and CV texts, identifies explicit business
    concepts, and scores independent dimensions. It never awards evidence that
    is absent from the source text and keeps all decisions reproducible.
    """

    version = "mission-fit-v2.0"

    def evaluate(self, job_text: str, candidate_text: str, candidate_name: str = "Candidate") -> MissionFitResult:
        job = self._normalise(job_text)
        candidate = self._normalise(candidate_text)
        job_concepts = self._detect(job)
        candidate_concepts = self._detect(candidate)
        minimum_years = self._minimum_years(job)
        candidate_years = self._candidate_years(candidate)

        dimensions = [
            self._concept_dimension("industry", "Industry fit", job_concepts, candidate_concepts,
                                    ["industry_textile_apparel", "industry_software", "industry_retail"]),
            self._concept_dimension("function", "Functional fit", job_concepts, candidate_concepts,
                                    ["function_sales", "function_operations", "function_engineering"]),
            self._concept_dimension("leadership", "Leadership fit", job_concepts, candidate_concepts,
                                    ["leadership_regional", "leadership_people"]),
            self._experience_dimension(minimum_years, candidate_years),
            self._concept_dimension("business_scope", "Business scope", job_concepts, candidate_concepts,
                                    ["commercial_b2b", "commercial_pnl", "skill_negotiation", "skill_pricing", "skill_forecasting"]),
            self._concept_dimension("tools", "Tools fit", job_concepts, candidate_concepts,
                                    ["tool_sap", "tool_salesforce", "tool_power_bi"]),
            self._concept_dimension("geography", "Geographic fit", job_concepts, candidate_concepts,
                                    ["geography_apac"]),
            self._concept_dimension("education_languages", "Education and languages", job_concepts, candidate_concepts,
                                    ["language_english", "language_mandarin", "education_mba"]),
        ]

        raw_score = sum(item.weighted_score for item in dimensions)
        # Critical mismatch guard: shared generic skills cannot compensate for a
        # completely different function or industry.
        critical_penalty = 0.0
        industry = self._by_key(dimensions, "industry")
        function = self._by_key(dimensions, "function")
        if industry.missing and industry.score == 0:
            critical_penalty += 10
        if function.missing and function.score == 0:
            critical_penalty += 18
        if "function_engineering" in candidate_concepts and "function_sales" in job_concepts:
            critical_penalty += 12

        overall = round(max(0.0, min(100.0, raw_score - critical_penalty)), 2)
        evidence_count = sum(len(item.evidence) for item in dimensions)
        confidence = int(max(45, min(96, 58 + evidence_count * 3 + (8 if candidate_years else 0))))
        gaps = [gap for item in dimensions for gap in item.missing][:8]
        strengths = [match for item in sorted(dimensions, key=lambda x: x.weighted_score, reverse=True) for match in item.matched][:6]
        evidence = [ev for item in dimensions for ev in item.evidence][:10]
        recommendation, risk = self._decision(
            overall,
            critical_penalty,
            len(gaps),
            industry_score=industry.score,
            function_score=function.score,
            required_years=minimum_years,
            candidate_years=candidate_years,
            matched_concepts=len(job_concepts & candidate_concepts),
        )
        rationale = self._rationale(candidate_name, overall, recommendation, strengths, gaps)

        return MissionFitResult(
            overall_score=overall,
            confidence_score=confidence,
            recommendation=recommendation,
            risk_level=risk,
            dimensions=dimensions,
            strengths=strengths,
            gaps=gaps,
            evidence=evidence,
            rationale=rationale,
            engine_version=self.version,
        )

    def _concept_dimension(self, key: str, label: str, job: Set[str], candidate: Set[str], concepts: Iterable[str]) -> FitDimension:
        relevant = [concept for concept in concepts if concept in job]
        matched = [concept for concept in relevant if concept in candidate]
        missing = [concept for concept in relevant if concept not in candidate]
        if not relevant:
            score = 75.0 if any(concept in candidate for concept in concepts) else 55.0
        else:
            score = 100.0 * len(matched) / len(relevant)
        matched_labels = [LABELS[item] for item in matched]
        missing_labels = [LABELS[item] for item in missing]
        evidence = [f"Evidence found: {LABELS[item]}" for item in matched]
        return FitDimension(key, label, round(score, 2), DIMENSION_WEIGHTS[key], matched_labels, missing_labels, evidence)

    def _experience_dimension(self, required: int, candidate: int) -> FitDimension:
        if required <= 0:
            score = 80.0 if candidate > 0 else 55.0
        else:
            score = min(100.0, 100.0 * candidate / required)
        matched = [f"{candidate} years of experience evidenced"] if candidate else []
        missing = [] if required <= 0 or candidate >= required else [f"Minimum {required} years required; {candidate} evidenced"]
        evidence = list(matched)
        return FitDimension("experience", "Experience fit", round(score, 2), DIMENSION_WEIGHTS["experience"], matched, missing, evidence)

    def _detect(self, text: str) -> Set[str]:
        found: Set[str] = set()
        for concept, aliases in CONCEPTS.items():
            if any(self._contains(text, alias) for alias in aliases):
                found.add(concept)
        return found

    def _contains(self, text: str, phrase: str) -> bool:
        return bool(re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, flags=re.IGNORECASE))

    def _minimum_years(self, text: str) -> int:
        matches = re.findall(r"(?:minimum|min\.?|at least|over)?\s*(\d{1,2})\s*\+?\s*years", text, re.I)
        return max((int(value) for value in matches), default=0)

    def _candidate_years(self, text: str) -> int:
        explicit = re.findall(r"(\d{1,2})\s*\+?\s*years", text, re.I)
        values = [int(value) for value in explicit if int(value) <= 50]
        # Career date ranges are a useful fallback when a summary omits total experience.
        years = [int(value) for value in re.findall(r"\b(19\d{2}|20\d{2})\b", text)]
        if len(years) >= 2:
            values.append(max(years) - min(years))
        return max(values, default=0)

    def _decision(
        self,
        score: float,
        penalty: float,
        gaps: int,
        *,
        industry_score: float,
        function_score: float,
        required_years: int,
        candidate_years: int,
        matched_concepts: int,
    ) -> Tuple[str, str]:
        """Return a recommendation with hard guards for obvious no-fit cases.

        A low global score alone is not enough to distinguish an adjacent
        profile from a clearly unsuitable one. Critical functional mismatch,
        combined with a material experience shortfall, must therefore reject
        the candidate even when generic evidence raises the weighted score.
        """
        experience_ratio = (candidate_years / required_years) if required_years > 0 else 1.0
        critical_no_fit = (
            experience_ratio < 0.5
            and matched_concepts == 0
            and score < 58
        ) or (
            function_score == 0
            and experience_ratio < 0.5
            and (industry_score == 0 or penalty >= 18)
        )
        if critical_no_fit:
            return "Reject", "Critical"
        if score >= 85 and penalty == 0:
            return "Strong Hire", "Low"
        if score >= 72:
            return "Interview", "Low" if gaps <= 2 else "Medium"
        if score >= 58:
            return "More Evidence Required", "Medium"
        if score >= 40:
            return "Review", "High"
        return "Reject", "Critical" if penalty >= 25 else "High"

    def _rationale(self, name: str, score: float, recommendation: str, strengths: List[str], gaps: List[str]) -> str:
        strength_text = ", ".join(strengths[:3]) or "limited directly evidenced alignment"
        gap_text = ", ".join(gaps[:3]) or "no material critical gap identified"
        return f"{name}: {score:.0f}% mission fit. {recommendation}. Strongest evidence: {strength_text}. Main validation points: {gap_text}."

    def _normalise(self, value: str) -> str:
        return " ".join(str(value or "").replace("’", "'").lower().split())

    def _by_key(self, dimensions: List[FitDimension], key: str) -> FitDimension:
        return next(item for item in dimensions if item.key == key)
