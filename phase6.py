import datetime
import pandas as pd
import phase1_database
from sklearn.impute import SimpleImputer
def log_cleaning_action(session_id,action_text):
    now = datetime.datetime.now()
    phase1_database.run_query("""
insert into CLEANED_LOGS (Session_ID,Actions_taken,Created_on)
                              values(%s, %s, %s)
""", (session_id, action_text, now))
    print(f"cleaning step: {action_text}")
def remove_duplicated_rows(df,session_id):
    before = df.shape[0]
    print(f"Dataset before: \n{before}")
    print()
    re_df = df.drop_duplicates()
    after = re_df.shape[0]
    print(f"Dataset after cleaning: \n{after}")
    rem = before - after
    if rem > 0:
        log_cleaning_action(session_id,f"removed {rem} from the dataset")
        return re_df
    return df
def remove_empty_col(df,session_id,threshold = 0.9):
    col_to_drop = []
    for col in df.columns:
        mr = df[col].isnull().mean()
        if mr > threshold:
            col_to_drop.append(col)

    if col_to_drop:
        df.drop(columns=col_to_drop, inplace=True)
        print("About 90 % of empty columns removed..")
    else:
        print("No need to clean column....")

    log_cleaning_action(session_id,f"removed {col_to_drop} which have more than {threshold*100}% empty values")
    return df
def handle_missing_values(df,session_id):
    nc = df.select_dtypes(include="number").columns.to_list()
    cc = df.select_dtypes(include=["object", "category"]).columns.to_list()
    mv = int(df.isnull().sum().sum())
    total_cells = df.shape[0] * df.shape[1]
    percent = (mv / total_cells) * 100 if total_cells > 0 else 0
    print(f"About {percent:.2f}% missing values found, cleaning started....")

    if mv > 0:
        if nc:
            s = SimpleImputer(strategy="median")
            df[nc] = s.fit_transform(df[nc])
        if cc:
            s = SimpleImputer(strategy="most_frequent")
            df[cc] = s.fit_transform(df[cc])
    else:
        print("proceeding further......\nNo missing values found")

    log_cleaning_action(session_id,f"Removed {mv} missing values")
    return df
def std_dataframe(df, session_id):
    for column in df.columns:
        if df[column].dtype == "object":
            # Try to convert to numeric first
            converted = pd.to_numeric(df[column], errors="coerce")
            non_null_before = df[column].notnull().sum()
            non_null_after = converted.notnull().sum()

            if non_null_before > 0 and (non_null_after / non_null_before) > 0.9:
                df[column] = converted
                log_cleaning_action(session_id, f"Converted column '{column}' to numeric type.")

    # Now standardize only the columns that are STILL text
    text_columns = df.select_dtypes(include="object").columns
    for column in text_columns:
        # avoid turning NaN into string "nan"
        df[column] = df[column].apply(
            lambda x: x.strip().lower() if isinstance(x, str) else x
        )

    if len(text_columns) > 0:
        log_cleaning_action(session_id, f"Standardized text formatting in columns: {list(text_columns)}")
    else:
        print("nothing to standardize....")
    return df
def clean_dataset(df,session_id):
    df = remove_duplicated_rows(df,session_id)
    df = remove_empty_col(df,session_id)
    df = handle_missing_values(df,session_id)
    df = std_dataframe(df,session_id)
    print(f"Cleaning complete. New shape {df.shape}")
    return df
