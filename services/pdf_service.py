
import pymupdf as fitz
import os

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    text_content = []
    try:
        with fitz.open(pdf_path) as pdf_doc:
            for page in pdf_doc:
                text = page.get_text()
                text_content.append(text)
                # Add a page break marker (optional, but good for structure)
                text_content.append("\n\f") 
    except Exception as e:
        raise RuntimeError(f"Error extracting text from PDF: {e}")

    return "".join(text_content)
