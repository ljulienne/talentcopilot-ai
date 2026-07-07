from typing import Any, Iterable, List

from talentcopilot.models.talent_locator import (
    TalentLocatorCandidate,
    TalentLocatorFit,
    TalentLocatorReason,
    TalentLocatorReport,
)


class TalentLocatorEngine:
    """
    Internal talent pool locator.

    This engine ranks candidates from an existing talent pool. It does not scrape
    or query external websites. Future connector integrations can reuse this
    scoring contract.
    """

    def locate(self, job: Any, talent_pool: Iterable[Any], limit: int = 10) -> TalentLocatorReport:
        candidates = list(talent_pool or [])
        role_title = self._role_title(job)
        required_skills = self._required_skills(job)
        keywords = self._keywords(job)

        results = [
            self._score_candidate(candidate, role_title, required_skills, keywords)
            for candidate in candidates
        ]

        results = sorted(results, key=lambda item: item.locator_score, reverse=True)[:limit]

        summary = (
            f"Talent Locator reviewed {len(candidates)} candidate(s) for {role_title} "
            f"and found {len([r for r in results if r.is_recommended])} recommended profile(s)."
        )

        return TalentLocatorReport(
            role_title=role_title,
            total_candidates=len(candidates),
            results=results,
            summary=summary,
        )

    def _score_candidate(
        self,
        candidate: Any,
        role_title: str,
        required_skills: List[str],
        keywords: List[str],
    ) -> TalentLocatorCandidate:
        name = self._candidate_name(candidate)
        candidate_skills = self._candidate_skills(candidate)
        candidate_text = self._candidate_text(candidate)

        matched_skills = [
            skill for skill in required_skills
            if skill.lower() in {s.lower() for s in candidate_skills}
            or skill.lower() in candidate_text.lower()
        ]
        missing_skills = [skill for skill in required_skills if skill not in matched_skills]

        skill_score = self._skill_score(required_skills, matched_skills)
        keyword_score = self._keyword_score(keywords, candidate_text)
        evidence_score = self._evidence_score(candidate)
        seniority_score = self._seniority_score(candidate)

        locator_score = round(
            (skill_score * 0.50) +
            (keyword_score * 0.20) +
            (evidence_score * 0.20) +
            (seniority_score * 0.10),
            2,
        )

        reasons = self._reasons(
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            skill_score=skill_score,
            keyword_score=keyword_score,
            evidence_score=evidence_score,
            seniority_score=seniority_score,
        )

        return TalentLocatorCandidate(
            candidate_name=name,
            role_title=role_title,
            locator_score=locator_score,
            fit=self._fit(locator_score),
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            reasons=reasons,
            evidence_hints=self._evidence_hints(candidate),
        )

    def _skill_score(self, required: List[str], matched: List[str]) -> float:
        if not required:
            return 70.0
        return round((len(matched) / len(required)) * 100, 2)

    def _keyword_score(self, keywords: List[str], text: str) -> float:
        if not keywords:
            return 60.0
        hits = sum(1 for keyword in keywords if keyword.lower() in text.lower())
        return round((hits / len(keywords)) * 100, 2)

    def _evidence_score(self, candidate: Any) -> float:
        achievements = self._as_list(self._get(candidate, "achievements"))
        experience = self._as_list(self._get(candidate, "experience")) + self._as_list(self._get(candidate, "experiences"))
        evidence_count = len(achievements) + len(experience)
        if evidence_count >= 5:
            return 90.0
        if evidence_count >= 3:
            return 75.0
        if evidence_count >= 1:
            return 55.0
        return 30.0

    def _seniority_score(self, candidate: Any) -> float:
        years = self._get(candidate, "years_experience", 0)
        try:
            years = float(years)
        except (TypeError, ValueError):
            years = 0
        if years >= 10:
            return 90.0
        if years >= 5:
            return 75.0
        if years >= 2:
            return 55.0
        return 35.0

    def _fit(self, score: float) -> TalentLocatorFit:
        if score >= 85:
            return TalentLocatorFit.EXCELLENT
        if score >= 70:
            return TalentLocatorFit.STRONG
        if score >= 50:
            return TalentLocatorFit.MODERATE
        return TalentLocatorFit.WEAK

    def _reasons(self, matched_skills, missing_skills, skill_score, keyword_score, evidence_score, seniority_score):
        reasons = []
        if matched_skills:
            reasons.append(TalentLocatorReason("Matched skills", f"Matched skills: {', '.join(matched_skills)}.", 0.5))
        if missing_skills:
            reasons.append(TalentLocatorReason("Missing skills", f"Missing skills: {', '.join(missing_skills)}.", 0.3))
        reasons.append(TalentLocatorReason("Skill score", f"Skill coverage score is {skill_score}/100.", 0.5))
        reasons.append(TalentLocatorReason("Keyword score", f"Keyword relevance score is {keyword_score}/100.", 0.2))
        reasons.append(TalentLocatorReason("Evidence score", f"Evidence availability score is {evidence_score}/100.", 0.2))
        reasons.append(TalentLocatorReason("Seniority score", f"Seniority signal score is {seniority_score}/100.", 0.1))
        return reasons

    def _evidence_hints(self, candidate: Any) -> List[str]:
        hints = []
        hints.extend(self._as_list(self._get(candidate, "achievements")))
        hints.extend(self._as_list(self._get(candidate, "experience")))
        hints.extend(self._as_list(self._get(candidate, "experiences")))
        return [str(item) for item in hints if item][:5]

    def _candidate_name(self, candidate: Any) -> str:
        return str(self._get(candidate, "name", "Candidate"))

    def _role_title(self, job: Any) -> str:
        return str(self._get(job, "title", "Role"))

    def _required_skills(self, job: Any) -> List[str]:
        return [str(item) for item in self._as_list(
            self._get(job, "required_skills")
            or self._get(job, "skills")
            or self._get(job, "competencies")
        )]

    def _keywords(self, job: Any) -> List[str]:
        raw = []
        raw.extend(self._as_list(self._get(job, "keywords")))
        raw.extend(self._as_list(self._get(job, "title")))
        raw.extend(self._required_skills(job))
        return [str(item) for item in raw if item]

    def _candidate_skills(self, candidate: Any) -> List[str]:
        return [str(item) for item in self._as_list(self._get(candidate, "skills"))]

    def _candidate_text(self, candidate: Any) -> str:
        values = []
        for key in ["name", "title", "summary", "skills", "achievements", "experience", "experiences"]:
            values.extend(self._as_list(self._get(candidate, key)))
        return " ".join(str(value) for value in values if value)

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
