from pathlib import Path


def test_score_cache_schema_invalidates_pre_4_2_sessions():
    source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    assert (
        'OFFICIAL_SCORE_CACHE_SCHEMA = '
        '"isolated-fit-session-v4.2.2"'
        in source
    )

    assert (
        'OFFICIAL_SCORE_CACHE_SCHEMA = '
        '"isolated-fit-session-v3.4"'
        not in source
    )

    assert "cached_session_schema == OFFICIAL_SCORE_CACHE_SCHEMA" in source
    assert '"official_score_cache_schema"' in source
