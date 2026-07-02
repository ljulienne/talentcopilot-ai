from __future__ import annotations

import re
from typing import Any, Dict, List

from talentcopilot.semantic.semantic_index import build_semantic_index


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z0-9+#.-]+", text.lower())


def _lexical_score(query_tokens: List[str], document: str) -> int:
    document = document.lower()

    score = 0

    for token in query_tokens:
        score += document.count(token)

    return score


def _hybrid_score(
    lexical_score: int,
    talent: Dict[str, Any],
) -> float:

    talent_score = talent.get("talent_score", 0)
    average_match = talent.get("average_score", 0)
    confidence = talent.get("average_confidence", 0)

    return (
        lexical_score * 10
        + talent_score * 0.4
        + average_match * 0.3
        + confidence * 0.3
    )


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

        lexical = _lexical_score(
            query_tokens,
            entry["document"],
        )

        if lexical == 0:
            continue

        hybrid = _hybrid_score(
            lexical,
            entry["talent"],
        )

        results.append(
            {
                "lexical_score": lexical,
                "semantic_score": round(hybrid, 2),
                "talent": entry["talent"],
            }
        )

    results.sort(
        key=lambda item: item["semantic_score"],
        reverse=True,
    )

    return results[:top_k]
