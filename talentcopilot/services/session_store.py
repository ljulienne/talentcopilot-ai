from typing import Optional

from talentcopilot.models.recruitment_session import RecruitmentSession


class SessionStore:
    """
    Lightweight session store with Streamlit compatibility.

    Priority:
    1. Streamlit `st.session_state["recruitment_session"]` when Streamlit is available.
    2. Class-level fallback for tests and non-Streamlit contexts.
    """

    _current_session: Optional[RecruitmentSession] = None
    STREAMLIT_KEY = "recruitment_session"

    @classmethod
    def _streamlit_state(cls):
        try:
            import streamlit as st
            return st.session_state
        except Exception:
            return None

    @classmethod
    def set_current_session(cls, session: RecruitmentSession) -> RecruitmentSession:
        cls._current_session = session
        state = cls._streamlit_state()
        if state is not None:
            state[cls.STREAMLIT_KEY] = session
            state["current_recruitment"] = session
            state["recruitment_context"] = {
                "session_id": session.session_id,
                "title": session.role_title,
                "candidate_count": session.candidate_count,
                "analyzed_count": session.analyzed_count,
            }
        return session

    @classmethod
    def get_current_session(cls) -> Optional[RecruitmentSession]:
        state = cls._streamlit_state()
        if state is not None and cls.STREAMLIT_KEY in state:
            return state[cls.STREAMLIT_KEY]
        return cls._current_session

    @classmethod
    def clear(cls) -> None:
        cls._current_session = None
        state = cls._streamlit_state()
        if state is not None:
            for key in [cls.STREAMLIT_KEY, "current_recruitment", "recruitment_context"]:
                if key in state:
                    del state[key]

    @classmethod
    def has_session(cls) -> bool:
        return cls.get_current_session() is not None
