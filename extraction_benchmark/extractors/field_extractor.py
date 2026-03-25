import fitz
import re

def extract_fields(file_path):

    doc = fitz.open(file_path)
    text = ""

    for page in doc:
        text += page.get_text()

    fields = {}

    # PAN
    pan = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', text)
    fields["PAN"] = pan.group() if pan else None

    # DOB
    dob = re.search(r'\d{2}/\d{2}/\d{4}', text)
    fields["DOB"] = dob.group() if dob else None

    # Name (simple pattern)
    name = re.search(r'Name\s*[:\-]?\s*([A-Za-z ]+)', text)
    fields["Name"] = name.group(1) if name else None

    # AY
    ay = re.search(r'AY\s*[:\-]?\s*(\d{4}-\d{2})', text)
    fields["AY"] = ay.group(1) if ay else None

    # FY
    fy = re.search(r'FY\s*[:\-]?\s*(\d{4}-\d{2})', text)
    fields["FY"] = fy.group(1) if fy else None

    return fields