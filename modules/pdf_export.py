# modules/pdf_export.py

import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
import io

def clean_text(text: str) -> str:
    """Remove markdown and special characters"""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    text = re.sub(r'`(.*?)`', r'\1', text)
    text = text.replace('|', ' ')
    text = text.replace('&', '&amp;')
    text = text.replace('<b>', '<b>').replace('</b>', '</b>')
    text = text.encode('ascii', errors='ignore').decode('ascii')
    text = re.sub(r' +', ' ', text)
    return text.strip()

def markdown_to_pdf(markdown_text: str,
                    recommendations: str = None) -> bytes:
    try:
        print("Generating PDF...")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Title'],
            fontSize=16,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        h1_style = ParagraphStyle(
            'H1',
            parent=styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#2980B9'),
            spaceAfter=8
        )
        h2_style = ParagraphStyle(
            'H2',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=6
        )
        h3_style = ParagraphStyle(
            'H3',
            parent=styles['Heading3'],
            fontSize=11,
            textColor=colors.HexColor('#E74C3C'),
            spaceAfter=5
        )
        normal_style = ParagraphStyle(
            'Normal',
            parent=styles['Normal'],
            fontSize=10,
            spaceAfter=4,
            leading=14
        )
        bullet_style = ParagraphStyle(
            'Bullet',
            parent=styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceAfter=3,
            leading=14
        )
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            fontName='Helvetica-Oblique'
        )

        story = []

        # Title
        story.append(Paragraph("EduAssist - Cleaned Notes", title_style))
        story.append(Spacer(1, 0.2 * inch))

        def process_lines(text, story):
            for line in text.split("\n"):
                c = clean_text(line)
                if not c:
                    story.append(Spacer(1, 0.1 * inch))
                    continue
                if re.match(r'^[-* |]+$', c):
                    continue

                try:
                    if line.startswith("# "):
                        story.append(Paragraph(c, h1_style))
                    elif line.startswith("## "):
                        story.append(Paragraph(c, h2_style))
                    elif line.startswith("### "):
                        story.append(Paragraph(c, h3_style))
                    elif line.strip().startswith(("- ", "* ")):
                        story.append(Paragraph(f"- {c}", bullet_style))
                    elif re.match(r'^\d+\.', line.strip()):
                        story.append(Paragraph(c, bullet_style))
                    elif line.strip().startswith(">"):
                        story.append(Paragraph(c, disclaimer_style))
                    else:
                        story.append(Paragraph(c, normal_style))
                except Exception as e:
                    # Skip problematic lines
                    continue

        # Process notes
        process_lines(markdown_text, story)

        # Process recommendations
        if recommendations and recommendations.strip():
            story.append(Spacer(1, 0.3 * inch))
            story.append(Paragraph("AI Recommendations", title_style))
            story.append(Spacer(1, 0.2 * inch))
            process_lines(recommendations, story)

            story.append(Spacer(1, 0.2 * inch))
            story.append(Paragraph(
                "All recommendations are AI-generated. "
                "Please verify with your textbook or professor.",
                disclaimer_style
            ))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        print("PDF generated!")
        return pdf_bytes

    except Exception as e:
        print(f"PDF Error: {str(e)}")
        return b""