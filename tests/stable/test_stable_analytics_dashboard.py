from talentcopilot.services.analytics_dashboard_service import AnalyticsDashboardService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_analytics_dashboard_empty_report():
    report = AnalyticsDashboardService().build(None)

    assert report.role_title == "No active recruitment"
    assert report.global_readiness == 0
    assert report.kpis
    assert report.signals
    assert report.recommendations


def test_analytics_dashboard_imports():
    module = __import__("talentcopilot.ui.analytics_dashboard", fromlist=["render_analytics_dashboard"])
    assert hasattr(module, "render_analytics_dashboard")


def test_analytics_dashboard_navigation():
    page = get_page_by_label("Analytics Dashboard")
    assert page is not None
    assert page.module == "talentcopilot.ui.analytics_dashboard"
    assert page.function == "render_analytics_dashboard"
