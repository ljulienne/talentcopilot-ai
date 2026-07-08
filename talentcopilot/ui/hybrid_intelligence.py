from talentcopilot.hybrid_matching.engine import HybridMatchingEngine
from talentcopilot.hybrid_matching.models import HybridMatchingInput
from talentcopilot.services.hybrid_intelligence_demo_service import HybridIntelligenceDemoService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _render_report(report):
    import streamlit as st

    recruiter = report.recruiter_report

    metric_grid([
        ("Candidate", report.candidate_name, report.role_title),
        ("Hybrid Score", f"{report.hybrid_score}%", recruiter.readiness_level if recruiter else "Explainable"),
        ("Semantic Score", f"{report.semantic_score}%", "Skill proximity"),
        ("Career Score", f"{report.career_score}%", report.career_report.seniority_level if report.career_report else "-"),
    ])

    insight_card("Recruiter Summary", report.summary, "Hybrid Intelligence Report")

    tab_summary, tab_breakdown, tab_skills, tab_career, tab_explain = st.tabs([
        "Recruiter Report",
        "Score Breakdown",
        "Semantic Skills",
        "Career Intelligence",
        "Explainability",
    ])

    with tab_summary:
        section_title("Recruiter-Ready Report")
        if recruiter:
            st.write(f"**Readiness:** {recruiter.readiness_level}")
            st.write(f"**Action:** {recruiter.action_recommendation}")
            st.write(recruiter.executive_summary)

            st.write("**Top strengths**")
            st.write(recruiter.top_strengths or ["No major strength detected yet."])

            st.write("**Gaps**")
            st.write(recruiter.gaps or ["No critical gap detected."])

            st.write("**Interview focus**")
            st.write(recruiter.interview_focus)
        else:
            st.info("No recruiter report available.")

    with tab_breakdown:
        section_title("Score Breakdown")
        if report.explanation_report:
            st.json(report.explanation_report.breakdown.__dict__)

    with tab_skills:
        section_title("Semantic Skill Matching")
        st.dataframe([
            {
                "Required Skill": match.required_skill,
                "Candidate Skill": match.candidate_skill or "-",
                "Score": match.score,
                "Type": match.match_type,
                "Explanation": match.explanation,
            }
            for match in report.semantic_skill_report.matches
        ], use_container_width=True)

    with tab_career:
        section_title("Career & Achievement Signals")
        if report.career_report:
            st.write(f"**Seniority:** {report.career_report.seniority_level}")
            st.dataframe([
                {
                    "Category": signal.category,
                    "Label": signal.label,
                    "Score": signal.score,
                    "Evidence": " | ".join(signal.evidence),
                }
                for signal in report.career_report.signals
            ], use_container_width=True)

    with tab_explain:
        section_title("Explainability")
        if report.explanation_report:
            st.write(report.explanation_report.recruiter_summary)
            st.dataframe([
                {
                    "Category": item.category,
                    "Label": item.label,
                    "Points": item.points,
                    "Evidence": " | ".join(item.evidence),
                    "Explanation": item.explanation,
                }
                for item in report.explanation_report.positive_contributions
            ], use_container_width=True)


def render_hybrid_intelligence():
    import streamlit as st

    apply_enterprise_theme()

    enterprise_hero(
        "Hybrid Intelligence",
        "Generate recruiter-ready explanations from semantic skills, career evidence and hybrid scoring.",
        "Release 2.0 — Sprint 4E",
    )

    insight_card(
        "Why this matters",
        "The system now turns hybrid matching into actionable recruiter guidance.",
        "Recruiter Report",
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
