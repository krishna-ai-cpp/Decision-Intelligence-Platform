import os
import time
import joblib
from datetime import datetime

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.cluster import KMeans
from sklearn.metrics import (
    r2_score, mean_absolute_error, mean_squared_error,
    accuracy_score, precision_score, recall_score, f1_score,
    silhouette_score
)

import phase1_config
import phase1_database
def save_model(model,session_id,model_name):
    if not os.path.exists(phase1_config.model_f):
        os.makedirs(phase1_config.model_f)

    safe_name = model_name.lower().replace(" ", "_")
    model_path = os.path.join(phase1_config.model_f, f"{safe_name}_session_{session_id}.joblib")
    joblib.dump(model, model_path)
    return model_path
def model_metadata(sesion_id,model_name,model_path,score):
    now = datetime.now()
    phase1_database.run_query(
        """INSERT INTO models (session_id, model_name, model_path, score, created_on)
           VALUES (%s, %s, %s, %s, %s)""",
        (sesion_id, model_name, model_path, score, now)
    )
def train_reg(features,target,session_id):
    print("\n----- TRAINING REGRESSION MODELS -----")

    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42
    )

    models_to_train = {
        "Linear Regression": LinearRegression(),
        "Decision Tree Regressor": DecisionTreeRegressor(random_state=42),
        "Random Forest Regressor": RandomForestRegressor(random_state=42)
    }

    results = []

    for model_name, model in models_to_train.items():
        start_train_time = time.time()
        model.fit(X_train, y_train)
        training_time = time.time() - start_train_time

        start_predict_time = time.time()
        predictions = model.predict(X_test)
        prediction_time = time.time() - start_predict_time

        print(f"model took {training_time} to train...")
        print(f"model took {prediction_time} to make predicion...")

        r2 = r2_score(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        rmse = mean_squared_error(y_test, predictions) ** 0.5

        print(f"\n{model_name}:")
        print(f"  R²   = {r2:.4f}")
        print(f"  MAE  = {mae:.4f}")
        print(f"  RMSE = {rmse:.4f}")
        print(f"  Training time   = {training_time:.4f} seconds")
        print(f"  Prediction time = {prediction_time:.4f} seconds")

        model_path = save_model(model, session_id, model_name)
        model_metadata(session_id, model_name, model_path, r2)

        results.append({
            "model_name": model_name,
            "model_object": model,
            "model_path": model_path,
            "r2": r2,
            "mae": mae,
            "rmse": rmse,
            "training_time": training_time,
            "prediction_time": prediction_time,
            "y_test": y_test,
            "predictions": predictions
        })

    print("----------------------------------------\n")
    return results
def train_class(features,target,session_id):
    print("\n----- TRAINING CLASSIFICATION MODELS -----")
    x_train,x_test,y_train,y_test = train_test_split(features,target,test_size=0.2,random_state=42)
    models_to_train = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "KNN": KNeighborsClassifier(),
        "Decision Tree": DecisionTreeClassifier(random_state=42),
        "Random Forest": RandomForestClassifier(random_state=42)
    }
    results=[]
    for model_name,model in models_to_train.items():
        start_train = time.time()
        model.fit(x_train,y_train)
        ttime = time.time() - start_train
        start_predict_time = time.time()
        predictions = model.predict(x_test)
        prediction_time = time.time() - start_predict_time
        print(f"model took {ttime} to train...")
        print(f"model took {prediction_time} to make predicion...")
        accuracy = accuracy_score(y_test, predictions)
        precision = precision_score(y_test, predictions, average="weighted", zero_division=0)
        recall = recall_score(y_test, predictions, average="weighted", zero_division=0)
        f1 = f1_score(y_test, predictions, average="weighted", zero_division=0)

        print(f"\n{model_name}:")
        print(f"  Accuracy  = {accuracy:.4f}")
        print(f"  Precision = {precision:.4f}")
        print(f"  Recall    = {recall:.4f}")
        print(f"  F1 Score  = {f1:.4f}")
        print(f"  Training time   = {ttime:.4f} seconds")
        print(f"  Prediction time = {prediction_time:.4f} seconds")

        model_path = save_model(model, session_id, model_name)
        model_metadata(session_id, model_name, model_path, accuracy)

        results.append({
            "model_name": model_name,
            "model_object": model,
            "model_path": model_path,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "training_time": ttime,
            "prediction_time": prediction_time,
            "y_test": y_test,
            "predictions": predictions
        })

    print("---------------------------------------------\n")
    return results
def find_best_k(features,max_k=10):
    iv = []
    kv = range(1,max_k+1)
    for k in kv:
        kmeans_model = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans_model.fit(features)
        iv.append(kmeans_model.inertia_)

    return list(kv), iv
def optimal_k(kv,iv):
    # Choose k with the largest drop in inertia between consecutive k's
    if len(iv) < 2:
        return kv[0]
    deltas = [iv[i-1] - iv[i] for i in range(1, len(iv))]
    max_idx = deltas.index(max(deltas))
    # corresponding k is the second element in the pair
    return kv[max_idx+1]
def clustering(features,session_id):
    k_value,iv = find_best_k(features)
    best_k = optimal_k(k_value,iv)
    print(f"Suggested optimal k Number: {best_k}")
    fm = KMeans(n_clusters=best_k,random_state=42,n_init=10)
    st = time.time()
    pred = fm.fit_predict(features)
    et = time.time() - st
    print(f"Model took {et:.4f} seconds to train and predict")
    if best_k > 1:
        sil_score = silhouette_score(features, pred)
        print(f"silhouette_score : {sil_score:.4f}")
    else:
        sil_score = None
    path = save_model(fm,session_id,"KMeans")
    model_metadata(session_id, "KMeans", path, sil_score if sil_score else 0)
    print("-----------------------------------------------\n")

    return {
        "model_object": fm,
        "model_path": path,
        "best_k": best_k,
        "cluster_labels": pred,
        "silhouette_score": sil_score,
        "k_values": k_value,
        "inertia_values": iv
    }
