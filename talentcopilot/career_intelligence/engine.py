from __future__ import annotations

import re
from typing import Iterable, List, Sequence, Tuple

from talentcopilot.career_intelligence.models import CareerDimension, CareerFitReport
from talentcopilot.evidence_profiles.models import CandidateEvidenceProfile, EvidenceItem, MissionEvidenceProfile


class CareerFitEngine:
    """Evidence-grounded career alignment, separate from official Mission Fit."""

    version = "career-fit-intelligence-v1.0"

    DOMAIN_GROUPS = {
        "hris": ("hris", "sirh", "human resources information system", "successfactors", "workday", "oracle hcm", "sap hcm", "peopleSoft", "core hr"),
        "sales": ("sales", "commercial", "business development", "key account", "revenue", "pricing", "customer"),
        "engineering": ("engineering", "software", "developer", "cloud", "devops", "architecture", "python", "java"),
        "finance": ("finance", "financial", "accounting", "controlling", "treasury", "audit"),
        "operations": ("operations", "operational", "supply chain", "logistics", "manufacturing", "production"),
    }
    DELIVERY_TERMS = ("implementation", "deployment", "rollout", "migration", "integration", "interfaces", "project", "programme", "program", "delivery", "configuration", "support")
    GENERALIST_HR_TERMS = ("hr director", "human resources director", "hr strategy", "talent management", "employee relations", "compensation", "recruitment", "hr business partner")
    SENIORITY = {
        "executive": 4,
        "senior": 3,
        "mid": 2,
        "junior": 1,
        "unspecified": 2,
    }

    def assess(self, *, candidate_profile: CandidateEvidenceProfile, mission_profile: MissionEvidenceProfile, candidate_text: str = "", job_text: str = "") -> CareerFitReport:
        candidate = self._normalise(candidate_text)
        job = self._normalise(job_text)
        domain, domain_terms = self._target_domain(mission_profile, job)
        recent_text = self._recent_slice(candidate)

        functional, functional_ev = self._term_score(candidate, domain_terms, base=22, increment=13)
        recent, recent_ev = self._term_score(recent_text, (*domain_terms, *self.DELIVERY_TERMS), base=18, increment=10)
        persistence, persistence_ev = self._persistence(candidate, domain_terms)
        drift, drift_ev = self._drift(candidate, recent_text, domain_terms, domain)
        seniority, seniority_ev = self._seniority_alignment(candidate, mission_profile.seniority)
        transfer, transfer_ev = self._transferability(candidate, mission_profile, domain_terms)

        score = self._clamp(
            functional * 0.25
            + recent * 0.25
            + persistence * 0.16
            + (100 - drift) * 0.14
            + seniority * 0.10
            + transfer * 0.10
        )
        evidence_index = self._index(candidate_profile.evidence)
        dimensions = [
            self._dimension("functional_alignment", "Functional alignment", functional, functional_ev, evidence_index),
            self._dimension("recent_role_alignment", "Recent role alignment", recent, recent_ev, evidence_index),
            self._dimension("domain_persistence", "Domain persistence", persistence, persistence_ev, evidence_index),
            self._dimension("career_drift", "Career drift", drift, drift_ev, evidence_index, inverse=True),
            self._dimension("seniority_alignment", "Seniority alignment", seniority, seniority_ev, evidence_index),
            self._dimension("transferability", "Transferability", transfer, transfer_ev, evidence_index),
        ]
        strengths = [item.label for item in dimensions if (item.score >= 72 if item.key != "career_drift" else item.score <= 28)][:4]
        concerns = [item.label for item in dimensions if (item.score < 48 if item.key != "career_drift" else item.score > 52)][:4]
        confidence = max(50, min(96, 52 + sum(bool(item.evidence) for item in dimensions) * 6 + min(8, len(candidate_profile.evidence) // 3)))
        summary = self._summary(candidate_profile.candidate_name, domain, score, strengths, concerns)
        interview_focus = [f"Validate {item.lower()} with recent, dated examples." for item in concerns[:3]]
        return CareerFitReport(
            candidate_name=candidate_profile.candidate_name,
            score=round(score, 2), confidence=confidence,
            functional_alignment=functional, recent_role_alignment=recent,
            domain_persistence=persistence, career_drift=drift,
            seniority_alignment=seniority, transferability=transfer,
            dimensions=dimensions, strengths=strengths, concerns=concerns,
            summary=summary, interview_focus=interview_focus,
            engine_version=self.version,
        )

    def _target_domain(self, mission: MissionEvidenceProfile, job: str) -> Tuple[str, Tuple[str, ...]]:
        haystack = " ".join([mission.role_title, *mission.required_skills, *mission.technologies, job]).casefold()
        scored = [(name, sum(haystack.count(term.casefold()) for term in terms)) for name, terms in self.DOMAIN_GROUPS.items()]
        name, count = max(scored, key=lambda item: item[1])
        if count:
            return name, self.DOMAIN_GROUPS[name]
        fallback = tuple(dict.fromkeys([x.casefold() for x in mission.required_skills + mission.technologies if x]))
        return "target domain", fallback or (mission.role_title.casefold(),)

    def _term_score(self, text: str, terms: Iterable[str], *, base: float, increment: float) -> Tuple[float, List[str]]:
        found = self._find(text, terms)
        return self._clamp(base + len(found) * increment), found

    def _persistence(self, text: str, terms: Sequence[str]) -> Tuple[float, List[str]]:
        found = self._find(text, terms)
        years = [int(value) for value in re.findall(r"\b(\d{1,2})\s*\+?\s*(?:years?|ans)\b", text, re.I)]
        year_signal = max(years, default=0)
        score = 24 + min(46, len(found) * 9) + min(30, year_signal * 2.5)
        evidence = list(found)
        if year_signal:
            evidence.append(f"{year_signal} years")
        return self._clamp(score), evidence

    def _drift(self, text: str, recent: str, domain_terms: Sequence[str], domain: str) -> Tuple[float, List[str]]:
        all_domain = len(self._find(text, domain_terms))
        recent_domain = len(self._find(recent, domain_terms))
        concerns: List[str] = []
        drift = 20.0 if recent_domain else (48.0 if all_domain else 70.0)
        if domain == "hris":
            generalist = self._find(recent, self.GENERALIST_HR_TERMS)
            delivery = self._find(recent, self.DELIVERY_TERMS)
            if generalist and not delivery:
                drift += 24
                concerns.extend(generalist[:3])
            elif generalist:
                drift += 8
                concerns.extend(generalist[:2])
        if all_domain and recent_domain == 0:
            concerns.append("target-domain evidence is concentrated outside the recent career section")
        return self._clamp(drift), concerns or self._find(recent, domain_terms)[:3]

    def _seniority_alignment(self, text: str, target: str) -> Tuple[float, List[str]]:
        recent = self._recent_slice(text)
        labels = []
        patterns = [
            ("executive", r"\b(?:chief|chro|vice president|vp|director)\b"),
            ("senior", r"\b(?:senior|lead|head|manager)\b"),
            ("mid", r"\b(?:consultant|specialist|analyst|coordinator)\b"),
            ("junior", r"\b(?:junior|assistant|trainee|intern)\b"),
        ]
        candidate_level = "unspecified"
        for label, pattern in patterns:
            match = re.search(pattern, recent, re.I)
            if match:
                candidate_level = label
                labels.append(match.group(0))
                break
        gap = abs(self.SENIORITY.get(candidate_level, 2) - self.SENIORITY.get(target, 2))
        return {0: 92.0, 1: 72.0, 2: 42.0, 3: 22.0}.get(gap, 42.0), labels

    def _transferability(self, text: str, mission: MissionEvidenceProfile, domain_terms: Sequence[str]) -> Tuple[float, List[str]]:
        mission_terms = tuple(mission.required_skills + mission.technologies + mission.responsibilities)
        evidence = self._find(text, (*domain_terms, *mission_terms, *self.DELIVERY_TERMS))
        return self._clamp(28 + len(evidence) * 8), evidence[:8]

    def _dimension(self, key: str, label: str, score: float, phrases: List[str], evidence_index: dict, inverse: bool = False) -> CareerDimension:
        ids = []
        excerpts = []
        for phrase in phrases:
            match = evidence_index.get(phrase.casefold())
            if match:
                ids.append(match.evidence_id)
                excerpts.append(match.excerpt)
            else:
                excerpts.append(phrase)
        effective = 100 - score if inverse else score
        rationale = f"{label} is {'strong' if effective >= 72 else 'credible' if effective >= 48 else 'limited'} based on {len(excerpts)} evidence signal(s)."
        return CareerDimension(key=key, label=label, score=round(score, 2), evidence_ids=ids, evidence=excerpts[:6], rationale=rationale)

    def _index(self, evidence: List[EvidenceItem]) -> dict:
        index = {}
        for item in evidence:
            for value in (item.label, item.normalized_value):
                index[str(value).casefold()] = item
        return index

    def _recent_slice(self, text: str) -> str:
        lines = [line.strip() for line in re.split(r"[\n\r]+|(?<=[.;])\s+", text) if line.strip()]
        if not lines:
            return text
        return " ".join(lines[: max(3, min(10, len(lines) // 2 + 1))])

    def _find(self, text: str, terms: Iterable[str]) -> List[str]:
        found = []
        for term in terms:
            clean = str(term or "").strip()
            if not clean:
                continue
            match = re.search(r"(?<!\w)" + re.escape(clean) + r"(?!\w)", text, re.I)
            if match and match.group(0).casefold() not in {x.casefold() for x in found}:
                found.append(match.group(0))
        return found

    def _summary(self, name: str, domain: str, score: float, strengths: List[str], concerns: List[str]) -> str:
        band = "strong" if score >= 75 else "credible" if score >= 58 else "limited"
        text = f"{name} shows a {band} career fit for the {domain} mission."
        if strengths:
            text += f" Career evidence is strongest in {', '.join(strengths[:3]).lower()}."
        if concerns:
            text += f" Priority validation areas are {', '.join(concerns[:3]).lower()}."
        return text

    def _normalise(self, value: str) -> str:
        return " ".join(str(value or "").replace("’", "'").split())

    def _clamp(self, value: float) -> float:
        return max(0.0, min(100.0, float(value)))
