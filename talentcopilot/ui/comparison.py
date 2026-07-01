
import streamlit as st
import pandas as pd

MIN_COMPARE_CANDIDATES = 2
MAX_COMPARE_CANDIDATES = 5


def _candidate_label(item, index):
    candidate = item["candidate"]
    score = item["match_result"].overall_score
    return f"#{index + 1} - {candidate.name} ({score}%)"


def _get_strengths(match_result, limit=3):
    strengths = [
        detail.requirement.name
        for detail in match_result.match_details
        if detail.score >= 80
    ]
    return strengths[:limit]


def _get_gaps(match_result, limit=3):
    gaps = [gap.competency for gap in match_result.gaps]
    return gaps[:limit]


def _detect_languages(candidate):
    detected = []

    for capability in candidate.capabilities:
        name = capability.name.lower()
        if "french" in name or "français" in name:
            detected.append("🇫🇷 French")
        if "english" in name or "anglais" in name:
            detected.append("🇬🇧 English")
        if "mandarin" in name or "chinese" in name or "chinois" in name:
            detected.append("🇨🇳 Mandarin")

    return detected if detected else ["Not detected"]


def render_candidate_comparison(results):
    st.title("⚖️ Candidate Comparison")
    st.caption("Compare 2 to 5 candidates side by side.")

    if not results:
        st.info("Run an analysis first from the Dashboard.")
        return

    labels = [_candidate_label(item, index) for index, item in enumerate(results)]

    selected_labels = st.multiselect(
        "Select candidates to compare",
        labels,
        max_selections=MAX_COMPARE_CANDIDATES
    )

    if len(selected_labels) < MIN_COMPARE_CANDIDATES:
        st.info("Select at least 2 candidates to start the comparison.")
        return

    selected_items = [
        results[labels.index(label)]
        for label in selected_labels
    ]

    st.subheader("Overview")

    overview_rows = []

    for item in selected_items:
        candidate = item["candidate"]
        match = item["match_result"]

        overview_rows.append({
            "Candidate": candidate.name,
            "Match": f"{match.overall_score}%",
            "Confidence": f"{match.confidence_score}%",
            "Recommendation": match.recommendation
        })

    st.dataframe(pd.DataFrame(overview_rows), use_container_width=True)

    st.subheader("Strengths and gaps")

    cols = st.columns(len(selected_items))

    for col, item in zip(cols, selected_items):
        candidate = item["candidate"]
        match = item["match_result"]

        strengths = _get_strengths(match)
        gaps = _get_gaps(match)
        languages = _detect_languages(candidate)

        with col:
            st.markdown(f"### {candidate.name}")
            st.metric("Match", f"{match.overall_score}%")
            st.write("**Strengths**")
            if strengths:
                for strength in strengths:
                    st.write(f"✅ {strength}")
            else:
                st.write("No major strength detected.")

            st.write("**Gaps**")
            if gaps:
                for gap in gaps:
                    st.write(f"⚠️ {gap}")
            else:
                st.write("No major gap detected.")

            st.write("**Languages**")
            for language in languages:
                st.write(language)

    st.subheader("Decision summary")

    best = max(selected_items, key=lambda item: item["match_result"].overall_score)
    best_candidate = best["candidate"].name
    best_score = best["match_result"].overall_score

    st.success(
        f"{best_candidate} currently has the strongest overall fit "
        f"among the selected candidates with a match score of {best_score}%."
    )
