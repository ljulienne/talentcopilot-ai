from talentcopilot.models.recruitment_session import (
    CandidateAnalysisState,
    CandidateAnalysisStatus,
    RecruitmentSession,
)
from talentcopilot.ui.enterprise_navigation import flatten_enterprise_pages, get_page_by_label
from talentcopilot.ui.project_hub import (
    activate_recruitment_project,
    build_project_summaries,
    render_project_hub,
    session_from_recruitment_data,
)


def _active_session():
    return RecruitmentSession(
        session_id="REC-ACTIVE",
        job={"title": "Transformation Lead"},
        candidates=[{"name": "Alice"}, {"name": "Bob"}],
        analyses=[
            CandidateAnalysisState(
                candidate_name="Alice",
                status=CandidateAnalysisStatus.ANALYZED,
                match_score=88,
                rank=1,
            )
        ],
    )


def test_project_hub_is_importable():
    assert callable(render_project_hub)


def test_project_hub_combines_active_and_saved_projects_without_duplicates():
    projects = build_project_summaries(
        _active_session(),
        [
            {"id": "REC-ACTIVE", "title": "Duplicate", "candidate_count": 2},
            {"id": "REC-SAVED", "title": "Finance Manager", "candidate_count": 3, "updated_at": "2026-07-10T10:00:00"},
        ],
    )
    assert [project.project_id for project in projects] == ["REC-ACTIVE", "REC-SAVED"]
    assert projects[0].is_active is True
    assert projects[0].progress_percent == 50


def test_saved_recruitment_can_be_reconstructed_as_active_session():
    data = {
        "id": "REC-SAVED",
        "title": "HRIS Project Manager",
        "analysis_batch": {
            "success": True,
            "results": [
                {"candidate": {"name": "Alice"}, "match_score": 91, "rank": 1},
                {"candidate": {"name": "Bob"}, "match_score": 76, "rank": 2},
            ],
        },
    }
    session = session_from_recruitment_data(data)
    assert session.session_id == "REC-SAVED"
    assert session.role_title == "HRIS Project Manager"
    assert session.candidate_count == 2
    assert session.analyzed_count == 2
    assert session.ranked_analyses[0].candidate_name == "Alice"


def test_activate_recruitment_project_returns_session_outside_streamlit():
    session = activate_recruitment_project({"id": "REC-1", "title": "Recruitment", "analysis_batch": {"results": []}})
    assert session.session_id == "REC-1"


def test_projects_is_primary_navigation_destination():
    labels = [page.label for page in flatten_enterprise_pages()]
    assert labels[:2] == ["Executive Brief", "Projects"]
    page = get_page_by_label("Projects")
    assert page is not None
    assert page.module == "talentcopilot.ui.project_hub"
