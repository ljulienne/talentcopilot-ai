import re
from typing import List


class TextSignalExtractor:
    def extract_years_experience(self, text: str) -> int:
        lower = (text or "").lower()
        candidates = []

        patterns = [
            r"(\d{1,2})\+?\s+(?:years|ans)\s+(?:of\s+)?(?:experience|expérience)",
            r"(?:experience|expérience)\s+(?:of\s+)?(\d{1,2})\+?\s+(?:years|ans)",
            r"(\d{1,2})\+?\s+(?:years|ans)",
        ]

        for pattern in patterns:
            for match in re.findall(pattern, lower):
                try:
                    value = int(match)
                    if 0 <= value <= 50:
                        candidates.append(value)
                except ValueError:
                    continue

        return max(candidates) if candidates else 0

    def extract_languages(self, text: str) -> List[str]:
        lower = (text or "").lower()
        mapping = {
            "French": ["french", "français", "francais"],
            "English": ["english", "anglais"],
            "Mandarin": ["mandarin", "chinese", "chinois", "中文", "普通话"],
            "Spanish": ["spanish", "espagnol"],
        }
        found = []
        for language, aliases in mapping.items():
            if any(alias in lower for alias in aliases):
                found.append(language)
        return found

    def extract_certifications(self, text: str) -> List[str]:
        lower = (text or "").lower()
        mapping = {
            "PMP": ["pmp", "project management professional"],
            "PHRi": ["phri"],
            "SPHRi": ["sphri"],
            "PRINCE2": ["prince2"],
            "Scrum": ["scrum master", "scrum"],
            "ITIL": ["itil"],
        }
        found = []
        for cert, aliases in mapping.items():
            if any(alias in lower for alias in aliases):
                found.append(cert)
        return found

    def extract_achievements(self, text: str) -> List[str]:
        achievements = []
        lines = [line.strip(" -•*") for line in (text or "").splitlines() if line.strip()]
        for line in lines:
            lower = line.lower()
            has_metric = bool(re.search(r"\d+\s?%|\d+\s?(?:employees|users|agents|countries|pays|fte|people|collaborateurs)", lower))
            has_impact = any(word in lower for word in ["improved", "reduced", "increased", "decreased", "deployed", "implemented", "led", "piloté", "déployé", "amélioré", "réduit"])
            if has_metric or has_impact:
                achievements.append(line[:240])
        return list(dict.fromkeys(achievements))[:8]

    def extract_responsibilities(self, text: str) -> List[str]:
        responsibilities = []
        lines = [line.strip(" -•*") for line in (text or "").splitlines() if line.strip()]
        verbs = ["lead", "manage", "implement", "deploy", "coordinate", "pilot", "piloter", "gérer", "déployer", "coordonner", "animer"]
        for line in lines:
            lower = line.lower()
            if any(lower.startswith(v) or f" {v}" in lower for v in verbs):
                responsibilities.append(line[:220])
        return list(dict.fromkeys(responsibilities))[:10]
