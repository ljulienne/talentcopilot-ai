from talentcopilot.llm_extraction.engine import LLMExtractionEngine
from talentcopilot.services.llm_extraction_status_service import LLMExtractionStatusService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def render_llm_extraction():
    import streamlit as st

    apply_enterprise_theme()

    status = LLMExtractionStatusService().build()

    enterprise_hero(
        "LLM Extraction",
        "Extract CVs and job descriptions into structured Pydantic models.",
        "Release 2.0",
    )

    metric_grid([
        ("OpenAI Key", "Configured" if status.openai_key_configured else "Not configured", "Environment"),
        ("Mode", status.mode, "Extraction"),
        ("Sample Candidate", status.sample_candidate_name, status.sample_status),
        ("Confidence", str(status.sample_confidence), "Extraction"),
    ])

    insight_card(
        "Extraction principle",
        "The LLM extracts structured facts and insights. Decision Core still owns scoring and recommendations.",
        "AI Governance",
    )

    tab_candidate, tab_role = st.tabs(["Candidate Extraction", "Role Extraction"])

    with tab_candidate:
        section_title("Candidate Structured Extraction")
        text = st.text_area(
            "CV text",
            value="LORETTA DANIELSON, MBA, SPHR, SHRM-SCP\nHuman Resources Director\nHRIS, Change Management, Talent Acquisition",
            height=180,
        )
        if st.button("Extract candidate"):
            result = LLMExtractionEngine().extract_candidate(text)
            st.json(result.model_dump())

    with tab_role:
        section_title("Role Structured Extraction")
        text = st.text_area(
            "Job description text",
            value="HRIS Director\nMinimum 8 years experience. Required skills: HRIS, Change Management, Leadership.",
            height=180,
        )
        if st.button("Extract role"):
            result = LLMExtractionEngine().extract_role(text)
            st.json(result.model_dump())
