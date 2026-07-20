from __future__ import annotations

from talentcopilot.interview.pro_service import InterviewIntelligenceProService
from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.interview.workspace_service import InterviewWorkspaceService
from talentcopilot.services.interview_report_pdf_service import InterviewReportPdfService
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


CACHE_PREFIX = "interview_strategy_"
OUTCOME_PREFIX = "interview_outcome_"


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

    section_title("Targeted interview playbook")
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


def _render_live_evaluation(session, report):
    import streamlit as st

    service = InterviewIntelligenceProService()
    candidate_key = f"{getattr(session, 'session_id', 'session')}:{report.candidate_name}"
    outcome_key = f"{OUTCOME_PREFIX}{candidate_key}"

    section_title("Live interview evidence")
    st.caption(
        "Capture recruiter observations and candidate evidence. This evaluation does not alter "
        "the official matching score, official rank, or AI confidence."
    )

    ratings = []
    for index, competency in enumerate(report.competencies[:7]):
        safe_key = f"{candidate_key}:{index}"
        with st.expander(competency.name, expanded=index == 0):
            answer = st.text_area(
                "Candidate answer / evidence",
                key=f"answer:{safe_key}",
                height=130,
                placeholder="Capture the context, personal responsibility, actions, results and measurable evidence…",
            )
            col1, col2 = st.columns(2)
            with col1:
                recruiter_score = st.slider(
                    "Recruiter rating",
                    min_value=1,
                    max_value=5,
                    value=3,
                    key=f"rating:{safe_key}",
                )
            with col2:
                confirmed = st.checkbox(
                    "Evidence confirmed",
                    key=f"confirmed:{safe_key}",
                )
            notes = st.text_input(
                "Recruiter notes",
                key=f"notes:{safe_key}",
                placeholder="Optional decision-relevant note",
            )

            star = service.assess_star(answer)
            st.progress(star.completeness_score / 100, text=f"STAR evidence completeness: {star.completeness_score}%")
            if answer:
                st.caption(star.evidence_summary)
                follow_ups = service.suggest_follow_ups(star, competency.name)
                if follow_ups:
                    st.markdown("**Suggested follow-up questions**")
                    for prompt in follow_ups:
                        st.write(f"- {prompt}")
                else:
                    st.success("The answer covers the expected STAR and evidence dimensions.")

            ratings.append(
                service.build_rating(
                    competency=competency.name,
                    answer=answer,
                    recruiter_score=recruiter_score,
                    evidence_confirmed=confirmed,
                    notes=notes or answer,
                )
            )

    if st.button("Generate post-interview recommendation", type="primary", key=f"evaluate:{candidate_key}"):
        st.session_state[outcome_key] = service.evaluate(report.candidate_name, ratings)

    outcome = st.session_state.get(outcome_key)
    if outcome is None:
        return

    section_title("Post-interview decision support")
    metric_grid([
        ("Recommendation", outcome.recommendation.label, "Based only on captured interview evidence"),
        ("Interview score", f"{outcome.overall_score:.2f}/5", "Recruiter scorecard average"),
        ("Evidence coverage", f"{outcome.evidence_coverage}%", "Competencies explicitly confirmed"),
        ("Recommendation confidence", f"{outcome.recommendation.confidence}%", "Evidence and STAR completeness"),
    ])

    insight_card(
        "Executive interview summary",
        service.build_executive_summary(outcome),
        "Explainable recommendation",
    )

    st.markdown("**Decision rationale**")
    for item in outcome.recommendation.rationale:
        st.write(f"- {item}")

    st.markdown("**Remaining risks and missing evidence**")
    if outcome.recommendation.remaining_risks:
        for item in outcome.recommendation.remaining_risks:
            st.warning(item)
    else:
        st.success("No material interview evidence gap remains.")

    st.info(f"Recommended next step: {outcome.recommendation.next_step}")

    pdf = InterviewReportPdfService().build(outcome, role_title=report.role_title)
    st.download_button(
        "Download Interview Intelligence Report",
        data=pdf,
        file_name=f"interview_intelligence_{report.candidate_name.replace(' ', '_').lower()}.pdf",
        mime="application/pdf",
        key=f"download:{candidate_key}",
    )


def render_interview_intelligence():
    import streamlit as st

    apply_enterprise_theme()
    session = get_streamlit_session()

    enterprise_hero(
        "Interview Intelligence Pro",
        "Prepare, conduct and evaluate a focused, evidence-based interview from the active recruitment session.",
        "Release 4.7",
    )

    if session is None or not getattr(session, "ranked_analyses", None):
        st.info("Create or load a recruitment session before preparing an interview strategy.")
        return

    with st.spinner("Preparing the interview context…"):
        reports = InterviewWorkspaceService().build_all(session)

    if not reports:
        st.info("No candidate analysis is available for interview preparation.")
        return

    reports = sorted(
        reports,
        key=lambda item: (
            int(getattr(item, "official_rank", 9999) or 9999),
            -float(getattr(item, "fit_score", 0) or 0),
            item.candidate_name.casefold(),
            str(getattr(item, "candidate_id", "")),
        ),
    )
    reports_by_id = {
        str(getattr(report, "candidate_id", "") or report.candidate_name): report
        for report in reports
    }
    option_ids = list(reports_by_id)
    selection_key = "interview_intelligence_candidate_id"
    context_key = "interview_intelligence_candidate_context"
    context = (
        str(getattr(session, "session_id", "session")),
        tuple(option_ids),
    )
    if st.session_state.get(context_key) != context:
        st.session_state[context_key] = context
        st.session_state[selection_key] = option_ids[0]

    selected_id = st.selectbox(
        "Candidate",
        option_ids,
        key=selection_key,
        format_func=lambda candidate_id: (
            f"#{reports_by_id[candidate_id].official_rank} "
            f"{reports_by_id[candidate_id].candidate_name}"
        ),
    )
    report = reports_by_id[selected_id]

    metric_grid([
        ("Candidate", report.candidate_name, f"Official rank #{report.official_rank} · {report.role_title}"),
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

    tab_overview, tab_strategy, tab_live, tab_scorecard = st.tabs([
        "Overview",
        "Interview Playbook",
        "Live Evaluation",
        "Preparation Scorecard",
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
            if st.button("Generate Interview Playbook", type="primary", key=f"generate_{key}"):
                st.session_state[key] = report.questions
                cached_questions = report.questions
                st.success("Interview playbook generated and cached.")
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption("Using the cached playbook for this candidate and mission.")
            with col2:
                if st.button("Regenerate", key=f"regenerate_{key}"):
                    st.session_state[key] = report.questions
                    cached_questions = report.questions

        if cached_questions is not None:
            _render_strategy(report, cached_questions)

    with tab_live:
        _render_live_evaluation(session, report)

    with tab_scorecard:
        section_title("Pre-interview scorecard")
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
        st.caption("This preparation scorecard is not a post-interview hiring decision.")
