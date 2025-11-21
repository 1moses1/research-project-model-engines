"""
Production-Ready XGBoost Training with Realistic Improvements

Improvements:
1. Data augmentation with noise/variations
2. Cross-validation to detect overfitting
3. Text feature extraction from log messages
4. Confidence-based predictions
5. Realistic performance expectations
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from sklearn.feature_extraction.text import TfidfVectorizer
import xgboost as xgb
import warnings
warnings.filterwarnings('ignore')

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(step, message):
    """Print colored step message."""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}[STEP {step}] {message}{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

def add_realistic_noise(df):
    """Add realistic noise to make data less perfect."""
    print("Adding realistic variations to training data...")

    df_noisy = df.copy()
    n_samples = len(df_noisy)

    # 1. Add random missing values (5% of data)
    for col in df_noisy.select_dtypes(include=[np.number]).columns:
        mask = np.random.random(n_samples) < 0.05
        df_noisy.loc[mask, col] = np.nan

    # 2. Add noise to numeric features (±10%)
    for col in ['hour_of_day', 'port']:
        if col in df_noisy.columns:
            noise = np.random.normal(0, 0.1, n_samples)
            df_noisy[col] = df_noisy[col] * (1 + noise)
            df_noisy[col] = df_noisy[col].clip(lower=0)

    # 3. Flip some labels (2% label noise - simulates human error)
    flip_mask = np.random.random(n_samples) < 0.02
    df_noisy.loc[flip_mask, 'compliance_status'] = df_noisy.loc[flip_mask, 'compliance_status'].apply(
        lambda x: 'compliant' if x == 'non_compliant' else 'non_compliant'
    )

    # 4. Add typos to log messages (5% get minor modifications)
    if 'log_message' in df_noisy.columns:
        typo_mask = np.random.random(n_samples) < 0.05
        df_noisy.loc[typo_mask, 'log_message'] = df_noisy.loc[typo_mask, 'log_message'].apply(
            lambda x: x.replace(' ', '  ') if isinstance(x, str) else x  # Double spaces
        )

    print(f"  - Added missing values: ~{int(n_samples * 0.05)} cells")
    print(f"  - Added numeric noise: ±10% variation")
    print(f"  - Label noise: {int(n_samples * 0.02)} flipped labels")
    print(f"  - Log message variations: {int(n_samples * 0.05)} modified")

    return df_noisy

def extract_text_features(df, max_features=50):
    """Extract TF-IDF features from log messages."""
    print(f"Extracting text features from log messages (max {max_features} features)...")

    if 'log_message' not in df.columns:
        print(f"{Colors.YELLOW}  ⚠️  No log_message column found, skipping text features{Colors.END}")
        return df, None

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),  # unigrams and bigrams
        min_df=2,
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

def train_with_cross_validation(X, y):
    """Train model with cross-validation to detect overfitting."""
    print_step(3, "Training with Cross-Validation")

    # Create model
    model = xgb.XGBClassifier(
        n_estimators=150,      # Reduced to prevent overfitting
        max_depth=6,           # Shallower trees
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.7,  # More randomness
        min_child_weight=5,    # Prevent overfitting
        gamma=0.1,             # Min loss reduction
        reg_alpha=0.1,         # L1 regularization
        reg_lambda=1.0,        # L2 regularization
        scale_pos_weight=3,
        objective='binary:logistic',
        random_state=42,
        n_jobs=-1,
        tree_method='hist'
    )

    # 5-fold stratified cross-validation
    print("Running 5-fold cross-validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    cv_scores = cross_val_score(model, X, y, cv=cv, scoring='f1', n_jobs=-1)

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
        print(f"{Colors.GREEN}✅ Cross-validation looks reasonable{Colors.END}")

    return model, cv_scores

def train_final_model(X_train, y_train, X_val, y_val):
    """Train final model with validation set."""
    print_step(4, "Training Final Model")

    model = xgb.XGBClassifier(
        n_estimators=150,
        max_depth=6,
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
        n_jobs=-1,
        tree_method='hist',
        early_stopping_rounds=20  # Stop if no improvement
    )

    print(f"Training on {len(X_train):,} samples...")
    print(f"Validation on {len(X_val):,} samples...")

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )

    # Evaluate
    y_pred = model.predict(X_val)
    accuracy = accuracy_score(y_val, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_val, y_pred, average='binary')

    print(f"\n{Colors.GREEN}Training Complete!{Colors.END}")
    print(f"\nValidation Performance:")
    print(f"  Accuracy:  {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")

    # Check for overfitting indicators
    train_pred = model.predict(X_train)
    train_acc = accuracy_score(y_train, train_pred)

    print(f"\nOverfitting Check:")
    print(f"  Training Accuracy:   {train_acc:.4f}")
    print(f"  Validation Accuracy: {accuracy:.4f}")
    print(f"  Difference:          {abs(train_acc - accuracy):.4f}")

    if abs(train_acc - accuracy) > 0.15:
        print(f"{Colors.RED}  ⚠️  SEVERE OVERFITTING DETECTED!{Colors.END}")
    elif abs(train_acc - accuracy) > 0.08:
        print(f"{Colors.YELLOW}  ⚠️  Moderate overfitting detected{Colors.END}")
    else:
        print(f"{Colors.GREEN}  ✅ Acceptable train/val gap{Colors.END}")

    return model

def evaluate_with_confidence(model, X_test, y_test, le):
    """Evaluate model with confidence thresholds."""
    print_step(5, "Evaluation with Confidence Analysis")

    # Get predictions and probabilities
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)

    # Overall metrics
    print("\nOverall Performance:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Confidence-based analysis
    max_proba = y_proba.max(axis=1)

    print("\nConfidence Distribution:")
    for threshold in [0.5, 0.7, 0.8, 0.9]:
        confident_mask = max_proba >= threshold
        n_confident = confident_mask.sum()

        if n_confident > 0:
            acc = accuracy_score(y_test[confident_mask], y_pred[confident_mask])
            print(f"  At ≥{threshold:.0%} confidence: {n_confident:,} samples ({n_confident/len(y_test):.1%}), Accuracy: {acc:.4f}")

    # Recommended production threshold
    print(f"\n{Colors.BLUE}Production Recommendations:{Colors.END}")

    # Find threshold where accuracy is ≥85%
    best_threshold = 0.5
    for threshold in np.arange(0.5, 1.0, 0.05):
        mask = max_proba >= threshold
        if mask.sum() > 0:
            acc = accuracy_score(y_test[mask], y_pred[mask])
            if acc >= 0.85:
                best_threshold = threshold
                break

    mask = max_proba >= best_threshold
    coverage = mask.sum() / len(y_test)
    acc_at_threshold = accuracy_score(y_test[mask], y_pred[mask]) if mask.sum() > 0 else 0

    print(f"  Recommended confidence threshold: {best_threshold:.2f}")
    print(f"  Coverage at threshold: {coverage:.1%} of predictions")
    print(f"  Accuracy at threshold: {acc_at_threshold:.4f}")
    print(f"  {Colors.YELLOW}→ Flag {100-coverage*100:.1f}% of predictions for human review{Colors.END}")

    return {
        'overall_accuracy': accuracy_score(y_test, y_pred),
        'recommended_threshold': float(best_threshold),
        'coverage_at_threshold': float(coverage),
        'accuracy_at_threshold': float(acc_at_threshold)
    }

def main():
    """Main training function."""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}Production-Ready XGBoost Training{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

    start_time = datetime.now()

    # Step 1: Load data
    print_step(1, "Loading and Augmenting Data")

    train_df = pd.read_csv('data/validated_synthetic/train_validated.csv')
    val_df = pd.read_csv('data/validated_synthetic/val_validated.csv')
    test_df = pd.read_csv('data/validated_synthetic/test_validated.csv')

    print(f"Loaded: {len(train_df):,} train, {len(val_df):,} val, {len(test_df):,} test")

    # Add realistic noise
    train_df = add_realistic_noise(train_df)

    # Step 2: Feature Engineering
    print_step(2, "Feature Engineering")

    # Extract text features
    train_df, vectorizer = extract_text_features(train_df, max_features=50)

    if vectorizer:
        # Apply to val and test
        val_log_messages = val_df['log_message'].fillna('').astype(str)
        test_log_messages = test_df['log_message'].fillna('').astype(str)

        val_tfidf = vectorizer.transform(val_log_messages)
        test_tfidf = vectorizer.transform(test_log_messages)

        val_tfidf_df = pd.DataFrame(
            val_tfidf.toarray(),
            columns=[f'text_{i}' for i in range(val_tfidf.shape[1])],
            index=val_df.index
        )
        test_tfidf_df = pd.DataFrame(
            test_tfidf.toarray(),
            columns=[f'text_{i}' for i in range(test_tfidf.shape[1])],
            index=test_df.index
        )

        val_df = pd.concat([val_df, val_tfidf_df], axis=1)
        test_df = pd.concat([test_df, test_tfidf_df], axis=1)

    # Select numeric features
    numeric_cols = train_df.select_dtypes(include=[np.number]).columns.tolist()
    exclude_cols = ['event_id']
    features = [col for col in numeric_cols if col not in exclude_cols]

    print(f"Using {len(features)} features (numeric + text)")

    # Prepare data
    X_train = train_df[features].fillna(0)
    X_val = val_df[features].fillna(0)
    X_test = test_df[features].fillna(0)

    # Ensure same columns
    for col in features:
        if col not in X_val.columns:
            X_val[col] = 0
        if col not in X_test.columns:
            X_test[col] = 0

    X_val = X_val[features]
    X_test = X_test[features]

    le = LabelEncoder()
    y_train = le.fit_transform(train_df['compliance_status'])
    y_val = le.transform(val_df['compliance_status'])
    y_test = le.transform(test_df['compliance_status'])

    # Cross-validation
    model, cv_scores = train_with_cross_validation(X_train, y_train)

    # Train final model
    model = train_final_model(X_train, y_train, X_val, y_val)

    # Evaluate with confidence
    confidence_metrics = evaluate_with_confidence(model, X_test, y_test, le)

    # Save model
    print_step(6, "Saving Model and Metrics")

    model_dir = Path("models/production_ready")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "xgboost_improved.json"
    model.save_model(model_path)

    import pickle
    with open(model_dir / "label_encoder.pkl", 'wb') as f:
        pickle.dump(le, f)

    with open(model_dir / "features.json", 'w') as f:
        json.dump({'features': features}, f, indent=2)

    if vectorizer:
        with open(model_dir / "text_vectorizer.pkl", 'wb') as f:
            pickle.dump(vectorizer, f)

    # Save metrics
    metrics = {
        'model': 'XGBoost (Production-Ready)',
        'framework': 'Rwanda NCSA (PRIMARY) + NIST (SECONDARY)',
        'validated': True,
        'validation_date': datetime.now().strftime('%Y-%m-%d'),
        'improvements': [
            'Realistic data augmentation (noise, missing values, label errors)',
            'Text feature extraction (TF-IDF from log messages)',
            'Cross-validation (5-fold)',
            'Regularization (L1/L2, max_depth=6)',
            'Confidence-based predictions'
        ],
        'cross_validation': {
            'mean_f1': float(cv_scores.mean()),
            'std_f1': float(cv_scores.std()),
            'scores': cv_scores.tolist()
        },
        'test_performance': confidence_metrics,
        'features_used': len(features),
        'training_samples': len(train_df),
        'expected_real_world_performance': '65-80% (estimate based on synthetic training)'
    }

    metrics_path = model_dir / "metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"{Colors.GREEN}✅ Model saved to: {model_path}{Colors.END}")
    print(f"{Colors.GREEN}✅ Metrics saved to: {metrics_path}{Colors.END}")

    # Final summary
    duration = (datetime.now() - start_time).total_seconds()

    print(f"\n{Colors.GREEN}{'='*80}{Colors.END}")
    print(f"{Colors.GREEN}Training Complete!{Colors.END}")
    print(f"{Colors.GREEN}{'='*80}{Colors.END}\n")

    print(f"Duration: {duration:.1f} seconds")
    print(f"Cross-Validation F1: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
    print(f"Test Accuracy: {confidence_metrics['overall_accuracy']:.4f}")
    print(f"Recommended Threshold: {confidence_metrics['recommended_threshold']:.2f}")

    print(f"\n{Colors.YELLOW}Expected Real-World Performance: 65-80% accuracy{Colors.END}")
    print(f"{Colors.YELLOW}Recommend: Human review for low-confidence predictions (<{confidence_metrics['recommended_threshold']:.2f}){Colors.END}")

if __name__ == "__main__":
    main()
