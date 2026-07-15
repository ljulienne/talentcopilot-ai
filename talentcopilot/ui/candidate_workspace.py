from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.services.candidate_intelligence import CandidateIntelligenceService
from talentcopilot.services.candidate_intelligence_view_service import (
    CandidateDecisionBrief,
    CandidateIntelligenceViewService,
)
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _render_skill_bars(report):
    import streamlit as st

    if not report.skills:
        st.info("No skills available.")
        return

    for skill in report.skills:
        st.write(f"**{skill.name}**")
        st.progress(max(0, min(100, skill.level)) / 100)
        if skill.evidence:
            st.caption(skill.evidence)


def _render_evidence(report):
    import streamlit as st

    if not report.evidence:
        st.info("No evidence available.")
        return

    for item in report.evidence:
        with st.expander(f"{item.title} · {item.strength}"):
            st.write(item.detail)


def _render_risks(report):
    import streamlit as st

    if not report.risks:
        st.success("No major risk detected in the current candidate report.")
        return

    for risk in report.risks:
        st.warning(f"**{risk.title}** — {risk.detail}")




def _render_list_section(
    title: str,
    items,
    *,
    empty_message: str,
    tone: str = "neutral",
) -> None:
    import streamlit as st

    st.markdown(f"#### {title}")

    values = list(items or [])
    if not values:
        st.info(empty_message)
        return

    for item in values:
        if tone == "positive":
            st.success(item)
        elif tone == "risk":
            st.warning(item)
        else:
            st.markdown(f"- {item}")


def _render_candidate_decision_brief(
    brief: CandidateDecisionBrief,
) -> None:
    import streamlit as st

    section_title(
        "Decision Brief",
        "A concise interpretation of the official candidate result. "
        "The score and rank below are read directly from the active recruitment session.",
    )

    metric_grid([
        (
            "Official Match",
            f"{brief.official_match_score:.0f}%",
            "Official session score",
        ),
        (
            "Official Rank",
            f"#{brief.official_rank}",
            "Official session ranking",
        ),
        (
            "AI Confidence",
            f"{brief.confidence_score}%",
            brief.confidence_label,
        ),
        (
            "Evidence Coverage",
            f"{brief.evidence_coverage}%",
            "Available evidence readiness",
        ),
    ])

    insight_card(
        brief.recommendation_label,
        brief.recommendation_explanation,
        brief.recommendation,
    )

    st.markdown("#### Executive interpretation")
    st.write(brief.executive_summary)

    strengths_col, transferable_col = st.columns(2)

    with strengths_col:
        _render_list_section(
            "Top strengths",
            brief.strengths,
            empty_message="No structured strength is available yet.",
            tone="positive",
        )

    with transferable_col:
        _render_list_section(
            "Transferable evidence",
            brief.transferable_evidence,
            empty_message=(
                "No transferable capability has been identified from the "
                "current structured profile."
            ),
        )

    gaps_col, risks_col = st.columns(2)

    with gaps_col:
        _render_list_section(
            "Missing or limited evidence",
            brief.missing_evidence,
            empty_message="No material evidence gap is currently documented.",
        )

    with risks_col:
        _render_list_section(
            "Hiring risks to validate",
            brief.hiring_risks,
            empty_message="No material risk is currently documented.",
            tone="risk",
        )

    _render_list_section(
        "Interview priorities",
        brief.interview_priorities,
        empty_message="No interview priority is currently available.",
    )

    st.markdown("#### Development signal — not a hiring decision")
    st.progress(
        max(0, min(100, brief.potential_signal)) / 100
    )
    st.caption(
        f"Potential signal: {brief.potential_signal}%. "
        "This indicator highlights possible development capacity from the "
        "available evidence. Potential signals do not evaluate a person's worth. "
        "They must not be used as an autonomous hiring, rejection, promotion, "
        "or compensation decision."
    )

    st.caption(
        f"{brief.evidence_summary} "
        "Potential and confidence indicators organise existing evidence only; "
        "they do not replace recruiter judgment or evaluate a person's worth."
    )



def render_candidate_workspace():
    import streamlit as st

    apply_enterprise_theme()

    session = get_streamlit_session()
    reports = CandidateWorkspaceService().build_all(session)

    enterprise_hero(
        "Candidate Intelligence",
        "Understand the official match, supporting evidence, uncertainties and interview priorities.",
        "Recruitment Decision Support",
    )

    if not reports:
        st.info("No active candidate analysis. Load the Enterprise Demo to populate this workspace.")
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            reports = CandidateWorkspaceService().build_all(session)
            st.success("Enterprise demo loaded.")

    if not reports:
        return

    candidate_names = [report.candidate_name for report in reports]
    selected_name = st.selectbox("Select candidate", candidate_names)
    report = reports[candidate_names.index(selected_name)]

    intelligence = CandidateIntelligenceService().build(report)
    decision_brief = CandidateIntelligenceViewService().build(
        report,
        intelligence,
    )

    section_title(
        report.candidate_name,
        f"Official candidate #{report.rank} in the active recruitment session.",
    )

    _render_candidate_decision_brief(decision_brief)

    tab_overview, tab_skills, tab_evidence, tab_risks, tab_interview = st.tabs([
        "Overview",
        "Skills",
        "Evidence",
        "Risks",
        "Interview Focus",
    ])

    with tab_overview:
        section_title("Candidate Overview")
        st.write(f"**Recommendation:** {report.recommendation}")
        st.write(f"**Match score:** {report.match_score:.0f}%")

    with tab_skills:
        section_title("Skills")
        _render_skill_bars(report)

    with tab_evidence:
        section_title("Evidence")
        _render_evidence(report)

    with tab_risks:
        section_title("Risks")
        _render_risks(report)

    with tab_interview:
        section_title("Interview Focus")
        if report.interview_focus:
            for item in report.interview_focus:
                st.write(f"- {item}")
        else:
            st.info("No interview focus generated yet.")
