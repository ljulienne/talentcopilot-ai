from typing import Iterable, List, Tuple


def safe_render(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            try:
                import streamlit as st
                st.warning("This section could not render completely.")
                st.caption(str(exc))
            except Exception:
                return None
    return wrapper


def hero(title: str, subtitle: str, badge: str = "Enterprise AI"):
    import streamlit as st
    st.markdown(
        f"""
        <div class="tc-card">
            <span class="tc-badge">{badge}</span>
            <h1 style="margin-bottom:0.2rem;">{title}</h1>
            <p class="tc-muted">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row(metrics: Iterable[Tuple[str, str]]):
    import streamlit as st
    metrics = list(metrics)
    cols = st.columns(len(metrics) if metrics else 1)
    for col, (label, value) in zip(cols, metrics):
        col.metric(label, value)


def capability_grid(items: Iterable[Tuple[str, str]]):
    import streamlit as st
    cols = st.columns(2)
    for idx, (title, body) in enumerate(items):
        with cols[idx % 2]:
            st.markdown(
                f"""
                <div class="tc-card">
                    <h4>{title}</h4>
                    <p class="tc-muted">{body}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def workflow_steps(steps: List[str]):
    import streamlit as st
    for idx, step in enumerate(steps, start=1):
        st.write(f"**{idx}. {step}**")


def context_panel():
    import streamlit as st
    context = st.session_state.get("recruitment_context", None)
    if context:
        st.success("Active recruitment context detected.")
        st.write(context)
    else:
        st.info("No active recruitment context yet. Start with New Recruitment or use demo data.")
