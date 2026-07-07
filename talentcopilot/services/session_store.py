from typing import Optional

from talentcopilot.models.recruitment_session import RecruitmentSession


class SessionStore:
    """
    Lightweight in-memory session store.

    In Streamlit, this can be bridged with st.session_state.
    Later, it can be replaced by persistence in database or files.
    """

    _current_session: Optional[RecruitmentSession] = None

    @classmethod
    def set_current_session(cls, session: RecruitmentSession) -> RecruitmentSession:
        cls._current_session = session
        return session

    @classmethod
    def get_current_session(cls) -> Optional[RecruitmentSession]:
        return cls._current_session

    @classmethod
    def clear(cls) -> None:
        cls._current_session = None

    @classmethod
    def has_session(cls) -> bool:
        return cls._current_session is not None
