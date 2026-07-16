from pathlib import Path

from talentcopilot.services.isolated_recruitment_upload_service import (
    IsolatedRecruitmentUploadService,
)
from talentcopilot.services.upload_text_reader_service import (
    UploadedTextDocument,
)


def test_isolated_service_returns_official_session():
    job = UploadedTextDocument(
        filename="job.txt",
        file_type="txt",
        text=(
            "Transformation Lead\n"
            "Requirements\n"
            "Minimum 6 years experience.\n"
            "Skills\n"
            "HRIS, Project Management, "
            "Stakeholder Management"
        ),
    )
    candidates = [
        UploadedTextDocument(
            filename="alice.txt",
            file_type="txt",
            text=(
                "Alice Martin\n"
                "8 years experience\n"
                "Skills\n"
                "HRIS, Project Management, "
                "Stakeholder Management"
            ),
        )
    ]

    session = IsolatedRecruitmentUploadService().run(
        job,
        candidates,
    )

    assert session.metadata["source"] == "real_upload"
    assert (
        session.metadata["execution_mode"]
        == "isolated_subprocess"
    )
    assert (
        session.metadata["canonical_score_contract"]
        == "fit-score-v1"
    )
    assert len(session.ranked_analyses) == 1


def test_streamlit_panel_uses_isolated_service():
    source = Path(
        "talentcopilot/ui/recruitment_upload_panel.py"
    ).read_text(encoding="utf-8")

    assert "IsolatedRecruitmentUploadService" in source
    assert (
        "IsolatedRecruitmentUploadService().run("
        in source
    )
    assert (
        "RecruitmentUploadSessionService().run("
        not in source
    )
    assert (
        "isolated-fit-session-v3.4"
        in source
    )


def test_temporary_runtime_diagnostics_are_removed():
    source = Path(
        "talentcopilot/ui/"
        "recruitment_decision_workspace.py"
    ).read_text(encoding="utf-8")

    assert "Runtime score diagnostic" not in source
    assert (
        "Candidate inputs stored in active session"
        not in source
    )
