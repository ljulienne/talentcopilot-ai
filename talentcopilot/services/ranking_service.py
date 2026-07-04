
from typing import Any, Dict, List

from talentcopilot.engines.weighted_ranking_engine import enrich_with_weighted_ranking


def get_candidate_score(candidate: Dict[str, Any]) -> float:
    """
    Official ranking rule:
    use weighted_ranking.weighted_ranking_score when available.
    Fallback to match_result.overall_score.
    """

    weighted = candidate.get("weighted_ranking")
    if isinstance(weighted, dict):
        value = weighted.get("weighted_ranking_score")
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass

    match_result = candidate.get("match_result")
    if match_result is not None:
        value = getattr(match_result, "overall_score", None)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass

    return 0.0


def rank_candidates(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Rank candidates using the official weighted ranking score.
    """

    enriched_candidates = enrich_with_weighted_ranking(candidates)

    ranked_candidates = sorted(
        enriched_candidates,
        key=get_candidate_score,
        reverse=True,
    )

    for index, candidate in enumerate(ranked_candidates, start=1):
        candidate["rank"] = index

    return ranked_candidates
