from talentcopilot.services.session_manager import get_current_session


def test_get_current_session_is_callable():
    assert callable(get_current_session)
