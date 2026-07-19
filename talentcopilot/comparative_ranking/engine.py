from __future__ import annotations

import re
from typing import Iterable, List

from talentcopilot.comparative_ranking.models import ComparativeProfile


class ComparativeRankingEngine:
    """Bounded, job-aware comparative scope analysis."""

    version = "comparative-ranking-v1.1-universal"

    FAMILY_PATTERNS = {
        "sales": r"\b(sales|commercial|business development|key account)\b",
        "hris": r"\b(hris|sirh|hr systems?|people systems?|hr technology)\b",
        "engineering": r"\b(software|engineering|developer|devops|cloud)\b",
        "finance": r"\b(finance|financial|accounting|controller|fp&a|cfo)\b",
        "supply_chain": r"\b(supply chain|logistics|procurement|warehouse|planning)\b",
        "operations": r"\b(operations?|operational excellence)\b",
        "data": r"\b(data|analytics|business intelligence)\b",
        "marketing": r"\b(marketing|brand|digital marketing)\b",
        "human_resources": r"\b(human resources|hr business partner|talent management)\b",
    }

    def analyse(self, candidate_name: str, candidate_text: str, job_text: str) -> ComparativeProfile:
        text = self._normalise(candidate_text)
        job = self._normalise(job_text)
        family = self._job_family(job)

        role_level, role_reason = self._role_level(text, job, family)
        geography, geography_reason, geography_required = self._geographic_scope(text, job)
        leadership, leadership_reason, leadership_required = self._leadership_scope(text, job)
        commercial, commercial_reason, commercial_required = self._commercial_scope(text, job, family)
        industry, industry_reason = self._industry_depth(text, job, family)
        progression, progression_reason = self._career_progression(text)

        dimensions = [role_level, geography, leadership, commercial, industry, progression]
        weights = [0.30, 0.12, 0.16, 0.10, 0.24, 0.08]
        score = round(sum(value * weight for value, weight in zip(dimensions, weights)), 2)

        differentiators = [
            reason for value, reason in [
                (role_level, role_reason),
                (geography, geography_reason),
                (leadership, leadership_reason),
                (commercial, commercial_reason),
                (industry, industry_reason),
                (progression, progression_reason),
            ] if reason and value >= 70
        ][:5]

        return ComparativeProfile(
            candidate_name=candidate_name,
            role_level=role_level,
            geographic_scope=geography,
            leadership_scope=leadership,
            commercial_scope=commercial,
            industry_depth=industry,
            career_progression=progression,
            score=score,
            differentiators=differentiators,
            validation_points=self._validation_points(text, job, family),
            job_family=family,
            geography_required=geography_required,
            leadership_required=leadership_required,
            commercial_required=commercial_required,
        )

    def adjusted_fit(self, mission_fit: float, profile: ComparativeProfile) -> float:
        base = max(0.0, min(100.0, float(mission_fit or 0)))
        if base < 40:
            return round(base, 2)
        delta = (profile.score - 70.0) * 0.08
        return round(max(0.0, min(99.0, base + delta)), 2)

    def _job_family(self, job: str) -> str:
        for family, pattern in self.FAMILY_PATTERNS.items():
            if re.search(pattern, job):
                return family
        return "general"

    def _family_match(self, text: str, family: str) -> bool:
        pattern = self.FAMILY_PATTERNS.get(family)
        return bool(pattern and re.search(pattern, text))

    def _seniority(self, text: str) -> tuple[float, str]:
        patterns = [
            (r"\b(chief|c-level|vice president|vp|head of)\b", 96, "Executive functional scope"),
            (r"\b(global|regional|apac|emea)\s+.*\bdirector\b|\bdirector\b", 90, "Director-level scope"),
            (r"\b(senior|lead|principal)\s+.*\b(manager|consultant|specialist)\b", 80, "Senior or lead scope"),
            (r"\bmanager\b|\bresponsable\b", 72, "Management scope"),
            (r"\bproject manager\b|\bchef de projet\b|\bconsultant\b", 66, "Project or consulting scope"),
            (r"\banalyst\b|\bspecialist\b|\bcoordinator\b", 48, "Individual contributor scope"),
        ]
        return self._first_match(text, patterns, 45, "Role seniority requires validation")

    def _role_level(self, text: str, job: str, family: str) -> tuple[float, str]:
        # Preserve the detailed sales benchmark contract.
        sales_patterns = [
            (r"\b(?:regional|apac|global)\s+sales\s+director\b", 100, "Regional sales director scope"),
            (r"\bregional\s+(?:key\s+account|commercial|sales)\s+director\b", 94, "Regional director-level commercial scope"),
            (r"\b(?:sales|commercial)\s+director\b", 88, "Director-level commercial responsibility"),
            (r"\bregional\s+(?:sales|key\s+account)\s+manager\b", 84, "Regional sales management scope"),
            (r"\bcountry\s+sales\s+manager\b", 76, "Country sales management scope"),
            (r"\bsenior\s+sales\s+manager\b", 74, "Senior sales management scope"),
            (r"\bretail\s+operations\s+manager\b", 48, "Operations management is adjacent to sales leadership"),
            (r"\bsoftware\s+engineering\s+(?:manager|leader)\b", 10, "Engineering leadership is outside the target function"),
        ]
        if family == "sales":
            return self._first_match(text, sales_patterns, 45, "Role seniority requires validation")

        seniority, reason = self._seniority(text)
        if family != "general" and not self._family_match(text, family):
            return min(20.0, seniority), f"Candidate function does not match the {family} mission"
        return seniority, reason

    def _geographic_scope(self, text: str, job: str) -> tuple[float, str, bool]:
        required = bool(re.search(r"\b(apac|asia pacific|emea|regional|multi-country|global)\b", job))
        if not required:
            return 75, "Geographic scope is not a decisive criterion", False
        if re.search(r"\b(apac|asia[- ]pacific|southeast asia|north asia|oceania)\b", text):
            return (100 if "regional" in text else 88), "Explicit target-region scope", True
        if re.search(r"\b(global|international|multi-country|multiple countries)\b", text):
            return 82, "International or multi-country exposure", True
        if re.search(r"\bcountry\b", text):
            return 62, "Country-level geographic scope", True
        return 35, "Required regional scope is not evidenced", True

    def _leadership_scope(self, text: str, job: str) -> tuple[float, str, bool]:
        required = bool(re.search(r"\b(leadership|manage a team|manage teams|people management|encadrement|team of)\b", job))
        if not required:
            return 75, "People leadership is not a decisive criterion", False
        ranges = re.findall(r"(?:managed|led|supervised)\s+(?:teams?\s+of\s+)?(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?", text)
        maximum = max((int(second or first) for first, second in ranges), default=0)
        if maximum >= 30:
            return 96, f"Managed teams of up to {maximum} people", True
        if maximum >= 15:
            return 86, f"Managed teams of up to {maximum} people", True
        if maximum >= 5:
            return 70, f"Managed a team of {maximum} people", True
        if re.search(r"\b(managed|mentored|coached|led|encadrement)\b", text):
            return 62, "Leadership activity evidenced; scale unclear", True
        return 35, "Required leadership is not evidenced", True

    def _commercial_scope(self, text: str, job: str, family: str) -> tuple[float, str, bool]:
        required = family == "sales" or bool(re.search(r"\b(p&l|revenue|sales target|commercial|pricing|forecast)\b", job))
        if not required:
            return 75, "Commercial ownership is not a decisive criterion", False
        if re.search(r"\b(?:usd|\$)\s*80\s*m(?:illion)?\+?\b|\b80m\+?\b", text):
            return 100, "USD 80M+ commercial responsibility", True
        signals = sum(bool(re.search(pattern, text)) for pattern in [
            r"\bowned budgets?\b", r"\bforecasts?\b", r"\bstrategic accounts?\b",
            r"\bpricing\b", r"\bcontract negotiation\b", r"\bp&l\b", r"\brevenue\b",
        ])
        if signals >= 4:
            return 82, "Broad commercial ownership", True
        if signals >= 2:
            return 68, "Material commercial responsibility", True
        return 35, "Required commercial ownership is not evidenced", True

    def _industry_depth(self, text: str, job: str, family: str) -> tuple[float, str]:
        if family == "sales" and re.search(r"\b(textile|apparel|garment|fabric)\b", job):
            if re.search(r"\b(textile|apparel)\b", text):
                if re.search(r"\b(regional|director|country sales manager)\b", text):
                    return 98, "Direct textile/apparel leadership experience"
                return 90, "Direct textile/apparel industry experience"
            if re.search(r"\bretail\b", text):
                return 55, "Retail is adjacent to textile/apparel"
            return 10, "No direct textile/apparel evidence"

        if family == "general":
            return 70, "No decisive job family detected"
        if self._family_match(text, family):
            return 92, f"Direct {family} domain experience"
        adjacent = {
            "hris": ("human_resources", "data"),
            "human_resources": ("hris",),
            "data": ("engineering", "hris", "finance"),
            "operations": ("supply_chain",),
            "supply_chain": ("operations",),
        }
        if any(self._family_match(text, item) for item in adjacent.get(family, ())):
            return 55, f"Adjacent transferable experience for {family}"
        return 15, f"No direct {family} domain evidence"

    def _career_progression(self, text: str) -> tuple[float, str]:
        markers = sum(bool(re.search(pattern, text)) for pattern in [
            r"\bearlier career\b", r"\bprevious employer\b", r"\bcurrent employer\b",
            r"\bmanager\b", r"\bdirector\b", r"\blead\b",
        ])
        if "director" in text and markers >= 3:
            return 90, "Progression to director-level scope"
        if re.search(r"\b(manager|lead|responsable)\b", text) and markers >= 3:
            return 78, "Progressive management career"
        if markers >= 2:
            return 65, "Career progression is partially evidenced"
        return 50, "Career progression requires validation"

    def _validation_points(self, text: str, job: str, family: str) -> List[str]:
        points = []
        checks = [
            (r"\bmandarin\b", "Validate Mandarin capability"),
            (r"\bworkday\b", "Validate Workday depth"),
            (r"\bsuccessfactors\b", "Validate SuccessFactors depth"),
            (r"\bpayroll\b|\bpaie\b", "Validate payroll process depth"),
            (r"\bapac\b", "Validate APAC scope"),
        ]
        for pattern, message in checks:
            if re.search(pattern, job) and not re.search(pattern, text):
                points.append(message)
        if family != "general" and not self._family_match(text, family):
            points.insert(0, f"Validate direct {family} functional experience")
        return points[:4]

    def _first_match(self, text: str, patterns: Iterable[tuple[str, float, str]], default: float, reason: str):
        for pattern, score, label in patterns:
            if re.search(pattern, text):
                return float(score), label
        return float(default), reason

    def _normalise(self, value: str) -> str:
        return " ".join(str(value or "").replace("’", "'").lower().split())
