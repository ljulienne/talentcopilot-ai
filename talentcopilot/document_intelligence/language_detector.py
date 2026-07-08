class LanguageDetector:
    def detect(self, text: str) -> str:
        sample = text or ""
        if any("\u4e00" <= char <= "\u9fff" for char in sample):
            return "zh"

        lower = sample.lower()
        french_markers = ["expérience", "formation", "compétences", "diplôme", "langues", "emploi"]
        english_markers = ["experience", "education", "skills", "certification", "languages", "employment"]

        fr_score = sum(1 for marker in french_markers if marker in lower)
        en_score = sum(1 for marker in english_markers if marker in lower)

        if fr_score > en_score:
            return "fr"
        if en_score > fr_score:
            return "en"
        return "unknown"
