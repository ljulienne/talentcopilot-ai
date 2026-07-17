"""Unified recruitment decision workspace for TalentCopilot Release Alpha.

This module consolidates the existing recruitment, candidate, comparison,
interview, decision, copilot and reporting experiences into one guided surface.
The underlying services remain unchanged so the release does not duplicate or
replace the current intelligence engines.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from talentcopilot.services.candidate_workspace_service import CandidateWorkspaceService
from talentcopilot.services.comparison_workspace_service import ComparisonWorkspaceService
from talentcopilot.services.decision_board_service import DecisionBoardService
from talentcopilot.services.demo_session_factory import create_demo_recruitment_session
from talentcopilot.services.executive_reporting_service import ExecutiveReportingService
from talentcopilot.interview.workspace_service import InterviewWorkspaceService
from talentcopilot.services.recruiter_copilot_workspace_service import RecruiterCopilotWorkspaceService
from talentcopilot.services.recruitment_pipeline_service import RecruitmentPipelineService
from talentcopilot.services.recruitment_tasks_service import RecruitmentTasksService
from talentcopilot.services.recruitment_workspace_service import RecruitmentWorkspaceService
from talentcopilot.services.recruitment_cockpit_service import (
    RecruitmentCockpitService,
    RecruitmentCockpitView,
)
from talentcopilot.services.streamlit_session_bridge import get_streamlit_session, set_streamlit_session
from talentcopilot.ui.recruitment_upload_panel import render_recruitment_upload_panel
from talentcopilot.ui.design_system.components import (
    enterprise_hero,
    insight_card,
    metric_grid,
    next_action_card,
    section_title,
)
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


def _names(items: Iterable[object], attribute: str = "candidate_name") -> list[str]:
    """Return unique, non-empty names while preserving source order."""
    names: list[str] = []
    seen: set[str] = set()
    for item in items or []:
        value = str(getattr(item, attribute, "") or "").strip()
        if value and value not in seen:
            names.append(value)
            seen.add(value)
    return names


def _find(items: Sequence[object], name: str, attribute: str = "candidate_name"):
    for item in items or []:
        if str(getattr(item, attribute, "") or "") == name:
            return item
    return None



@dataclass(frozen=True)
class ExplainableMatchView:
    """Presentation-only explanation of an existing matching score."""

    score: float
    evidence_quality: str
    evidence_summary: str
    drivers: tuple[tuple[str, int, str], ...]
    gaps: tuple[str, ...]
    source_facts: tuple[str, ...]


@dataclass(frozen=True)
class ExecutiveDecisionView:
    """Presentation-only summary built from existing recruitment reports."""

    candidate_name: str
    recommendation: str
    match_score: float
    confidence_label: str
    confidence_reason: str
    strengths: tuple[str, ...]
    risks: tuple[str, ...]
    next_actions: tuple[str, ...]


def _text(value: object, fallback: str = "Not available") -> str:
    cleaned = str(value or "").strip()
    return cleaned or fallback


def _build_executive_decision(candidate_report, decision_report) -> ExecutiveDecisionView | None:
    """Build a defensive executive view without recalculating AI results."""
    if candidate_report is None:
        return None

    decision_candidate = _find(
        getattr(decision_report, "candidates", []) or [],
        _text(getattr(candidate_report, "candidate_name", ""), ""),
    )

    evidence = list(getattr(candidate_report, "evidence", []) or [])
    candidate_risks = list(getattr(candidate_report, "risks", []) or [])
    decision_reasons = list(getattr(decision_candidate, "reasons", []) or [])
    decision_risks = list(getattr(decision_candidate, "risks", []) or [])

    strengths = tuple(
        _text(getattr(item, "title", item))
        for item in (decision_reasons or evidence)[:3]
    )
    risks = tuple(
        _text(getattr(item, "title", item))
        for item in (decision_risks or candidate_risks)[:3]
    )

    score = float(getattr(candidate_report, "match_score", 0.0) or 0.0)
    evidence_count = len(evidence) + len(decision_reasons)
    risk_count = len(candidate_risks) + len(decision_risks)

    if score >= 80 and evidence_count >= 3:
        confidence_label = "High"
    elif score >= 60 and evidence_count >= 1:
        confidence_label = "Medium"
    else:
        confidence_label = "Limited"

    confidence_reason = (
        f"Based on {evidence_count} supporting observations and "
        f"{risk_count} identified risk{'s' if risk_count != 1 else ''}."
    )

    recommendation = _text(
        getattr(decision_candidate, "ai_recommendation", None)
        or getattr(candidate_report, "recommendation", None)
    )

    actions = tuple(
        _text(item)
        for item in (getattr(decision_report, "next_actions", []) or [])[:3]
    )
    if not actions:
        actions = ("Complete human validation before making the final decision.",)

    return ExecutiveDecisionView(
        candidate_name=_text(getattr(candidate_report, "candidate_name", None)),
        recommendation=recommendation,
        match_score=score,
        confidence_label=confidence_label,
        confidence_reason=confidence_reason,
        strengths=strengths,
        risks=risks,
        next_actions=actions,
    )


def _build_explainable_match(candidate_report) -> ExplainableMatchView | None:
    """Explain an existing match score using already available report data.

    This function never recalculates or changes the score. It only organises
    skills, evidence and risks already produced by the current services.
    """
    if candidate_report is None:
        return None

    skills = sorted(
        list(getattr(candidate_report, "skills", []) or []),
        key=lambda item: int(getattr(item, "level", 0) or 0),
        reverse=True,
    )
    evidence = list(getattr(candidate_report, "evidence", []) or [])
    risks = list(getattr(candidate_report, "risks", []) or [])

    drivers = tuple(
        (
            _text(getattr(skill, "name", None), "Relevant capability"),
            max(0, min(100, int(getattr(skill, "level", 0) or 0))),
            _text(getattr(skill, "evidence", None), "Detected in the candidate profile."),
        )
        for skill in skills[:5]
    )

    gaps = [
        _text(getattr(risk, "title", None), "Evidence gap")
        for risk in risks[:4]
    ]
    if len(gaps) < 3:
        for skill in reversed(skills):
            level = int(getattr(skill, "level", 0) or 0)
            if level < 75:
                label = f"Validate depth of {_text(getattr(skill, 'name', None), 'this capability')}"
                if label not in gaps:
                    gaps.append(label)
            if len(gaps) >= 3:
                break
    if not gaps:
        gaps.append("No material gap is documented; validate the strongest claims in interview.")

    source_facts = tuple(
        _text(getattr(item, "detail", None), _text(getattr(item, "title", None)))
        for item in evidence[:4]
    )

    strong_evidence = sum(
        1
        for item in evidence
        if _text(getattr(item, "strength", None), "Medium").lower() == "high"
    )
    evidence_count = len(evidence)
    if evidence_count >= 4 and strong_evidence >= 2:
        quality = "High"
    elif evidence_count >= 2:
        quality = "Medium"
    else:
        quality = "Limited"

    summary = (
        f"{evidence_count} evidence item{'s' if evidence_count != 1 else ''} available; "
        f"{strong_evidence} rated high strength. The displayed score is unchanged."
    )

    return ExplainableMatchView(
        score=float(getattr(candidate_report, "match_score", 0.0) or 0.0),
        evidence_quality=quality,
        evidence_summary=summary,
        drivers=drivers,
        gaps=tuple(gaps[:4]),
        source_facts=source_facts,
    )


def _render_explainable_match(view: ExplainableMatchView | None) -> None:
    import streamlit as st

    section_title(
        "Explainable matching",
        "Understand the existing score through visible capability drivers, gaps and source evidence.",
    )
    if view is None:
        st.info("Select an analysed candidate to explain the matching result.")
        return

    metric_grid([
        ("Overall match", f"{view.score:.0f}%", "Existing score — not recalculated"),
        ("Evidence quality", view.evidence_quality, view.evidence_summary),
        ("Positive drivers", str(len(view.drivers)), "Capabilities supporting the result"),
        ("Gaps to validate", str(len(view.gaps)), "Questions for human review"),
    ])

    drivers_col, gaps_col = st.columns([1.25, 0.75])
    with drivers_col:
        st.markdown("#### Main matching drivers")
        if view.drivers:
            for name, level, evidence in view.drivers:
                st.write(f"**{name} · {level}%**")
                st.progress(level / 100)
                st.caption(evidence)
        else:
            st.info("No structured skill drivers are available yet.")

    with gaps_col:
        st.markdown("#### Gaps to validate")
        for gap in view.gaps:
            st.warning(gap)

    st.markdown("#### Evidence influencing the explanation")
    if view.source_facts:
        for fact in view.source_facts:
            st.write(f"- {fact}")
    else:
        st.info("No detailed source facts are available. Treat the score as provisional.")

    st.caption(
        "Explainable Matching organises evidence already present in TalentCopilot. "
        "It does not alter ranking, matching weights or the underlying decision engines."
    )


def _render_executive_decision(view: ExecutiveDecisionView | None) -> None:
    import streamlit as st

    section_title(
        "Executive decision",
        "A concise, evidence-led view of the current recommendation. Human validation remains required.",
    )
    if view is None:
        st.info("Select an analysed candidate to display the executive decision summary.")
        return

    metric_grid([
        ("Candidate", view.candidate_name, "Current focus"),
        ("Recommendation", view.recommendation, "Existing decision signal"),
        ("Match", f"{view.match_score:.0f}%", "Existing matching result"),
        ("Evidence confidence", view.confidence_label, view.confidence_reason),
    ])

    left, middle, right = st.columns(3)
    with left:
        st.markdown("#### Why this candidate")
        if view.strengths:
            for item in view.strengths:
                st.success(item)
        else:
            st.info("No supporting strengths are available yet.")
    with middle:
        st.markdown("#### What to validate")
        if view.risks:
            for item in view.risks:
                st.warning(item)
        else:
            st.success("No material risk is currently documented.")
    with right:
        st.markdown("#### Recommended next actions")
        for item in view.next_actions:
            st.write(f"- {item}")

    st.caption(
        "TalentCopilot supports the hiring team with existing evidence and recommendations; "
        "it does not make the final hiring decision."
    )


def _status_icon(status: str) -> str:
    return {
        "done": "✓",
        "active": "●",
        "pending": "○",
    }.get(str(status or "").lower(), "○")


def _render_workflow_rail(view: RecruitmentCockpitView) -> None:
    """Render a compact workflow rail from the presentation model."""
    import streamlit as st

    section_title(
        "Recruitment workflow",
        "A single guided path from the mission to the final human decision.",
    )

    columns = st.columns(len(view.workflow_steps))
    for column, step in zip(columns, view.workflow_steps):
        with column:
            icon = _status_icon(step.status)
            st.markdown(f"### {icon}")
            st.markdown(f"**{step.label}**")
            st.caption(step.detail)

    st.progress(max(0, min(100, view.progress_percent)) / 100)
    st.caption(
        f"{view.progress_percent}% complete · Current stage: {view.current_stage}"
    )


def _render_cockpit(view: RecruitmentCockpitView) -> None:
    """Render the premium session cockpit without any business calculation."""
    import streamlit as st

    section_title(
        "Active recruitment",
        "The essential session context, official ranking and next recommended action.",
    )

    metric_grid([
        ("Mission", view.role_title, f"Session {view.session_id}"),
        (
            "Candidates",
            str(view.candidates_count),
            f"{view.analyzed_count} analysed",
        ),
        (
            "Current lead",
            view.top_candidate_name,
            f"{view.top_candidate_score:.0f}% official match"
            if view.top_candidate_name != "Not available"
            else "No ranking yet",
        ),
        (
            "Progress",
            f"{view.progress_percent}%",
            view.current_stage,
        ),
    ])

    _render_workflow_rail(view)

    next_action_card(
        view.next_action_title,
        view.next_action_detail,
        "Recommended next step",
    )


def _render_empty_state() -> None:
    import streamlit as st

    st.info(
        "No active recruitment is available. Create or reopen a recruitment from Projects, "
        "or load the Enterprise Demo to explore the unified workspace."
    )
    if st.button("Load Enterprise Demo", key="rdw_load_demo"):
        session = create_demo_recruitment_session()
        set_streamlit_session(session)
        st.success("Enterprise demo loaded.")
        st.rerun()


def _render_overview(workspace_report, pipeline_report, task_report) -> None:
    import streamlit as st
    from talentcopilot.ui.recruitment_workspace import _pipeline_deep_view, _task_board, _timeline

    section_title("Recruitment overview", "Pipeline health, timeline and operational next steps.")
    _pipeline_deep_view(pipeline_report)

    left, right = st.columns([1.15, 0.85])
    with left:
        section_title("Decision timeline")
        _timeline(workspace_report)
    with right:
        _task_board(task_report)

    if task_report.tasks:
        first = task_report.tasks[0]
        next_action_card(first.title, first.detail, "Continue")


def _render_candidate(report) -> None:
    import streamlit as st
    from talentcopilot.ui.candidate_workspace import (
        _render_evidence,
        _render_risks,
        _render_skill_bars,
    )

    if report is None:
        st.info("Select a candidate with an available analysis.")
        return

    insight_card("Executive summary", report.executive_summary, "Candidate Intelligence")
    metric_grid([
        ("Candidate", report.candidate_name, f"Rank #{report.rank}"),
        ("Match", f"{report.match_score:.0f}%", "AI matching"),
        ("Recommendation", report.recommendation, "Decision signal"),
        ("Evidence", str(len(report.evidence)), "Supporting observations"),
    ])
    _render_explainable_match(_build_explainable_match(report))

    overview, skills, evidence, risks, interview = st.tabs(
        ["Overview", "Skills", "Evidence", "Risks", "Interview focus"]
    )
    with overview:
        st.write(f"**Recommendation:** {report.recommendation}")
        st.write(f"**Match score:** {report.match_score:.0f}%")
    with skills:
        _render_skill_bars(report)
    with evidence:
        _render_evidence(report)
    with risks:
        _render_risks(report)
    with interview:
        if report.interview_focus:
            for item in report.interview_focus:
                st.write(f"- {item}")
        else:
            st.info("No interview focus generated yet.")


def _render_comparison(report) -> None:
    import streamlit as st
    from talentcopilot.ui.comparison_workspace import _matrix, _ranking_table, _score_gaps

    if not report.candidates:
        st.info("At least two analysed candidates are required for comparison.")
        return

    if report.differentiators:
        insight_card("Key differentiator", report.differentiators[0], "Comparison Intelligence")

    ranking, gaps, matrix, differentiators = st.tabs(
        ["Ranking", "Score gaps", "Decision matrix", "Differentiators"]
    )
    with ranking:
        _ranking_table(report)
    with gaps:
        _score_gaps(report)
    with matrix:
        _matrix(report)
    with differentiators:
        for item in report.differentiators:
            st.write(f"- {item}")


def _render_interview(report) -> None:
    import streamlit as st
    from talentcopilot.ui.interview_workspace import (
        _competency_matrix,
        _evaluation,
        _interview_plan,
        _live_notes,
        _questions,
        _scorecard,
    )

    if report is None:
        st.info("No interview plan is available for the selected candidate.")
        return

    metric_grid([
        ("Readiness", f"{report.readiness.score}%", report.readiness.status),
        ("Fit", f"{report.fit_score:.0f}%", "Current analysis"),
        ("Confidence", f"{report.confidence_score}%", "Interview basis"),
        ("Decision readiness", f"{report.decision_readiness}%", "After scorecard"),
    ])

    readiness, matrix, plan, questions, notes, scorecard, evaluation = st.tabs(
        ["Readiness", "Competencies", "Plan", "Questions", "Notes", "Scorecard", "Evaluation"]
    )
    with readiness:
        st.progress(max(0, min(100, report.readiness.score)) / 100)
        for driver in report.readiness.drivers:
            st.success(driver)
        for gap in report.readiness.gaps:
            st.warning(gap)
    with matrix:
        _competency_matrix(report)
    with plan:
        _interview_plan(report)
    with questions:
        _questions(report)
    with notes:
        _live_notes(report)
    with scorecard:
        _scorecard(report)
    with evaluation:
        _evaluation(report)


def _render_decision(report, candidate_name: str) -> None:
    import streamlit as st
    from talentcopilot.ui.decision_board import _reasons, _risks, _stakeholder_matrix

    candidate = _find(report.candidates, candidate_name)
    if candidate is None:
        st.info("No decision board is available for the selected candidate.")
        return

    insight_card(
        "Hiring recommendation",
        f"{candidate.candidate_name} is currently assessed as {candidate.ai_recommendation}. "
        f"Collaborative consensus is {candidate.consensus_score}%.",
        "Decision Intelligence",
    )
    metric_grid([
        ("Candidate", candidate.candidate_name, f"Rank #{candidate.rank}"),
        ("Match", f"{candidate.match_score:.0f}%", "AI matching"),
        ("Recommendation", candidate.ai_recommendation, "Decision signal"),
        ("Consensus", f"{candidate.consensus_score}%", "Collaborative readiness"),
    ])

    matrix, reasons, risks, actions = st.tabs(
        ["Stakeholder matrix", "Reasons", "Risks", "Next actions"]
    )
    with matrix:
        _stakeholder_matrix(candidate)
    with reasons:
        _reasons(candidate)
    with risks:
        _risks(candidate)
    with actions:
        for action in report.next_actions:
            st.write(f"- {action}")
        next_action_card(
            "Complete human validation",
            "AI guidance supports the decision; the hiring team remains accountable for the final choice.",
            "Continue",
        )


def _render_advisor(report, candidate_name: str) -> None:
    import streamlit as st
    from talentcopilot.ui.recruiter_copilot_workspace import (
        _render_actions,
        _render_alerts,
        _render_questions,
    )

    candidate = _find(report.candidates, candidate_name)
    section_title("Global AI actions", "The most useful actions for the active recruitment.")
    _render_actions(report.global_actions)

    if candidate is None:
        st.info("No candidate-specific Copilot guidance is available.")
        return

    insight_card(candidate.headline, candidate.recruiter_summary, "Recruiter Copilot")
    actions, questions, alerts, stakeholder = st.tabs(
        ["Actions", "Interview guide", "Alerts", "Stakeholder summary"]
    )
    with actions:
        _render_actions(candidate.actions)
    with questions:
        _render_questions(candidate.questions)
    with alerts:
        _render_alerts(candidate.alerts)
    with stakeholder:
        st.info(candidate.stakeholder_summary)


def _render_report(report, service: ExecutiveReportingService) -> None:
    import streamlit as st
    from talentcopilot.ui.executive_reporting import _risks, _shortlist_table

    insight_card("Executive summary", report.executive_summary, "Executive Brief")
    shortlist, risks, recommendations, export = st.tabs(
        ["Shortlist", "Risks", "Recommendations", "Export"]
    )
    with shortlist:
        _shortlist_table(report)
    with risks:
        _risks(report)
    with recommendations:
        section_title("Recommendations")
        for item in report.recommendations:
            st.write(f"- {item}")
        section_title("Next steps")
        for item in report.next_steps:
            st.write(f"- {item}")
    with export:
        markdown_report = service.to_markdown(report)
        st.download_button(
            "Download executive report",
            data=markdown_report,
            file_name="talentcopilot_executive_report.md",
            mime="text/markdown",
            key="rdw_download_report",
        )
        st.markdown(markdown_report)


def render_recruitment_decision_workspace() -> None:
    """Render the unified, decision-led recruitment experience."""
    import streamlit as st

    apply_enterprise_theme()
    session = get_streamlit_session()

    enterprise_hero(
        "Recruitment Decision Workspace",
        "Upload a mission and candidate CVs, then move from evidence to a confident hiring decision.",
        "Recruitment workflow",
    )

    session = render_recruitment_upload_panel(session)

    if session is None:
        _render_empty_state()
        return

    workspace_report = RecruitmentWorkspaceService().build(session)
    cockpit_view = RecruitmentCockpitService().build(session, workspace_report)
    _render_cockpit(cockpit_view)

    pipeline_report = RecruitmentPipelineService().build(session)
    task_report = RecruitmentTasksService().build(session)
    candidate_reports = CandidateWorkspaceService().build_all(session)
    comparison_report = ComparisonWorkspaceService().build(session)

    # Temporary Release 4.2.3 diagnostic.
    # Follow the official match value from the active session
    # to the Comparison workspace output without recomputation.
    with st.expander(
        "Official score propagation trace",
        expanded=True,
    ):
        import subprocess
        from pathlib import Path

        try:
            deployed_commit = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                cwd=str(Path(__file__).resolve().parents[2]),
                text=True,
                capture_output=True,
                check=False,
            ).stdout.strip() or "unknown"
        except Exception:
            deployed_commit = "unknown"

        metadata = dict(
            getattr(session, "metadata", {}) or {}
        )

        runtime_input_contract = metadata.get(
            "runtime_input_contract",
            {},
        ) or {}

        provenance_candidate_filenames = list(
            metadata.get("candidate_filenames", []) or []
        )
        provenance_candidate_hashes = list(
            metadata.get("candidate_document_hashes", []) or []
        )

        provenance_hash_by_filename = {
            str(filename): str(document_hash)
            for filename, document_hash in zip(
                provenance_candidate_filenames,
                provenance_candidate_hashes,
            )
        }

        st.markdown(
            "**0 — Production input contract**"
        )

        job_contract = dict(
            runtime_input_contract.get("job", {}) or {}
        )

        st.write(
            {
                "job_filename": job_contract.get("filename"),
                "job_status": job_contract.get("status"),
                "job_upload_bytes": job_contract.get(
                    "upload_bytes"
                ),
                "job_upload_sha256": job_contract.get(
                    "upload_sha256"
                ),
                "job_text_characters": job_contract.get(
                    "text_characters"
                ),
                "job_text_sha256_before_worker": (
                    job_contract.get("text_sha256")
                ),
                "job_text_sha256_from_session": metadata.get(
                    "job_document_hash"
                ),
                "job_hashes_equal": (
                    job_contract.get("text_sha256")
                    == metadata.get("job_document_hash")
                ),
            }
        )

        candidate_contract_rows = []

        for item in list(
            runtime_input_contract.get("candidates", []) or []
        ):
            item = dict(item or {})
            filename = str(item.get("filename") or "")
            before_hash = item.get("text_sha256")
            session_hash = provenance_hash_by_filename.get(
                filename
            )

            candidate_contract_rows.append(
                {
                    "filename": filename,
                    "status": item.get("status"),
                    "upload_bytes": item.get("upload_bytes"),
                    "upload_sha256": item.get("upload_sha256"),
                    "text_characters": item.get(
                        "text_characters"
                    ),
                    "text_sha256_before_worker": before_hash,
                    "text_sha256_from_session": session_hash,
                    "hashes_equal": before_hash == session_hash,
                }
            )

        st.dataframe(
            candidate_contract_rows,
            use_container_width=True,
            hide_index=True,
        )

        st.write(
            {
                "deployed_commit": deployed_commit,
                "session_id": getattr(
                    session,
                    "session_id",
                    None,
                ),
                "pipeline": metadata.get("pipeline"),
                "workflow_version": metadata.get(
                    "workflow_version"
                ),
                "analysis_version": metadata.get(
                    "analysis_version"
                ),
                "cache_schema": metadata.get(
                    "official_score_cache_schema"
                ),
                "execution_mode": metadata.get(
                    "execution_mode"
                ),
                "canonical_score_contract": metadata.get(
                    "canonical_score_contract"
                ),
            }
        )

        session_trace_rows = []

        for analysis in list(
            getattr(
                session,
                "ranked_analyses",
                [],
            )
            or []
        ):
            breakdown = dict(
                getattr(
                    analysis,
                    "score_breakdown",
                    {},
                )
                or {}
            )

            session_trace_rows.append(
                {
                    "candidate": getattr(
                        analysis,
                        "candidate_name",
                        None,
                    ),
                    "session_rank": getattr(
                        analysis,
                        "rank",
                        None,
                    ),
                    "session_match_score": getattr(
                        analysis,
                        "match_score",
                        None,
                    ),
                    "session_official_match": getattr(
                        analysis,
                        "official_match_score",
                        None,
                    ),
                    "session_decision_score": getattr(
                        analysis,
                        "decision_score",
                        None,
                    ),
                    "breakdown_official_upload_fit": (
                        breakdown.get(
                            "official_upload_fit"
                        )
                    ),
                    "breakdown_role_fit": breakdown.get(
                        "role_fit"
                    ),
                    "breakdown_confidence": breakdown.get(
                        "confidence"
                    ),
                }
            )

        st.markdown(
            "**1 — Active RecruitmentSession**"
        )
        st.dataframe(
            session_trace_rows,
            use_container_width=True,
            hide_index=True,
        )

        comparison_trace_rows = []

        for candidate in list(
            getattr(
                comparison_report,
                "candidates",
                [],
            )
            or []
        ):
            comparison_trace_rows.append(
                {
                    "candidate": getattr(
                        candidate,
                        "candidate_name",
                        None,
                    ),
                    "comparison_rank": getattr(
                        candidate,
                        "rank",
                        None,
                    ),
                    "comparison_match_score": getattr(
                        candidate,
                        "match_score",
                        None,
                    ),
                    "comparison_official_match": getattr(
                        candidate,
                        "official_match_score",
                        None,
                    ),
                    "comparison_decision_score": getattr(
                        candidate,
                        "decision_score",
                        None,
                    ),
                    "comparison_confidence": getattr(
                        candidate,
                        "ai_confidence",
                        None,
                    ),
                }
            )

        st.markdown(
            "**2 — ComparisonWorkspaceService output**"
        )
        st.dataframe(
            comparison_trace_rows,
            use_container_width=True,
            hide_index=True,
        )

        session_by_candidate = {
            str(row.get("candidate")): row
            for row in session_trace_rows
        }

        propagation_rows = []

        for comparison_row in comparison_trace_rows:
            name = str(
                comparison_row.get("candidate")
            )

            session_row = session_by_candidate.get(
                name,
                {},
            )

            session_score = session_row.get(
                "session_match_score"
            )

            comparison_score = comparison_row.get(
                "comparison_match_score"
            )

            propagation_rows.append(
                {
                    "candidate": name,
                    "session_score": session_score,
                    "comparison_score": comparison_score,
                    "delta": (
                        None
                        if session_score is None
                        or comparison_score is None
                        else round(
                            float(comparison_score)
                            - float(session_score),
                            2,
                        )
                    ),
                    "session_rank": session_row.get(
                        "session_rank"
                    ),
                    "comparison_rank": comparison_row.get(
                        "comparison_rank"
                    ),
                }
            )

        st.markdown(
            "**3 — Propagation comparison**"
        )
        st.dataframe(
            propagation_rows,
            use_container_width=True,
            hide_index=True,
        )
    interview_reports = InterviewWorkspaceService().build_all(session)
    decision_report = DecisionBoardService().build(session)
    copilot_report = RecruiterCopilotWorkspaceService().build(session)
    reporting_service = ExecutiveReportingService()
    executive_report = reporting_service.build(session)

    candidate_names = _names(candidate_reports)
    if not candidate_names:
        candidate_names = _names(decision_report.candidates)

    if candidate_names:
        selected_name = st.selectbox(
            "Candidate in focus",
            candidate_names,
            key="recruitment_decision_candidate",
        )
    else:
        selected_name = ""

    selected_candidate_report = _find(candidate_reports, selected_name)
    executive_decision = _build_executive_decision(
        selected_candidate_report,
        decision_report,
    )
    _render_executive_decision(executive_decision)

    overview, candidate, compare, interview, decision, advisor, report = st.tabs(
        ["Overview", "Candidate", "Compare", "Interview", "Decision", "AI Advisor", "Report"]
    )

    with overview:
        _render_overview(workspace_report, pipeline_report, task_report)
    with candidate:
        _render_candidate(selected_candidate_report)
    with compare:
        _render_comparison(comparison_report)
    with interview:
        _render_interview(_find(interview_reports, selected_name))
    with decision:
        _render_decision(decision_report, selected_name)
    with advisor:
        _render_advisor(copilot_report, selected_name)
    with report:
        _render_report(executive_report, reporting_service)
