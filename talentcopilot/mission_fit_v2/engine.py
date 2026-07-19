from __future__ import annotations

import re
from typing import Iterable, List, Set, Tuple

from talentcopilot.mission_fit_v2.models import FitDimension, MissionFitResult
from talentcopilot.mission_fit_v2.ontology import CONCEPTS, DIMENSION_WEIGHTS, LABELS


class MissionFitEngineV2:
    """Universal, explainable and deterministic CV-to-mission matching."""

    version = "mission-fit-v2.0"

    INDUSTRY_CONCEPTS = [
        "industry_textile_apparel", "industry_software", "industry_retail",
        "industry_hr_technology", "industry_financial_services",
        "industry_manufacturing", "industry_logistics",
    ]
    FUNCTION_CONCEPTS = [
        "function_sales", "function_operations", "function_engineering",
        "function_hris", "function_human_resources", "function_finance",
        "function_supply_chain", "function_data", "function_marketing",
    ]
    LEADERSHIP_CONCEPTS = ["leadership_regional", "leadership_people"]
    BUSINESS_CONCEPTS = [
        "commercial_b2b", "commercial_pnl", "skill_negotiation",
        "skill_pricing", "skill_forecasting", "skill_project_management",
        "skill_change_management", "skill_stakeholder_management",
        "skill_process_design", "skill_reporting", "skill_integration",
        "skill_payroll", "skill_time_management",
    ]
    TOOL_CONCEPTS = [
        "tool_sap", "tool_salesforce", "tool_power_bi", "tool_workday",
        "tool_successfactors", "tool_oracle_hcm", "tool_talentsoft",
        "tool_excel", "tool_sql", "tool_python",
    ]
    GEOGRAPHY_CONCEPTS = ["geography_apac", "geography_emea", "geography_global"]
    EDUCATION_LANGUAGE_CONCEPTS = [
        "language_english", "language_mandarin", "language_french",
        "education_mba", "education_degree",
    ]

    def evaluate(
        self,
        job_text: str,
        candidate_text: str,
        candidate_name: str = "Candidate",
    ) -> MissionFitResult:
        job = self._normalise(job_text)
        candidate = self._normalise(candidate_text)
        job_concepts = self._detect(job)
        candidate_concepts = self._detect(candidate)
        minimum_years = self._minimum_years(job)
        candidate_years = self._candidate_years(candidate)

        dimensions = [
            self._concept_dimension("industry", "Domain / industry fit", job_concepts, candidate_concepts, self.INDUSTRY_CONCEPTS),
            self._concept_dimension("function", "Functional fit", job_concepts, candidate_concepts, self.FUNCTION_CONCEPTS),
            self._concept_dimension("leadership", "Leadership fit", job_concepts, candidate_concepts, self.LEADERSHIP_CONCEPTS),
            self._experience_dimension(minimum_years, candidate_years),
            self._concept_dimension("business_scope", "Mission capabilities", job_concepts, candidate_concepts, self.BUSINESS_CONCEPTS),
            self._concept_dimension("tools", "Tools fit", job_concepts, candidate_concepts, self.TOOL_CONCEPTS),
            self._concept_dimension("geography", "Geographic fit", job_concepts, candidate_concepts, self.GEOGRAPHY_CONCEPTS),
            self._concept_dimension("education_languages", "Education and languages", job_concepts, candidate_concepts, self.EDUCATION_LANGUAGE_CONCEPTS),
        ]

        raw_score = sum(item.weighted_score for item in dimensions)
        industry = self._by_key(dimensions, "industry")
        function = self._by_key(dimensions, "function")
        business = self._by_key(dimensions, "business_scope")

        critical_penalty = 0.0
        if industry.missing and industry.score == 0:
            critical_penalty += 8
        if function.missing and function.score == 0:
            critical_penalty += 20
        if function.score == 0 and business.score < 35:
            critical_penalty += 10

        overall = round(max(0.0, min(100.0, raw_score - critical_penalty)), 2)
        evidence_count = sum(len(item.evidence) for item in dimensions)
        confidence = int(max(45, min(96, 56 + evidence_count * 3 + (8 if candidate_years else 0))))
        gaps = [gap for item in dimensions for gap in item.missing][:10]
        strengths = [
            match
            for item in sorted(dimensions, key=lambda x: x.weighted_score, reverse=True)
            for match in item.matched
        ][:8]
        evidence = [ev for item in dimensions for ev in item.evidence][:12]
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

        return MissionFitResult(
            overall_score=overall,
            confidence_score=confidence,
            recommendation=recommendation,
            risk_level=risk,
            dimensions=dimensions,
            strengths=strengths,
            gaps=gaps,
            evidence=evidence,
            rationale=self._rationale(candidate_name, overall, recommendation, strengths, gaps),
            engine_version=self.version,
        )

    def _concept_dimension(
        self,
        key: str,
        label: str,
        job: Set[str],
        candidate: Set[str],
        concepts: Iterable[str],
    ) -> FitDimension:
        relevant = [concept for concept in concepts if concept in job]
        matched = [concept for concept in relevant if concept in candidate]
        missing = [concept for concept in relevant if concept not in candidate]

        # A dimension absent from the job is neutral. It must not create an
        # artificial advantage merely because a CV contains unrelated evidence.
        score = 55.0 if not relevant else 100.0 * len(matched) / len(relevant)

        return FitDimension(
            key,
            label,
            round(score, 2),
            DIMENSION_WEIGHTS[key],
            [LABELS[item] for item in matched],
            [LABELS[item] for item in missing],
            [f"Evidence found: {LABELS[item]}" for item in matched],
        )

    def _experience_dimension(self, required: int, candidate: int) -> FitDimension:
        if required <= 0:
            score = 75.0 if candidate > 0 else 55.0
        else:
            score = min(100.0, 100.0 * candidate / required)
        matched = [f"{candidate} years of experience evidenced"] if candidate else []
        missing = [] if required <= 0 or candidate >= required else [
            f"Minimum {required} years required; {candidate} evidenced"
        ]
        return FitDimension(
            "experience",
            "Experience fit",
            round(score, 2),
            DIMENSION_WEIGHTS["experience"],
            matched,
            missing,
            list(matched),
        )

    def _detect(self, text: str) -> Set[str]:
        return {
            concept
            for concept, aliases in CONCEPTS.items()
            if any(self._contains(text, alias) for alias in aliases)
        }

    def _contains(self, text: str, phrase: str) -> bool:
        return bool(re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text, re.IGNORECASE))

    def _minimum_years(self, text: str) -> int:
        patterns = [
            r"(?:minimum|min\.?|at least|over|au moins|minimum de)?\s*(\d{1,2})\s*\+?\s*(?:years?|ans?)",
            r"(\d{1,2})\s*(?:years?|ans?)\s+(?:minimum|required|requis)",
        ]
        values = [
            int(value)
            for pattern in patterns
            for value in re.findall(pattern, text, re.I)
        ]
        return max(values, default=0)

    def _candidate_years(self, text: str) -> int:
        explicit = re.findall(r"(\d{1,2})\s*\+?\s*(?:years?|ans?)", text, re.I)
        values = [int(value) for value in explicit if int(value) <= 50]
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
        ratio = candidate_years / required_years if required_years > 0 else 1.0
        critical_no_fit = (
            ratio < 0.5 and matched_concepts == 0 and score < 58
        ) or (
            function_score == 0 and ratio < 0.5 and (industry_score == 0 or penalty >= 20)
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

    def _rationale(self, name, score, recommendation, strengths, gaps) -> str:
        strength_text = ", ".join(strengths[:3]) or "limited directly evidenced alignment"
        gap_text = ", ".join(gaps[:3]) or "no material critical gap identified"
        return (
            f"{name}: {score:.0f}% mission fit. {recommendation}. "
            f"Strongest evidence: {strength_text}. "
            f"Main validation points: {gap_text}."
        )

    def _normalise(self, value: str) -> str:
        return " ".join(str(value or "").replace("’", "'").lower().split())

    def _by_key(self, dimensions: List[FitDimension], key: str) -> FitDimension:
        return next(item for item in dimensions if item.key == key)
