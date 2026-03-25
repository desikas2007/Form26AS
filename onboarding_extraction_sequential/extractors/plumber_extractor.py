import pdfplumber
from utils.cleaner import clean_text

def extract_text_plumber(filepath):
    """
    Extract raw text from all pages using pdfplumber.
    Returns list of cleaned strings, one per page.
    """
    pages_text = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            raw = page.extract_text() or ""
            pages_text.append(clean_text(raw))
    return pages_text