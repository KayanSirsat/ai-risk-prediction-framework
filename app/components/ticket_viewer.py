import streamlit as st
import pandas as pd
import joblib
import os
import re

FEATURE_COLUMNS_PATH = "models/feature_columns.pkl"


def _preprocess_row(ticket_row, dataset):
    TARGET_COL = "Risk_Level"

    X = pd.DataFrame([ticket_row.values], columns=ticket_row.index)

    original_dtypes = dataset.drop(columns=[TARGET_COL], errors="ignore").dtypes
    for col in X.columns:
        if col in original_dtypes.index:
            X[col] = X[col].astype(original_dtypes[col])

    X = X.drop(columns=["Actual_Days", "Cost_Consumed"], errors="ignore")
    X = X.drop(
        columns=["Summary", "Description", "Issue_ID", "Issue_key"], errors="ignore"
    )

    cat_cols = X.select_dtypes(include=["object", "category"]).columns
    if len(cat_cols) > 0:
        X = pd.get_dummies(X, columns=cat_cols)

    X.columns = [re.sub(r"[\[\]<]", "_", str(c)) for c in X.columns]

    # Align columns to the training feature set so all expected one-hot columns exist.
    # Columns present in train but missing here (e.g. Priority_High when ticket is Low)
    # are filled with 0; extra columns are dropped.
    if os.path.exists(FEATURE_COLUMNS_PATH):
        training_columns = joblib.load(FEATURE_COLUMNS_PATH)
        X = X.reindex(columns=training_columns, fill_value=0)

    return X


def render_ticket_context(selected_row, pipeline, dataset):
    TARGET_COL = "Risk_Level"
    risk_map = {0: "Low", 1: "Medium", 2: "High"}

    cols = st.columns(4)

    try:
        cols[0].metric("Estimated Days", int(selected_row["Estimated_Days"]))
        cols[1].metric("Budget (USD)", f"${selected_row['Budget_Allocated']:,.2f}")
        cols[2].metric("Story Points", int(selected_row["Story_Points"]))
        cols[3].metric("Assignee Seniority", str(selected_row["Assignee_Seniority"]))
    except KeyError as e:
        st.error("Missing column in dataset: " + str(e))
        return None, None, None

    if TARGET_COL not in selected_row.index:
        st.error(f"Target column '{TARGET_COL}' not found in dataset.")
        return None, None, None

    features = selected_row.drop(labels=[TARGET_COL])
    processed_features = _preprocess_row(features, dataset)

    try:
        prediction = pipeline.predict(processed_features)[0]
        prediction_proba = pipeline.predict_proba(processed_features)[0]
    except Exception as e:
        st.error(f"Prediction failed: {e}")
        return None, None, None

    risk_label = risk_map.get(int(prediction), str(prediction))
    predicted_class_index = int(prediction)
    confidence = prediction_proba[predicted_class_index] * 100

    if risk_label == "Low":
        st.success(f"Predicted Risk: Low ({confidence:.2f}%)")
    elif risk_label == "Medium":
        st.warning(f"Predicted Risk: Medium ({confidence:.2f}%)")
    else:
        st.error(f"Predicted Risk: High ({confidence:.2f}%)")

    return risk_label, processed_features, features
