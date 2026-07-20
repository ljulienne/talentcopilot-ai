class SourceOfTruthViolation(RuntimeError):
    pass


READ_ONLY_FIELDS = frozenset({
    "candidate_id",
    "match_score",
    "decision_score",
    "rank",
    "mission_fit_rank",
    "decision_rank",
})


def assert_snapshot_matches_session(snapshot, session) -> None:
    current = {
        str(item.candidate_id): (
            round(float(item.match_score or 0), 6),
            None if item.decision_score is None else round(float(item.decision_score), 6),
            int(item.rank or 0),
        )
        for item in getattr(session, "analyses", [])
    }
    official = {
        item.candidate_id: (
            round(float(item.mission_fit_score or 0), 6),
            None if item.decision_score is None else round(float(item.decision_score), 6),
            int(item.decision_rank or 0),
        )
        for item in snapshot.candidates
    }
    if current != official:
        raise SourceOfTruthViolation(
            "Recruitment session scores or ranks diverged from the frozen official snapshot."
        )
