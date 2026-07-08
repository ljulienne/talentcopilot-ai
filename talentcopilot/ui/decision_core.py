from talentcopilot.services.decision_core_demo_service import DecisionCoreDemoService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _engine_status(output):
    import streamlit as st

    rows = [
        {"Engine": key.replace("_", " ").title(), "Status": value}
        for key, value in output.engine_status.items()
    ]
    st.dataframe(rows, use_container_width=True)


def _decision_trace(output):
    import streamlit as st

    steps = output.profile.decision_trace.steps
    for index, step in enumerate(steps, start=1):
        with st.expander(f"{index}. {step.engine} · {step.action}"):
            st.write(step.explanation)
            st.caption(f"Output: {step.output_ref}")


def _metadata_table(output):
    import streamlit as st

    rows = [
        {"Signal": key, "Value": value}
        for key, value in output.profile.metadata.items()
    ]
    st.dataframe(rows, use_container_width=True)


def render_decision_core():
    import streamlit as st

    apply_enterprise_theme()

    service = DecisionCoreDemoService()
    scenarios = service.scenarios()

    enterprise_hero(
        "Decision Core",
        "Run the new Decision Intelligence Core v2 pipeline from Evidence Graph to final recommendation.",
        "Decision Intelligence Core v2",
    )

    selected = st.selectbox("Scenario", [scenario.name for scenario in scenarios])
    scenario = next(item for item in scenarios if item.name == selected)
    st.caption(scenario.description)

    output = service.run(selected)
    profile = output.profile

    metric_grid([
        ("Candidate", profile.candidate_name, profile.role_title),
        ("Fit", f"{profile.fit_score}%", profile.metadata.get("fit_status", "-")),
        ("Risk", profile.risk_level or "-", profile.metadata.get("risk_score", "-")),
        ("Confidence", f"{profile.confidence_score}%", profile.metadata.get("confidence_level", "-")),
    ])

    insight_card(
        "Final Recommendation",
        f"{profile.recommendation}: {profile.metadata.get('recommendation_rationale', '-')}",
        profile.metadata.get("recommendation_category", "Recommendation"),
    )

    tab_summary, tab_signals, tab_engines, tab_trace = st.tabs([
        "Summary",
        "Signals",
        "Engine Status",
        "Decision Trace",
    ])

    with tab_summary:
        section_title("Executive Summary")
        st.write(profile.metadata.get("executive_summary", "-"))
        section_title("Recruiter Summary")
        st.write(profile.metadata.get("recruiter_summary", "-"))
        st.caption(f"Pipeline version: {output.pipeline_version}")

    with tab_signals:
        section_title("CandidateDecisionProfile Signals")
        _metadata_table(output)

    with tab_engines:
        section_title("Engine Status")
        _engine_status(output)

    with tab_trace:
        section_title("Decision Trace")
        _decision_trace(output)
