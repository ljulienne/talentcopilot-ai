import pandas as pd
import streamlit as st

from talentcopilot.organization_intelligence.demo_data import demo_dataframe
from talentcopilot.organization_intelligence.ingestion import dataframe_to_employees, load_uploaded_file
from talentcopilot.organization_intelligence.knowledge_engine import KnowledgeConcentrationEngine
from talentcopilot.organization_intelligence.graph import OrganizationGraphBuilder
from talentcopilot.organization_intelligence.graph_engine import OrganizationGraphEngine
from talentcopilot.organization_intelligence.graph_export import edges_dataframe
from talentcopilot.intelligence_core.adapters import KnowledgeInsightAdapter
from talentcopilot.intelligence_core.engine import DecisionEngine, ExecutiveEngine
from talentcopilot.ui.intelligence_core import render_executive_brief, render_insight
from talentcopilot.ui.decision_queue import render_decision_queue
from talentcopilot.ui.decision_timeline import render_decision_timeline
from talentcopilot.ui.next_shell import apply_next_style, hero, insight_card, recommendation_block
from talentcopilot.skills_intelligence import SkillsIntelligenceEngine, skills_dataframe


def _render_diagnostic(diagnostic):
    insights = KnowledgeInsightAdapter().from_diagnostic(diagnostic)
    brief = ExecutiveEngine().generate(insights)
    render_executive_brief(brief)
    recommendation_block("Diagnostic summary", diagnostic.summary)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Employees analyzed", diagnostic.employee_count)
    c2.metric("Skills mapped", diagnostic.skill_count)
    c3.metric("High-risk skills", diagnostic.high_risk_count)
    c4.metric("Overall risk", f"{diagnostic.overall_risk_score}/100")

    if not diagnostic.skill_risks:
        st.info("No skill data was available for diagnosis.")
        return

    st.markdown("### Priority organizational insights")
    for index, insight in enumerate(insights[:5]):
        render_insight(insight, expanded=index == 0)

    st.markdown("### Detailed knowledge risks")
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

    return insights

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
        knowledge_insights = _render_diagnostic(diagnostic)
        st.markdown("---")
        st.markdown("### Organization graph foundation")
        graph = OrganizationGraphBuilder().build(employees)
        graph_diagnostic = OrganizationGraphEngine().analyze(graph)

        g1, g2, g3, g4 = st.columns(4)
        g1.metric("People nodes", graph_diagnostic.employee_count)
        g2.metric("Inferred relationships", graph_diagnostic.edge_count)
        g3.metric("Key connectors", graph_diagnostic.connector_count)
        g4.metric("Isolated departments", graph_diagnostic.isolated_department_count)

        if graph_diagnostic.insights:
            st.markdown("#### Network insights")
            for index, insight in enumerate(graph_diagnostic.insights[:4]):
                render_insight(insight, expanded=index == 0)

        st.markdown("---")
        st.markdown("### Skills Intelligence")
        st.caption("Normalize the skills portfolio, identify strategic gaps and reveal capabilities that are rare or concentrated.")
        strategic_text = st.text_input(
            "Strategic skills to assess",
            value="HRIS, Project Management, Payroll, Artificial Intelligence",
            help="Comma-separated capabilities that matter to the organization's strategy.",
        )
        strategic_skills = [item.strip() for item in strategic_text.split(",") if item.strip()]
        skills_report = SkillsIntelligenceEngine().analyze(employees, strategic_skills=strategic_skills)

        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Portfolio health", f"{skills_report.portfolio_health_score}/100")
        s2.metric("Normalized skills", skills_report.unique_skill_count)
        s3.metric("Critical exposures", skills_report.critical_skill_count)
        s4.metric("Strategic gaps", skills_report.missing_strategic_count)
        st.write(skills_report.executive_summary)

        if skills_report.insights:
            st.markdown("#### Priority skills insights")
            for index, insight in enumerate(skills_report.insights[:4]):
                render_insight(insight, expanded=index == 0)

        skills_table = skills_dataframe(skills_report)
        if not skills_table.empty:
            st.markdown("#### Skills portfolio")
            st.dataframe(
                skills_table[["skill", "category", "strategic", "gap_status", "holder_count", "department_count", "rarity_score", "coverage_level"]],
                use_container_width=True,
                hide_index=True,
            )
            st.download_button(
                "Download skills intelligence CSV",
                skills_table.to_csv(index=False).encode("utf-8"),
                file_name="talentcopilot_skills_intelligence.csv",
                mime="text/csv",
            )

        combined_insights = [
            *(knowledge_insights or []),
            *(getattr(graph_diagnostic, "insights", []) or []),
            *(getattr(skills_report, "insights", []) or []),
        ]
        decision_queue = DecisionEngine().generate(combined_insights)
        st.markdown("---")
        render_decision_queue(decision_queue)
        render_decision_timeline(decision_queue)

        left, right = st.columns(2)
        with left:
            st.markdown("#### Most connected people")
            people_df = pd.DataFrame([
                {
                    "Name": item.name,
                    "Department": item.department,
                    "Relationships": item.degree,
                    "Cross-department": item.cross_department_links,
                }
                for item in graph_diagnostic.people[:8]
            ])
            st.dataframe(people_df, use_container_width=True, hide_index=True)
        with right:
            st.markdown("#### Department connectivity")
            dept_df = pd.DataFrame([
                {
                    "Department": item.department,
                    "Employees": item.employee_count,
                    "External links": item.external_links,
                    "Connectivity": item.connectivity_score,
                }
                for item in graph_diagnostic.departments
            ])
            st.dataframe(dept_df, use_container_width=True, hide_index=True)

        graph_export = edges_dataframe(graph)
        st.download_button(
            "Download inferred organization graph",
            graph_export.to_csv(index=False).encode("utf-8"),
            file_name="talentcopilot_organization_graph.csv",
            mime="text/csv",
        )
    except Exception as exc:
        st.error("The organization diagnostic could not be generated.")
        st.exception(exc)
