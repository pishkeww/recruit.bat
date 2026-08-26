from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def generate_pdf(output_path, content: dict):
    doc = SimpleDocTemplate(output_path)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Cover Letter", styles["Heading1"]))
    elements.append(Paragraph(content["cover_letter"], styles["BodyText"]))

    elements.append(Paragraph("Improvements", styles["Heading1"]))
    elements.append(Paragraph(content["improvements"], styles["BodyText"]))

    doc.build(elements)