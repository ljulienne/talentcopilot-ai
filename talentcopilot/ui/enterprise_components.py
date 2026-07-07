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


def get_active_session():
    try:
        from talentcopilot.services.session_store import SessionStore
        return SessionStore.get_current_session()
    except Exception:
        return None


def context_panel():
    import streamlit as st
    session = get_active_session()
    if session:
        st.success("Active recruitment session detected.")
        c1, c2, c3 = st.columns(3)
        c1.metric("Role", session.role_title)
        c2.metric("Candidates", session.candidate_count)
        c3.metric("Analyzed", session.analyzed_count)
        st.caption(f"Session ID: {session.session_id}")
    else:
        st.info("No active recruitment session yet. Launch the demo session from Home.")


def ranked_candidate_table(session):
    import streamlit as st
    if not session or not getattr(session, "analyses", None):
        st.info("No analyzed candidates available yet.")
        return
    rows = []
    for analysis in session.ranked_analyses:
        decision = getattr(analysis, "decision_report", None)
        recommendation = "—"
        if decision is not None:
            recommendation = getattr(getattr(decision, "recommendation", "—"), "value", getattr(decision, "recommendation", "—"))
        rows.append({
            "Rank": analysis.rank,
            "Candidate": analysis.candidate_name,
            "Match": analysis.match_score,
            "Status": analysis.status.value,
            "Decision": recommendation,
        })
    st.dataframe(rows, use_container_width=True)
