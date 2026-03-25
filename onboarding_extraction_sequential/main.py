import os
import time
from extractors.field_extractor import extract_form26as

INPUT_DIR = "input_pdfs"
OUTPUT_DIR = "output_results"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_pdf(filename):
    """Process a single PDF file sequentially."""
    filepath = os.path.join(INPUT_DIR, filename)
    print(f"[START] Processing: {filename}")
    
    start = time.time()
    result = extract_form26as(filepath)
    elapsed = time.time() - start
    
    print(f"[DONE]  {filename} → {elapsed:.2f}s")
    return result

def main():
    pdf_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".pdf")]
    
    if not pdf_files:
        print("No PDF files found in input_pdfs/")
        return

    total_start = time.time()
    results = []

    # Sequential: one PDF at a time, in order
    for pdf_file in pdf_files:
        result = process_pdf(pdf_file)
        results.append(result)

    total_elapsed = time.time() - total_start
    print(f"\nAll {len(pdf_files)} files processed in {total_elapsed:.2f}s")
    return results

if __name__ == "__main__":
    main()