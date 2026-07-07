from typing import Any


def render_product_readiness(report: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("Product Readiness")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Product", report.product_name)
    col2.metric("Version", report.version)
    col3.metric("Readiness", report.readiness_level.value)
    col4.metric("Score", f"{report.readiness_score:.0f}%")

    st.info(report.summary)

    if report.critical_count:
        st.error(f"{report.critical_count} critical readiness issue(s) detected.")

    with st.expander("Readiness checks"):
        for check in report.checks:
            icon = "✅" if check.passed else "⚠️"
            st.write(f"{icon} **{check.name}** — {check.message}")
            if check.recommendation:
                st.caption(f"Recommendation: {check.recommendation}")
