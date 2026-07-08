from talentcopilot.services.executive_reporting_service import ExecutiveReportingService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_executive_reporting_empty_report():
    service = ExecutiveReportingService()
    report = service.build(None)

    assert report.role_title == "No active recruitment"
    assert report.recommendations
    assert "Executive Recruitment Report" in service.to_markdown(report)


def test_executive_reporting_imports():
    module = __import__("talentcopilot.ui.executive_reporting", fromlist=["render_executive_reporting"])
    assert hasattr(module, "render_executive_reporting")


def test_executive_reporting_navigation():
    page = get_page_by_label("Executive Reporting")
    assert page is not None
    assert page.module == "talentcopilot.ui.executive_reporting"
    assert page.function == "render_executive_reporting"
