from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
import io

def generate_contract_pdf(analysis_data):
    """
    Generate a professional PDF report for contract analysis
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#C2410C'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1C1917'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        spaceAfter=12
    )
    
    # Title
    story.append(Paragraph('🧾 LegalMe Contract Review Report', title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # 1. Document Overview
    story.append(Paragraph('1. Document Overview', heading_style))
    
    overview_data = [
        ['Type:', analysis_data.get('document_type', 'General').capitalize()],
        ['Filename:', analysis_data.get('filename', 'N/A')],
        ['Date Reviewed:', datetime.fromisoformat(analysis_data.get('timestamp')).strftime('%d/%m/%Y')],
        ['Risk Level:', f"{get_risk_emoji(analysis_data.get('risk_level'))} {analysis_data.get('risk_level', 'unknown').capitalize()}"]
    ]
    
    overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F5F5F4')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    story.append(overview_table)
    story.append(Spacer(1, 0.3*inch))
    
    # 2. Summary
    story.append(Paragraph('2. Summary', heading_style))
    story.append(Paragraph(analysis_data.get('summary', 'No summary available.'), body_style))
    story.append(Spacer(1, 0.2*inch))
    
    # 3. Safe Clauses
    if analysis_data.get('clauses_safe'):
        story.append(Paragraph('3. Clauses That Are Acceptable (🟢)', heading_style))
        for clause in analysis_data['clauses_safe']:
            story.append(Paragraph(f"<b>• {clause.get('explanation', 'N/A')}</b>", body_style))
            story.append(Paragraph(f"<i>Excerpt: ...{clause.get('clause', 'N/A')[:100]}...</i>", body_style))
            story.append(Paragraph(f"Reference: {clause.get('law', 'N/A')}", body_style))
            story.append(Spacer(1, 0.1*inch))
        story.append(Spacer(1, 0.2*inch))
    
    # 4. Attention Clauses
    if analysis_data.get('clauses_attention'):
        story.append(Paragraph('4. Clauses That May Be Problematic (🟡)', heading_style))
        for clause in analysis_data['clauses_attention']:
            story.append(Paragraph(f"<b>• {clause.get('explanation', 'N/A')}</b>", body_style))
            story.append(Paragraph(f"<i>Excerpt: ...{clause.get('clause', 'N/A')[:100]}...</i>", body_style))
            story.append(Paragraph(f"Reference: {clause.get('law', 'N/A')}", body_style))
            story.append(Spacer(1, 0.1*inch))
        story.append(Spacer(1, 0.2*inch))
    
    # 5. Violating Clauses
    if analysis_data.get('clauses_violates'):
        story.append(Paragraph('5. Clauses That Violate German Law (🔴)', heading_style))
        for clause in analysis_data['clauses_violates']:
            story.append(Paragraph(f"<b>• {clause.get('explanation', 'N/A')}</b>", body_style))
            story.append(Paragraph(f"<i>Excerpt: ...{clause.get('clause', 'N/A')[:100]}...</i>", body_style))
            story.append(Paragraph(f"Reference: {clause.get('law', 'N/A')}", body_style))
            story.append(Spacer(1, 0.1*inch))
        story.append(Spacer(1, 0.2*inch))
    
    # 6. Recommendations
    story.append(Paragraph('6. Recommendations', heading_style))
    story.append(Paragraph(analysis_data.get('recommendations', 'Please consult with a legal professional.'), body_style))
    story.append(Spacer(1, 0.3*inch))
    
    # 7. Full Text (optional, first 2000 chars)
    story.append(PageBreak())
    story.append(Paragraph('7. Full Extracted Text', heading_style))
    extracted_text = analysis_data.get('extracted_text', '')
    if len(extracted_text) > 3000:
        extracted_text = extracted_text[:3000] + '...\n\n[Text truncated for PDF report]'
    story.append(Paragraph(extracted_text.replace('\n', '<br/>'), body_style))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def get_risk_emoji(risk_level):
    if risk_level == 'high':
        return '🔴'
    elif risk_level == 'medium':
        return '🟡'
    else:
        return '🟢'
