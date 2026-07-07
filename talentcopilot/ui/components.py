def footer(*args, **kwargs):
    try:
        import streamlit as st
        st.markdown("---")
        st.caption("TalentCopilot-AI · Explainable recruitment intelligence")
    except Exception:
        return


def page_header(title, subtitle=None):
    try:
        import streamlit as st
        st.title(title)
        if subtitle:
            st.caption(subtitle)
    except Exception:
        return


def info_card(title, body):
    try:
        import streamlit as st
        st.markdown(
            f"""
            <div class="tc-card">
              <h4>{title}</h4>
              <p class="tc-muted">{body}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    except Exception:
        return
