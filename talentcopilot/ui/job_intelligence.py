from talentcopilot.job_intelligence.pipeline import JobIntelligencePipeline
from talentcopilot.services.job_intelligence_status_service import JobIntelligenceStatusService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_job_intelligence():
    import streamlit as st

    apply_enterprise_theme()

    status = JobIntelligenceStatusService().build_sample()

    enterprise_hero(
        "Job Intelligence",
        "Extract structured role requirements from job descriptions before matching candidates.",
        "Release 1.2 — Real Intelligence",
    )

    metric_grid([
        ("Sample Language", status.language, "Detected"),
        ("Sections", str(status.section_count), "Segmented"),
        ("Role", status.role_title, status.extraction_status),
        ("Required Skills", str(status.required_skills_count), f"{status.minimum_years_experience} years min"),
    ])

    insight_card(
        "Job Intelligence principle",
        "This layer extracts job requirements. Candidate scoring and recommendation remain owned by the Decision Core.",
        "AI Governance",
    )

    sample_text = st.text_area(
        "Paste job description",
        value=(
            "Transformation Lead\n"
            "Responsibilities\n"
            "Lead HRIS transformation projects and stakeholder management.\n"
            "Requirements\n"
            "Minimum 6 years experience. Required skills: Project Management, Stakeholder Management, HRIS, Leadership.\n"
            "Languages\nEnglish and French.\n"
            "Compensation\n85000 100000"
        ),
        height=220,
    )

    if st.button("Analyze job description"):
        analysis = JobIntelligencePipeline().analyze_text("pasted_job.txt", sample_text)
        profile = analysis.role_profile

        tab_profile, tab_sections, tab_cleaned = st.tabs(["Role Profile", "Sections", "Cleaned Text"])

        with tab_profile:
            section_title("Structured RoleProfile")
            st.json({
                "role_title": profile.role_title,
                "required_skills": profile.required_skills,
                "preferred_skills": profile.preferred_skills,
                "minimum_years_experience": profile.minimum_years_experience,
                "responsibilities": profile.responsibilities,
                "languages": profile.languages,
                "certifications": profile.certifications,
                "target_salary": profile.target_salary,
                "maximum_salary": profile.maximum_salary,
                "language": profile.language,
                "extraction_status": profile.extraction_status,
            })

        with tab_sections:
            section_title("Detected Job Sections")
            rows = [
                {"Section": section.title, "Confidence": section.confidence, "Content": section.content[:300]}
                for section in analysis.sections
            ]
            st.dataframe(rows, use_container_width=True)

        with tab_cleaned:
            section_title("Cleaned Text")
            st.text(analysis.cleaned_text[:3000])
