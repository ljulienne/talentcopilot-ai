from pathlib import Path

from talentcopilot.services.blueprint_overview_service import BlueprintOverviewService
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_blueprint_overview_service():
    overview = BlueprintOverviewService().build()

    assert "Blueprint" in overview.title
    assert overview.principles
    assert overview.layers
    assert overview.next_chapters


def test_blueprint_overview_imports():
    module = __import__("talentcopilot.ui.blueprint_overview", fromlist=["render_blueprint_overview"])
    assert hasattr(module, "render_blueprint_overview")


def test_blueprint_overview_navigation():
    page = get_page_by_label("Blueprint Overview")
    assert page is not None
    assert page.module == "talentcopilot.ui.blueprint_overview"
    assert page.function == "render_blueprint_overview"


def test_blueprint_docs_exist():
    repo = Path.cwd()
    docs = repo / "docs" / "blueprint"
    assert (docs / "README.md").exists()
    assert (docs / "01_vision_and_strategy.md").exists()
    assert (docs / "02_product_principles.md").exists()
