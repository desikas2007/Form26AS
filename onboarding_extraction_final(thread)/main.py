import time
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from extractors.pdf_processor import process_page_threaded
from utils.cleaner import clean_and_normalize
from utils.excel_writer import save_to_excel


def select_26as_file():
    input_dir = "input_pdfs"
    if not os.path.exists(input_dir):
        os.makedirs(input_dir)
    
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("\n❌ No PDF files found in input_pdfs folder.")
        print("   Please place your 26AS PDF file in the 'input_pdfs' folder.")
        return None
    
    print("\n📁 Available PDF files:")
    for i, f in enumerate(pdf_files, 1):
        print(f"   {i}. {f}")
    
    if len(pdf_files) == 1:
        selected = pdf_files[0]
        print(f"\n✓ Auto-selected: {selected}")
    else:
        while True:
            try:
                choice = int(input("\nEnter file number to process (or 0 to exit): "))
                if choice == 0:
                    return None
                if 1 <= choice <= len(pdf_files):
                    selected = pdf_files[choice - 1]
                    break
                print("Invalid selection. Try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    return os.path.join(input_dir, selected)


def extract_26as(file_path):
    start_time = time.time()
    overall_start = start_time
    
    print(f"\n📄 Processing: {os.path.basename(file_path)}")
    print("=" * 60)
    
    try:
        from extractors.pdf_processor import get_page_count
        total_pages = get_page_count(file_path)
        print(f"📑 Total pages: {total_pages}")
        
        print("\n⚙️  Processing pages with threaded extraction...")
        page_results = process_page_threaded(file_path, total_pages)
        
        all_tables = []
        all_fields = {}
        page_timing = []
        
        for page_num, result in sorted(page_results.items()):
            page_timing.append({
                "Page": page_num,
                "Extraction Time (s)": result["time"],
                "Tables Found": len(result["tables"]),
                "Status": result["status"]
            })
            
            for table in result["tables"]:
                all_tables.append(table)
            
            for key, value in result["fields"].items():
                if key not in all_fields or not all_fields[key]:
                    all_fields[key] = value
            
            print(f"   Page {page_num}: {result['time']:.2f}s - {len(result['tables'])} tables - {result['status']}")
        
        cleaned_tables = clean_and_normalize(all_tables)
        
        end_time = time.time()
        total_time = end_time - overall_start
        
        summary = {
            "File": os.path.basename(file_path),
            "Total Pages": total_pages,
            "Total Tables Extracted": len(all_tables),
            "Total Tables After Cleaning": len(cleaned_tables),
            "Total Rows": sum(len(df) for df in cleaned_tables),
            "Total Extraction Time (s)": round(total_time, 2),
            "Average Time Per Page (s)": round(total_time / total_pages, 2) if total_pages > 0 else 0,
            "Processed At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("\n" + "=" * 60)
        print("📊 EXTRACTION SUMMARY")
        print("=" * 60)
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        output_file = save_to_excel(cleaned_tables, all_fields, page_timing, summary)
        
        print("\n" + "=" * 60)
        print(f"✅ EXTRACTION COMPLETE!")
        print(f"   Output saved: {output_file}")
        print(f"   Total time: {total_time:.2f} seconds")
        print("=" * 60)
        
        return {
            "success": True,
            "tables": cleaned_tables,
            "fields": all_fields,
            "page_timing": page_timing,
            "summary": summary,
            "output_file": output_file
        }
        
    except Exception as e:
        print(f"\n❌ Error processing file: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("       26AS FORM DATA EXTRACTION TOOL")
    print("       (Page-Level Threaded Processing)")
    print("=" * 60)
    
    file_path = select_26as_file()
    
    if file_path:
        result = extract_26as(file_path)
    else:
        print("\n👋 Exiting. No file selected.")
