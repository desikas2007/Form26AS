import os
import sys
import argparse
from typing import List, Dict, Any

import pdfplumber
import pandas as pd
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ExtractedTable:
    table_name: str
    headers: List[str]
    rows: List[List[str]]
    page_number: int
    confidence: float = 1.0


@dataclass
class ExtractedField:
    key: str
    value: str
    section: str
    page: int
    confidence: float = 1.0


@dataclass
class ExtractionResult:
    file_path: str
    tables: List[ExtractedTable] = field(default_factory=list)
    fields: List[ExtractedField] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: str = None


class DataCleaner:
    def __init__(self):
        self.amount_pattern = r'[\u20b9\s]*\d{1,3}(?:,\d{3})*(?:\.\d{2})?'
        self.pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]'
        self.tan_pattern = r'[A-Z]{4}[0-9]{5}[A-Z]'

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\u20b9.\-,():%/]', '', text)
        return text.strip()

    def extract_amount(self, text: str) -> float:
        match = re.search(self.amount_pattern, text)
        if match:
            amount = re.sub(r'[\u20b9\s,]', '', match.group())
            try:
                return float(amount)
            except ValueError:
                return 0.0
        return 0.0

    def extract_pan(self, text: str) -> str:
        match = re.search(self.pan_pattern, text)
        return match.group(0) if match else None

    def extract_tan(self, text: str) -> str:
        match = re.search(self.tan_pattern, text)
        return match.group(0) if match else None

    def normalize_table(self, table: ExtractedTable) -> ExtractedTable:
        return ExtractedTable(
            table_name=table.table_name,
            headers=[self.clean_text(h) for h in table.headers],
            rows=[[self.clean_text(c) for c in row] for row in table.rows],
            page_number=table.page_number,
            confidence=table.confidence
        )


class PDFExtractor:
    KEY_PATTERNS = {
        'PAN': r'(?:PAN|Permanent Account Number)[:\s]*([A-Z]{5}[0-9]{4}[A-Z])',
        'Name': r'(?:Name|Assessee Name)[:\s]*(.+?)(?:\n|$)',
        'Assessment Year': r'(?:Assessment Year|AY)[:\s]*(\d{4}-\d{4})',
        'Financial Year': r'(?:Financial Year|FY)[:\s]*(\d{4}-\d{4})',
        'TAN': r'(?:TAN|Tax Deduction Account Number)[:\s]*([A-Z]{4}[0-9]{5}[A-Z])',
        'Total Tax Deducted': r'(?:Total Tax Deducted|TDS)[:\s]*([\d,]+\.?\d*)',
        'Total Tax Collected': r'(?:Total Tax Collected|TCS)[:\s]*([\d,]+\.?\d*)',
        'Section Code': r'Section\s*(\d+[A-Z]?)',
        'Claim Status': r'(?:Claim Status|Status)[:\s]*(Verified|Pending|Discrepancy)',
    }

    def __init__(self, cleaner: DataCleaner):
        self.cleaner = cleaner

    def extract_tables(self, pdf_path: str) -> List[ExtractedTable]:
        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for idx, table_data in enumerate(page_tables):
                            if table_data and len(table_data) > 1:
                                headers = [str(h).strip() if h else "" for h in table_data[0]]
                                rows = [[str(c).strip() if c else "" for c in row] for row in table_data[1:]]
                                tables.append(ExtractedTable(
                                    table_name=f"Table_{page_num}_{idx+1}",
                                    headers=headers,
                                    rows=rows,
                                    page_number=page_num
                                ))
        except Exception as e:
            logger.error(f"Error extracting tables: {e}")
        return tables

    def extract_fields(self, pdf_path: str) -> List[ExtractedField]:
        fields = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    for field_name, pattern in self.KEY_PATTERNS.items():
                        for match in re.finditer(pattern, text, re.IGNORECASE):
                            value = match.group(1) if match.lastindex else match.group(0)
                            fields.append(ExtractedField(
                                key=field_name,
                                value=self.cleaner.clean_text(value),
                                section="General",
                                page=page_num
                            ))
        except Exception as e:
            logger.error(f"Error extracting fields: {e}")
        return fields

    def extract_raw_text(self, pdf_path: str) -> Dict[str, Any]:
        raw_data = {'pages': [], 'metadata': {}}
        try:
            with pdfplumber.open(pdf_path) as pdf:
                raw_data['metadata']['page_count'] = len(pdf.pages)
                raw_data['metadata']['file_name'] = os.path.basename(pdf_path)
                for page_num, page in enumerate(pdf.pages, start=1):
                    text = page.extract_text() or ""
                    raw_data['pages'].append({
                        'page_number': page_num,
                        'text': text,
                        'lines': text.split('\n') if text else []
                    })
        except Exception as e:
            logger.error(f"Error extracting raw data: {e}")
        return raw_data


class SummaryGenerator:
    def __init__(self, cleaner: DataCleaner):
        self.cleaner = cleaner

    def generate_summary(self, result: ExtractionResult) -> Dict[str, Any]:
        summary = {
            'total_tables': len(result.tables),
            'total_fields': len(result.fields),
            'pages_processed': set(),
            'pan_details': {},
            'tax_summary': {},
            'total_amount': 0.0,
            'table_details': []
        }

        for table in result.tables:
            summary['pages_processed'].add(table.page_number)
            table_amount = sum(self.cleaner.extract_amount(' '.join(row)) for row in table.rows)
            summary['total_amount'] += table_amount
            summary['table_details'].append({
                'name': table.table_name,
                'rows': len(table.rows),
                'headers': table.headers
            })

        for field in result.fields:
            summary['pages_processed'].add(field.page)
            if field.key in ['PAN', 'Name', 'Assessment Year', 'Financial Year', 'TAN']:
                summary['pan_details'][field.key] = field.value
            elif 'Tax' in field.key:
                amount = self.cleaner.extract_amount(field.value)
                if amount:
                    summary['tax_summary'][field.key] = amount

        summary['pages_processed'] = len(summary['pages_processed'])
        return summary


def process_single_pdf(pdf_path: str) -> ExtractionResult:
    logger.info(f"Processing: {pdf_path}")
    result = ExtractionResult(file_path=pdf_path)
    
    cleaner = DataCleaner()
    extractor = PDFExtractor(cleaner)
    summary_gen = SummaryGenerator(cleaner)

    try:
        result.tables = extractor.extract_tables(pdf_path)
        result.tables = [cleaner.normalize_table(t) for t in result.tables]
        result.fields = extractor.extract_fields(pdf_path)
        result.raw_data = extractor.extract_raw_text(pdf_path)
        result.summary = summary_gen.generate_summary(result)
        logger.info(f"Completed: {pdf_path}")
    except Exception as e:
        result.success = False
        result.error = str(e)
        logger.error(f"Failed: {pdf_path} - {e}")

    return result


def process_directory(input_dir: str, output_dir: str, max_workers: int = 4) -> List[ExtractionResult]:
    pdf_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return []

    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_pdf = {executor.submit(process_single_pdf, pdf): pdf for pdf in pdf_files}
        for future in as_completed(future_to_pdf):
            try:
                results.append(future.result())
            except Exception as e:
                logger.error(f"Exception: {e}")

    return results


def print_results(results: List[ExtractionResult]):
    for result in results:
        if not result.success:
            continue
        print(f"\n{'='*60}")
        print(f"FILE: {os.path.basename(result.file_path)}")
        print(f"{'='*60}")
        print(f"\n[SUMMARY]")
        print(f"  Total Tables: {len(result.tables)}")
        print(f"  Total Fields: {len(result.fields)}")
        print(f"  Pages Processed: {result.summary.get('pages_processed', 0)}")
        print(f"  Total Amount: {result.summary.get('total_amount', 0)}")
        
        print(f"\n[TABLES]")
        for table in result.tables:
            print(f"\n  Table: {table.table_name} (Page {table.page_number})")
            print(f"  Headers: {table.headers}")
            for i, row in enumerate(table.rows[:5]):
                print(f"    Row {i+1}: {row}")

        print(f"\n[KEY FIELDS]")
        for field in result.fields:
            print(f"  {field.key}: {field.value}")


def save_output(results: List[ExtractionResult], output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None
    
    all_tables = []
    all_fields = []

    for result in results:
        if result.success:
            for table in result.tables:
                if table.rows:
                    df = pd.DataFrame(table.rows, columns=table.headers)
                    df['source_file'] = os.path.basename(result.file_path)
                    df['table_name'] = table.table_name
                    all_tables.append(df)

            for field in result.fields:
                all_fields.append({
                    'source_file': os.path.basename(result.file_path),
                    'key': field.key,
                    'value': field.value,
                    'section': field.section,
                    'page': field.page
                })

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        if all_tables:
            pd.concat(all_tables, ignore_index=True).to_excel(writer, sheet_name='Tables', index=False)
        if all_fields:
            pd.DataFrame(all_fields).to_excel(writer, sheet_name='Fields', index=False)
        if results and results[0].summary:
            pd.DataFrame([results[0].summary]).to_excel(writer, sheet_name='Summary', index=False)

    logger.info(f"Output saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='PDF Data Extraction Tool')
    parser.add_argument('-i', '--input', required=True, help='Input PDF file or directory')
    parser.add_argument('-o', '--output', required=True, help='Output file path (.xlsx)')
    parser.add_argument('-w', '--workers', type=int, default=4, help='Number of parallel workers')
    args = parser.parse_args()

    if os.path.isfile(args.input):
        results = [process_single_pdf(args.input)]
        print_results(results)
        save_output(results, args.output)
        print(f"\nOutput saved to: {args.output}")
        
    elif os.path.isdir(args.input):
        results = process_directory(args.input, os.path.dirname(args.output), args.workers)
        successful = sum(1 for r in results if r.success)
        print(f"\nProcessed {len(results)} files, {successful} successful")
        print_results(results)
        save_output(results, args.output)
        print(f"\nOutput saved to: {args.output}")
        
    else:
        print(f"Error: Input path does not exist: {args.input}")


if __name__ == '__main__':
    main()
