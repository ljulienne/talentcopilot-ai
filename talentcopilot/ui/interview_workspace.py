from talentcopilot.interview.evaluation_models import InterviewRating
from talentcopilot.interview.post_interview_evaluation_service import PostInterviewEvaluationService
from talentcopilot.interview.workspace_service import InterviewWorkspaceService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _competency_matrix(report):
    import streamlit as st

    rows = [
        {
            "Competency": c.name,
            "Evidence": c.evidence_level,
            "Confidence": c.confidence,
            "Validate in Interview": "Yes" if c.validate_in_interview else "No",
            "Rationale": c.rationale,
        }
        for c in report.competencies
    ]
    st.dataframe(rows, use_container_width=True)


def _interview_plan(report):
    import streamlit as st

    st.metric("Total interview time", f"{report.plan.total_minutes} min")
    for section in report.plan.sections:
        with st.expander(f"{section.duration_minutes} min · {section.title}"):
            st.write(section.objective)


def _questions(report):
    import streamlit as st

    for question in report.questions:
        with st.expander(f"{question.competency} · {question.question}"):
            st.write(f"**Objective:** {question.objective}")
            st.write("**Expected evidence**")
            for item in question.expected_evidence:
                st.write(f"- {item}")
            st.write("**Positive signals**")
            for item in question.positive_signals:
                st.write(f"- {item}")
            st.write("**Warning signals**")
            for item in question.warning_signals:
                st.write(f"- {item}")
            st.write("**Follow-up questions**")
            for item in question.follow_ups:
                st.write(f"- {item}")


def _scorecard(report):
    import streamlit as st

    rows = [
        {
            "Competency": item.competency,
            "Suggested Score": item.suggested_score,
            "Guidance": item.evaluation_guidance,
        }
        for item in report.scorecard
    ]
    st.dataframe(rows, use_container_width=True)


def _live_notes(report):
    import streamlit as st

    st.text_area(
        "Live interview notes",
        placeholder="Capture candidate answers, evidence confirmed, risks and follow-up items...",
        height=180,
        key=f"interview_notes_{report.candidate_name}",
    )
    st.caption("In Release 2.0, notes will feed the Decision Intelligence Core.")


def _evaluation(report):
    import streamlit as st

    service = PostInterviewEvaluationService()
    default_ratings = service.build_default_ratings(report)

    ratings = []
    for rating in default_ratings:
        with st.expander(f"Evaluate {rating.competency}", expanded=False):
            score = st.slider(
                f"Score — {rating.competency}",
                min_value=1,
                max_value=5,
                value=rating.score,
                key=f"score_{report.candidate_name}_{rating.competency}",
            )
            confirmed = st.checkbox(
                f"Evidence confirmed — {rating.competency}",
                value=rating.evidence_confirmed,
                key=f"confirmed_{report.candidate_name}_{rating.competency}",
            )
            notes = st.text_area(
                f"Notes — {rating.competency}",
                value=rating.notes,
                key=f"eval_notes_{report.candidate_name}_{rating.competency}",
            )
            ratings.append(
                InterviewRating(
                    competency=rating.competency,
                    score=score,
                    evidence_confirmed=confirmed,
                    notes=notes,
                )
            )

    summary = service.evaluate(report.candidate_name, ratings)

    metric_grid([
        ("Overall Interview", f"{summary.overall_score}/5", summary.decision_impact),
        ("Recommendation", summary.recommendation_after_interview, "Post interview"),
        ("Strengths", str(len(summary.strengths_confirmed)), "Confirmed"),
        ("Risks", str(len(summary.risks_remaining)), "Remaining"),
    ])

    section_title("Strengths confirmed")
    if summary.strengths_confirmed:
        for item in summary.strengths_confirmed:
            st.success(item)
    else:
        st.info("No strengths confirmed yet.")

    section_title("Risks remaining")
    if summary.risks_remaining:
        for item in summary.risks_remaining:
            st.warning(item)
    else:
        st.success("No major remaining risk.")

    markdown = service.to_markdown(summary)
    st.download_button(
        "Download interview evaluation",
        data=markdown,
        file_name=f"interview_evaluation_{report.candidate_name.replace(' ', '_').lower()}.md",
        mime="text/markdown",
    )


def render_interview_workspace():
    import streamlit as st

    apply_enterprise_theme()

    session = get_streamlit_session()
    reports = InterviewWorkspaceService().build_all(session)

    enterprise_hero(
        "Interview Workspace",
        "Prepare and evaluate structured, evidence-based interviews.",
        "Interview Intelligence",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            reports = InterviewWorkspaceService().build_all(session)
            st.success("Enterprise demo loaded.")
    with col2:
        st.caption("Use this workspace to prepare, run and evaluate candidate interviews.")

    if not reports:
        st.info("No interview workspace available yet. Load the Enterprise Demo or create a recruitment session.")
        return

    candidate_names = [report.candidate_name for report in reports]
    selected_name = st.selectbox("Select candidate", candidate_names)
    report = reports[candidate_names.index(selected_name)]

    metric_grid([
        ("Candidate", report.candidate_name, report.role_title),
        ("Fit", f"{report.fit_score:.0f}%", "Current analysis"),
        ("Confidence", f"{report.confidence_score}%", "Interview basis"),
        ("Recommendation", report.recommendation, report.risk_level),
    ])

    insight_card(
        "Interview Readiness",
        f"{report.readiness.status}. Readiness score: {report.readiness.score}%. Decision readiness after scorecard: {report.decision_readiness}%.",
        "Interview Intelligence",
    )

    tab_readiness, tab_matrix, tab_plan, tab_questions, tab_notes, tab_scorecard, tab_evaluation = st.tabs([
        "Readiness",
        "Competency Matrix",
        "Interview Plan",
        "AI Questions",
        "Live Notes",
        "Scorecard",
        "Evaluation",
    ])

    with tab_readiness:
        section_title("Readiness Drivers")
        st.progress(max(0, min(100, report.readiness.score)) / 100)
        for driver in report.readiness.drivers:
            st.success(driver)
        section_title("Gaps to Validate")
        if report.readiness.gaps:
            for gap in report.readiness.gaps:
                st.warning(gap)
        else:
            st.success("No major gap detected before interview.")

    with tab_matrix:
        section_title("Competency Validation Matrix")
        _competency_matrix(report)

    with tab_plan:
        section_title("Interview Plan")
        _interview_plan(report)

    with tab_questions:
        section_title("AI Interview Questions")
        _questions(report)

    with tab_notes:
        section_title("Live Notes")
        _live_notes(report)

    with tab_scorecard:
        section_title("Interview Scorecard")
        _scorecard(report)
        st.metric("Decision Readiness", f"{report.decision_readiness}%")

    with tab_evaluation:
        section_title("Post-Interview Evaluation")
        _evaluation(report)
