"""PDF export for the Release 4.6 Executive Decision Center."""
from __future__ import annotations

from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class ExecutiveDecisionPdfService:
    def generate(self, brief, center=None) -> bytes:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, leftMargin=42, rightMargin=42, topMargin=42,
            bottomMargin=42, title=f"Executive Decision Brief - {brief.candidate_name}",
        )
        styles = getSampleStyleSheet()
        story = [
            Paragraph("TalentCopilot AI — Executive Decision Report", styles["Title"]),
            Spacer(1, 12), Paragraph(brief.candidate_name, styles["Heading2"]), Spacer(1, 8),
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
        if center is not None:
            metrics.insert(3, ["Decision Readiness", f"{center.decision_readiness}% — {center.readiness_label}"])
        table = Table(metrics, colWidths=[145, 340])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EEF2FF")),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))
        story.extend([table, Spacer(1, 16)])
        self._section(story, styles, "Executive interpretation", [brief.executive_narrative])
        if center is not None:
            self._section(story, styles, "Decision readiness gaps", [f"{g.label} — {g.status}: {g.rationale}" for g in center.readiness_gaps])
            self._section(story, styles, "Evidence quality", [f"{e.label} — {e.quality}: {e.rationale}" for e in center.evidence_quality])
            self._section(story, styles, "Confidence rationale", center.confidence_reasons)
        self._section(story, styles, "Top strengths", brief.strengths)
        self._section(story, styles, "Hiring risk matrix", [f"{r.name} — {r.level}: {r.rationale}" for r in brief.risks])
        self._section(story, styles, "Interview priorities", brief.interview_priorities)
        self._section(story, styles, "Recommended next action", [brief.next_action])
        if center is not None:
            self._section(story, styles, "Executive timeline", [f"{m.period}: {m.objective}" for m in center.timeline])
        self._section(story, styles, "Ramp-up rationale", [brief.ramp_up_rationale])
        story.extend([Spacer(1, 10), Paragraph(center.governance_note if center is not None else brief.governance_note, styles["Italic"])])
        doc.build(story)
        return buffer.getvalue()

    def _section(self, story, styles, title: str, values) -> None:
        story.extend([Paragraph(title, styles["Heading2"]), Spacer(1, 4)])
        items = list(values or []) or ["No structured information available."]
        for value in items:
            story.append(Paragraph(f"• {value}", styles["BodyText"]))
        story.append(Spacer(1, 10))
