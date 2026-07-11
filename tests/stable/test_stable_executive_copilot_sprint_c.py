from pathlib import Path

from talentcopilot.ui.navigation_actions import ENGINE_PAGE_MAP, page_for_engine


def test_engine_navigation_targets_visible_workspaces():
    assert page_for_engine("Skills") == "Organization Intelligence"
    assert page_for_engine("Workforce") == "Organization Intelligence"
    assert page_for_engine("Recruitment") == "Recruitment Workspace"
    assert page_for_engine("Decision") == "Decision Board"
    assert ENGINE_PAGE_MAP


def test_workspace_supports_follow_up_and_action_plan():
    workspace = Path("talentcopilot/ui/executive_copilot_workspace.py").read_text(
        encoding="utf-8"
    )
    response = Path("talentcopilot/ui/executive/response_view.py").read_text(
        encoding="utf-8"
    )
    assert "executive_copilot_pending_question_id" in workspace
    assert "executive_copilot_auto_generate" in workspace
    assert "_render_action_plan" in workspace
    assert "Add to session action plan" in response
    assert "request_page" in response
    assert "disabled=True" not in response


def test_shell_consumes_contextual_navigation_request():
    app_text = Path("app.py").read_text(encoding="utf-8")
    assert "consume_page_request" in app_text
    assert 'key="enterprise_section_key"' in app_text
    assert 'key="enterprise_page_label"' in app_text
