# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- 16GB+ RAM recommended
- GPU (optional, but recommended for BERT training)

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/1moses1/research-project-model-engines.git
cd model-engine

# Run setup script
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### Option 2: Manual Setup

```bash
# Clone the repository
git clone https://github.com/1moses1/research-project-model-engines.git
cd model-engine

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Verify Installation

```bash
# Test configuration loader
python -c "from src.utils.config_loader import ConfigLoader; print('✅ Config loader works!')"

# Test logger
python -c "from src.utils.logger import setup_logger; print('✅ Logger works!')"

# Generate control taxonomy
python src/data_pipeline/control_mapper.py
```

Expected output:
```
✅ Control taxonomy created successfully!
📁 Output: data/processed/control_taxonomy.json

📊 Summary:
  - Total Controls: 50
  - NIST Controls: 29
  - Rwanda Controls: 21
  - Control Families: 12
```

## Project Structure

```
model-engine/
├── src/                  # Source code
│   ├── data_pipeline/   # Data processing
│   ├── models/          # ML models
│   ├── utils/           # Utilities
│   ├── api/             # Backend API
│   └── ui/              # Dashboard
├── data/                # Data storage
├── docs/                # Documentation
├── config/              # Configuration files
├── logs/                # Application logs
├── outputs/             # Model outputs
├── tests/               # Unit tests
└── notebooks/           # Jupyter notebooks
```

## Running Components

### 1. Generate Control Taxonomy

```bash
python src/data_pipeline/control_mapper.py
```

Output: `data/processed/control_taxonomy.json`

### 2. Generate Synthetic Dataset (Coming Soon)

```bash
python src/data_pipeline/synthetic_generator.py --size 100000
```

Output: `data/synthetic/compliance_events.csv`

### 3. Train BERT Classifier (Coming Soon)

```bash
python src/models/bert_classifier.py --config config/model_config.yaml
```

### 4. Launch Training Dashboard (Coming Soon)

```bash
streamlit run src/ui/dashboard.py
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution**: Make sure you've activated the virtual environment and installed dependencies:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: CUDA out of memory (GPU training)

**Solution**: Reduce batch size in `config/model_config.yaml`:

```yaml
bert:
  training:
    batch_size: 8  # Reduce from 16 to 8
```

### Issue: Download spaCy model failed

**Solution**: Manually download spaCy model:

```bash
python -m spacy download en_core_web_sm
```

## Development Setup

### Install Additional Dev Dependencies

```bash
pip install pytest pytest-cov black flake8 mypy
```

### Run Tests

```bash
pytest tests/ -v --cov=src
```

### Code Formatting

```bash
black src/
flake8 src/
```

## GPU Setup (Optional)

### For NVIDIA GPUs (CUDA)

```bash
# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### For Mac M1/M2 (MPS)

PyTorch with MPS support is included in requirements.txt. No additional setup needed.

### Verify GPU

```python
import torch
print("CUDA available:", torch.cuda.is_available())
print("MPS available:", torch.backends.mps.is_available())
```

## Next Steps

After installation:

1. ✅ Verify installation with test commands above
2. 📊 Generate control taxonomy
3. 🔄 Review `PROGRESS_SUMMARY.md` for current status
4. 📖 Read `docs/research/MODEL_SELECTION_STRATEGY.md`
5. 🚀 Start implementing remaining components

## Support

For issues or questions:
- Check `docs/` directory for detailed documentation
- Review `PROGRESS_SUMMARY.md` for current implementation status
- Open an issue on GitHub: https://github.com/1moses1/research-project-model-engines/issues

## Contributors

- Moise Iradukunda - Carnegie Mellon University
- Claude Code Assistant

---

**Last Updated**: October 2025
