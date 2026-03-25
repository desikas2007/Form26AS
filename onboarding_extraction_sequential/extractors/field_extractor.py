import pdfplumber
from utils.cleaner import clean_text

def extract_form26as(filepath):
    """
    Extract key fields from Form 26AS sequentially.
    Returns a dict of extracted data.
    """
    data = {
        "filename": filepath,
        "tds_entries": [],
        "tcs_entries": [],
        "pan": None,
    }

    with pdfplumber.open(filepath) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue

            cleaned = clean_text(text)

            # Extract PAN from first page
            if page_num == 0 and "PAN" in cleaned:
                for line in cleaned.split("\n"):
                    if line.strip().startswith("PAN"):
                        data["pan"] = line.split(":")[-1].strip()
                        break

            # Extract tables (TDS / TCS sections)
            tables = page.extract_tables()
            for table in tables:
                if not table:
                    continue
                header = [str(cell).upper() if cell else "" for cell in table[0]]

                if "TAN" in header or "TDS" in str(header):
                    for row in table[1:]:
                        if row and any(row):
                            data["tds_entries"].append(row)

                elif "TCS" in str(header):
                    for row in table[1:]:
                        if row and any(row):
                            data["tcs_entries"].append(row)

    print(f"  → PAN: {data['pan']}, TDS rows: {len(data['tds_entries'])}, "
          f"TCS rows: {len(data['tcs_entries'])}")
    return data