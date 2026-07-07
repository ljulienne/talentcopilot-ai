from talentcopilot.ai.enterprise_pipeline import EnterprisePipeline
from talentcopilot.services.session_store import SessionStore


def test_session_store_class_fallback():
    SessionStore.clear()
    session = EnterprisePipeline().run(
        {"title": "Role", "required_skills": ["Python"]},
        [{"name": "Alice", "skills": ["Python"]}],
    )
    SessionStore.set_current_session(session)
    assert SessionStore.has_session() is True
    assert SessionStore.get_current_session().role_title == "Role"
    SessionStore.clear()
    assert SessionStore.has_session() is False
