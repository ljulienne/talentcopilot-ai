from __future__ import annotations

from talentcopilot.executive_copilot import ExecutiveCopilotEngine, QuestionCatalog
from talentcopilot.executive_copilot.context import ExecutiveCopilotContextBuilder
from talentcopilot.executive_copilot.session import history_entry
from talentcopilot.executive_copilot.actions import get_action_plan, remove_action_item
from talentcopilot.organization_intelligence.demo_data import demo_dataframe
from talentcopilot.organization_intelligence.ingestion import dataframe_to_employees, load_uploaded_file
from talentcopilot.ui.executive.response_view import render_copilot_response


def render_executive_copilot_workspace() -> None:
    import streamlit as st

    st.title("Executive Copilot")
    st.caption(
        "Ask decision-oriented HR questions grounded in TalentCopilot's workforce, "
        "skills, knowledge and collaboration evidence."
    )

    source = st.radio(
        "Data source",
        ("Demo organization", "Upload company data"),
        horizontal=True,
        key="executive_copilot_data_source",
    )

    if source == "Demo organization":
        employees = dataframe_to_employees(demo_dataframe())
    else:
        uploaded = st.file_uploader(
            "Upload an employee skills export",
            type=("csv", "xlsx", "xls"),
            key="executive_copilot_upload",
        )
        if uploaded is None:
            st.info("Upload company data to start an executive analysis.")
            return
        employees = load_uploaded_file(uploaded)

    try:
        context = ExecutiveCopilotContextBuilder().build(employees)
    except Exception as exc:
        st.error("The Executive Copilot context could not be generated.")
        st.exception(exc)
        return

    catalog = QuestionCatalog()
    questions = catalog.all()
    labels = {question.title: question.question_id for question in questions}

    pending_question_id = st.session_state.pop(
        "executive_copilot_pending_question_id",
        None,
    )
    if pending_question_id:
        pending_question = catalog.get(str(pending_question_id))
        if pending_question is not None:
            st.session_state["executive_copilot_question_select"] = pending_question.title

    selected_title = st.selectbox(
        "What would you like to understand?",
        tuple(labels),
        key="executive_copilot_question_select",
    )
    question_id = labels[selected_title]

    free_text = st.text_input(
        "Optional: ask the question in your own words",
        placeholder="Example: Which teams need attention this week?",
        key="executive_copilot_free_text",
    )

    generate_requested = st.button(
        "Generate executive answer",
        type="primary",
        use_container_width=True,
        key="executive_copilot_generate",
    )
    auto_generate = bool(
        st.session_state.pop("executive_copilot_auto_generate", False)
    )
    if generate_requested or auto_generate:
        response = ExecutiveCopilotEngine().answer(
            insights=list(context.insights),
            decision_queue=context.decision_queue,
            text=free_text or None,
            question_id=None if free_text else question_id,
        )
        st.session_state["executive_copilot_response"] = response
        history = st.session_state.setdefault("executive_copilot_history", [])
        history.append(history_entry(response))

    response = st.session_state.get("executive_copilot_response")
    if response is None:
        _render_context_summary(context.source_counts, len(context.insights))
        st.info("Choose a question and generate an executive answer.")
        return

    render_copilot_response(response, key_prefix="executive_copilot_workspace")
    _render_action_plan()
    _render_history()


def _render_context_summary(source_counts: dict[str, int], insight_count: int) -> None:
    import streamlit as st

    st.markdown("### Available intelligence")
    cols = st.columns(4)
    cols[0].metric("Insights", insight_count)
    cols[1].metric("Skills", source_counts.get("Skills", 0))
    cols[2].metric("Workforce", source_counts.get("Workforce", 0))
    cols[3].metric(
        "Organization",
        source_counts.get("Knowledge", 0)
        + source_counts.get("Organization Graph", 0)
        + source_counts.get("Collaboration", 0),
    )


def _render_history() -> None:
    import streamlit as st

    history = st.session_state.get("executive_copilot_history", [])
    if not history:
        return

    with st.expander("Session history"):
        for item in reversed(history[-8:]):
            st.markdown(f"**{item.question_title}**")
            st.caption(
                f"Confidence {round(item.confidence * 100)}% · "
                f"{item.created_at.strftime('%H:%M UTC')}"
            )
            st.write(item.summary)


def _render_action_plan() -> None:
    import streamlit as st

    items = get_action_plan()
    if not items:
        return

    with st.expander(f"Session action plan ({len(items)})", expanded=True):
        for index, item in enumerate(items):
            left, right = st.columns((5, 1))
            with left:
                st.markdown(f"**{item.title}**")
                st.caption(
                    f"Impact: {item.impact} · Source: {item.source_question_id}"
                )
            with right:
                if st.button(
                    "Remove",
                    key=f"executive_copilot_remove_action_{index}",
                ):
                    remove_action_item(item.title)
                    st.rerun()
