import pandas as pd
import re


def clean_text_value(value):
    try:
        if value is None:
            return None
        
        if isinstance(value, pd.Series):
            return None
        
        if pd.isna(value):
            return None
        
        if isinstance(value, (int, float)):
            return value
        
        text = str(value).strip()
        
        text = re.sub(r'[₹Rs.,\s]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip(' -_:|/\\')
        
        if text.lower() in ['none', 'null', 'na', 'n/a', '-', '']:
            return None
        
        return text if text else None
    except:
        return None


def clean_amount(value):
    try:
        if value is None:
            return None
        
        if isinstance(value, pd.Series):
            return None
        
        if pd.isna(value):
            return None
        
        if isinstance(value, (int, float)):
            return value
        
        text = str(value).strip()
        text = re.sub(r'[₹Rs,]', '', text)
        text = re.sub(r'\s+', '', text)
        
        try:
            if '.' in text:
                return float(text)
            return int(text)
        except:
            return text.strip() if text.strip() else None
    except:
        return None


def normalize_column_name(col):
    if pd.isna(col):
        return "Unknown"
    
    try:
        col = str(col).strip()
        col = re.sub(r'\s+', '_', col)
        col = re.sub(r'[^\w_]', '', col)
        col = col.lower()
        col = re.sub(r'_+', '_', col)
        col = col.strip('_')
        
        if not col:
            return "unknown"
        
        return col
    except:
        return "unknown"


def clean_dataframe(df):
    if df is None or df.empty:
        return df
    
    try:
        df = df.copy()
        
        df.columns = [normalize_column_name(c) for c in df.columns]
        
        df = df.dropna(how='all')
        
        df = df.drop_duplicates()
        
        for col in df.columns:
            col_data = df[col]
            if col_data.apply(lambda x: isinstance(x, pd.Series)).any():
                df[col] = None
                continue
                
            if any(keyword in col.lower() for keyword in ['amount', 'tax', 'tds', 'deduct', 'income', 'balance', 'rate']):
                df[col] = df[col].apply(clean_amount)
            else:
                df[col] = df[col].apply(clean_text_value)
        
        df = df.loc[:, df.columns.notna()]
        
        return df
    except Exception as e:
        return df


def clean_and_normalize(tables):
    if not tables:
        return []
    
    cleaned = []
    seen_data = set()
    
    for i, table in enumerate(tables):
        if isinstance(table, pd.DataFrame) and not table.empty:
            try:
                df = clean_dataframe(table)
                
                if not df.empty and len(df.columns) >= 2:
                    data_hash = tuple(sorted(df.columns.tolist()))
                    if data_hash not in seen_data:
                        seen_data.add(data_hash)
                        
                        df = df.reset_index(drop=True)
                        df.index = df.index + 1
                        df.index.name = 'S.No'
                        
                        cleaned.append(df)
            except Exception as e:
                continue
    
    return cleaned


def merge_similar_tables(tables, similarity_threshold=0.7):
    if not tables:
        return tables
    
    merged = []
    skip_indices = set()
    
    for i, table1 in enumerate(tables):
        if i in skip_indices:
            continue
        
        try:
            current = table1.copy()
            
            for j, table2 in enumerate(tables[i + 1:], start=i + 1):
                if j in skip_indices:
                    continue
                
                if list(table1.columns) == list(table2.columns):
                    overlap = len(table1.merge(table2).drop_duplicates())
                    total = len(table1) + len(table2)
                    
                    if overlap / total >= similarity_threshold:
                        current = pd.concat([current, table2], ignore_index=True)
                        skip_indices.add(j)
            
            merged.append(current)
        except:
            merged.append(table1)
    
    return merged


def get_table_summary(df):
    if df is None or df.empty:
        return {}
    
    summary = {
        "rows": len(df),
        "columns": len(df.columns),
        "null_count": df.isnull().sum().sum(),
        "column_names": list(df.columns),
        "numeric_columns": [c for c in df.columns if df[c].dtype in ['int64', 'float64']],
        "text_columns": [c for c in df.columns if df[c].dtype == 'object']
    }
    
    return summary
