from talentcopilot.services.llm_monitor_service import LLMMonitorService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme

def render_llm_monitor():
    import streamlit as st
    apply_enterprise_theme()
    service = LLMMonitorService()
    status = service.status()
    enterprise_hero("LLM Monitor", "Monitor extraction cache and LLM performance readiness.", "Release 2.0")
    metric_grid([
        ("Cache Entries", str(status.cache_entries), "Stored extractions"),
        ("Cache Size", f"{status.cache_size_bytes} bytes", "Local JSON cache"),
        ("Cache Dir", status.cache_dir, "Runtime storage"),
        ("Mode", "Cached", "Extraction"),
    ])
    insight_card("Performance principle", "TalentCopilot extracts each job once per batch and reuses cached CV extractions.", "LLM Performance")
    section_title("Cache Management")
    if st.button("Clear LLM extraction cache"):
        st.success(f"Cleared {service.clear_cache()} cached extraction file(s).")
