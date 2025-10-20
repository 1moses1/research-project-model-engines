# AI-Driven Compliance Auditing System - Project Structure

## Directory Organization

```
model-engine/
├── src/                          # Source code
│   ├── data_pipeline/           # Data ingestion and processing
│   │   ├── log_parser.py       # Drain algorithm implementation
│   │   ├── synthetic_generator.py  # Synthetic dataset generation
│   │   ├── control_mapper.py   # NIST + Rwanda control mapping
│   │   ├── data_augmentation.py # Data augmentation pipeline
│   │   └── preprocessor.py     # Data preprocessing utilities
│   ├── models/                  # ML model implementations
│   │   ├── bert_classifier.py  # BERT-based model
│   │   ├── svm_classifier.py   # SVM model
│   │   ├── lstm_classifier.py  # LSTM model
│   │   ├── base_model.py       # Base model interface
│   │   └── transfer_learning.py # Fine-tuning capabilities
│   ├── utils/                   # Utility functions
│   │   ├── evaluation.py       # Metrics calculation
│   │   ├── config_loader.py    # Configuration management
│   │   └── logger.py           # Logging utilities
│   ├── api/                     # Backend API
│   │   ├── app.py              # FastAPI application
│   │   ├── routes.py           # API endpoints
│   │   └── claude_integration.py # Claude assistant integration
│   └── ui/                      # Frontend dashboard
│       ├── dashboard.py        # Streamlit/Gradio UI
│       ├── components/         # UI components
│       └── static/             # Static assets
├── data/                        # Data storage
│   ├── raw/                    # Raw regulatory documents
│   ├── processed/              # Processed datasets
│   ├── synthetic/              # Generated synthetic data
│   └── public_datasets/        # HDFS, BGL, etc.
├── docs/                        # Documentation
│   ├── regulatory_frameworks/  # Rwanda laws & NIST docs
│   ├── research/               # Literature review & papers
│   └── deliverables/           # Project deliverables
├── config/                      # Configuration files
│   ├── model_config.yaml       # Model hyperparameters
│   ├── data_config.yaml        # Data pipeline settings
│   └── api_config.yaml         # API configuration
├── logs/                        # Application logs
├── outputs/                     # Model outputs
│   ├── models/                 # Trained model checkpoints
│   ├── evaluation/             # Evaluation results
│   └── reports/                # Generated reports
├── tests/                       # Unit and integration tests
├── notebooks/                   # Jupyter notebooks for experiments
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # Project documentation
```

## Key Components

### Phase 1: Project Setup (Current)
- Git repository initialization
- Directory structure creation
- Regulatory framework documentation

### Phase 2: Literature Review
- Research >93% accuracy models
- Identify novelty gap
- Define unique contributions

### Phase 3: Model Selection
- Compare BERT vs SVM vs LSTM
- Evaluate fine-tuning options
- Design comparison framework

### Phase 4: Data Pipeline
- Synthetic dataset generation
- Log parsing (Drain algorithm)
- Data augmentation & balancing
- Public dataset integration

### Phase 5: Baseline Models
- BERT classifier implementation
- SVM classifier implementation
- LSTM classifier implementation
- Comparative evaluation

### Phase 6: Transfer Learning
- Multi-country extensibility
- Fine-tuning pipeline
- RAG integration

### Phase 7: UI/Dashboard
- Training monitoring interface
- File upload capabilities
- Claude assistant integration
- Real-time visualization

### Phase 8: Validation
- Research question validation
- End-to-end testing
- Documentation & reporting

## Mid-October Deliverable (20%)
**Due: Mid-October 2025**

Requirements:
1. Prototype pipeline + baseline ML models
2. Data ingestion implementation
3. Log mapping functionality
4. Baseline ML classifiers (BERT, SVM, LSTM)

## Success Metrics
- Model accuracy > 93%
- Low error rate
- Multi-country extensibility
- Real-time monitoring capabilities
- Clear documentation of algorithms and results
