import streamlit as st
from .components import action_card, evidence_card, insight_card, metric_grid, recommendation_card, section_header, status_badge
from .layout import enterprise_page

def render_enterprise_v2_showcase() -> None:
    with enterprise_page(
        "Enterprise Design System v2",
        subtitle="Reusable presentation components for TalentCopilot workspaces.",
        eyebrow="Release 6.0B.1",
        metadata=["Presentation only", "Backward compatible", "Enterprise UI"],
    ):
        section_header("Official metrics", description="Consistent hierarchy for decision-critical values.")
        metric_grid([
            {"label":"Official match","value":"86%","caption":"Canonical session score","badge":"High confidence","tone":"success"},
            {"label":"Official rank","value":"#1","caption":"Among 12 candidates"},
            {"label":"Decision readiness","value":"91%","caption":"Ready for final review","badge":"Ready","tone":"success"},
            {"label":"Evidence quality","value":"Strong","caption":"7 verified signals","badge":"Governed","tone":"info"},
        ])
        section_header("Status language")
        cols = st.columns(5)
        for col, item in zip(cols, [("Approved","success"),("Needs review","warning"),("Risk","risk"),("Information","info"),("Pending","neutral")]):
            with col: status_badge(item[0], tone=item[1])
        section_header("AI decision support")
        recommendation_card("Proceed to final interview", reason="Strong HR transformation leadership and stakeholder ownership.", confidence=91, next_action="Validate global payroll exposure.")
        insight_card("Decision insight", "Supported by verified role scope, measurable outcomes and relevant platform experience.", badge="Explainable AI")
        evidence_card(["Workday programme leadership","SAP SuccessFactors delivery","Executive stakeholder management","Multi-country HR transformation"])
        action_card("Launch structured final interview", "Use the competency-specific interview plan and preserve official session evidence.")
