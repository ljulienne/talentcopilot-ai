from talentcopilot.ui.session_health import render_session_health


def test_session_health_is_callable():
    assert callable(render_session_health)
