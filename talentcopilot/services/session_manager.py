import streamlit as st

from talentcopilot.models.recruitment import RecruitmentSession
from talentcopilot.services.session_adapter import session_from_state


def get_current_session() -> RecruitmentSession:
    return session_from_state(
        recruitment_context=st.session_state.get("recruitment_context"),
        analysis_batch=st.session_state.get("analysis_batch"),
    )
