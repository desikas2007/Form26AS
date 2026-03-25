import camelot


def extract_with_camelot(file_path, pages='all'):
    try:
        tables = camelot.read_pdf(file_path, pages=pages)
        dfs = []
        for t in tables:
            if t.df is not None and not t.df.empty:
                dfs.append(t.df)
        return dfs
    except Exception as e:
        print(f"Camelot extraction error: {e}")
        return []


def extract_page_camelot(file_path, page_num):
    try:
        tables = camelot.read_pdf(file_path, pages=str(page_num))
        dfs = []
        for t in tables:
            if t.df is not None and not t.df.empty and t.df.shape[0] > 1:
                df = t.df.copy()
                df.columns = df.iloc[0]
                df = df[1:]
                df = df.dropna(how='all')
                dfs.append(df)
        return dfs
    except Exception:
        return []
