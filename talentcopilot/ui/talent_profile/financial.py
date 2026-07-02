import streamlit as st

from talentcopilot.finance.financial_analyzer import (
    analyze_candidate_financial_fit,
    generate_financial_summary,
)
from talentcopilot.talent_pool.talent_store import update_talent_financial_data
from talentcopilot.ui.components import metric_card, section_title


def render_financial(talent):
    section_title(
        "Financial Intelligence",
        "Assess salary expectations against the recruitment budget.",
    )

    candidate_key = talent.get("candidate_key", "unknown")
    name = talent.get("name", "Unknown Candidate")
    financial_data = talent.get("financial_data", {})

    with st.expander("Budget & Salary Simulation", expanded=True):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            budget_min = st.number_input(
                "Budget min",
                min_value=0,
                value=int(financial_data.get("budget_min", 70000)),
                step=1000,
                key=f"budget_min_{candidate_key}",
            )

        with col2:
            budget_max = st.number_input(
                "Budget max",
                min_value=0,
                value=int(financial_data.get("budget_max", 85000)),
                step=1000,
                key=f"budget_max_{candidate_key}",
            )

        with col3:
            expected_salary = st.number_input(
                "Expected salary",
                min_value=0,
                value=int(financial_data.get("expected_salary", 82000)),
                step=1000,
                key=f"expected_salary_{candidate_key}",
            )

        with col4:
            currency_options = ["EUR", "USD", "XPF", "GBP", "CNY"]
            default_currency = financial_data.get("currency", "EUR")
            default_index = currency_options.index(default_currency) if default_currency in currency_options else 0

            currency = st.selectbox(
                "Currency",
                currency_options,
                index=default_index,
                key=f"currency_{candidate_key}",
            )

        if st.button("💾 Save Financial Data", key=f"save_financial_{candidate_key}", use_container_width=True):
            update_talent_financial_data(
                candidate_key,
                {
                    "budget_min": budget_min,
                    "budget_max": budget_max,
                    "expected_salary": expected_salary,
                    "currency": currency,
                },
            )
            st.success("Financial data saved.")

        analysis = analyze_candidate_financial_fit(
            candidate_name=name,
            expected_salary=expected_salary,
            budget_min=budget_min,
            budget_max=budget_max,
            currency=currency,
        )

        col_a, col_b, col_c = st.columns(3)

        with col_a:
            metric_card("Budget Fit", f"{analysis.get('budget_fit_score', 0)}%", "Salary vs budget")

        with col_b:
            metric_card(
                "Salary Gap",
                f"{analysis.get('salary_gap', 0):,.0f} {currency}",
                "Expected salary minus max budget",
            )

        with col_c:
            metric_card("Verdict", analysis.get("verdict", "-"), "Financial recommendation")

        st.progress(min(analysis.get("budget_fit_score", 0), 100) / 100)
        st.write(generate_financial_summary(analysis))
