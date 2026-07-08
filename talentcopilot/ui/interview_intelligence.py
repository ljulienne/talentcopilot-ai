from talentcopilot.interview_intelligence_v2.interview_engine import InterviewIntelligenceEngine
from talentcopilot.services.real_ranking_demo_service import RealRankingDemoService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _render_question_set(question_set):
    import streamlit as st

    metric_grid([
        ("Candidate", question_set.candidate_name, question_set.role_title),
        ("Recommendation", question_set.recommendation, "Decision Core"),
        ("Evidence Gaps", str(len(question_set.evidence_gaps)), "Detected"),
        ("Questions", str(len(question_set.questions)), "Generated"),
    ])

    insight_card(
        "Interview strategy",
        question_set.summary,
        "Evidence-based interview",
    )

    tab_gaps, tab_questions = st.tabs(["Evidence Gaps", "Questions"])

    with tab_gaps:
        section_title("Evidence Gaps")
        rows = [
            {"Area": gap.area, "Severity": gap.severity, "Detail": gap.detail, "Reason": gap.reason}
            for gap in question_set.evidence_gaps
        ]
        st.dataframe(rows, use_container_width=True)

    with tab_questions:
        section_title("Structured Interview Questions")
        for index, q in enumerate(question_set.questions, start=1):
            with st.expander(f"{index}. {q.area}"):
                st.write(f"**Question:** {q.question}")
                st.write(f"**Purpose:** {q.purpose}")
                st.write(f"**Expected strong answer:** {q.expected_strong_answer}")
                st.write("**Positive signals:**")
                st.write(q.positive_signals)
                st.write("**Red flags:**")
                st.write(q.red_flags)
                st.write("**Follow-ups:**")
                st.write(q.follow_ups)
                st.write("**Evaluation criteria:**")
                st.write(q.evaluation_criteria)


def render_interview_intelligence():
    import streamlit as st

    apply_enterprise_theme()

    enterprise_hero(
        "Interview Intelligence",
        "Generate targeted interview questions from Decision Core evidence gaps.",
        "Release 1.2 — Real Intelligence",
    )

    insight_card(
        "Interview principle",
        "Interviews should validate uncertainty. Questions are generated from evidence gaps, risk and confidence signals.",
        "Evidence Gap Engine",
    )

    ranking = RealRankingDemoService().run_demo().output
    names = [item.candidate_name for item in ranking.ranked_candidates]
    selected = st.selectbox("Candidate from real ranking demo", names)
    item = ranking.ranked_candidates[names.index(selected)]
    profile = item.matching_output.decision_output.profile

    if st.button("Generate interview questions"):
        question_set = InterviewIntelligenceEngine().generate(profile)
        _render_question_set(question_set)
