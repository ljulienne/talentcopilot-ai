import streamlit as st

from talentcopilot.ui.ai_cards import ai_recommendation_card
from talentcopilot.ui.financial_cards import financial_card
from talentcopilot.ui.hero_components import candidate_hero
from talentcopilot.ui.interview_cards import interview_card
from talentcopilot.ui.kpi_components import candidate_kpis
from talentcopilot.ui.skills_cards import skills_card
from talentcopilot.ui.summary_cards import executive_summary_card
from talentcopilot.ui.timeline_cards import timeline_card


def render_candidate_workspace(talent: dict):
    candidate_hero(
        name=talent.get("name", "Unknown Candidate"),
        talent_score=talent.get("talent_score", 0),
        confidence=talent.get("average_confidence", 0),
        applications=talent.get("application_count", 0),
        recommendation=talent.get(
            "recommendation",
            "No recommendation available",
        ),
    )

    candidate_kpis(talent)

    ai_recommendation_card(talent)

    executive_summary_card(talent)

    skills_card(talent)

    interview_card(talent)

    financial_card(talent)

    timeline_card(talent)

    st.divider()

    st.success("✅ Candidate Workspace v2 structure ready.")
