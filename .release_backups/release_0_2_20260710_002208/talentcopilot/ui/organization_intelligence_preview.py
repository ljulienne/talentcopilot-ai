import csv
import io

import streamlit as st

from talentcopilot.organization_intelligence import CollaborationRecord, OrganizationIntelligenceService
from talentcopilot.ui.next_shell import apply_next_style, hero, recommendation_block, signal_row


def _read_uploaded_csv(uploaded_file) -> list[CollaborationRecord]:
    content = uploaded_file.getvalue().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    missing = OrganizationIntelligenceService.REQUIRED_COLUMNS - set(reader.fieldnames or [])
    if missing:
        raise ValueError("Missing columns: " + ", ".join(sorted(missing)))

    records = []
    for index, row in enumerate(reader, start=2):
        try:
            interactions = int(row.get("interactions") or 1)
        except ValueError as exc:
            raise ValueError(f"Invalid interactions value on row {index}.") from exc
        records.append(
            CollaborationRecord(
                source_person=(row.get("source_person") or "").strip(),
                source_department=(row.get("source_department") or "").strip(),
                target_person=(row.get("target_person") or "").strip(),
                target_department=(row.get("target_department") or "").strip(),
                interactions=interactions,
            )
        )
    return records


def render_organization_intelligence_preview():
    apply_next_style()
    hero(
        "Organization Intelligence",
        "Upload collaboration metadata or use the demonstration dataset. TalentCopilot turns network signals into an executive diagnosis and practical actions.",
        tag="Release 0.1B",
    )

    st.caption("Privacy by design: this prototype uses relationship metadata only—not message content, emotion analysis or protected characteristics.")

    source = st.radio("Analysis source", ["Demonstration dataset", "Upload CSV"], horizontal=True)
    service = OrganizationIntelligenceService()

    if source == "Upload CSV":
        uploaded = st.file_uploader(
            "Collaboration export",
            type=["csv"],
            help="Required columns: source_person, source_department, target_person, target_department, interactions",
        )
        if not uploaded:
            st.info("Upload a CSV to generate the diagnostic. You can also switch to the demonstration dataset.")
            return
        try:
            records = _read_uploaded_csv(uploaded)
        except (UnicodeDecodeError, ValueError) as exc:
            st.error(str(exc))
            return
    else:
        records = service.demo_records()

    diagnostic = service.analyze(records)
    recommendation_block("Executive diagnosis", diagnostic.executive_summary)

    col1, col2, col3 = st.columns(3)
    col1.metric("Departments", len(diagnostic.departments))
    col2.metric("Collaboration links", diagnostic.record_count)
    cross_ratio = diagnostic.cross_department_weight / diagnostic.total_weight if diagnostic.total_weight else 0
    col3.metric("Cross-team interaction", f"{cross_ratio:.0%}")

    left, right = st.columns([1.05, .95])
    with left:
        st.markdown("### Signals that require attention")
        for item in diagnostic.department_insights[:4]:
            signal_row(
                item.department,
                f"Cross-department collaboration ratio: {item.collaboration_ratio:.0%}",
                f"External weight {item.external_weight} · Internal weight {item.internal_weight}",
            )

    with right:
        st.markdown("### Hidden connectors")
        if diagnostic.connectors:
            for connector in diagnostic.connectors:
                signal_row(
                    connector.person,
                    f"Connects {connector.departments_reached} departments",
                    f"Observed interaction weight: {connector.interaction_weight}",
                )
        else:
            st.info("No cross-department connector was detected in this dataset.")

    st.markdown("### Recommended actions")
    for index, recommendation in enumerate(diagnostic.recommendations, start=1):
        st.markdown(f"**{index}.** {recommendation}")

    with st.expander("CSV format and interpretation limits"):
        st.code("source_person,source_department,target_person,target_department,interactions\nMaya,HR,Noah,IT,12", language="text")
        st.write("This diagnostic identifies network patterns, not causation. Validate findings with business context, project outcomes and employee feedback before acting.")
