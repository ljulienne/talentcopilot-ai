import streamlit as st


def evidence_card(
    text: str,
    interpretation: str = "",
    strength: str = "unknown",
    confidence_score: float | None = None,
) -> None:
    strength_label = strength.title()

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**📎 {strength_label} evidence**")

        with col2:
            if confidence_score is not None:
                st.metric("Confidence", f"{int(confidence_score * 100)}%")

        st.write(f"“{text}”")

        if interpretation:
            st.info(interpretation)
