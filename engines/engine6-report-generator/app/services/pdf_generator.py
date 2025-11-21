"""
PDF Generator Service
Generates PDF reports from content and charts
"""

from typing import Dict, List
from datetime import datetime
import os
import base64


class PDFGenerator:
    """Generates PDF reports"""

    def __init__(self):
        self.reportlab_available = False
        self._check_reportlab()

    def _check_reportlab(self):
        """Check if ReportLab is available"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            self.reportlab_available = True
            print("✅ ReportLab available for PDF generation")
        except ImportError:
            print("⚠️  ReportLab not available - using text-based fallback")

    def generate_pdf(
        self,
        content: Dict,
        charts: List[Dict],
        output_path: str,
        report_type: str,
        company_name: str
    ) -> Dict:
        """
        Generate PDF report

        Args:
            content: Report content sections
            charts: List of charts (base64 encoded images)
            output_path: Output file path
            report_type: Type of report
            company_name: Company name

        Returns:
            Dictionary with PDF info (file_size, pages, etc.)
        """
        if self.reportlab_available:
            return self._generate_with_reportlab(content, charts, output_path, report_type, company_name)
        else:
            return self._generate_text_fallback(content, output_path, report_type, company_name)

    def _generate_with_reportlab(
        self,
        content: Dict,
        charts: List[Dict],
        output_path: str,
        report_type: str,
        company_name: str
    ) -> Dict:
        """Generate PDF using ReportLab"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
            import io

            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=letter,
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)

            # Container for PDF elements
            elements = []

            # Get styles
            styles = getSampleStyleSheet()

            # Custom styles
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                textColor=colors.HexColor('#34495e'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            )

            subheading_style = ParagraphStyle(
                'CustomSubHeading',
                parent=styles['Heading3'],
                fontSize=12,
                textColor=colors.HexColor('#7f8c8d'),
                spaceAfter=6,
                fontName='Helvetica-Bold'
            )

            body_style = ParagraphStyle(
                'CustomBody',
                parent=styles['BodyText'],
                fontSize=10,
                alignment=TA_JUSTIFY,
                spaceAfter=12
            )

            # Add cover page
            elements.extend(self._create_cover_page(
                company_name, report_type, styles, title_style
            ))

            elements.append(PageBreak())

            # Add table of contents
            elements.append(Paragraph("TABLE OF CONTENTS", heading_style))
            elements.append(Spacer(1, 0.2*inch))

            sections = content.get('sections', {})
            toc_data = []
            page_num = 3  # Start after cover and TOC

            for idx, section_name in enumerate(sections.keys(), 1):
                formatted_name = section_name.replace('_', ' ').title()
                toc_data.append([f"{idx}.", formatted_name, f"Page {page_num}"])
                page_num += 1

            if toc_data:
                toc_table = Table(toc_data, colWidths=[0.5*inch, 4.5*inch, 1*inch])
                toc_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(toc_table)

            elements.append(PageBreak())

            # Add content sections
            for section_name, section_content in sections.items():
                # Section heading
                formatted_name = section_name.replace('_', ' ').title()
                elements.append(Paragraph(formatted_name, heading_style))
                elements.append(Spacer(1, 0.1*inch))

                # Section content
                paragraphs = section_content.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        # Clean and format the paragraph
                        clean_para = para.strip().replace('\n', '<br/>')
                        elements.append(Paragraph(clean_para, body_style))
                        elements.append(Spacer(1, 0.1*inch))

                elements.append(Spacer(1, 0.2*inch))

            # Add charts if available
            if charts:
                elements.append(PageBreak())
                elements.append(Paragraph("VISUALIZATIONS", heading_style))
                elements.append(Spacer(1, 0.2*inch))

                for chart in charts:
                    if 'data' in chart and chart['data']:
                        try:
                            # Decode base64 image
                            img_data = base64.b64decode(chart['data'])
                            img_buffer = io.BytesIO(img_data)

                            # Add chart title
                            if 'title' in chart:
                                elements.append(Paragraph(chart['title'], subheading_style))
                                elements.append(Spacer(1, 0.1*inch))

                            # Add image
                            img = Image(img_buffer, width=5*inch, height=3.5*inch)
                            elements.append(img)
                            elements.append(Spacer(1, 0.3*inch))

                            # Add description
                            if 'description' in chart:
                                elements.append(Paragraph(chart['description'], body_style))
                                elements.append(Spacer(1, 0.2*inch))

                        except Exception as e:
                            print(f"⚠️ Error adding chart: {str(e)}")

            # Add footer
            elements.append(PageBreak())
            elements.extend(self._create_footer(company_name, styles, body_style))

            # Build PDF
            doc.build(elements)

            # Get file info
            file_size = os.path.getsize(output_path)
            estimated_pages = len(elements) // 10  # Rough estimate

            return {
                "file_size": file_size,
                "pages": max(estimated_pages, 3),
                "format": "PDF (ReportLab)",
                "success": True
            }

        except Exception as e:
            print(f"⚠️ ReportLab PDF generation error: {str(e)}")
            # Fallback to text
            return self._generate_text_fallback(content, output_path, report_type, company_name)

    def _create_cover_page(self, company_name: str, report_type: str, styles, title_style) -> List:
        """Create PDF cover page"""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib import colors

        elements = []

        # Add spacing
        elements.append(Spacer(1, 2*inch))

        # Report title
        report_title = report_type.replace('_', ' ').title() + " Report"
        elements.append(Paragraph(f"<b>{report_title}</b>", title_style))
        elements.append(Spacer(1, 0.5*inch))

        # Company name
        company_style = styles['Heading2']
        elements.append(Paragraph(f"<b>{company_name}</b>", company_style))
        elements.append(Spacer(1, 1*inch))

        # Framework
        elements.append(Paragraph("Rwanda NCSA Cybersecurity", styles['Heading3']))
        elements.append(Paragraph("Compliance Assessment", styles['Heading3']))
        elements.append(Spacer(1, 1.5*inch))

        # Date
        date_str = datetime.now().strftime("%B %d, %Y")
        elements.append(Paragraph(date_str, styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))

        # Confidential notice
        confidential_style = styles['Normal']
        elements.append(Paragraph("<b>CONFIDENTIAL</b>", confidential_style))
        elements.append(Paragraph("This report contains proprietary information", confidential_style))

        return elements

    def _create_footer(self, company_name: str, styles, body_style) -> List:
        """Create PDF footer"""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch

        elements = []

        elements.append(Spacer(1, 1*inch))
        elements.append(Paragraph("<b>Document Information</b>", styles['Heading3']))
        elements.append(Spacer(1, 0.1*inch))

        footer_info = [
            f"Company: {company_name}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Framework: Rwanda NCSA Cybersecurity Minimum Standards",
            "Report Generator: ENGINE 5 - Rwanda NCSA Compliance Auditor v3.0.0",
            "",
            "<b>Disclaimer:</b> This report is generated automatically based on compliance data.",
            "The findings and recommendations should be reviewed by qualified security professionals."
        ]

        for line in footer_info:
            elements.append(Paragraph(line, body_style))

        return elements

    def _generate_text_fallback(
        self,
        content: Dict,
        output_path: str,
        report_type: str,
        company_name: str
    ) -> Dict:
        """Generate text-based PDF fallback"""
        try:
            # Generate plain text report
            text_content = []

            # Header
            text_content.append("=" * 80)
            text_content.append(f"{report_type.replace('_', ' ').title()} Report".center(80))
            text_content.append(f"{company_name}".center(80))
            text_content.append("Rwanda NCSA Cybersecurity Compliance Assessment".center(80))
            text_content.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(80))
            text_content.append("=" * 80)
            text_content.append("")

            # Sections
            sections = content.get('sections', {})
            for section_name, section_content in sections.items():
                text_content.append("")
                text_content.append("-" * 80)
                text_content.append(section_name.replace('_', ' ').upper())
                text_content.append("-" * 80)
                text_content.append("")
                text_content.append(section_content)
                text_content.append("")

            # Footer
            text_content.append("")
            text_content.append("=" * 80)
            text_content.append("ENGINE 5: Report Generation Engine")
            text_content.append("Rwanda NCSA Compliance Auditor v3.0.0")
            text_content.append("=" * 80)

            # Write to file (as .txt, but saved with .pdf extension)
            full_text = "\n".join(text_content)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_text)

            file_size = os.path.getsize(output_path)
            estimated_pages = len(text_content) // 50

            print(f"📄 Generated text-based report (ReportLab not available)")

            return {
                "file_size": file_size,
                "pages": max(estimated_pages, 1),
                "format": "Text (fallback)",
                "success": True
            }

        except Exception as e:
            print(f"⚠️ Text fallback error: {str(e)}")
            raise
