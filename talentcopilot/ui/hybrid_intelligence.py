from talentcopilot.hybrid_matching.engine import HybridMatchingEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput
from talentcopilot.services.hybrid_intelligence_demo_service import HybridIntelligenceDemoService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _render_report(report):
    import streamlit as st

    metric_grid([
        ("Candidate", report.candidate_name, report.role_title),
        ("Hybrid Score", f"{report.hybrid_score}%", "Explainable"),
        ("Semantic Score", f"{report.semantic_score}%", "Skill proximity"),
        ("Career Score", f"{report.career_score}%", report.career_report.seniority_level if report.career_report else "-"),
    ])

    insight_card("Recruiter Summary", report.summary, "Explainable Hybrid Matching")

    tab_breakdown, tab_skills, tab_career, tab_explain = st.tabs([
        "Score Breakdown",
        "Semantic Skills",
        "Career Intelligence",
        "Explainability",
    ])

    with tab_breakdown:
        section_title("Score Breakdown")
        if report.explanation_report:
            st.json(report.explanation_report.breakdown.__dict__)
        else:
            st.info("No explanation report available.")

    with tab_skills:
        section_title("Semantic Skill Matching")
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

    with tab_career:
        section_title("Career & Achievement Signals")
        if not report.career_report:
            st.info("No career report.")
        else:
            st.write(f"**Seniority:** {report.career_report.seniority_level}")
            rows = [
                {
                    "Category": signal.category,
                    "Label": signal.label,
                    "Score": signal.score,
                    "Evidence": " | ".join(signal.evidence),
                }
                for signal in report.career_report.signals
            ]
            st.dataframe(rows, use_container_width=True)

    with tab_explain:
        section_title("Positive Contributions")
        if report.explanation_report:
            st.dataframe(
                [
                    {
                        "Category": item.category,
                        "Label": item.label,
                        "Points": item.points,
                        "Evidence": " | ".join(item.evidence),
                        "Explanation": item.explanation,
                    }
                    for item in report.explanation_report.positive_contributions
                ],
                use_container_width=True,
            )

            section_title("Penalties")
            st.dataframe(
                [
                    {
                        "Category": item.category,
                        "Label": item.label,
                        "Points": item.points,
                        "Evidence": " | ".join(item.evidence),
                        "Explanation": item.explanation,
                    }
                    for item in report.explanation_report.penalties
                ],
                use_container_width=True,
            )


def render_hybrid_intelligence():
    import streamlit as st

    apply_enterprise_theme()

    enterprise_hero(
        "Hybrid Intelligence",
        "Explain candidate-role fit through semantic skills, career evidence and score contributions.",
        "Release 2.0 — Sprint 4C",
    )

    insight_card(
        "Why this matters",
        "Hybrid Intelligence now explains why a candidate receives a score, including positive factors and penalties.",
        "Explainable Matching",
    )

    tab_demo, tab_custom = st.tabs(["Demo", "Custom"])

    with tab_demo:
        if st.button("Run hybrid demo"):
            _render_report(HybridIntelligenceDemoService().run_demo().report)

    with tab_custom:
        candidate_name = st.text_input("Candidate name", value="Candidate")
        role_title = st.text_input("Role title", value="HRIS Manager")
        years_experience = st.number_input("Years of experience", min_value=0, max_value=50, value=8)
        candidate_skills = st.text_area("Candidate skills, comma-separated", value="SIRH, Workday, OCTIME, Business Objects")
        required_skills = st.text_area("Required skills, comma-separated", value="HRIS, Time Management, Reporting, Project Management")
        titles = st.text_area("Titles, one per line", value="HRIS Consultant\nHRIS Project Manager")
        achievements = st.text_area("Achievements, one per line", value="Improved adoption by 35%\nLed HRIS transformation")

        if st.button("Run hybrid comparison"):
            report = HybridMatchingEngine().analyze(
                HybridMatchingInput(
                    candidate_name=candidate_name,
                    role_title=role_title,
                    candidate_skills=[s.strip() for s in candidate_skills.split(",") if s.strip()],
                    required_skills=[s.strip() for s in required_skills.split(",") if s.strip()],
                    years_experience=int(years_experience),
                    titles=[s.strip() for s in titles.splitlines() if s.strip()],
                    achievements=[s.strip() for s in achievements.splitlines() if s.strip()],
                    responsibilities=[],
                )
            )
            _render_report(report)
