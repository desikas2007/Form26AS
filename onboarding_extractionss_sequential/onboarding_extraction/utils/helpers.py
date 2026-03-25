import re
import hashlib
from typing import Any, Dict, Optional, List
from datetime import datetime


def sanitize_filename(filename: str) -> str:
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename.strip('_')


def generate_file_hash(file_path: str) -> str:
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def format_currency(amount: float, currency: str = 'INR') -> str:
    if currency == 'INR':
        return f"₹{amount:,.2f}"
    return f"{amount:,.2f}"


def parse_date(date_str: str, formats: List[str] = None) -> Optional[datetime]:
    if formats is None:
        formats = [
            '%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y',
            '%m-%d-%Y', '%m/%d/%Y',
            '%Y-%m-%d', '%Y/%m/%d',
        ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def clean_numeric(value: str) -> Optional[float]:
    if not value:
        return None
    cleaned = re.sub(r'[^\d.]', '', str(value))
    try:
        return float(cleaned)
    except ValueError:
        return None


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                else:
                    items.append((f"{new_key}[{i}]", item))
        else:
            items.append((new_key, v))
    return dict(items)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def merge_extraction_results(results: List[Any]) -> Dict[str, Any]:
    merged = {
        'tables': [],
        'fields': [],
        'summaries': [],
        'total_files': len(results),
        'successful': 0,
        'failed': 0,
    }
    for result in results:
        if result.success:
            merged['successful'] += 1
            merged['tables'].extend(result.tables)
            merged['fields'].extend(result.fields)
            merged['summaries'].append(result.summary)
        else:
            merged['failed'] += 1
    return merged
