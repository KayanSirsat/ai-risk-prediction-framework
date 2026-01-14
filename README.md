# AI-Driven Risk Prediction and Mitigation Framework

This repository contains the design and ongoing implementation of an AI-driven
risk prediction and mitigation framework developed as part of my Final Year
Project (B.E. Computer Engineering, Sinhgad College of Engineering).

The objective of the project is to design a unified, explainable AI system that
predicts project risks, forecasts deviations, detects anomalies and provides
actionable mitigation insights using Machine Learning (ML), Natural Language
Processing (NLP) and Explainable AI (XAI).

## Project Status
This project is currently in a Stage-1 → Stage-2 transition phase.

### Completed
- System architecture and module design
- Software Requirement Specification (IEEE-style)
- Data pipeline planning for structured and unstructured data
- Baseline ML model selection (Random Forest, XGBoost)
- Explainability design using SHAP

### In Progress
- Risk classification model implementation
- SHAP-based explainability integration
- Time-series forecasting (Prophet)
- NLP-based qualitative risk detection
- Streamlit dashboard integration

## Core Components
- Risk Prediction: ML-based classification of project risk levels
- Forecasting: Time-series prediction of cost and schedule deviations
- Anomaly Detection: Identification of abnormal project behavior
- Explainable AI: SHAP-based interpretability for model decisions
- NLP Module: Detection of qualitative risks from text data
- Dashboard: Interactive visualization and decision support

## Tech Stack
- Python
- scikit-learn, XGBoost
- Prophet
- SHAP
- spaCy
- Streamlit
- FastAPI / Flask
- PostgreSQL

## Documentation
Detailed documentation and design artifacts are available in the `docs/` folder.

## Future Work
- Full model evaluation on real project datasets
- Jira API integration for live data ingestion
- Deployment on cloud infrastructure
