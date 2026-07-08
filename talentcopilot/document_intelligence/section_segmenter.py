from talentcopilot.document_intelligence.models import DocumentSection


class CVSectionSegmenter:
    HEADINGS = {
        "experience": ["experience", "expérience", "employment", "professional experience", "work experience"],
        "education": ["education", "formation", "academic background"],
        "skills": ["skills", "compétences", "technical skills", "expertise"],
        "languages": ["languages", "langues"],
        "certifications": ["certifications", "certification"],
        "projects": ["projects", "projets"],
    }

    def segment(self, text: str) -> list[DocumentSection]:
        lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
        if not lines:
            return []

        sections = []
        current_title = "profile"
        current_content = []

        for line in lines:
            matched = self._match_heading(line)
            if matched:
                if current_content:
                    sections.append(DocumentSection(current_title, "\n".join(current_content), confidence=75))
                current_title = matched
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections.append(DocumentSection(current_title, "\n".join(current_content), confidence=75))

        return sections or [DocumentSection("profile", text, confidence=60)]

    def _match_heading(self, line: str) -> str | None:
        normalized = line.lower().strip(":").strip()
        if len(normalized) > 40:
            return None
        for canonical, aliases in self.HEADINGS.items():
            if normalized in aliases:
                return canonical
        return None
