"""PDF export for the Release 4.5A Executive Decision Brief."""

from __future__ import annotations

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class ExecutiveDecisionPdfService:
    def generate(self, brief) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=42,
            rightMargin=42,
            topMargin=42,
            bottomMargin=42,
            title=f"Executive Decision Brief - {brief.candidate_name}",
        )
        styles = getSampleStyleSheet()
        story = [
            Paragraph("TalentCopilot AI — Executive Decision Brief", styles["Title"]),
            Spacer(1, 12),
            Paragraph(brief.candidate_name, styles["Heading2"]),
            Spacer(1, 8),
        ]

        metrics = [
            ["Official Match", f"{brief.official_match_score:.0f}%"],
            ["Official Rank", f"#{brief.official_rank}"],
            ["AI Confidence", f"{brief.ai_confidence}%"],
            ["Recommendation", brief.recommendation],
            ["Decision Status", brief.decision_status],
            ["Business Impact", brief.business_impact],
            ["Expected Ramp-up", brief.ramp_up],
        ]
        table = Table(metrics, colWidths=[145, 340])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2FF")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        story.extend([table, Spacer(1, 16)])

        self._section(story, styles, "Executive interpretation", [brief.executive_narrative])
        self._section(story, styles, "Top strengths", brief.strengths)
        self._section(
            story,
            styles,
            "Hiring risk matrix",
            [f"{risk.name} — {risk.level}: {risk.rationale}" for risk in brief.risks],
        )
        self._section(story, styles, "Interview priorities", brief.interview_priorities)
        self._section(story, styles, "Recommended next action", [brief.next_action])
        self._section(story, styles, "Ramp-up rationale", [brief.ramp_up_rationale])
        story.extend([Spacer(1, 10), Paragraph(brief.governance_note, styles["Italic"])])

        doc.build(story)
        return buffer.getvalue()

    def _section(self, story, styles, title: str, values) -> None:
        story.extend([Paragraph(title, styles["Heading2"]), Spacer(1, 4)])
        items = list(values or [])
        if not items:
            items = ["No structured information available."]
        for value in items:
            story.append(Paragraph(f"• {value}", styles["BodyText"]))
        story.append(Spacer(1, 10))
