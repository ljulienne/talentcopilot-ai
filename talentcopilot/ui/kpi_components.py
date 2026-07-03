
import streamlit as st


def candidate_kpis(talent: dict):

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "🎯 Talent Score",
            f"{talent.get('talent_score',0)}%"
        )

    with col2:
        st.metric(
            "📈 Average Match",
            f"{talent.get('average_score',0)}%"
        )

    with col3:
        st.metric(
            "🤖 Confidence",
            f"{talent.get('average_confidence',0)}%"
        )

    with col4:
        st.metric(
            "📄 Applications",
            talent.get("application_count",0)
        )
