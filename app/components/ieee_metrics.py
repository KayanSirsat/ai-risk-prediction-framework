import streamlit as st
import os

CONFUSION_MATRIX_PATH = "app/components/confusion_matrix.png"
ROC_CURVE_PATH = "app/components/roc_curve.png"


def render_ieee_metrics():
    with st.expander("View IEEE Publication Artifacts"):
        col1, col2 = st.columns(2)

        with col1:
            try:
                st.image(
                    CONFUSION_MATRIX_PATH,
                    caption="Confusion Matrix: Risk Level Prediction",
                )
            except FileNotFoundError:
                st.warning(
                    "Confusion Matrix not found. Run `generate_paper_plots.py` first."
                )

        with col2:
            try:
                st.image(
                    ROC_CURVE_PATH,
                    caption="One-vs-Rest ROC Curve: Risk Level Prediction",
                )
            except FileNotFoundError:
                st.warning("ROC Curve not found. Run `generate_paper_plots.py` first.")
