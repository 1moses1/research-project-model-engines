# Source Code Directory (`src/`)

This directory contains all source code for the Rwanda NCSA Compliance Monitoring System.

## Directory Structure

```
src/
├── api/                    # Secure API endpoints for model serving
├── data_pipeline/          # Data ingestion, preprocessing, and generation
├── explainability/         # SHAP explanations and model interpretability
├── integrations/           # External system integrations (SIEM, databases)
├── models/                 # ML model implementations (XGBoost, BERT, LSTM)
├── nlp/                    # NLP utilities (tokenization, embeddings, log parsing)
├── security/               # Security layer (auth, encryption, validation)
├── training/               # Model training orchestration and evaluation
└── utils/                  # Utility functions (config loading, logging)
```

## Key Modules

### 1. API (`src/api/`)

**Purpose**: Production-ready secure API for model inference

**Key Files**:
- `secure_api.py`: Flask API with JWT authentication, RBAC, rate limiting, HTTPS
- Endpoints: `/api/predict`, `/api/predict/batch`, `/api/auth/login`, `/api/health`

**Usage**:
```bash
python src/api/secure_api.py
```

### 2. Data Pipeline (`src/data_pipeline/`)

**Purpose**: Data generation, preprocessing, and formatting

**Key Files**:
- `synthetic_generator.py`: Generates 100K compliance events from control definitions
- `control_mapper.py`: Maps NIST SP 800-53 and Rwanda NCSA controls
- `log_parser.py`: Drain algorithm for log template extraction
- `public_dataset_preprocessor.py`: Processes NSL-KDD and LogHub datasets

**Usage**:
```bash
# Generate synthetic data
python src/data_pipeline/synthetic_generator.py --output data/synthetic/

# Preprocess public datasets
python src/data_pipeline/public_dataset_preprocessor.py
```

### 3. Security (`src/security/`)

**Purpose**: 9-layer security framework for production deployment

**Key Files**:
- `input_validator.py`: Input validation and sanitization
- `auth.py`: JWT authentication and RBAC
- `rate_limiter.py`: API rate limiting (60/min, 1K/hr, 10K/day)
- `adversarial_detector.py`: Statistical anomaly detection
- `model_signing.py`: Cryptographic model integrity (HMAC-SHA256)
- `encryption.py`: File encryption and data protection

**Security Layers**:
1. Input validation (length, characters, patterns)
2. Authentication (JWT tokens, API keys)
3. Authorization (role-based access control)
4. Rate limiting (abuse prevention)
5. Adversarial detection (evasion attempts)
6. Model integrity (cryptographic signatures)
7. Data protection (encryption at rest)
8. Audit logging (security events tracking)
9. Monitoring (incident response)

### 4. Models (`src/models/`)

**Purpose**: ML model implementations

**Key Files**:
- `xgboost_classifier.py`: XGBoost Phase 2.5 (production model)
- `bert_classifier.py`: BERT fine-tuned classifier (experimental)
- `lstm_classifier.py`: BiLSTM classifier (experimental)

**Model Selection**: XGBoost Phase 2.5 is the production model (99.49% accuracy, 1ms inference)

### 5. Training (`src/training/`)

**Purpose**: Model training orchestration and evaluation

**Key Files**:
- `trainer.py`: Unified training pipeline
- `evaluator.py`: Performance metrics calculation
- `cross_validator.py`: K-fold cross-validation

**Usage**:
```bash
# Train XGBoost Phase 2.5
python train_xgboost_phase2_5.py --data-dir data/real_formatted/
```

### 6. Explainability (`src/explainability/`)

**Purpose**: Model interpretability and SHAP explanations

**Key Files**:
- `shap_explainer.py`: SHAP value calculation for XGBoost
- `visualization.py`: SHAP plots (global importance, summary, dependence)

**Usage**:
```python
from src.explainability.shap_explainer import SHAPExplainer

explainer = SHAPExplainer(model)
shap_values = explainer.explain(X_test)
explainer.plot_summary(shap_values, X_test)
```

## Architecture Patterns

### Dependency Injection
Models and utilities accept dependencies via constructors for testability:
```python
class XGBoostClassifier:
    def __init__(self, config: dict, logger: logging.Logger):
        self.config = config
        self.logger = logger
```

### Configuration Management
All modules load configuration from `config/` directory:
```python
from src.utils.config_loader import load_config

config = load_config('config/model_config.yaml')
```

### Logging
Standardized logging across all modules:
```python
from src.utils.logger import setup_logger

logger = setup_logger('module_name', 'logs/module.log')
logger.info("Processing started")
```

## Testing

Run unit tests:
```bash
pytest tests/
```

Run integration tests:
```bash
pytest tests/integration/
```

## Development Guidelines

1. **Code Style**: Follow PEP 8
2. **Type Hints**: Use type annotations for all functions
3. **Docstrings**: Google-style docstrings for all classes and functions
4. **Error Handling**: Use try-except blocks with specific exceptions
5. **Logging**: Log at appropriate levels (DEBUG, INFO, WARNING, ERROR)

## Performance Considerations

- **XGBoost**: 1ms inference, 100 MB RAM, CPU-only
- **BERT**: 100ms inference, 400 MB RAM, GPU recommended
- **LSTM**: 20ms inference, 50 MB RAM, CPU-only

## Security Considerations

- **Never commit** credentials, API keys, or signing keys
- **Always validate** user input before processing
- **Always log** security events to audit logs
- **Always verify** model signatures before loading

---

**Last Updated**: November 3, 2025
**Version**: 2.0 (Production-Ready)
