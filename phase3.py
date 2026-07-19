import os
import pandas as pd
from datetime import datetime
import phase1_database
def upload_read_csv(file_path, session_id):
    # use the provided file_path argument; validate existence
    if not file_path or not os.path.exists(file_path):
        print("NO file found.....")
        return None
    else:
        data = pd.read_csv(file_path)
        if data is None:
            return None
        df = pd.DataFrame(data)
        print("File uploaded successfully.....")
        print("________DATAFRAME SUMMARY_________")
        print("Shape (rows, columns):", df.shape)
        print("Number of Rows:", df.shape[0])
        print("Number of Columns:", df.shape[1])
        print("\nData Types:\n", df.dtypes)
        memory_used_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
        print(f"\nMemory Usage: {memory_used_mb:.2f} MB")
        print("\nFirst 5 Rows:\n", df.head())
        print("\nLast 5 Rows:\n", df.tail())
        print("----------------------------\n")
        now = datetime.now()
        phase1_database.run_query(
            "insert into DATASET_METADATA (Session_ID, file_path, Missing_values, Duplicate_rows, Created_on) values (%s, %s, %s, %s, %s)",
            (session_id, file_path, int(df.isna().sum().sum()), int(df.duplicated().sum()), now)
        )
        print("Meta Data saved to Database.....")
        return df

def detect(df):
    # identify numeric columns and return basic summary as tuple
    nc = df.select_dtypes(include="number").columns.to_list()
    cc = df.select_dtypes(include=["object", "category"]).columns.to_list()
    dc = []
    bc = []
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            dc.append(col)
        else:
            # Try to see if a "text" column is secretly a date
            try:
                pd.to_datetime(df[col], errors="raise")
                dc.append(col)
            except (ValueError, TypeError):
                bc.append(col)
    return nc, cc, dc, bc
def constant(df):
    con = []
    for col in df.columns:
        if df[col].nunique(dropna=False) <= 1:
            con.append(col)
    return con
def correlated(df,nc,threshold=0.9):
    co = []
    if len(nc) < 2:
        return co
    cm = df[nc].corr().abs()
    cols = cm.columns.tolist()
    for i in range(len(cols)):
        for j in range(i+1, len(cols)):
            col_a = cols[i]
            col_b = cols[j]
            cv = cm.loc[col_a, col_b]
            if cv >= threshold:
                co.append((col_a, col_b, round(cv, 2)))
    return co
def skewed(df,nc,skew_limit = 1.0):
    sc = []
    for col in nc:
        sv = df[col].skew()
        if abs(sv) > skew_limit:
            sc.append((col, round(sv, 2)))
    return sc
def data_quality(df,mc,dc_count,con,co):
    rows, cols = df.shape
    cells = rows * cols
    print(f"Total cells: {cells}")
    score = 100.0
    if cells > 0:
        mp = (mc / cells) * 100
        score -= min(mp, 30)
    if rows > 0:
        dp = (dc_count / rows) * 100
        score -= min(dp, 20)
    score -= min(len(con) * 5, 20)
    score -= min(len(co) * 5, 20)
    score = max(score, 0)
    return round(score, 2)
def profile(df, session_id, file_path):
    nc, cc, dc, bc = detect(df)
    print(f"Numeric Columns: \n{nc}")
    print(f"Categorial Columns: \n{cc}")
    print(f"Datetime Column: \n{dc}")
    print(f"Boolean Columns: \n{bc}")

    cons = constant(df)
    print(f"Constant Columns: \n{cons}")
    co = correlated(df, nc)
    print(f"Correlated Columns: \n{co}")
    sk = skewed(df, nc)
    print(f"Skewed Coluns: {sk}")
    mc = int(df.isnull().sum().sum())
    dup = int(df.duplicated().sum())
    dq = data_quality(df, mc, len(dc), cons, co)
    print(f"Data Quality: {dq} %")

    now = datetime.now()
    phase1_database.run_query(
        "insert into DATASET_METADATA (Session_ID, file_path, Missing_values, Duplicate_rows, Created_on) values (%s, %s, %s, %s, %s)",
        (session_id, file_path, mc, dup, now)
    )