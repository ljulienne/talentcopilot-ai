from talentcopilot.ui.enterprise_navigation import (
    flatten_enterprise_pages,
    get_page_by_label,
)


def test_comparison_and_decision_board_remain_hidden_from_primary_navigation():
    labels = [
        page.label
        for page in flatten_enterprise_pages()
    ]

    assert "Comparison" not in labels
    assert "Decision Board" not in labels


def test_hidden_workflow_routes_remain_resolvable():
    comparison = get_page_by_label("Comparison")
    decision = get_page_by_label("Decision Board")

    assert comparison is not None
    assert decision is not None

    assert comparison.module == (
        "talentcopilot.ui.comparison_workspace"
    )

    assert decision.module == (
        "talentcopilot.ui.decision_board"
    )
