import pdfplumber
import pandas as pd


def extract_with_plumber(file_path, pages='all'):
    all_tables = []
    
    with pdfplumber.open(file_path) as pdf:
        page_range = pages if pages != 'all' else range(1, len(pdf.pages) + 1)
        
        if isinstance(page_range, str) and '-' in page_range:
            start, end = page_range.split('-')
            page_range = range(int(start), int(end) + 1)
        
        for idx in page_range:
            if idx <= len(pdf.pages):
                page = pdf.pages[idx - 1]
                tables = page.extract_tables()
                for table in tables:
                    if table and len(table) > 0:
                        all_tables.append(table)
    
    return all_tables


def extract_page_plumber(file_path, page_num):
    tables = []
    
    with pdfplumber.open(file_path) as pdf:
        if page_num <= len(pdf.pages):
            page = pdf.pages[page_num - 1]
            raw_tables = page.extract_tables()
            
            for table in raw_tables:
                if table and len(table) > 1:
                    header = table[0]
                    col_len = len(header)
                    
                    rows = []
                    for r in table[1:]:
                        if len(r) < col_len:
                            r = list(r) + [None] * (col_len - len(r))
                        if len(r) > col_len:
                            r = r[:col_len]
                        rows.append(r)
                    
                    df = pd.DataFrame(rows, columns=header)
                    tables.append(df)
    
    return tables


def extract_page_text(file_path, page_num):
    with pdfplumber.open(file_path) as pdf:
        if page_num <= len(pdf.pages):
            return pdf.pages[page_num - 1].extract_text()
    return ""
