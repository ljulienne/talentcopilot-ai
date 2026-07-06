import streamlit as st

from talentcopilot.ai.reasoning_engine import ReasoningEngine
from talentcopilot.ai.interview_intelligence import InterviewIntelligenceEngine
from talentcopilot.ai.recommendation_engine import RecommendationEngine
from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceBuilder

from talentcopilot.ui.design_system.hero import render_hero
from talentcopilot.ui.design_system.metrics import metric_card
from talentcopilot.ui.design_system.cards import section_card, info_card, inject_card_styles
from talentcopilot.ui.design_system.timeline import horizontal_timeline


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


def render_decision_workspace():
    view_model = _build_demo_view_model()

    inject_card_styles()

    render_hero(
        title="Decision Workspace",
        subtitle="Evidence-based recruitment decision intelligence",
        icon="🧠",
        badge=view_model.recommendation,
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        metric_card(
            "Decision Confidence",
            f"{view_model.decision_confidence}%",
            "🎯",
            "Confidence in the recommendation",
            "#16A34A",
        )

    with col2:
        metric_card(
            "Decision Readiness",
            f"{view_model.decision_readiness}%",
            "🚀",
            "Ready for next step",
            "#2563EB",
        )

    with col3:
        demonstrated = len([
            s for s in view_model.reasoning_report.skill_assessment
            if s.status == "demonstrated"
        ])
        metric_card(
            "Demonstrated Skills",
            str(demonstrated),
            "✅",
            "Supported by evidence",
            "#7C3AED",
        )

    with col4:
        risks = len(view_model.reasoning_report.risks)
        metric_card(
            "Decision Risks",
            str(risks),
            "⚠️",
            "To validate before decision",
            "#F59E0B",
        )

    st.markdown("")

    left, right = st.columns([2, 1])

    with left:
        section_card(
            "Executive Summary",
            "📌",
            view_model.executive_summary,
        )

        st.markdown("### Decision Framework")
        horizontal_timeline(view_model.timeline)

        st.markdown("### Evidence Explorer")
        for evidence in view_model.reasoning_report.evidence_assessment[:4]:
            info_card(
                title=f"{evidence.strength.title()} evidence",
                body=f"{evidence.text}<br><br><strong>Interpretation:</strong> {evidence.interpretation}",
                icon="📎",
                color="#2563EB",
            )

        st.markdown("### Interview Intelligence")
        if view_model.interview_guide:
            st.info(view_model.interview_guide.interview_focus)

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
        section_card(
            "AI Recommendation",
            "✅",
            view_model.reasoning_report.recommendation_rationale,
        )

        section_card(
            "Challenge",
            "⚖️",
            view_model.recommendation_report.challenge,
        )

        st.markdown("### Actions")
        st.button("Compare Candidate", use_container_width=True, disabled=True)
        st.button("Generate Decision Report", use_container_width=True, disabled=True)
        st.button("Ask Copilot", use_container_width=True, disabled=True)
        st.button("Save to Talent Pool", use_container_width=True, disabled=True)

        st.caption("Actions will be activated progressively.")
