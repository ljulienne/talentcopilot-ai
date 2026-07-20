from talentcopilot.models.hiring_budget import HiringBudgetInput
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.hiring_budget_service import HiringBudgetService
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _money(value):
    return "—" if value is None else f"{value:,.0f}"


def _percent(value):
    return "—" if value is None else f"{value}%"


def _assessment_table(report):
    import streamlit as st

    rows = [
        {
            "Candidate": a.candidate_name,
            "Candidate Fit": f"{a.fit_score:.0f}%",
            "Talent Recommendation": a.talent_recommendation,
            "Compensation Data": a.compensation_data_status,
            "Expected Salary": _money(a.expected_salary),
            "Budget Fit": _percent(a.budget_fit),
            "Budget Decision": a.budget_recommendation,
        }
        for a in report.assessments
    ]

    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No budget assessment available yet.")


def render_hiring_budget():
    import streamlit as st

    apply_enterprise_theme()

    service = HiringBudgetService()
    session = get_streamlit_session()

    enterprise_hero(
        "Hiring Budget",
        "Separate candidate suitability from compensation feasibility without inventing salary data.",
        "Budget Intelligence",
    )

    with st.sidebar.expander("Budget assumptions", expanded=False):
        target_salary = st.number_input("Target salary", min_value=0, value=85000, step=5000)
        maximum_salary = st.number_input("Maximum salary", min_value=0, value=100000, step=5000)
        relocation_budget = st.number_input("Relocation budget", min_value=0, value=8000, step=1000)
        signing_bonus = st.number_input("Signing bonus", min_value=0, value=5000, step=1000)

    budget = HiringBudgetInput(
        target_salary=float(target_salary),
        maximum_salary=float(maximum_salary),
        relocation_budget=float(relocation_budget),
        signing_bonus=float(signing_bonus),
    )

    report = service.build(session, budget)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            report = service.build(session, budget)
            st.success("Enterprise demo loaded.")
    with col2:
        st.caption(f"Active recruitment: {report.role_title}")

    available = [a for a in report.assessments if a.budget_fit is not None]
    top_budget_fit = max((a.budget_fit for a in available), default=None)

    metric_grid([
        ("Target Salary", f"{report.target_salary:,.0f}", "Budget assumption"),
        ("Max Salary", f"{report.maximum_salary:,.0f}", "Approved ceiling"),
        ("Candidates", str(len(report.assessments)), "Talent assessed"),
        ("Budget Assessments", str(len(available)), "With salary data"),
    ])

    insight_card(
        "Decision principle",
        "Talent recommendations come from the active RecruitmentSession. When salary expectations are missing, the budget decision remains pending rather than defaulting every candidate to Review.",
        "Source of Truth",
    )

    if report.assessments and not available:
        st.warning(
            "No candidate salary expectations are available. Candidate fit and official recruitment recommendations remain valid, but budget feasibility cannot yet be assessed."
        )
    elif top_budget_fit is not None:
        st.caption(f"Highest available budget fit: {top_budget_fit}%")

    tab_assessments, tab_details, tab_actions = st.tabs([
        "Assessments",
        "Candidate Details",
        "Actions",
    ])

    with tab_assessments:
        section_title("Talent and Budget Assessments")
        _assessment_table(report)

    with tab_details:
        if not report.assessments:
            st.info("No candidate details available.")
        else:
            names = [a.candidate_name for a in report.assessments]
            selected = st.selectbox("Select candidate", names)
            a = report.assessments[names.index(selected)]
            metric_grid([
                ("Candidate Fit", f"{a.fit_score:.0f}%", "Official match"),
                ("Talent Recommendation", a.talent_recommendation, "Recruitment decision"),
                ("Budget Fit", _percent(a.budget_fit), "Financial fit"),
                ("Budget Decision", a.budget_recommendation, a.compensation_data_status),
            ])
            st.info(a.rationale)

    with tab_actions:
        if not report.assessments:
            st.info("No actions available.")
        else:
            for a in report.assessments:
                with st.expander(
                    f"{a.candidate_name} · {a.talent_recommendation} · {a.budget_recommendation}"
                ):
                    st.write(a.rationale)
                    for action in a.next_actions:
                        st.write(f"- {action}")
