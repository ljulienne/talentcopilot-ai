import streamlit as st

from talentcopilot.services.session_manager import get_current_session


def render_reports_v2():
    session = get_current_session()
    ranked = session.ranked_results
    best = session.best_candidate

    with st.container(border=True):
        st.caption("Decision Reporting")
        st.title("📄 Decision Reports")
        st.write(
            "Generate clear, evidence-based reports to explain hiring recommendations "
            "to hiring managers and HR leaders."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Candidates", session.total_candidates)
    with col2:
        st.metric("Reports Ready", len(ranked))
    with col3:
        st.metric("Avg Confidence", f"{session.average_confidence}%")
    with col4:
        st.metric("Explainability", "100%")

    st.divider()

    if not best:
        with st.container(border=True):
            st.subheader("No decision report available yet")
            st.info("Run a candidate analysis first to generate live decision reports.")
        return

    left, right = st.columns([2, 1], gap="large")

    with left:
        with st.container(border=True):
            st.subheader("🧠 Report Preview")

            st.markdown(f"### {best.name} · {session.job.title}")

            if "strong" in best.recommendation.lower():
                st.success(best.recommendation)
            elif "validation" in best.recommendation.lower() or "review" in best.recommendation.lower():
                st.warning(best.recommendation)
            else:
                st.info(best.recommendation)

            st.markdown("**Executive Summary**")
            st.write(
                best.summary
                or f"{best.name} is currently the strongest available candidate based on the live analysis."
            )

            st.markdown("**Key Evidence**")
            if best.evidence:
                for item in best.evidence[:5]:
                    st.write(f"- {item}")
            else:
                st.caption("No detailed evidence available yet.")

            st.markdown("**Decision Risks**")
            if best.risks:
                for risk in best.risks[:3]:
                    st.warning(risk)
            else:
                st.success("No major risk documented in the current analysis.")

        with st.container(border=True):
            st.subheader("🎯 Interview Priorities")
            if best.risks:
                for index, risk in enumerate(best.risks[:3], start=1):
                    st.write(f"{index}. Validate: {risk}")
            else:
                st.write("1. Confirm motivation and availability.")
                st.write("2. Validate ownership of key achievements.")
                st.write("3. Clarify expectations for the role.")

    with right:
        with st.container(border=True):
            st.subheader("⚡ Report Actions")
            st.button("Generate PDF", use_container_width=True, disabled=True)
            st.button("Share with Hiring Manager", use_container_width=True, disabled=True)
            st.button("Export Evidence Summary", use_container_width=True, disabled=True)

        with st.container(border=True):
            st.subheader("📌 Report Quality")
            if best.evidence:
                st.success("Evidence linked")
            else:
                st.warning("Evidence incomplete")

            if best.risks:
                st.success("Risks documented")
            else:
                st.info("No major risks documented")

            st.success("Human decision required")

        with st.container(border=True):
            st.subheader("🤖 Copilot")
            st.info(
                "Ask Copilot to rewrite this report for a hiring manager, HR Director, "
                "or interview panel."
            )
