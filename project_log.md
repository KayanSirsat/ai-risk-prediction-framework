# Project Log - AI-Driven Risk Prediction Framework

This file serves as the official development log for the Final Year Project. It tracks progress, architectural decisions, and milestones to aid in generating the Stage 2 report and final documentation.

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

### Next Steps
- Begin active development on the `notebooks/01_data_exploration.ipynb`.
- Establish the baseline datasets for the `preprocessing` and `models` modules.
