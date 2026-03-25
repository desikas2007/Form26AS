import time
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from extractors.table_extractor import extract_tables
from extractors.field_extractor import extract_fields
from utils.cleaner import tables_to_dataframe


file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "input_pdfs", "form_26as.pdf")

result = {}
lock = threading.Lock()


def extract_table_data():
    tables = extract_tables(file_path)
    df = tables_to_dataframe(tables)
    with lock:
        result["tables"] = tables
        result["df"] = df


def extract_field_data():
    fields = extract_fields(file_path)
    with lock:
        result["fields"] = fields


def process_threading():
    print("THREADING PROCESSING")
    print("=" * 50)
    
    print(f"\nProcessing form26as with threading...")
    
    start = time.time()
    
    thread1 = threading.Thread(target=extract_table_data)
    thread2 = threading.Thread(target=extract_field_data)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    end = time.time()
    elapsed_time = end - start
    
    print(f"\nExtraction completed!")
    print(f"Tables found: {len(result.get('tables', []))}")
    print(f"Total rows: {len(result.get('df', pd.DataFrame()))}")
    print(f"Fields extracted: {result.get('fields', {})}")
    print(f"\nTime taken: {elapsed_time:.4f} seconds")
    
    output_file = "threading_output.xlsx"
    writer = pd.ExcelWriter(output_file, engine="openpyxl")
    result["df"].to_excel(writer, sheet_name="Tables", index=False)
    field_df = pd.DataFrame(list(result["fields"].items()), columns=["Field", "Value"])
    field_df.to_excel(writer, sheet_name="Fields", index=False)
    writer.close()
    print(f"\nOutput saved to: {output_file}")
    
    with open("threading_time.txt", "w") as f:
        f.write(f"Threading Processing Time: {elapsed_time:.4f} seconds\n")
    
    return elapsed_time


if __name__ == "__main__":
    process_threading()
