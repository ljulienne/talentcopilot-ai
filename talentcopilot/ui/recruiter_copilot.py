import streamlit as st

from talentcopilot.ai.openai_recruiter import generate_openai_recruiter_answer, is_openai_available
from talentcopilot.ai.recruiter_agent import RecruiterAgent
from talentcopilot.ai.recruiter_context import build_recruiter_context
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
    "Compare Emma and John.",
]


def _load_agent():
    raw_talents = list_talent_profiles()
    enriched = enrich_talent_profiles(raw_talents)
    enriched = enrich_talents_with_skills(enriched)
    return RecruiterAgent(enriched), enriched


def _init_conversation():
    if "recruiter_copilot_history" not in st.session_state:
        st.session_state.recruiter_copilot_history = []


def _add_message(role, content, title=None, source=None):
    st.session_state.recruiter_copilot_history.append(
        {
            "role": role,
            "title": title,
            "content": content,
            "source": source,
        }
    )


def _render_conversation():
    history = st.session_state.get("recruiter_copilot_history", [])

    if not history:
        st.info("No conversation yet. Ask TalentCopilot your first question.")
        return

    for message in history:
        role = message.get("role")
        title = message.get("title")
        content = message.get("content", "")
        source = message.get("source")

        if role == "user":
            st.markdown(f"**🧑 Recruiter:** {content}")
        else:
            label = f"### 🧠 {title or 'Recruiter Copilot'}"
            if source:
                label += f" · `{source}`"
            st.markdown(label)
            st.markdown(content)

        st.divider()


def render_recruiter_copilot():
    _init_conversation()

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
        "Use local reasoning or OpenAI-enhanced reasoning."
    )

    use_openai = st.toggle(
        "Use OpenAI generative reasoning",
        value=False,
        help="When enabled, TalentCopilot uses the local agent first, then asks OpenAI to generate a more executive answer from the structured context.",
    )

    if use_openai and not is_openai_available():
        st.warning("OPENAI_API_KEY is not configured. TalentCopilot will fall back to local reasoning.")

    with st.expander("Suggested Questions", expanded=True):
        for question in SUGGESTED_QUESTIONS:
            st.caption(question)

    question = st.text_input(
        "Your question",
        placeholder="Example: Who should I interview first?",
        key="recruiter_copilot_question",
    )

    col_ask, col_clear = st.columns([3, 1])

    with col_ask:
        ask = st.button("💬 Ask Recruiter Copilot", use_container_width=True)

    with col_clear:
        clear = st.button("🧹 Clear", use_container_width=True)

    if clear:
        st.session_state.recruiter_copilot_history = []
        st.rerun()

    if ask:
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            local_response = agent.answer(question)

            if use_openai and is_openai_available():
                context = build_recruiter_context(
                    question=question,
                    talents=talents,
                    local_response=local_response,
                )
                response = generate_openai_recruiter_answer(context)
                answer_text = response.get("answer", local_response.get("answer", "No answer available."))
                source = response.get("source", "openai")
                title = f"{local_response.get('title', 'Recruiter Copilot')} — Enhanced"
            else:
                answer_text = local_response.get("answer", "No answer available.")
                source = "local"
                title = local_response.get("title", "Recruiter Copilot")

            _add_message("user", question)
            _add_message("assistant", answer_text, title, source)

            st.rerun()

    st.divider()

    section_title(
        "Conversation",
        "Recruiter questions and TalentCopilot answers."
    )

    _render_conversation()

    st.divider()

    assistant_panel(
        "How it works",
        "TalentCopilot first uses its local recruitment intelligence engine. When OpenAI mode is enabled, it builds a structured context and generates a more executive recruiter-style answer."
    )
