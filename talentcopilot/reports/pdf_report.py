
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_recruiter_report(batch, recruitment_context=None):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("TalentCopilot AI - Recruiter Report", styles["Title"]))
    elements.append(Spacer(1, 16))

    if recruitment_context:
        elements.append(Paragraph("Recruitment Context", styles["Heading2"]))

        context_data = [
            ["Job Title", recruitment_context.get("job_title", "")],
            ["Company", recruitment_context.get("company", "")],
            ["Department", recruitment_context.get("department", "")],
            ["Location", recruitment_context.get("location", "")],
            ["Type", recruitment_context.get("recruitment_type", "")],
            ["Language", recruitment_context.get("language", "")]
        ]

        table = Table(context_data, colWidths=[140, 330])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2FF")),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 18))

    results = batch.get("results", [])

    elements.append(Paragraph("Candidate Ranking", styles["Heading2"]))

    ranking_data = [["Rank", "Candidate", "Score", "Confidence", "Recommendation"]]

    for index, item in enumerate(results, start=1):
        candidate = item["candidate"]
        match = item["match_result"]

        ranking_data.append([
            str(index),
            candidate.name,
            f"{match.overall_score}%",
            f"{match.confidence_score}%",
            match.recommendation
        ])

    table = Table(ranking_data, colWidths=[45, 170, 70, 80, 120])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 18))

    elements.append(Paragraph("Top Candidate Details", styles["Heading2"]))

    for index, item in enumerate(results[:5], start=1):
        candidate = item["candidate"]
        match = item["match_result"]

        elements.append(Paragraph(f"#{index} - {candidate.name}", styles["Heading3"]))
        elements.append(Paragraph(f"Score: {match.overall_score}% | Confidence: {match.confidence_score}% | Recommendation: {match.recommendation}", styles["Normal"]))
        elements.append(Paragraph(match.executive_summary, styles["Normal"]))
        elements.append(Spacer(1, 8))

        if match.gaps:
            elements.append(Paragraph("Main gaps:", styles["Normal"]))
            for gap in match.gaps[:3]:
                elements.append(Paragraph(f"- {gap.competency}: {gap.explanation}", styles["Normal"]))

        if match.interview_questions:
            elements.append(Paragraph("Suggested interview questions:", styles["Normal"]))
            for q in match.interview_questions[:3]:
                elements.append(Paragraph(f"- {q.question}", styles["Normal"]))

        elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer
