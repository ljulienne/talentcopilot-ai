from talentcopilot.services.recruitment_pipeline_service import RecruitmentPipelineService


def test_recruitment_pipeline_empty():
    report = RecruitmentPipelineService().build(None)

    assert report.role_title == "No active recruitment"
    assert report.overall_readiness == 0
    assert report.stages
    assert report.next_actions


def test_recruitment_workspace_import_after_pipeline_patch():
    module = __import__("talentcopilot.ui.recruitment_workspace", fromlist=["render_recruitment_workspace"])
    assert hasattr(module, "render_recruitment_workspace")
