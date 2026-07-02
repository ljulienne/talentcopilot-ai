import streamlit as st

from talentcopilot.talent_pool.talent_skills import enrich_talent_with_skills
from talentcopilot.ui.components import metric_card, section_title


def render_skills(talent):
    enriched = enrich_talent_with_skills(talent)
    detected_skills = enriched.get("detected_skills", {})
    skill_coverage = enriched.get("skill_coverage", 0)

    section_title(
        "Skills Intelligence",
        "Skills detected from the talent's recruitment history and AI summaries.",
    )

    col1, col2 = st.columns(2)

    with col1:
        metric_card("Skill Coverage", f"{skill_coverage}%", "Detected skill categories")

    with col2:
        metric_card("Skill Categories", len(detected_skills), "Detected domains")

    st.progress(min(skill_coverage, 100) / 100)

    if not detected_skills:
        st.info("No structured skills detected yet. Future analyses will enrich this profile.")
        return

    for category, skills in detected_skills.items():
        with st.expander(category, expanded=True):
            st.write(", ".join(sorted(set(skills))))
