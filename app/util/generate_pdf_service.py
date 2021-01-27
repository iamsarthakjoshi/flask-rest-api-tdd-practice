import pdfkit
from flask import render_template
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


class GeneratePDFService:

    __instance = None

    @staticmethod
    def get_instance() -> "GeneratePDFService":
        if not GeneratePDFService.__instance:
            GeneratePDFService.__instance = GeneratePDFService()
        return GeneratePDFService.__instance

    def generate_pdf_with_reportlab(self, logo, title, content, file_name):
        """
        Generate PDF with ReportLab.
        Adjust page structure here if needed.
        """
        doc = SimpleDocTemplate(
            file_name,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name="center", alignment=TA_CENTER))
        Story = []

        im = Image(logo, 5 * inch, 1 * inch)
        Story.append(im)

        # Set title of the pdf
        Story.append(Spacer(1, 6))
        ptext = "<font size=8>%s</font>" % title

        Story.append(Spacer(1, 8))
        Story.append(Paragraph(ptext, styles["center"]))
        Story.append(Spacer(1, 22))

        # Set policy wordings
        ptext = "<font size=11>Following are some rules:</font>"
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 10))
        ptext = content
        Story.append(Paragraph(ptext, styles["Normal"]))
        Story.append(Spacer(1, 0.5 * inch))

        ptext = "<font size=9>Thank you very much and we look forward to serving you.</font>"
        Story.append(Paragraph(ptext, styles["center"]))
        doc.build(Story)

    def generate_pdf_with_pdfkit(
        self,
        logo,
        title,
        content,
        file_name="sample_pdf.pdf",
        get_response_content=False,
    ):
        """
        Generate PDF out of HTML template file. Library used is pdfkit.
        But most importantly you have to install "wkhtmltox" package on the host/server machine
        Only then pdfkit is able to generate PDF file from HTML template files
        More details in README.md
        """
        context = {
            "logo": logo,
            "title": title,
            "content": content,
            "filename": file_name,
            "enumerate": enumerate,
        }
        rendered = render_template("sample_pdf_template.html", **context)
        pdf = pdfkit.from_string(rendered, False if get_response_content else file_name)
        return pdf
