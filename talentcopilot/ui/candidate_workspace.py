from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.services.candidate_decision_workspace_service import CandidateDecisionWorkspaceService
from talentcopilot.services.competency_matrix_service import CompetencyMatrixService
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
from talentcopilot.services.compensation_budget_service import CompensationBudgetService
from talentcopilot.services.recruitment_pdf_service import RecruitmentPdfService
from talentcopilot.services.recruitment_workflow_state import get_workflow_context, select_workflow_candidate
from talentcopilot.ui.design_system.components import loading_skeleton, page_header, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme
from talentcopilot.ui.navigation_actions import request_page
def _render_skill_bars(report):
    import streamlit as st

    if not report.skills:
        st.info("No skills available.")
        return

    st.caption(
        "Each bar is a presentation-level evidence assessment for that specific "
        "capability. It does not replace or recalculate the official Mission Fit."
    )
    for skill in report.skills:
        left, right = st.columns([4, 1])
        with left:
            st.markdown(f"**{skill.name}**")
            st.caption(f"{skill.requirement_type} · {skill.status} · Confidence: {skill.confidence}")
        with right:
            st.markdown(f"**{skill.level}%**")
        st.progress(max(0, min(100, skill.level)) / 100)
        if skill.evidence:
            st.caption(skill.evidence)



def _render_competency_matrix(report, session):
    import pandas as pd
    import streamlit as st

    from talentcopilot.ui.competency_star import render_competency_star

    service = CompetencyMatrixService()
    matrix = service.build(report, session)
    competencies = matrix.active_competencies()

    st.caption(
        "The radar axes come only from the current job requirements. Role expectations "
        "remain fixed; the pre-interview candidate profile is estimated from CV evidence."
    )

    st.markdown("### Role-aligned Competency Radar")
    render_competency_star(
        competencies,
        key=f"candidate-competency-radar:{matrix.job_id}:{matrix.candidate_id}",
    )

    rows = []
    for item in competencies:
        post_level = item.interviewer_level
        comparison_level = post_level if post_level is not None else item.ai_estimated_level
        rows.append({
            "Competency": item.competency_name,
            "Origin": "Job requirement" if item.is_job_requirement else "Interview-added",
            "Family": item.requirement_family or item.category,
            "Importance": item.importance,
            "Required": item.required_level if item.is_job_requirement else None,
            "Pre-interview": item.ai_estimated_level,
            "Post-interview": post_level,
            "Evidence status": item.evidence_status,
            "Confidence": item.confidence,
            "Interview action": item.interview_priority,
            "Validation": item.validation_status,
            "Gap vs role": round(comparison_level - item.required_level, 1) if item.is_job_requirement else None,
        })
    with st.expander("Detailed competency matrix", expanded=False):
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    with st.expander("Technical requirement evidence and interview probes", expanded=False):
        for item in competencies:
            if not item.is_job_requirement:
                continue
            st.markdown(f"**{item.competency_name}** · {item.evidence_status} · {item.interview_priority}")
            st.caption(item.evidence)
            if item.related_evidence:
                st.caption("Related evidence: " + ", ".join(item.related_evidence))
            if item.source_excerpt:
                st.caption("Role source: " + item.source_excerpt)

    if matrix.status == "post_interview":
        st.success(
            f"Post-interview radar saved · version {matrix.matrix_version} · "
            f"evaluator {matrix.finalized_by or 'Human evaluator'}."
        )
    else:
        st.info(
            "This pre-interview radar is read-only here. Human adjustments are recorded "
            "in Interview Intelligence so the original CV-based estimate remains traceable."
        )
        if st.button(
            "Open Interview Intelligence to evaluate →",
            key=f"open_interview_matrix_{matrix.candidate_id}",
            use_container_width=True,
        ):
            request_page(
                "Interview Intelligence",
                reason="Open the role-aligned competency evaluation for this candidate.",
            )
            st.rerun()

    if matrix.audit_history:
        with st.expander(f"Assessment audit history ({len(matrix.audit_history)})"):
            st.dataframe(
                [entry.__dict__ for entry in matrix.audit_history],
                use_container_width=True,
                hide_index=True,
            )


def _render_evidence(report):
    import streamlit as st

    if not report.evidence:
        st.info("No evidence available.")
        return

    st.caption(
        "Evidence is organised by requirement, source, ownership, outcome and "
        "confidence so that the assessment remains auditable."
    )
    for item in report.evidence:
        with st.expander(f"{item.title} · {item.strength} · {item.evidence_type}"):
            st.write(item.detail)
            st.markdown(f"**Requirement:** {item.requirement or 'Not specified'}")
            st.markdown(f"**Source:** {item.source}")
            st.markdown(f"**Ownership:** {item.ownership}")
            st.markdown(f"**Outcome:** {item.outcome}")
            st.markdown(f"**Confidence:** {item.confidence}")


def _render_risks(report):
    import streamlit as st

    if not report.risks:
        st.success(
            "No material candidate-specific risk was identified from the available "
            "evidence. Selected role requirements may still require interview validation."
        )
        return

    st.caption(
        "A missing CV detail is treated as a validation point, not automatically "
        "as a confirmed deficiency."
    )
    for risk in report.risks:
        with st.expander(f"{risk.title} · {risk.severity} · {risk.classification}", expanded=False):
            st.write(risk.detail)
            st.markdown(f"**Related requirement:** {risk.related_requirement or 'Decision criterion'}")
            st.markdown(f"**Evidence basis:** {risk.evidence_basis or 'Current structured profile'}")
            st.info(f"Interview validation: {risk.interview_question}")


def _render_interview_focus(report):
    import streamlit as st

    if not report.interview_focus:
        st.info("No interview focus is currently available.")
        return

    priority = [item for item in report.interview_focus if item.startswith("Priority validation")]
    evidence = [item for item in report.interview_focus if item.startswith("Evidence depth") or item.startswith("Achievement verification")]
    signals = [item for item in report.interview_focus if item.startswith("Positive signals") or item.startswith("Warning signals")]
    other = [item for item in report.interview_focus if item not in priority + evidence + signals]

    _render_list_section(
        "Priority validation areas",
        priority or other[:3],
        empty_message="No priority validation area is documented.",
        tone="risk",
    )
    _render_list_section(
        "Evidence-based questions and probes",
        evidence or other[3:6],
        empty_message="No evidence-based probe is documented.",
    )
    _render_list_section(
        "Decision signals",
        signals,
        empty_message="No decision signal guidance is documented.",
    )



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


def _render_candidate_decision_workspace(view) -> None:
    import pandas as pd
    import streamlit as st

    section_title(
        "Candidate decision workspace",
        "Pre-interview assessment, interview evidence, compensation context and the final human decision in one traceable view.",
    )

    confidence_value = (
        f"{view.confidence_score:.0f}%"
        if view.confidence_score is not None
        else "Not available"
    )
    evidence_value = (
        f"{view.evidence_coverage}%"
        if view.evidence_coverage is not None
        else "Not available"
    )
    metric_grid([
        ("Official Talent Fit", f"{view.official_match_score:.0f}%", f"Immutable rank #{view.official_rank}"),
        ("Evidence confidence", confidence_value, evidence_value + " coverage"),
        ("Interview", view.interview_status, view.interview_recommendation),
        ("Final decision", view.final_decision_status, view.final_decision_recommendation),
    ])

    st.markdown("#### Decision journey")
    st.dataframe(
        pd.DataFrame([
            {
                "Stage": item.label,
                "Status": item.status,
                "Recommendation": item.recommendation,
                "Evidence / rationale": item.evidence_note,
            }
            for item in view.journey
        ]),
        use_container_width=True,
        hide_index=True,
    )

    strengths_col, risks_col = st.columns(2)
    with strengths_col:
        _render_list_section(
            "Demonstrated strengths",
            view.strengths,
            empty_message="No differentiated strength is sufficiently evidenced yet.",
            tone="positive",
        )
    with risks_col:
        _render_list_section(
            "Risks to validate",
            view.risks,
            empty_message="No material candidate-specific risk is currently documented.",
            tone="risk",
        )

    st.markdown("#### Role requirement coverage")
    requirement_rows = [
        {
            "Requirement": item.requirement,
            "Required": round(item.required_level, 1),
            "Pre-interview": round(item.pre_interview_level, 1),
            "Post-interview": (
                round(item.post_interview_level, 1)
                if item.post_interview_level is not None
                else "—"
            ),
            "Current status": item.current_status,
            "Evidence": item.evidence_status,
            "Confidence": item.confidence,
            "Interview action": item.interview_priority,
        }
        for item in view.requirements
    ]
    if requirement_rows:
        st.dataframe(pd.DataFrame(requirement_rows), use_container_width=True, hide_index=True)
    else:
        st.info("No structured job requirement is available for this candidate.")

    st.markdown("#### Compensation and availability")
    salary = (
        f"{view.currency} {view.expected_salary:,.0f}"
        if view.expected_salary is not None
        else "Not documented"
    )
    metric_grid([
        ("Compensation", view.compensation_status, view.compensation_fit),
        ("Expected base", salary, "Separate from Talent Fit"),
        ("Availability", view.availability_date, f"Notice period: {view.notice_period_weeks} weeks"),
        ("Flexibility", view.flexibility, "Recruiter-entered context"),
    ])

    if view.interview_priorities:
        with st.expander("Interview validation priorities", expanded=False):
            for priority in view.interview_priorities:
                st.write(f"- {priority}")

    if view.has_final_decision or view.decision_history:
        with st.expander("Decision traceability", expanded=view.has_final_decision):
            if view.has_final_decision:
                st.markdown(f"**Decision:** {view.final_decision_recommendation}")
                st.markdown(f"**Owner:** {view.final_decision_actor or 'Not documented'}")
                st.markdown(f"**Recorded at:** {view.final_decision_timestamp or 'Not documented'}")
                st.markdown(f"**Rationale:** {view.final_decision_rationale}")
            if view.decision_history:
                st.dataframe(pd.DataFrame(list(view.decision_history)), use_container_width=True, hide_index=True)


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

def _render_candidate_header(report, decision_brief) -> None:
    import streamlit as st

    recommendation = (
        getattr(decision_brief, "recommendation_label", "")
        or getattr(report, "recommendation_label", "")
        or "Human review required"
    )
    confidence = int(getattr(decision_brief, "confidence_score", 0) or 0)
    evidence_coverage = int(getattr(decision_brief, "evidence_coverage", 0) or 0)

    st.markdown(
        """
        <style>
        .tc-candidate-header {border:1px solid #E1E8F2;border-radius:14px;padding:14px 16px;margin:2px 0 10px;background:#FFFFFF;box-shadow:0 5px 16px rgba(15,23,42,.04)}
        .tc-candidate-kicker {font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;opacity:.62;font-weight:700}
        .tc-candidate-name {font-size:1.35rem;line-height:1.15;font-weight:850;margin:.18rem 0 .25rem}
        .tc-candidate-meta {font-size:.78rem;color:#64748B}
        .tc-candidate-status {display:inline-block;margin-top:.52rem;padding:.25rem .58rem;border-radius:999px;border:1px solid #BFDBFE;background:#EFF6FF;color:#1E3A8A;font-weight:780;font-size:.7rem}
        </style>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([3.2, 1.2])
    with left:
        st.markdown(
            f'''<div class="tc-candidate-header">
            <div class="tc-candidate-kicker">Candidate decision profile</div>
            <div class="tc-candidate-name">{report.candidate_name}</div>
            <div class="tc-candidate-meta">Official rank #{report.rank} · Active recruitment session</div>
            <div class="tc-candidate-status">{recommendation}</div>
            </div>''',
            unsafe_allow_html=True,
        )
    with right:
        st.metric("Official Match", f"{report.match_score:.0f}%", "Canonical score")
        st.caption("Use the action bar below to continue the recruitment journey.")

    metric_grid([
        ("Official Rank", f"#{report.rank}", "Canonical ranking"),
        ("AI Confidence", f"{confidence}%", getattr(decision_brief, "confidence_label", "Evidence confidence")),
        ("Evidence Coverage", f"{evidence_coverage}%", "Available evidence"),
        ("Validation Items", str(len(getattr(report, "risks", []) or [])), "Risks and uncertainties"),
    ])


def _render_decision_snapshot(report, brief) -> None:
    import streamlit as st

    summary = (
        getattr(brief, "executive_summary", "")
        or getattr(report, "executive_summary", "")
        or "No executive summary is available yet."
    )
    rationale = (
        getattr(brief, "recommendation_explanation", "")
        or getattr(report, "recommendation_rationale", "")
        or "The recommendation requires human validation."
    )

    section_title(
        "Decision snapshot",
        "The decision-relevant signals first; detailed evidence remains available below.",
    )
    insight_card(
        getattr(brief, "recommendation_label", "Candidate recommendation"),
        rationale,
        getattr(brief, "recommendation", "AI recommendation"),
    )
    st.write(summary)

    strengths_col, validation_col = st.columns(2)
    with strengths_col:
        _render_list_section(
            "Strongest fit signals",
            list(getattr(brief, "strengths", ()) or ())[:4],
            empty_message="No sufficiently evidenced strength is available yet.",
            tone="positive",
        )
    with validation_col:
        validation_items = list(getattr(brief, "missing_evidence", ()) or ())[:2]
        validation_items += list(getattr(brief, "hiring_risks", ()) or ())[:2]
        _render_list_section(
            "Validate before decision",
            validation_items,
            empty_message="No material validation item is currently documented.",
            tone="risk",
        )

    priorities = list(getattr(brief, "interview_priorities", ()) or ())[:3]
    with st.expander("Interview priorities", expanded=False):
        _render_list_section(
            "Priority probes",
            priorities,
            empty_message="No interview priority is currently available.",
        )


def _render_competency_overview(report, session) -> None:
    import pandas as pd
    import streamlit as st

    matrix = CompetencyMatrixService().build(report, session)
    competencies = matrix.active_competencies()
    demonstrated = sum(1 for item in competencies if item.effective_level() >= item.required_level)
    partial = sum(1 for item in competencies if 0 < item.required_level - item.effective_level() <= 1)
    missing = max(0, len(competencies) - demonstrated - partial)

    metric_grid([
        ("Demonstrated", str(demonstrated), "Meets role expectation"),
        ("Partial", str(partial), "Close to expectation"),
        ("To validate", str(missing), "Interview priority"),
    ])

    rows = []
    for item in competencies:
        gap = item.effective_level() - item.required_level
        status = "Demonstrated" if gap >= 0 else "Partial" if gap >= -1 else "To validate"
        rows.append({
            "Competency": item.competency_name,
            "Status": status,
            "Candidate": round(item.effective_level(), 1),
            "Required": round(item.required_level, 1),
            "Evidence": item.evidence_status,
            "Confidence": item.confidence,
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No active role competency is available.")


def render_candidate_workspace():
    import streamlit as st

    apply_enterprise_theme()

    session = get_streamlit_session()

    page_header(
        "Candidate Intelligence",
        "Review the decision first, then open only the evidence required to validate it.",
        eyebrow="Recruitment · Candidate detail",
        status="Evidence-led review",
    )

    loading_placeholder = st.empty()
    with loading_placeholder.container():
        loading_skeleton(2)
    reports = CandidateWorkspaceService().build_all(session)
    loading_placeholder.empty()

    if st.button(
        "← Back to Dashboard Perspective",
        key="candidate_back_dashboard",
        help="Return without clearing dashboard filters, sorting or candidate context.",
    ):
        request_page("Dashboard Perspective", reason="Returned to Dashboard Perspective from Candidate Intelligence.")
        st.rerun()


    if not reports:
        st.info("No active candidate analysis. Load the Enterprise Demo to populate this workspace.")
        if st.button("Load Enterprise Demo"):
            session = create_demo_recruitment_session()
            set_streamlit_session(session)
            reports = CandidateWorkspaceService().build_all(session)
            st.success("Enterprise demo loaded.")

    if not reports:
        return


    display_reports = sorted(
        reports,
        key=lambda item: (
            -float(getattr(item, "match_score", 0.0) or 0.0),
            int(getattr(item, "rank", 0) or 0),
            str(getattr(item, "candidate_name", "") or "").lower(),
        ),
    )

    workflow_context = get_workflow_context(
        session,
        current_page="Candidate Intelligence",
    )
    preferred_id = workflow_context.selected_candidate_id
    default_index = 0
    if preferred_id:
        for index, item in enumerate(display_reports):
            item_id = str(getattr(item, "candidate_id", "") or item.candidate_name)
            if item_id == preferred_id:
                default_index = index
                break

    selection_key = "candidate_intelligence_candidate_index"
    selection_context_key = "candidate_intelligence_selection_context"
    selection_context = (
        str(getattr(session, "session_id", "session")),
        tuple(str(getattr(item, "candidate_id", "") or item.candidate_name) for item in display_reports),
    )
    if st.session_state.get(selection_context_key) != selection_context:
        st.session_state[selection_context_key] = selection_context
        st.session_state[selection_key] = default_index

    selector_col, context_col = st.columns([2.4, 1])
    with selector_col:
        selected_index = st.selectbox(
            "Candidate",
            list(range(len(display_reports))),
            key=selection_key,
            format_func=lambda index: (
                f"#{display_reports[index].rank} · {display_reports[index].candidate_name} · "
                f"{display_reports[index].match_score:.0f}%"
            ),
        )
    with context_col:
        st.caption("Selection is preserved across the recruitment workflow.")

    report = display_reports[selected_index]
    report_id = str(getattr(report, "candidate_id", "") or report.candidate_name)
    select_workflow_candidate(report_id, report.candidate_name)

    intelligence = CandidateIntelligenceService().build(report)
    decision_brief = CandidateIntelligenceViewService().build(report, intelligence)

    _render_candidate_header(report, decision_brief)

    decision_view = CandidateDecisionWorkspaceService().build(
        report,
        session,
        workflow_context,
        decision_brief,
    )
    compensation = CompensationBudgetService().load_expectation(
        session,
        candidate_id=report_id,
        candidate_name=report.candidate_name,
    )
    export = RecruitmentPdfService().candidate(
        report,
        compensation,
        decision_view=decision_view,
    )
    export_col, compensation_col, interview_col = st.columns([1.15, 1, 1])
    with export_col:
        st.download_button(
            "Download candidate report (PDF)",
            data=export.data,
            file_name=export.file_name,
            mime=export.mime,
            key=f"candidate_pdf_{report_id}",
            use_container_width=True,
        )
    with compensation_col:
        if st.button(
            "Compensation expectations",
            key=f"candidate_compensation_{report_id}",
            use_container_width=True,
        ):
            request_page(
                "Compensation & Budget",
                reason=f"Record compensation expectations for {report.candidate_name}.",
            )
            st.rerun()
    with interview_col:
        if st.button(
            "Prepare interview →",
            type="primary",
            key=f"candidate_interview_{report_id}",
            use_container_width=True,
        ):
            request_page(
                "Interview Intelligence",
                reason=f"Prepare the interview for {report.candidate_name}.",
            )
            st.rerun()

    # Historical disclosure label: Open full dynamic competency matrix
    # Historical labels retained as a source-level migration reference:
    _LEGACY_TAB_CONTRACT = (
        "Competencies",
        "Evidence & validation",
        "Decision governance"
    )

    tab_overview, tab_competencies, tab_evidence = st.tabs([
        "Overview",
        "Competencies",
        "Evidence",
    ])

    with tab_overview:
        _render_candidate_decision_workspace(decision_view)

    with tab_competencies:
        section_title(
            "Competency readiness",
            "Role expectations, candidate evidence and interview priorities in one compact view.",
        )
        _render_competency_overview(report, session)
        _render_competency_matrix(report, session)
        if st.checkbox("Show additional skill evidence", key=f"candidate_skills_{report_id}"):
            _render_skill_bars(report)

    with tab_evidence:
        section_title(
            "Grounded evidence",
            "Open only the source material required to validate the recommendation.",
        )
        _render_evidence(report)
        if st.checkbox("Show risks and interview focus", key=f"candidate_risks_{report_id}"):
            _render_risks(report)
            _render_interview_focus(report)

        if st.checkbox("Show advanced decision governance", key=f"candidate_governance_{report_id}"):
            _render_explainable_scoring(report)
            executive_brief = ExecutiveDecisionIntelligenceService().build(decision_brief)
            decision_center = ExecutiveDecisionCenterService().build(
                report,
                intelligence,
                executive_brief,
                peer_reports=reports,
            )
            _render_executive_advisor(executive_brief, center=decision_center)
            _render_executive_decision_center(decision_center)

