#!/usr/bin/env python3
"""
Phase 2.5 Training - XGBoost + BERT + Temporal + Targeted Datasets

Improvements over Phase 2:
- 114K training samples (+29% from 88K)
- 37K targeted attack samples added:
  * 15K phishing emails
  * 8K insider threats
  * 7K DDoS attacks
  * 7K credential stuffing attacks

Target: Fix Phase 2's "compliant bias" and achieve 85-90%+ on real scenarios
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
from scipy.sparse import hstack, csr_matrix
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase25Trainer:
    """Train Phase 2.5 model with targeted datasets"""

    def __init__(self,
                 data_dir: str = "data/integrated_targeted",
                 bert_dir: str = "data/bert_embeddings_integrated",
                 output_dir: str = "results/models/xgboost_phase2_5"):
        self.data_dir = Path(data_dir)
        self.bert_dir = Path(bert_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Feature extractors
        self.tfidf_vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1, 2))
        self.control_encoder = LabelEncoder()
        self.family_encoder = LabelEncoder()

        # Temporal feature names
        self.temporal_features = [
            'hour', 'minute', 'day_of_week', 'day_of_month', 'month',
            'is_weekend', 'is_business_hours', 'is_late_night', 'is_unusual_time',
            'events_last_5min', 'failed_attempts_last_5min',
            'unique_ips_last_5min', 'unique_users_last_5min', 'rapid_succession',
            'large_transfer', 'usb_access', 'sensitive_data',
            'multiple_connections', 'smb_rdp_ssh', 'high_volume',
            'spike_traffic', 'credential_related', 'multiple_ips',
            'encryption_activity', 'file_modification', 'anomaly_score'
        ]

    def load_data(self):
        """Load integrated datasets"""
        logger.info("Loading integrated datasets...")

        train_df = pd.read_csv(self.data_dir / "train_integrated.csv")
        val_df = pd.read_csv(self.data_dir / "val_integrated.csv")
        test_df = pd.read_csv(self.data_dir / "test_integrated.csv")

        logger.info(f"  Train: {len(train_df):,} events (+{len(train_df) - 88321:,} from Phase 2)")
        logger.info(f"  Val:   {len(val_df):,} events")
        logger.info(f"  Test:  {len(test_df):,} events")

        return train_df, val_df, test_df

    def load_bert_embeddings(self):
        """Load pre-computed BERT embeddings"""
        logger.info("Loading BERT embeddings...")

        try:
            train_bert = np.load(self.bert_dir / "train_bert_embeddings.npy")
            val_bert = np.load(self.bert_dir / "val_bert_embeddings.npy")
            test_bert = np.load(self.bert_dir / "test_bert_embeddings.npy")

            logger.info(f"  Train BERT: {train_bert.shape}")
            logger.info(f"  Val BERT:   {val_bert.shape}")
            logger.info(f"  Test BERT:  {test_bert.shape}")

            return train_bert, val_bert, test_bert

        except FileNotFoundError as e:
            logger.error(f"BERT embeddings not found: {e}")
            logger.error("Run: python generate_bert_integrated.py first")
            raise

    def extract_features(self, df, bert_embeddings=None, fit=False):
        """Extract all features: TF-IDF + BERT + Temporal + Metadata"""

        logger.info(f"Extracting features (fit={fit})...")

        # 1. TF-IDF features
        if fit:
            tfidf_features = self.tfidf_vectorizer.fit_transform(df['log_message'])
        else:
            tfidf_features = self.tfidf_vectorizer.transform(df['log_message'])
        logger.info(f"  TF-IDF: {tfidf_features.shape}")

        # 2. Categorical features
        if fit:
            control_encoded = self.control_encoder.fit_transform(df['control_id'].fillna('UNKNOWN'))
            family_encoded = self.family_encoder.fit_transform(df['control_family'].fillna('UNKNOWN'))
        else:
            control_encoded = self.control_encoder.transform(df['control_id'].fillna('UNKNOWN'))
            family_encoded = self.family_encoder.transform(df['control_family'].fillna('UNKNOWN'))

        # 3. Temporal features
        temporal_cols = [c for c in self.temporal_features if c in df.columns]
        if temporal_cols:
            df_temp = df[temporal_cols].copy()
            if 'day_of_week' in df_temp.columns and df_temp['day_of_week'].dtype == 'object':
                day_mapping = {
                    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                    'Friday': 4, 'Saturday': 5, 'Sunday': 6
                }
                df_temp['day_of_week'] = df_temp['day_of_week'].map(day_mapping).fillna(0)

            if 'time_of_day' in df_temp.columns:
                time_mapping = {'night': 0, 'morning': 1, 'afternoon': 2, 'evening': 3}
                df_temp['time_of_day'] = df_temp['time_of_day'].map(time_mapping).fillna(1)

            temporal_features = df_temp.fillna(0).astype(float).values
            logger.info(f"  Temporal: {temporal_features.shape}")
        else:
            temporal_features = np.zeros((len(df), len(self.temporal_features)))
            logger.warning("  No temporal features found, using zeros")

        # Combine features
        categorical_sparse = csr_matrix(np.column_stack([control_encoded, family_encoded]))
        temporal_sparse = csr_matrix(temporal_features)

        features_to_combine = [tfidf_features, categorical_sparse, temporal_sparse]

        # 4. BERT embeddings
        if bert_embeddings is not None:
            bert_sparse = csr_matrix(bert_embeddings)
            features_to_combine.append(bert_sparse)
            logger.info(f"  BERT: {bert_embeddings.shape}")
        else:
            logger.warning("  No BERT embeddings - training without semantic features")

        X = hstack(features_to_combine)
        logger.info(f"  Combined: {X.shape}")

        return X

    def train_model(self, X_train, y_train, X_val, y_val):
        """Train XGBoost with enhanced features"""

        logger.info("\nTraining Phase 2.5 Model...")
        logger.info(f"  Training samples: {X_train.shape[0]:,} (+{X_train.shape[0] - 88321:,} from Phase 2)")
        logger.info(f"  Total features: {X_train.shape[1]:,}")
        logger.info(f"    - TF-IDF: 2,000")
        logger.info(f"    - Categorical: 2")
        logger.info(f"    - Temporal: {len(self.temporal_features)}")
        logger.info(f"    - BERT: 768")

        # XGBoost parameters (same as Phase 2)
        params = {
            'objective': 'binary:logistic',
            'max_depth': 8,
            'learning_rate': 0.05,
            'n_estimators': 300,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'min_child_weight': 3,
            'gamma': 0.1,
            'random_state': 42,
            'eval_metric': 'logloss',
            'tree_method': 'hist',
            'enable_categorical': False
        }

        model = xgb.XGBClassifier(**params)

        logger.info("\n  Training in progress...")
        model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=50
        )

        logger.info("  ✅ Training complete!")

        return model

    def evaluate_model(self, model, X_test, y_test, df_test):
        """Comprehensive evaluation"""

        logger.info("\nEvaluating Phase 2.5 model...")

        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1]

        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"\n  Overall Accuracy: {accuracy*100:.2f}%")

        logger.info("\n  Classification Report:")
        print(classification_report(y_test, y_pred,
                                   target_names=['compliant', 'non_compliant']))

        cm = confusion_matrix(y_test, y_pred)
        logger.info("\n  Confusion Matrix:")
        logger.info(f"    True Negatives:  {cm[0][0]:,}")
        logger.info(f"    False Positives: {cm[0][1]:,}")
        logger.info(f"    False Negatives: {cm[1][0]:,}")
        logger.info(f"    True Positives:  {cm[1][1]:,}")

        # Breakdown by data source
        if 'dataset_source' in df_test.columns:
            logger.info("\n  Performance by Dataset Source:")
            for source in df_test['dataset_source'].unique():
                if pd.notna(source):
                    mask = df_test['dataset_source'] == source
                    if mask.sum() > 0:
                        source_acc = accuracy_score(y_test[mask], y_pred[mask])
                        logger.info(f"    {source}: {source_acc*100:.2f}% ({mask.sum():,} samples)")

        # Feature importance
        feature_importance = model.feature_importances_
        logger.info(f"\n  Top 20 Important Features:")
        top_indices = np.argsort(feature_importance)[-20:][::-1]
        for rank, idx in enumerate(top_indices, 1):
            logger.info(f"    {rank}. Feature {idx}: {feature_importance[idx]:.4f}")

        return {
            'accuracy': float(accuracy),
            'confusion_matrix': cm.tolist(),
            'classification_report': classification_report(y_test, y_pred,
                                                          target_names=['compliant', 'non_compliant'],
                                                          output_dict=True)
        }

    def save_model(self, model, metrics):
        """Save Phase 2.5 model"""

        logger.info(f"\nSaving Phase 2.5 model to: {self.output_dir}")

        model.save_model(str(self.output_dir / "xgboost_phase2_5.json"))
        joblib.dump(model, self.output_dir / "xgboost_phase2_5.pkl")

        joblib.dump(self.tfidf_vectorizer, self.output_dir / "tfidf_vectorizer.pkl")
        joblib.dump(self.control_encoder, self.output_dir / "control_encoder.pkl")
        joblib.dump(self.family_encoder, self.output_dir / "family_encoder.pkl")

        with open(self.output_dir / "phase2_5_metrics.json", 'w') as f:
            json.dump(metrics, f, indent=2)

        metadata = {
            'trained_at': datetime.now().isoformat(),
            'phase': '2.5 - With Targeted Datasets',
            'data_sources': [
                'Original Phase 2 (88K)',
                'Phishing emails (15K)',
                'Insider threats (8K)',
                'DDoS attacks (7K)',
                'Credential stuffing (7K)'
            ],
            'total_samples': 114221,
            'targeted_samples_added': 37000,
            'features': {
                'tfidf': 2000,
                'categorical': 2,
                'temporal': len(self.temporal_features),
                'bert': 768,
                'total': 2796
            },
            'accuracy': metrics['accuracy'],
            'model_type': 'XGBoost with BERT + Temporal + Targeted Data',
            'version': '2.5 - Targeted Dataset Integration',
            'improvements': 'Added 37K targeted attack samples to fix Phase 2 bias'
        }

        with open(self.output_dir / "model_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        logger.info("  ✅ Model saved successfully!")
        logger.info(f"  ✅ Accuracy: {metrics['accuracy']*100:.2f}%")

    def run_training_pipeline(self):
        """Complete Phase 2.5 training pipeline"""

        logger.info("\n" + "="*100)
        logger.info("PHASE 2.5 TRAINING: BERT + TEMPORAL + TARGETED DATASETS")
        logger.info("="*100 + "\n")

        # Load data
        train_df, val_df, test_df = self.load_data()

        # Load BERT embeddings
        train_bert, val_bert, test_bert = self.load_bert_embeddings()

        # Prepare labels
        y_train = (train_df['compliance_status'] == 'non_compliant').astype(int)
        y_val = (val_df['compliance_status'] == 'non_compliant').astype(int)
        y_test = (test_df['compliance_status'] == 'non_compliant').astype(int)

        logger.info(f"\nLabel distribution:")
        logger.info(f"  Train - Compliant: {(y_train == 0).sum():,}, Non-compliant: {(y_train == 1).sum():,}")
        logger.info(f"  Val   - Compliant: {(y_val == 0).sum():,}, Non-compliant: {(y_val == 1).sum():,}")
        logger.info(f"  Test  - Compliant: {(y_test == 0).sum():,}, Non-compliant: {(y_test == 1).sum():,}")

        # Extract features
        logger.info("\nExtracting all features...")
        X_train = self.extract_features(train_df, train_bert, fit=True)
        X_val = self.extract_features(val_df, val_bert, fit=False)
        X_test = self.extract_features(test_df, test_bert, fit=False)

        # Train
        model = self.train_model(X_train, y_train, X_val, y_val)

        # Evaluate
        metrics = self.evaluate_model(model, X_test, y_test, test_df)

        # Save
        self.save_model(model, metrics)

        logger.info("\n" + "="*100)
        logger.info("PHASE 2.5 TRAINING COMPLETE")
        logger.info("="*100)
        logger.info(f"Phase 1 (Real Data): 87.5% on real scenarios")
        logger.info(f"Phase 2 (BERT + Temporal): 58.3% on real scenarios")
        logger.info(f"Phase 2.5 (+ Targeted Data): {metrics['accuracy']*100:.2f}% on test set")
        logger.info("Expected on real scenarios: 80-90%")
        logger.info("="*100 + "\n")

        return model, metrics


def main():
    """Main training script"""
    trainer = Phase25Trainer()
    model, metrics = trainer.run_training_pipeline()

    print("\n" + "="*100)
    print("NEXT STEPS:")
    print("="*100)
    print("1. Test Phase 2.5 model on 12 real-world scenarios")
    print("   Command: python test_phase2_5.py")
    print()
    print("2. Compare Phase 2 vs Phase 2.5 results:")
    print("   - Phase 2: 58.3% (7/12 scenarios)")
    print("   - Phase 2.5: Expected 80-90% (10-11/12 scenarios)")
    print()
    print("3. If 85%+: Excellent improvement!")
    print("   If 75-85%: Good progress, consider feature ablation")
    print("   If <75%: BERT bias still present, try without BERT")
    print("="*100)


if __name__ == '__main__':
    main()
