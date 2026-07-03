import streamlit as st


def executive_summary_card(talent: dict):
    summary = talent.get(
        "executive_summary",
        "No executive summary available yet."
    )

    recommendation = talent.get(
        "recommendation",
        "No recommendation available"
    )

    st.markdown(
        f"""
<div class="tc-card">

<h2>📌 Executive Summary</h2>

<p>{summary}</p>

<hr>

<b>Overall Recommendation</b>

<h3>{recommendation}</h3>

</div>
""",
        unsafe_allow_html=True,
    )
