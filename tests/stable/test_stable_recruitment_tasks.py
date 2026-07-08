from talentcopilot.services.recruitment_tasks_service import RecruitmentTasksService


def test_recruitment_tasks_empty():
    report = RecruitmentTasksService().build(None)

    assert report.role_title == "No active recruitment"
    assert report.tasks
    assert report.open_tasks >= 1
    assert report.blockers


def test_recruitment_workspace_import_after_tasks_patch():
    module = __import__("talentcopilot.ui.recruitment_workspace", fromlist=["render_recruitment_workspace"])
    assert hasattr(module, "render_recruitment_workspace")
