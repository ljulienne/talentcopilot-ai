from talentcopilot.services.decision_board_service import DecisionBoardService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, next_action_card, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _stakeholder_matrix(candidate):
    import streamlit as st

    rows = [
        {
            "Stakeholder": item.stakeholder,
            "Recommendation": item.recommendation,
            "Confidence": item.confidence,
            "Comment": item.comment,
        }
        for item in candidate.stakeholder_decisions
    ]
    st.dataframe(rows, use_container_width=True)


def _reasons(candidate):
    import streamlit as st

    if not candidate.reasons:
        st.info("No decision reasons available.")
        return

    for reason in candidate.reasons:
        with st.expander(f"{reason.title} · {reason.strength}"):
            st.write(reason.detail)


def _risks(candidate):
    import streamlit as st

    if not candidate.risks:
        st.success("No risk detected.")
        return

    for risk in candidate.risks:
        if risk.severity.lower() == "low":
            st.info(f"**{risk.title}** — {risk.detail}")
        else:
            st.warning(f"**{risk.title}** — {risk.detail}")


def render_decision_board():
    import streamlit as st

    apply_enterprise_theme()

    session = get_streamlit_session()
    report = DecisionBoardService().build(session)

    enterprise_hero(
        "Decision Board",
        "Bring AI, recruiter, hiring manager and HR decision signals into one clear board.",
        "Decision",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            report = DecisionBoardService().build(session)
            st.success("Enterprise demo loaded.")
    with col2:
        st.caption(f"Active recruitment: {report.role_title} · Status: {report.decision_status}")

    if not report.candidates:
        st.info("No decision board available yet. Load the Enterprise Demo or create a recruitment session.")
        return

    candidate_names = [candidate.candidate_name for candidate in report.candidates]
    selected = st.selectbox("Select candidate for decision review", candidate_names)
    candidate = report.candidates[candidate_names.index(selected)]

    metric_grid([
        ("Candidate", candidate.candidate_name, f"Rank #{candidate.rank}"),
        ("Match", f"{candidate.match_score:.0f}%", "AI matching"),
        ("AI Recommendation", candidate.ai_recommendation, "Decision signal"),
        ("Consensus", f"{candidate.consensus_score}%", "Collaborative readiness"),
    ])

    insight_card(
        "Decision recommendation",
        f"{candidate.candidate_name} is currently recommended as: {candidate.ai_recommendation}. Consensus is {candidate.consensus_score}%.",
        "Decision Intelligence",
    )

    tab_matrix, tab_reasons, tab_risks, tab_actions = st.tabs([
        "Stakeholder Matrix",
        "Top Reasons",
        "Risks",
        "Next Actions",
    ])

    with tab_matrix:
        section_title("Stakeholder Decision Matrix")
        _stakeholder_matrix(candidate)

    with tab_reasons:
        section_title("Decision Reasons")
        _reasons(candidate)

    with tab_risks:
        section_title("Decision Risks")
        _risks(candidate)

    with tab_actions:
        section_title("Recommended Next Actions")
        for action in report.next_actions:
            st.write(f"- {action}")
        next_action_card(
            "Complete Hiring Manager review",
            "The decision is not final until the operational assessment is completed.",
            "Continue",
        )
