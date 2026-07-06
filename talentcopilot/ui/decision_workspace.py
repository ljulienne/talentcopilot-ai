import streamlit as st

from talentcopilot.ai.reasoning_engine import ReasoningEngine
from talentcopilot.ai.interview_intelligence import InterviewIntelligenceEngine
from talentcopilot.ai.recommendation_engine import RecommendationEngine
from talentcopilot.viewmodels.decision_workspace import DecisionWorkspaceBuilder

from talentcopilot.ui.components.decision.header import render_decision_header
from talentcopilot.ui.components.decision.timeline import render_decision_timeline
from talentcopilot.ui.components.decision.summary import render_executive_summary
from talentcopilot.ui.components.decision.metrics import render_decision_metrics
from talentcopilot.ui.components.decision.recommendation import render_recommendation_panel
from talentcopilot.ui.components.decision.interview import render_interview_panel
from talentcopilot.ui.components.decision.actions import render_decision_actions


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
    st.title("Decision Workspace")
    st.caption("Evidence-based recruitment decision intelligence")

    view_model = _build_demo_view_model()

    render_decision_header(view_model)

    st.divider()

    render_executive_summary(view_model)

    st.divider()

    render_decision_metrics(view_model)

    st.divider()

    render_decision_timeline(view_model)

    st.divider()

    render_recommendation_panel(view_model)

    st.divider()

    render_interview_panel(view_model)

    st.divider()

    render_decision_actions()
