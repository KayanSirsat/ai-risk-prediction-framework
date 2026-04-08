import pandas as pd
import numpy as np
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_curve, auc, classification_report
from sklearn.preprocessing import label_binarize

# Constants
DATA_PATH = "data/ml_ready_data.csv"
MODEL_PATH = "models/xgb_model.pkl"
OUTPUT_DIR = "app/components/"
CM_PATH = os.path.join(OUTPUT_DIR, "confusion_matrix.png")
ROC_PATH = os.path.join(OUTPUT_DIR, "roc_curve.png")
TARGET_COL = "Risk_Level"


def generate_publication_plots():
    # 1. Load dataset and pipeline
    print("[INFO] Loading data and model...")
    if not os.path.exists(DATA_PATH) or not os.path.exists(MODEL_PATH):
        print("[ERROR] Required data or model files missing.")
        return

    df = pd.read_csv(DATA_PATH)
    pipeline = joblib.load(MODEL_PATH)

    # 2. Prepare X and y
    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    # Map labels to integers for metrics calculation if they are strings
    # The pipeline handles mapping internally, but for sklearn metrics we need consistent labels
    risk_map = {"Low": 0, "Medium": 1, "High": 2}
    if y.dtype == "object":
        y_numeric = y.map(risk_map)
    else:
        y_numeric = y

    # Split data (test_size=0.2, random_state=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_numeric, test_size=0.2, random_state=42, stratify=y_numeric
    )

    # 3. Generate predictions and probabilities
    print("[INFO] Generating test set predictions...")

    # Check if loaded object is a Pipeline or just a classifier
    if hasattr(pipeline, "named_steps"):
        preprocessor = pipeline.named_steps["preprocessor"]
        classifier = pipeline.named_steps["classifier"]
    else:
        # If only the classifier was saved, we need to handle preprocessing manually
        print("[WARN] Loaded object is a classifier, not a full pipeline.")
        print("[INFO] Applying manual preprocessing for compatibility...")
        classifier = pipeline

        # Manual preprocessing matching the training pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler
        from sklearn.feature_extraction.text import TfidfVectorizer

        # Drop text columns for now (would need TF-IDF for full compatibility)
        text_cols = [
            c
            for c in X_test.columns
            if c in ["Summary", "Description", "text_combined"]
        ]
        cat_cols = [
            c
            for c in ["Priority", "Issue_Type", "Assignee_Seniority"]
            if c in X_test.columns
        ]
        num_cols = [
            c
            for c in ["Estimated_Days", "Story_Points", "Budget_Allocated"]
            if c in X_test.columns
        ]

        # Simple encoding for compatibility
        X_test_processed = X_test[num_cols].copy()
        if cat_cols:
            X_test_cat = pd.get_dummies(X_test[cat_cols], drop_first=False)
            X_test_processed = pd.concat([X_test_processed, X_test_cat], axis=1)

        X_test_transformed = X_test_processed.values

    y_pred = classifier.predict(X_test_transformed)
    # Ensure y_pred is numeric for the confusion matrix
    if isinstance(y_pred[0], str):
        y_pred = np.array([risk_map[val] for val in y_pred])

    y_prob = classifier.predict_proba(X_test_transformed)

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 4. Figure 1: Confusion Matrix
    print("[INFO] Generating Confusion Matrix...")
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_pred)
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=["Low", "Medium", "High"],
        yticklabels=["Low", "Medium", "High"],
    )
    plt.title("Confusion Matrix: Risk Level Prediction", fontsize=14, pad=20)
    plt.xlabel("Predicted Label", fontsize=12)
    plt.ylabel("True Label", fontsize=12)
    plt.savefig(CM_PATH, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved Confusion Matrix to {CM_PATH}")

    # 5. Figure 2: ROC Curve (One-vs-Rest)
    print("[INFO] Generating ROC Curves...")
    plt.figure(figsize=(8, 6))

    # Binarize the output for multi-class ROC
    y_test_bin = label_binarize(y_test, classes=[0, 1, 2])
    n_classes = 3
    labels = ["Low", "Medium", "High"]

    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_prob[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])
        plt.plot(
            fpr[i],
            tpr[i],
            label=f"Class {labels[i]} (AUC = {roc_auc[i]:.2f})",
            linewidth=2,
        )

    plt.plot([0, 1], [0, 1], "k--", lw=2)  # Diagonal dashed line
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel("False Positive Rate", fontsize=12)
    plt.ylabel("True Positive Rate", fontsize=12)
    plt.title("One-vs-Rest ROC Curve: Risk Level Prediction", fontsize=14, pad=20)
    plt.legend(loc="lower right")
    plt.grid(alpha=0.3)
    plt.savefig(ROC_PATH, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved ROC Curve to {ROC_PATH}")


if __name__ == "__main__":
    try:
        generate_publication_plots()
        print("\n[SUCCESS] All research figures have been generated successfully.")
    except Exception as e:
        print(f"\n[ERROR] Plot generation failed: {e}")
        import traceback

        traceback.print_exc()
