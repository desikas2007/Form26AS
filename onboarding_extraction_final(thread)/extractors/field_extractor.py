import fitz
import re


def extract_fields(file_path):
    doc = fitz.open(file_path)
    full_text = ""
    
    for page in doc:
        full_text += page.get_text() + "\n"
    
    fields = {}
    
    pan = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', full_text)
    fields["PAN"] = pan.group(0) if pan else None
    
    dob = re.search(r'\d{2}/\d{2}/\d{4}', full_text)
    fields["DOB"] = dob.group(0) if dob else None
    
    name_patterns = [
        r'(?:Name|Assessee Name|Taxpayer Name)\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$|,)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
    ]
    for pattern in name_patterns:
        name = re.search(pattern, full_text, re.IGNORECASE)
        if name:
            fields["Name"] = name.group(1).strip()
            break
    
    ay = re.search(r'AY\s*[:\-]?\s*(\d{4}-\d{4})', full_text)
    if not ay:
        ay = re.search(r'Assessment Year\s*[:\-]?\s*(\d{4}-\d{4})', full_text, re.IGNORECASE)
    fields["AY"] = ay.group(1) if ay else None
    
    fy = re.search(r'FY\s*[:\-]?\s*(\d{4}-\d{4})', full_text)
    if not fy:
        fy = re.search(r'Financial Year\s*[:\-]?\s*(\d{4}-\d{4})', full_text, re.IGNORECASE)
    fields["FY"] = fy.group(1) if fy else None
    
    tan = re.search(r'TAN\s*[:\-]?\s*([A-Z]{10})', full_text, re.IGNORECASE)
    fields["TAN"] = tan.group(1) if tan else None
    
    cin = re.search(r'CIN\s*[:\-]?\s*([A-Z0-9]+)', full_text, re.IGNORECASE)
    fields["CIN"] = cin.group(1) if cin else None
    
    total_tax = re.search(r'(?:Total Tax|Balance Tax|Balance Tax Payable)\s*[:\-]?\s*([\d,.]+)', full_text, re.IGNORECASE)
    fields["TotalTax"] = total_tax.group(1).replace(',', '') if total_tax else None
    
    tds_patterns = [
        r'(?:TDS|Total TDS Amount)\s*[:\-]?\s*([\d,.]+)',
        r'TDS\s*\((\d+)\)\s*[:\-]?\s*([\d,.]+)',
    ]
    for pattern in tds_patterns:
        tds = re.search(pattern, full_text, re.IGNORECASE)
        if tds:
            groups = tds.groups()
            fields["TDSAmount"] = groups[-1].replace(',', '') if isinstance(groups[-1], str) else str(groups[-1])
            break
    
    tcs = re.search(r'(?:TCS|Total TCS)\s*[:\-]?\s*([\d,.]+)', full_text, re.IGNORECASE)
    fields["TCSAmount"] = tcs.group(1).replace(',', '') if tcs else None
    
    refund = re.search(r'(?:Refund|Due Refund)\s*[:\-]?\s*([\d,.]+)', full_text, re.IGNORECASE)
    fields["RefundAmount"] = refund.group(1).replace(',', '') if refund else None
    
    tax_paid = re.search(r'(?:Tax Paid|Advance Tax)\s*[:\-]?\s*([\d,.]+)', full_text, re.IGNORECASE)
    fields["TaxPaid"] = tax_paid.group(1).replace(',', '') if tax_paid else None
    
    sections = re.findall(r'Section\s*(\d+[A-Z]?)\s*[:\-]?\s*([\d,.]+)', full_text)
    if sections:
        fields["TDS_Sections"] = "; ".join([f"Sec {s}: {a}" for s, a in sections[:5]])
    
    doc.close()
    return fields


def extract_page_specific_fields(file_path, page_num):
    doc = fitz.open(file_path)
    
    if page_num > len(doc):
        doc.close()
        return {}
    
    page = doc[page_num - 1]
    text = page.get_text()
    
    fields = {}
    
    pan = re.search(r'[A-Z]{5}[0-9]{4}[A-Z]', text)
    fields["PAN"] = pan.group(0) if pan else None
    
    name = re.search(r'Name\s*[:\-]?\s*([A-Za-z\s]+?)(?:\n|$)', text)
    fields["Name"] = name.group(1).strip() if name else None
    
    ay = re.search(r'AY\s*[:\-]?\s*(\d{4}-\d{4})', text)
    fields["AY"] = ay.group(1) if ay else None
    
    section_data = re.findall(r'(Section\s*\d+[A-Z]?)\s*[:\-]?\s*([\d,.]+)', text)
    if section_data:
        fields["Sections"] = section_data
    
    doc.close()
    return fields
