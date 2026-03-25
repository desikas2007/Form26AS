import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from extractors.table_extractor import extract_tables
from extractors.field_extractor import extract_fields
from utils.cleaner import tables_to_dataframe


file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "input_pdfs", "form_26as.pdf")


def process_sequential():
    print("SEQUENTIAL PROCESSING")
    print("=" * 50)
    
    print(f"\nProcessing form26as...")
    
    start = time.time()
    
    tables = extract_tables(file_path)
    df = tables_to_dataframe(tables)
    fields = extract_fields(file_path)
    
    end = time.time()
    
    elapsed_time = end - start
    
    print(f"\nExtraction completed!")
    print(f"Tables found: {len(tables)}")
    print(f"Total rows: {len(df)}")
    print(f"Fields extracted: {fields}")
    print(f"\nTime taken: {elapsed_time:.4f} seconds")
    
    output_file = "sequential_output.xlsx"
    writer = pd.ExcelWriter(output_file, engine="openpyxl")
    df.to_excel(writer, sheet_name="Tables", index=False)
    field_df = pd.DataFrame(list(fields.items()), columns=["Field", "Value"])
    field_df.to_excel(writer, sheet_name="Fields", index=False)
    writer.close()
    print(f"\nOutput saved to: {output_file}")
    
    with open("sequential_time.txt", "w") as f:
        f.write(f"Sequential Processing Time: {elapsed_time:.4f} seconds\n")
    
    return elapsed_time


if __name__ == "__main__":
    process_sequential()
