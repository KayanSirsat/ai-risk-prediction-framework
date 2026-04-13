import streamlit as st
import pandas as pd
import numpy as np
import shap


def render_shap_table(ticket_features, pipeline):
    st.subheader("Top Risk Drivers (Local SHAP)")

    explainer = shap.TreeExplainer(pipeline)
    shap_values = explainer.shap_values(ticket_features)

    if isinstance(shap_values, list):
        shap_values = np.array(shap_values).sum(axis=0).flatten()
    else:
        shap_values = np.abs(shap_values).flatten()

    feature_names = list(ticket_features.columns)
    importance = list(zip(feature_names, shap_values))
    importance.sort(key=lambda x: x[1], reverse=True)

    top5 = importance[:5]

    if not top5:
        st.info("SHAP explanation not available for this model.")
        return

    total_shap = sum(val for _, val in top5)

    df_shap = pd.DataFrame(
        {
            "Risk Driver": [feat.replace("_", " ").title() for feat, _ in top5],
            "Influence (%)": [
                (val / total_shap) * 100 if total_shap else 0 for _, val in top5
            ],
            "Raw SHAP": [val for _, val in top5],
        }
    )

    st.dataframe(
        df_shap,
        column_config={
            "Risk Driver": st.column_config.TextColumn(
                "Risk Driver",
                width="medium",
            ),
            "Influence (%)": st.column_config.ProgressColumn(
                "Influence (%)",
                min_value=0,
                max_value=100,
                format="%d%%",
                width="medium",
            ),
            "Raw SHAP": st.column_config.NumberColumn(
                "Raw SHAP",
                format="%.4f",
                width="small",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )
