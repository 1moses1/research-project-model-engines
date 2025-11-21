"""
Hybrid Ensemble Classifier for Compliance Auditing

Combines BERT and XGBoost predictions using stacking meta-classifier
for improved accuracy and robustness.

Architecture:
    Level 0 (Base Models):
        - BERT: Deep learning (transformer-based text understanding)
        - XGBoost: Gradient boosting (structured feature patterns)
        - LSTM: Recurrent neural network (sequential dependencies)

    Level 1 (Meta-Classifier):
        - Logistic Regression: Learns optimal combination of base predictions
        - Or: Simple Voting (majority vote)

Expected Performance: 96-99% accuracy

Author: Moise Iradukunda (CMU)
Date: October 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import joblib
import json
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score

import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import setup_logger
from models.bert_classifier import BERTClassifier
from models.xgboost_classifier import XGBoostClassifier
from models.lstm_classifier import LSTMClassifier


class EnsembleClassifier:
    """
    Hybrid ensemble combining BERT, XGBoost, and LSTM.

    Supports two ensemble strategies:
    1. Stacking: Meta-classifier learns to combine base model predictions
    2. Voting: Simple majority vote or weighted average
    """

    def __init__(
        self,
        ensemble_method: str = 'stacking',
        voting_strategy: str = 'soft',
        weights: Optional[List[float]] = None,
        use_lstm: bool = True
    ):
        """
        Initialize ensemble classifier.

        Args:
            ensemble_method: 'stacking' or 'voting'
            voting_strategy: 'hard' (majority) or 'soft' (probability averaging)
            weights: Model weights for voting [bert_weight, xgb_weight, lstm_weight]
            use_lstm: Whether to include LSTM in ensemble
        """
        self.ensemble_method = ensemble_method
        self.voting_strategy = voting_strategy
        self.weights = weights or [0.4, 0.4, 0.2]  # Default: BERT=40%, XGBoost=40%, LSTM=20%
        self.use_lstm = use_lstm

        # Base models
        self.bert_model = None
        self.xgboost_model = None
        self.lstm_model = None

        # Meta-classifier
        self.meta_classifier = None

        self.is_fitted = False

        self.logger = setup_logger("ensemble", "logs/ensemble.log")

        self.logger.info("Ensemble classifier initialized:")
        self.logger.info(f"  Method: {ensemble_method}")
        self.logger.info(f"  Voting strategy: {voting_strategy}")
        self.logger.info(f"  Weights: {self.weights}")
        self.logger.info(f"  Use LSTM: {use_lstm}")

    def load_base_models(
        self,
        bert_path: str,
        xgboost_path: str,
        lstm_path: Optional[str] = None
    ):
        """
        Load pre-trained base models.

        Args:
            bert_path: Path to BERT model directory
            xgboost_path: Path to XGBoost model file
            lstm_path: Path to LSTM model directory (optional)
        """
        self.logger.info("Loading base models...")

        # Load BERT
        self.logger.info(f"Loading BERT from: {bert_path}")
        self.bert_model = BERTClassifier()
        self.bert_model.load_model(bert_path)
        self.logger.info("✅ BERT loaded")

        # Load XGBoost
        self.logger.info(f"Loading XGBoost from: {xgboost_path}")
        self.xgboost_model = XGBoostClassifier()
        self.xgboost_model.load_model(xgboost_path)
        self.logger.info("✅ XGBoost loaded")

        # Load LSTM (optional)
        if self.use_lstm and lstm_path:
            self.logger.info(f"Loading LSTM from: {lstm_path}")
            self.lstm_model = LSTMClassifier()
            self.lstm_model.load_model(lstm_path)
            self.logger.info("✅ LSTM loaded")

        self.logger.info("All base models loaded successfully")

    def get_base_predictions(
        self,
        df: pd.DataFrame,
        return_proba: bool = True
    ) -> Dict[str, np.ndarray]:
        """
        Get predictions from all base models.

        Args:
            df: Input DataFrame with log_message and metadata
            return_proba: Return probabilities instead of hard labels

        Returns:
            Dictionary with model predictions
        """
        predictions = {}

        # BERT predictions
        if return_proba:
            _, bert_proba = self.bert_model.predict(df['log_message'].values)
            predictions['bert'] = bert_proba[:, 1]  # Probability of non-compliant
        else:
            bert_labels, _ = self.bert_model.predict(df['log_message'].values)
            predictions['bert'] = (np.array(bert_labels) == 'non_compliant').astype(int)

        # XGBoost predictions
        if return_proba:
            _, xgb_proba = self.xgboost_model.predict(df)
            predictions['xgboost'] = xgb_proba[:, 1]
        else:
            xgb_labels, _ = self.xgboost_model.predict(df)
            predictions['xgboost'] = (np.array(xgb_labels) == 'non_compliant').astype(int)

        # LSTM predictions
        if self.use_lstm and self.lstm_model:
            if return_proba:
                _, lstm_proba = self.lstm_model.predict(df['log_message'].values)
                predictions['lstm'] = lstm_proba[:, 1]
            else:
                lstm_labels, _ = self.lstm_model.predict(df['log_message'].values)
                predictions['lstm'] = (np.array(lstm_labels) == 'non_compliant').astype(int)

        return predictions

    def fit_meta_classifier(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame
    ):
        """
        Fit meta-classifier on validation set using base model predictions.

        Args:
            train_df: Training DataFrame (used to get base predictions)
            val_df: Validation DataFrame (used to train meta-classifier)
        """
        if self.ensemble_method != 'stacking':
            self.logger.info("Voting ensemble - no meta-classifier needed")
            self.is_fitted = True
            return

        self.logger.info("Training meta-classifier...")

        # Get base model predictions on validation set
        val_predictions = self.get_base_predictions(val_df, return_proba=True)

        # Stack predictions as features
        if self.use_lstm and 'lstm' in val_predictions:
            X_meta = np.column_stack([
                val_predictions['bert'],
                val_predictions['xgboost'],
                val_predictions['lstm']
            ])
        else:
            X_meta = np.column_stack([
                val_predictions['bert'],
                val_predictions['xgboost']
            ])

        # True labels
        y_meta = (val_df['compliance_status'] == 'non_compliant').astype(int).values

        # Train logistic regression meta-classifier
        self.meta_classifier = LogisticRegression(
            max_iter=1000,
            random_state=42,
            class_weight='balanced'
        )

        self.meta_classifier.fit(X_meta, y_meta)

        # Log meta-classifier weights
        self.logger.info("Meta-classifier trained:")
        self.logger.info(f"  Coefficients: {self.meta_classifier.coef_[0]}")
        self.logger.info(f"  Intercept: {self.meta_classifier.intercept_[0]}")

        # Validate on training set
        train_predictions = self.get_base_predictions(train_df, return_proba=True)
        if self.use_lstm and 'lstm' in train_predictions:
            X_train_meta = np.column_stack([
                train_predictions['bert'],
                train_predictions['xgboost'],
                train_predictions['lstm']
            ])
        else:
            X_train_meta = np.column_stack([
                train_predictions['bert'],
                train_predictions['xgboost']
            ])

        y_train_meta = (train_df['compliance_status'] == 'non_compliant').astype(int).values

        train_acc = self.meta_classifier.score(X_train_meta, y_train_meta)
        val_acc = self.meta_classifier.score(X_meta, y_meta)

        self.logger.info(f"  Train accuracy: {train_acc:.4f}")
        self.logger.info(f"  Val accuracy: {val_acc:.4f}")

        self.is_fitted = True

    def predict(
        self,
        df: pd.DataFrame,
        return_proba: bool = False
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Make ensemble predictions.

        Args:
            df: Input DataFrame
            return_proba: Return probabilities

        Returns:
            Tuple of (labels, probabilities)
        """
        if not self.is_fitted:
            raise ValueError("Ensemble not fitted. Call load_base_models() and fit_meta_classifier() first")

        # Get base predictions
        base_predictions = self.get_base_predictions(df, return_proba=True)

        if self.ensemble_method == 'stacking':
            # Stack predictions
            if self.use_lstm and 'lstm' in base_predictions:
                X_meta = np.column_stack([
                    base_predictions['bert'],
                    base_predictions['xgboost'],
                    base_predictions['lstm']
                ])
            else:
                X_meta = np.column_stack([
                    base_predictions['bert'],
                    base_predictions['xgboost']
                ])

            # Meta-classifier prediction
            y_proba = self.meta_classifier.predict_proba(X_meta)
            y_pred = self.meta_classifier.predict(X_meta)

        else:  # voting
            if self.voting_strategy == 'soft':
                # Weighted average of probabilities
                if self.use_lstm and 'lstm' in base_predictions:
                    y_proba_noncompliant = (
                        self.weights[0] * base_predictions['bert'] +
                        self.weights[1] * base_predictions['xgboost'] +
                        self.weights[2] * base_predictions['lstm']
                    )
                else:
                    # Normalize weights without LSTM
                    w_bert = self.weights[0] / (self.weights[0] + self.weights[1])
                    w_xgb = self.weights[1] / (self.weights[0] + self.weights[1])
                    y_proba_noncompliant = (
                        w_bert * base_predictions['bert'] +
                        w_xgb * base_predictions['xgboost']
                    )

                y_proba_compliant = 1 - y_proba_noncompliant
                y_proba = np.column_stack([y_proba_compliant, y_proba_noncompliant])
                y_pred = (y_proba_noncompliant > 0.5).astype(int)

            else:  # hard voting
                # Get hard predictions
                hard_preds = self.get_base_predictions(df, return_proba=False)

                if self.use_lstm and 'lstm' in hard_preds:
                    # Majority vote
                    votes = np.column_stack([
                        hard_preds['bert'],
                        hard_preds['xgboost'],
                        hard_preds['lstm']
                    ])
                    y_pred = (votes.sum(axis=1) >= 2).astype(int)  # 2 out of 3
                else:
                    # Average of two models
                    y_pred = ((hard_preds['bert'] + hard_preds['xgboost']) >= 1).astype(int)

                # Approximate probabilities from hard votes
                y_proba_noncompliant = y_pred.astype(float)
                y_proba = np.column_stack([1 - y_proba_noncompliant, y_proba_noncompliant])

        # Convert to labels
        label_map = {0: 'compliant', 1: 'non_compliant'}
        y_labels = np.array([label_map[pred] for pred in y_pred])

        if return_proba:
            return y_labels, y_proba
        else:
            return y_labels, y_proba

    def evaluate(
        self,
        test_df: pd.DataFrame,
        return_predictions: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate ensemble on test set.

        Args:
            test_df: Test DataFrame
            return_predictions: Return predictions along with metrics

        Returns:
            Dictionary with evaluation metrics
        """
        self.logger.info("Evaluating ensemble...")

        # Get predictions
        y_pred, y_proba = self.predict(test_df, return_proba=True)

        # True labels
        y_true = (test_df['compliance_status'] == 'non_compliant').astype(int).values
        y_pred_binary = (y_pred == 'non_compliant').astype(int)

        # Calculate metrics
        accuracy = accuracy_score(y_true, y_pred_binary)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_true, y_pred_binary, average='binary', zero_division=0
        )
        roc_auc = roc_auc_score(y_true, y_proba[:, 1])

        # Confusion matrix
        tn = np.sum((y_true == 0) & (y_pred_binary == 0))
        fp = np.sum((y_true == 0) & (y_pred_binary == 1))
        fn = np.sum((y_true == 1) & (y_pred_binary == 0))
        tp = np.sum((y_true == 1) & (y_pred_binary == 1))

        results = {
            'model_name': 'Ensemble',
            'ensemble_method': self.ensemble_method,
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

        self.logger.info("Ensemble Evaluation Results:")
        self.logger.info(f"  Method: {self.ensemble_method}")
        self.logger.info(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        self.logger.info(f"  Precision: {precision:.4f}")
        self.logger.info(f"  Recall: {recall:.4f}")
        self.logger.info(f"  F1 Score: {f1:.4f}")
        self.logger.info(f"  ROC-AUC: {roc_auc:.4f}")

        if return_predictions:
            results['predictions'] = y_pred
            results['probabilities'] = y_proba

        return results

    def compare_with_base_models(
        self,
        test_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Compare ensemble with individual base models.

        Args:
            test_df: Test DataFrame

        Returns:
            Comparison DataFrame
        """
        self.logger.info("Comparing ensemble with base models...")

        # Ensemble results
        ensemble_results = self.evaluate(test_df)

        # Base model results
        y_true = (test_df['compliance_status'] == 'non_compliant').astype(int).values

        results = []

        # BERT
        bert_pred, bert_proba = self.bert_model.predict(test_df['log_message'].values)
        bert_pred_binary = (np.array(bert_pred) == 'non_compliant').astype(int)
        bert_acc = accuracy_score(y_true, bert_pred_binary)
        bert_prec, bert_rec, bert_f1, _ = precision_recall_fscore_support(
            y_true, bert_pred_binary, average='binary', zero_division=0
        )
        results.append({
            'Model': 'BERT',
            'Accuracy': bert_acc,
            'Precision': bert_prec,
            'Recall': bert_rec,
            'F1 Score': bert_f1
        })

        # XGBoost
        xgb_pred, xgb_proba = self.xgboost_model.predict(test_df)
        xgb_pred_binary = (np.array(xgb_pred) == 'non_compliant').astype(int)
        xgb_acc = accuracy_score(y_true, xgb_pred_binary)
        xgb_prec, xgb_rec, xgb_f1, _ = precision_recall_fscore_support(
            y_true, xgb_pred_binary, average='binary', zero_division=0
        )
        results.append({
            'Model': 'XGBoost',
            'Accuracy': xgb_acc,
            'Precision': xgb_prec,
            'Recall': xgb_rec,
            'F1 Score': xgb_f1
        })

        # LSTM
        if self.use_lstm and self.lstm_model:
            lstm_pred, lstm_proba = self.lstm_model.predict(test_df['log_message'].values)
            lstm_pred_binary = (np.array(lstm_pred) == 'non_compliant').astype(int)
            lstm_acc = accuracy_score(y_true, lstm_pred_binary)
            lstm_prec, lstm_rec, lstm_f1, _ = precision_recall_fscore_support(
                y_true, lstm_pred_binary, average='binary', zero_division=0
            )
            results.append({
                'Model': 'LSTM',
                'Accuracy': lstm_acc,
                'Precision': lstm_prec,
                'Recall': lstm_rec,
                'F1 Score': lstm_f1
            })

        # Ensemble
        results.append({
            'Model': f'Ensemble ({self.ensemble_method})',
            'Accuracy': ensemble_results['accuracy'],
            'Precision': ensemble_results['precision'],
            'Recall': ensemble_results['recall'],
            'F1 Score': ensemble_results['f1_score']
        })

        comparison_df = pd.DataFrame(results)

        self.logger.info("\nModel Comparison:")
        self.logger.info("\n" + comparison_df.to_string(index=False))

        # Determine if ensemble improved
        best_base_acc = max([r['Accuracy'] for r in results[:-1]])
        ensemble_acc = ensemble_results['accuracy']

        if ensemble_acc > best_base_acc:
            improvement = (ensemble_acc - best_base_acc) * 100
            self.logger.info(f"\n✅ Ensemble improved accuracy by {improvement:.2f}%")
        else:
            self.logger.info(f"\n⚠️ Ensemble did not improve over best base model")

        return comparison_df

    def save_model(self, save_dir: str):
        """
        Save ensemble configuration.

        Args:
            save_dir: Directory to save ensemble
        """
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        # Save meta-classifier if using stacking
        if self.ensemble_method == 'stacking' and self.meta_classifier:
            joblib.dump(
                self.meta_classifier,
                save_path / 'meta_classifier.joblib'
            )

        # Save configuration
        config = {
            'ensemble_method': self.ensemble_method,
            'voting_strategy': self.voting_strategy,
            'weights': self.weights,
            'use_lstm': self.use_lstm
        }

        with open(save_path / 'ensemble_config.json', 'w') as f:
            json.dump(config, f, indent=2)

        self.logger.info(f"Ensemble saved to: {save_path}")

    def load_model(self, load_dir: str):
        """
        Load ensemble configuration.

        Args:
            load_dir: Directory containing ensemble
        """
        load_path = Path(load_dir)

        # Load configuration
        with open(load_path / 'ensemble_config.json') as f:
            config = json.load(f)

        self.ensemble_method = config['ensemble_method']
        self.voting_strategy = config['voting_strategy']
        self.weights = config['weights']
        self.use_lstm = config['use_lstm']

        # Load meta-classifier if exists
        meta_path = load_path / 'meta_classifier.joblib'
        if meta_path.exists():
            self.meta_classifier = joblib.load(meta_path)

        self.is_fitted = True
        self.logger.info(f"Ensemble loaded from: {load_path}")


def main():
    """Demo: Train and evaluate ensemble"""
    import argparse

    parser = argparse.ArgumentParser(description='Train hybrid ensemble classifier')
    parser.add_argument('--data-dir', type=str, default='data/real_formatted',
                      help='Data directory')
    parser.add_argument('--bert-model', type=str, default='results/real_data/bert/best_model',
                      help='BERT model path')
    parser.add_argument('--xgboost-model', type=str, default='results/real_data/xgboost/best_model',
                      help='XGBoost model path')
    parser.add_argument('--lstm-model', type=str, default='results/real_data/lstm/best_model',
                      help='LSTM model path')
    parser.add_argument('--method', type=str, default='stacking', choices=['stacking', 'voting'],
                      help='Ensemble method')
    parser.add_argument('--save-dir', type=str, default='results/ensemble',
                      help='Save directory')

    args = parser.parse_args()

    # Load data
    print("Loading data...")
    train_df = pd.read_csv(f"{args.data_dir}/compliance_events_train.csv")
    val_df = pd.read_csv(f"{args.data_dir}/compliance_events_val.csv")
    test_df = pd.read_csv(f"{args.data_dir}/compliance_events_test.csv")

    # Create ensemble
    print(f"\nCreating {args.method} ensemble...")
    ensemble = EnsembleClassifier(ensemble_method=args.method)

    # Load base models
    ensemble.load_base_models(
        bert_path=args.bert_model,
        xgboost_path=args.xgboost_model,
        lstm_path=args.lstm_model
    )

    # Fit meta-classifier
    ensemble.fit_meta_classifier(train_df, val_df)

    # Evaluate
    print("\nEvaluating ensemble...")
    results = ensemble.evaluate(test_df)

    # Compare with base models
    comparison = ensemble.compare_with_base_models(test_df)

    # Save
    ensemble.save_model(args.save_dir)

    print(f"\n✅ Ensemble training complete!")
    print(f"Results saved to: {args.save_dir}")


if __name__ == "__main__":
    main()
