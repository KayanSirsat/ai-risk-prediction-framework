import pandas as pd
import numpy as np
import joblib
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.utils.class_weight import compute_sample_weight

# Constants
DATA_PATH = "data/ml_ready_data.csv"
MODEL_DIR = "models/"
RF_MODEL_PATH = os.path.join(MODEL_DIR, "rf_model.pkl")
XGB_MODEL_PATH = os.path.join(MODEL_DIR, "xgb_model.pkl")

def load_and_prepare_data(path):
    print("[INFO] Loading data from {}...".format(path))
    df = pd.read_csv(path)
    
    # 1. Target Mapping
    risk_map = {"Low": 0, "Medium": 1, "High": 2}
    df["Risk_Level"] = df["Risk_Level"].map(risk_map)
    
    # 2. Feature Separation
    X = df.drop(columns=["Risk_Level"])
    y = df["Risk_Level"]
    
    # 3. Resolve Target Leakage: Drop columns used to create Risk_Level
    leakage_cols = ["Actual_Days", "Cost_Consumed"]
    cols_to_drop = [col for col in leakage_cols if col in X.columns]
    X = X.drop(columns=cols_to_drop)
    print(f"[INFO] Prevented target leakage by dropping: {cols_to_drop}")
    
    # 4. Drop Text/ID Columns (Reserved for NLP)
    text_cols = ["Summary", "Description", "Developer_Comments", "Issue_ID", "Issue_key"]
    text_to_drop = [col for col in text_cols if col in X.columns]
    X = X.drop(columns=text_to_drop)
    print(f"[INFO] Dropped text/ID columns: {text_to_drop}")
    
    # 5. Aggressive Text Purge & Robust Encoding
    # We drop any object/category column with > 15 unique values to prevent memory explosion and noise
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns
    to_encode = []
    to_drop = []
    
    for col in categorical_cols:
        if X[col].nunique() <= 15:
            to_encode.append(col)
        else:
            to_drop.append(col)
            
    if to_drop:
        print(f"[INFO] Dropping high-cardinality/text columns (>15 unique): {to_drop}")
        X = X.drop(columns=to_drop)
        
    if to_encode:
        print(f"[INFO] One-hot encoding categorical columns: {to_encode}")
        X = pd.get_dummies(X, columns=to_encode)
    
    # 6. Sanitize Feature Names for XGBoost
    # Replace illegal characters [, ], < with underscores
    X.columns = [re.sub(r'[\[\]<]', '_', str(c)) for c in X.columns]
    print("[INFO] Sanitized feature names for XGBoost compatibility.")
    
    return X, y

def train_and_evaluate():
    # Load and Prepare
    X, y = load_and_prepare_data(DATA_PATH)
    
    # 6. Train/Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("[INFO] Data split into 80% train and 20% test sets.")

    # 7. Handle Class Imbalance for XGBoost (Calculate weights)
    sample_weights = compute_sample_weight(class_weight="balanced", y=y_train)

    # 8. Model Definitions
    models = {
        "RandomForest": RandomForestClassifier(
            n_estimators=100, 
            random_state=42, 
            class_weight="balanced"
        ),
        "XGBoost": XGBClassifier(
        eval_metric="mlogloss",
        base_score=0.5,      # Explicit scalar — avoids per-class vector that breaks SHAP
        random_state=42
        ),
    }

    results = {}

    for name, model in models.items():
        print(f"\n[INFO] Training {name} Classifier...")
        
        if name == "XGBoost":
            model.fit(X_train, y_train, sample_weight=sample_weights)
        else:
            model.fit(X_train, y_train)
        
        # Predictions
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        report = classification_report(
            y_test, preds, target_names=["Low", "Medium", "High"]
        )
        
        print(f"--- {name} Results ---")
        print(f"Accuracy: {acc:.4f}")
        print(report)
        
        results[name] = model

    # 9. Save Models
    print("\n[INFO] Saving trained models to {}...".format(MODEL_DIR))
    joblib.dump(results["RandomForest"], RF_MODEL_PATH)
    joblib.dump(results["XGBoost"], XGB_MODEL_PATH)
    print(f"[SUCCESS] Saved: {RF_MODEL_PATH} and {XGB_MODEL_PATH}")

    # 10. Save feature column names for Ticket Auditor alignment
    # ticket_viewer._preprocess_row() uses this to ensure inference
    # features exactly match the training feature space.
    FEATURE_COLUMNS_PATH = os.path.join(MODEL_DIR, "feature_columns.pkl")
    joblib.dump(list(X.columns), FEATURE_COLUMNS_PATH)
    print(f"[SUCCESS] Saved feature column names to {FEATURE_COLUMNS_PATH}")
    print(f"[INFO] Training feature columns ({len(X.columns)}): {list(X.columns)}")

if __name__ == "__main__":
    try:
        train_and_evaluate()
        print("\n[SUCCESS] Training pipeline completed successfully.")
    except Exception as e:
        print(f"\n[ERROR] Training failed: {e}")
