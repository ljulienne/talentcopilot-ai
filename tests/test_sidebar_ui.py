from talentcopilot.ui.sidebar import (
    render_sidebar_brand,
    render_sidebar_context,
    render_sidebar_workflow,
)


def test_sidebar_components_are_callable():
    assert callable(render_sidebar_brand)
    assert callable(render_sidebar_context)
    assert callable(render_sidebar_workflow)
