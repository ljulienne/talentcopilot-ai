
import streamlit as st


def ai_recommendation_card(talent: dict):

    recommendation = talent.get(
        "recommendation",
        "No recommendation"
    )

    confidence = talent.get(
        "average_confidence",
        0
    )

    st.markdown(
        f"""
<div class="tc-card">

<h2>🤖 AI Recommendation</h2>

<h1>{recommendation}</h1>

<h3>Confidence: {confidence}%</h3>

<hr>

<b>Decision Support</b>

<ul>

<li>✔ Talent profile analyzed</li>

<li>✔ Skills evaluated</li>

<li>✔ Recruitment history checked</li>

<li>✔ Financial analysis available</li>

</ul>

</div>
""",
        unsafe_allow_html=True,
    )
