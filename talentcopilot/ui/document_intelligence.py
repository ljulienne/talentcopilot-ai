from talentcopilot.document_intelligence.pipeline import DocumentIntelligencePipeline
from talentcopilot.services.document_intelligence_status_service import DocumentIntelligenceStatusService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_document_intelligence():
    import streamlit as st

    apply_enterprise_theme()

    status = DocumentIntelligenceStatusService().build_sample()

    enterprise_hero(
        "Document Intelligence",
        "Extract structured candidate data from documents before sending it to the Decision Core.",
        "Release 1.2 — Real Intelligence",
    )

    metric_grid([
        ("Sample Language", status.language, "Detected"),
        ("Sections", str(status.section_count), "Segmented"),
        ("Candidate", status.candidate_name, status.extraction_status),
        ("Skills", str(status.skills_count), "Extracted"),
    ])

    insight_card(
        "Document Intelligence principle",
        "This layer extracts structured data only. Scores and hiring recommendations remain owned by the Decision Core.",
        "AI Governance",
    )

    sample_text = st.text_area(
        "Paste CV text",
        value="Alice Martin\nExperience\nLed HRIS transformation and Project Management initiatives.\nSkills\nHRIS, Leadership, Project Management, Workday",
        height=180,
    )

    if st.button("Analyze sample text"):
        analysis, candidate = DocumentIntelligencePipeline().analyze_text("pasted_cv.txt", sample_text)

        tab_candidate, tab_sections, tab_cleaned = st.tabs(["Candidate", "Sections", "Cleaned Text"])

        with tab_candidate:
            section_title("Structured Candidate Extraction")
            st.json({
                "candidate_name": candidate.candidate_name,
                "skills": candidate.skills,
                "language": candidate.language,
                "extraction_status": candidate.extraction_status,
                "raw_excerpt": candidate.raw_excerpt,
            })

        with tab_sections:
            section_title("Detected Sections")
            rows = [
                {"Section": section.title, "Confidence": section.confidence, "Content": section.content[:300]}
                for section in analysis.sections
            ]
            st.dataframe(rows, use_container_width=True)

        with tab_cleaned:
            section_title("Cleaned Text")
            st.text(analysis.cleaned_text[:3000])
