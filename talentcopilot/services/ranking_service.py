
from typing import Any, Dict, List


def get_candidate_score(candidate: Dict[str, Any]) -> float:
    """
    Extract the best available score from a talent or candidate dictionary.
    """

    score_fields = [
        "talent_score",
        "overall_score",
        "average_score",
        "score",
        "match_score",
        "final_score",
    ]

    for field in score_fields:
        value = candidate.get(field)

        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                continue

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
    Rank candidates from highest score to lowest score.
    """

    ranked_candidates = sorted(
        candidates,
        key=get_candidate_score,
        reverse=True,
    )

    for index, candidate in enumerate(ranked_candidates, start=1):
        candidate["rank"] = index

    return ranked_candidates
