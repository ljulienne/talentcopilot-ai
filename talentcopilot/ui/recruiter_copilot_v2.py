from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.ui.enterprise_components import hero, safe_render
from talentcopilot.ui.feature_restoration_components import page_purpose, session_required_hint


@safe_render
def render_recruiter_copilot_v2(*args, **kwargs):
    import streamlit as st

    hero(
        "Recruiter Copilot",
        "Turn analysis into next actions, interview questions and stakeholder summaries.",
        "Decide",
    )

    page_purpose(
        "Recruiter Copilot",
        "This page is for action, not analysis.",
        [
            "See recommended recruiter actions.",
            "Prepare interview questions.",
            "Summarize each candidate for stakeholders.",
        ],
    )

    session = get_streamlit_session()
    if not session_required_hint(session):
        return

    has_guidance = False
    for analysis in session.ranked_analyses:
        report = analysis.recruiter_copilot_report
        if not report:
            continue

        has_guidance = True
        with st.expander(f"{analysis.candidate_name} — {report.headline}"):
            st.write(report.recruiter_summary)

            if report.actions:
                st.markdown("**Actions**")
                for action in report.actions:
                    st.write(f"- **{action.title}** — {action.rationale}")

            if report.interview_questions:
                st.markdown("**Interview questions**")
                for question in report.interview_questions[:5]:
                    st.write(f"- {question.question}")

            if report.stakeholder_summary:
                st.markdown("**Stakeholder summary**")
                st.info(report.stakeholder_summary)

    if not has_guidance:
        st.info("No recruiter copilot guidance available yet. Run or refresh analysis from Decision Center.")
