import pandas as pd

def tables_to_dataframe(tables):

    all_rows = []

    for table in tables:
        for row in table:
            all_rows.append(row)

    if not all_rows:
        return pd.DataFrame()

    header = all_rows[0]
    col_len = len(header)

    clean_rows = []

    for row in all_rows[1:]:

        if len(row) < col_len:
            row += [None] * (col_len - len(row))

        if len(row) > col_len:
            row = row[:col_len]

        clean_rows.append(row)

    df = pd.DataFrame(clean_rows, columns=header)

    df = df.replace({'₹': '', 'n': '', ',': ''}, regex=True)

    return df