"""
Model Evaluation Metrics for Compliance Classification.

This module provides comprehensive evaluation metrics for binary classification
of compliance events:
- Accuracy
- Precision
- Recall
- F1 Score
- Error Rate
- ROC-AUC
- Confusion Matrix
- Classification Report

Features:
- Support for binary and multi-class classification
- Visualization of confusion matrices
- Detailed classification reports
- Threshold tuning for precision/recall trade-off
- Cross-validation support
- Model comparison utilities

Target: >93% accuracy for mid-October deliverable
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import json
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    roc_curve,
    precision_recall_curve
)
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns

import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import setup_logger


class ModelEvaluator:
    """
    Comprehensive model evaluation toolkit.

    Provides metrics and visualizations for assessing compliance
    classification model performance.
    """

    def __init__(self, output_dir: str = "results/evaluation"):
        """
        Initialize model evaluator.

        Args:
            output_dir: Directory for saving evaluation results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger("evaluation", "logs/evaluation.log")

        self.logger.info(f"Model evaluator initialized: {output_dir}")

    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: Optional[np.ndarray] = None,
        model_name: str = "model"
    ) -> Dict[str, Any]:
        """
        Evaluate model predictions.

        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional)
            model_name: Name of the model for logging

        Returns:
            Dictionary of evaluation metrics
        """
        self.logger.info(f"Evaluating {model_name}...")

        # Basic metrics
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='binary', pos_label='non_compliant')
        recall = recall_score(y_true, y_pred, average='binary', pos_label='non_compliant')
        f1 = f1_score(y_true, y_pred, average='binary', pos_label='non_compliant')

        # Error rate
        error_rate = 1 - accuracy

        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred, labels=['compliant', 'non_compliant'])

        # ROC-AUC (if probabilities provided)
        roc_auc = None
        if y_pred_proba is not None:
            try:
                # Convert labels to binary
                y_true_binary = (y_true == 'non_compliant').astype(int)
                roc_auc = roc_auc_score(y_true_binary, y_pred_proba)
            except Exception as e:
                self.logger.warning(f"Could not compute ROC-AUC: {e}")

        # Classification report
        report = classification_report(
            y_true, y_pred,
            labels=['compliant', 'non_compliant'],
            output_dict=True
        )

        # Compile metrics
        metrics = {
            "model_name": model_name,
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "error_rate": float(error_rate),
            "roc_auc": float(roc_auc) if roc_auc is not None else None,
            "confusion_matrix": cm.tolist(),
            "classification_report": report,
            "total_samples": len(y_true),
            "true_positives": int(cm[1, 1]),
            "true_negatives": int(cm[0, 0]),
            "false_positives": int(cm[0, 1]),
            "false_negatives": int(cm[1, 0])
        }

        # Log summary
        self.logger.info(f"{model_name} Evaluation:")
        self.logger.info(f"  Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
        self.logger.info(f"  Precision: {precision:.4f}")
        self.logger.info(f"  Recall: {recall:.4f}")
        self.logger.info(f"  F1 Score: {f1:.4f}")
        self.logger.info(f"  Error Rate: {error_rate:.4f}")
        if roc_auc:
            self.logger.info(f"  ROC-AUC: {roc_auc:.4f}")

        # Check if target accuracy met
        if accuracy >= 0.93:
            self.logger.info(f"✅ Target accuracy (>93%) MET: {accuracy*100:.2f}%")
        else:
            self.logger.warning(f"⚠️ Target accuracy (>93%) NOT MET: {accuracy*100:.2f}%")

        return metrics

    def plot_confusion_matrix(
        self,
        cm: np.ndarray,
        model_name: str = "model",
        save: bool = True
    ) -> Optional[Path]:
        """
        Plot confusion matrix heatmap.

        Args:
            cm: Confusion matrix array
            model_name: Model name for title
            save: Whether to save plot

        Returns:
            Path to saved plot if save=True
        """
        plt.figure(figsize=(8, 6))

        # Plot heatmap
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['Compliant', 'Non-Compliant'],
            yticklabels=['Compliant', 'Non-Compliant'],
            cbar=True
        )

        plt.title(f'Confusion Matrix - {model_name}')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()

        if save:
            output_path = self.output_dir / f"{model_name}_confusion_matrix.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Confusion matrix saved: {output_path}")
            plt.close()
            return output_path
        else:
            plt.show()
            return None

    def plot_roc_curve(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        model_name: str = "model",
        save: bool = True
    ) -> Optional[Path]:
        """
        Plot ROC curve.

        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            model_name: Model name
            save: Whether to save plot

        Returns:
            Path to saved plot if save=True
        """
        # Convert labels to binary
        y_true_binary = (y_true == 'non_compliant').astype(int)

        # Compute ROC curve
        fpr, tpr, thresholds = roc_curve(y_true_binary, y_pred_proba)
        roc_auc = roc_auc_score(y_true_binary, y_pred_proba)

        plt.figure(figsize=(8, 6))

        plt.plot(fpr, tpr, color='darkorange', lw=2,
                label=f'ROC curve (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--',
                label='Random classifier')

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {model_name}')
        plt.legend(loc="lower right")
        plt.grid(alpha=0.3)
        plt.tight_layout()

        if save:
            output_path = self.output_dir / f"{model_name}_roc_curve.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"ROC curve saved: {output_path}")
            plt.close()
            return output_path
        else:
            plt.show()
            return None

    def plot_precision_recall_curve(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        model_name: str = "model",
        save: bool = True
    ) -> Optional[Path]:
        """
        Plot precision-recall curve.

        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            model_name: Model name
            save: Whether to save plot

        Returns:
            Path to saved plot if save=True
        """
        # Convert labels to binary
        y_true_binary = (y_true == 'non_compliant').astype(int)

        # Compute precision-recall curve
        precision, recall, thresholds = precision_recall_curve(
            y_true_binary, y_pred_proba
        )

        plt.figure(figsize=(8, 6))

        plt.plot(recall, precision, color='blue', lw=2)
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curve - {model_name}')
        plt.grid(alpha=0.3)
        plt.tight_layout()

        if save:
            output_path = self.output_dir / f"{model_name}_pr_curve.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"PR curve saved: {output_path}")
            plt.close()
            return output_path
        else:
            plt.show()
            return None

    def save_metrics(
        self,
        metrics: Dict[str, Any],
        filename: str = None
    ) -> Path:
        """
        Save metrics to JSON file.

        Args:
            metrics: Metrics dictionary
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file
        """
        if filename is None:
            model_name = metrics.get('model_name', 'model')
            filename = f"{model_name}_metrics.json"

        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(metrics, f, indent=2)

        self.logger.info(f"Metrics saved: {output_path}")

        return output_path

    def compare_models(
        self,
        metrics_list: List[Dict[str, Any]],
        save: bool = True
    ) -> pd.DataFrame:
        """
        Compare multiple models.

        Args:
            metrics_list: List of metrics dictionaries
            save: Whether to save comparison

        Returns:
            DataFrame with model comparison
        """
        self.logger.info(f"Comparing {len(metrics_list)} models...")

        # Extract key metrics
        comparison_data = []

        for metrics in metrics_list:
            row = {
                'Model': metrics['model_name'],
                'Accuracy': metrics['accuracy'],
                'Precision': metrics['precision'],
                'Recall': metrics['recall'],
                'F1 Score': metrics['f1_score'],
                'Error Rate': metrics['error_rate'],
                'ROC-AUC': metrics.get('roc_auc', None)
            }
            comparison_data.append(row)

        df_comparison = pd.DataFrame(comparison_data)

        # Sort by accuracy (descending)
        df_comparison = df_comparison.sort_values('Accuracy', ascending=False)

        # Log comparison
        self.logger.info("Model Comparison:")
        self.logger.info(f"\n{df_comparison.to_string(index=False)}")

        # Identify best model
        best_model = df_comparison.iloc[0]['Model']
        best_accuracy = df_comparison.iloc[0]['Accuracy']

        self.logger.info(f"\n🏆 Best Model: {best_model} (Accuracy: {best_accuracy:.4f})")

        if save:
            output_path = self.output_dir / "model_comparison.csv"
            df_comparison.to_csv(output_path, index=False)
            self.logger.info(f"Comparison saved: {output_path}")

        return df_comparison

    def plot_model_comparison(
        self,
        df_comparison: pd.DataFrame,
        save: bool = True
    ) -> Optional[Path]:
        """
        Plot model comparison bar chart.

        Args:
            df_comparison: Model comparison DataFrame
            save: Whether to save plot

        Returns:
            Path to saved plot if save=True
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score']

        for idx, metric in enumerate(metrics):
            ax = axes[idx // 2, idx % 2]

            df_comparison.plot(
                x='Model',
                y=metric,
                kind='bar',
                ax=ax,
                legend=False,
                color='skyblue'
            )

            ax.set_title(f'{metric} Comparison', fontsize=12, fontweight='bold')
            ax.set_xlabel('')
            ax.set_ylabel(metric)
            ax.set_ylim([0, 1.05])
            ax.grid(axis='y', alpha=0.3)

            # Add value labels on bars
            for container in ax.containers:
                ax.bar_label(container, fmt='%.3f', padding=3)

            # Rotate x labels
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')

        plt.tight_layout()

        if save:
            output_path = self.output_dir / "model_comparison.png"
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Comparison plot saved: {output_path}")
            plt.close()
            return output_path
        else:
            plt.show()
            return None

    def cross_validate(
        self,
        model,
        X: np.ndarray,
        y: np.ndarray,
        cv: int = 5,
        scoring: str = 'accuracy'
    ) -> Dict[str, float]:
        """
        Perform cross-validation.

        Args:
            model: Scikit-learn compatible model
            X: Feature matrix
            y: Target labels
            cv: Number of folds
            scoring: Scoring metric

        Returns:
            Dictionary with CV results
        """
        self.logger.info(f"Performing {cv}-fold cross-validation...")

        scores = cross_val_score(model, X, y, cv=cv, scoring=scoring)

        results = {
            'mean_score': float(np.mean(scores)),
            'std_score': float(np.std(scores)),
            'min_score': float(np.min(scores)),
            'max_score': float(np.max(scores)),
            'scores': scores.tolist()
        }

        self.logger.info(f"CV {scoring}: {results['mean_score']:.4f} ± {results['std_score']:.4f}")

        return results


def main():
    """
    Main function to demonstrate evaluation metrics.

    Creates synthetic predictions and evaluates them.
    """
    print("\n" + "="*60)
    print("MODEL EVALUATION METRICS - DEMO")
    print("="*60 + "\n")

    # Create synthetic data for demonstration
    np.random.seed(42)

    n_samples = 1000

    # True labels (75% compliant, 25% non-compliant)
    y_true = np.random.choice(
        ['compliant', 'non_compliant'],
        size=n_samples,
        p=[0.75, 0.25]
    )

    # Predicted labels (simulate 95% accuracy)
    y_pred = y_true.copy()
    n_errors = int(n_samples * 0.05)
    error_indices = np.random.choice(n_samples, n_errors, replace=False)

    for idx in error_indices:
        y_pred[idx] = 'compliant' if y_pred[idx] == 'non_compliant' else 'non_compliant'

    # Predicted probabilities (random for demo)
    y_pred_proba = np.random.uniform(0, 1, n_samples)
    # Adjust probabilities to be more realistic
    y_pred_proba[y_pred == 'non_compliant'] = np.random.uniform(0.6, 1.0,
                                                                  (y_pred == 'non_compliant').sum())
    y_pred_proba[y_pred == 'compliant'] = np.random.uniform(0.0, 0.4,
                                                             (y_pred == 'compliant').sum())

    print(f"Generated {n_samples} synthetic predictions")
    print(f"True distribution: {np.unique(y_true, return_counts=True)}")
    print()

    # Initialize evaluator
    evaluator = ModelEvaluator()

    print("✅ Evaluator initialized")
    print()

    # Evaluate
    print("📊 Evaluating predictions...")
    metrics = evaluator.evaluate(
        y_true=y_true,
        y_pred=y_pred,
        y_pred_proba=y_pred_proba,
        model_name="demo_model"
    )

    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)

    print(f"\nAccuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall: {metrics['recall']:.4f}")
    print(f"F1 Score: {metrics['f1_score']:.4f}")
    print(f"Error Rate: {metrics['error_rate']:.4f}")
    print(f"ROC-AUC: {metrics['roc_auc']:.4f}")

    print(f"\nConfusion Matrix:")
    print(f"  True Negatives: {metrics['true_negatives']}")
    print(f"  False Positives: {metrics['false_positives']}")
    print(f"  False Negatives: {metrics['false_negatives']}")
    print(f"  True Positives: {metrics['true_positives']}")

    # Save metrics
    print("\n💾 Saving metrics...")
    metrics_path = evaluator.save_metrics(metrics)
    print(f"✅ Metrics saved: {metrics_path}")

    # Plot confusion matrix
    print("\n📈 Generating visualizations...")
    cm_path = evaluator.plot_confusion_matrix(
        np.array(metrics['confusion_matrix']),
        model_name="demo_model"
    )
    print(f"✅ Confusion matrix: {cm_path}")

    # Plot ROC curve
    roc_path = evaluator.plot_roc_curve(
        y_true=y_true,
        y_pred_proba=y_pred_proba,
        model_name="demo_model"
    )
    print(f"✅ ROC curve: {roc_path}")

    # Plot PR curve
    pr_path = evaluator.plot_precision_recall_curve(
        y_true=y_true,
        y_pred_proba=y_pred_proba,
        model_name="demo_model"
    )
    print(f"✅ PR curve: {pr_path}")

    print("\n" + "="*60)
    print("✅ EVALUATION DEMO COMPLETE!")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
