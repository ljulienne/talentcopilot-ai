from talentcopilot.real_matching.models import RealMatchingInput
from talentcopilot.real_matching.pipeline import RealMatchingPipeline
from talentcopilot.services.real_matching_demo_service import RealMatchingDemoService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


DEFAULT_CANDIDATE_TEXT = '''Alice Martin
Experience
8 years experience leading HRIS transformation projects.
Led Project Management and Stakeholder Management initiatives.
Skills
HRIS, Project Management, Stakeholder Management, Leadership, Workday
Achievements
Improved adoption by 35%.
'''

DEFAULT_JOB_TEXT = '''Transformation Lead
Responsibilities
Lead HRIS transformation projects and stakeholder management.
Requirements
Minimum 6 years experience.
Required skills: Project Management, Stakeholder Management, HRIS.
Languages
English and French.
Compensation
85000 100000
'''


def _render_output(output):
    import streamlit as st

    profile = output.decision_output.profile
    role = output.role_profile
    candidate = output.extracted_candidate

    metric_grid([
        ("Candidate", profile.candidate_name, candidate.extraction_status),
        ("Role", role.role_title, role.extraction_status),
        ("Fit", f"{profile.fit_score}%", profile.metadata.get("fit_status", "-")),
        ("Confidence", f"{profile.confidence_score}%", profile.metadata.get("confidence_level", "-")),
    ])

    insight_card(
        "Recommendation",
        f"{profile.recommendation}: {profile.metadata.get('recommendation_rationale', '-')}",
        profile.metadata.get("recommendation_category", "Decision Core"),
    )

    tab_candidate, tab_role, tab_decision, tab_trace = st.tabs([
        "Candidate Extraction",
        "Role Profile",
        "Decision Signals",
        "Decision Trace",
    ])

    with tab_candidate:
        section_title("Extracted Candidate")
        st.json({
            "candidate_name": candidate.candidate_name,
            "skills": candidate.skills,
            "language": candidate.language,
            "sections": [section.title for section in output.candidate_analysis.sections],
        })

    with tab_role:
        section_title("Extracted RoleProfile")
        st.json({
            "role_title": role.role_title,
            "required_skills": role.required_skills,
            "preferred_skills": role.preferred_skills,
            "minimum_years_experience": role.minimum_years_experience,
            "target_salary": role.target_salary,
            "maximum_salary": role.maximum_salary,
            "languages": role.languages,
        })

    with tab_decision:
        section_title("CandidateDecisionProfile")
        rows = [{"Signal": key, "Value": value} for key, value in profile.metadata.items()]
        st.dataframe(rows, use_container_width=True)

    with tab_trace:
        section_title("Decision Trace")
        for index, step in enumerate(profile.decision_trace.steps, start=1):
            with st.expander(f"{index}. {step.engine} · {step.action}"):
                st.write(step.explanation)
                st.caption(f"Output: {step.output_ref}")


def render_real_matching():
    import streamlit as st

    apply_enterprise_theme()

    enterprise_hero(
        "Real Matching",
        "Connect real candidate text and job description text to the Decision Intelligence Core.",
        "Release 1.2 — Real Intelligence",
    )

    insight_card(
        "End-to-end real-data flow",
        "Document Intelligence extracts the candidate, Job Intelligence extracts the role, and Decision Core produces the recommendation.",
        "Real Matching Pipeline",
    )

    candidate_text = st.text_area("Candidate CV text", value=DEFAULT_CANDIDATE_TEXT, height=220)
    job_text = st.text_area("Job description text", value=DEFAULT_JOB_TEXT, height=220)
    expected_salary = st.number_input("Candidate expected salary", value=90000, min_value=0, step=5000)

    col1, col2 = st.columns(2)
    run_manual = col1.button("Run real matching")
    run_demo = col2.button("Run demo")

    if run_demo:
        output = RealMatchingDemoService().run_demo().output
        _render_output(output)

    if run_manual:
        output = RealMatchingPipeline().run(
            RealMatchingInput(
                candidate_filename="candidate.txt",
                candidate_text=candidate_text,
                job_filename="job.txt",
                job_text=job_text,
                expected_salary=float(expected_salary),
            )
        )
        _render_output(output)
