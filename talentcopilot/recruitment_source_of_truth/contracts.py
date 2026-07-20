class SourceOfTruthViolation(RuntimeError):
    pass


READ_ONLY_FIELDS = frozenset({
    "candidate_id",
    "match_score",
    "decision_score",
    "rank",
    "mission_fit_rank",
    "decision_rank",
    "interview_priority",
})


def _positive_int(value, fallback=0):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return int(fallback or 0)
    return parsed if parsed > 0 else int(fallback or 0)


def assert_snapshot_matches_session(snapshot, session) -> None:
    analyses = list(getattr(session, "analyses", []) or [])
    mission_order = sorted(
        analyses,
        key=lambda item: (
            -float(getattr(item, "match_score", 0) or 0),
            str(getattr(item, "candidate_name", "")).casefold(),
            str(getattr(item, "candidate_id", "")),
        ),
    )
    computed_mission_ranks = {
        str(getattr(item, "candidate_id", "")): index
        for index, item in enumerate(mission_order, start=1)
    }

    current = {}
    for item in analyses:
        candidate_id = str(item.candidate_id)
        breakdown = dict(getattr(item, "score_breakdown", {}) or {})
        mission_rank = _positive_int(
            breakdown.get("mission_fit_rank"),
            computed_mission_ranks.get(candidate_id, getattr(item, "rank", 0)),
        )
        decision_rank = _positive_int(
            breakdown.get("decision_rank"),
            getattr(item, "rank", 0),
        )
        current[candidate_id] = (
            round(float(item.match_score or 0), 6),
            None if item.decision_score is None else round(float(item.decision_score), 6),
            mission_rank,
            decision_rank,
        )

    official = {
        item.candidate_id: (
            round(float(item.mission_fit_score or 0), 6),
            None if item.decision_score is None else round(float(item.decision_score), 6),
            int(item.mission_rank or 0),
            int(item.decision_rank or 0),
        )
        for item in snapshot.candidates
    }
    if current != official:
        raise SourceOfTruthViolation(
            "Recruitment session scores or ranks diverged from the frozen official snapshot."
        )
