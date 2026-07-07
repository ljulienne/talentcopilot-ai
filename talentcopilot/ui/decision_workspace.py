import streamlit as st

from talentcopilot.ai.reasoning_engine import ReasoningEngine
from talentcopilot.ai.interview_intelligence import InterviewIntelligenceEngine
from talentcopilot.ai.recommendation_engine import RecommendationEngine
from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceBuilder
from talentcopilot.services.session_manager import get_current_session


def _build_view_model_from_candidate(candidate, job_title):
    candidate_payload = {
        "name": candidate.name,
        "skills": candidate.skills,
        "years_experience": 0,
        "achievements": candidate.evidence,
    }

    job_payload = {
        "title": job_title,
        "required_skills": candidate.skills[:3],
        "preferred_skills": candidate.skills[3:6],
        "years_experience": 0,
    }

    evidence_payload = [{"text": item} for item in candidate.evidence]

    reasoning_report = ReasoningEngine().build_report(
        candidate=candidate_payload,
        job=job_payload,
        evidence=evidence_payload,
        match_result={"score": candidate.decision_confidence or candidate.score},
    )

    interview_guide = InterviewIntelligenceEngine().build_guide(reasoning_report)
    recommendation_report = RecommendationEngine().build_recommendation([reasoning_report])

    return DecisionWorkspaceBuilder().build(
        reasoning_report=reasoning_report,
        interview_guide=interview_guide,
        recommendation_report=recommendation_report,
    )


def _build_demo_view_model():
    from talentcopilot.ai.reasoning_engine import ReasoningEngine
    from talentcopilot.ai.interview_intelligence import InterviewIntelligenceEngine
    from talentcopilot.ai.recommendation_engine import RecommendationEngine
    from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceBuilder

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
    session = get_current_session()
    live_candidate = session.best_candidate

    if live_candidate:
        view_model = _build_view_model_from_candidate(
            candidate=live_candidate,
            job_title=session.job.title,
        )
        data_mode = "Live analysis"
    else:
        view_model = _build_demo_view_model()
        data_mode = "Demo mode"

    with st.container(border=True):
        st.caption(f"Decision Intelligence Workspace · {data_mode}")
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
            evidence_items = view_model.reasoning_report.evidence_assessment

            if evidence_items:
                for evidence in evidence_items[:4]:
                    with st.expander(
                        f"{evidence.strength.title()} evidence · {int(evidence.confidence_score * 100)}%",
                        expanded=False,
                    ):
                        st.write(f"“{evidence.text}”")
                        st.info(evidence.interpretation)
            else:
                st.info("No detailed evidence available yet.")

        with st.container(border=True):
            st.subheader("🧠 Competency Reasoning")

            arguments = getattr(view_model.reasoning_report, "competency_arguments", [])

            if arguments:
                for argument in arguments:
                    with st.expander(
                        f"{argument.competency} · {argument.conclusion} · {argument.confidence_score}%",
                        expanded=False,
                    ):
                        st.markdown("**Conclusion**")
                        st.write(argument.conclusion)

                        st.markdown("**Rationale**")
                        st.write(argument.rationale)

                        st.markdown("**Evidence**")
                        if argument.evidence:
                            for item in argument.evidence:
                                st.write(f"- {item}")
                        else:
                            st.caption("No direct evidence found.")

                        st.markdown("**Limitations**")
                        if argument.limitations:
                            for item in argument.limitations:
                                st.warning(item)
                        else:
                            st.success("No major limitation detected for this competency.")

                        st.markdown("**Interview validation**")
                        for question in argument.interview_validation:
                            st.write(f"- {question}")
            else:
                st.info("No competency reasoning available yet.")

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
