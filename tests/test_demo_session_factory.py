from talentcopilot.services.demo_session_factory import DemoSessionFactory
from talentcopilot.services.session_store import SessionStore


def test_demo_session_factory_creates_analyzed_session():
    SessionStore.clear()
    session = DemoSessionFactory().create_demo_session(candidate_limit=3)

    assert session.candidate_count == 3
    assert session.analyzed_count == 3
    assert session.role_title
    assert SessionStore.get_current_session() is session
    assert all(not str(skill).startswith("SK") for c in session.candidates for skill in c.get("skills", []))
