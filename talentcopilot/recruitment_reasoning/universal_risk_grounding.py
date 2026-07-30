from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

from talentcopilot.models.candidate_workspace import CandidateRisk, CandidateSkill


@dataclass(frozen=True)
class _RankedRisk:
    priority: float
    risk: CandidateRisk


class UniversalCandidateRiskGroundingEngine:
    """Create evidence-grounded candidate risks for any job family.

    The engine is intentionally domain-agnostic. It receives structured role
    requirements and candidate evidence, then identifies the most consequential
    uncertainty without hard-coding technologies, industries or job titles.

    It is presentation/reasoning only: official Talent Fit scores and ranks are
    never recalculated here.
    """

    VERSION = "universal-candidate-risk-grounding-v1.0"

    _OWNERSHIP_TERMS = (
        "led",
        "managed",
        "owned",
        "directed",
        "accountable",
        "responsible",
        "headed",
        "supervised",
        "piloted",
        "piloté",
        "pilotage",
        "dirigé",
        "géré",
        "responsable",
    )
    _CONTRIBUTION_TERMS = (
        "supported",
        "contributed",
        "assisted",
        "participated",
        "collaborated",
        "contribué",
        "participé",
        "accompagné",
    )
    _CRITICAL_MARKERS = (
        "required",
        "mandatory",
        "must",
        "essential",
        "critical",
        "minimum",
        "requis",
        "obligatoire",
        "indispensable",
        "essentiel",
    )
    _MEASURABLE_PATTERN = re.compile(
        r"\b\d+(?:[.,]\d+)?\s*(?:%|users?|employees?|people|countries?|sites?|projects?|"
        r"clients?|customers?|million|millions|m\b|k\b|€|\$|£)",
        re.IGNORECASE,
    )

    def build(
        self,
        *,
        decision_report: Any,
        skills: Sequence[CandidateSkill],
        candidate: dict[str, Any] | None,
        job: dict[str, Any] | None,
        achievements: Iterable[str],
        candidate_text: str,
        limit: int = 3,
    ) -> list[CandidateRisk]:
        candidate = dict(candidate or {})
        job = dict(job or {})
        achievements = [str(item).strip() for item in achievements or () if str(item).strip()]
        ranked: list[_RankedRisk] = []

        ranked.extend(self._decision_concerns(decision_report))
        ranked.extend(self._requirement_gaps(skills, job))

        experience_risk = self._experience_gap(candidate, job)
        if experience_risk is not None:
            ranked.append(experience_risk)

        ranked.extend(self._language_gaps(candidate, job, candidate_text))

        # Generic evidence-quality risks are fallback signals only. They must not
        # crowd out a concrete role-requirement gap.
        if not ranked:
            ownership_risk = self._ownership_gap(
                candidate_text=candidate_text,
                skills=skills,
                job=job,
            )
            if ownership_risk is not None:
                ranked.append(ownership_risk)

        if len(ranked) < max(1, limit):
            impact_risk = self._impact_gap(achievements)
            if impact_risk is not None:
                ranked.append(impact_risk)

        ordered = sorted(
            ranked,
            key=lambda item: (
                -float(item.priority),
                self._severity_order(item.risk.severity),
                self._normalise(item.risk.related_requirement or item.risk.title),
            ),
        )
        return self._dedupe([item.risk for item in ordered])[: max(1, int(limit))]

    def _decision_concerns(self, decision_report: Any) -> list[_RankedRisk]:
        output: list[_RankedRisk] = []
        for concern in getattr(decision_report, "concerns", ()) or ():
            title = self._clean(getattr(concern, "title", "")) or "Documented decision concern"
            detail = self._clean(getattr(concern, "explanation", "")) or "Validate this concern during human review."
            severity = self._normalise_severity(getattr(concern, "severity", "Medium"))
            output.append(
                _RankedRisk(
                    priority=120 + self._severity_weight(severity),
                    risk=CandidateRisk(
                        title=title,
                        detail=detail,
                        severity=severity,
                        classification="Confirmed risk",
                        related_requirement=title,
                        interview_question=(
                            f"Clarify the evidence behind {title}. What was the context, your personal responsibility, "
                            "the decisions you made and the resulting impact?"
                        ),
                        evidence_basis=detail,
                    ),
                )
            )
        return output

    def _requirement_gaps(
        self,
        skills: Sequence[CandidateSkill],
        job: dict[str, Any],
    ) -> list[_RankedRisk]:
        raw_job = str(job.get("raw_text", "") or "")
        output: list[_RankedRisk] = []

        for skill in skills:
            if str(getattr(skill, "requirement_type", "")).casefold() != "role requirement":
                continue
            level = float(getattr(skill, "level", 0) or 0)
            if level >= 70:
                continue

            requirement = self._clean(getattr(skill, "name", ""))
            if not requirement:
                continue
            status = self._clean(getattr(skill, "status", "")) or "limited evidence"
            evidence = self._clean(getattr(skill, "evidence", "")) or (
                f"No direct candidate evidence was identified for {requirement}."
            )
            criticality = self._criticality(requirement, raw_job)
            gap = max(0.0, 70.0 - level)

            if level < 35:
                title = f"Direct evidence of {requirement} is not established"
                detail = (
                    f"The role requires {requirement}, but the current profile does not provide sufficiently direct evidence. "
                    "This is an evidence gap, not proof that the candidate lacks the capability."
                )
                severity = "High" if criticality >= 2 else "Medium"
                classification = "Probable risk"
            elif level < 55:
                title = f"Depth of {requirement} evidence is limited"
                detail = (
                    f"The available profile provides {status.lower()} for {requirement}. "
                    "Scope, recency and applied depth should be verified before the decision."
                )
                severity = "High" if criticality >= 3 else "Medium"
                classification = "Validation point"
            else:
                title = f"Scope of {requirement} requires validation"
                detail = (
                    f"The profile contains relevant signals for {requirement}, but the evidence is not yet strong enough "
                    "to confirm the required level and operating scope."
                )
                severity = "Low" if criticality <= 1 else "Medium"
                classification = "Validation point"

            priority = 60 + gap + criticality * 10 + self._severity_weight(severity)
            output.append(
                _RankedRisk(
                    priority=priority,
                    risk=CandidateRisk(
                        title=title,
                        detail=detail,
                        severity=severity,
                        classification=classification,
                        related_requirement=requirement,
                        interview_question=(
                            f"Describe your most relevant recent example of {requirement}. What did you personally own, "
                            "what was the scale, which decisions did you make and what measurable result followed?"
                        ),
                        evidence_basis=evidence,
                    ),
                )
            )
        return output

    def _experience_gap(
        self,
        candidate: dict[str, Any],
        job: dict[str, Any],
    ) -> _RankedRisk | None:
        required = self._number(job.get("minimum_years_experience"))
        if required <= 0:
            required = self._extract_required_years(str(job.get("raw_text", "") or ""))
        candidate_years = self._number(candidate.get("years_experience"))
        if required <= 0 or candidate_years <= 0 or candidate_years + 0.5 >= required:
            return None

        gap = required - candidate_years
        severity = "High" if gap >= 4 else "Medium" if gap >= 2 else "Low"
        return _RankedRisk(
            priority=72 + gap * 4 + self._severity_weight(severity),
            risk=CandidateRisk(
                title="Experience depth is below the stated requirement",
                detail=(
                    f"The job description requests approximately {required:g} years of relevant experience, while the "
                    f"current profile evidences approximately {candidate_years:g}. The difference should be assessed "
                    "against the actual complexity and transferability of prior work."
                ),
                severity=severity,
                classification="Confirmed requirement gap",
                related_requirement=f"Minimum {required:g} years of relevant experience",
                interview_question=(
                    "Which assignments best demonstrate equivalent complexity despite the shorter documented tenure? "
                    "Describe scope, autonomy and results."
                ),
                evidence_basis=f"Candidate years: {candidate_years:g}; stated requirement: {required:g}.",
            ),
        )

    def _language_gaps(
        self,
        candidate: dict[str, Any],
        job: dict[str, Any],
        candidate_text: str,
    ) -> list[_RankedRisk]:
        required = self._unique(job.get("languages") or job.get("required_languages") or ())
        candidate_languages = self._unique(candidate.get("languages") or ())
        candidate_haystack = self._normalise(" ".join([*candidate_languages, candidate_text]))
        output: list[_RankedRisk] = []

        for language in required:
            if self._normalise(language) and self._normalise(language) in candidate_haystack:
                continue
            output.append(
                _RankedRisk(
                    priority=76,
                    risk=CandidateRisk(
                        title=f"Required {language} proficiency is not evidenced",
                        detail=(
                            f"The job description identifies {language} as a role requirement, but the current candidate "
                            "profile does not provide a clear proficiency signal."
                        ),
                        severity="Medium",
                        classification="Validation point",
                        related_requirement=f"{language} proficiency",
                        interview_question=f"What is your working proficiency in {language}, and in which professional situations have you used it?",
                        evidence_basis=f"No explicit {language} proficiency was found in the current structured profile.",
                    ),
                )
            )
        return output

    def _ownership_gap(
        self,
        *,
        candidate_text: str,
        skills: Sequence[CandidateSkill],
        job: dict[str, Any],
    ) -> _RankedRisk | None:
        if self._contains_any(candidate_text, self._OWNERSHIP_TERMS):
            return None

        anchor = self._ownership_anchor(skills, job)
        if not anchor:
            return None
        contribution = self._contains_any(candidate_text, self._CONTRIBUTION_TERMS)
        detail = (
            f"The profile shows contribution to {anchor}, but does not clearly establish the candidate's individual "
            "decision authority and accountable deliverables."
            if contribution
            else f"The current profile does not clearly establish individual accountability for {anchor}."
        )
        return _RankedRisk(
            priority=54,
            risk=CandidateRisk(
                title=f"Decision ownership for {anchor} is not established",
                detail=detail,
                severity="Medium",
                classification="Validation point",
                related_requirement=anchor,
                interview_question=(
                    f"For a recent example involving {anchor}, which decisions and deliverables were you personally "
                    "accountable for, and how did your contribution differ from the wider team's work?"
                ),
                evidence_basis="Direct ownership language is limited in the current candidate evidence.",
            ),
        )

    def _impact_gap(self, achievements: Sequence[str]) -> _RankedRisk | None:
        if not achievements or any(self._MEASURABLE_PATTERN.search(item) for item in achievements):
            return None
        return _RankedRisk(
            priority=38,
            risk=CandidateRisk(
                title="Delivery impact is not quantified",
                detail=(
                    "The profile describes relevant activity, but the available achievements do not quantify scale, "
                    "quality, adoption, revenue, cost, time or another decision-relevant outcome."
                ),
                severity="Low",
                classification="Validation point",
                related_requirement="Demonstrated delivery impact",
                interview_question="Which recent result best demonstrates your impact, and how was that outcome measured?",
                evidence_basis="No measurable outcome was identified in the structured achievements.",
            ),
        )

    def _ownership_anchor(
        self,
        skills: Sequence[CandidateSkill],
        job: dict[str, Any],
    ) -> str:
        responsibilities = self._unique(job.get("responsibilities") or ())
        for responsibility in responsibilities:
            clean = self._clean_responsibility(responsibility)
            if clean:
                return clean
        required = [
            skill
            for skill in skills
            if str(getattr(skill, "requirement_type", "")).casefold() == "role requirement"
        ]
        if required:
            ranked = sorted(required, key=lambda item: (-float(getattr(item, "level", 0) or 0), self._normalise(getattr(item, "name", ""))))
            return self._clean(getattr(ranked[0], "name", ""))
        return ""

    def _criticality(self, requirement: str, raw_job: str) -> int:
        normalized_requirement = self._normalise(requirement)
        normalized_job = self._normalise(raw_job)
        if not normalized_requirement or not normalized_job:
            return 1

        tokens = [token for token in normalized_requirement.split() if len(token) > 2]
        positions = [normalized_job.find(token) for token in tokens if normalized_job.find(token) >= 0]
        if not positions:
            return 1
        position = min(positions)
        window = normalized_job[max(0, position - 100): position + len(normalized_requirement) + 120]
        return 1 + min(3, sum(marker in window for marker in self._CRITICAL_MARKERS))

    @staticmethod
    def _extract_required_years(text: str) -> float:
        candidates: list[float] = []
        patterns = (
            r"(?:minimum|min\.?|at least|au moins)\s+(?:of\s+)?(\d{1,2})\s*\+?\s*(?:years?|ans)",
            r"(\d{1,2})\s*\+?\s*(?:years?|ans)\s+(?:of\s+)?(?:relevant\s+|significant\s+)?(?:experience|expérience)",
        )
        for pattern in patterns:
            for match in re.findall(pattern, str(text or ""), re.IGNORECASE):
                try:
                    value = float(match)
                except (TypeError, ValueError):
                    continue
                if 0 < value <= 50:
                    candidates.append(value)
        return max(candidates) if candidates else 0.0

    @staticmethod
    def _clean_responsibility(value: Any) -> str:
        text = " ".join(str(value or "").split()).strip(" .;:")
        if not text:
            return ""
        text = re.sub(r"^(?:to\s+)?(?:lead|manage|coordinate|deliver|implement|develop|support|drive|oversee)\s+", "", text, flags=re.IGNORECASE)
        words = text.split()
        return " ".join(words[:8]).strip(" .;:")

    @staticmethod
    def _number(value: Any) -> float:
        try:
            return float(value or 0)
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _clean(value: Any) -> str:
        return " ".join(str(value or "").split()).strip()

    @classmethod
    def _normalise(cls, value: Any) -> str:
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", str(value or "").casefold())).strip()

    @classmethod
    def _contains_any(cls, text: Any, values: Iterable[str]) -> bool:
        normalized = cls._normalise(text)
        return any(cls._normalise(value) in normalized for value in values if cls._normalise(value))

    @classmethod
    def _unique(cls, values: Iterable[Any]) -> list[str]:
        output: list[str] = []
        seen: set[str] = set()
        for value in values or ():
            text = cls._clean(value)
            key = cls._normalise(text)
            if text and key and key not in seen:
                seen.add(key)
                output.append(text)
        return output

    @classmethod
    def _dedupe(cls, risks: Sequence[CandidateRisk]) -> list[CandidateRisk]:
        output: list[CandidateRisk] = []
        seen: set[str] = set()
        for risk in risks:
            key = cls._normalise(risk.related_requirement or risk.title)
            if key and key not in seen:
                seen.add(key)
                output.append(risk)
        return output

    @staticmethod
    def _normalise_severity(value: Any) -> str:
        normalized = str(value or "Medium").strip().casefold()
        return "High" if normalized in {"high", "critical"} else "Low" if normalized == "low" else "Medium"

    @staticmethod
    def _severity_weight(severity: str) -> int:
        return {"High": 22, "Medium": 12, "Low": 4}.get(str(severity), 12)

    @staticmethod
    def _severity_order(severity: str) -> int:
        return {"High": 0, "Medium": 1, "Low": 2}.get(str(severity), 1)


__all__ = ["UniversalCandidateRiskGroundingEngine"]
