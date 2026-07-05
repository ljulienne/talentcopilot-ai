import streamlit as st


def render_interview_focus_card(interview_plan=None, questions=None, title: str = "🎯 Interview Focus"):
    """
    Displays interview focus areas and suggested questions.
    Pure UI component.
    """

    st.subheader(title)

    focus_areas = []
    question_items = []

    if interview_plan:
        focus_areas = getattr(interview_plan, "focus_areas", []) or []
        question_items = getattr(interview_plan, "questions", []) or []

    if questions:
        question_items = questions

    if not focus_areas and not question_items:
        st.info("No interview focus available.")
        return

    if focus_areas:
        st.write("**Focus areas**")
        for focus in focus_areas[:5]:
            st.write(f"🎯 {focus}")

    if question_items:
        st.write("**Suggested questions**")
        for question in question_items[:5]:
            st.markdown(
                f"""
<div style="
background:white;
border:1px solid #dbeafe;
border-radius:12px;
padding:14px;
margin-bottom:10px;
">
💬 {question}
</div>
""",
                unsafe_allow_html=True,
            )
