EXTRACTION_CONFIG = {
    'max_workers': 4,
    'supported_formats': ['.pdf'],
    'table_confidence_threshold': 0.5,
    'enable_camelot_fallback': True,
    'camelot_flavor': 'lattice',
    'output_formats': ['xlsx', 'csv', 'json'],
}

PATTERNS = {
    'pan': r'[A-Z]{5}[0-9]{4}[A-Z]',
    'tan': r'[A-Z]{4}[0-9]{5}[A-Z]',
    'aadhaar': r'\d{4}\s\d{4}\s\d{4}',
    'assessment_year': r'\d{4}-\d{4}',
    'financial_year': r'\d{4}-\d{4}',
    'date': r'\d{2}[-/\.]\d{2}[-/\.]\d{4}',
    'amount': r'[\u20b9₹Rs.,\s]*\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
}

TABLE_TYPES = {
    'tax_deducted': ['tax deducted', 'tds', 'deduction'],
    'tax_collected': ['tax collected', 'tcs', 'collection'],
    'challan': ['challan', 'payment', 'deposit'],
    'deductor': ['deductor', 'employer', 'deducter'],
    'refund': ['refund', 'adjustment'],
}

SECTION_MAPPING = {
    'A': 'Basic Details',
    'B': 'Summary of Tax Deducted at Source',
    'C': 'Summary of Tax Collected at Source',
    'D': 'TDS/TCS Verification',
    'E': 'Tax Paid',
    'F': 'Refund Details',
    'G': 'Short Tax Deduction Details',
}

KEY_FIELDS = [
    'PAN', 'Name', 'Assessment Year', 'Financial Year', 'TAN',
    'Total Tax Deducted', 'Total Tax Collected', 'Claim Status',
    'Section Code', 'Certificate Number', 'Date'
]
