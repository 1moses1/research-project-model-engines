"""
Unified Training Pipeline for All Baseline Models.

This script trains all three baseline models (BERT, XGBoost, LSTM) on the
synthetic compliance dataset and generates comprehensive comparison results.

Workflow:
1. Load and validate dataset
2. Train BERT classifier
3. Train XGBoost classifier
4. Train LSTM classifier
5. Evaluate all models on test set
6. Generate comparison visualizations
7. Save results and best model

Usage:
    python train_all_models.py [--sample N] [--epochs N] [--gpu]

Arguments:
    --sample N: Use only N samples for quick testing (default: full dataset)
    --epochs N: Number of epochs for BERT/LSTM (default: 5 for BERT, 10 for LSTM)
    --gpu: Force GPU usage (auto-detected by default)
    --skip-bert: Skip BERT training (large model)
    --skip-xgboost: Skip XGBoost training
    --skip-lstm: Skip LSTM training

Target: Achieve >93% accuracy on at least one model
"""

import sys
from pathlib import Path
import argparse
import json
import time
from datetime import datetime
import pandas as pd
import numpy as np

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from models.bert_classifier import BERTClassifier
from models.xgboost_classifier import XGBoostClassifier
from models.lstm_classifier import LSTMClassifier
from models.evaluation import ModelEvaluator
from utils.logger import setup_logger


class TrainingPipeline:
    """
    Unified training pipeline for all baseline models.

    Manages training, evaluation, and comparison of BERT, XGBoost, and LSTM.
    """

    def __init__(
        self,
        data_dir: str = "data/synthetic",
        results_dir: str = "results",
        models_dir: str = "models/checkpoints",
        sample_size: int = None
    ):
        """
        Initialize training pipeline.

        Args:
            data_dir: Directory containing train/val/test data
            results_dir: Directory for results
            models_dir: Directory for model checkpoints
            sample_size: If provided, use only N samples (for testing)
        """
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.models_dir = Path(models_dir)
        self.sample_size = sample_size

        # Create directories
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Logger
        self.logger = setup_logger("training_pipeline", "logs/training_pipeline.log")

        # Evaluation
        self.evaluator = ModelEvaluator()

        # Results storage
        self.results = {
            'start_time': datetime.now().isoformat(),
            'models': {},
            'comparison': None
        }

        self.logger.info("="*60)
        self.logger.info("UNIFIED TRAINING PIPELINE INITIALIZED")
        self.logger.info("="*60)
        self.logger.info(f"Data directory: {self.data_dir}")
        self.logger.info(f"Results directory: {self.results_dir}")
        self.logger.info(f"Sample size: {sample_size or 'Full dataset'}")

    def load_data(self) -> tuple:
        """
        Load train, validation, and test datasets.

        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("LOADING DATASETS")
        self.logger.info("="*60)

        # Check if files exist
        train_file = self.data_dir / "compliance_events_train.csv"
        val_file = self.data_dir / "compliance_events_val.csv"
        test_file = self.data_dir / "compliance_events_test.csv"

        if not train_file.exists():
            self.logger.error(f"Training file not found: {train_file}")
            self.logger.error("Please generate synthetic dataset first:")
            self.logger.error("  python src/data_pipeline/synthetic_generator.py")
            raise FileNotFoundError(f"Training file not found: {train_file}")

        # Load datasets
        train_df = pd.read_csv(train_file)
        val_df = pd.read_csv(val_file)
        test_df = pd.read_csv(test_file)

        self.logger.info(f"✅ Loaded train: {len(train_df)} samples")
        self.logger.info(f"✅ Loaded val: {len(val_df)} samples")
        self.logger.info(f"✅ Loaded test: {len(test_df)} samples")

        # Sample if requested
        if self.sample_size:
            self.logger.info(f"\n⚠️  Using sample size: {self.sample_size}")
            train_df = train_df.head(self.sample_size)
            val_df = val_df.head(int(self.sample_size * 0.15 / 0.70))
            test_df = test_df.head(int(self.sample_size * 0.15 / 0.70))

            self.logger.info(f"   Train: {len(train_df)}")
            self.logger.info(f"   Val: {len(val_df)}")
            self.logger.info(f"   Test: {len(test_df)}")

        # Validate data
        required_columns = ['log_message', 'compliance_status']
        for col in required_columns:
            if col not in train_df.columns:
                raise ValueError(f"Required column '{col}' not found in dataset")

        # Check class distribution
        self.logger.info("\nClass distribution (train):")
        class_dist = train_df['compliance_status'].value_counts()
        for label, count in class_dist.items():
            self.logger.info(f"  {label}: {count} ({count/len(train_df)*100:.1f}%)")

        return train_df, val_df, test_df

    def train_bert(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        epochs: int = 5
    ) -> dict:
        """
        Train BERT classifier.

        Args:
            train_df: Training data
            val_df: Validation data
            test_df: Test data
            epochs: Number of epochs

        Returns:
            Dictionary with model, predictions, and metrics
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("TRAINING BERT CLASSIFIER")
        self.logger.info("="*60)

        start_time = time.time()

        try:
            # Initialize
            classifier = BERTClassifier(
                model_name='bert-base-uncased',
                max_length=128,
                freeze_layers=10
            )

            # Prepare data
            train_loader, val_loader = classifier.prepare_data(
                train_texts=train_df['log_message'].tolist(),
                train_labels=train_df['compliance_status'].tolist(),
                val_texts=val_df['log_message'].tolist(),
                val_labels=val_df['compliance_status'].tolist(),
                batch_size=16
            )

            # Train
            history = classifier.train(
                train_loader=train_loader,
                val_loader=val_loader,
                epochs=epochs,
                learning_rate=2e-5,
                save_dir=str(self.models_dir / "bert")
            )

            # Predict on test set
            self.logger.info("\nEvaluating on test set...")
            test_pred, test_proba = classifier.predict(
                texts=test_df['log_message'].tolist(),
                batch_size=32
            )

            # Evaluate
            metrics = self.evaluator.evaluate(
                y_true=test_df['compliance_status'].values,
                y_pred=test_pred,
                y_pred_proba=test_proba,
                model_name="BERT"
            )

            # Save metrics
            self.evaluator.save_metrics(metrics, "bert_metrics.json")

            # Visualizations
            self.evaluator.plot_confusion_matrix(
                np.array(metrics['confusion_matrix']),
                "BERT",
                save=True
            )

            self.evaluator.plot_roc_curve(
                test_df['compliance_status'].values,
                test_proba,
                "BERT",
                save=True
            )

            training_time = time.time() - start_time

            self.logger.info(f"\n✅ BERT training complete in {training_time/60:.1f} minutes")
            self.logger.info(f"   Test Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")

            return {
                'model': classifier,
                'predictions': test_pred,
                'probabilities': test_proba,
                'metrics': metrics,
                'history': history,
                'training_time': training_time
            }

        except Exception as e:
            self.logger.error(f"❌ BERT training failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def train_xgboost(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame
    ) -> dict:
        """
        Train XGBoost classifier.

        Args:
            train_df: Training data
            val_df: Validation data
            test_df: Test data

        Returns:
            Dictionary with model, predictions, and metrics
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("TRAINING XGBOOST CLASSIFIER")
        self.logger.info("="*60)

        start_time = time.time()

        try:
            # Initialize
            classifier = XGBoostClassifier(
                n_estimators=500,
                max_depth=6,
                learning_rate=0.1,
                use_gpu=False
            )

            # Prepare data
            X_train, y_train, X_val, y_val = classifier.prepare_data(train_df, val_df)

            # Train
            history = classifier.train(
                X_train, y_train,
                X_val, y_val,
                early_stopping_rounds=50
            )

            # Predict on test set
            self.logger.info("\nEvaluating on test set...")
            test_pred, test_proba = classifier.predict(test_df)

            # Evaluate
            metrics = self.evaluator.evaluate(
                y_true=test_df['compliance_status'].values,
                y_pred=test_pred,
                y_pred_proba=test_proba,
                model_name="XGBoost"
            )

            # Save metrics
            self.evaluator.save_metrics(metrics, "xgboost_metrics.json")

            # Visualizations
            self.evaluator.plot_confusion_matrix(
                np.array(metrics['confusion_matrix']),
                "XGBoost",
                save=True
            )

            self.evaluator.plot_roc_curve(
                test_df['compliance_status'].values,
                test_proba,
                "XGBoost",
                save=True
            )

            # Feature importance
            importance_df = classifier.get_feature_importance(top_n=20)

            training_time = time.time() - start_time

            self.logger.info(f"\n✅ XGBoost training complete in {training_time/60:.1f} minutes")
            self.logger.info(f"   Test Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")

            return {
                'model': classifier,
                'predictions': test_pred,
                'probabilities': test_proba,
                'metrics': metrics,
                'history': history,
                'feature_importance': importance_df,
                'training_time': training_time
            }

        except Exception as e:
            self.logger.error(f"❌ XGBoost training failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def train_lstm(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        epochs: int = 10
    ) -> dict:
        """
        Train LSTM classifier.

        Args:
            train_df: Training data
            val_df: Validation data
            test_df: Test data
            epochs: Number of epochs

        Returns:
            Dictionary with model, predictions, and metrics
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("TRAINING LSTM CLASSIFIER")
        self.logger.info("="*60)

        start_time = time.time()

        try:
            # Initialize
            classifier = LSTMClassifier(
                max_vocab_size=10000,
                max_length=128,
                embedding_dim=100,
                hidden_dim=128,
                num_layers=2,
                dropout=0.3
            )

            # Prepare data
            train_loader, val_loader = classifier.prepare_data(
                train_texts=train_df['log_message'].tolist(),
                train_labels=train_df['compliance_status'].tolist(),
                val_texts=val_df['log_message'].tolist(),
                val_labels=val_df['compliance_status'].tolist(),
                batch_size=32
            )

            # Train
            history = classifier.train(
                train_loader=train_loader,
                val_loader=val_loader,
                epochs=epochs,
                learning_rate=0.001,
                save_dir=str(self.models_dir / "lstm")
            )

            # Predict on test set
            self.logger.info("\nEvaluating on test set...")
            test_pred, test_proba = classifier.predict(
                texts=test_df['log_message'].tolist(),
                batch_size=32
            )

            # Evaluate
            metrics = self.evaluator.evaluate(
                y_true=test_df['compliance_status'].values,
                y_pred=test_pred,
                y_pred_proba=test_proba,
                model_name="LSTM"
            )

            # Save metrics
            self.evaluator.save_metrics(metrics, "lstm_metrics.json")

            # Visualizations
            self.evaluator.plot_confusion_matrix(
                np.array(metrics['confusion_matrix']),
                "LSTM",
                save=True
            )

            self.evaluator.plot_roc_curve(
                test_df['compliance_status'].values,
                test_proba,
                "LSTM",
                save=True
            )

            training_time = time.time() - start_time

            self.logger.info(f"\n✅ LSTM training complete in {training_time/60:.1f} minutes")
            self.logger.info(f"   Test Accuracy: {metrics['accuracy']:.4f} ({metrics['accuracy']*100:.2f}%)")

            return {
                'model': classifier,
                'predictions': test_pred,
                'probabilities': test_proba,
                'metrics': metrics,
                'history': history,
                'training_time': training_time
            }

        except Exception as e:
            self.logger.error(f"❌ LSTM training failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def compare_models(self, results: dict) -> pd.DataFrame:
        """
        Compare all trained models.

        Args:
            results: Dictionary of model results

        Returns:
            Comparison DataFrame
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("MODEL COMPARISON")
        self.logger.info("="*60)

        # Extract metrics
        metrics_list = []

        for model_name, result in results.items():
            if result is not None:
                metrics_list.append(result['metrics'])

        if not metrics_list:
            self.logger.error("No models trained successfully")
            return None

        # Compare
        comparison = self.evaluator.compare_models(metrics_list, save=True)

        # Plot comparison
        self.evaluator.plot_model_comparison(comparison, save=True)

        return comparison

    def save_final_results(self, results: dict, comparison: pd.DataFrame):
        """
        Save final training results.

        Args:
            results: All model results
            comparison: Model comparison DataFrame
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("SAVING FINAL RESULTS")
        self.logger.info("="*60)

        # Prepare summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'sample_size': self.sample_size,
            'models_trained': list(results.keys()),
            'best_model': None,
            'best_accuracy': 0.0,
            'target_achieved': False,
            'models': {}
        }

        # Add model summaries
        for model_name, result in results.items():
            if result is not None:
                summary['models'][model_name] = {
                    'accuracy': result['metrics']['accuracy'],
                    'precision': result['metrics']['precision'],
                    'recall': result['metrics']['recall'],
                    'f1_score': result['metrics']['f1_score'],
                    'training_time_minutes': result['training_time'] / 60
                }

                # Track best model
                if result['metrics']['accuracy'] > summary['best_accuracy']:
                    summary['best_accuracy'] = result['metrics']['accuracy']
                    summary['best_model'] = model_name

        # Check if target achieved
        if summary['best_accuracy'] >= 0.93:
            summary['target_achieved'] = True
            self.logger.info(f"\n🎉 TARGET ACHIEVED! Best model: {summary['best_model']}")
            self.logger.info(f"   Accuracy: {summary['best_accuracy']:.4f} ({summary['best_accuracy']*100:.2f}%)")
        else:
            self.logger.warning(f"\n⚠️  Target not achieved. Best: {summary['best_accuracy']*100:.2f}%")

        # Save summary
        summary_file = self.results_dir / "training_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        self.logger.info(f"\n✅ Results saved to {self.results_dir}/")
        self.logger.info(f"   - training_summary.json")
        self.logger.info(f"   - model_comparison.csv")
        self.logger.info(f"   - Individual model metrics and plots")

    def run(
        self,
        skip_bert: bool = False,
        skip_xgboost: bool = False,
        skip_lstm: bool = False,
        bert_epochs: int = 5,
        lstm_epochs: int = 10
    ):
        """
        Run complete training pipeline.

        Args:
            skip_bert: Skip BERT training
            skip_xgboost: Skip XGBoost training
            skip_lstm: Skip LSTM training
            bert_epochs: BERT epochs
            lstm_epochs: LSTM epochs
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("STARTING UNIFIED TRAINING PIPELINE")
        self.logger.info("="*60)

        start_time = time.time()

        # Load data
        train_df, val_df, test_df = self.load_data()

        # Train models
        results = {}

        if not skip_bert:
            results['BERT'] = self.train_bert(train_df, val_df, test_df, bert_epochs)

        if not skip_xgboost:
            results['XGBoost'] = self.train_xgboost(train_df, val_df, test_df)

        if not skip_lstm:
            results['LSTM'] = self.train_lstm(train_df, val_df, test_df, lstm_epochs)

        # Compare models
        comparison = self.compare_models(results)

        # Save results
        self.save_final_results(results, comparison)

        total_time = time.time() - start_time

        self.logger.info("\n" + "="*60)
        self.logger.info("PIPELINE COMPLETE!")
        self.logger.info("="*60)
        self.logger.info(f"Total time: {total_time/60:.1f} minutes")
        self.logger.info(f"Results directory: {self.results_dir}")


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(description="Train all baseline models")

    parser.add_argument(
        '--sample',
        type=int,
        default=None,
        help='Use only N samples for testing (default: full dataset)'
    )

    parser.add_argument(
        '--bert-epochs',
        type=int,
        default=5,
        help='Number of epochs for BERT (default: 5)'
    )

    parser.add_argument(
        '--lstm-epochs',
        type=int,
        default=10,
        help='Number of epochs for LSTM (default: 10)'
    )

    parser.add_argument(
        '--skip-bert',
        action='store_true',
        help='Skip BERT training'
    )

    parser.add_argument(
        '--skip-xgboost',
        action='store_true',
        help='Skip XGBoost training'
    )

    parser.add_argument(
        '--skip-lstm',
        action='store_true',
        help='Skip LSTM training'
    )

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = TrainingPipeline(sample_size=args.sample)

    # Run
    pipeline.run(
        skip_bert=args.skip_bert,
        skip_xgboost=args.skip_xgboost,
        skip_lstm=args.skip_lstm,
        bert_epochs=args.bert_epochs,
        lstm_epochs=args.lstm_epochs
    )

    print("\n" + "="*60)
    print("✅ TRAINING PIPELINE COMPLETE!")
    print("="*60)
    print(f"\nResults saved to: results/")
    print("\nView results:")
    print("  - results/training_summary.json")
    print("  - results/evaluation/model_comparison.csv")
    print("  - results/evaluation/*_confusion_matrix.png")
    print("  - results/evaluation/*_roc_curve.png")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
