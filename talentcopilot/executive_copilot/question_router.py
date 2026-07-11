from __future__ import annotations

import re

from .models import RoutedQuestion
from .question_catalog import QuestionCatalog


class QuestionRouter:
    def __init__(self, catalog: QuestionCatalog | None = None) -> None:
        self.catalog = catalog or QuestionCatalog()

    def route(self, text: str | None = None, *, question_id: str | None = None) -> RoutedQuestion:
        if question_id:
            question = self.catalog.get(question_id)
            if question is None:
                raise ValueError(f"Unknown executive question: {question_id}")
            return RoutedQuestion(question=question, matched_text=text or question.title, match_score=1.0)

        normalized = self._normalize(text or "")
        if not normalized:
            default = self.catalog.get("HR-OVERVIEW-001")
            assert default is not None
            return RoutedQuestion(question=default, matched_text="", match_score=0.5)

        best = None
        best_score = -1.0
        tokens = set(normalized.split())
        for question in self.catalog.all():
            score = 0.0
            for keyword in question.keywords:
                normalized_keyword = self._normalize(keyword)
                if normalized_keyword in normalized:
                    score += 2.0
                keyword_tokens = set(normalized_keyword.split())
                if keyword_tokens:
                    score += len(tokens.intersection(keyword_tokens)) / len(keyword_tokens)
            title_tokens = set(self._normalize(question.title).split())
            if title_tokens:
                score += len(tokens.intersection(title_tokens)) / len(title_tokens)
            if score > best_score:
                best = question
                best_score = score

        assert best is not None
        confidence = min(1.0, max(0.25, best_score / 4.0))
        return RoutedQuestion(question=best, matched_text=text or "", match_score=confidence)

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
