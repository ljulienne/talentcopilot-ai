from __future__ import annotations

import re
from typing import Dict, Iterable, List, Tuple

from talentcopilot.recruiter_intelligence.models import (
    CandidateDNA,
    EvidenceClaim,
    RecruiterIntelligenceAssessment,
)


class RecruiterIntelligenceEngine:
    """Evidence-grounded qualitative interpretation above Mission Fit.

    The engine never changes the official match score or rank. It turns facts
    already present in the job and CV into structured recruiter reasoning.
    """

    version = "recruiter-intelligence-v1.0"

    DIMENSIONS = {
        "expertise_depth": (
            "Expertise depth",
            [r"\b(?:10|11|12|13|14|15|16|17|18|19|20)\+?\s+years?\b", r"\b(?:10|11|12|13|14|15|16|17|18|19|20)\+?\s+ans\b", r"\bsenior\b", r"\blead\b", r"\bmanager\b", r"\bdirector\b"],
        ),
        "international_scope": (
            "International scope",
            [r"\binternational\b", r"\bglobal\b", r"\bworldwide\b", r"\bapac\b", r"\bemea\b", r"\beurope\b", r"\basia\b", r"\bmulticountry\b", r"\bmulti-country\b"],
        ),
        "transformation_complexity": (
            "Transformation complexity",
            [r"\btransformation\b", r"\bmigration\b", r"\bimplementation\b", r"\bdeployment\b", r"\brollout\b", r"\bcore hr\b", r"\bintegration\b", r"\binterfaces?\b", r"\bprogramme\b", r"\bprogram\b"],
        ),
        "leadership": (
            "Leadership",
            [r"\bmanaged?\b", r"\bled\b", r"\bteam(?:s)?\b", r"\bleadership\b", r"\bpeople manager\b", r"\bstakeholder(?:s)?\b", r"\bsteering committee\b"],
        ),
        "enterprise_exposure": (
            "Enterprise exposure",
            [r"\benterprise\b", r"\bmultinational\b", r"\bglobal company\b", r"\bgroup\b", r"\bfortune 500\b", r"\bcac\s*40\b", r"\blvmh\b", r"\bbnp\b", r"\bsiemens\b", r"\brenault\b", r"\bnissan\b", r"\bsoci[eé]t[eé] g[eé]n[eé]rale\b", r"\bcr[eé]dit suisse\b"],
        ),
        "digital_analytics": (
            "Digital and analytics",
            [r"\bpower bi\b", r"\btableau\b", r"\bqliksense\b", r"\bbusiness objects?\b", r"\banalytics\b", r"\breporting\b", r"\bdata science\b", r"\bai\b"],
        ),
        "technology_ecosystem": (
            "Technology ecosystem",
            [r"\bsuccessfactors\b", r"\bworkday\b", r"\boracle\b", r"\bsap(?: hr| hcm)?\b", r"\bpeoplesoft\b", r"\bcornerstone\b", r"\btalentsoft\b", r"\bsaba\b"],
        ),
    }

    ARCHETYPES = {
        "Transformer": [r"\btransformation\b", r"\bchange management\b", r"\bconduite du changement\b", r"\bmigration\b"],
        "Integrator": [r"\bintegration\b", r"\binterfaces?\b", r"\bapi\b", r"\bimplementation\b", r"\bdeployment\b"],
        "Leader": [r"\bled\b", r"\bmanaged?\b", r"\bdirector\b", r"\bhead of\b", r"\bteam(?:s)?\b"],
        "Strategist": [r"\bstrategy\b", r"\bstrategic\b", r"\broadmap\b", r"\bgovernance\b", r"\bexecutive\b"],
        "Operator": [r"\bsupport\b", r"\boperations?\b", r"\bmaintenance\b", r"\badministration\b", r"\brun\b"],
        "Analyst": [r"\banalytics\b", r"\bpower bi\b", r"\breporting\b", r"\bdata\b", r"\bdashboard\b"],
        "Architect": [r"\barchitecture\b", r"\bsolution design\b", r"\btechnical design\b", r"\bcloud\b"],
    }

    def assess(self, *, candidate_name: str, candidate_text: str, job_text: str, mission_fit: float = 0.0, mission_breakdown: Dict[str, float] | None = None) -> RecruiterIntelligenceAssessment:
        candidate = self._normalise(candidate_text)
        job = self._normalise(job_text)
        persona = self._job_persona(job)
        dimensions = [self._dimension(key, label, patterns, candidate, job) for key, (label, patterns) in self.DIMENSIONS.items()]
        dna = self._candidate_dna(candidate)
        dimension_score = sum(item.score for item in dimensions) / max(1, len(dimensions))
        official = self._clamp(mission_fit)
        strategic = round(official * 0.72 + dimension_score * 0.28, 2)
        strengths = [item.label for item in dimensions if item.score >= 72 and item.evidence][:4]
        gaps = [gap for item in dimensions for gap in item.gaps][:5]
        evidence_count = sum(len(item.evidence) for item in dimensions)
        confidence = int(max(50, min(96, 55 + evidence_count * 3 + len([v for v in (mission_breakdown or {}).values() if float(v or 0) > 0]) * 2 - len(gaps) * 2)))
        summary = self._summary(candidate_name, strategic, dna.primary_archetype, strengths, gaps)
        focus = [f"Validate {gap.lower()}" for gap in gaps[:4]]
        return RecruiterIntelligenceAssessment(
            candidate_name=candidate_name,
            strategic_fit_score=strategic,
            confidence_score=confidence,
            job_persona=persona,
            candidate_dna=dna,
            dimensions=dimensions,
            decisive_strengths=strengths,
            material_gaps=gaps,
            recruiter_summary=summary,
            interview_focus=focus,
            engine_version=self.version,
        )

    def _dimension(self, key: str, label: str, patterns: Iterable[str], candidate: str, job: str) -> EvidenceClaim:
        evidence = self._matched_phrases(candidate, patterns)
        required = bool(self._matched_phrases(job, patterns))
        count = len(evidence)
        score = min(100.0, 45.0 + count * 15.0) if count else (42.0 if not required else 20.0)
        gaps = []
        if required and not evidence:
            gaps.append(label)
        return EvidenceClaim(key=key, label=label, score=score, evidence=evidence[:6], gaps=gaps)

    def _candidate_dna(self, text: str) -> CandidateDNA:
        raw = {name: len(self._matched_phrases(text, patterns)) for name, patterns in self.ARCHETYPES.items()}
        total = sum(raw.values()) or 1
        values = {name: round(value * 100 / total, 1) for name, value in raw.items()}
        primary = max(values, key=values.get) if any(raw.values()) else "Generalist"
        evidence = [name for name, value in sorted(values.items(), key=lambda item: -item[1]) if value > 0][:3]
        return CandidateDNA(archetypes=values, primary_archetype=primary, evidence=evidence)

    def _job_persona(self, job: str) -> List[str]:
        labels = []
        checks = [
            (r"\b(?:senior|lead|manager|director)\b", "Senior leadership"),
            (r"\b(?:international|global|apac|emea|worldwide)\b", "International complexity"),
            (r"\b(?:transformation|migration|implementation|deployment|rollout)\b", "Transformation delivery"),
            (r"\b(?:stakeholder|steering committee|executive)\b", "Stakeholder complexity"),
            (r"\b(?:power bi|analytics|reporting|data)\b", "Data and analytics"),
            (r"\b(?:successfactors|workday|oracle|sap|peopleSoft|cornerstone)\b", "HRIS ecosystem depth"),
        ]
        for pattern, label in checks:
            if re.search(pattern, job, re.I): labels.append(label)
        return labels[:6] or ["Role delivery"]

    def _matched_phrases(self, text: str, patterns: Iterable[str]) -> List[str]:
        found = []
        for pattern in patterns:
            match = re.search(pattern, text, re.I)
            if match:
                value = match.group(0).strip()
                if value and value.casefold() not in {x.casefold() for x in found}: found.append(value)
        return found

    def _summary(self, name: str, score: float, archetype: str, strengths: List[str], gaps: List[str]) -> str:
        band = "strong" if score >= 75 else "credible" if score >= 58 else "limited"
        text = f"{name} shows a {band} strategic fit and is primarily a {archetype.lower()} profile."
        if strengths: text += f" Decisive evidence is strongest in {', '.join(strengths[:3]).lower()}."
        if gaps: text += f" The main validation areas are {', '.join(gaps[:3]).lower()}."
        return text

    def _normalise(self, value: str) -> str:
        return " ".join(str(value or "").replace("’", "'").split())

    def _clamp(self, value: float) -> float:
        try: return max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError): return 0.0
