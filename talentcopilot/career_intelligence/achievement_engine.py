import re
from talentcopilot.career_intelligence.models import CareerSignal


class AchievementIntelligenceEngine:
    def analyze(self, achievements: list[str], responsibilities: list[str] | None = None) -> list[CareerSignal]:
        lines = [line for line in [*(achievements or []), *((responsibilities or []))] if line]
        signals = []

        impact_evidence = []
        leadership_evidence = []
        transformation_evidence = []

        for line in lines:
            lower = line.lower()

            if re.search(r"\d+\s?%|\$\s?\d+|€\s?\d+|\d+\s?(employees|users|agents|countries|pays|fte|collaborateurs)", lower):
                impact_evidence.append(line)

            if any(word in lower for word in ["led", "managed", "supervised", "directed", "piloté", "géré", "encadré", "team", "équipe"]):
                leadership_evidence.append(line)

            if any(word in lower for word in ["transformation", "change", "adoption", "implementation", "déploiement", "conduite du changement", "migration"]):
                transformation_evidence.append(line)

        if impact_evidence:
            signals.append(CareerSignal("Impact", "Quantified business impact", min(100, 60 + len(impact_evidence) * 10), impact_evidence[:5]))

        if leadership_evidence:
            signals.append(CareerSignal("Leadership", "Leadership responsibility", min(100, 60 + len(leadership_evidence) * 10), leadership_evidence[:5]))

        if transformation_evidence:
            signals.append(CareerSignal("Transformation", "Transformation delivery", min(100, 60 + len(transformation_evidence) * 10), transformation_evidence[:5]))

        return signals
