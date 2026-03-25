import time
import fitz
import pdfplumber
import camelot
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_page_count(file_path):
    with pdfplumber.open(file_path) as pdf:
        return len(pdf.pages)


def extract_page_camelot(file_path, page_num):
    start_time = time.time()
    result = {
        "page": page_num,
        "tables": [],
        "fields": {},
        "time": 0,
        "status": "Success"
    }
    
    try:
        tables = camelot.read_pdf(file_path, pages=str(page_num))
        
        for t in tables:
            if t.df is not None and not t.df.empty and t.df.shape[0] > 1:
                df = t.df.copy()
                df.columns = df.iloc[0]
                df = df[1:]
                df = df.dropna(how='all')
                if not df.empty:
                    result["tables"].append(df)
        
        if not result["tables"]:
            result["status"] = "No tables (Camelot)"
            
    except Exception as e:
        result["status"] = f"Camelot error: {str(e)[:20]}"
    
    result["time"] = round(time.time() - start_time, 3)
    return result


def extract_page_plumber(file_path, page_num):
    start_time = time.time()
    result = {
        "page": page_num,
        "tables": [],
        "fields": {},
        "time": 0,
        "status": "Success"
    }
    
    try:
        with pdfplumber.open(file_path) as pdf:
            page = pdf.pages[page_num - 1]
            tables = page.extract_tables()
            
            for table in tables:
                if table and len(table) > 1:
                    import pandas as pd
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
                    df = df.dropna(how='all')
                    if not df.empty:
                        result["tables"].append(df)
            
            if not result["tables"]:
                result["status"] = "No tables (Plumber)"
                
    except Exception as e:
        result["status"] = f"Plumber error: {str(e)[:20]}"
    
    result["time"] = round(time.time() - start_time, 3)
    return result


def extract_page_fields(file_path, page_num):
    start_time = time.time()
    fields = {}
    
    try:
        doc = fitz.open(file_path)
        if page_num <= len(doc):
            page = doc[page_num - 1]
            text = page.get_text()
            
            import re
            
            pan = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', text)
            fields["PAN"] = pan.group(0) if pan else None
            
            dob = re.search(r'\d{2}/\d{2}/\d{4}', text)
            fields["DOB"] = dob.group(0) if dob else None
            
            name = re.search(r'(?:Name|Assessee Name|taxpayer)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$)', text, re.IGNORECASE)
            if name:
                fields["Name"] = name.group(1).strip()
            
            ay = re.search(r'AY\s*[:\-]?\s*(\d{4}-\d{4})', text)
            if not ay:
                ay = re.search(r'Assessment Year\s*[:\-]?\s*(\d{4}-\d{4})', text, re.IGNORECASE)
            fields["AY"] = ay.group(1) if ay else None
            
            fy = re.search(r'FY\s*[:\-]?\s*(\d{4}-\d{4})', text)
            if not fy:
                fy = re.search(r'Financial Year\s*[:\-]?\s*(\d{4}-\d{4})', text, re.IGNORECASE)
            fields["FY"] = fy.group(1) if fy else None
            
            tan = re.search(r'TAN\s*[:\-]?\s*([A-Z]{10})', text, re.IGNORECASE)
            fields["TAN"] = tan.group(1) if tan else None
            
            cin = re.search(r'CIN\s*[:\-]?\s*([A-Z0-9]+)', text, re.IGNORECASE)
            fields["CIN"] = cin.group(1) if cin else None
            
            total_tax = re.search(r'(?:Total Tax|Balance Tax)\s*[:\-]?\s*([\d,.]+)', text, re.IGNORECASE)
            fields["TotalTax"] = total_tax.group(1) if total_tax else None
            
            tds_amount = re.search(r'(?:TDS|Total TDS)\s*[:\-]?\s*([\d,.]+)', text, re.IGNORECASE)
            fields["TDSAmount"] = tds_amount.group(1) if tds_amount else None
            
        doc.close()
        
    except Exception:
        pass
    
    return fields


def process_single_page(file_path, page_num):
    start_time = time.time()
    
    camelot_result = extract_page_camelot(file_path, page_num)
    
    if camelot_result["tables"]:
        tables = camelot_result["tables"]
        method = "Camelot"
    else:
        plumber_result = extract_page_plumber(file_path, page_num)
        tables = plumber_result["tables"]
        method = "Plumber"
    
    if not tables:
        try:
            doc = fitz.open(file_path)
            page = doc[page_num - 1]
            text = page.get_text()
            
            if text.strip():
                import pandas as pd
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                
                if len(lines) > 2:
                    df = pd.DataFrame({'Line': lines})
                    tables = [df]
                else:
                    tables = []
            doc.close()
        except:
            tables = []
    
    fields = extract_page_fields(file_path, page_num)
    
    total_time = time.time() - start_time
    
    return {
        "page": page_num,
        "tables": tables,
        "fields": fields,
        "time": round(total_time, 3),
        "method": method,
        "status": "Success"
    }


def process_page_threaded(file_path, total_pages, max_workers=None):
    if max_workers is None:
        max_workers = min(4, total_pages)
    
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_single_page, file_path, page_num): page_num
            for page_num in range(1, total_pages + 1)
        }
        
        for future in as_completed(futures):
            page_num = futures[future]
            try:
                result = future.result()
                results[page_num] = result
            except Exception as e:
                results[page_num] = {
                    "page": page_num,
                    "tables": [],
                    "fields": {},
                    "time": 0,
                    "status": f"Error: {str(e)[:30]}"
                }
    
    return results
