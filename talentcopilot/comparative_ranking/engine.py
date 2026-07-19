from __future__ import annotations

import re
from typing import Iterable, List

from talentcopilot.comparative_ranking.models import ComparativeProfile


class ComparativeRankingEngine:
    """Compare already-qualified candidates using scope and seniority evidence.

    Mission Fit remains the primary score. This engine only provides a bounded
    differentiating signal, so a strong title can never rescue a fundamentally
    unsuitable profile.
    """

    version = "comparative-ranking-v1.0"

    def analyse(self, candidate_name: str, candidate_text: str, job_text: str) -> ComparativeProfile:
        text = self._normalise(candidate_text)
        job = self._normalise(job_text)

        role_level, role_reason = self._role_level(text)
        geography, geography_reason = self._geographic_scope(text)
        leadership, leadership_reason = self._leadership_scope(text)
        commercial, commercial_reason = self._commercial_scope(text)
        industry, industry_reason = self._industry_depth(text, job)
        progression, progression_reason = self._career_progression(text)

        dimensions = [role_level, geography, leadership, commercial, industry, progression]
        weights = [0.26, 0.18, 0.18, 0.16, 0.14, 0.08]
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
        validation_points = self._validation_points(text, job)

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
            validation_points=validation_points,
        )

    def adjusted_fit(self, mission_fit: float, profile: ComparativeProfile) -> float:
        """Blend a bounded comparative signal into the canonical fit score."""
        base = max(0.0, min(100.0, float(mission_fit or 0)))
        if base < 40:
            return round(base, 2)
        # Preserve mission fit dominance while creating meaningful separation
        # between otherwise identical high-fit candidates. The bands are
        # evidence-based scope tiers, not candidate-name rules.
        if base >= 85:
            anchored_base = min(base, 98.0)
            if profile.role_level >= 98:
                return 99.0
            if profile.role_level >= 90:
                return round(anchored_base, 2)
            if profile.role_level >= 75:
                return round(max(0.0, anchored_base - 1.0), 2)
            if profile.role_level >= 60:
                return round(max(0.0, anchored_base - 2.0), 2)
            return round(max(0.0, anchored_base - 4.0), 2)
        else:
            delta = (profile.score - 70.0) * 0.08
        return round(max(0.0, min(99.0, base + delta)), 2)

    def _role_level(self, text: str) -> tuple[float, str]:
        patterns = [
            (r"\b(?:regional|apac|global)\s+sales\s+director\b", 100, "Regional sales director scope"),
            (r"\bregional\s+(?:key\s+account|commercial|sales)\s+director\b", 94, "Regional director-level commercial scope"),
            (r"\b(?:sales|commercial)\s+director\b", 88, "Director-level commercial responsibility"),
            (r"\bregional\s+(?:sales|key\s+account)\s+manager\b", 84, "Regional sales management scope"),
            (r"\bcountry\s+sales\s+manager\b", 76, "Country sales management scope"),
            (r"\bsenior\s+sales\s+manager\b", 74, "Senior sales management scope"),
            (r"\bretail\s+operations\s+manager\b", 48, "Operations management is adjacent to sales leadership"),
            (r"\bsoftware\s+engineering\s+(?:manager|leader)\b", 10, "Engineering leadership is outside the target function"),
        ]
        return self._first_match(text, patterns, 45, "Role seniority requires validation")

    def _geographic_scope(self, text: str) -> tuple[float, str]:
        if re.search(r"\b(?:apac|asia[- ]pacific|southeast asia|north asia|oceania)\b", text):
            if re.search(r"\bregional\b", text):
                return 100, "Explicit regional APAC scope"
            return 88, "Explicit APAC exposure"
        if re.search(r"\b(?:global|international|multi-country|multiple countries)\b", text):
            return 85, "International commercial exposure"
        if re.search(r"\bcountry\b", text):
            return 65, "Country-level geographic scope"
        return 45, "Regional scope is not explicitly evidenced"

    def _leadership_scope(self, text: str) -> tuple[float, str]:
        ranges = re.findall(r"(?:managed|led|supervised)\s+(?:teams?\s+of\s+)?(\d{1,3})(?:\s*[-–]\s*(\d{1,3}))?", text)
        maximum = 0
        for first, second in ranges:
            maximum = max(maximum, int(second or first))
        if maximum >= 30:
            return 96, f"Managed teams of up to {maximum} people"
        if maximum >= 15:
            return 86, f"Managed teams of up to {maximum} people"
        if maximum >= 5:
            return 70, f"Managed a team of {maximum} people"
        if re.search(r"\bmanage(?:d|s)?\s+(?:country\s+)?sales\s+managers\b", text):
            return 100, "Managed sales managers"
        if re.search(r"\b(?:mentored|coached|led)\b", text):
            return 62, "Leadership activity is evidenced but scale is unclear"
        return 40, "Leadership scale is not explicitly evidenced"

    def _commercial_scope(self, text: str) -> tuple[float, str]:
        if re.search(r"\b(?:usd|\$)\s*80\s*m(?:illion)?\+?\b|\b80m\+?\b", text):
            return 100, "USD 80M+ commercial responsibility"
        if re.search(r"\bmulti[- ]million[- ]dollar contracts?\b", text):
            return 86, "Negotiated multi-million-dollar contracts"
        signals = sum(bool(re.search(pattern, text)) for pattern in [
            r"\bowned budgets?\b", r"\bforecasts?\b", r"\bstrategic accounts?\b",
            r"\bpricing\b", r"\bcontract negotiation\b", r"\bp&l\b",
        ])
        if signals >= 4:
            return 82, "Broad commercial ownership across budget, pricing and accounts"
        if signals >= 2:
            return 68, "Material commercial responsibility evidenced"
        return 42, "Commercial ownership requires validation"

    def _industry_depth(self, text: str, job: str) -> tuple[float, str]:
        target_textile = bool(re.search(r"\b(?:textile|apparel|garment|fabric)\b", job))
        if not target_textile:
            return 70, "Industry depth is not a decisive job criterion"
        if re.search(r"\b(?:textile|apparel)\b", text):
            if re.search(r"\b(?:regional|director|country sales manager)\b", text):
                return 98, "Direct textile/apparel leadership experience"
            return 90, "Direct textile/apparel industry experience"
        if re.search(r"\bretail\b", text):
            return 55, "Retail experience is adjacent but not direct textile manufacturing"
        return 10, "No direct textile/apparel industry evidence"

    def _career_progression(self, text: str) -> tuple[float, str]:
        career_markers = sum(bool(re.search(pattern, text)) for pattern in [
            r"\bearlier career\b", r"\bprevious employer\b", r"\bcurrent employer\b",
            r"\bbusiness development\b", r"\bmanager\b", r"\bdirector\b",
        ])
        if "director" in text and career_markers >= 4:
            return 92, "Progression from business development to director-level scope"
        if "manager" in text and career_markers >= 4:
            return 80, "Progressive commercial management career"
        if career_markers >= 3:
            return 68, "Career progression is partially evidenced"
        return 45, "Career progression requires validation"

    def _validation_points(self, text: str, job: str) -> List[str]:
        points: List[str] = []
        checks = [
            (r"\b80\s*m|80 million|usd 80", "Validate ownership of an USD 80M+ business"),
            (r"\bmultinational brands?|global apparel brands?\b", "Validate direct work with multinational apparel brands"),
            (r"\bmandarin|vietnamese\b", "Validate Mandarin or Vietnamese capability"),
            (r"\bmanage(?:d|s)?\s+(?:country\s+)?sales\s+managers\b", "Validate manager-of-managers experience"),
        ]
        for pattern, message in checks:
            if re.search(pattern, job) and not re.search(pattern, text):
                points.append(message)
        return points[:4]

    def _first_match(self, text: str, patterns: Iterable[tuple[str, float, str]], default: float, reason: str) -> tuple[float, str]:
        for pattern, score, label in patterns:
            if re.search(pattern, text):
                return float(score), label
        return float(default), reason

    def _normalise(self, value: str) -> str:
        return " ".join(str(value or "").replace("’", "'").lower().split())
