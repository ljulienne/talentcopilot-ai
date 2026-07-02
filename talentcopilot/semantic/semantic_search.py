from __future__ import annotations

import re
from typing import Any, Dict, List

from talentcopilot.semantic.semantic_index import build_semantic_index


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9+#.-]+", text.lower())


def _score_document(query_tokens: List[str], document: str) -> int:
    doc = document.lower()

    score = 0

    for token in query_tokens:
        score += doc.count(token)

    return score


def semantic_search(
    talents: List[Dict[str, Any]],
    query: str,
    top_k: int = 5,
) -> List[Dict[str, Any]]:

    if not query.strip():
        return []

    query_tokens = _tokenize(query)

    index = build_semantic_index(talents)

    results = []

    for entry in index:
        score = _score_document(query_tokens, entry["document"])

        if score > 0:
            results.append(
                {
                    "score": score,
                    "talent": entry["talent"],
                }
            )

    results.sort(
        key=lambda x: (
            x["score"],
            x["talent"].get("talent_score", 0),
        ),
        reverse=True,
    )

    return results[:top_k]
