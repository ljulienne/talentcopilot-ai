from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import (
    clear_streamlit_session,
    get_streamlit_session,
    set_streamlit_session,
)


def test_session_bridge_without_streamlit_runtime():
    clear_streamlit_session()
    assert get_streamlit_session() is None

    session = create_demo_recruitment_session()
    set_streamlit_session(session)

    assert get_streamlit_session() is not None
    assert get_streamlit_session().session_id == session.session_id

    clear_streamlit_session()
    assert get_streamlit_session() is None
