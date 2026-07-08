from talentcopilot.services.demo_experience_service import DemoExperienceService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_demo_experience_empty_report():
    report = DemoExperienceService().build(None)

    assert report.scenario_name
    assert report.readiness_score == 0
    assert report.steps
    assert report.checks


def test_demo_experience_imports():
    module = __import__("talentcopilot.ui.demo_experience", fromlist=["render_demo_experience"])
    assert hasattr(module, "render_demo_experience")


def test_demo_experience_navigation():
    page = get_page_by_label("Demo Experience")
    assert page is not None
    assert page.module == "talentcopilot.ui.demo_experience"
    assert page.function == "render_demo_experience"
