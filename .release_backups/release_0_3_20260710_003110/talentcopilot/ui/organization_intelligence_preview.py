import pandas as pd
import streamlit as st

from talentcopilot.organization_intelligence.demo_data import demo_dataframe
from talentcopilot.organization_intelligence.ingestion import dataframe_to_employees, load_uploaded_file
from talentcopilot.organization_intelligence.knowledge_engine import KnowledgeConcentrationEngine
from talentcopilot.ui.next_shell import apply_next_style, hero, insight_card, recommendation_block


def _render_diagnostic(diagnostic):
    recommendation_block("Executive Brief", diagnostic.summary)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Employees analyzed", diagnostic.employee_count)
    c2.metric("Skills mapped", diagnostic.skill_count)
    c3.metric("High-risk skills", diagnostic.high_risk_count)
    c4.metric("Overall risk", f"{diagnostic.overall_risk_score}/100")

    if not diagnostic.skill_risks:
        st.info("No skill data was available for diagnosis.")
        return

    st.markdown("### Priority knowledge risks")
    for risk in diagnostic.skill_risks[:8]:
        badge = "🔴" if risk.risk_level == "High" else "🟠" if risk.risk_level == "Medium" else "🟢"
        with st.expander(f"{badge} {risk.skill} — {risk.risk_score}/100 ({risk.risk_level})", expanded=risk.risk_level == "High"):
            st.write(f"**Holders:** {', '.join(risk.holders) or 'None'}")
            st.write(f"**Departments:** {', '.join(risk.departments) or 'Unknown'}")
            st.write(f"**Backups:** {', '.join(risk.backups) or 'None identified'}")
            st.markdown("**Why this matters**")
            for reason in risk.reasons:
                st.write(f"- {reason}")
            st.markdown("**Recommended actions**")
            for action in risk.recommendations:
                st.write(f"- {action}")

    export = pd.DataFrame([
        {
            "skill": r.skill,
            "risk_score": r.risk_score,
            "risk_level": r.risk_level,
            "holders": "; ".join(r.holders),
            "backups": "; ".join(r.backups),
            "reasons": "; ".join(r.reasons),
            "recommendations": "; ".join(r.recommendations),
        }
        for r in diagnostic.skill_risks
    ])
    st.download_button(
        "Download diagnostic CSV",
        export.to_csv(index=False).encode("utf-8"),
        file_name="talentcopilot_knowledge_concentration_diagnostic.csv",
        mime="text/csv",
    )


def render_organization_intelligence_preview():
    apply_next_style()
    hero(
        "Organization Intelligence",
        "Reveal where critical knowledge is concentrated, why continuity is at risk, and which actions should be prioritized.",
        tag="Knowledge Concentration Engine v1",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        insight_card("Upload-first", "Analyze HRIS exports without creating employee records in TalentCopilot.", "CSV and Excel supported.")
    with col2:
        insight_card("Explainable", "Every risk score is supported by explicit reasons and evidence.", "No opaque AI grade.")
    with col3:
        insight_card("Action-oriented", "Each risk produces practical continuity and knowledge-transfer actions.", "Designed for HR, HRIS and transformation leaders.")

    source = st.radio("Choose a data source", ["Demo organization", "Upload company data"], horizontal=True)

    try:
        if source == "Demo organization":
            df = demo_dataframe()
            with st.expander("View demo input data"):
                st.dataframe(df, use_container_width=True, hide_index=True)
            employees = dataframe_to_employees(df)
        else:
            uploaded = st.file_uploader("Upload an employee skills export", type=["csv", "xlsx", "xls"])
            st.caption("Required columns: name, department, skills. Optional: employee_id, role, manager, critical_skills, backup_for, retirement_risk, documentation_level.")
            if uploaded is None:
                st.info("Upload a file to generate the diagnostic.")
                return
            employees = load_uploaded_file(uploaded)

        diagnostic = KnowledgeConcentrationEngine().analyze(employees)
        _render_diagnostic(diagnostic)
    except Exception as exc:
        st.error("The organization diagnostic could not be generated.")
        st.exception(exc)
