from __future__ import annotations

from dataclasses import replace

from talentcopilot.models.hiring_budget import HiringBudgetInput
from talentcopilot.services.compensation_budget_service import (
    CandidateCompensationExpectation,
    CompensationBudgetService,
)
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.hiring_budget_service import HiringBudgetService
from talentcopilot.services.recruitment_pdf_service import RecruitmentPdfService
from talentcopilot.services.recruitment_workflow_state import select_workflow_candidate
from talentcopilot.services.streamlit_session_bridge import (
    get_streamlit_session,
    set_streamlit_session,
)
from talentcopilot.ui.design_system.components import (
    page_header,
    insight_card,
    metric_grid,
    section_title,
)
from talentcopilot.ui.design_system.theme import apply_enterprise_theme
from talentcopilot.ui.navigation_actions import request_page


def _money(value, currency="EUR"):
    return "—" if value is None else f"{currency} {float(value):,.0f}"


def _percent(value):
    return "—" if value is None else f"{value}%"


def _candidate_options(session):
    values = []
    for analysis in list(getattr(session, "ranked_analyses", []) or []):
        candidate_id = str(getattr(analysis, "candidate_id", "") or getattr(analysis, "candidate_name", ""))
        candidate_name = str(getattr(analysis, "candidate_name", "Candidate") or "Candidate")
        values.append((candidate_id, candidate_name))
    return values


def _assessment_table(report):
    import streamlit as st

    rows = [
        {
            "Candidate": assessment.candidate_name,
            "Talent Fit": f"{assessment.fit_score:.0f}%",
            "Talent Recommendation": assessment.talent_recommendation,
            "Expected Salary": _money(assessment.expected_salary, assessment.currency),
            "Requested Package": _money(assessment.requested_package, assessment.currency),
            "Compensation Fit": _percent(assessment.budget_fit),
            "Budget Decision": assessment.budget_recommendation,
        }
        for assessment in report.assessments
    ]

    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.info("No compensation assessment is available yet.")


def _position_budget_form(session, service: CompensationBudgetService, budget: HiringBudgetInput):
    import streamlit as st

    with st.expander("Edit approved position budget", expanded=not bool(getattr(session, "metadata", {}).get(service.BUDGET_KEY))):
        with st.form("compensation_position_budget_form"):
            currency = st.selectbox(
                "Currency",
                ["EUR", "USD", "GBP", "AUD", "XPF", "CNY", "SGD"],
                index=["EUR", "USD", "GBP", "AUD", "XPF", "CNY", "SGD"].index(budget.currency)
                if budget.currency in ["EUR", "USD", "GBP", "AUD", "XPF", "CNY", "SGD"]
                else 0,
            )
            min_col, target_col, max_col = st.columns(3)
            minimum_salary = min_col.number_input(
                "Minimum base salary",
                min_value=0.0,
                value=float(budget.minimum_salary),
                step=1000.0,
            )
            target_salary = target_col.number_input(
                "Target base salary",
                min_value=0.0,
                value=float(budget.target_salary),
                step=1000.0,
            )
            maximum_salary = max_col.number_input(
                "Maximum base salary",
                min_value=0.0,
                value=float(budget.maximum_salary),
                step=1000.0,
            )
            bonus_col, benefits_col, first_year_col = st.columns(3)
            target_bonus_percent = bonus_col.number_input(
                "Target bonus (%)",
                min_value=0.0,
                value=float(budget.target_bonus_percent),
                step=1.0,
            )
            benefits_budget = benefits_col.number_input(
                "Benefits budget",
                min_value=0.0,
                value=float(budget.benefits_budget),
                step=1000.0,
            )
            first_year_cost_limit = first_year_col.number_input(
                "Maximum first-year cost",
                min_value=0.0,
                value=float(budget.first_year_cost_limit),
                step=1000.0,
            )
            relocation_col, signing_col, agency_col, onboarding_col = st.columns(4)
            relocation_budget = relocation_col.number_input(
                "Relocation budget", min_value=0.0, value=float(budget.relocation_budget), step=1000.0
            )
            signing_bonus = signing_col.number_input(
                "Signing bonus", min_value=0.0, value=float(budget.signing_bonus), step=1000.0
            )
            agency_fee = agency_col.number_input(
                "Agency fee", min_value=0.0, value=float(budget.agency_fee), step=1000.0
            )
            onboarding_cost = onboarding_col.number_input(
                "Onboarding cost", min_value=0.0, value=float(budget.onboarding_cost), step=1000.0
            )
            notes = st.text_area(
                "Budget notes and approval constraints",
                value=budget.notes,
                placeholder="Approval owner, flexibility, market reference, exceptional conditions…",
            )
            saved = st.form_submit_button("Save position budget", type="primary", use_container_width=True)

        if saved:
            if minimum_salary and target_salary and minimum_salary > target_salary:
                st.error("Minimum salary cannot exceed the target salary.")
            elif target_salary > maximum_salary:
                st.error("Target salary cannot exceed the maximum salary.")
            else:
                updated = HiringBudgetInput(
                    target_salary=target_salary,
                    maximum_salary=maximum_salary,
                    minimum_salary=minimum_salary,
                    currency=currency,
                    target_bonus_percent=target_bonus_percent,
                    benefits_budget=benefits_budget,
                    relocation_budget=relocation_budget,
                    agency_fee=agency_fee,
                    signing_bonus=signing_bonus,
                    onboarding_cost=onboarding_cost,
                    first_year_cost_limit=first_year_cost_limit,
                    notes=notes,
                )
                service.save_budget(session, updated)
                set_streamlit_session(session)
                st.success("Approved position budget saved.")
                st.rerun()


def _candidate_expectation_form(session, service: CompensationBudgetService, candidate_id: str, candidate_name: str):
    import streamlit as st

    expectation = service.load_expectation(
        session,
        candidate_id=candidate_id,
        candidate_name=candidate_name,
    )
    with st.expander(f"Record expectations · {candidate_name}", expanded=not expectation.documented):
        with st.form(f"candidate_compensation_form_{candidate_id}"):
            currency = st.selectbox(
                "Candidate currency",
                ["EUR", "USD", "GBP", "AUD", "XPF", "CNY", "SGD"],
                index=["EUR", "USD", "GBP", "AUD", "XPF", "CNY", "SGD"].index(expectation.currency)
                if expectation.currency in ["EUR", "USD", "GBP", "AUD", "XPF", "CNY", "SGD"]
                else 0,
                key=f"candidate_currency_{candidate_id}",
            )
            salary_col, variable_col, benefits_value_col = st.columns(3)
            expected_salary = salary_col.number_input(
                "Requested base salary",
                min_value=0.0,
                value=float(expectation.expected_salary),
                step=1000.0,
                key=f"expected_salary_{candidate_id}",
            )
            variable_compensation = variable_col.number_input(
                "Requested variable / bonus",
                min_value=0.0,
                value=float(expectation.variable_compensation),
                step=1000.0,
                key=f"variable_compensation_{candidate_id}",
            )
            benefits_value = benefits_value_col.number_input(
                "Estimated benefits value",
                min_value=0.0,
                value=float(expectation.benefits_value),
                step=500.0,
                key=f"benefits_value_{candidate_id}",
            )
            benefits_requested = st.text_input(
                "Benefits requested",
                value=expectation.benefits_requested,
                key=f"benefits_requested_{candidate_id}",
                placeholder="Remote work, health insurance, vehicle, housing, leave…",
            )
            relocation_col, signing_col, notice_col = st.columns(3)
            relocation_support_requested = relocation_col.number_input(
                "Relocation support requested",
                min_value=0.0,
                value=float(expectation.relocation_support_requested),
                step=1000.0,
                key=f"relocation_requested_{candidate_id}",
            )
            signing_bonus_requested = signing_col.number_input(
                "Signing bonus requested",
                min_value=0.0,
                value=float(expectation.signing_bonus_requested),
                step=1000.0,
                key=f"signing_requested_{candidate_id}",
            )
            notice_period_weeks = notice_col.number_input(
                "Notice period (weeks)",
                min_value=0,
                value=int(expectation.notice_period_weeks),
                step=1,
                key=f"notice_weeks_{candidate_id}",
            )
            availability_col, flexibility_col = st.columns(2)
            availability_date = availability_col.text_input(
                "Availability date",
                value=expectation.availability_date,
                key=f"availability_{candidate_id}",
                placeholder="YYYY-MM-DD or candidate wording",
            )
            flexibility_options = ["Unknown", "Low", "Moderate", "High"]
            flexibility = flexibility_col.selectbox(
                "Negotiation flexibility",
                flexibility_options,
                index=flexibility_options.index(expectation.flexibility)
                if expectation.flexibility in flexibility_options
                else 0,
                key=f"flexibility_{candidate_id}",
            )
            visa_sponsorship_required = st.checkbox(
                "Visa sponsorship required",
                value=expectation.visa_sponsorship_required,
                key=f"visa_required_{candidate_id}",
            )
            notes = st.text_area(
                "Recruiter notes",
                value=expectation.notes,
                key=f"compensation_notes_{candidate_id}",
                placeholder="Source, date, negotiation signals and conditions…",
            )
            saved = st.form_submit_button("Save candidate expectations", type="primary", use_container_width=True)

        if saved:
            saved_expectation = CandidateCompensationExpectation(
                candidate_id=candidate_id,
                candidate_name=candidate_name,
                currency=currency,
                expected_salary=expected_salary,
                variable_compensation=variable_compensation,
                benefits_value=benefits_value,
                benefits_requested=benefits_requested,
                relocation_support_requested=relocation_support_requested,
                signing_bonus_requested=signing_bonus_requested,
                notice_period_weeks=int(notice_period_weeks),
                availability_date=availability_date,
                visa_sponsorship_required=visa_sponsorship_required,
                flexibility=flexibility,
                notes=notes,
            )
            service.save_expectation(session, saved_expectation)
            set_streamlit_session(session)
            select_workflow_candidate(candidate_id, candidate_name)
            st.success(f"Compensation expectations saved for {candidate_name}.")
            st.rerun()


def _offer_scenarios(service, budget, expectation):
    import streamlit as st

    scenarios = service.offer_scenarios(budget, expectation)
    rows = [
        {
            "Scenario": item.label,
            "Base salary": _money(item.base_salary, budget.currency),
            "Variable": _money(item.variable_compensation, budget.currency),
            "Benefits": _money(item.benefits_value, budget.currency),
            "Signing": _money(item.signing_bonus, budget.currency),
            "Relocation": _money(item.relocation_support, budget.currency),
            "First-year cost": _money(item.first_year_cost, budget.currency),
            "Budget position": item.position,
        }
        for item in scenarios
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)
    for item in scenarios:
        with st.expander(f"{item.label} · {item.position}"):
            st.write(item.rationale)


def render_hiring_budget():
    import streamlit as st

    apply_enterprise_theme()

    compensation_service = CompensationBudgetService()
    budget_service = HiringBudgetService()
    session = get_streamlit_session()

    page_header(
        "Compensation & Budget",
        "Define the approved position package, record candidate expectations and model offer scenarios without changing Talent Fit.",
        eyebrow="Recruitment · Financial alignment",
        status="Independent signal",
    )

    if session is None:
        st.info("Create or reopen a recruitment mission before defining compensation and budget.")
        if st.button("Load Enterprise Demo", type="primary", key="compensation_load_demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            st.rerun()
        return

    budget = compensation_service.load_budget(session)
    report = budget_service.build(session, budget)
    expectations = compensation_service.all_expectations(session)
    documented = sum(1 for item in expectations if item.documented)
    aligned = sum(1 for item in report.assessments if item.budget_fit is not None and item.budget_fit >= 70)

    export = RecruitmentPdfService().compensation(report, budget, expectations)
    export_col, dashboard_col = st.columns([1, 1])
    with export_col:
        st.download_button(
            "Download compensation report (PDF)",
            data=export.data,
            file_name=export.file_name,
            mime=export.mime,
            key="compensation_download_pdf",
            use_container_width=True,
        )
    with dashboard_col:
        if st.button("Back to Dashboard Perspective", key="compensation_back_dashboard", use_container_width=True):
            request_page("Dashboard Perspective", reason="Returned to the candidate dashboard.")
            st.rerun()

    metric_grid([
        ("Approved salary range", f"{budget.currency} {budget.minimum_salary:,.0f}–{budget.maximum_salary:,.0f}", "Position framework"),
        ("Target package", _money(budget.target_salary, budget.currency), f"{budget.target_bonus_percent:.0f}% target bonus"),
        ("Candidate expectations", f"{documented}/{len(expectations)}", "Documented before or after interview"),
        ("Compensation aligned", str(aligned), "Separate from Talent Fit"),
    ])

    insight_card(
        "Decision principle",
        "Talent Fit and official ranking remain unchanged. Compensation Fit is a separate decision signal used for affordability, negotiation and offer design.",
        "Independent Signal",
    )

    tab_position, tab_candidates, tab_scenarios = st.tabs([
        "Position budget",
        "Candidate expectations",
        "Offer scenarios",
    ])

    with tab_position:
        section_title("Position budget", "Set the approved package before interviews and update it only through an explicit recruiter action.")
        metric_grid([
            ("Minimum", _money(budget.minimum_salary, budget.currency), "Approved floor"),
            ("Target", _money(budget.target_salary, budget.currency), "Preferred base"),
            ("Maximum", _money(budget.maximum_salary, budget.currency), "Approved ceiling"),
            ("First-year limit", _money(budget.first_year_cost_limit, budget.currency), "Salary + package costs"),
        ])
        _position_budget_form(session, compensation_service, budget)

    with tab_candidates:
        section_title("Candidate expectations", "Capture salary, benefits, availability and flexibility whenever the information becomes available.")
        _assessment_table(report)
        options = _candidate_options(session)
        if not options:
            st.info("Analyse candidates before recording expectations.")
        else:
            option_ids = [item[0] for item in options]
            names = {item[0]: item[1] for item in options}
            selected_id = st.selectbox(
                "Candidate",
                option_ids,
                format_func=lambda value: names[value],
                key="compensation_candidate_selector",
            )
            select_workflow_candidate(selected_id, names[selected_id])
            _candidate_expectation_form(session, compensation_service, selected_id, names[selected_id])

    with tab_scenarios:
        section_title("Offer scenarios", "Compare budget-aligned, balanced and candidate-requested packages before the final decision.")
        options = _candidate_options(session)
        if not options:
            st.info("No analysed candidate is available.")
        else:
            option_ids = [item[0] for item in options]
            names = {item[0]: item[1] for item in options}
            scenario_id = st.selectbox(
                "Candidate for scenario modelling",
                option_ids,
                format_func=lambda value: names[value],
                key="compensation_scenario_candidate",
            )
            expectation = compensation_service.load_expectation(
                session,
                candidate_id=scenario_id,
                candidate_name=names[scenario_id],
            )
            if not expectation.documented:
                st.info("Record candidate expectations first. The budget-aligned scenario remains available as a planning baseline.")
            _offer_scenarios(compensation_service, budget, expectation)
