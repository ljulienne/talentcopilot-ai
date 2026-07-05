import streamlit as st

from talentcopilot.i18n import tr


def _recommendation_color(recommendation: str) -> str:
    recommendation = (recommendation or "").lower()

    if "strong" in recommendation:
        return "#16a34a"
    if "interview" in recommendation:
        return "#2563eb"
    if "pipeline" in recommendation or "maybe" in recommendation:
        return "#d97706"
    return "#dc2626"


def render_decision_header(candidate_decision=None, match_result=None, rank=None):
    """
    Decision Header.

    Preferred input:
    - candidate_decision

    Legacy fallback:
    - match_result + rank
    """

    if candidate_decision:
        recommendation = candidate_decision.recommendation or "Not Available"
        match_score = candidate_decision.match_score
        confidence = candidate_decision.confidence
        rank = candidate_decision.rank
        decision_basis = candidate_decision.decision_basis
        next_action = candidate_decision.next_action or "Proceed according to the hiring recommendation."
    else:
        recommendation = getattr(match_result, "recommendation", "Not Available")
        match_score = getattr(match_result, "overall_score", 0)
        confidence = getattr(match_result, "confidence_score", 0)
        decision_basis = "{tr('decision.match_score')}"
        next_action = "Proceed according to the hiring recommendation."

    color = _recommendation_color(recommendation)

    st.markdown(
        f"""
<div class="tc-card" style="padding:30px;border-radius:14px;">

<h3 style="margin-bottom:10px;">
🧠 {tr('decision.summary')}
</h3>

<div style="
background:{color};
padding:12px;
border-radius:10px;
color:white;
font-size:22px;
font-weight:bold;
text-align:center;
margin-bottom:25px;
">
{recommendation}
</div>

<div style="display:flex;justify-content:space-between;gap:30px;">

<div style="text-align:center;flex:1;">
<div style="font-size:14px;color:#777;">{tr('decision.match_score')}</div>
<div style="font-size:32px;font-weight:bold;">{match_score}%</div>
</div>

<div style="text-align:center;flex:1;">
<div style="font-size:14px;color:#777;">{tr('decision.confidence')}</div>
<div style="font-size:32px;font-weight:bold;">{confidence}%</div>
</div>

<div style="text-align:center;flex:1;">
<div style="font-size:14px;color:#777;">{tr('decision.rank')}</div>
<div style="font-size:32px;font-weight:bold;">#{rank if rank else "-"}</div>
</div>

</div>

<hr style="margin-top:25px;margin-bottom:20px;">

<b>{tr('decision.basis')}</b>
<p style="margin-top:5px;">{decision_basis}</p>

<b>{tr('decision.next_action')}</b>
<p style="margin-top:5px;">{next_action}</p>

</div>
""",
        unsafe_allow_html=True,
    )
