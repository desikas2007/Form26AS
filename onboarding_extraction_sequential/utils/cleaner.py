import re

def clean_text(text):
    """
    Clean raw extracted PDF text:
    - Remove excessive whitespace
    - Strip non-printable characters
    - Normalise line endings
    """
    if not text:
        return ""
    
    # Remove non-printable chars except newline and tab
    text = re.sub(r"[^\x20-\x7E\n\t]", " ", text)
    
    # Collapse multiple spaces into one
    text = re.sub(r"[ \t]+", " ", text)
    
    # Collapse multiple blank lines into one
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    return text.strip()
