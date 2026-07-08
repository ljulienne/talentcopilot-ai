from talentcopilot.career_intelligence.achievement_engine import AchievementIntelligenceEngine
from talentcopilot.career_intelligence.models import CareerIntelligenceReport, CareerSignal


class CareerIntelligenceEngine:
    def analyze(
        self,
        candidate_name: str,
        years_experience: int = 0,
        titles: list[str] | None = None,
        achievements: list[str] | None = None,
        responsibilities: list[str] | None = None,
    ) -> CareerIntelligenceReport:
        titles = titles or []
        achievements = achievements or []
        responsibilities = responsibilities or []

        seniority = self._seniority_level(years_experience, titles)
        signals = AchievementIntelligenceEngine().analyze(achievements, responsibilities)

        if titles:
            progression_score = self._progression_score(titles)
            signals.append(
                CareerSignal(
                    category="Progression",
                    label="Career progression coherence",
                    score=progression_score,
                    evidence=titles[:8],
                )
            )

        career_score = self._career_score(years_experience, signals)

        return CareerIntelligenceReport(
            candidate_name=candidate_name,
            years_experience=years_experience,
            seniority_level=seniority,
            career_score=career_score,
            signals=signals,
        )

    def _seniority_level(self, years: int, titles: list[str]) -> str:
        title_text = " ".join(titles).lower()
        if any(word in title_text for word in ["director", "head", "vp", "chief", "directeur"]):
            return "Executive"
        if years >= 12:
            return "Senior+"
        if years >= 7:
            return "Senior"
        if years >= 3:
            return "Mid-level"
        return "Junior"

    def _progression_score(self, titles: list[str]) -> int:
        text = " ".join(titles).lower()
        score = 50
        if any(word in text for word in ["assistant", "officer", "analyst"]):
            score += 10
        if any(word in text for word in ["consultant", "project manager", "manager", "chef de projet"]):
            score += 20
        if any(word in text for word in ["lead", "director", "head", "responsable"]):
            score += 20
        return min(100, score)

    def _career_score(self, years: int, signals: list[CareerSignal]) -> int:
        base = min(70, years * 5)
        bonus = int(sum(signal.score for signal in signals) / len(signals) * 0.3) if signals else 0
        return min(100, base + bonus)
