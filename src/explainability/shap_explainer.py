"""
SHAP Explainability for XGBoost Compliance Classifier

Provides model-agnostic explanations for XGBoost predictions using SHAP
(SHapley Additive exPlanations) values.

Features:
- Global feature importance (which features matter most overall)
- Local explanations (why a specific log was flagged)
- Dependence plots (how features interact)
- Force plots (visual explanation for individual predictions)
- Summary plots (distribution of feature impacts)

Author: Moise Iradukunda (CMU)
Date: October 2025
"""

import shap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import joblib
import json

import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import setup_logger


class SHAPExplainer:
    """
    SHAP-based explainability for XGBoost compliance classifier.

    Uses TreeExplainer for fast, exact SHAP values for tree-based models.
    """

    def __init__(self, model_path: str = None):
        """
        Initialize SHAP explainer.

        Args:
            model_path: Path to trained XGBoost model
        """
        self.model = None
        self.feature_engineer = None
        self.explainer = None
        self.feature_names = None
        self.shap_values = None
        self.base_value = None

        self.logger = setup_logger("shap_explainer", "logs/shap_explainer.log")

        if model_path:
            self.load_model(model_path)

        self.logger.info("SHAP Explainer initialized")

    def load_model(self, model_path: str):
        """
        Load trained XGBoost model.

        Args:
            model_path: Path to model directory
        """
        from models.xgboost_classifier import XGBoostClassifier

        self.logger.info(f"Loading model from: {model_path}")

        # Load XGBoost classifier
        xgb_classifier = XGBoostClassifier()
        xgb_classifier.load_model(model_path)

        self.model = xgb_classifier.model
        self.feature_engineer = xgb_classifier.feature_engineer

        # Get feature names
        self.feature_names = self.feature_engineer.get_feature_names()

        # Initialize SHAP TreeExplainer
        self.explainer = shap.TreeExplainer(self.model)

        self.logger.info(f"✅ Model loaded with {len(self.feature_names)} features")
        self.logger.info(f"   SHAP TreeExplainer initialized")

    def explain_dataset(
        self,
        df: pd.DataFrame,
        max_samples: int = 1000
    ) -> np.ndarray:
        """
        Calculate SHAP values for entire dataset.

        Args:
            df: DataFrame with compliance events
            max_samples: Maximum samples to explain (for performance)

        Returns:
            SHAP values array (samples × features)
        """
        self.logger.info(f"Calculating SHAP values for {len(df)} samples...")

        # Sample if too large
        if len(df) > max_samples:
            self.logger.info(f"  Sampling {max_samples} from {len(df)} for performance")
            df_sample = df.sample(n=max_samples, random_state=42)
        else:
            df_sample = df

        # Transform to features
        X = self.feature_engineer.fit_transform(df_sample)

        # Calculate SHAP values
        self.shap_values = self.explainer.shap_values(X)
        self.base_value = self.explainer.expected_value

        self.logger.info(f"✅ SHAP values calculated: {self.shap_values.shape}")
        self.logger.info(f"   Base value (expected): {self.base_value:.4f}")

        return self.shap_values

    def global_feature_importance(
        self,
        save_path: str = None,
        top_n: int = 20
    ) -> pd.DataFrame:
        """
        Calculate global feature importance from SHAP values.

        Args:
            save_path: Path to save plot
            top_n: Number of top features to show

        Returns:
            DataFrame with feature importance
        """
        if self.shap_values is None:
            raise ValueError("Call explain_dataset() first to calculate SHAP values")

        self.logger.info("Calculating global feature importance...")

        # Mean absolute SHAP value for each feature
        importance = np.abs(self.shap_values).mean(axis=0)

        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)

        # Top N features
        top_features = importance_df.head(top_n)

        self.logger.info(f"Top {top_n} features by SHAP importance:")
        for idx, row in top_features.iterrows():
            self.logger.info(f"  {row['feature']}: {row['importance']:.4f}")

        # Plot
        if save_path:
            plt.figure(figsize=(10, 8))
            plt.barh(range(len(top_features)), top_features['importance'].values)
            plt.yticks(range(len(top_features)), top_features['feature'].values)
            plt.xlabel('Mean |SHAP value| (average impact on model output)')
            plt.title(f'Top {top_n} Features - Global SHAP Importance')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            self.logger.info(f"✅ Plot saved: {save_path}")

        return importance_df

    def summary_plot(self, save_path: str = None):
        """
        Create SHAP summary plot (beeswarm plot).

        Shows distribution of SHAP values for each feature.
        """
        if self.shap_values is None:
            raise ValueError("Call explain_dataset() first")

        self.logger.info("Creating SHAP summary plot...")

        plt.figure(figsize=(12, 10))
        shap.summary_plot(
            self.shap_values,
            features=self.shap_values,  # Use SHAP values for coloring
            feature_names=self.feature_names,
            show=False,
            max_display=20
        )

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            self.logger.info(f"✅ Summary plot saved: {save_path}")
        else:
            plt.show()

    def explain_prediction(
        self,
        log_message: str,
        log_data: Dict,
        save_path: str = None
    ) -> Dict:
        """
        Explain a single prediction with SHAP force plot.

        Args:
            log_message: The log message text
            log_data: Dictionary with metadata (control_id, control_family, etc.)
            save_path: Path to save force plot

        Returns:
            Explanation dictionary
        """
        self.logger.info(f"Explaining prediction for log: {log_message[:100]}...")

        # Create DataFrame for single sample
        df = pd.DataFrame([{
            'log_message': log_message,
            **log_data
        }])

        # Transform to features
        X = self.feature_engineer.transform(df)

        # Get prediction
        y_pred = self.model.predict(X)[0]
        y_proba = self.model.predict_proba(X)[0]

        # Calculate SHAP values for this sample
        shap_values_sample = self.explainer.shap_values(X)

        # Get top contributing features
        shap_dict = {
            name: float(val)
            for name, val in zip(self.feature_names, shap_values_sample[0])
        }

        # Sort by absolute impact
        sorted_features = sorted(
            shap_dict.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        explanation = {
            'log_message': log_message,
            'prediction': int(y_pred),
            'prediction_label': 'non_compliant' if y_pred == 1 else 'compliant',
            'probability_compliant': float(y_proba[0]),
            'probability_non_compliant': float(y_proba[1]),
            'base_value': float(self.base_value),
            'shap_values': shap_dict,
            'top_positive_features': [
                {'feature': name, 'shap_value': val}
                for name, val in sorted_features if val > 0
            ][:10],
            'top_negative_features': [
                {'feature': name, 'shap_value': val}
                for name, val in sorted_features if val < 0
            ][:10]
        }

        self.logger.info(f"  Prediction: {explanation['prediction_label']}")
        self.logger.info(f"  Probability: {explanation['probability_non_compliant']:.4f}")
        self.logger.info(f"  Top 3 contributing features:")
        for feat in explanation['top_positive_features'][:3]:
            self.logger.info(f"    {feat['feature']}: +{feat['shap_value']:.4f}")

        # Create force plot
        if save_path:
            shap.force_plot(
                self.base_value,
                shap_values_sample[0],
                X[0],
                feature_names=self.feature_names,
                matplotlib=True,
                show=False
            )
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            self.logger.info(f"✅ Force plot saved: {save_path}")

        return explanation

    def dependence_plot(
        self,
        feature_name: str,
        interaction_feature: str = None,
        save_path: str = None
    ):
        """
        Create SHAP dependence plot for a feature.

        Shows how SHAP values for a feature vary with its value.

        Args:
            feature_name: Feature to plot
            interaction_feature: Feature to use for interaction coloring
            save_path: Path to save plot
        """
        if self.shap_values is None:
            raise ValueError("Call explain_dataset() first")

        self.logger.info(f"Creating dependence plot for: {feature_name}")

        # Get feature index
        try:
            feature_idx = self.feature_names.index(feature_name)
        except ValueError:
            self.logger.error(f"Feature '{feature_name}' not found")
            return

        plt.figure(figsize=(10, 6))
        shap.dependence_plot(
            feature_idx,
            self.shap_values,
            features=self.shap_values,  # Use SHAP values as features for coloring
            feature_names=self.feature_names,
            interaction_index=interaction_feature,
            show=False
        )

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            self.logger.info(f"✅ Dependence plot saved: {save_path}")
        else:
            plt.show()

    def generate_report(
        self,
        df: pd.DataFrame,
        output_dir: str = "results/explainability",
        top_n_features: int = 20
    ):
        """
        Generate comprehensive explainability report.

        Args:
            df: Test DataFrame
            output_dir: Directory to save outputs
            top_n_features: Number of top features to analyze
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        self.logger.info("=" * 80)
        self.logger.info("GENERATING SHAP EXPLAINABILITY REPORT")
        self.logger.info("=" * 80)

        # 1. Calculate SHAP values
        self.explain_dataset(df, max_samples=1000)

        # 2. Global feature importance
        importance_df = self.global_feature_importance(
            save_path=str(output_path / "shap_global_importance.png"),
            top_n=top_n_features
        )

        # Save importance to CSV
        importance_df.to_csv(output_path / "shap_feature_importance.csv", index=False)

        # 3. Summary plot
        self.summary_plot(save_path=str(output_path / "shap_summary_plot.png"))

        # 4. Dependence plots for top features
        self.logger.info("\nCreating dependence plots for top 5 features...")
        top_features = importance_df.head(5)['feature'].values

        for i, feature in enumerate(top_features):
            self.dependence_plot(
                feature,
                save_path=str(output_path / f"shap_dependence_{i+1}_{feature}.png")
            )

        # 5. Example explanations
        self.logger.info("\nGenerating example explanations...")

        # Get one compliant and one non-compliant example
        compliant_samples = df[df['compliance_status'] == 'compliant'].sample(n=1)
        non_compliant_samples = df[df['compliance_status'] == 'non_compliant'].sample(n=1)

        examples = []

        for idx, (sample_type, samples) in enumerate([
            ('compliant', compliant_samples),
            ('non_compliant', non_compliant_samples)
        ]):
            for _, row in samples.iterrows():
                explanation = self.explain_prediction(
                    row['log_message'],
                    {
                        'control_id': row['control_id'],
                        'control_family': row['control_family'],
                        'framework': row.get('framework', 'NIST-800-53')
                    },
                    save_path=str(output_path / f"shap_force_plot_{sample_type}.png")
                )
                examples.append(explanation)

        # Save examples to JSON
        with open(output_path / "shap_example_explanations.json", 'w') as f:
            json.dump(examples, f, indent=2)

        # 6. Create summary report
        report = {
            'model_type': 'XGBoost',
            'total_features': len(self.feature_names),
            'samples_analyzed': len(self.shap_values),
            'base_value': float(self.base_value),
            'top_features': [
                {
                    'rank': i+1,
                    'feature': row['feature'],
                    'importance': float(row['importance'])
                }
                for i, (_, row) in enumerate(importance_df.head(top_n_features).iterrows())
            ]
        }

        with open(output_path / "shap_report_summary.json", 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info("\n" + "=" * 80)
        self.logger.info("SHAP EXPLAINABILITY REPORT COMPLETE")
        self.logger.info("=" * 80)
        self.logger.info(f"✅ All outputs saved to: {output_path}")
        self.logger.info(f"   - Global importance: shap_global_importance.png")
        self.logger.info(f"   - Summary plot: shap_summary_plot.png")
        self.logger.info(f"   - Dependence plots: {len(top_features)} plots")
        self.logger.info(f"   - Example explanations: 2 force plots")
        self.logger.info(f"   - Report summary: shap_report_summary.json")

        return report


def main():
    """Demo: Generate SHAP explainability report"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate SHAP explainability report')
    parser.add_argument('--model-path', type=str,
                       default='results/real_data/xgboost/best_model',
                       help='Path to XGBoost model')
    parser.add_argument('--data-path', type=str,
                       default='data/real_formatted/compliance_events_test.csv',
                       help='Path to test data')
    parser.add_argument('--output-dir', type=str,
                       default='results/explainability',
                       help='Output directory')
    parser.add_argument('--top-n', type=int, default=20,
                       help='Number of top features to analyze')

    args = parser.parse_args()

    # Check if model exists
    if not Path(args.model_path).exists():
        print(f"❌ Error: Model not found at {args.model_path}")
        print(f"\nNote: XGBoost model was not saved during training.")
        print(f"Options:")
        print(f"  1. Retrain XGBoost with model saving enabled")
        print(f"  2. Use the feature importance already calculated in results/evaluation/")
        return

    # Load data
    print(f"Loading test data from: {args.data_path}")
    df = pd.read_csv(args.data_path)
    print(f"✅ Loaded {len(df)} samples\n")

    # Create explainer
    explainer = SHAPExplainer(model_path=args.model_path)

    # Generate report
    report = explainer.generate_report(
        df,
        output_dir=args.output_dir,
        top_n_features=args.top_n
    )

    print(f"\n✅ SHAP explainability report generated!")
    print(f"📊 View results in: {args.output_dir}/")


if __name__ == "__main__":
    main()
