
import streamlit as st

from talentcopilot.i18n import tr

from talentcopilot.services.ranking_service import rank_candidates
import pandas as pd

from talentcopilot.ui.components import section_title, assistant_panel
from talentcopilot.ui.design_system import render_page_header

MIN_COMPARE_CANDIDATES = 2
MAX_COMPARE_CANDIDATES = 5


def _candidate_label(item, index):
    candidate = item["candidate"]
    score = item["match_result"].overall_score
    return f"#{index + 1} - {candidate.name} ({score}%)"


def _score_status(score):
    if score >= 85:
        return "🟢 Excellent Match"
    if score >= 70:
        return "🟡 Strong Match"
    if score >= 50:
        return "🟠 Potential Match"
    return "🔴 Weak Match"


def _hiring_risk(match):
    if match.overall_score >= 85 and len(match.gaps) <= 1:
        return "🟢 Low"
    if match.overall_score >= 70 and len(match.gaps) <= 3:
        return "🟡 Medium"
    return "🔴 High"


def _get_strengths(match_result, limit=3):
    return [
        detail.requirement.name
        for detail in match_result.match_details
        if detail.score >= 80
    ][:limit]


def _get_gaps(match_result, limit=3):
    return [gap.competency for gap in match_result.gaps][:limit]


def _detect_languages(candidate):
    flags = []

    for capability in candidate.capabilities:
        name = capability.name.lower()

        if "french" in name or "français" in name:
            flags.append("🇫🇷")
        if "english" in name or "anglais" in name:
            flags.append("🇬🇧")
        if "mandarin" in name or "chinese" in name or "chinois" in name:
            flags.append("🇨🇳")

    unique_flags = list(dict.fromkeys(flags))
    return " ".join(unique_flags) if unique_flags else "Not detected"


def _main_badge(item, all_items):
    match = item["match_result"]
    candidate = item["candidate"]

    best_score = max(i["match_result"].overall_score for i in all_items)

    if match.overall_score == best_score:
        return "🏆 Best Overall Match"

    capability_names = " ".join([cap.name.lower() for cap in candidate.capabilities])

    if "power bi" in capability_names or "analytics" in capability_names or "reporting" in capability_names:
        return "📊 Data Expert"

    if "mandarin" in capability_names or "chinese" in capability_names:
        return "🌍 International Profile"

    if "hris" in capability_names or "sirh" in capability_names:
        return "🔧 HRIS Specialist"

    return "⭐ Relevant Profile"


def _candidate_card(item, index, all_items):
    candidate = item["candidate"]
    match = item["match_result"]

    st.markdown(f"""
    <div style="
        background:white;
        border-radius:18px;
        padding:18px;
        border:1px solid #E2E8F0;
        box-shadow:0 4px 12px rgba(0,0,0,.05);
        margin-bottom:16px;
    ">
        <div style="font-size:13px;color:#64748B;">#{index + 1}</div>
        <h3 style="margin-bottom:4px;">{candidate.name}</h3>
        <div style="font-size:13px;color:#4F46E5;font-weight:600;">
            {_main_badge(item, all_items)}
        </div>
        <div style="font-size:34px;font-weight:700;color:#0F172A;margin-top:12px;">
            {match.overall_score}%
        </div>
        <div style="color:#64748B;margin-bottom:10px;">
            {_score_status(match.overall_score)}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(match.overall_score / 100)
    st.write(f"**Confidence:** {match.confidence_score}%")
    st.write(f"**Hiring Risk:** {_hiring_risk(match)}")
    st.write(f"**Languages:** {_detect_languages(candidate)}")
    st.write(f"**Recommendation:** {match.recommendation}")


def render_candidate_comparison(results):
    render_page_header(
        title=tr("comparison.title"),
        subtitle=tr("comparison.subtitle"),
        description=tr("comparison.description"),
        icon="⚖️",
    )

    if not results:
        st.info("Run an analysis first from the Dashboard.")
        return

    section_title(
        tr("comparison.workspace"),
        tr("comparison.workspace_subtitle")
    )

    assistant_panel(
        "Recruiter Copilot",
        "Choose your shortlisted candidates. I will compare match score, confidence, languages, hiring risk, strengths and gaps."
    )

    labels = [_candidate_label(item, index) for index, item in enumerate(results)]

    selected_labels = st.multiselect(
        "Select candidates to compare",
        labels,
        max_selections=MAX_COMPARE_CANDIDATES
    )

    if len(selected_labels) < MIN_COMPARE_CANDIDATES:
        st.info("Select at least 2 candidates to start the comparison.")
        return

    selected_items = [results[labels.index(label)] for label in selected_labels]

    section_title(
        "Candidate Cards",
        "Quick overview of selected candidates."
    )

    cols = st.columns(len(selected_items))

    for index, (col, item) in enumerate(zip(cols, selected_items)):
        with col:
            _candidate_card(item, index, selected_items)

    st.divider()

    section_title(
        "Comparison Table",
        "Side-by-side decision matrix."
    )

    overview_rows = []

    for item in selected_items:
        candidate = item["candidate"]
        match = item["match_result"]

        overview_rows.append({
            "Candidate": candidate.name,
            "Match": f"{match.overall_score}%",
            "Status": _score_status(match.overall_score),
            "Confidence": f"{match.confidence_score}%",
            "Hiring Risk": _hiring_risk(match),
            "Languages": _detect_languages(candidate),
            "Recommendation": match.recommendation
        })

    st.dataframe(pd.DataFrame(overview_rows), use_container_width=True)

    st.divider()

    section_title(
        "Strengths & Gaps",
        "Key observations for each candidate."
    )

    cols = st.columns(len(selected_items))

    for col, item in zip(cols, selected_items):
        candidate = item["candidate"]
        match = item["match_result"]

        strengths = _get_strengths(match)
        gaps = _get_gaps(match)

        with col:
            st.markdown(f"### {candidate.name}")

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

    st.divider()

    section_title(
        "Recruiter Recommendation",
        "AI-generated conclusion."
    )

    best = max(selected_items, key=lambda item: item["match_result"].overall_score)
    best_candidate = best["candidate"].name
    best_score = best["match_result"].overall_score

    st.success(
        f"{best_candidate} currently has the strongest overall fit among the selected candidates "
        f"with a match score of {best_score}%. Review strengths, gaps, languages and hiring risk before making the final decision."
    )
