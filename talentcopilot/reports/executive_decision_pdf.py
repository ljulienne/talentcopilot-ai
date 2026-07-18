"""PDF export for the Executive Decision Brief."""
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def generate_executive_decision_pdf(brief):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=42, leftMargin=42, topMargin=42, bottomMargin=42)
    styles = getSampleStyleSheet()
    elements = [Paragraph('TalentCopilot AI — Executive Decision Brief', styles['Title']), Spacer(1, 14)]
    overview = [
        ['Candidate', brief.candidate_name], ['Official Match', f'{brief.official_match_score:.0f}%'],
        ['Official Rank', f'#{brief.official_rank}'], ['AI Confidence', f'{brief.ai_confidence}%'],
        ['Recommendation', brief.recommendation], ['Business Impact', brief.business_impact],
        ['Expected Ramp-Up', brief.expected_ramp_up],
    ]
    table = Table(overview, colWidths=[130, 345])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),colors.HexColor('#EEF2FF')),('GRID',(0,0),(-1,-1),0.25,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP'),('PADDING',(0,0),(-1,-1),7)]))
    elements += [table, Spacer(1, 16), Paragraph('Executive Summary', styles['Heading2']), Paragraph(brief.executive_summary, styles['BodyText']), Spacer(1, 12)]
    elements.append(Paragraph('Why this candidate?', styles['Heading2']))
    for item in brief.why: elements.append(Paragraph(f'• {item}', styles['BodyText']))
    elements += [Spacer(1, 10), Paragraph('Hiring Risk Matrix', styles['Heading2'])]
    risk_data=[['Dimension','Level','Rationale']]+[[r.name,r.level,r.rationale] for r in brief.risks]
    risk_table=Table(risk_data,colWidths=[90,65,320])
    risk_table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#4F46E5')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.25,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP'),('PADDING',(0,0),(-1,-1),6)]))
    elements += [risk_table, Spacer(1, 12), Paragraph('Interview Priorities', styles['Heading2'])]
    for item in brief.interview_priorities: elements.append(Paragraph(f'• {item}', styles['BodyText']))
    elements += [Spacer(1, 10), Paragraph('Recommended Action', styles['Heading2']), Paragraph(brief.recommended_action, styles['BodyText']), Spacer(1, 8), Paragraph('Ramp-Up Rationale', styles['Heading2']), Paragraph(brief.ramp_up_rationale, styles['BodyText']), Spacer(1, 12), Paragraph('Governance note: this report organises existing evidence and does not replace accountable human judgment.', styles['Italic'])]
    doc.build(elements); buffer.seek(0); return buffer.getvalue()
