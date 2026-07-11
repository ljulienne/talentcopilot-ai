from __future__ import annotations

from talentcopilot.executive_copilot.actions import CopilotActionItem, add_action_item
from talentcopilot.executive_copilot.models import CopilotResponse
from talentcopilot.executive_copilot.response_view import build_response_view
from talentcopilot.ui.navigation_actions import page_for_engine, request_page

from .cards import (
    render_confidence_card,
    render_evidence_card,
    render_health_card,
    render_metric_card,
    render_priority_card,
    render_recommendation_card,
)
from .section import render_section
from .theme import apply_executive_theme
from .timeline import TimelineStep, render_timeline


def render_copilot_response(
    response: CopilotResponse,
    *,
    key_prefix: str = "executive_copilot_response",
) -> None:
    """Render a consistent, decision-oriented Executive Copilot response."""
    import streamlit as st

    view = build_response_view(response)
    apply_executive_theme()

    st.caption(f"{view.question_domain} · {view.question_id}")
    st.markdown(f"### {view.question_title}")

    left, middle, right = st.columns(3)
    with left:
        render_health_card(view.executive_health_score, status=view.health_status)
    with middle:
        render_confidence_card(
            view.confidence_percent,
            detail=f"Evidence quality: {view.evidence_quality}",
        )
    with right:
        render_metric_card(
            "Data readiness",
            view.data_readiness,
            detail=f"Engine coverage: {view.coverage_percent}%",
            tone=_readiness_tone(view.data_readiness),
        )

    render_section(
        "Executive summary",
        subtitle="A concise answer based on the available TalentCopilot evidence.",
    )
    render_priority_card(
        view.summary,
        priority=view.priority,
        body=f"Business impact: {view.business_impact}",
    )

    if view.actions:
        render_section(
            "Recommended actions",
            subtitle="Prioritized actions derived from the executive reasoning output.",
        )
        for index, action in enumerate(view.actions[:5]):
            render_recommendation_card(
                action.title,
                impact=action.impact,
                rationale=action.rationale,
            )
            if st.button(
                "Add to session action plan",
                key=f"{key_prefix}_add_action_{index}",
                use_container_width=True,
            ):
                added = add_action_item(
                    CopilotActionItem(
                        title=action.title,
                        impact=action.impact,
                        source_question_id=view.question_id,
                    )
                )
                if added:
                    st.success("Action added to the session plan.")
                else:
                    st.info("This action is already in the session plan.")

    render_section(
        "Evidence",
        subtitle="The most relevant signals supporting this response.",
    )
    if view.evidence:
        for item in view.evidence[:8]:
            render_evidence_card(
                f"{item.title} · {item.source_engine}",
                (
                    item.detail,
                    f"Confidence: {item.confidence_percent}%",
                    f"Severity: {item.severity}",
                ),
            )
    else:
        st.info("No supporting evidence is available for this question yet.")

    if view.trace:
        trace_steps = [
            TimelineStep(
                title=item.source_engine,
                detail=(
                    f"{item.contribution} "
                    f"({item.evidence_count} evidence reference(s))"
                ),
                status="complete" if item.included else "skipped",
            )
            for item in view.trace
        ]
        render_timeline(trace_steps, title="Decision trace")

        included_engines = []
        for item in view.trace:
            if item.included and item.source_engine not in included_engines:
                included_engines.append(item.source_engine)
        if included_engines:
            render_section(
                "Explore source workspaces",
                subtitle="Open the workspace most closely related to each contributing engine.",
            )
            columns = st.columns(min(3, len(included_engines)))
            for index, engine in enumerate(included_engines):
                page_label = page_for_engine(engine)
                with columns[index % len(columns)]:
                    if st.button(
                        f"Open {page_label}",
                        key=f"{key_prefix}_open_{index}_{engine}",
                        use_container_width=True,
                        help=f"Explore evidence contributed by {engine}.",
                    ):
                        request_page(
                            page_label,
                            reason=f"Opened from Executive Copilot · {engine}",
                        )
                        st.rerun()

    if view.missing_data or view.assumptions:
        with st.expander("Data limitations and assumptions"):
            if view.missing_data:
                st.markdown("**Missing data**")
                for item in view.missing_data:
                    st.write(f"- {item}")
            if view.assumptions:
                st.markdown("**Assumptions**")
                for item in view.assumptions:
                    st.write(f"- {item}")

    if view.suggested_questions:
        render_section(
            "Suggested follow-up questions",
            subtitle="Continue the analysis without losing the executive context.",
        )
        for question_id, title in view.suggested_questions:
            if st.button(
                title,
                key=f"{key_prefix}_follow_up_{question_id}",
                use_container_width=True,
            ):
                st.session_state["executive_copilot_pending_question_id"] = question_id
                st.session_state["executive_copilot_auto_generate"] = True
                st.rerun()

    readiness_label = "Decision ready" if view.is_decision_ready else "Review required"
    st.caption(
        f"{readiness_label} · Generated from {view.coverage_percent}% engine coverage."
    )


def _readiness_tone(readiness: str) -> str:
    normalized = readiness.strip().lower()
    if normalized == "high":
        return "success"
    if normalized == "medium":
        return "warning"
    return "danger"
