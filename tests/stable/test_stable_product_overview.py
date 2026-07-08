from talentcopilot.services.product_overview_service import ProductOverviewService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_product_overview_service():
    overview = ProductOverviewService().build()

    assert "Better Hiring Decisions" in overview.tagline
    assert overview.workspaces
    assert overview.personas
    assert overview.demo_flow


def test_product_overview_imports():
    module = __import__("talentcopilot.ui.product_overview", fromlist=["render_product_overview"])
    assert hasattr(module, "render_product_overview")


def test_product_overview_navigation():
    page = get_page_by_label("Product Overview")
    assert page is not None
    assert page.module == "talentcopilot.ui.product_overview"
    assert page.function == "render_product_overview"
