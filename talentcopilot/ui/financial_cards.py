
import streamlit as st


def financial_card(talent: dict):

    financial = talent.get("financial_data", {}) or {}

    st.markdown(
        """
<div class="tc-card">

<h2>💰 Financial Intelligence</h2>

</div>
""",
        unsafe_allow_html=True,
    )

    if not financial:
        st.info("No financial information available.")
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Expected Salary",
            financial.get("expected_salary", "-"),
        )

    with col2:
        st.metric(
            "Budget Max",
            financial.get("budget_max", "-"),
        )

    with col3:
        expected = financial.get("expected_salary")
        budget = financial.get("budget_max")

        if (
            isinstance(expected, (int, float))
            and isinstance(budget, (int, float))
        ):
            if expected <= budget:
                st.success("🟢 Within Budget")
            else:
                st.error("🔴 Above Budget")
        else:
            st.info("Budget Unknown")
