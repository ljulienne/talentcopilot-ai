from talentcopilot.services.enterprise_demo_final_service import EnterpriseDemoFinalService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_enterprise_demo_final_report():
    report = EnterpriseDemoFinalService().build(None)

    assert "TalentCopilot" in report.title
    assert report.steps
    assert report.total_duration_minutes >= 20
    assert report.readiness_items


def test_enterprise_demo_final_imports():
    module = __import__("talentcopilot.ui.enterprise_demo_final", fromlist=["render_enterprise_demo_final"])
    assert hasattr(module, "render_enterprise_demo_final")


def test_enterprise_demo_final_navigation():
    page = get_page_by_label("Enterprise Demo Final")
    assert page is not None
    assert page.module == "talentcopilot.ui.enterprise_demo_final"
    assert page.function == "render_enterprise_demo_final"
