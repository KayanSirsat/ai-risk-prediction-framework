# Architecture - AI-Driven Risk Prediction Framework

## Overview

The AI-Driven Risk Prediction Framework is a comprehensive AI/ML system designed to predict, analyze, and mitigate project risks. The architecture follows a modular, scalable design that enables seamless integration of new features and Phase 2 advanced analytics.

## Directory Structure

```
src/
├── __init__.py                 # Main package exports
├── config.py                   # Global configuration
├── models/                     # Core ML models
│   ├── __init__.py
│   ├── nlp_risk_engine.py     # NLP-based risk detection (Phase 2-C)
│   ├── anomaly_detector.py    # Anomaly detection engine
│   ├── risk_classifier.py     # Risk classification model
│   └── train.py               # Model training pipeline
├── forecasting/                # Time-series forecasting (Phase 2-A)
│   ├── __init__.py
│   └── forecast.py            # Prophet-based forecasting
├── nlp/                        # Natural Language Processing
│   ├── __init__.py
│   └── text_risk_detector.py  # Text risk analysis
├── preprocessing/              # Data preparation
│   ├── __init__.py
│   ├── data_pipeline.py       # Data pipeline orchestration
│   └── preprocess.py          # Feature engineering
├── xai/                        # Explainable AI
│   ├── __init__.py
│   └── shap_explainer.py      # SHAP model explanations
├── mitigation/                 # Risk mitigation
│   ├── __init__.py
│   └── llm_agent.py           # LLM-based mitigation agent
├── anomaly/                    # Phase 2-B (Placeholder)
│   └── __init__.py
├── simulation/                 # Phase 2-D (Placeholder)
│   └── __init__.py
└── integrations/               # Phase 2-E/F (Placeholder)
    └── __init__.py

tests/
├── __init__.py
├── conftest.py                # Pytest configuration & fixtures
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_nlp_risk_engine.py
│   ├── test_nlp_tokenizer_fix.py
│   └── test_anomaly_engine.py
└── integration/                # Integration tests
    ├── __init__.py
    ├── test_nlp_integration.py
    └── benchmark_nlp_engine.py
```

## Key Modules

### 1. Models (`src/models/`)

**RiskNLPEngine** - NLP-based risk detection from text
- Entity extraction for project entities (tasks, resources, dates)
- Sentiment analysis for risk tone
- Risk phrase detection using pattern matching
- Confidence scoring for risk assessment

**AnomalyEngine** - Statistical anomaly detection
- Isolation Forest implementation
- Outlier detection in risk metrics
- Temporal anomaly identification

**RiskClassifier** - Machine learning risk classification
- Multi-class risk categorization
- Probability-based scoring

### 2. Forecasting (`src/forecasting/`)

**ProjectForecaster** - Time-series risk forecasting
- Facebook Prophet for trend prediction
- Handles seasonality and holidays
- Confidence intervals for predictions

### 3. NLP (`src/nlp/`)

**RiskTextDetector** - Text-based risk analysis
- Integration point for NLP models
- Risk score calculation from text

### 4. XAI (`src/xai/`)

**SHAPExplainer** - Model interpretability
- Feature importance analysis
- Decision explanations using SHAP values

### 5. Mitigation (`src/mitigation/`)

**MitigationAgent** - Risk mitigation recommendation engine
- LLM-based strategy generation
- Actionable recommendations

## Import Patterns

### Main Package Imports (Recommended)

```python
# Import from main package
from src import RiskNLPEngine, AnomalyEngine, ProjectForecaster

# Or specific module imports
from src.models import RiskNLPEngine
from src.forecasting import ProjectForecaster
from src.xai import SHAPExplainer
```

### Direct Module Imports

```python
# For more explicit imports
from src.models.nlp_risk_engine import RiskNLPEngine
from src.forecasting.forecast import ProjectForecaster
```

## Phase 2 Extension Points

The framework includes placeholder modules for Phase 2 features:

- **Phase 2-B** (`src/anomaly/`) - Advanced anomaly detection
- **Phase 2-D** (`src/simulation/`) - What-If scenario analysis
- **Phase 2-E/F** (`src/integrations/`) - Jira and OAuth integration

## Configuration

Global configuration is managed in `src/config.py` and supports:
- Environment-based configuration
- Model parameters
- API endpoints
- Data paths

## Testing Architecture

Tests are organized into two categories:

### Unit Tests (`tests/unit/`)
- Isolated component testing
- Fast execution
- No external dependencies
- Run with: `pytest tests/unit/`

### Integration Tests (`tests/integration/`)
- End-to-end workflow validation
- Performance benchmarks
- Real data testing
- Run with: `pytest tests/integration/`

### Pytest Configuration

Global fixtures and configuration in `tests/conftest.py`:
- `project_root` - Root directory path
- `data_dir` - Data directory path
- `github_issues_dataset` - Sample test data

## Build & Installation

### Development Installation

```bash
# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

### Package Configuration

- **setup.py** - Traditional setuptools configuration
- **pyproject.toml** - PEP 517/518 build configuration
- **pytest.ini** - Pytest test discovery and markers

## Design Principles

1. **Modularity** - Each component is self-contained and reusable
2. **Scalability** - Easy to add Phase 2 features without modifying core
3. **Testability** - Comprehensive test coverage with unit/integration separation
4. **Maintainability** - Clear imports, documentation, and configuration
5. **Extensibility** - Phase 2 placeholders prepared for seamless integration

## Future Enhancements

Phase 2 includes:
- Advanced anomaly detection algorithms
- What-If scenario simulation engine
- Jira ticket integration
- OAuth-based authentication
- Real-time risk streaming
- Advanced visualization dashboard
