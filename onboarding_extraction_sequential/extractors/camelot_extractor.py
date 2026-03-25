import camelot

def extract_tables_camelot(filepath, flavor="lattice"):
    """
    Use Camelot to extract bordered/lattice tables from a PDF.
    flavor: 'lattice' for tables with borders, 'stream' for borderless.
    """
    print(f"  [camelot] Reading tables from: {filepath}")
    tables = camelot.read_pdf(filepath, pages="all", flavor=flavor)
    
    extracted = []
    for i, table in enumerate(tables):
        df = table.df
        print(f"  [camelot] Table {i+1}: {df.shape[0]} rows x {df.shape[1]} cols")
        extracted.append(df)
    
    return extracted