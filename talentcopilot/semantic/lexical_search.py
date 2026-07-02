from __future__ import annotations

from typing import Any, Dict, List

from talentcopilot.semantic.search_engine import SearchEngine
from talentcopilot.semantic.semantic_search import semantic_search


class LexicalSearchEngine(SearchEngine):
    def search(
        self,
        talents: List[Dict[str, Any]],
        query: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        return semantic_search(
            talents=talents,
            query=query,
            top_k=top_k,
        )
