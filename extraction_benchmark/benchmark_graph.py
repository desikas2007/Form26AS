import os
import sys
import time
import tempfile
import shutil
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import fitz
import pandas as pd
from extractors.table_extractor import extract_tables
from extractors.field_extractor import extract_fields
from utils.cleaner import tables_to_dataframe
import matplotlib.pyplot as plt


def create_multipage_pdf(input_pdf, num_pages):
    doc = fitz.open(input_pdf)
    output_doc = fitz.open()
    
    for _ in range(num_pages):
        for page_num in range(len(doc)):
            page = doc[page_num]
            output_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
    
    temp_path = os.path.join(tempfile.gettempdir(), f"test_pdf_{num_pages}.pdf")
    output_doc.save(temp_path)
    output_doc.close()
    doc.close()
    return temp_path


def extract_sequential(file_path):
    tables = extract_tables(file_path)
    df = tables_to_dataframe(tables)
    fields = extract_fields(file_path)
    return len(tables), len(df), fields


def extract_threading(file_path):
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
    
    thread1 = threading.Thread(target=extract_table_data)
    thread2 = threading.Thread(target=extract_field_data)
    
    thread1.start()
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    return len(result.get("tables", [])), len(result.get("df", pd.DataFrame())), result.get("fields", {})


def run_benchmark():
    input_pdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), "input_pdfs", "form_26as.pdf")
    
    page_counts = [1, 2, 3, 5, 10]
    
    sequential_times = []
    threading_times = []
    
    print("Running Benchmark...")
    print("=" * 60)
    
    for pages in page_counts:
        print(f"\nTesting with {pages} page(s)...")
        
        if pages == 1:
            test_pdf = input_pdf
        else:
            test_pdf = create_multipage_pdf(input_pdf, pages)
        
        start = time.time()
        extract_sequential(test_pdf)
        seq_time = time.time() - start
        sequential_times.append(seq_time)
        
        start = time.time()
        extract_threading(test_pdf)
        thread_time = time.time() - start
        threading_times.append(thread_time)
        
        print(f"  Sequential: {seq_time:.4f}s | Threading: {thread_time:.4f}s")
        
        if pages > 1:
            os.unlink(test_pdf)
    
    print("\n" + "=" * 60)
    print("Benchmark Complete!")
    
    create_graph(page_counts, sequential_times, threading_times)
    
    return page_counts, sequential_times, threading_times


def create_graph(page_counts, sequential_times, threading_times):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.plot(page_counts, sequential_times, 'b-o', linewidth=2, markersize=8, label='Sequential')
    ax.plot(page_counts, threading_times, 'r-s', linewidth=2, markersize=8, label='Threading')
    
    ax.set_xlabel('Number of Pages', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('PDF Extraction Benchmark: Sequential vs Threading', fontsize=14, fontweight='bold', pad=20)
    
    ax.set_xticks(page_counts)
    ax.set_xlim(0, max(page_counts) + 1)
    ax.set_ylim(0, max(max(sequential_times), max(threading_times)) * 1.1)
    
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='upper left', fontsize=10)
    
    libraries_text = "Libraries Used: pandas | openpyxl | pdfplumber | pymupdf"
    fig.text(0.5, 0.95, libraries_text, ha='center', fontsize=10, 
             fontweight='bold', style='italic',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    
    output_file = "benchmark_graph.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"\nGraph saved to: {output_file}")
    
    create_html_benchmark(page_counts, sequential_times, threading_times)
    print(f"HTML Graph saved to: benchmark_graph.html")


def create_html_benchmark(page_counts, sequential_times, threading_times):
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Extraction Benchmark</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); min-height: 100vh; padding: 40px; display: flex; justify-content: center; align-items: center; }
        .container { max-width: 900px; width: 100%; background: white; border-radius: 20px; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3); overflow: hidden; }
        .libraries { background: #fff3cd; padding: 15px 30px; text-align: center; border-bottom: 3px solid #ffc107; }
        .libraries strong { color: #856404; font-size: 18px; }
        .chart-container { padding: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="libraries">
            <strong>Libraries Used:</strong> pandas | openpyxl | pdfplumber | pymupdf
        </div>
        <div class="chart-container">
            <canvas id="benchmarkChart"></canvas>
        </div>
    </div>
    <script>
        const pageCounts = """ + str(page_counts) + """;
        const sequentialTimes = """ + str(sequential_times) + """;
        const threadingTimes = """ + str(threading_times) + """;
        
        const ctx = document.getElementById('benchmarkChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: pageCounts,
                datasets: [
                    {
                        label: 'Sequential',
                        data: sequentialTimes,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#667eea',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    },
                    {
                        label: 'Threading',
                        data: threadingTimes,
                        borderColor: '#f5576c',
                        backgroundColor: 'rgba(245, 87, 108, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4,
                        pointBackgroundColor: '#f5576c',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 6,
                        pointHoverRadius: 8
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: { position: 'top', labels: { font: { size: 14 }, padding: 20, usePointStyle: true }},
                    tooltip: { backgroundColor: 'rgba(0, 0, 0, 0.8)', titleFont: { size: 14 }, bodyFont: { size: 13 }, padding: 12, cornerRadius: 8 }
                },
                scales: {
                    x: { title: { display: true, text: 'Number of Pages', font: { size: 14, weight: 'bold' } }, grid: { color: 'rgba(0, 0, 0, 0.05)' }},
                    y: { title: { display: true, text: 'Time (seconds)', font: { size: 14, weight: 'bold' } }, grid: { color: 'rgba(0, 0, 0, 0.05)' }, beginAtZero: true }
                }
            }
        });
    </script>
</body>
</html>"""
    
    with open("benchmark_graph.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    with open("benchmark_results.txt", "w") as f:
        f.write("PDF Extraction Benchmark Results\n")
        f.write("=" * 40 + "\n")
        f.write(f"{'Pages':<10} {'Sequential (s)':<20} {'Threading (s)':<20}\n")
        f.write("-" * 50 + "\n")
        for i, pages in enumerate(page_counts):
            f.write(f"{pages:<10} {sequential_times[i]:<20.4f} {threading_times[i]:<20.4f}\n")


if __name__ == "__main__":
    run_benchmark()
