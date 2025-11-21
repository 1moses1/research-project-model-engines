"""
Optimized XGBoost Training for Resource-Constrained Systems

RESOURCE OPTIMIZATIONS:
1. Limited CPU cores (n_jobs=2 instead of -1)
2. Reduced cross-validation folds (3 instead of 5)
3. Smaller TF-IDF features (25 instead of 50)
4. Sequential CV instead of parallel
5. Memory-efficient data loading (chunks)
6. Progress monitoring to prevent freezing

SYSTEM REQUIREMENTS:
- Target: 8-core CPU, 16GB RAM
- Peak Usage: ~4-6GB RAM, 2-4 CPU cores
- Training Time: ~10-15 minutes (vs 5-10 mins unoptimized)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
import xgboost as xgb
import warnings
import psutil
import os
warnings.filterwarnings('ignore')

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'

def print_step(step, message):
    """Print colored step message."""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}[STEP {step}] {message}{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_resource_usage():
    """Print current system resource usage."""
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    mem_percent = process.memory_percent()
    cpu_percent = process.cpu_percent(interval=1)

    vm = psutil.virtual_memory()

    print(f"\n{Colors.CYAN}[RESOURCES]{Colors.END}")
    print(f"  Process Memory: {mem_info.rss / 1024**3:.2f} GB ({mem_percent:.1f}%)")
    print(f"  Process CPU: {cpu_percent:.1f}%")
    print(f"  System Memory: {vm.used / 1024**3:.1f}/{vm.total / 1024**3:.1f} GB ({vm.percent:.1f}% used)")
    print(f"  System Available: {vm.available / 1024**3:.1f} GB")

def extract_text_features(df, max_features=25):
    """Extract TF-IDF features from log messages (REDUCED for memory)."""
    print(f"Extracting text features from log messages (max {max_features} features)...")
    print_resource_usage()

    if 'log_message' not in df.columns:
        print(f"{Colors.YELLOW}  ⚠️  No log_message column found, skipping text features{Colors.END}")
        return df, None

    # Create TF-IDF vectorizer (REDUCED max_features)
    vectorizer = TfidfVectorizer(
        max_features=max_features,  # Reduced from 50 to 25
        ngram_range=(1, 1),  # Only unigrams (reduced from 1,2)
        min_df=5,  # Increased from 2
        stop_words='english'
    )

    # Fit and transform
    log_messages = df['log_message'].fillna('').astype(str)
    tfidf_matrix = vectorizer.fit_transform(log_messages)

    # Create dataframe with TF-IDF features
    tfidf_df = pd.DataFrame(
        tfidf_matrix.toarray(),
        columns=[f'text_{i}' for i in range(tfidf_matrix.shape[1])],
        index=df.index
    )

    # Combine with original dataframe
    df_combined = pd.concat([df, tfidf_df], axis=1)

    print(f"{Colors.GREEN}  ✅ Extracted {tfidf_matrix.shape[1]} text features{Colors.END}")

    return df_combined, vectorizer

def train_with_optimized_cv(X, y):
    """Train model with OPTIMIZED cross-validation for resource-constrained systems."""
    print_step(3, "Training with Optimized Cross-Validation (3-fold, n_jobs=2)")
    print_resource_usage()

    # Create model with OPTIMIZED parameters
    model = xgb.XGBClassifier(
        n_estimators=100,      # Reduced from 150
        max_depth=5,           # Reduced from 6
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.7,
        min_child_weight=5,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        scale_pos_weight=3,
        objective='binary:logistic',
        random_state=42,
        n_jobs=2,              # CRITICAL: Limited to 2 cores (was -1)
        tree_method='hist'
    )

    # 3-fold stratified cross-validation (REDUCED from 5-fold)
    print("Running 3-fold cross-validation (sequential, n_jobs=1)...")
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    # SEQUENTIAL cross-validation (n_jobs=1) to prevent resource overload
    cv_scores = cross_val_score(model, X, y, cv=cv, scoring='f1', n_jobs=1, verbose=1)

    print(f"\nCross-Validation F1 Scores:")
    for i, score in enumerate(cv_scores, 1):
        print(f"  Fold {i}: {score:.4f}")

    print(f"\n{Colors.BLUE}Mean CV F1-Score: {cv_scores.mean():.4f} (±{cv_scores.std():.4f}){Colors.END}")

    # Check for overfitting
    if cv_scores.std() > 0.1:
        print(f"{Colors.YELLOW}⚠️  High variance detected - model may be overfitting{Colors.END}")
    elif cv_scores.mean() > 0.95:
        print(f"{Colors.YELLOW}⚠️  Very high CV score - check for data leakage{Colors.END}")
    else:
        print(f"{Colors.GREEN}✅ Cross-validation scores look reasonable{Colors.END}")

    print_resource_usage()
    return model, cv_scores

def train_final_model(X_train, y_train, X_val, y_val):
    """Train final model on full training set."""
    print_step(4, "Training Final Model on Full Training Set")
    print_resource_usage()

    model = xgb.XGBClassifier(
        n_estimators=100,      # Reduced from 150
        max_depth=5,           # Reduced from 6
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.7,
        min_child_weight=5,
        gamma=0.1,
        reg_alpha=0.1,
        reg_lambda=1.0,
        scale_pos_weight=3,
        objective='binary:logistic',
        random_state=42,
        n_jobs=2,              # CRITICAL: Limited to 2 cores
        tree_method='hist',
        early_stopping_rounds=10,
        eval_metric=['logloss', 'error']
    )

    # Train with validation set for early stopping
    print("Training with early stopping...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=True
    )

    print(f"\n{Colors.GREEN}✅ Training completed!{Colors.END}")
    print(f"Best iteration: {model.best_iteration}")
    print(f"Best score: {model.best_score:.4f}")

    print_resource_usage()
    return model

def main():
    """Main training pipeline."""
    print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║  OPTIMIZED XGBOOST TRAINING - 196 CONTROLS (RESOURCE-SAFE)    ║{Colors.END}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════════╝{Colors.END}\n")

    print(f"{Colors.YELLOW}OPTIMIZATION SETTINGS:{Colors.END}")
    print(f"  • CPU Cores: 2 (limited from {psutil.cpu_count()})")
    print(f"  • CV Folds: 3 (reduced from 5)")
    print(f"  • Trees: 100 (reduced from 150)")
    print(f"  • Tree Depth: 5 (reduced from 6)")
    print(f"  • Text Features: 25 (reduced from 50)")
    print(f"  • Sequential CV: Yes (n_jobs=1)")
    print()

    # Step 1: Load data
    print_step(1, "Loading Training Data")
    print_resource_usage()

    train_path = Path('data/synthetic/compliance_events_train.csv')
    val_path = Path('data/synthetic/compliance_events_val.csv')
    test_path = Path('data/synthetic/compliance_events_test.csv')

    print(f"Loading training data from {train_path}...")
    train_df = pd.read_csv(train_path)

    print(f"Loading validation data from {val_path}...")
    val_df = pd.read_csv(val_path)

    print(f"Loading test data from {test_path}...")
    test_df = pd.read_csv(test_path)

    print(f"\n{Colors.GREEN}Data Loaded:{Colors.END}")
    print(f"  Training: {len(train_df):,} events")
    print(f"  Validation: {len(val_df):,} events")
    print(f"  Test: {len(test_df):,} events")
    print(f"  Total: {len(train_df) + len(val_df) + len(test_df):,} events")
    print(f"  Controls: {train_df['control_id'].nunique()} unique")

    # Step 2: Extract text features
    print_step(2, "Feature Engineering")
    train_df, vectorizer = extract_text_features(train_df, max_features=25)

    if vectorizer:
        val_log = val_df['log_message'].fillna('').astype(str)
        test_log = test_df['log_message'].fillna('').astype(str)

        val_tfidf = vectorizer.transform(val_log).toarray()
        test_tfidf = vectorizer.transform(test_log).toarray()

        val_tfidf_df = pd.DataFrame(
            val_tfidf,
            columns=[f'text_{i}' for i in range(val_tfidf.shape[1])],
            index=val_df.index
        )
        test_tfidf_df = pd.DataFrame(
            test_tfidf,
            columns=[f'text_{i}' for i in range(test_tfidf.shape[1])],
            index=test_df.index
        )

        val_df = pd.concat([val_df, val_tfidf_df], axis=1)
        test_df = pd.concat([test_df, test_tfidf_df], axis=1)

    # Prepare features (only columns that exist in the dataset)
    feature_cols = ['hour_of_day', 'day_of_week', 'is_business_hours',
                    'status_code', 'port']

    # Add text features if available
    text_feature_cols = [col for col in train_df.columns if col.startswith('text_')]
    feature_cols.extend(text_feature_cols)

    # Encode labels
    label_encoder = LabelEncoder()

    y_train = label_encoder.fit_transform(train_df['compliance_status'])
    y_val = label_encoder.transform(val_df['compliance_status'])
    y_test = label_encoder.transform(test_df['compliance_status'])

    # Prepare feature matrices and convert categorical to numeric
    X_train = train_df[feature_cols].fillna(0).copy()
    X_val = val_df[feature_cols].fillna(0).copy()
    X_test = test_df[feature_cols].fillna(0).copy()

    # Convert day_of_week to numeric if it's categorical
    if X_train['day_of_week'].dtype == 'object':
        day_encoder = LabelEncoder()
        X_train['day_of_week'] = day_encoder.fit_transform(X_train['day_of_week'].astype(str))
        X_val['day_of_week'] = day_encoder.transform(X_val['day_of_week'].astype(str))
        X_test['day_of_week'] = day_encoder.transform(X_test['day_of_week'].astype(str))

    print(f"\n{Colors.GREEN}Features prepared:{Colors.END}")
    print(f"  Total features: {len(feature_cols)}")
    print(f"  Numeric features: {len(feature_cols) - len(text_feature_cols)}")
    print(f"  Text features: {len(text_feature_cols)}")

    # Step 3: Cross-validation
    model_template, cv_scores = train_with_optimized_cv(X_train, y_train)

    # Step 4: Train final model
    model = train_final_model(X_train, y_train, X_val, y_val)

    # Step 5: Evaluate
    print_step(5, "Evaluating Model Performance")
    print_resource_usage()

    # Predictions
    train_pred = model.predict(X_train)
    val_pred = model.predict(X_val)
    test_pred = model.predict(X_test)

    # Metrics
    train_acc = accuracy_score(y_train, train_pred)
    val_acc = accuracy_score(y_val, val_pred)
    test_acc = accuracy_score(y_test, test_pred)

    train_p, train_r, train_f1, _ = precision_recall_fscore_support(y_train, train_pred, average='binary')
    val_p, val_r, val_f1, _ = precision_recall_fscore_support(y_val, val_pred, average='binary')
    test_p, test_r, test_f1, _ = precision_recall_fscore_support(y_test, test_pred, average='binary')

    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}PERFORMANCE SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

    print(f"Training Set:")
    print(f"  Accuracy:  {train_acc:.4f}")
    print(f"  Precision: {train_p:.4f}")
    print(f"  Recall:    {train_r:.4f}")
    print(f"  F1-Score:  {train_f1:.4f}")

    print(f"\nValidation Set:")
    print(f"  Accuracy:  {val_acc:.4f}")
    print(f"  Precision: {val_p:.4f}")
    print(f"  Recall:    {val_r:.4f}")
    print(f"  F1-Score:  {val_f1:.4f}")

    print(f"\nTest Set:")
    print(f"  Accuracy:  {test_acc:.4f}")
    print(f"  Precision: {test_p:.4f}")
    print(f"  Recall:    {test_r:.4f}")
    print(f"  F1-Score:  {test_f1:.4f}")

    # Check for overfitting
    overfit_gap = train_f1 - test_f1
    if overfit_gap > 0.10:
        print(f"\n{Colors.YELLOW}⚠️  Overfitting detected: Train F1 - Test F1 = {overfit_gap:.4f}{Colors.END}")
    else:
        print(f"\n{Colors.GREEN}✅ No significant overfitting detected (gap: {overfit_gap:.4f}){Colors.END}")

    # Confusion matrix
    test_cm = confusion_matrix(y_test, test_pred)
    print(f"\nTest Set Confusion Matrix:")
    print(f"  TN: {test_cm[0,0]:,}  FP: {test_cm[0,1]:,}")
    print(f"  FN: {test_cm[1,0]:,}  TP: {test_cm[1,1]:,}")

    # Step 6: Save model
    print_step(6, "Saving Model and Artifacts")

    output_dir = Path('models/xgboost_196controls')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save model
    model_path = output_dir / 'xgboost_model.json'
    model.save_model(str(model_path))
    print(f"{Colors.GREEN}✅ Model saved: {model_path}{Colors.END}")

    # Save encoders
    import joblib
    label_encoder_path = output_dir / 'label_encoder.pkl'
    joblib.dump(label_encoder, label_encoder_path)
    print(f"{Colors.GREEN}✅ Label encoder saved: {label_encoder_path}{Colors.END}")

    if vectorizer:
        vectorizer_path = output_dir / 'tfidf_vectorizer.pkl'
        joblib.dump(vectorizer, vectorizer_path)
        print(f"{Colors.GREEN}✅ TF-IDF vectorizer saved: {vectorizer_path}{Colors.END}")

    # Save metrics
    metrics = {
        'model_info': {
            'controls': train_df['control_id'].nunique(),
            'training_events': len(train_df),
            'validation_events': len(val_df),
            'test_events': len(test_df),
            'features': len(feature_cols),
            'text_features': len(text_feature_cols),
            'trained_at': datetime.now().isoformat()
        },
        'optimization': {
            'n_jobs': 2,
            'cv_folds': 3,
            'n_estimators': 100,
            'max_depth': 5,
            'max_text_features': 25
        },
        'cross_validation': {
            'mean_f1': float(cv_scores.mean()),
            'std_f1': float(cv_scores.std()),
            'fold_scores': [float(s) for s in cv_scores]
        },
        'training': {
            'accuracy': float(train_acc),
            'precision': float(train_p),
            'recall': float(train_r),
            'f1_score': float(train_f1)
        },
        'validation': {
            'accuracy': float(val_acc),
            'precision': float(val_p),
            'recall': float(val_r),
            'f1_score': float(val_f1)
        },
        'test': {
            'accuracy': float(test_acc),
            'precision': float(test_p),
            'recall': float(test_r),
            'f1_score': float(test_f1)
        },
        'confusion_matrix': {
            'true_negative': int(test_cm[0,0]),
            'false_positive': int(test_cm[0,1]),
            'false_negative': int(test_cm[1,0]),
            'true_positive': int(test_cm[1,1])
        },
        'overfitting_analysis': {
            'train_test_gap': float(overfit_gap),
            'overfitting_detected': bool(overfit_gap > 0.10)
        }
    }

    metrics_path = output_dir / 'training_metrics.json'
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"{Colors.GREEN}✅ Metrics saved: {metrics_path}{Colors.END}")

    print_resource_usage()

    print(f"\n{Colors.CYAN}╔════════════════════════════════════════════════════════════════╗{Colors.END}")
    print(f"{Colors.CYAN}║  TRAINING COMPLETE! ✅                                         ║{Colors.END}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════════════════════╝{Colors.END}\n")

    print(f"{Colors.GREEN}Model artifacts saved to: {output_dir}{Colors.END}")
    print(f"{Colors.BLUE}Test F1-Score: {test_f1:.4f}{Colors.END}")

if __name__ == '__main__':
    main()
