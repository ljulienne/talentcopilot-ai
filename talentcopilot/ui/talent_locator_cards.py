from typing import Any


def render_talent_locator_results(report: Any) -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("Talent Locator")
    st.info(report.summary)

    col1, col2 = st.columns(2)
    col1.metric("Candidates reviewed", report.total_candidates)
    col2.metric("Recommended profiles", report.recommended_count)

    for result in report.results:
        with st.expander(f"{result.candidate_name} — {result.fit.value} ({result.locator_score:.0f}%)"):
            st.write(f"**Role:** {result.role_title}")

            if result.matched_skills:
                st.success("Matched skills: " + ", ".join(result.matched_skills))

            if result.missing_skills:
                st.warning("Missing skills: " + ", ".join(result.missing_skills))

            if result.reasons:
                st.markdown("**Reasons**")
                for reason in result.reasons:
                    st.write(f"- {reason.title}: {reason.explanation}")

            if result.evidence_hints:
                st.markdown("**Evidence hints**")
                for hint in result.evidence_hints:
                    st.caption(hint)


def render_talent_locator_empty_state() -> None:
    try:
        import streamlit as st
    except ImportError:
        return

    st.info("No talent locator results yet. Create a job context and provide a talent pool to start.")
