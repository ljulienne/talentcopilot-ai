from talentcopilot.job_intelligence.job_section_segmenter import JobSectionSegmenter
from talentcopilot.job_intelligence.pipeline import JobIntelligencePipeline
from talentcopilot.ui.enterprise_navigation import get_page_by_label


def test_job_section_segmenter_detects_sections():
    sections = JobSectionSegmenter().segment(
        "Transformation Lead\nResponsibilities\nLead HRIS projects\nRequirements\nProject Management"
    )
    titles = [section.title for section in sections]
    assert "responsibilities" in titles
    assert "requirements" in titles


def test_job_pipeline_extracts_role_profile():
    analysis = JobIntelligencePipeline().analyze_text(
        "job.txt",
        "Transformation Lead\nRequirements\nMinimum 6 years experience. Project Management HRIS Leadership",
    )
    profile = analysis.role_profile

    assert profile.role_title
    assert profile.extraction_status == "Valid"
    assert "Project Management" in profile.required_skills
    assert profile.minimum_years_experience == 6


def test_job_intelligence_navigation():
    page = get_page_by_label("Job Intelligence")
    assert page is not None
    assert page.module == "talentcopilot.ui.job_intelligence"
