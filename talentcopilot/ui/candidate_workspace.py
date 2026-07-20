from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.explainable_scoring import ExplainableScoringService
from talentcopilot.services.candidate_intelligence import CandidateIntelligenceService
from talentcopilot.services.candidate_intelligence_view_service import (
    CandidateDecisionBrief,
    CandidateIntelligenceViewService,
)
from talentcopilot.services.executive_decision_intelligence_service import (
    ExecutiveDecisionIntelligenceService,
)
from talentcopilot.services.executive_decision_pdf_service import (
    ExecutiveDecisionPdfService,
)
from talentcopilot.services.executive_decision_center_service import (
    ExecutiveDecisionCenterService,
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




def _render_executive_advisor(brief, center=None) -> None:
    import streamlit as st

    section_title(
        "AI Executive Advisor",
        "A decision-ready interpretation of canonical candidate results. Official Match and rank are never recalculated here.",
    )

    metric_grid([
        ("Recommendation", brief.recommendation, brief.decision_status),
        ("Business Impact", brief.business_impact, "Expected contribution signal"),
        ("Expected Ramp-up", brief.ramp_up, brief.ramp_up_rationale),
        ("AI Confidence", f"{brief.ai_confidence}%", "Canonical confidence"),
    ])

    insight_card(
        "Executive interpretation",
        brief.executive_narrative,
        brief.recommendation,
    )

    strengths_col, action_col = st.columns(2)
    with strengths_col:
        _render_list_section(
            "Why this candidate",
            brief.strengths,
            empty_message="No decisive strength is documented yet.",
            tone="positive",
        )
    with action_col:
        st.markdown("#### Recommended next action")
        st.info(brief.next_action)

    st.markdown("#### Hiring Risk Matrix")
    risk_rows = [
        {
            "Dimension": risk.name,
            "Risk": risk.level,
            "Rationale": risk.rationale,
        }
        for risk in brief.risks
    ]
    st.dataframe(risk_rows, use_container_width=True, hide_index=True)

    _render_list_section(
        "Priority interview topics",
        brief.interview_priorities,
        empty_message="No interview priority is currently available.",
    )

    pdf_bytes = ExecutiveDecisionPdfService().generate(brief, center=center)
    st.download_button(
        "Download Executive Decision Brief (PDF)",
        data=pdf_bytes,
        file_name=f"executive_decision_{brief.candidate_id or 'candidate'}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )
    st.caption(brief.governance_note)



def _render_executive_decision_center(center) -> None:
    import streamlit as st

    section_title(
        "Executive Decision Center",
        "Evaluate whether the hiring decision is sufficiently documented, not whether the candidate is inherently good or bad.",
    )

    metric_grid([
        ("Decision Readiness", f"{center.decision_readiness}%", center.readiness_label),
        ("Official Match", f"{center.official_match_score:.0f}%", "Unchanged canonical score"),
        ("Official Rank", f"#{center.official_rank}", "Unchanged canonical rank"),
        ("AI Confidence", f"{center.ai_confidence}%", "Unchanged canonical confidence"),
    ])

    st.progress(max(0, min(100, center.decision_readiness)) / 100)
    insight_card("Executive decision summary", center.executive_summary, center.recommendation)

    readiness_col, confidence_col = st.columns(2)
    with readiness_col:
        st.markdown("#### Decision readiness gaps")
        if center.readiness_gaps:
            for gap in center.readiness_gaps:
                st.warning(f"**{gap.label} — {gap.status}**\n\n{gap.rationale}")
        else:
            st.success("No material decision-readiness gap is documented.")
    with confidence_col:
        _render_list_section(
            "Why confidence is at this level",
            center.confidence_reasons,
            empty_message="No confidence explanation is available.",
        )

    st.markdown("#### Evidence Quality")
    st.dataframe(
        [
            {"Evidence": item.label, "Quality": item.quality, "Rationale": item.rationale}
            for item in center.evidence_quality
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("#### Executive Timeline")
    for milestone in center.timeline:
        st.markdown(f"**{milestone.period}** — {milestone.objective}")

    if center.comparison:
        st.markdown("#### What changes versus other candidates?")
        for peer in center.comparison:
            with st.expander(peer.headline):
                _render_list_section(
                    "Relative strengths",
                    peer.strengths,
                    empty_message="No relative strength is documented.",
                    tone="positive",
                )
                _render_list_section(
                    "Trade-offs",
                    peer.trade_offs,
                    empty_message="No material trade-off is documented.",
                    tone="risk",
                )

    st.caption(center.governance_note)



def _render_explainable_scoring(report) -> None:
    import streamlit as st

    explanation = ExplainableScoringService().build(report)
    section_title(
        "Explainable Mission Fit",
        "Every contribution reconciles to the immutable official Mission Fit; this view never creates a second score.",
    )
    metric_grid([
        ("Official Mission Fit", f"{explanation.mission_fit:.0f}%", "Canonical RecruitmentSession score"),
        ("Reconstructed total", f"{explanation.reconstructed_score:.0f}%", "Traceability control"),
        ("Confidence", f"{explanation.confidence:.0f}%", "Evidence confidence"),
        ("Engine", explanation.engine_version, "Explanation layer only"),
    ])
    st.write(explanation.rationale)
    st.dataframe(
        [
            {
                "Dimension": item.label,
                "Score": f"{item.score:.0f}%",
                "Weight": f"{item.weight:.0%}",
                "Contribution": f"{item.contribution:.1f} pts",
                "Status": item.status,
            }
            for item in explanation.dimensions
        ],
        use_container_width=True,
        hide_index=True,
    )
    left, right = st.columns(2)
    with left:
        _render_list_section(
            "Positive contributions",
            [item.detail for item in explanation.positive_contributions],
            empty_message="No dimension-level positive contribution is available yet.",
            tone="positive",
        )
    with right:
        _render_list_section(
            "Evidence gaps / penalties",
            [item.detail for item in explanation.penalties],
            empty_message="No material weighted gap is currently documented.",
            tone="risk",
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

    # Candidate Intelligence displays the official Mission Fit percentage.
    # Therefore, the selector is ordered by that same visible score.
    # This is presentation logic only: it does not mutate the RecruitmentSession,
    # official ranking, Decision Rank, or Source of Truth.
    display_reports = sorted(
        reports,
        key=lambda item: (
            -float(getattr(item, "match_score", 0.0) or 0.0),
            int(getattr(item, "rank", 0) or 0),
            str(getattr(item, "candidate_name", "") or "").lower(),
        ),
    )

    candidate_options = list(range(len(display_reports)))

    selected_index = st.selectbox(
        "Select candidate",
        candidate_options,
        format_func=lambda index: (
            f"{display_reports[index].candidate_name} · "
            f"{display_reports[index].match_score:.0f}%"
        ),
    )

    report = display_reports[selected_index]

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
    _render_explainable_scoring(report)

    executive_brief = ExecutiveDecisionIntelligenceService().build(
        decision_brief
    )
    decision_center = ExecutiveDecisionCenterService().build(
        report,
        intelligence,
        executive_brief,
        peer_reports=reports,
    )
    _render_executive_advisor(executive_brief, center=decision_center)
    _render_executive_decision_center(decision_center)

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
