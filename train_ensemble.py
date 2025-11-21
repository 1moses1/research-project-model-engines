"""
Train Hybrid Ensemble Classifier

Trains BERT, XGBoost, and LSTM, then combines them using stacking or voting.
This script handles the full pipeline: train base models → combine into ensemble.

Author: Moise Iradukunda (CMU)
Date: October 2025
"""

import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score, confusion_matrix
import json

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.models.bert_classifier import BERTClassifier
from src.models.xgboost_classifier import XGBoostClassifier
from src.models.lstm_classifier import LSTMClassifier
from src.utils.logger import setup_logger

logger = setup_logger("ensemble_training", "logs/ensemble_training.log")


def load_data(data_dir: str):
    """Load training, validation, and test data"""
    logger.info(f"Loading data from: {data_dir}")

    train_df = pd.read_csv(f"{data_dir}/compliance_events_train.csv")
    val_df = pd.read_csv(f"{data_dir}/compliance_events_val.csv")
    test_df = pd.read_csv(f"{data_dir}/compliance_events_test.csv")

    logger.info(f"✅ Loaded train: {len(train_df)}, val: {len(val_df)}, test: {len(test_df)}")

    return train_df, val_df, test_df


def train_bert(train_df, val_df, epochs=3, batch_size=16):
    """Train BERT classifier"""
    logger.info("=" * 80)
    logger.info("TRAINING BERT")
    logger.info("=" * 80)

    bert = BERTClassifier(
        model_name='bert-base-uncased',
        max_length=128,
        freeze_layers=10
    )

    # Prepare data
    X_train = train_df['log_message'].values
    y_train = (train_df['compliance_status'] == 'non_compliant').astype(int).values

    X_val = val_df['log_message'].values
    y_val = (val_df['compliance_status'] == 'non_compliant').astype(int).values

    # Train
    bert.fit(X_train, y_train, X_val, y_val, epochs=epochs, batch_size=batch_size)

    logger.info("✅ BERT training complete")

    return bert


def train_xgboost(train_df, val_df):
    """Train XGBoost classifier"""
    logger.info("=" * 80)
    logger.info("TRAINING XGBOOST")
    logger.info("=" * 80)

    xgb = XGBoostClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.1
    )

    # Train
    xgb.fit(train_df, val_df)

    logger.info("✅ XGBoost training complete")

    return xgb


def train_lstm(train_df, val_df, epochs=5, batch_size=32):
    """Train LSTM classifier"""
    logger.info("=" * 80)
    logger.info("TRAINING LSTM")
    logger.info("=" * 80)

    lstm = LSTMClassifier(
        embedding_dim=100,
        hidden_dim=128,
        num_layers=2,
        max_length=100
    )

    # Prepare data
    X_train = train_df['log_message'].values
    y_train = (train_df['compliance_status'] == 'non_compliant').astype(int).values

    X_val = val_df['log_message'].values
    y_val = (val_df['compliance_status'] == 'non_compliant').astype(int).values

    # Train
    lstm.fit(X_train, y_train, X_val, y_val, epochs=epochs, batch_size=batch_size)

    logger.info("✅ LSTM training complete")

    return lstm


def get_base_predictions(models, df, return_proba=True):
    """Get predictions from all base models"""
    bert, xgb, lstm = models

    predictions = {}

    # BERT
    if return_proba:
        _, bert_proba = bert.predict(df['log_message'].values)
        predictions['bert'] = bert_proba[:, 1]
    else:
        bert_labels, _ = bert.predict(df['log_message'].values)
        predictions['bert'] = (np.array(bert_labels) == 'non_compliant').astype(int)

    # XGBoost
    if return_proba:
        _, xgb_proba = xgb.predict(df)
        predictions['xgboost'] = xgb_proba[:, 1]
    else:
        xgb_labels, _ = xgb.predict(df)
        predictions['xgboost'] = (np.array(xgb_labels) == 'non_compliant').astype(int)

    # LSTM
    if return_proba:
        _, lstm_proba = lstm.predict(df['log_message'].values)
        predictions['lstm'] = lstm_proba[:, 1]
    else:
        lstm_labels, _ = lstm.predict(df['log_message'].values)
        predictions['lstm'] = (np.array(lstm_labels) == 'non_compliant').astype(int)

    return predictions


def train_stacking_ensemble(models, val_df):
    """Train stacking meta-classifier"""
    logger.info("=" * 80)
    logger.info("TRAINING STACKING ENSEMBLE")
    logger.info("=" * 80)

    # Get base predictions on validation set
    val_preds = get_base_predictions(models, val_df, return_proba=True)

    # Stack as features
    X_meta = np.column_stack([
        val_preds['bert'],
        val_preds['xgboost'],
        val_preds['lstm']
    ])

    # True labels
    y_meta = (val_df['compliance_status'] == 'non_compliant').astype(int).values

    # Train logistic regression
    meta_clf = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
    meta_clf.fit(X_meta, y_meta)

    # Log coefficients
    logger.info("Meta-classifier coefficients:")
    logger.info(f"  BERT: {meta_clf.coef_[0][0]:.4f}")
    logger.info(f"  XGBoost: {meta_clf.coef_[0][1]:.4f}")
    logger.info(f"  LSTM: {meta_clf.coef_[0][2]:.4f}")
    logger.info(f"  Intercept: {meta_clf.intercept_[0]:.4f}")

    val_acc = meta_clf.score(X_meta, y_meta)
    logger.info(f"  Val accuracy: {val_acc:.4f}")

    logger.info("✅ Stacking ensemble trained")

    return meta_clf


def evaluate_ensemble(models, meta_clf, test_df, method='stacking'):
    """Evaluate ensemble on test set"""
    logger.info("=" * 80)
    logger.info(f"EVALUATING {method.upper()} ENSEMBLE")
    logger.info("=" * 80)

    # Get base predictions
    test_preds = get_base_predictions(models, test_df, return_proba=True)

    # True labels
    y_true = (test_df['compliance_status'] == 'non_compliant').astype(int).values

    if method == 'stacking':
        # Stack and predict
        X_meta = np.column_stack([
            test_preds['bert'],
            test_preds['xgboost'],
            test_preds['lstm']
        ])

        y_pred = meta_clf.predict(X_meta)
        y_proba = meta_clf.predict_proba(X_meta)

    elif method == 'voting_soft':
        # Weighted average (BERT=40%, XGB=40%, LSTM=20%)
        y_proba_nc = 0.4 * test_preds['bert'] + 0.4 * test_preds['xgboost'] + 0.2 * test_preds['lstm']
        y_pred = (y_proba_nc > 0.5).astype(int)
        y_proba = np.column_stack([1 - y_proba_nc, y_proba_nc])

    elif method == 'voting_hard':
        # Majority vote
        bert_hard = (test_preds['bert'] > 0.5).astype(int)
        xgb_hard = (test_preds['xgboost'] > 0.5).astype(int)
        lstm_hard = (test_preds['lstm'] > 0.5).astype(int)

        votes = bert_hard + xgb_hard + lstm_hard
        y_pred = (votes >= 2).astype(int)  # 2 out of 3
        y_proba_nc = votes / 3.0
        y_proba = np.column_stack([1 - y_proba_nc, y_proba_nc])

    # Calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
    roc_auc = roc_auc_score(y_true, y_proba[:, 1])

    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    results = {
        'method': method,
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'roc_auc': float(roc_auc),
        'error_rate': float(1 - accuracy),
        'confusion_matrix': {
            'tn': int(tn),
            'fp': int(fp),
            'fn': int(fn),
            'tp': int(tp)
        }
    }

    logger.info(f"✅ {method.upper()} Ensemble Results:")
    logger.info(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    logger.info(f"  Precision: {precision:.4f}")
    logger.info(f"  Recall: {recall:.4f}")
    logger.info(f"  F1 Score: {f1:.4f}")
    logger.info(f"  ROC-AUC: {roc_auc:.4f}")
    logger.info(f"  Confusion Matrix: TN={tn}, FP={fp}, FN={fn}, TP={tp}")

    return results


def compare_all_models(models, meta_clf, test_df):
    """Compare ensemble with base models"""
    logger.info("=" * 80)
    logger.info("COMPREHENSIVE MODEL COMPARISON")
    logger.info("=" * 80)

    bert, xgb, lstm = models
    y_true = (test_df['compliance_status'] == 'non_compliant').astype(int).values

    results = []

    # Base models
    for model_name, model in [('BERT', bert), ('XGBoost', xgb), ('LSTM', lstm)]:
        if model_name in ['BERT', 'LSTM']:
            pred_labels, pred_proba = model.predict(test_df['log_message'].values)
        else:
            pred_labels, pred_proba = model.predict(test_df)

        y_pred = (np.array(pred_labels) == 'non_compliant').astype(int)

        acc = accuracy_score(y_true, y_pred)
        prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)
        auc = roc_auc_score(y_true, pred_proba[:, 1])

        results.append({
            'Model': model_name,
            'Accuracy': f"{acc:.4f}",
            'Precision': f"{prec:.4f}",
            'Recall': f"{rec:.4f}",
            'F1 Score': f"{f1:.4f}",
            'ROC-AUC': f"{auc:.4f}"
        })

    # Ensemble results
    ensemble_results = evaluate_ensemble(models, meta_clf, test_df, method='stacking')

    results.append({
        'Model': 'Ensemble (Stacking)',
        'Accuracy': f"{ensemble_results['accuracy']:.4f}",
        'Precision': f"{ensemble_results['precision']:.4f}",
        'Recall': f"{ensemble_results['recall']:.4f}",
        'F1 Score': f"{ensemble_results['f1_score']:.4f}",
        'ROC-AUC': f"{ensemble_results['roc_auc']:.4f}"
    })

    # Print comparison
    df_comparison = pd.DataFrame(results)
    logger.info("\n" + df_comparison.to_string(index=False))

    # Save comparison
    Path("results/ensemble").mkdir(parents=True, exist_ok=True)
    df_comparison.to_csv("results/ensemble/model_comparison.csv", index=False)

    # Save ensemble metrics
    with open("results/ensemble/ensemble_metrics.json", 'w') as f:
        json.dump(ensemble_results, f, indent=2)

    logger.info("\n✅ Comparison saved to results/ensemble/")

    return df_comparison, ensemble_results


def main():
    """Main training pipeline"""
    import argparse

    parser = argparse.ArgumentParser(description='Train hybrid ensemble')
    parser.add_argument('--data-dir', type=str, default='data/real_formatted')
    parser.add_argument('--bert-epochs', type=int, default=3)
    parser.add_argument('--lstm-epochs', type=int, default=5)
    parser.add_argument('--skip-base-training', action='store_true',
                       help='Skip training base models (load from previous run)')

    args = parser.parse_args()

    # Load data
    train_df, val_df, test_df = load_data(args.data_dir)

    if not args.skip_base_training:
        # Train base models
        logger.info("\n" + "=" * 80)
        logger.info("PHASE 1: TRAINING BASE MODELS")
        logger.info("=" * 80 + "\n")

        bert = train_bert(train_df, val_df, epochs=args.bert_epochs)
        xgb = train_xgboost(train_df, val_df)
        lstm = train_lstm(train_df, val_df, epochs=args.lstm_epochs)

        models = (bert, xgb, lstm)

        logger.info("\n✅ All base models trained successfully")
    else:
        logger.info("⏭️  Skipping base model training (not implemented yet)")
        return

    # Train ensemble
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 2: TRAINING ENSEMBLE")
    logger.info("=" * 80 + "\n")

    meta_clf = train_stacking_ensemble(models, val_df)

    # Evaluate and compare
    logger.info("\n" + "=" * 80)
    logger.info("PHASE 3: EVALUATION & COMPARISON")
    logger.info("=" * 80 + "\n")

    comparison, ensemble_results = compare_all_models(models, meta_clf, test_df)

    # Final summary
    logger.info("\n" + "=" * 80)
    logger.info("ENSEMBLE TRAINING COMPLETE!")
    logger.info("=" * 80)
    logger.info(f"✅ Ensemble Accuracy: {ensemble_results['accuracy']:.4f} ({ensemble_results['accuracy']*100:.2f}%)")
    logger.info(f"✅ Ensemble F1 Score: {ensemble_results['f1_score']:.4f}")
    logger.info(f"✅ Ensemble ROC-AUC: {ensemble_results['roc_auc']:.4f}")
    logger.info(f"\n📊 Results saved to: results/ensemble/")
    logger.info("=" * 80 + "\n")


if __name__ == "__main__":
    main()
