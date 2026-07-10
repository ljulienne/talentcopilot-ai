import streamlit as st

from talentcopilot.ui.next_shell import apply_next_style, hero, insight_card, recommendation_block


def render_organization_intelligence_preview():
    apply_next_style()

    hero(
        "Organization Intelligence Preview",
        "A first look at the future of TalentCopilot: diagnostics that reveal collaboration risks, invisible silos and organizational blind spots.",
        tag="Preview",
    )

    recommendation_block(
        "AI diagnostic hypothesis",
        "The organization does not only need better recruitment decisions. It needs visibility into how teams, skills and collaboration patterns influence performance.",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        insight_card(
            "Potential silo detected",
            "HR and IT appear structurally dependent, but collaboration is often late in the project lifecycle.",
            "Future signal: project history + org chart + collaboration data.",
        )
    with col2:
        insight_card(
            "Hidden connector",
            "One non-manager profile may act as the operational bridge between business and technical teams.",
            "Future signal: project participation + peer nominations + workflow data.",
        )
    with col3:
        insight_card(
            "Knowledge concentration",
            "Critical process knowledge may be concentrated in a small number of people.",
            "Future signal: role history + skills + process ownership.",
        )

    st.markdown("### Data that could power this diagnostic")
    st.write("For a V1, TalentCopilot should work through uploads rather than employee records.")
    st.markdown(
        """
        - Organization chart export
        - Employee list with department, role and manager
        - Project participation history
        - Skills or competency matrix
        - Engagement or collaboration survey results
        - Optional communication metadata, only if legally and ethically appropriate
        """
    )

    st.warning(
        "This preview is intentionally not a full ONA engine yet. Release 0.1A defines the product experience. Release 0.2 can add the first real analysis engine."
    )
