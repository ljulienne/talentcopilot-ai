from talentcopilot.services.release_readiness_service import ReleaseReadinessService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_release_readiness_builds():
    report = ReleaseReadinessService().build()

    assert report.score >= 0
    assert report.checks
    assert report.recommendations


def test_release_readiness_imports():
    module = __import__("talentcopilot.ui.release_readiness", fromlist=["render_release_readiness"])
    assert hasattr(module, "render_release_readiness")


def test_release_readiness_navigation():
    page = get_page_by_label("Release Readiness")
    assert page is not None
    assert page.module == "talentcopilot.ui.release_readiness"
    assert page.function == "render_release_readiness"
