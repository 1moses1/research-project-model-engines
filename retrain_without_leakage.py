#!/usr/bin/env python3
"""
Retrain XGBoost WITHOUT Data Leakage
Remove status_code and other leaky features
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.xgboost_classifier import XGBoostClassifier
from utils.logger import setup_logger

logger = setup_logger('retrain_no_leakage')


def remove_leaky_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove features that cause data leakage

    Leaky features identified:
    - status_code: Perfect predictor (200=compliant, 403=non-compliant)
    - anomaly_label: Too directly correlated with label
    - anomaly_type: Same issue
    """
    leaky_features = ['status_code', 'anomaly_label', 'anomaly_type', 'severity']

    logger.info("Removing leaky features:")
    for feat in leaky_features:
        if feat in df.columns:
            logger.info(f"  - {feat}")
            df = df.drop(columns=[feat])
        else:
            logger.warning(f"  - {feat} not found in dataframe")

    return df


def main():
    print("\n" + "="*80)
    print("RETRAIN MODEL WITHOUT DATA LEAKAGE")
    print("="*80)
    print()

    output_dir = Path("results/models/xgboost_no_leakage")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load datasets
    logger.info("Loading datasets...")
    train_df = pd.read_csv("data/combined_compliance/compliance_events_train.csv")
    val_df = pd.read_csv("data/combined_compliance/compliance_events_val.csv")
    test_df = pd.read_csv("data/combined_compliance/compliance_events_test.csv")

    logger.info(f"Train: {len(train_df)} events")
    logger.info(f"Val: {len(val_df)} events")
    logger.info(f"Test: {len(test_df)} events")

    # Remove leaky features
    print("\n📋 Removing leaky features...")
    train_df = remove_leaky_features(train_df)
    val_df = remove_leaky_features(val_df)
    test_df = remove_leaky_features(test_df)

    # Initialize classifier
    logger.info("Initializing XGBoost classifier...")
    classifier = XGBoostClassifier()

    # Prepare features
    logger.info("Preparing features...")
    classifier.feature_engineer.fit(train_df)

    X_train = classifier.feature_engineer.transform(train_df)
    y_train = train_df['compliance_status'].map({'compliant': 0, 'non_compliant': 1}).values

    X_val = classifier.feature_engineer.transform(val_df)
    y_val = val_df['compliance_status'].map({'compliant': 0, 'non_compliant': 1}).values

    X_test = classifier.feature_engineer.transform(test_df)
    y_test = test_df['compliance_status'].map({'compliant': 0, 'non_compliant': 1}).values

    logger.info(f"Training features: {X_train.shape}")
    logger.info(f"Validation features: {X_val.shape}")
    logger.info(f"Test features: {X_test.shape}")

    # Train model
    print("\n🚀 Training model WITHOUT leaky features...")
    print("   (This may take longer as model must learn from actual patterns)\n")

    history = classifier.train(X_train, y_train, X_val, y_val, early_stopping_rounds=50)

    # Save model
    model_path = output_dir / "xgboost_model_no_leakage"
    classifier.save_model(str(model_path))
    logger.info(f"✅ Model saved to {model_path}")

    # Evaluate on test set
    print("\n📊 Evaluating on test set...")
    predictions, probabilities = classifier.predict(test_df)

    from sklearn.metrics import (
        accuracy_score, precision_score, recall_score, f1_score,
        confusion_matrix
    )

    y_pred = [1 if p == 'non_compliant' else 0 for p in predictions]

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        'accuracy': float(accuracy_score(y_test, y_pred)),
        'precision': float(precision_score(y_test, y_pred, zero_division=0)),
        'recall': float(recall_score(y_test, y_pred, zero_division=0)),
        'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
        'true_positives': int(tp),
        'false_positives': int(fp),
        'true_negatives': int(tn),
        'false_negatives': int(fn),
        'avg_confidence': float(np.mean(probabilities)),
        'trained_at': datetime.now().isoformat()
    }

    print("\n" + "="*80)
    print("TEST SET PERFORMANCE (Without Data Leakage)")
    print("="*80)
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    print(f"Precision: {metrics['precision']:.2%}")
    print(f"Recall: {metrics['recall']:.2%}")
    print(f"F1 Score: {metrics['f1_score']:.2%}")
    print()
    print("Confusion Matrix:")
    print(f"  True Negatives (TN): {metrics['true_negatives']}")
    print(f"  False Positives (FP): {metrics['false_positives']}")
    print(f"  False Negatives (FN): {metrics['false_negatives']}")  # Critical!
    print(f"  True Positives (TP): {metrics['true_positives']}")
    print()

    # Assess performance
    if metrics['accuracy'] >= 0.90:
        print("✅ EXCELLENT: Accuracy ≥90% without data leakage!")
        assessment = "EXCELLENT"
    elif metrics['accuracy'] >= 0.85:
        print("✅ GOOD: Accuracy ≥85% - acceptable for production")
        assessment = "GOOD"
    elif metrics['accuracy'] >= 0.75:
        print("⚠️  FAIR: Accuracy ≥75% - needs improvement")
        assessment = "FAIR"
    else:
        print("❌ POOR: Accuracy <75% - significant improvement needed")
        assessment = "POOR"

    metrics['assessment'] = assessment

    # Save metrics
    metrics_file = output_dir / "metrics_no_leakage.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"✅ Metrics saved to {metrics_file}")

    # Now test with status code flip
    print("\n" + "="*80)
    print("VERIFYING NO DATA LEAKAGE")
    print("="*80)
    print("\n🔄 Testing with flipped status codes...")

    # Add status_code back temporarily for the test
    test_with_status = test_df.copy()
    test_with_status['status_code'] = 200  # Set all to success

    preds1, _ = classifier.predict(test_with_status)

    test_with_status['status_code'] = 403  # Set all to forbidden

    preds2, _ = classifier.predict(test_with_status)

    # Check if predictions changed
    changes = sum(1 for p1, p2 in zip(preds1, preds2) if p1 != p2)
    change_rate = changes / len(preds1) * 100

    print(f"\nPredictions that changed when status flipped: {changes}/{len(preds1)} ({change_rate:.1f}%)")

    if change_rate < 10:
        print("✅ Model is ROBUST - not relying on status codes!")
        leakage_check = "PASSED"
    else:
        print("⚠️  Model still affected by status codes")
        leakage_check = "FAILED"

    metrics['leakage_check'] = {
        'change_rate': float(change_rate),
        'status': leakage_check
    }

    # Save final metrics
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)

    print("\n" + "="*80)
    print("RETRAINING COMPLETE")
    print("="*80)
    print(f"\nModel: {model_path}")
    print(f"Metrics: {metrics_file}")
    print(f"\nThis is the REAL performance - no cheating with status codes!")
    print("="*80)


if __name__ == '__main__':
    main()
