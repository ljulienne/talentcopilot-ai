import streamlit as st


def render_decision_actions() -> None:
    st.subheader("Actions")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.button("Compare", disabled=True)

    with col2:
        st.button("Generate PDF", disabled=True)

    with col3:
        st.button("Ask Copilot", disabled=True)

    with col4:
        st.button("Save to Talent Pool", disabled=True)

    st.caption("Actions are shown as the target workflow and will be activated progressively.")
