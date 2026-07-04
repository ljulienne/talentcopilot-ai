
from typing import Any, Dict, List

from talentcopilot.engines.decision_engine import evaluate_batch_decisions


def get_candidate_score(candidate: Dict[str, Any]) -> float:
    """
    Extract the best available ranking score from a talent or candidate dictionary.
    Priority:
    1. decision_score
    2. talent_score
    3. match_result.overall_score
    4. other legacy score fields
    """

    decision = candidate.get("decision")
    if isinstance(decision, dict):
        value = decision.get("decision_score")
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                pass

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


def rank_candidates(candidates: List[Dict[str, Any]], use_decision_engine: bool = True) -> List[Dict[str, Any]]:
    """
    Rank candidates from highest score to lowest score.

    If possible, enrich candidates with Decision Engine scores before ranking.
    """

    candidates_to_rank = candidates

    if use_decision_engine:
        try:
            candidates_to_rank = evaluate_batch_decisions(candidates)
        except Exception:
            candidates_to_rank = candidates

    ranked_candidates = sorted(
        candidates_to_rank,
        key=get_candidate_score,
        reverse=True,
    )

    for index, candidate in enumerate(ranked_candidates, start=1):
        candidate["rank"] = index

    return ranked_candidates
