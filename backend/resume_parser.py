from pathlib import Path

from pypdf import PdfReader
from docx import Document


# ==========================================
# PDF TEXT EXTRACTION
# ==========================================

def extract_text_from_pdf(file_path):
    """
    Extract text from a PDF file.
    """

    reader = PdfReader(file_path)

    pages = []

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            pages.append(page_text)

    return "\n".join(pages)


# ==========================================
# DOCX TEXT EXTRACTION
# ==========================================

def extract_text_from_docx(file_path):
    """
    Extract text from a DOCX file.
    """

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return "\n".join(paragraphs)


# ==========================================
# MAIN RESUME PARSER
# ==========================================

def extract_resume_text(file_path):
    """
    Detect file extension and extract text.
    """

    file_path = Path(file_path)

    extension = file_path.suffix.lower()

    if extension == ".pdf":

        return extract_text_from_pdf(
            file_path
        )

    if extension == ".docx":

        return extract_text_from_docx(
            file_path
        )

    raise ValueError(
        "Only PDF and DOCX files are supported."
    )