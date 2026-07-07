import streamlit as st


def render_talent_pool_v2():
    with st.container(border=True):
        st.caption("Talent Intelligence")
        st.title("🌐 Talent Pool")
        st.write(
            "Keep track of promising candidates, reusable profiles, and future hiring opportunities."
        )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Saved Talents", "126")
    with col2:
        st.metric("High Potential", "28")
    with col3:
        st.metric("Interview Ready", "14")
    with col4:
        st.metric("Recently Added", "9")

    st.divider()

    talents = [
        {
            "name": "Alice Martin",
            "target": "Transformation / HRIS / Operations",
            "status": "High priority",
            "confidence": "91%",
            "notes": "Strong transformation leadership profile.",
        },
        {
            "name": "Maria Garcia",
            "target": "Operations / Team Management",
            "status": "Interview ready",
            "confidence": "82%",
            "notes": "Strong operational leadership signals.",
        },
        {
            "name": "Bob Lee",
            "target": "Data / Analytics",
            "status": "Needs validation",
            "confidence": "74%",
            "notes": "Good technical baseline, business impact unclear.",
        },
    ]

    talents = sorted(
        talents,
        key=lambda t: int(t["confidence"].replace("%", "")),
        reverse=True,
    )

    left, right = st.columns([2, 1], gap="large")

    with left:
        st.subheader("🧠 Saved talent profiles")

        for index, talent in enumerate(talents):
            with st.container(border=True):
                c1, c2, c3 = st.columns([2, 1, 1])

                with c1:
                    st.markdown(f"### {talent['name']}")
                    st.caption(talent["target"])
                    st.write(talent["notes"])

                with c2:
                    if talent["status"] == "High priority":
                        st.success(talent["status"])
                    elif talent["status"] == "Needs validation":
                        st.warning(talent["status"])
                    else:
                        st.info(talent["status"])

                with c3:
                    st.caption("Decision Confidence")
                    st.markdown(f"## {talent['confidence']}")
                    st.button("Open Profile", use_container_width=True, disabled=True, key=f"open_talent_{index}")
                    st.button("Match to Job", use_container_width=True, disabled=True, key=f"match_talent_{index}")

    with right:
        with st.container(border=True):
            st.subheader("⚡ Talent actions")
            st.button("Add Talent", use_container_width=True, disabled=True)
            st.button("Search Talent Pool", use_container_width=True, disabled=True)
            st.button("Find Similar Profiles", use_container_width=True, disabled=True)

        with st.container(border=True):
            st.subheader("🤖 Copilot suggestions")
            st.info("Alice Martin could be reused for transformation roles.")
            st.warning("Bob Lee needs stronger evidence before shortlisting.")
            st.success("Maria Garcia is ready for an operational leadership interview.")
