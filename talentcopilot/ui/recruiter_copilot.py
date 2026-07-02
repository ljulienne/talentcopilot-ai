import streamlit as st

from talentcopilot.ai.recruiter_agent import RecruiterAgent
from talentcopilot.talent_pool.talent_metrics import enrich_talent_profiles
from talentcopilot.talent_pool.talent_skills import enrich_talents_with_skills
from talentcopilot.talent_pool.talent_store import list_talent_profiles
from talentcopilot.ui.components import section_title, assistant_panel, metric_card


SUGGESTED_QUESTIONS = [
    "Who is the best candidate?",
    "Which candidates are above budget?",
    "What skills are available?",
    "Who should I interview first?",
    "Show me risks or gaps.",
]


def _load_agent():
    raw_talents = list_talent_profiles()
    enriched = enrich_talent_profiles(raw_talents)
    enriched = enrich_talents_with_skills(enriched)
    return RecruiterAgent(enriched), enriched


def render_recruiter_copilot():
    st.markdown("""
    <div class="tc-hero">
        <h1>💬 Recruiter Copilot</h1>
        <h3>Ask questions across your Talent Pool</h3>
        <p class="tc-muted">
        Query TalentCopilot about candidates, skills, budget, risks and interview priorities.
        </p>
    </div>
    """, unsafe_allow_html=True)

    agent, talents = _load_agent()

    if not talents:
        assistant_panel(
            "Recruiter Copilot",
            "No talent data is available yet. Analyze and save a recruitment to populate the Talent Pool."
        )
        return

    col1, col2, col3 = st.columns(3)

    with col1:
        metric_card("Talents", len(talents), "Available in Talent Pool")

    with col2:
        top_score = max(talent.get("talent_score", 0) for talent in talents)
        metric_card("Top Talent Score", f"{top_score}%", "Best consolidated profile")

    with col3:
        with_financial = sum(1 for talent in talents if talent.get("financial_data"))
        metric_card("Financial Profiles", with_financial, "With budget data")

    st.divider()

    section_title(
        "Ask TalentCopilot",
        "Use natural questions to explore recruitment intelligence."
    )

    with st.expander("Suggested Questions", expanded=True):
        for question in SUGGESTED_QUESTIONS:
            st.caption(question)

    question = st.text_input(
        "Your question",
        placeholder="Example: Who should I interview first?",
        key="recruiter_copilot_question",
    )

    if st.button("💬 Ask Recruiter Copilot", use_container_width=True):
        response = agent.answer(question)

        st.markdown(f"### 🧠 {response.get('title', 'Recruiter Copilot')}")
        st.markdown(response.get("answer", "No answer available."))

    st.divider()

    assistant_panel(
        "How it works",
        "This first version uses TalentCopilot's local intelligence engine. Future versions will add OpenAI reasoning, conversation memory and advanced tool usage."
    )
