import time
import pandas as pd

from extractors.table_extractor import extract_tables
from extractors.field_extractor import extract_fields
from utils.cleaner import tables_to_dataframe


files = {
    "AIS": "input_pdfs/ais_sample.pdf",
    "FORM26AS": "input_pdfs/form26as_sample.pdf",
    "TIS": "input_pdfs/tis_sample.pdf"
}


def process(file_name, path):

    print(f"\nProcessing {file_name}...")

    start = time.time()

    tables = extract_tables(path)
    df = tables_to_dataframe(tables)

    fields = extract_fields(path)

    end = time.time()

    return {
        "df": df,
        "fields": fields,
        "time": end - start,
        "tables": len(tables),
        "rows": len(df)
    }


def save_excel(results):

    writer = pd.ExcelWriter("FINAL_OUTPUT.xlsx", engine="openpyxl")

    summary = []

    for name, data in results.items():

        df = data["df"]
        fields = data["fields"]

        # Save table
        df.to_excel(writer, sheet_name=name, index=False)

        # Save fields
        field_df = pd.DataFrame(list(fields.items()), columns=["Field", "Value"])
        field_df.to_excel(writer, sheet_name=f"{name}_FIELDS", index=False)

        # Summary
        summary.append({
            "Form": name,
            "Time": data["time"],
            "Tables": data["tables"],
            "Rows": data["rows"],
            "PAN": fields.get("PAN"),
            "Name": fields.get("Name")
        })

    summary_df = pd.DataFrame(summary)
    summary_df.to_excel(writer, sheet_name="SUMMARY", index=False)

    writer.close()

    print("\nExcel Generated: FINAL_OUTPUT.xlsx")


if __name__ == "__main__":

    results = {}

    for name, path in files.items():
        results[name] = process(name, path)

    save_excel(results)