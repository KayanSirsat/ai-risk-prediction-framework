# Project Log - AI-Driven Risk Prediction Framework

This file serves as the official development log for the Final Year Project. It tracks progress, architectural decisions, and milestones to aid in generating the Stage 2 report and final documentation.

---

## [2026-04-07]
**Phase:** Phase 3 & Phase 4 Implementation
**Focus:** UI Dashboard Deployment, Explainable AI (XAI), and GenAI Integration.

### Accomplishments
- Built the complete Streamlit UI (`app/main.py`) featuring a professional "Jira-Minimalist" design with sidebars and split-screen audit trails.
- Generated mandatory IEEE publication artifacts (Multi-Class ROC-AUC Curve and Confusion Matrix) via a dedicated `generate_paper_plots.py` script.
- Integrated local SHAP explainability into the dashboard, normalizing raw SHAP decimals into readable "Percentage of Influence" progress bars using Streamlit's native `st.column_config`.
- Built `src/mitigation/llm_agent.py` to route high-risk tickets to a GenAI auditor (Qwen 3.5 via NVIDIA API).
- Engineered enterprise-grade Exponential Backoff and Retry logic into the API requests to prevent network timeout crashes.
- Implemented Streamlit `st.session_state` caching to ensure AI mitigation strategies persist across UI interactions without unnecessary API calls.

### Next Steps
- Refactor the monolithic `main.py` into a feature-sliced modular architecture.
- Integrate advanced UI extensions (e.g., `streamlit-shadcn-ui`) to finalize the enterprise SaaS aesthetic.

---

## [2026-04-05]
**Phase:** Stage-1 → Stage-2 Transition
**Focus:** Project initialization and repository clean-up.

### Accomplishments
- Consolidated project tracking by merging `roadmap.md` into `README.md`.
- Removed redundant files (`references.md`, `roadmap.md`) to maintain a clean root directory.
- Initialized `project_log.md` (this file) to maintain an ongoing history of development decisions, ensuring a smoother writing process for the Stage-2 structural reports.
- Verified architecture placeholder files inside the `src/` modules are accurately mapped to the `module_overview.md` definitions.
- Created `src/preprocessing/data_pipeline.py` to generate synthetic timeline and financial metrics, calculate risk levels, and output ML-ready data.
- Created `src/models/train.py` to train baseline RandomForest and XGBoost classification models for risk prediction.
- Refactored `train.py` to eliminate critical target leakage, ensuring the model only trains on pre-execution indicators.
- Improved model robustness by handling class imbalances, sanitizing XGBoost feature names, and preventing high-cardinality text column memory explosions.
- Pipeline architecture was successfully implemented!

### Next Steps
- Begin active development on the `notebooks/01_data_exploration.ipynb`.
- Establish the baseline datasets for the `preprocessing` and `models` modules.
