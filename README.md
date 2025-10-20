# AI-Driven Compliance Auditing System for Rwanda's Cybersecurity Standards

## Overview

This research project develops an AI-driven compliance auditing system tailored to Rwanda's National Cyber Security Authority (NCSA) Minimum Cybersecurity Standards, with extensibility to other regulatory frameworks (NIST SP 800-53, ISO 27001, PCI DSS).

### Research Context

- **Case Study**: Rwanda's cybersecurity regulatory framework
- **Primary Standards**: Rwanda NCSA Minimum Cybersecurity Standards
- **Baseline Framework**: NIST SP 800-53
- **Target Accuracy**: >93% with low error rate
- **Key Innovation**: Multi-country regulatory framework adaptability through transfer learning and RAG

## Research Questions

1. How can machine learning effectively automate compliance auditing for cybersecurity controls?
2. What models achieve optimal accuracy (>93%) in log-based compliance classification?
3. How can a base model be designed for extensibility to different countries' regulatory frameworks?
4. What role does explainability (SHAP/LIME) play in building trust in AI-driven auditing?

## Project Objectives

### Mid-October 2025 Deliverable (20%)
- ✅ Comprehensive project structure
- 🔄 Data ingestion pipeline
- 🔄 Log parsing and mapping engine
- 🔄 Baseline ML classifiers (BERT, SVM, LSTM)
- 🔄 Comparative evaluation framework

## Architecture

### Data Pipeline
1. **Synthetic Dataset Generation**: Creates compliance events based on Rwanda NCSA and NIST controls
2. **Log Parsing**: Drain algorithm for extracting structured templates
3. **Data Augmentation**: Increases dataset diversity while preserving semantics
4. **Class Balancing**: Handles imbalanced compliance/non-compliance events

### ML Models

#### Baseline Models (Phase 5)
- **BERT Classifier**: Pre-trained transformer fine-tuned for compliance classification
- **SVM Classifier**: Traditional ML baseline with engineered features
- **LSTM Classifier**: Sequential model for temporal log analysis

#### Transfer Learning (Phase 6)
- Base model architecture for multi-country adaptability
- Fine-tuning pipeline for new regulatory frameworks
- RAG (Retrieval Augmented Generation) integration

### UI/Dashboard (Phase 7)
- Real-time training progress monitoring
- File upload for new regulatory documents
- Integrated Claude assistant for guidance
- Model comparison visualizations
- Interactive evaluation metrics

## Installation

```bash
# Clone the repository
git clone https://github.com/1moses1/research-project-model-engines.git
cd model-engine

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

## Project Structure

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed directory organization.

## Usage

### Data Pipeline
```bash
# Generate synthetic dataset
python src/data_pipeline/synthetic_generator.py --config config/data_config.yaml

# Parse logs with Drain algorithm
python src/data_pipeline/log_parser.py --input data/raw/logs --output data/processed
```

### Model Training
```bash
# Train BERT classifier
python src/models/bert_classifier.py --config config/model_config.yaml

# Train all baseline models and compare
python src/utils/train_all.py --compare
```

### UI Dashboard
```bash
# Launch training dashboard
streamlit run src/ui/dashboard.py

# Or use Gradio interface
python src/ui/gradio_app.py
```

### API Server
```bash
# Start FastAPI backend
uvicorn src.api.app:app --reload --port 8000
```

## Development Roadmap

### ✅ Phase 1: Project Setup & Requirements Analysis
- [x] Extract deliverable requirements
- [x] Initialize Git repository
- [x] Create project structure
- [ ] Document regulatory frameworks

### 🔄 Phase 2: Literature Review
- [ ] Research >93% accuracy models
- [ ] Identify novelty gap
- [ ] Define unique contributions

### 🔄 Phase 3: Model Selection Strategy
- [ ] Compare BERT vs SVM vs LSTM
- [ ] Evaluate fine-tuning vs training from scratch
- [ ] Design comparison framework

### 📋 Phase 4: Data Pipeline
- [ ] Synthetic dataset schema
- [ ] Control mapper (NIST + Rwanda)
- [ ] Log parsing engine
- [ ] Data augmentation
- [ ] Public dataset integration

### 📋 Phase 5: Baseline Models
- [ ] BERT classifier
- [ ] SVM classifier
- [ ] LSTM classifier
- [ ] Comparative evaluation

### 📋 Phase 6: Transfer Learning
- [ ] Multi-country base model
- [ ] Fine-tuning pipeline
- [ ] RAG integration

### 📋 Phase 7: UI/Dashboard
- [ ] Training monitoring interface
- [ ] Backend API
- [ ] Frontend dashboard
- [ ] Claude assistant integration

### 📋 Phase 8: Validation
- [ ] Research question validation
- [ ] End-to-end testing
- [ ] Documentation & reporting

## Key Features

- **Automated Compliance Auditing**: ML-driven analysis of system logs against regulatory controls
- **Multi-Framework Support**: Extensible to Rwanda, NIST, ISO 27001, PCI DSS
- **Explainability**: SHAP/LIME integration for transparent decision-making
- **Real-time Monitoring**: Live training progress and performance metrics
- **Interactive Assistant**: Claude-powered guidance throughout the training process
- **Synthetic Data Generation**: Privacy-preserving dataset construction

## Regulatory Frameworks

### Rwanda Standards
- NCSA Minimum Cybersecurity Standards for Essential Service Providers
- Minimum Cybersecurity Standards for Public Institutions
- Minimum Cybersecurity Standards for Financial Sector
- Cyber Crimes Law
- Law Establishing NCSA

### International Standards
- NIST SP 800-53 (Security and Privacy Controls)
- ISO 27001 (planned for Phase II)
- PCI DSS (planned for Phase II)

## Evaluation Metrics

- **Accuracy**: Overall classification correctness
- **Precision**: True positive rate for compliance detection
- **Recall**: Coverage of actual compliance events
- **F1 Score**: Harmonic mean of precision and recall
- **Error Rate**: Misclassification frequency
- **Explainability**: SHAP value consistency

## Contributing

This is a research project for Carnegie Mellon University. For questions or collaboration inquiries, please open an issue.

## Research Milestones

### Fall 2025
1. ✅ Literature Review & Dataset Strategy (15%) - Mid-September
2. ✅ Proposal Refinement (10%) - Late September
3. 🔄 **Data Pipeline & Baseline Models (20%) - Mid-October** ⬅️ Current Focus
4. Prototype Development Phase I (25%) - Mid-November
5. Mid-Semester Presentation (10%) - Late November
6. Conference Paper Submission (20%) - Early December

### Spring 2026
7. Explainability & Bias Analysis (25%) - February
8. System Expansion & Benchmarking (30%) - March
9. Thesis Draft & Defense (30%) - April-May
10. Journal Publication (15%) - May

## License

This research project is for academic purposes. All rights reserved.

## Acknowledgments

- Carnegie Mellon University
- Rwanda National Cyber Security Authority (NCSA)
- NIST for SP 800-53 framework
- Public cybersecurity log datasets (HDFS, BGL, etc.)

## Contact

Moise Iradukunda - Carnegie Mellon University

---

**Status**: Phase 1 Complete | Phase 2-3 In Progress
**Next Milestone**: Data Pipeline & Baseline Models - Mid-October 2025
