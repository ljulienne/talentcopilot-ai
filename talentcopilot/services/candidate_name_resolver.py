"""Deterministic candidate-name resolution for uploaded resumes.

Resolution order:
1. Explicit personal email local part.
2. LinkedIn profile slug.
3. Standalone name-like line in the resume header.
4. Uploaded filename.
5. Existing pipeline extraction.

The resolver deliberately avoids treating employer or client names as
candidate identities.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Iterable


GENERIC_EMAIL_PREFIXES = {
    "contact",
    "hello",
    "info",
    "office",
    "admin",
    "recruitment",
    "recruiting",
    "career",
    "careers",
    "support",
    "mail",
    "email",
}

HEADER_LABELS = {
    "about me",
    "profile",
    "summary",
    "professional summary",
    "curriculum vitae",
    "resume",
    "cv",
    "competencies",
    "skills",
    "experience",
    "professional experience",
    "education",
    "contact",
    "personal details",
    "languages",
    "interests",
}

ROLE_WORDS = {
    "manager",
    "consultant",
    "director",
    "specialist",
    "analyst",
    "engineer",
    "officer",
    "lead",
    "leader",
    "architect",
    "developer",
    "coordinator",
    "administrator",
    "freelance",
    "contractor",
    "project",
    "program",
    "human",
    "resources",
    "hris",
}

ORGANIZATION_WORDS = {
    "bank",
    "group",
    "software",
    "consulting",
    "consultants",
    "company",
    "corporation",
    "corp",
    "limited",
    "ltd",
    "inc",
    "llc",
    "university",
    "institute",
    "systems",
    "services",
    "international",
    "credit",
    "finance",
    "financial",
    "technologies",
    "technology",
    "solutions",
}


class CandidateNameResolver:
    """Resolve a person's name from an uploaded resume."""

    def resolve(
        self,
        text: str,
        filename: str = "",
        extracted_name: str = "",
    ) -> str:
        source = self._clean_text(text)

        candidates = [
            self._from_email(source),
            self._from_linkedin(source),
            self._from_header(source),
            self._from_filename(filename),
            self._validate_existing(extracted_name),
        ]

        for candidate in candidates:
            normalized = self._normalize_name(candidate)
            if normalized and self._is_person_name(normalized):
                return normalized

        return "Unknown Candidate"

    def _from_email(self, text: str) -> str:
        matches = re.findall(
            r"\b([A-Z0-9._%+\-]+)@([A-Z0-9.\-]+\.[A-Z]{2,})\b",
            text,
            flags=re.IGNORECASE,
        )

        for local_part, _domain in matches:
            local = local_part.lower().strip("._-")

            if local in GENERIC_EMAIL_PREFIXES:
                continue

            parts = [
                part
                for part in re.split(r"[._\-]+", local)
                if part and not part.isdigit()
            ]

            if 2 <= len(parts) <= 4:
                return " ".join(parts)

        return ""

    def _from_linkedin(self, text: str) -> str:
        matches = re.findall(
            r"(?:linkedin\.com/in/|linkedin:\s*)([a-z0-9\-_%]+)",
            text,
            flags=re.IGNORECASE,
        )

        for slug in matches:
            clean = re.sub(r"%[0-9a-f]{2}", "", slug, flags=re.IGNORECASE)
            parts = [
                part
                for part in re.split(r"[-_.]+", clean)
                if part and not part.isdigit()
            ]

            # Slugs without separators are less reliable and are used only
            # when a plausible split can be inferred elsewhere.
            if 2 <= len(parts) <= 4:
                return " ".join(parts)

        return ""

    def _from_header(self, text: str) -> str:
        lines = [
            re.sub(r"\s+", " ", line).strip(" |•\t")
            for line in text.splitlines()
        ]
        lines = [line for line in lines if line]

        # Resume extraction order is not always visually ordered, so inspect
        # a generous header window while still avoiding experience tables.
        for line in lines[:60]:
            if self._is_header_name_line(line):
                return line

        return ""

    def _from_filename(self, filename: str) -> str:
        stem = Path(str(filename or "")).stem
        stem = re.sub(
            r"(?i)\b(cv|resume|curriculum|vitae|profile|candidate)\b",
            " ",
            stem,
        )
        stem = re.sub(r"\(\d+\)$", " ", stem)
        stem = re.sub(r"[_\-]+", " ", stem)
        stem = re.sub(r"\s+", " ", stem).strip()

        return stem if self._is_person_name(stem) else ""

    def _validate_existing(self, name: str) -> str:
        clean = self._normalize_name(name)

        if not clean:
            return ""

        if self._looks_like_organization(clean):
            return ""

        return clean

    def _is_header_name_line(self, line: str) -> bool:
        clean = self._normalize_name(line)

        if not clean:
            return False

        lower = clean.lower()

        if lower in HEADER_LABELS:
            return False

        if any(character.isdigit() for character in clean):
            return False

        if "@" in clean or "http" in lower or "www." in lower:
            return False

        if ":" in clean or "/" in clean or "\\" in clean:
            return False

        if len(clean) > 60:
            return False

        words = clean.split()

        if not 2 <= len(words) <= 4:
            return False

        if self._looks_like_organization(clean):
            return False

        if any(word.lower() in ROLE_WORDS for word in words):
            return False

        alphabetic_ratio = sum(
            character.isalpha() or character in "'’ -"
            for character in clean
        ) / max(1, len(clean))

        if alphabetic_ratio < 0.95:
            return False

        # A header name is usually Title Case or uppercase.
        return all(
            self._looks_like_name_token(word)
            for word in words
        )

    def _is_person_name(self, value: str) -> bool:
        clean = self._normalize_name(value)

        if not clean:
            return False

        words = clean.split()

        if not 2 <= len(words) <= 4:
            return False

        if self._looks_like_organization(clean):
            return False

        if any(word.lower() in ROLE_WORDS for word in words):
            return False

        return all(self._looks_like_name_token(word) for word in words)

    def _looks_like_organization(self, value: str) -> bool:
        words = {
            re.sub(r"[^a-z]", "", word.lower())
            for word in value.split()
        }

        return bool(words & ORGANIZATION_WORDS)

    def _looks_like_name_token(self, token: str) -> bool:
        clean = token.strip("'’.- ")

        if len(clean) < 2:
            return False

        if not re.fullmatch(
            r"[A-Za-zÀ-ÖØ-öø-ÿ'’\-]+",
            clean,
        ):
            return False

        return clean.isupper() or clean.istitle() or clean.islower()

    def _normalize_name(self, value: str) -> str:
        clean = unicodedata.normalize("NFKC", str(value or ""))
        clean = re.sub(r"\s+", " ", clean).strip(" ,;|•\t")

        if not clean:
            return ""

        return " ".join(
            self._format_token(token)
            for token in clean.split()
        )

    def _format_token(self, token: str) -> str:
        parts = re.split(r"([\-’'])", token.lower())

        return "".join(
            part.capitalize()
            if part not in {"-", "’", "'"}
            else part
            for part in parts
        )

    def _clean_text(self, text: str) -> str:
        return unicodedata.normalize(
            "NFKC",
            str(text or ""),
        )
