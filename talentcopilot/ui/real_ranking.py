from talentcopilot.real_ranking.models import CandidateTextInput, RealRankingInput
from talentcopilot.real_ranking.pipeline import RealRankingPipeline
from talentcopilot.services.real_ranking_demo_service import RealRankingDemoService
from talentcopilot.ui.design_system.components import enterprise_hero, insight_card, metric_grid, section_title
from talentcopilot.ui.design_system.theme import apply_enterprise_theme


DEFAULT_JOB_TEXT = '''Transformation Lead
Responsibilities
Lead HRIS transformation projects and stakeholder management.
Requirements
Minimum 6 years experience.
Required skills: Project Management, Stakeholder Management, HRIS.
Compensation
85000 100000
'''

DEFAULT_CANDIDATES = '''Alice Martin
Experience
8 years experience leading HRIS transformation projects.
Skills
HRIS, Project Management, Stakeholder Management, Leadership
---
Sophie Chen
Experience
10 years experience leading global HRIS transformation.
Skills
HRIS, Project Management, Stakeholder Management, SuccessFactors
---
David Smith
Experience
1 years experience in graphic design.
Skills
Graphic Design, Branding
'''


def _parse_candidates(text: str):
    candidates = []
    for index, block in enumerate((text or "").split("---"), start=1):
        clean = block.strip()
        if clean:
            candidates.append(CandidateTextInput(filename=f"candidate_{index}.txt", text=clean))
    return candidates


def _render_output(output):
    import streamlit as st

    metric_grid([
        ("Role", output.role_title, "RoleProfile"),
        ("Candidates", str(output.total_candidates), "Analyzed"),
        ("Top Candidate", output.ranked_candidates[0].candidate_name if output.ranked_candidates else "-", "Ranking"),
        ("Top Score", str(output.ranked_candidates[0].ranking_score) if output.ranked_candidates else "-", "Ranking Score"),
    ])

    rows = [
        {
            "Rank": item.rank,
            "Candidate": item.candidate_name,
            "Recommendation": item.recommendation,
            "Fit": item.fit_score,
            "Confidence": item.confidence_score,
            "Risk": item.risk_level,
            "Ranking Score": item.ranking_score,
        }
        for item in output.ranked_candidates
    ]
    st.dataframe(rows, use_container_width=True)

    names = [item.candidate_name for item in output.ranked_candidates]
    if not names:
        return

    selected = st.selectbox("Candidate detail", names)
    item = output.ranked_candidates[names.index(selected)]
    profile = item.matching_output.decision_output.profile

    insight_card(
        "Recommendation rationale",
        item.rationale,
        item.recommendation,
    )

    tab_summary, tab_signals, tab_trace = st.tabs(["Summary", "Signals", "Decision Trace"])

    with tab_summary:
        section_title("Executive Summary")
        st.write(profile.metadata.get("executive_summary", "-"))

    with tab_signals:
        rows = [{"Signal": key, "Value": value} for key, value in profile.metadata.items()]
        st.dataframe(rows, use_container_width=True)

    with tab_trace:
        for index, step in enumerate(profile.decision_trace.steps, start=1):
            with st.expander(f"{index}. {step.engine} · {step.action}"):
                st.write(step.explanation)
                st.caption(f"Output: {step.output_ref}")


def render_real_ranking():
    import streamlit as st

    apply_enterprise_theme()

    enterprise_hero(
        "Real Ranking",
        "Rank multiple real candidate texts against one job description through Decision Core.",
        "Release 1.2 — Real Intelligence",
    )

    insight_card(
        "Ranking principle",
        "Ranking consumes CandidateDecisionProfiles. It does not recalculate Fit, Risk, Budget or Recommendation.",
        "Decision Core",
    )

    job_text = st.text_area("Job description text", value=DEFAULT_JOB_TEXT, height=180)
    candidates_text = st.text_area("Candidate texts separated by ---", value=DEFAULT_CANDIDATES, height=300)

    col1, col2 = st.columns(2)
    run_manual = col1.button("Run real ranking")
    run_demo = col2.button("Run demo")

    if run_demo:
        output = RealRankingDemoService().run_demo().output
        _render_output(output)

    if run_manual:
        output = RealRankingPipeline().run(
            RealRankingInput(
                job_filename="job.txt",
                job_text=job_text,
                candidates=_parse_candidates(candidates_text),
            )
        )
        _render_output(output)
