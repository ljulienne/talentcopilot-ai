"""Hotfix 3.3.1 — obsolete Streamlit score cache invalidation."""

from pathlib import Path


PANEL = (
    Path(__file__).resolve().parents[1]
    / "talentcopilot"
    / "ui"
    / "recruitment_upload_panel.py"
)


def _source() -> str:
    return PANEL.read_text(encoding="utf-8")


def test_analysis_request_key_contains_official_score_schema():
    source = _source()

    assert (
        'OFFICIAL_SCORE_CACHE_SCHEMA = '
        '"official-fit-session-v3.3.1"'
    ) in source

    components_start = source.index("components = [")
    components_end = source.index("]", components_start)
    components = source[components_start:components_end]

    assert "OFFICIAL_SCORE_CACHE_SCHEMA" in components


def test_cached_session_requires_matching_score_schema():
    source = _source()

    assert "cached_session_schema =" in source
    assert (
        "cached_session_schema == OFFICIAL_SCORE_CACHE_SCHEMA"
        in source
    )


def test_new_session_records_score_schema():
    source = _source()

    assert '"official_score_cache_schema"' in source
    assert "OFFICIAL_SCORE_CACHE_SCHEMA" in source


def test_upload_still_uses_official_real_pipeline():
    source = _source()

    assert "RecruitmentUploadSessionService().run(" in source
    assert "set_streamlit_session(session)" in source
