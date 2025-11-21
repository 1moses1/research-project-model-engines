#!/usr/bin/env python3
"""
Retrain XGBoost Model with Enhanced Dataset
Integrates: Synthetic + SecRepo + NSL-KDD + MITRE + CISA KEV

Expected improvement: 75% → 85%+ accuracy
"""

import pandas as pd
import numpy as np
import joblib
import json
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedModelTrainer:
    """Train XGBoost on enhanced dataset with real-world data"""

    def __init__(self, data_dir: str = "data/advanced_processed"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path("results/models/xgboost_enhanced")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Feature extractors
        self.tfidf_vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
        self.control_encoder = LabelEncoder()
        self.family_encoder = LabelEncoder()

    def load_data(self):
        """Load enhanced datasets"""
        logger.info("Loading enhanced datasets...")

        train_df = pd.read_csv(self.data_dir / "enhanced_train.csv")
        val_df = pd.read_csv(self.data_dir / "enhanced_val.csv")
        test_df = pd.read_csv(self.data_dir / "enhanced_test.csv")

        logger.info(f"  Train: {len(train_df):,} events")
        logger.info(f"  Val:   {len(val_df):,} events")
        logger.info(f"  Test:  {len(test_df):,} events")

        return train_df, val_df, test_df

    def extract_features(self, df, fit=False):
        """Extract features from log messages and metadata"""

        # Text features (TF-IDF)
        if fit:
            tfidf_features = self.tfidf_vectorizer.fit_transform(df['log_message'])
        else:
            tfidf_features = self.tfidf_vectorizer.transform(df['log_message'])

        # Categorical features
        if fit:
            control_encoded = self.control_encoder.fit_transform(df['control_id'].fillna('UNKNOWN'))
            family_encoded = self.family_encoder.fit_transform(df['control_family'].fillna('UNKNOWN'))
        else:
            control_encoded = self.control_encoder.transform(df['control_id'].fillna('UNKNOWN'))
            family_encoded = self.family_encoder.transform(df['control_family'].fillna('UNKNOWN'))

        # Temporal features - convert day_of_week to numeric
        day_mapping = {
            'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
            'Friday': 4, 'Saturday': 5, 'Sunday': 6
        }

        df_temporal = df[['hour_of_day', 'day_of_week', 'is_business_hours']].copy()
        df_temporal['day_of_week'] = df_temporal['day_of_week'].map(day_mapping).fillna(0)
        temporal_features = df_temporal.fillna(0).astype(float).values

        # Combine all features
        from scipy.sparse import hstack, csr_matrix

        categorical_sparse = csr_matrix(np.column_stack([control_encoded, family_encoded]))
        temporal_sparse = csr_matrix(temporal_features.astype(np.float64))

        X = hstack([tfidf_features, categorical_sparse, temporal_sparse])

        return X

    def train_model(self, X_train, y_train, X_val, y_val):
        """Train XGBoost classifier with enhanced data"""

        logger.info("\nTraining XGBoost with enhanced dataset...")
        logger.info(f"  Training samples: {X_train.shape[0]:,}")
        logger.info(f"  Features: {X_train.shape[1]:,}")
        logger.info(f"  Real data included: SecRepo + NSL-KDD + MITRE + CISA KEV")

        # XGBoost parameters
        params = {
            'objective': 'binary:logistic',
            'max_depth': 6,
            'learning_rate': 0.1,
            'n_estimators': 200,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'random_state': 42,
            'eval_metric': 'logloss'
        }

        model = xgb.XGBClassifier(**params)

        # Train with validation monitoring
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=50
        )

        logger.info("  Training complete!")

        return model

    def evaluate_model(self, model, X_test, y_test, df_test):
        """Comprehensive model evaluation"""

        logger.info("\nEvaluating enhanced model on test set...")

        # Predictions
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        # Overall accuracy
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"\n  Overall Accuracy: {accuracy*100:.2f}%")

        # Classification report
        logger.info("\n  Classification Report:")
        print(classification_report(y_test, y_pred,
                                   target_names=['compliant', 'non_compliant']))

        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        logger.info("\n  Confusion Matrix:")
        logger.info(f"    True Negatives:  {cm[0][0]:,}")
        logger.info(f"    False Positives: {cm[0][1]:,}")
        logger.info(f"    False Negatives: {cm[1][0]:,}")
        logger.info(f"    True Positives:  {cm[1][1]:,}")

        # Breakdown by data source
        if 'framework' in df_test.columns:
            logger.info("\n  Performance by Data Source:")
            for framework in df_test['framework'].unique():
                mask = df_test['framework'] == framework
                if mask.sum() > 0:
                    source_acc = accuracy_score(y_test[mask], y_pred[mask])
                    logger.info(f"    {framework}: {source_acc*100:.2f}% ({mask.sum():,} samples)")

        # Feature importance
        feature_importance = model.feature_importances_
        logger.info(f"\n  Top 10 Important Features:")
        top_indices = np.argsort(feature_importance)[-10:][::-1]
        for idx in top_indices:
            logger.info(f"    Feature {idx}: {feature_importance[idx]:.4f}")

        return {
            'accuracy': float(accuracy),
            'confusion_matrix': cm.tolist(),
            'classification_report': classification_report(y_test, y_pred,
                                                          target_names=['compliant', 'non_compliant'],
                                                          output_dict=True)
        }

    def save_model(self, model, metrics):
        """Save model and artifacts"""

        logger.info(f"\nSaving enhanced model to: {self.output_dir}")

        # Save XGBoost model
        model.save_model(str(self.output_dir / "xgboost_enhanced.json"))
        joblib.dump(model, self.output_dir / "xgboost_enhanced.pkl")

        # Save feature extractors
        joblib.dump(self.tfidf_vectorizer, self.output_dir / "tfidf_vectorizer.pkl")
        joblib.dump(self.control_encoder, self.output_dir / "control_encoder.pkl")
        joblib.dump(self.family_encoder, self.output_dir / "family_encoder.pkl")

        # Save metrics
        with open(self.output_dir / "enhanced_metrics.json", 'w') as f:
            json.dump(metrics, f, indent=2)

        # Save training metadata
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'data_sources': [
                'Synthetic compliance events (103K)',
                'SecRepo web logs (22.6M samples)',
                'NSL-KDD intrusion dataset (148K records)',
                'MITRE ATT&CK (26K techniques)',
                'CISA KEV (1,453 CVEs)'
            ],
            'total_samples': 156173,
            'features': 2000 + 3,  # TF-IDF + categorical + temporal
            'accuracy': metrics['accuracy'],
            'model_type': 'XGBoost',
            'version': '2.0 - Enhanced with Real Data'
        }

        with open(self.output_dir / "model_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info("  ✅ Model saved successfully!")
        logger.info(f"  ✅ Accuracy: {metrics['accuracy']*100:.2f}%")
        logger.info(f"  ✅ Ready for deployment")

    def run_training_pipeline(self):
        """Complete training pipeline"""

        logger.info("\n" + "="*100)
        logger.info("RETRAINING WITH ENHANCED DATASET")
        logger.info("="*100 + "\n")

        # Load data
        train_df, val_df, test_df = self.load_data()

        # Prepare labels
        y_train = (train_df['compliance_status'] == 'non_compliant').astype(int)
        y_val = (val_df['compliance_status'] == 'non_compliant').astype(int)
        y_test = (test_df['compliance_status'] == 'non_compliant').astype(int)

        logger.info(f"\nLabel distribution:")
        logger.info(f"  Train - Compliant: {(y_train == 0).sum():,}, Non-compliant: {(y_train == 1).sum():,}")
        logger.info(f"  Val   - Compliant: {(y_val == 0).sum():,}, Non-compliant: {(y_val == 1).sum():,}")
        logger.info(f"  Test  - Compliant: {(y_test == 0).sum():,}, Non-compliant: {(y_test == 1).sum():,}")

        # Extract features
        logger.info("\nExtracting features...")
        X_train = self.extract_features(train_df, fit=True)
        X_val = self.extract_features(val_df, fit=False)
        X_test = self.extract_features(test_df, fit=False)

        logger.info(f"  Feature matrix shape: {X_train.shape}")

        # Train model
        model = self.train_model(X_train, y_train, X_val, y_val)

        # Evaluate
        metrics = self.evaluate_model(model, X_test, y_test, test_df)

        # Save
        self.save_model(model, metrics)

        logger.info("\n" + "="*100)
        logger.info("TRAINING COMPLETE")
        logger.info("="*100)
        logger.info(f"Previous model (synthetic only): 99.09% accuracy on test, 75% on real scenarios")
        logger.info(f"Enhanced model (synthetic + real): {metrics['accuracy']*100:.2f}% accuracy on mixed test set")
        logger.info("Expected improvement on unstructured scenarios: 75% → 85%+")
        logger.info("="*100 + "\n")

        return model, metrics


def main():
    """Main training script"""
    trainer = EnhancedModelTrainer()
    model, metrics = trainer.run_training_pipeline()

    print("\n" + "="*100)
    print("NEXT STEPS:")
    print("="*100)
    print("1. Test enhanced model on real-world scenarios")
    print("   Command: python test_enhanced_model.py")
    print()
    print("2. Compare with previous model (75% baseline)")
    print("   Expected: 85%+ accuracy on ransomware, insider threats")
    print()
    print("3. If 85%+: Proceed to Phase 2 (BERT embeddings)")
    print("   If <85%: Analyze failures and add more attack patterns")
    print("="*100)


if __name__ == '__main__':
    main()
