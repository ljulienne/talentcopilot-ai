"""Canonical recruiter-facing candidate score resolution."""

from __future__ import annotations

from typing import Any


def get_official_candidate_score(analysis: Any) -> float:
    """Return ranking_score when available, otherwise raw match_score."""

    official = getattr(analysis, "official_match_score", None)

    if official is not None:
        try:
            return float(official)
        except (TypeError, ValueError):
            pass

    ranking = getattr(analysis, "ranking_score", None)

    if ranking is not None:
        try:
            return float(ranking)
        except (TypeError, ValueError):
            pass

    try:
        return float(getattr(analysis, "match_score", 0.0) or 0.0)
    except (TypeError, ValueError):
        return 0.0
