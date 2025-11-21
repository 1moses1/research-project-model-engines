"""
PDF Text Extraction Service
"""

from typing import Optional
import PyPDF2


class PDFExtractor:
    """Extracts text from PDF files"""

    def extract(self, file_path: str) -> str:
        """
        Extract text from PDF file

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        try:
            text_content = []

            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)

                print(f"📄 PDF has {num_pages} pages")

                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    text_content.append(text)

            full_text = "\n\n".join(text_content)

            return full_text

        except Exception as e:
            print(f"⚠️ PDF extraction error: {str(e)}")
            return f"Error extracting PDF: {str(e)}"
