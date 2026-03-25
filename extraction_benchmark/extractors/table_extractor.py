import pdfplumber

def extract_tables(file_path):

    tables = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_tables = page.extract_tables()
            for table in page_tables:
                if table:
                    tables.append(table)

    return tables