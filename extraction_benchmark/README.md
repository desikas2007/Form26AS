# PDF Table Extraction Benchmark
This project benchmarks sequential vs threading approaches for extracting table data and fields from PDF files (Form 26AS).

## Prerequisites

  Python 3.11 or higher
- pip (Python package manager)

## Required Libraries

Install the following libraries:

```bash
pip install pandas openpyxl pdfplumber pymupdf matplotlib
```

| Library | Purpose |
|---------|---------|
| pandas | Data manipulation and Excel output |
| openpyxl | Excel file generation |
| pdfplumber | PDF table extraction |
| pymupdf | PDF text/field extraction |
| matplotlib | Graph generation for benchmark |

## Project Structure

```
extraction_benchmark/
├── input_pdfs/
│   └── form_26as.pdf          # Input PDF file
├── extractors/
│   ├── table_extractor.py     # Extracts tables from PDF
│   └── field_extractor.py     # Extracts text fields from PDF
├── utils/
│   └── cleaner.py             # Cleans and converts data to DataFrame
├── sequential/
│   └── main.py                # Sequential processing script
├── threading/
│   └── main.py                # Threading processing script
└── README.md
```

## Workflow

### 1. Prepare Input

Place your PDF file in `input_pdfs/` folder with name `form_26as.pdf`.

Or update the file path in the scripts:
- `sequential/main.py`
- `threading/main.py`

### 2. Run Sequential Extraction

```bash
cd sequential
python main.py
```

**Output:**
- `sequential/sequential_output.xlsx` - Extracted tables and fields
- `sequential/sequential_time.txt` - Processing time

### 3. Run Threading Extraction

```bash
cd threading
python main.py
```

**Output:**
- `threading/threading_output.xlsx` - Extracted tables and fields
- `threading/threading_time.txt` - Processing time

### 4. Compare Results

Check the time files to compare performance:

```bash
# View sequential time
type sequential\sequential_time.txt

# View threading time
type threading\threading_time.txt
```

### 5. Generate Benchmark Graph

Run the benchmark script to generate a graph comparing sequential vs threading performance across different page counts:

```bash
python benchmark_graph.py
```

**Output:**
- `benchmark_graph.png` - Graph showing time vs page count
- `benchmark_results.txt` - Detailed results table

## Processing Details

### Sequential Approach
- Processes table extraction first
- Then processes field extraction
- Operations run one after another

### Threading Approach
- Runs table extraction and field extraction simultaneously
- Uses Python threading module
- Both operations run in parallel

## Sample Output

```
SEQUENTIAL PROCESSING
==================================================
Processing form26as...
Extraction completed!
Tables found: 1
Total rows: 11
Fields extracted: {'PAN': None, 'DOB': None, 'Name': None, 'AY': None, 'FY': None}
Time taken: 0.0937 seconds

Output saved to: sequential_output.xlsx
```

```
THREADING PROCESSING
==================================================
Processing form26as with threading...
Extraction completed!
Tables found: 1
Total rows: 11
Fields extracted: {'PAN': None, 'DOB': None, 'Name': None, 'AY': None, 'FY': None}
Time taken: 0.0767 seconds

Output saved to: threading_output.xlsx
```

## Notes

- The actual speedup from threading depends on the PDF size and complexity
- Larger PDFs will show more significant performance improvements with threading
- Field extraction patterns may need adjustment based on your PDF format
