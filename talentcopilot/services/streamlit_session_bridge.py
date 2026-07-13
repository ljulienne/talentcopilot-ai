from typing import Any, Optional

from talentcopilot.services.session_store import SessionStore
from talentcopilot.services.analysis_provenance import (
    session_compatibility_reason,
)


SESSION_STATE_KEY = "talentcopilot_recruitment_session"
SESSION_INVALIDATION_NOTICE_KEY = "talentcopilot_session_invalidation_notice"


def set_streamlit_session(session: Any) -> Any:
    SessionStore.set_current_session(session)
    try:
        import streamlit as st
        st.session_state[SESSION_STATE_KEY] = session
    except Exception:
        pass
    return session


def _invalidate_if_obsolete(session: Optional[Any]) -> Optional[Any]:
    reason = session_compatibility_reason(session)
    if reason is None:
        return session

    clear_streamlit_session()

    try:
        import streamlit as st
        st.session_state[SESSION_INVALIDATION_NOTICE_KEY] = reason
    except Exception:
        pass

    return None


def get_streamlit_session() -> Optional[Any]:
    try:
        import streamlit as st
        session = st.session_state.get(SESSION_STATE_KEY)
        session = _invalidate_if_obsolete(session)
        if session is not None:
            SessionStore.set_current_session(session)
            return session
    except Exception:
        pass

    return _invalidate_if_obsolete(
        SessionStore.get_current_session()
    )


def consume_session_invalidation_notice() -> str:
    try:
        import streamlit as st
        return str(
            st.session_state.pop(
                SESSION_INVALIDATION_NOTICE_KEY,
                "",
            )
            or ""
        )
    except Exception:
        return ""


def clear_streamlit_session() -> None:
    SessionStore.clear()
    try:
        import streamlit as st
        if SESSION_STATE_KEY in st.session_state:
            del st.session_state[SESSION_STATE_KEY]
    except Exception:
        pass


def ensure_demo_session():
    session = get_streamlit_session()
    if session is not None:
        return session

    from talentcopilot.services.demo_session_factory import create_demo_recruitment_session

    return set_streamlit_session(create_demo_recruitment_session())
