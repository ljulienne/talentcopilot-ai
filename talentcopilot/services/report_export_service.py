from __future__ import annotations

from dataclasses import dataclass
from html import escape
from io import BytesIO
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


@dataclass(frozen=True)
class PdfExport:
    data: bytes
    file_name: str
    mime: str = "application/pdf"


class ReportExportService:
    """Central PDF export service for recruiter-facing reports.

    This service formats content already produced by TalentCopilot. It does not
    recalculate scores, rankings, recommendations, confidence, or evidence.
    """

    MIME_TYPE = "application/pdf"

    _REPLACEMENTS = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u00a0": " ",
    }

    def from_markdown(
        self,
        markdown_text: str,
        *,
        file_name: str,
        title: str,
        subtitle: str | None = None,
    ) -> PdfExport:
        return PdfExport(
            data=self.build_pdf(markdown_text, title=title, subtitle=subtitle),
            file_name=self._pdf_name(file_name),
            mime=self.MIME_TYPE,
        )

    def build_pdf(
        self,
        markdown_text: str,
        *,
        title: str,
        subtitle: str | None = None,
    ) -> bytes:
        buffer = BytesIO()
        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title=self._plain_text(title),
            author="TalentCopilot",
            subject=self._plain_text(subtitle or title),
        )

        styles = getSampleStyleSheet()
        styles.add(
            ParagraphStyle(
                name="TCBody",
                parent=styles["BodyText"],
                fontName="Helvetica",
                fontSize=9.5,
                leading=13,
                spaceAfter=5,
            )
        )
        styles.add(
            ParagraphStyle(
                name="TCBullet",
                parent=styles["TCBody"],
                leftIndent=12,
                firstLineIndent=-7,
                bulletIndent=0,
                spaceAfter=4,
            )
        )

        story = [
            Paragraph(escape(self._ascii_safe(title)), styles["Title"]),
            Spacer(1, 5 * mm),
        ]

        if subtitle:
            story.extend(
                [
                    Paragraph(escape(self._ascii_safe(subtitle)), styles["Italic"]),
                    Spacer(1, 4 * mm),
                ]
            )

        content_added = False
        for raw_line in str(markdown_text or "").splitlines():
            line = raw_line.strip()
            if not line:
                story.append(Spacer(1, 2.5 * mm))
                continue

            if line.startswith("# "):
                source_title = self._plain_text(line[2:])
                if source_title and source_title.lower() != title.strip().lower():
                    story.append(
                        Paragraph(escape(self._ascii_safe(source_title)), styles["Heading1"])
                    )
                content_added = True
                continue

            if line.startswith("## "):
                story.append(
                    Paragraph(
                        escape(self._ascii_safe(self._plain_text(line[3:]))),
                        styles["Heading2"],
                    )
                )
                content_added = True
                continue

            if line.startswith("### "):
                story.append(
                    Paragraph(
                        escape(self._ascii_safe(self._plain_text(line[4:]))),
                        styles["Heading3"],
                    )
                )
                content_added = True
                continue

            if line.startswith(("- ", "* ")):
                text = escape(self._ascii_safe(self._plain_text(line[2:])))
                story.append(Paragraph(f"- {text}", styles["TCBullet"]))
                content_added = True
                continue

            text = escape(self._ascii_safe(self._plain_text(line)))
            story.append(Paragraph(text, styles["TCBody"]))
            content_added = True

        if not content_added:
            story.append(Paragraph("No report content is available.", styles["TCBody"]))

        document.build(story)
        pdf = buffer.getvalue()
        buffer.close()

        if not pdf.startswith(b"%PDF"):
            raise RuntimeError("The generated report is not a valid PDF document.")

        return pdf

    @staticmethod
    def _pdf_name(file_name: str) -> str:
        value = str(file_name or "talentcopilot_report").strip()
        if value.lower().endswith(".md"):
            value = value[:-3]
        if not value.lower().endswith(".pdf"):
            value += ".pdf"
        return value

    @classmethod
    def _plain_text(cls, value: str) -> str:
        text = str(value or "")
        text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        text = text.replace("**", "").replace("__", "")
        text = text.replace("`", "")
        text = re.sub(r"^[_*]+|[_*]+$", "", text).strip()
        return text

    @classmethod
    def _ascii_safe(cls, value: str) -> str:
        text = str(value or "")
        for source, target in cls._REPLACEMENTS.items():
            text = text.replace(source, target)
        return text.encode("latin-1", errors="replace").decode("latin-1")
