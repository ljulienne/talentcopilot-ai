from __future__ import annotations

import pandas as pd
import streamlit as st

from talentcopilot.intelligence_core.engine import DecisionEngine
from talentcopilot.organization_intelligence.models import EmployeeRecord
from talentcopilot.ui.decision_queue import render_decision_queue
from talentcopilot.ui.intelligence_core import render_insight
from talentcopilot.workforce_intelligence import WorkforceScenarioEngine, successors_dataframe


def render_workforce_intelligence(employees: list[EmployeeRecord]) -> list:
    st.markdown("---")
    st.markdown("### Workforce Intelligence")
    st.caption("Simulate the impact of a departure using employee skills, critical capabilities and internal successor coverage.")

    options = {f"{employee.name} — {employee.role or 'Role unspecified'}": employee.employee_id for employee in employees}
    selected_label = st.selectbox("Select an employee departure scenario", list(options))
    report = WorkforceScenarioEngine().analyze_departure(employees, options[selected_label])
    impact = report.impact

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Continuity risk", f"{impact.risk_score}/100")
    c2.metric("Critical skills exposed", len(impact.critical_lost_skills))
    c3.metric("Unique skills exposed", len(impact.unique_skills_lost))
    c4.metric("Successor candidates", len(impact.successor_candidates))

    st.info(impact.executive_summary)

    for insight in impact.insights:
        render_insight(insight, expanded=True)

    st.markdown("#### Internal successor candidates")
    successor_df = successors_dataframe(report)
    if successor_df.empty:
        st.warning("No internal successor candidate currently matches the exposed skills.")
    else:
        st.dataframe(successor_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download successor analysis",
            successor_df.to_csv(index=False).encode("utf-8"),
            file_name="talentcopilot_workforce_successors.csv",
            mime="text/csv",
        )

    st.markdown("#### Recommended actions")
    for index, action in enumerate(impact.recommendations, start=1):
        st.write(f"{index}. {action}")

    if impact.insights:
        queue = DecisionEngine().generate(impact.insights)
        render_decision_queue(queue)

    return list(impact.insights)
