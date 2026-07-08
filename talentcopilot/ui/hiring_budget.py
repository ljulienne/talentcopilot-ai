from talentcopilot.models.hiring_budget import HiringBudgetInput
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.hiring_budget_service import HiringBudgetService
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _assessment_table(report):
    import streamlit as st

    rows = [
        {
            "Candidate": a.candidate_name,
            "Fit Score": a.fit_score,
            "Expected Salary": round(a.expected_salary, 0),
            "Salary Gap": round(a.salary_gap, 0),
            "Budget Fit": a.budget_fit,
            "Cost Impact": a.cost_impact,
            "Feasibility": a.feasibility,
            "Recommendation": a.recommendation,
        }
        for a in report.assessments
    ]

    if rows:
        st.dataframe(rows, use_container_width=True)
    else:
        st.info("No budget assessment available yet.")


def render_hiring_budget():
    import streamlit as st

    apply_enterprise_theme()

    service = HiringBudgetService()
    session = get_streamlit_session()

    enterprise_hero(
        "Hiring Budget",
        "Separate candidate fit from financial feasibility and compensation risk.",
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

    best = report.assessments[0] if report.assessments else None

    metric_grid([
        ("Target Salary", f"{report.target_salary:,.0f}", "Budget"),
        ("Max Salary", f"{report.maximum_salary:,.0f}", "Ceiling"),
        ("Candidates", str(len(report.assessments)), "Assessed"),
        ("Top Budget Fit", f"{best.budget_fit}%" if best else "-", best.recommendation if best else "-"),
    ])

    insight_card(
        "Budget principle",
        "Budget Fit does not modify Candidate Fit. A strong candidate can be recommended for compensation review instead of being incorrectly rejected.",
        "Decision Rule",
    )

    tab_assessments, tab_details, tab_actions = st.tabs([
        "Assessments",
        "Candidate Details",
        "Actions",
    ])

    with tab_assessments:
        section_title("Budget Assessments")
        _assessment_table(report)

    with tab_details:
        if not report.assessments:
            st.info("No candidate details available.")
        else:
            names = [a.candidate_name for a in report.assessments]
            selected = st.selectbox("Select candidate", names)
            a = report.assessments[names.index(selected)]
            metric_grid([
                ("Fit Score", f"{a.fit_score:.0f}%", "Candidate fit"),
                ("Budget Fit", f"{a.budget_fit}%", "Financial fit"),
                ("Salary Gap", f"{a.salary_gap:,.0f}", "Vs max budget"),
                ("Feasibility", a.feasibility, a.cost_impact),
            ])
            st.info(a.rationale)

    with tab_actions:
        if not report.assessments:
            st.info("No actions available.")
        else:
            for a in report.assessments:
                with st.expander(f"{a.candidate_name} · {a.recommendation}"):
                    st.write(a.rationale)
                    for action in a.next_actions:
                        st.write(f"- {action}")
