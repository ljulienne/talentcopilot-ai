from talentcopilot.hybrid_matching.engine import HybridMatchingEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput
from talentcopilot.services.hybrid_intelligence_demo_service import HybridIntelligenceDemoService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _render_report(report):
    import streamlit as st

    metric_grid([
        ("Candidate", report.candidate_name, report.role_title),
        ("Semantic Score", f"{report.semantic_score}%", "Skill proximity"),
        ("Covered Skills", str(report.semantic_skill_report.covered_skills), "Required skills"),
        ("Missing", str(len(report.semantic_skill_report.missing_skills)), "Skills"),
    ])

    insight_card("Hybrid Matching Summary", report.summary, "Semantic Skill Intelligence")

    rows = [
        {
            "Required Skill": match.required_skill,
            "Candidate Skill": match.candidate_skill or "-",
            "Score": match.score,
            "Type": match.match_type,
            "Explanation": match.explanation,
        }
        for match in report.semantic_skill_report.matches
    ]
    st.dataframe(rows, use_container_width=True)


def render_hybrid_intelligence():
    import streamlit as st

    apply_enterprise_theme()

    enterprise_hero(
        "Hybrid Intelligence",
        "Compare candidates and roles through semantic skill proximity.",
        "Release 2.0 — Sprint 4A",
    )

    insight_card(
        "Why this matters",
        "This engine recognizes that SIRH, HRIS, Workday, SuccessFactors and Oracle HCM can be semantically related instead of requiring exact keywords.",
        "Hybrid Matching Foundation",
    )

    tab_demo, tab_custom = st.tabs(["Demo", "Custom"])

    with tab_demo:
        if st.button("Run hybrid demo"):
            _render_report(HybridIntelligenceDemoService().run_demo().report)

    with tab_custom:
        candidate_name = st.text_input("Candidate name", value="Candidate")
        role_title = st.text_input("Role title", value="HRIS Manager")
        candidate_skills = st.text_area("Candidate skills, comma-separated", value="SIRH, Workday, OCTIME, Business Objects")
        required_skills = st.text_area("Required skills, comma-separated", value="HRIS, Time Management, Reporting, Project Management")

        if st.button("Run semantic comparison"):
            report = HybridMatchingEngine().analyze(
                HybridMatchingInput(
                    candidate_name=candidate_name,
                    role_title=role_title,
                    candidate_skills=[s.strip() for s in candidate_skills.split(",") if s.strip()],
                    required_skills=[s.strip() for s in required_skills.split(",") if s.strip()],
                )
            )
            _render_report(report)
