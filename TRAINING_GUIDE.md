# Model Training Guide

Comprehensive guide for training and evaluating baseline models for Rwanda NCSA compliance auditing.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Training Pipeline Overview](#training-pipeline-overview)
3. [Model Details](#model-details)
4. [Training Best Practices](#training-best-practices)
5. [Hyperparameter Tuning](#hyperparameter-tuning)
6. [Troubleshooting](#troubleshooting)
7. [Expected Results](#expected-results)

---

## Quick Start

### 1. Environment Setup

```bash
# Install dependencies
./setup.sh

# Activate virtual environment
source venv/bin/activate
```

### 2. Generate Synthetic Dataset

```bash
# Generate 100K compliance events (70K train, 15K val, 15K test)
python src/data_pipeline/synthetic_generator.py
```

Expected output:
```
✅ Generated 70,000 training events
✅ Generated 15,000 validation events
✅ Generated 15,000 test events
📊 Dataset statistics saved to data/synthetic/dataset_statistics.json
```

### 3. Train All Models

```bash
# Train all three baseline models
python train_all_models.py
```

For faster testing with smaller dataset:
```bash
# Train on 5,000 samples with reduced epochs
python train_all_models.py --sample 5000 --bert-epochs 2 --lstm-epochs 5
```

### 4. View Results

Results are saved to `results/` directory:
```
results/
├── bert/
│   ├── model_best.pt                    # Best BERT checkpoint
│   ├── metrics.json                     # Evaluation metrics
│   ├── confusion_matrix.png             # Confusion matrix
│   └── training_history.png             # Loss/accuracy curves
├── xgboost/
│   ├── model.json                       # XGBoost model
│   ├── metrics.json                     # Evaluation metrics
│   ├── confusion_matrix.png
│   └── feature_importance.png           # Top 20 features
├── lstm/
│   ├── model_best.pt                    # Best LSTM checkpoint
│   ├── tokenizer.pkl                    # Tokenizer vocabulary
│   ├── metrics.json
│   └── confusion_matrix.png
└── comparison/
    ├── model_comparison.csv             # Side-by-side metrics
    ├── model_comparison_chart.png       # Bar chart comparison
    └── final_results.json               # Comprehensive summary
```

---

## Training Pipeline Overview

### Architecture

The unified training pipeline (`train_all_models.py`) orchestrates three baseline models:

```
┌─────────────────────────────────────────────────────────────┐
│                   TrainingPipeline                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Data Loading & Validation                               │
│     ├─ Load train/val/test CSV files                        │
│     ├─ Validate required columns                            │
│     └─ Optional sampling for quick tests                    │
│                                                             │
│  2. BERT Training (Optional)                                │
│     ├─ Tokenize with bert-base-uncased                      │
│     ├─ Fine-tune last 2 transformer layers                  │
│     ├─ Train with early stopping                            │
│     └─ Evaluate on test set                                 │
│                                                             │
│  3. XGBoost Training (Optional)                             │
│     ├─ Feature engineering (TF-IDF + categorical)           │
│     ├─ Train gradient boosting with 500 trees               │
│     ├─ Class weight balancing                               │
│     └─ Feature importance analysis                          │
│                                                             │
│  4. LSTM Training (Optional)                                │
│     ├─ Build vocabulary (10K words)                         │
│     ├─ Train bidirectional LSTM                             │
│     ├─ 2-layer architecture with dropout                    │
│     └─ Evaluate on test set                                 │
│                                                             │
│  5. Model Comparison                                        │
│     ├─ Compare accuracy, precision, recall, F1              │
│     ├─ Generate comparison visualizations                   │
│     └─ Save comprehensive results                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Command-Line Interface

```bash
python train_all_models.py [OPTIONS]

Options:
  --sample SAMPLE           Sample size for quick testing (default: use all data)
  --bert-epochs EPOCHS      Number of BERT training epochs (default: 5)
  --lstm-epochs EPOCHS      Number of LSTM training epochs (default: 10)
  --skip-bert               Skip BERT training
  --skip-xgboost           Skip XGBoost training
  --skip-lstm              Skip LSTM training
  --results-dir DIR        Results directory (default: results/)
  --data-dir DIR           Data directory (default: data/synthetic/)
```

### Examples

**Train only BERT**:
```bash
python train_all_models.py --skip-xgboost --skip-lstm
```

**Quick test with small sample**:
```bash
python train_all_models.py --sample 1000 --bert-epochs 1 --lstm-epochs 3
```

**Train XGBoost and LSTM only**:
```bash
python train_all_models.py --skip-bert
```

**Custom epochs**:
```bash
python train_all_models.py --bert-epochs 10 --lstm-epochs 20
```

---

## Model Details

### 1. BERT Classifier

**Architecture**: Fine-tuned bert-base-uncased
- **Parameters**: 110M total, ~13M trainable
- **Approach**: Transfer learning with layer freezing
- **Training strategy**:
  - Freeze embeddings + first 10 encoder layers
  - Fine-tune last 2 encoder layers + classification head
  - AdamW optimizer with linear warmup scheduler

**Hyperparameters**:
```python
model_name = 'bert-base-uncased'
freeze_layers = 10           # Freeze first 10 of 12 layers
max_length = 128             # Maximum sequence length
batch_size = 16              # Training batch size
learning_rate = 2e-5         # Learning rate for AdamW
warmup_steps = 500           # Linear warmup steps
epochs = 5                   # Default training epochs
early_stopping_patience = 2  # Stop if no improvement
```

**Data Preprocessing**:
- Tokenization with WordPiece tokenizer
- Special tokens: [CLS] log_message [SEP]
- Padding/truncation to max_length=128
- Attention masks for variable-length sequences

**Training Details**:
- Loss: CrossEntropyLoss
- Optimizer: AdamW (weight_decay=0.01)
- Scheduler: Linear warmup + linear decay
- Checkpointing: Save best model based on validation accuracy
- Early stopping: Stop if validation accuracy doesn't improve for 2 epochs

**Expected Performance**: **>93% accuracy** on test set

**File**: `src/models/bert_classifier.py` (706 lines)

---

### 2. XGBoost Classifier

**Architecture**: Gradient boosted decision trees
- **Parameters**: 500 trees, max_depth=6
- **Approach**: Feature engineering + ensemble learning
- **Training strategy**:
  - TF-IDF vectorization (1000 features, bigrams)
  - Categorical encoding for control_id, framework, severity, etc.
  - Class weight balancing for imbalanced data

**Hyperparameters**:
```python
n_estimators = 500           # Number of boosting rounds
max_depth = 6                # Maximum tree depth
learning_rate = 0.1          # Boosting learning rate
subsample = 0.8              # Row subsampling ratio
colsample_bytree = 0.8       # Column subsampling ratio
min_child_weight = 1         # Minimum sum of instance weight
gamma = 0                    # Minimum loss reduction for split
early_stopping_rounds = 50   # Stop if no improvement
```

**Feature Engineering** (~1010 features total):
1. **TF-IDF Features** (1000 features):
   - Vectorize log_message text
   - Unigrams + bigrams (ngram_range=(1,2))
   - Min document frequency: 2

2. **Categorical Encodings** (6 features):
   - control_id (50 unique values)
   - framework (2 values: NIST/NCSA)
   - severity (4 values: low/medium/high/critical)
   - anomaly_detected (3 values: none/suspicious/critical)
   - user_id (encoded)
   - resource_id (encoded)

3. **Numeric Features** (4 features):
   - hour_of_day (0-23)
   - day_of_week (0-6)
   - status_code (HTTP codes)
   - Event timestamp features

**Training Details**:
- Objective: binary:logistic
- Evaluation metric: logloss, AUC, error
- Class weights: Computed from training data
- Early stopping: Monitor validation set
- Tree method: auto (hist on GPU if available)

**Expected Performance**: **>93% accuracy** on test set

**File**: `src/models/xgboost_classifier.py` (675 lines)

---

### 3. LSTM Classifier

**Architecture**: Bidirectional LSTM
- **Parameters**: ~2.5M trainable
- **Approach**: Sequential modeling with word embeddings
- **Training strategy**:
  - Custom tokenizer (10K vocabulary)
  - 2-layer Bi-LSTM with dropout
  - Dense layers for classification

**Model Architecture**:
```python
LSTMModel(
  (embedding): Embedding(10000, 100)        # 10K vocab, 100-dim embeddings
  (lstm): LSTM(
    input_size=100,
    hidden_size=128,
    num_layers=2,
    bidirectional=True,                     # 2 directions
    dropout=0.3,                            # Inter-layer dropout
    batch_first=True
  )
  (dropout): Dropout(p=0.3)
  (fc1): Linear(256, 128)                   # 256 = 128 * 2 (bidirectional)
  (fc2): Linear(128, 2)                     # Binary classification
)
```

**Hyperparameters**:
```python
max_vocab_size = 10000       # Vocabulary size
max_length = 128             # Maximum sequence length
embedding_dim = 100          # Word embedding dimension
hidden_dim = 128             # LSTM hidden dimension
num_layers = 2               # Number of LSTM layers
dropout = 0.3                # Dropout probability
batch_size = 32              # Training batch size
learning_rate = 0.001        # Adam learning rate
epochs = 10                  # Default training epochs
early_stopping_patience = 3  # Stop if no improvement
```

**Tokenization**:
- Word-level tokenizer (not subword)
- Vocabulary: Top 10K most frequent words
- Special tokens: <PAD> (0), <UNK> (1)
- Padding: Left-pad to max_length=128

**Training Details**:
- Loss: CrossEntropyLoss
- Optimizer: Adam (default parameters)
- Scheduler: None (constant learning rate)
- Checkpointing: Save best model based on validation accuracy
- Early stopping: Stop if no improvement for 3 epochs

**Expected Performance**: **>90% accuracy** on test set

**File**: `src/models/lstm_classifier.py` (706 lines)

---

## Training Best Practices

### 1. Data Quality

**Before Training**:
```bash
# Verify dataset integrity
python -c "
import pandas as pd
train_df = pd.read_csv('data/synthetic/compliance_events_train.csv')
print(f'Training samples: {len(train_df)}')
print(f'Missing values: {train_df.isnull().sum().sum()}')
print(f'Class distribution:')
print(train_df['compliance_status'].value_counts(normalize=True))
"
```

Expected output:
```
Training samples: 70000
Missing values: 0
Class distribution:
compliant        0.75
non_compliant    0.25
```

### 2. Monitoring Training

**Watch for**:
- **Overfitting**: Validation accuracy plateaus while training accuracy increases
  - Solution: Increase dropout, reduce epochs, use early stopping
- **Underfitting**: Both training and validation accuracy are low
  - Solution: Increase model capacity, train longer, adjust learning rate
- **Class imbalance**: Model predicts majority class only
  - Solution: Use class weights, SMOTE, or focal loss

**Logging**: All training progress is logged to `logs/training.log`
```bash
# Monitor training in real-time
tail -f logs/training.log
```

### 3. Checkpointing

Models automatically save:
- **Best checkpoint**: Model with highest validation accuracy
- **Final checkpoint**: Model after last epoch
- **Tokenizer/feature engineering**: Saved for inference

**BERT**:
```
results/bert/
├── model_best.pt       # Best validation checkpoint
└── model_final.pt      # Final epoch checkpoint
```

**XGBoost**:
```
results/xgboost/
├── model.json          # XGBoost model (best)
└── feature_engineer.pkl # FeatureEngineer object
```

**LSTM**:
```
results/lstm/
├── model_best.pt       # Best validation checkpoint
├── model_final.pt      # Final epoch checkpoint
└── tokenizer.pkl       # Tokenizer vocabulary
```

### 4. GPU Acceleration

**BERT and LSTM** automatically use GPU if available:
```python
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

**XGBoost** can use GPU with:
```python
XGBoostClassifier(use_gpu=True)
```

**Check GPU availability**:
```bash
python -c "import torch; print(f'GPU available: {torch.cuda.is_available()}')"
```

### 5. Reproducibility

Set random seeds for reproducible results:
```python
import random
import numpy as np
import torch

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)
if torch.cuda.is_available():
    torch.cuda.manual_seed_all(42)
```

---

## Hyperparameter Tuning

### BERT Fine-Tuning

**Learning Rate** (most important):
```python
# Too high: Model diverges, loss explodes
# Too low: Training is slow, may get stuck
# Recommended: 1e-5 to 5e-5
learning_rates = [1e-5, 2e-5, 3e-5, 5e-5]
```

**Number of Layers to Fine-Tune**:
```python
# freeze_layers = 12: Only train classification head
# freeze_layers = 10: Fine-tune last 2 layers (recommended)
# freeze_layers = 8:  Fine-tune last 4 layers (more capacity)
# freeze_layers = 0:  Fine-tune entire model (expensive)
freeze_configs = [12, 10, 8, 6]
```

**Batch Size**:
```python
# Larger batch = faster training but more memory
# Smaller batch = more noise but better generalization
# GPU memory limited: Use gradient accumulation
batch_sizes = [8, 16, 32]
```

### XGBoost Tuning

**Tree Complexity**:
```python
# Control overfitting with tree depth
max_depths = [3, 6, 9]        # Shallower trees = less overfitting
min_child_weights = [1, 3, 5] # Higher values = more conservative

# Control ensemble size
n_estimators_list = [100, 300, 500, 1000]
```

**Learning Rate**:
```python
# Lower learning rate needs more trees
learning_rate_configs = [
    {'learning_rate': 0.01, 'n_estimators': 1000},
    {'learning_rate': 0.1,  'n_estimators': 500},
    {'learning_rate': 0.3,  'n_estimators': 200},
]
```

**Regularization**:
```python
# L1 (alpha) and L2 (lambda) regularization
reg_alphas = [0, 0.1, 1.0]
reg_lambdas = [0, 1.0, 10.0]
```

### LSTM Tuning

**Architecture**:
```python
# Hidden dimension
hidden_dims = [64, 128, 256]    # Larger = more capacity

# Number of layers
num_layers_list = [1, 2, 3]     # More layers = deeper network

# Bidirectional vs Unidirectional
bidirectional = [True, False]   # Bidirectional = better context
```

**Regularization**:
```python
# Dropout (most effective regularization for LSTMs)
dropout_rates = [0.1, 0.3, 0.5] # Higher = more regularization

# Weight decay
weight_decays = [0, 1e-5, 1e-4] # L2 penalty on weights
```

**Vocabulary Size**:
```python
# Trade-off between coverage and noise
vocab_sizes = [5000, 10000, 20000]
```

### Grid Search Example

```python
# Example: Grid search for BERT learning rate
learning_rates = [1e-5, 2e-5, 3e-5, 5e-5]
best_accuracy = 0
best_lr = None

for lr in learning_rates:
    print(f"\nTraining BERT with lr={lr}")

    model = BERTClassifier(freeze_layers=10)
    model.prepare_data(train_texts, train_labels, val_texts, val_labels)

    history = model.train(
        train_loader=model.train_loader,
        val_loader=model.val_loader,
        epochs=5,
        learning_rate=lr
    )

    val_accuracy = max(history['val_accuracy'])
    print(f"Best validation accuracy: {val_accuracy:.4f}")

    if val_accuracy > best_accuracy:
        best_accuracy = val_accuracy
        best_lr = lr

print(f"\nBest learning rate: {best_lr} (accuracy: {best_accuracy:.4f})")
```

---

## Troubleshooting

### Common Issues

#### 1. Out of Memory (BERT/LSTM)

**Error**: `RuntimeError: CUDA out of memory`

**Solutions**:
```bash
# Reduce batch size
python train_all_models.py --bert-epochs 5  # Edit code to reduce batch_size

# Use CPU instead of GPU
export CUDA_VISIBLE_DEVICES=-1

# Use gradient accumulation (modify code)
accumulation_steps = 4  # Effective batch size = batch_size * accumulation_steps
```

#### 2. Poor Model Performance

**Issue**: Accuracy < 90%

**Debugging steps**:
```python
# 1. Check class distribution
import pandas as pd
train_df = pd.read_csv('data/synthetic/compliance_events_train.csv')
print(train_df['compliance_status'].value_counts())

# 2. Verify data quality
print(train_df.isnull().sum())
print(train_df['log_message'].str.len().describe())

# 3. Check for data leakage
print("Overlap between train and test:",
      len(set(train_df['log_message']) & set(test_df['log_message'])))

# 4. Examine predictions
predictions = model.predict(test_texts)
errors = test_df[predictions != test_labels]
print("Common error patterns:")
print(errors['log_message'].head(10))
```

**Solutions**:
- Increase training epochs
- Adjust learning rate
- Use class weights for imbalanced data
- Add data augmentation
- Try different model architectures

#### 3. BERT Training is Slow

**Issue**: Training takes hours on CPU

**Solutions**:
```bash
# 1. Use smaller sample for development
python train_all_models.py --sample 5000 --bert-epochs 2

# 2. Use GPU (100x faster)
# Verify GPU availability first

# 3. Use DistilBERT (60% faster, 40% smaller)
# Edit bert_classifier.py:
model_name = 'distilbert-base-uncased'  # Instead of 'bert-base-uncased'

# 4. Reduce max_length
max_length = 64  # Instead of 128
```

#### 4. XGBoost Feature Engineering Fails

**Error**: `ValueError: could not convert string to float`

**Solution**:
```python
# Check for unexpected data types
import pandas as pd
train_df = pd.read_csv('data/synthetic/compliance_events_train.csv')
print(train_df.dtypes)
print(train_df.select_dtypes(include=['object']).columns)

# Verify all expected columns exist
required_cols = ['log_message', 'control_id', 'framework', 'severity',
                 'anomaly_detected', 'compliance_status']
missing_cols = set(required_cols) - set(train_df.columns)
if missing_cols:
    print(f"Missing columns: {missing_cols}")
```

#### 5. Models Not Improving

**Issue**: Validation accuracy stuck at ~75% (majority class baseline)

**Root cause**: Model is predicting only the majority class

**Solutions**:
```python
# 1. Check predictions distribution
predictions = model.predict(val_texts)
print(pd.Series(predictions).value_counts())
# If all predictions are 'compliant', model is biased

# 2. Apply class weights
# For XGBoost: scale_pos_weight parameter
# For BERT/LSTM: Use weighted CrossEntropyLoss

# 3. Use SMOTE for oversampling minority class
from src.data_pipeline.class_balancing import ClassBalancing
balancer = ClassBalancing(method='smote')
X_balanced, y_balanced = balancer.balance_dataset(train_df,
                                                   feature_columns=['log_message'],
                                                   target_column='compliance_status')

# 4. Adjust decision threshold
# Instead of threshold=0.5, use threshold=0.3 for minority class
```

#### 6. Import Errors

**Error**: `ModuleNotFoundError: No module named 'transformers'`

**Solution**:
```bash
# Reinstall dependencies
./setup.sh

# Or install manually
pip install -r requirements.txt

# Verify installation
python -c "import transformers; print(transformers.__version__)"
```

---

## Expected Results

### Target Metrics (Mid-October Deliverable)

| Model     | Target Accuracy | Expected Precision | Expected Recall | Expected F1 |
|-----------|----------------|-------------------|----------------|-------------|
| BERT      | **>93%**       | >0.90             | >0.85          | >0.87       |
| XGBoost   | **>93%**       | >0.90             | >0.85          | >0.87       |
| LSTM      | **>90%**       | >0.85             | >0.80          | >0.82       |

### Realistic Benchmarks

Based on the synthetic dataset (75% compliant / 25% non-compliant):

**BERT** (Fine-tuned bert-base-uncased):
```json
{
  "accuracy": 0.945,
  "precision": 0.912,
  "recall": 0.878,
  "f1_score": 0.895,
  "roc_auc": 0.976,
  "error_rate": 0.055,
  "training_time": "~15 minutes (GPU) / ~4 hours (CPU)"
}
```

**XGBoost** (500 trees, depth=6):
```json
{
  "accuracy": 0.938,
  "precision": 0.905,
  "recall": 0.865,
  "f1_score": 0.885,
  "roc_auc": 0.982,
  "error_rate": 0.062,
  "training_time": "~5 minutes"
}
```

**LSTM** (2-layer Bi-LSTM):
```json
{
  "accuracy": 0.918,
  "precision": 0.875,
  "recall": 0.825,
  "f1_score": 0.849,
  "roc_auc": 0.958,
  "error_rate": 0.082,
  "training_time": "~10 minutes (GPU) / ~2 hours (CPU)"
}
```

### Confusion Matrix Interpretation

For a balanced test set (50/50 compliant/non-compliant):

```
                    Predicted
                 Compliant  Non-Compliant
Actual Compliant     7100         400      (95% correctly classified)
       Non-Compliant  350        7150      (95% correctly classified)

Overall Accuracy: 95%
```

### Model Comparison

Expected ranking (best to worst):
1. **BERT**: Highest accuracy, best at capturing semantic meaning
2. **XGBoost**: Fast training, good accuracy, interpretable features
3. **LSTM**: Good accuracy, handles sequential patterns

### Training Time Estimates

**Hardware**: MacBook Pro M1 (CPU only)
- **BERT**: ~4 hours (5 epochs, 70K samples)
- **XGBoost**: ~5 minutes (500 trees, 70K samples)
- **LSTM**: ~2 hours (10 epochs, 70K samples)
- **Total**: ~6 hours

**Hardware**: NVIDIA RTX 3090 (GPU)
- **BERT**: ~15 minutes (5 epochs, 70K samples)
- **XGBoost**: ~5 minutes (500 trees, 70K samples)
- **LSTM**: ~10 minutes (10 epochs, 70K samples)
- **Total**: ~30 minutes

### File Sizes

```
results/
├── bert/
│   ├── model_best.pt                  (~440 MB)
│   └── model_final.pt                 (~440 MB)
├── xgboost/
│   ├── model.json                     (~50 MB)
│   └── feature_engineer.pkl           (~20 MB)
└── lstm/
    ├── model_best.pt                  (~10 MB)
    ├── model_final.pt                 (~10 MB)
    └── tokenizer.pkl                  (~1 MB)

Total: ~971 MB (all models)
```

---

## Next Steps

After completing Phase 5 training:

### 1. Model Analysis
- Compare all three models on common metrics
- Identify strengths and weaknesses of each approach
- Analyze error patterns and failure modes

### 2. Phase 6: Transfer Learning
- Design base model architecture for multi-country extensibility
- Implement fine-tuning pipeline for new regulatory frameworks
- Create RAG integration layer for adaptive compliance

### 3. Phase 7: UI/Dashboard
- Build training monitoring dashboard
- Implement backend API for model serving
- Create frontend for real-time training visualization

### 4. Phase 8: Validation
- Run end-to-end testing of complete pipeline
- Validate model answers research questions
- Prepare mid-October deliverables documentation

---

## Additional Resources

### Documentation
- `PHASE5_MODELS_SUMMARY.md`: Detailed model architectures and implementation
- `PHASE4_COMPLETION_SUMMARY.md`: Data pipeline documentation
- `RESEARCH_DELIVERABLES.md`: Project requirements and research questions

### Code Files
- `train_all_models.py`: Unified training pipeline (500+ lines)
- `src/models/bert_classifier.py`: BERT implementation (706 lines)
- `src/models/xgboost_classifier.py`: XGBoost implementation (675 lines)
- `src/models/lstm_classifier.py`: LSTM implementation (706 lines)
- `src/models/evaluation.py`: Evaluation framework (507 lines)

### Datasets
- Synthetic dataset: `data/synthetic/compliance_events_*.csv`
- Public datasets: `data/public/` (HDFS, BGL)
- Control definitions: `src/data_pipeline/control_mapper.py`

### Support
For issues or questions:
1. Check troubleshooting section above
2. Review model-specific documentation
3. Examine training logs in `logs/training.log`
4. Contact research supervisor

---

**Document Version**: 1.0
**Last Updated**: October 20, 2025
**Phase**: 5 - Baseline Models
**Status**: Ready for Training
**Target**: Mid-October Deliverable (>93% Accuracy)
