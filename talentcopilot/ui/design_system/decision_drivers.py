import streamlit as st


def render_decision_drivers(match_details):
    """
    Displays the key decision drivers explaining
    why a candidate received the current Match Score.

    Pure UI component.
    """

    st.subheader("🧠 Decision Drivers")

    if not match_details:
        st.info("No decision drivers available.")
        return

    for detail in match_details:

        competency = detail.requirement.name

        score = detail.score

        explanation = detail.explanation

        if score >= 90:
            stars = "★★★★★"
            color = "#16a34a"

        elif score >= 80:
            stars = "★★★★☆"
            color = "#2563eb"

        elif score >= 70:
            stars = "★★★☆☆"
            color = "#d97706"

        else:
            stars = "★★☆☆☆"
            color = "#dc2626"

        st.markdown(
            f"""
<div style="
background:white;
border:1px solid #e5e7eb;
border-radius:12px;
padding:18px;
margin-bottom:12px;
">

<div style="font-size:20px;font-weight:bold;color:{color};">
{stars}
</div>

<div style="font-size:18px;font-weight:700;margin-top:6px;">
{competency}
</div>

<div style="margin-top:8px;font-size:14px;color:#475569;">
Match Score: <b>{score}%</b>
</div>

<div style="margin-top:8px;color:#475569;">
{explanation}
</div>

</div>
""",
            unsafe_allow_html=True,
        )
