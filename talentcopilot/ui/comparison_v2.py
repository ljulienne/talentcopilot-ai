import streamlit as st

from talentcopilot.services.session_manager import get_current_session


def render_comparison_v2():
    session = get_current_session()
    ranked = session.ranked_results

    with st.container(border=True):
        st.caption("Decision Comparison")
        st.title("⚖️ Candidate Comparison")
        st.write(
            "Compare candidates beyond scores: evidence quality, demonstrated skills, "
            "risks, uncertainty, and interview priorities."
        )

    if len(ranked) < 2:
        with st.container(border=True):
            st.subheader("Not enough candidates to compare")
            st.info("Run an analysis with at least two candidates to activate comparison.")
        return

    top_candidates = ranked[:3]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Candidates Compared", len(top_candidates))
    with col2:
        st.metric("Top Confidence", f"{int(top_candidates[0].candidate.decision_confidence)}%")
    with col3:
        st.metric("Main Trade-offs", max(1, len(top_candidates) - 1))
    with col4:
        total_risks = sum(len(r.candidate.risks) for r in top_candidates)
        st.metric("Risks to Validate", total_risks)

    st.divider()

    left, right = st.columns([2, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("🏆 Recommendation")
            best = top_candidates[0].candidate
            second = top_candidates[1].candidate

            st.success(f"{best.name} is currently the strongest candidate to prioritize.")
            st.write(
                f"{best.name} shows the strongest decision profile based on available "
                f"confidence, recommendation status, and current analysis. "
                f"{second.name} remains a relevant alternative depending on hiring priorities."
            )

        with st.container(border=True):
            st.subheader("📊 Decision matrix")

            table = {
                "Candidate": [],
                "Decision Confidence": [],
                "Recommendation": [],
                "Skills": [],
                "Risks": [],
            }

            for result in top_candidates:
                candidate = result.candidate
                table["Candidate"].append(candidate.name)
                table["Decision Confidence"].append(f"{int(candidate.decision_confidence)}%")
                table["Recommendation"].append(candidate.recommendation)
                table["Skills"].append(", ".join(candidate.skills[:4]) if candidate.skills else "Not documented")
                table["Risks"].append(candidate.risks[0] if candidate.risks else "No major risk documented")

            st.table(table)

        with st.container(border=True):
            st.subheader("🔁 Trade-offs")
            st.info(
                f"{best.name} appears stronger for immediate prioritization based on the current data."
            )
            st.warning(
                f"{second.name} could become a stronger option if the organization values "
                "potential, adaptability, or if missing evidence is validated."
            )

    with right:
        with st.container(border=True):
            st.subheader("🥇 Ranking")
            for index, result in enumerate(top_candidates, start=1):
                candidate = result.candidate
                st.write(f"{index}. **{candidate.name}** · {int(candidate.decision_confidence)}%")

        with st.container(border=True):
            st.subheader("🎯 Interview focus")
            for result in top_candidates:
                candidate = result.candidate
                if candidate.risks:
                    st.write(f"**{candidate.name}**: validate {candidate.risks[0]}")
                else:
                    st.write(f"**{candidate.name}**: confirm evidence depth and role motivation.")

        with st.container(border=True):
            st.subheader("⚖️ Challenge")
            st.warning(
                "The recommendation could change if the hiring priority shifts from "
                "immediate readiness to long-term potential, cost, or learning agility."
            )
