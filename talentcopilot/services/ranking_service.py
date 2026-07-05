
from typing import Any, Dict, List


RANKING_MODE_OFFICIAL = "official_match_score"


def get_match_score(candidate_item: Dict[str, Any]) -> float:
    """
    Official TalentCopilot ranking score.

    The official ranking is always based on match_result.overall_score.
    Candidate Fit or Hiring Strategy scores must be handled separately.
    """

    match_result = candidate_item.get("match_result")

    if match_result is None:
        return 0.0

    value = getattr(match_result, "overall_score", 0)

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def rank_candidates(
    candidates: List[Dict[str, Any]],
    ranking_mode: str = RANKING_MODE_OFFICIAL,
) -> List[Dict[str, Any]]:
    """
    Rank candidates.

    Default and official mode:
    - official_match_score

    Future modes may include:
    - candidate_fit
    - hiring_strategy
    """

    if ranking_mode != RANKING_MODE_OFFICIAL:
        raise ValueError(
            f"Unsupported ranking mode: {ranking_mode}. "
            "Only official_match_score is currently supported."
        )

    ranked_candidates = sorted(
        candidates,
        key=get_match_score,
        reverse=True,
    )

    for index, candidate in enumerate(ranked_candidates, start=1):
        candidate["rank"] = index
        candidate["ranking_mode"] = RANKING_MODE_OFFICIAL
        candidate["official_ranking_score"] = get_match_score(candidate)

    return ranked_candidates
