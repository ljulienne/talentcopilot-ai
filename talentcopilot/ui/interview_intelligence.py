from __future__ import annotations

from talentcopilot.interview.pro_service import InterviewIntelligenceProService
from talentcopilot.interview.question_service import InterviewQuestionService
from talentcopilot.interview.workspace_service import InterviewWorkspaceService
from talentcopilot.services.interview_report_pdf_service import InterviewReportPdfService
from talentcopilot.services.recruitment_pdf_service import RecruitmentPdfService
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session
from talentcopilot.services.candidate_ordering import sort_by_official_rank
from talentcopilot.services.recruitment_workflow_state import (
    get_workflow_context,
    save_interview_evaluation,
    save_workflow_context,
    select_workflow_candidate,
    set_workflow_finalists,
)
from talentcopilot.ui.navigation_actions import request_page
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


CACHE_PREFIX = "interview_strategy_"
OUTCOME_PREFIX = "interview_outcome_"


def _cache_key(session, report) -> str:
    session_id = str(getattr(session, "session_id", "session"))
    candidate_id = ""
    for analysis in getattr(session, "ranked_analyses", []) or []:
        if analysis.candidate_name == report.candidate_name:
            candidate_id = str(getattr(analysis, "candidate_id", ""))
            break
    return (
        f"{CACHE_PREFIX}{session_id}:{candidate_id or report.candidate_name}:"
        f"{report.fit_score:.4f}:{InterviewQuestionService.ENGINE_VERSION}"
    )


def _render_strategy(report, questions):
    import streamlit as st

    section_title("Interview objectives")
    for gap in report.readiness.gaps:
        st.warning(gap)
    if not report.readiness.gaps:
        st.success("No major pre-interview gap was detected. Use the interview to validate depth and ownership.")

    section_title("Evidence validation matrix")
    rows = [
        {
            "Competency": item.name,
            "Evidence": item.evidence_level,
            "Confidence": f"{item.confidence}%",
            "Interview priority": "Validate" if item.validate_in_interview else "Confirm",
            "Why": item.rationale,
        }
        for item in report.competencies
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    section_title("Targeted interview playbook")
    for index, question in enumerate(questions, start=1):
        with st.expander(f"{index}. {question.competency}", expanded=index == 1):
            st.markdown(f"**Question**  \n{question.question}")
            st.markdown(f"**Hypothesis tested / why it matters**  \n{question.objective}")
            st.markdown("**A strong answer should include**")
            for item in question.expected_evidence:
                st.write(f"- {item}")
            st.markdown("**Positive signals**")
            for item in question.positive_signals:
                st.write(f"- {item}")
            st.markdown("**Warning signals**")
            for item in question.warning_signals:
                st.write(f"- {item}")
            st.markdown("**Follow-up probes**")
            for item in question.follow_ups:
                st.write(f"- {item}")


def _resolve_candidate_competency_matrix(session, candidate_id: str):
    from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
    from talentcopilot.services.competency_matrix_service import CompetencyMatrixService

    candidate_reports = CandidateWorkspaceService().build_all(session)
    candidate_report = next(
        (
            item
            for item in candidate_reports
            if str(getattr(item, "candidate_id", "") or item.candidate_name)
            == str(candidate_id)
        ),
        None,
    )
    if candidate_report is None:
        return None, CompetencyMatrixService()
    service = CompetencyMatrixService()
    return service.build(candidate_report, session), service


def _render_live_evaluation(session, report, candidate_id: str):
    import streamlit as st

    from talentcopilot.ui.competency_star import render_competency_star

    interview_service = InterviewIntelligenceProService()
    matrix, matrix_service = _resolve_candidate_competency_matrix(session, candidate_id)
    if matrix is None:
        st.error("The role-aligned competency matrix could not be built for this candidate.")
        return

    candidate_key = f"{getattr(session, 'session_id', 'session')}:{candidate_id or report.candidate_name}"
    outcome_key = f"{OUTCOME_PREFIX}{candidate_key}"
    evaluator = st.text_input(
        "Evaluator",
        value=matrix.finalized_by or "Recruiter",
        key=f"competency-evaluator:{candidate_key}",
    )

    section_title("Role-aligned competency evaluation")
    st.caption(
        "The role expectations come from the job description and remain fixed. "
        "Adjust only the candidate assessment, capture supporting evidence, and save "
        "a versioned post-interview radar. Official fit and rank are never recalculated."
    )

    competency_star_slot = st.empty()
    live_assessments = []
    ratings = []
    updates = {}

    active_competencies = matrix.active_competencies()
    if not active_competencies:
        st.warning("No active role competency is available for this interview.")
        return

    for index, competency in enumerate(active_competencies):
        safe_key = f"{candidate_key}:{competency.competency_id}:{index}"
        origin_label = "Job requirement" if competency.is_job_requirement else "Interview-added"
        with st.expander(
            f"{competency.competency_name} · {origin_label}",
            expanded=index == 0,
        ):
            if competency.is_job_requirement:
                st.caption(
                    f"Required {competency.required_level:.1f}/5 · "
                    f"Pre-interview estimate {competency.ai_estimated_level:.1f}/5 · "
                    f"Confidence {competency.confidence}"
                )
                st.caption(
                    f"{competency.evidence_status} · Interview action: {competency.interview_priority}"
                )
                st.caption(competency.evidence)
                if competency.related_evidence:
                    st.caption("Related evidence: " + ", ".join(competency.related_evidence))
                if competency.source_excerpt:
                    st.caption("Role source: " + competency.source_excerpt)
            else:
                renamed = st.text_input(
                    "Competency name",
                    value=competency.competency_name,
                    key=f"rename:{safe_key}",
                )
                rename_col, archive_col = st.columns(2)
                with rename_col:
                    if st.button("Rename competency", key=f"rename-button:{safe_key}"):
                        try:
                            if matrix_service.rename_competency(
                                matrix,
                                competency.competency_id,
                                renamed,
                                evaluator=evaluator,
                            ):
                                st.success("Competency renamed.")
                                st.rerun()
                        except ValueError as exc:
                            st.error(str(exc))
                with archive_col:
                    if st.button("Remove competency", key=f"archive-button:{safe_key}"):
                        matrix_service.remove_competency(
                            matrix,
                            competency.competency_id,
                            evaluator=evaluator,
                            reason="Removed by the evaluator during the interview.",
                        )
                        st.success("Interview-added competency removed from the active radar.")
                        st.rerun()

            answer = st.text_area(
                "Candidate answer / evidence",
                value=competency.interview_evidence,
                key=f"answer:{safe_key}",
                height=120,
                placeholder="Capture context, personal responsibility, actions, results and measurable evidence…",
            )
            col1, col2 = st.columns(2)
            with col1:
                default_level = (
                    competency.interviewer_level
                    if competency.interviewer_level is not None
                    else competency.ai_estimated_level
                )
                recruiter_score = st.slider(
                    "Evaluator level",
                    min_value=0.0,
                    max_value=5.0,
                    value=float(max(0.0, min(5.0, default_level))),
                    step=0.1,
                    key=f"rating:{safe_key}",
                )
            with col2:
                statuses = list(matrix_service.VALIDATION_STATUSES)
                current_status = (
                    competency.validation_status
                    if competency.validation_status in statuses
                    else "To validate"
                )
                validation_status = st.selectbox(
                    "Validation status",
                    statuses,
                    index=statuses.index(current_status),
                    key=f"status:{safe_key}",
                )

            notes = st.text_area(
                "Evaluator notes",
                value=competency.comment,
                key=f"notes:{safe_key}",
                height=80,
                placeholder="Decision-relevant evidence or remaining uncertainty",
            )
            confirmed = validation_status == "Confirmed"

            star = interview_service.assess_star(answer)
            if answer.strip():
                st.progress(
                    star.completeness_score / 100,
                    text=f"STAR evidence completeness: {star.completeness_score}%",
                )
                st.caption(star.evidence_summary)
                follow_ups = interview_service.suggest_follow_ups(
                    star, competency.competency_name
                )
                if follow_ups:
                    st.markdown("**Suggested follow-up questions**")
                    for prompt in follow_ups:
                        st.write(f"- {prompt}")
                else:
                    st.success("The answer covers the expected STAR and evidence dimensions.")
            else:
                st.caption(
                    "STAR evidence completeness: not assessed — capture the candidate's "
                    "answer or interview evidence to calculate it."
                )

            live_assessments.append(
                {
                    "competency": competency.competency_name,
                    "score": recruiter_score,
                    "evidence_confirmed": confirmed,
                    "answer": answer,
                    "notes": notes,
                }
            )
            ratings.append(
                interview_service.build_rating(
                    competency=competency.competency_name,
                    answer=answer,
                    recruiter_score=max(1, min(5, round(recruiter_score))),
                    evidence_confirmed=confirmed,
                    notes=notes or answer,
                )
            )
            updates[competency.competency_id] = {
                "interviewer_level": recruiter_score,
                "validation_status": validation_status,
                "comment": notes,
                "interview_evidence": answer,
            }

    with competency_star_slot.container():
        st.markdown("### Competency Star — role-aligned radar")
        render_competency_star(
            matrix.active_competencies(),
            live_assessments=live_assessments,
            key=f"competency-star:{candidate_key}",
        )

    with st.expander("Add a competency discovered during the interview", expanded=False):
        new_name = st.text_input(
            "New competency",
            key=f"new-competency:{candidate_key}",
            placeholder="Example: Vendor Management",
        )
        new_level = st.slider(
            "Initial evaluator level",
            0.0,
            5.0,
            3.0,
            0.1,
            key=f"new-level:{candidate_key}",
        )
        new_comment = st.text_area(
            "Why is it relevant?",
            key=f"new-comment:{candidate_key}",
            placeholder="Evidence observed during the interview",
        )
        if st.button("Add to competency radar", key=f"add-competency:{candidate_key}"):
            try:
                matrix_service.add_competency(
                    matrix,
                    new_name,
                    evaluator=evaluator,
                    interviewer_level=new_level,
                    comment=new_comment,
                )
                st.success("Competency added to the interview radar.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))

    save_col, final_col = st.columns(2)
    with save_col:
        if st.button(
            "Save interview draft",
            key=f"save-draft:{candidate_key}",
            use_container_width=True,
        ):
            matrix_service.update(
                matrix,
                updates,
                evaluator=evaluator,
                rationale="Live interview competency assessment",
                status="interview_in_progress",
            )
            st.success(f"Interview competency draft saved · version {matrix.matrix_version}.")

    with final_col:
        if st.button(
            "Generate post-interview recommendation & save radar",
            type="primary",
            key=f"evaluate:{candidate_key}",
            use_container_width=True,
        ):
            matrix_service.update(
                matrix,
                updates,
                evaluator=evaluator,
                rationale="Final interview competency assessment",
                status="interview_in_progress",
            )
            matrix_service.finalize(matrix, evaluator=evaluator)
            outcome = interview_service.evaluate(report.candidate_name, ratings)
            st.session_state[outcome_key] = outcome
            save_interview_evaluation(
                candidate_id,
                {
                    "candidate_id": candidate_id,
                    "candidate_name": report.candidate_name,
                    "recommendation": outcome.recommendation.label,
                    "overall_score": outcome.overall_score,
                    "evidence_coverage": outcome.evidence_coverage,
                    "confidence": outcome.recommendation.confidence,
                    "rationale": list(outcome.recommendation.rationale),
                    "remaining_risks": list(outcome.recommendation.remaining_risks),
                    "next_step": outcome.recommendation.next_step,
                    "competency_matrix_version": matrix.matrix_version,
                    "competency_matrix_status": matrix.status,
                    "post_interview_radar": [
                        {
                            "competency_id": item.competency_id,
                            "competency": item.competency_name,
                            "origin": item.origin,
                            "required_level": item.required_level,
                            "pre_interview_level": item.ai_estimated_level,
                            "post_interview_level": item.interviewer_level,
                            "validation_status": item.validation_status,
                            "comment": item.comment,
                            "interview_evidence": item.interview_evidence,
                        }
                        for item in matrix.active_competencies()
                    ],
                },
            )
            st.success(
                f"Post-interview competency radar saved · version {matrix.matrix_version}."
            )

    archived = [item for item in matrix.competencies if not item.is_active]
    if archived:
        with st.expander(f"Removed interview-added competencies ({len(archived)})"):
            for item in archived:
                st.write(f"**{item.competency_name}** — {item.removed_reason or 'Archived'}")
                if not item.is_job_requirement and st.button(
                    f"Restore {item.competency_name}",
                    key=f"restore:{candidate_key}:{item.competency_id}",
                ):
                    matrix_service.restore_competency(
                        matrix,
                        item.competency_id,
                        evaluator=evaluator,
                    )
                    st.rerun()

    outcome = st.session_state.get(outcome_key)
    if outcome is None:
        return

    section_title("Post-interview decision support")
    metric_grid([
        ("Recommendation", outcome.recommendation.label, "Based only on captured interview evidence"),
        ("Interview score", f"{outcome.overall_score:.2f}/5", "Evaluator scorecard average"),
        ("Evidence coverage", f"{outcome.evidence_coverage}%", "Competencies explicitly confirmed"),
        ("Recommendation confidence", f"{outcome.recommendation.confidence}%", "Evidence and STAR completeness"),
    ])

    insight_card(
        "Executive interview summary",
        interview_service.build_executive_summary(outcome),
        "Explainable recommendation",
    )

    st.markdown("**Decision rationale**")
    for item in outcome.recommendation.rationale:
        st.write(f"- {item}")

    st.markdown("**Remaining risks and missing evidence**")
    if outcome.recommendation.remaining_risks:
        for item in outcome.recommendation.remaining_risks:
            st.warning(item)
    else:
        st.success("No material interview evidence gap remains.")

    st.info(f"Recommended next step: {outcome.recommendation.next_step}")

    workflow_context = get_workflow_context(session, current_page="Interview Intelligence")
    default_finalists = list(workflow_context.finalist_candidate_ids or workflow_context.shortlisted_candidate_ids)
    if candidate_id not in default_finalists:
        default_finalists.append(candidate_id)
    if st.button(
        "Save assessment and compare →",
        type="primary",
        key=f"compare:{candidate_key}",
        use_container_width=True,
    ):
        set_workflow_finalists(default_finalists)
        request_page("Comparison", reason="Interview assessment saved. Review the finalist comparison.")
        st.rerun()

    pdf = InterviewReportPdfService().build(outcome, role_title=report.role_title)
    st.download_button(
        "Download Interview Intelligence Report",
        data=pdf,
        file_name=f"interview_intelligence_{report.candidate_name.replace(' ', '_').lower()}.pdf",
        mime="application/pdf",
        key=f"download:{candidate_key}",
    )

def render_interview_intelligence():
    import streamlit as st

    apply_enterprise_theme()
    session = get_streamlit_session()

    if st.button(
        "← Back to Dashboard Perspective",
        key="interview_back_dashboard",
        help="Return to the whole candidate pool without clearing the active candidate.",
    ):
        request_page("Dashboard Perspective", reason="Returned to Dashboard Perspective from Interview & Assessment.")
        st.rerun()

    enterprise_hero(
        "Interview & Assessment",
        "Prepare, conduct and evaluate a focused, evidence-based interview while keeping pre-interview Talent Fit unchanged.",
        "Structured Human Assessment",
    )

    if session is None or not getattr(session, "ranked_analyses", None):
        st.info("Create or load a recruitment session before preparing an interview strategy.")
        return

    with st.spinner("Preparing the interview context…"):
        reports = InterviewWorkspaceService().build_all(session)

    if not reports:
        st.info("No candidate analysis is available for interview preparation.")
        return

    reports = sort_by_official_rank(
        reports
    )
    reports_by_id = {
        str(getattr(report, "candidate_id", "") or report.candidate_name): report
        for report in reports
    }
    option_ids = list(reports_by_id)
    selection_key = "interview_intelligence_candidate_id"
    context_key = "interview_intelligence_candidate_context"
    workflow_context = get_workflow_context(session, current_page="Interview Intelligence")
    preferred_id = workflow_context.selected_candidate_id
    preferred_option = preferred_id if preferred_id in option_ids else option_ids[0]
    selection_context = (
        str(
            getattr(
                session,
                "session_id",
                "session",
            )
        ),
        tuple(option_ids),
        preferred_option,
    )

    if (
        st.session_state.get(
            context_key
        )
        != selection_context
    ):
        st.session_state[
            context_key
        ] = selection_context

        st.session_state[
            selection_key
        ] = preferred_option

    elif (
        st.session_state.get(
            selection_key
        )
        not in option_ids
    ):
        st.session_state[
            selection_key
        ] = preferred_option

    selected_id = st.selectbox(
        "Candidate",
        option_ids,
        key=selection_key,
        format_func=lambda candidate_id: (
            f"#{reports_by_id[candidate_id].official_rank} "
            f"{reports_by_id[candidate_id].candidate_name}"
        ),
    )
    selected_id = str(
        selected_id
    )

    report = reports_by_id.get(
        selected_id
    )

    if report is None:
        st.error(
            "The selected candidate could not "
            "be resolved from the active "
            "recruitment session."
        )
        return

    resolved_report_id = str(
        getattr(
            report,
            "candidate_id",
            "",
        )
        or report.candidate_name
    )

    if resolved_report_id != selected_id:
        st.error(
            "Candidate context mismatch detected. "
            "Reload the active recruitment session."
        )
        return

    select_workflow_candidate(
        selected_id,
        report.candidate_name,
        source_widget_key=selection_key,
    )

    workflow_context = get_workflow_context(session, current_page="Interview Intelligence")
    saved_evaluation = workflow_context.interview_evaluations.get(selected_id)

    st.markdown(
        f'''<div class="tc-card" style="margin-top:.35rem">
        <div style="font-size:.7rem;text-transform:uppercase;letter-spacing:.08em;color:#64748B;font-weight:800">Candidate interview</div>
        <div style="font-size:1.35rem;font-weight:850;margin:.2rem 0">{report.candidate_name}</div>
        <div class="tc-muted">Official rank #{report.official_rank} · {report.role_title}</div>
        </div>''',
        unsafe_allow_html=True,
    )

    metric_grid([
        ("Official Fit", f"{report.fit_score:.0f}%", "Canonical score"),
        ("Evidence Confidence", f"{report.confidence_score}%", "Preparation basis"),
        (
            "Interview Status",
            "Assessed" if saved_evaluation else "Prepared" if selected_id in workflow_context.interview_prepared_candidate_ids else "Not started",
            report.risk_level,
        ),
    ])

    if saved_evaluation:
        st.success(
            f"Assessment saved · {saved_evaluation.get('recommendation', 'Recorded')} · "
            f"evidence coverage {saved_evaluation.get('evidence_coverage', 0)}%."
        )
    elif selected_id in workflow_context.interview_prepared_candidate_ids:
        st.info("Preparation is complete. Continue with the structured evaluation.")
    else:
        st.info("Prepare the interview playbook before recording evidence.")

    preparation_export = RecruitmentPdfService().interview(report, saved_evaluation)
    export_col, compensation_col, compare_col = st.columns([1.15, 1, 1])
    with export_col:
        st.download_button(
            "Download interview report (PDF)",
            data=preparation_export.data,
            file_name=preparation_export.file_name,
            mime=preparation_export.mime,
            key=f"interview_preparation_pdf_{selected_id}",
            use_container_width=True,
        )
    with compensation_col:
        if st.button(
            "Record compensation",
            key=f"interview_compensation_{selected_id}",
            use_container_width=True,
        ):
            request_page(
                "Compensation & Budget",
                reason=f"Record compensation expectations for {report.candidate_name} during or after interview.",
            )
            st.rerun()
    with compare_col:
        if st.button(
            "Compare finalists →",
            type="primary",
            key=f"interview_compare_top_{selected_id}",
            use_container_width=True,
        ):
            request_page("Comparison", reason="Open finalist comparison from Interview & Assessment.")
            st.rerun()

    # "Live Evaluation" remains the underlying evidence-capture capability.
    tab_prepare, tab_conduct, tab_assessment = st.tabs([
        "Prepare",
        "Conduct",
        "Assessment",
    ])

    with tab_prepare:
        plan_col, gap_col = st.columns([1, 1.35])
        with plan_col:
            section_title("Interview plan")
            st.metric("Suggested duration", f"{report.plan.total_minutes} min")
            with st.expander("View agenda", expanded=False):
                for section in report.plan.sections:
                    st.write(f"**{section.duration_minutes} min · {section.title}** — {section.objective}")
        with gap_col:
            section_title("Priority validation")
            priority = [c for c in report.competencies if c.validate_in_interview]
            for competency in priority[:4]:
                st.warning(f"{competency.name}: {competency.rationale}")

        key = _cache_key(session, report)
        cached_questions = st.session_state.get(key)
        if cached_questions is None:
            if st.button(
                "Generate interview playbook",
                type="primary",
                key=f"generate_{key}",
                use_container_width=True,
            ):
                st.session_state[key] = report.questions
                cached_questions = report.questions
                workflow_context = get_workflow_context(session, current_page="Interview Intelligence")
                if selected_id not in workflow_context.interview_prepared_candidate_ids:
                    workflow_context.interview_prepared_candidate_ids.append(selected_id)
                workflow_context.mark_completed("prepare")
                save_workflow_context(workflow_context)
                st.success("Interview playbook generated and cached.")
        else:
            action_col, refresh_col = st.columns([3, 1])
            with action_col:
                st.caption("The playbook is ready for this candidate and mission.")
            with refresh_col:
                if st.button("Regenerate", key=f"regenerate_{key}"):
                    st.session_state[key] = report.questions
                    cached_questions = report.questions
        if cached_questions is not None:
            _render_strategy(report, cached_questions)

    with tab_conduct:
        section_title("Live Evaluation", "Capture one grounded answer and assessment at a time.")
        _render_live_evaluation(session, report, selected_id)

    with tab_assessment:
        section_title("Assessment summary")
        if saved_evaluation:
            metric_grid([
                ("Recommendation", saved_evaluation.get("recommendation", "Recorded"), "Human assessment"),
                ("Evidence coverage", f"{saved_evaluation.get('evidence_coverage', 0)}%", "Captured evidence"),
                ("Confidence", f"{saved_evaluation.get('confidence', 0)}%", "Assessment confidence"),
            ])
            st.write(saved_evaluation.get("next_step", "Review the finalist comparison."))
        else:
            st.info("Complete and save the evaluation to unlock the post-interview summary.")
        with st.expander("Pre-interview preparation scorecard", expanded=False):
            rows = [
                {
                    "Competency": item.competency,
                    "Suggested score": item.suggested_score,
                    "Evaluation guidance": item.evaluation_guidance,
                }
                for item in report.scorecard
            ]
            st.dataframe(rows, use_container_width=True, hide_index=True)
            st.metric("Decision readiness", f"{report.decision_readiness}%")
            st.caption("This preparation scorecard is not a post-interview hiring decision.")

