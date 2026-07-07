from talentcopilot.models.recruitment_session import RecruitmentSession
from talentcopilot.services.session_store import SessionStore


def test_session_store_set_get_clear():
    SessionStore.clear()
    assert SessionStore.has_session() is False

    session = RecruitmentSession(
        session_id="session-test",
        job={"title": "Role"},
    )

    SessionStore.set_current_session(session)

    assert SessionStore.has_session() is True
    assert SessionStore.get_current_session().session_id == "session-test"

    SessionStore.clear()
    assert SessionStore.get_current_session() is None
