from talentcopilot.services.session_adapter import candidate_from_result, session_from_state


def test_zero_score_is_not_replaced_by_fallback_score():
    candidate = candidate_from_result({
        "candidate": {"name": "David Smith"},
        "match_score": 0,
        "overall_score": 41,
    })
    assert candidate.score == 0


def test_legacy_session_is_ranked_by_preserved_score():
    session = session_from_state(
        {"job_title": "Transformation Lead"},
        {
            "success": True,
            "results": [
                {"candidate": {"name": "David Smith"}, "match_score": 0},
                {"candidate": {"name": "Alice Martin"}, "match_score": 80},
                {"candidate": {"name": "Mei Chen"}, "match_score": 60},
            ],
        },
    )
    assert [item.candidate.name for item in session.results] == [
        "Alice Martin", "Mei Chen", "David Smith"
    ]
    assert [item.rank for item in session.results] == [1, 2, 3]
