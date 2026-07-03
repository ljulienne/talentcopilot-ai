import streamlit as st


def candidate_hero(
    name,
    talent_score,
    confidence,
    applications,
    recommendation,
):
    st.markdown(
        f"""
<div class="tc-card">

<h1>👤 {name}</h1>

<h3>Enterprise Talent Profile</h3>

<br>

| Talent Score | Confidence | Applications |
|--------------|------------|--------------|
| **{talent_score}%** | **{confidence}%** | **{applications}** |

<br>

### ⭐ AI Recommendation

**{recommendation}**

</div>
""",
        unsafe_allow_html=True,
    )
