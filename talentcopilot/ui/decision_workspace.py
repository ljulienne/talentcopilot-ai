import streamlit as st

from talentcopilot.ai.reasoning_engine import ReasoningEngine
from talentcopilot.ai.interview_intelligence import InterviewIntelligenceEngine
from talentcopilot.ai.recommendation_engine import RecommendationEngine
from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceBuilder


def _build_demo_view_model():
    candidate = {
        "name": "Alice Martin",
        "skills": ["Project Management", "Stakeholder Management", "Change Management"],
        "years_experience": 8,
        "achievements": ["Reduced processing time by 35%"],
    }

    job = {
        "title": "Transformation Lead",
        "required_skills": ["Project Management", "Stakeholder Management"],
        "preferred_skills": ["Change Management"],
        "years_experience": 5,
    }

    evidence = [
        {"text": "Led a transformation project across 4 countries."},
        {"text": "Managed executive stakeholders during a major process redesign."},
        {"text": "Reduced processing time by 35% through workflow automation."},
    ]

    reasoning_report = ReasoningEngine().build_report(
        candidate=candidate,
        job=job,
        evidence=evidence,
        match_result={"score": 88},
    )

    interview_guide = InterviewIntelligenceEngine().build_guide(reasoning_report)
    recommendation_report = RecommendationEngine().build_recommendation([reasoning_report])

    return DecisionWorkspaceBuilder().build(
        reasoning_report=reasoning_report,
        interview_guide=interview_guide,
        recommendation_report=recommendation_report,
    )


def _render_metric(label, value, help_text=None):
    with st.container(border=True):
        st.metric(label, value)
        if help_text:
            st.caption(help_text)


def render_decision_workspace():
    view_model = _build_demo_view_model()

    with st.container(border=True):
        st.caption("Decision Intelligence Workspace")
        st.title(f"🧠 {view_model.candidate_name}")
        st.subheader(view_model.role_title)
        st.success(view_model.recommendation)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        _render_metric("Decision Confidence", f"{view_model.decision_confidence}%", "Confidence in the recommendation")

    with col2:
        _render_metric("Decision Readiness", f"{view_model.decision_readiness}%", "Ready for next recruiting step")

    with col3:
        demonstrated = len([
            s for s in view_model.reasoning_report.skill_assessment
            if s.status == "demonstrated"
        ])
        _render_metric("Demonstrated Skills", demonstrated, "Supported by evidence")

    with col4:
        _render_metric("Decision Risks", len(view_model.reasoning_report.risks), "To validate before decision")

    left, right = st.columns([2, 1])

    with left:
        with st.container(border=True):
            st.subheader("📌 Executive Summary")
            st.write(view_model.executive_summary)

        with st.container(border=True):
            st.subheader("🧭 Decision Framework")
            tabs = st.tabs([step.name for step in view_model.timeline])
            for tab, step in zip(tabs, view_model.timeline):
                with tab:
                    if step.status == "completed":
                        st.success("Completed")
                    else:
                        st.warning("Requires attention")
                    st.write(step.description)

        with st.container(border=True):
            st.subheader("📎 Evidence Explorer")
            for evidence in view_model.reasoning_report.evidence_assessment[:4]:
                with st.expander(f"{evidence.strength.title()} evidence · {int(evidence.confidence_score * 100)}%", expanded=False):
                    st.write(f"“{evidence.text}”")
                    st.info(evidence.interpretation)

        with st.container(border=True):
            st.subheader("🎯 Interview Intelligence")
            st.write(view_model.interview_guide.interview_focus)

            for question in view_model.interview_guide.questions[:3]:
                with st.expander(question.question, expanded=False):
                    st.markdown("**Objective**")
                    st.write(question.objective)

                    st.markdown("**Strong answer should include**")
                    for item in question.strong_answer_should_include:
                        st.write(f"- {item}")

                    st.markdown("**Red flags**")
                    for item in question.red_flags:
                        st.write(f"- {item}")

    with right:
        with st.container(border=True):
            st.subheader("✅ AI Recommendation")
            st.write(view_model.reasoning_report.recommendation_rationale)

        with st.container(border=True):
            st.subheader("⚖️ Challenge")
            st.warning(view_model.recommendation_report.challenge)

        with st.container(border=True):
            st.subheader("🚀 Actions")
            st.button("Compare Candidate", use_container_width=True, disabled=True)
            st.button("Generate Decision Report", use_container_width=True, disabled=True)
            st.button("Ask Copilot", use_container_width=True, disabled=True)
            st.button("Save to Talent Pool", use_container_width=True, disabled=True)
            st.caption("Actions will be activated progressively.")
