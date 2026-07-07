from talentcopilot.ai.product_readiness_engine import ProductReadinessEngine
from talentcopilot.ui.product_readiness_cards import render_product_readiness


def test_product_readiness_ui_import_safe():
    report = ProductReadinessEngine().assess()
    render_product_readiness(report)
