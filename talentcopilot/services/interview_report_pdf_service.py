from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from talentcopilot.interview.pro_models import InterviewOutcome
from talentcopilot.interview.pro_service import InterviewIntelligenceProService


class InterviewReportPdfService:
    """Generate an explainable interview report without altering official decision data."""

    def build(self, outcome: InterviewOutcome, role_title: str = "") -> bytes:
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=f"Interview Intelligence Report - {outcome.candidate_name}",
        )
        styles = getSampleStyleSheet()
        story = [
            Paragraph("Interview Intelligence Report", styles["Title"]),
            Paragraph(outcome.candidate_name, styles["Heading2"]),
        ]
        if role_title:
            story.append(Paragraph(role_title, styles["Normal"]))
        story.extend([
            Spacer(1, 8),
            Paragraph(
                InterviewIntelligenceProService().build_executive_summary(outcome),
                styles["BodyText"],
            ),
            Spacer(1, 12),
            Paragraph("Decision recommendation", styles["Heading2"]),
        ])

        recommendation = outcome.recommendation
        summary_rows = [
            ["Recommendation", recommendation.label],
            ["Recommendation confidence", f"{recommendation.confidence}%"],
            ["Interview score", f"{outcome.overall_score:.2f}/5"],
            ["Evidence coverage", f"{outcome.evidence_coverage}%"],
            ["Next step", recommendation.next_step],
        ]
        table = Table(summary_rows, colWidths=[55 * mm, 105 * mm])
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([table, Spacer(1, 12), Paragraph("Competency scorecard", styles["Heading2"])])

        rating_rows = [["Competency", "Score", "Confirmed", "STAR", "Evidence notes"]]
        for item in outcome.ratings:
            rating_rows.append([
                item.competency,
                f"{item.score}/5",
                "Yes" if item.evidence_confirmed else "No",
                f"{item.star.completeness_score}%",
                item.notes or item.star.evidence_summary,
            ])
        rating_table = Table(rating_rows, colWidths=[34 * mm, 16 * mm, 20 * mm, 17 * mm, 73 * mm], repeatRows=1)
        rating_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.35, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.extend([rating_table, Spacer(1, 12)])

        story.append(Paragraph("Remaining evidence gaps", styles["Heading2"]))
        if recommendation.remaining_risks:
            for risk in recommendation.remaining_risks:
                story.append(Paragraph(f"• {risk}", styles["BodyText"]))
        else:
            story.append(Paragraph("No material evidence gap remains.", styles["BodyText"]))

        story.extend([
            Spacer(1, 14),
            Paragraph(
                "Governance note: this report evaluates interview evidence only. "
                "It does not recalculate the official matching score, official rank, or AI confidence.",
                styles["Italic"],
            ),
        ])
        document.build(story)
        return buffer.getvalue()
