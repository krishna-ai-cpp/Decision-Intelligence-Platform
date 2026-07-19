import os
import joblib
from datetime import datetime
from sklearn.preprocessing import LabelEncoder, StandardScaler
import phase1_config
import phase1_database
def split_dataset(df, target):
    x = df.drop(columns=[target])
    y = df[target]
    return x, y

def encoding(features):
    encoder = {}
    cols = features.select_dtypes(include=["object", "category"]).columns.to_list()
    for col in cols:
        le = LabelEncoder()
        features[col] = le.fit_transform(features[col])
        encoder[col] = le
        print(f"Encoded categorical column {col}")
    return features, encoder

def scaling(features):
    scaler = {}
    cols = features.select_dtypes(include="number").columns.to_list()
    for col in cols:
        ss = StandardScaler()
        features[col] = ss.fit_transform(features[[col]])
        scaler[col] = ss
        print(f"Scaled numerical column {col}")
    return features, scaler

def prepare(df, ta, session_id):
    ft, target = split_dataset(df, ta)
    features, encoders = encoding(ft)
    features, scaler = scaling(features)
    pdt = {
        "encoders": encoders,
        "scaler": scaler,
        "Feature_columns": list(features.columns),
        "target_columns": ta
    }
    if not os.path.exists(phase1_config.model_f):
        os.makedirs(phase1_config.model_f)
    pp = os.path.join(phase1_config.model_f, f"Pipeline_session_{session_id}.joblib")
    joblib.dump(pdt, pp)
    print(f"saved to : {pp}")
    now = datetime.now()
    details_text = f"Features: {list(features.columns)}, Target: {ta}"
    phase1_database.run_query(
        """INSERT INTO feature_engineering_logs (session_id, pipeline_path, details, created_on)
           VALUES (%s, %s, %s, %s)""",
        (session_id, pp, details_text, now)
    )

    print("Feature engineering complete. Final feature count:", features.shape[1])
    print("---------------------------------\n")

    return features, target, pp
