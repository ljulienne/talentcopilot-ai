from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

APP_SOURCE = (
    ROOT / "app.py"
).read_text(encoding="utf-8")

CANDIDATE_SOURCE = (
    ROOT
    / "talentcopilot"
    / "ui"
    / "candidate_workspace.py"
).read_text(encoding="utf-8")


def test_workflow_shell_is_rendered_globally_once():
    assert "render_recruitment_workflow_shell(" in APP_SOURCE


def test_candidate_intelligence_does_not_render_local_workflow_shell():
    assert (
        "render_recruitment_workflow_shell"
        not in CANDIDATE_SOURCE
    )


def test_candidate_intelligence_preserves_workflow_context():
    assert "get_workflow_context(" in CANDIDATE_SOURCE
    assert "select_workflow_candidate(" in CANDIDATE_SOURCE
