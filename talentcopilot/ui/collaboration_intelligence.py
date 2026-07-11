from __future__ import annotations

import pandas as pd
import streamlit as st

from talentcopilot.organization_intelligence.collaboration_models import CollaborationDiagnostic
from talentcopilot.ui.intelligence_core import render_insight


def render_collaboration_intelligence(diagnostic: CollaborationDiagnostic) -> None:
    st.markdown("---")
    st.markdown("### Collaboration Intelligence")
    st.caption("Explainable collaboration signals inferred from reporting lines, shared skills and backup relationships.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Collaboration health", diagnostic.overall_health)
    c2.metric("Collaboration score", f"{diagnostic.overall_collaboration_score}/100")
    c3.metric("Strong silo signals", diagnostic.silo_count)
    c4.metric("Critical bridges", diagnostic.broker_count)

    if diagnostic.insights:
        st.markdown("#### What requires attention")
        for index, insight in enumerate(diagnostic.insights[:5]):
            render_insight(insight, expanded=index == 0)

    left, right = st.columns(2)
    with left:
        st.markdown("#### Department collaboration")
        department_df = pd.DataFrame([
            {
                "Department": item.department,
                "Score": item.collaboration_score,
                "Partners": item.partner_departments,
                "External links": item.external_links,
                "Risk": item.risk_level,
            }
            for item in diagnostic.departments
        ])
        st.dataframe(department_df, use_container_width=True, hide_index=True)

    with right:
        st.markdown("#### Collaboration bridges")
        if diagnostic.brokers:
            broker_df = pd.DataFrame([
                {
                    "Name": item.name,
                    "Department": item.department,
                    "Cross-department links": item.cross_department_links,
                    "Departments reached": item.departments_reached,
                    "Dependency": item.dependency_level,
                }
                for item in diagnostic.brokers[:8]
            ])
            st.dataframe(broker_df, use_container_width=True, hide_index=True)
        else:
            st.info("No critical collaboration bridge was inferred from the available data.")

    export = pd.DataFrame([
        {
            "department_a": item.department_a,
            "department_b": item.department_b,
            "inferred_links": item.inferred_links,
            "collaboration_score": item.collaboration_score,
            "risk_level": item.risk_level,
        }
        for item in diagnostic.department_pairs
    ])
    st.download_button(
        "Download collaboration diagnostic",
        export.to_csv(index=False).encode("utf-8"),
        file_name="talentcopilot_collaboration_diagnostic.csv",
        mime="text/csv",
    )
