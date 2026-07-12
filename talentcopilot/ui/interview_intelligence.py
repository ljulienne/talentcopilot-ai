from __future__ import annotations

from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.interview.workspace_service import InterviewWorkspaceService
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


CACHE_PREFIX = "interview_strategy_"


def _cache_key(session, report) -> str:
    session_id = str(getattr(session, "session_id", "session"))
    candidate_id = ""
    for analysis in getattr(session, "ranked_analyses", []) or []:
        if analysis.candidate_name == report.candidate_name:
            candidate_id = str(getattr(analysis, "candidate_id", ""))
            break
    return (
        f"{CACHE_PREFIX}{session_id}:{candidate_id or report.candidate_name}:"
        f"{report.fit_score:.4f}:{InterviewQuestionService.ENGINE_VERSION}"
    )


def _render_strategy(report, questions):
    import streamlit as st

    section_title("Interview objectives")
    for gap in report.readiness.gaps:
        st.warning(gap)
    if not report.readiness.gaps:
        st.success("No major pre-interview gap was detected. Use the interview to validate depth and ownership.")

    section_title("Evidence validation matrix")
    rows = [
        {
            "Competency": item.name,
            "Evidence": item.evidence_level,
            "Confidence": f"{item.confidence}%",
            "Interview priority": "Validate" if item.validate_in_interview else "Confirm",
            "Why": item.rationale,
        }
        for item in report.competencies
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    section_title("Targeted interview questions")
    for index, question in enumerate(questions, start=1):
        with st.expander(f"{index}. {question.competency}", expanded=index == 1):
            st.markdown(f"**Question**  \n{question.question}")
            st.markdown(f"**Hypothesis tested / why it matters**  \n{question.objective}")
            st.markdown("**A strong answer should include**")
            for item in question.expected_evidence:
                st.write(f"- {item}")
            st.markdown("**Positive signals**")
            for item in question.positive_signals:
                st.write(f"- {item}")
            st.markdown("**Warning signals**")
            for item in question.warning_signals:
                st.write(f"- {item}")
            st.markdown("**Follow-up probes**")
            for item in question.follow_ups:
                st.write(f"- {item}")


def render_interview_intelligence():
    import streamlit as st

    apply_enterprise_theme()
    session = get_streamlit_session()

    enterprise_hero(
        "Interview Intelligence",
        "Prepare a focused, evidence-based interview from the active recruitment session.",
        "Performance Hotfix 3.1.1B",
    )

    if session is None or not getattr(session, "ranked_analyses", None):
        st.info("Create or load a recruitment session before preparing an interview strategy.")
        return

    with st.spinner("Preparing the interview context…"):
        reports = InterviewWorkspaceService().build_all(session)

    if not reports:
        st.info("No candidate analysis is available for interview preparation.")
        return

    names = [report.candidate_name for report in reports]
    selected_name = st.selectbox("Candidate", names, key="interview_intelligence_candidate")
    report = reports[names.index(selected_name)]

    metric_grid([
        ("Candidate", report.candidate_name, report.role_title),
        ("Official Fit", f"{report.fit_score:.0f}%", "Same score as the recruitment session"),
        ("Evidence Confidence", f"{report.confidence_score}%", "Interview preparation basis"),
        ("Hiring Risk", report.risk_level, report.recommendation),
    ])

    insight_card(
        "Interview focus",
        f"Readiness is {report.readiness.status.lower()} ({report.readiness.score}%). "
        f"Prioritise {len([c for c in report.competencies if c.validate_in_interview])} evidence gaps before the hiring decision.",
        "Evidence-led strategy",
    )

    tab_overview, tab_strategy, tab_scorecard = st.tabs([
        "Overview",
        "Interview Strategy",
        "Scorecard",
    ])

    with tab_overview:
        section_title("Recommended interview plan")
        st.metric("Suggested duration", f"{report.plan.total_minutes} min")
        for section in report.plan.sections:
            st.write(f"**{section.duration_minutes} min · {section.title}** — {section.objective}")

        section_title("Priority evidence gaps")
        priority = [c for c in report.competencies if c.validate_in_interview]
        for competency in priority[:6]:
            st.warning(f"{competency.name}: {competency.rationale}")

    with tab_strategy:
        key = _cache_key(session, report)
        cached_questions = st.session_state.get(key)

        if cached_questions is None:
            st.caption("Questions are generated only when requested and then reused for this candidate and mission.")
            if st.button("Generate Interview Strategy", type="primary", key=f"generate_{key}"):
                st.session_state[key] = report.questions
                cached_questions = report.questions
                st.success("Interview strategy generated and cached.")
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption("Using the cached strategy for this candidate and mission.")
            with col2:
                if st.button("Regenerate", key=f"regenerate_{key}"):
                    st.session_state[key] = report.questions
                    cached_questions = report.questions

        if cached_questions is not None:
            _render_strategy(report, cached_questions)

    with tab_scorecard:
        section_title("Structured scorecard")
        rows = [
            {
                "Competency": item.competency,
                "Suggested score": item.suggested_score,
                "Evaluation guidance": item.evaluation_guidance,
            }
            for item in report.scorecard
        ]
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.metric("Decision readiness", f"{report.decision_readiness}%")
