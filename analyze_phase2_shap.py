#!/usr/bin/env python3
"""
SHAP Analysis for Phase 2 Model - Debug Feature Bias

Analyzes which features cause the "compliant" bias for sophisticated attacks.
Focuses on the 5 failed scenarios:
1. Phishing Email
2. Insider Threat
3. Lateral Movement
4. DDoS Attack
5. Credential Stuffing
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.sparse import hstack, csr_matrix
import logging
import sys
import shap
import matplotlib.pyplot as plt

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.bert_feature_extractor import BERTFeatureExtractor
from models.temporal_feature_extractor import TemporalFeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase2SHAPAnalyzer:
    """Analyze Phase 2 model feature importance with SHAP"""

    def __init__(self, model_dir: str = "results/models/xgboost_phase2"):
        self.model_dir = Path(model_dir)
        self.output_dir = Path("results/shap_analysis_phase2")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Loading Phase 2 model...")
        self.model = joblib.load(self.model_dir / "xgboost_phase2.pkl")
        self.tfidf_vectorizer = joblib.load(self.model_dir / "tfidf_vectorizer.pkl")
        self.control_encoder = joblib.load(self.model_dir / "control_encoder.pkl")
        self.family_encoder = joblib.load(self.model_dir / "family_encoder.pkl")

        # Initialize feature extractors
        self.bert_extractor = BERTFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()

        # Feature names
        self.tfidf_names = self.tfidf_vectorizer.get_feature_names_out().tolist()
        self.categorical_names = ['control_id', 'control_family']
        self.temporal_names = [
            'hour', 'minute', 'day_of_week', 'day_of_month', 'month',
            'is_weekend', 'is_business_hours', 'is_late_night', 'is_unusual_time',
            'events_last_5min', 'failed_attempts_last_5min',
            'unique_ips_last_5min', 'unique_users_last_5min', 'rapid_succession',
            'large_transfer', 'usb_access', 'sensitive_data',
            'multiple_connections', 'smb_rdp_ssh', 'high_volume',
            'spike_traffic', 'credential_related', 'multiple_ips',
            'encryption_activity', 'file_modification', 'anomaly_score'
        ]
        self.bert_names = [f'bert_{i}' for i in range(768)]

        self.all_feature_names = (
            self.tfidf_names +
            self.categorical_names +
            self.temporal_names +
            self.bert_names
        )

        logger.info(f"Total features: {len(self.all_feature_names)}")

    def extract_features(self, log_message, control_id='SI-4',
                        control_family='System and Information Integrity'):
        """Extract all features for a log message"""

        # 1. TF-IDF
        tfidf_features = self.tfidf_vectorizer.transform([log_message])

        # 2. Categorical
        try:
            control_encoded = self.control_encoder.transform([control_id])
        except:
            control_encoded = np.array([0])

        try:
            family_encoded = self.family_encoder.transform([control_family])
        except:
            family_encoded = np.array([0])

        # 3. Temporal features
        from datetime import datetime
        df_temp = pd.DataFrame({
            'log_message': [log_message],
            'timestamp': [datetime.now()],
            'user_id': ['unknown'],
            'action': ['unknown'],
            'resource': ['unknown'],
            'source_ip': ['0.0.0.0'],
            'destination_ip': ['0.0.0.0']
        })

        df_enhanced = self.temporal_extractor.extract_all_temporal_features(df_temp)

        temporal_values = []
        for col in self.temporal_names:
            if col in df_enhanced.columns:
                val = df_enhanced[col].iloc[0]
                if col == 'day_of_week' and isinstance(val, str):
                    day_mapping = {
                        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                        'Friday': 4, 'Saturday': 5, 'Sunday': 6
                    }
                    val = day_mapping.get(val, 0)
                temporal_values.append(float(val) if pd.notna(val) else 0.0)
            else:
                temporal_values.append(0.0)

        temporal_features = np.array([temporal_values])

        # 4. BERT embeddings
        bert_embeddings = self.bert_extractor.extract_embeddings([log_message])

        # Combine
        categorical_sparse = csr_matrix(np.column_stack([control_encoded, family_encoded]))
        temporal_sparse = csr_matrix(temporal_features)
        bert_sparse = csr_matrix(bert_embeddings)

        X = hstack([tfidf_features, categorical_sparse, temporal_sparse, bert_sparse])

        return X

    def analyze_scenario(self, scenario_name, log_message, control_id, control_family):
        """Analyze a single scenario with SHAP"""

        logger.info(f"\n{'='*80}")
        logger.info(f"Analyzing: {scenario_name}")
        logger.info(f"{'='*80}")

        # Extract features
        X = self.extract_features(log_message, control_id, control_family)

        # Get prediction
        prediction = self.model.predict(X)[0]
        probability = self.model.predict_proba(X)[0]
        status = 'non_compliant' if prediction == 1 else 'compliant'
        confidence = probability[1] if prediction == 1 else probability[0]

        logger.info(f"Prediction: {status} ({confidence*100:.1f}% confidence)")

        # Convert to dense for SHAP
        X_dense = X.toarray()

        # Create SHAP explainer (use TreeExplainer for XGBoost)
        logger.info("Computing SHAP values...")
        explainer = shap.TreeExplainer(self.model)
        shap_values = explainer.shap_values(X_dense)

        # Get base value
        base_value = explainer.expected_value

        logger.info(f"Base value (expected): {base_value:.4f}")

        # Analyze top features pushing toward compliant (class 0)
        # For binary classification, shap_values is for class 1 (non_compliant)
        # Negative values push toward compliant, positive toward non_compliant

        shap_for_sample = shap_values[0]

        # Get feature contributions
        feature_contributions = list(zip(self.all_feature_names, shap_for_sample, X_dense[0]))

        # Sort by SHAP value (most negative = pushing toward compliant)
        sorted_contributions = sorted(feature_contributions, key=lambda x: x[1])

        # Top 20 features pushing toward COMPLIANT (negative SHAP)
        logger.info("\n" + "="*80)
        logger.info("TOP 20 FEATURES PUSHING TOWARD 'COMPLIANT' (negative SHAP):")
        logger.info("="*80)
        for i, (name, shap_val, feat_val) in enumerate(sorted_contributions[:20], 1):
            logger.info(f"{i:2d}. {name:40s} SHAP: {shap_val:+.4f}  Value: {feat_val:.4f}")

        # Top 20 features pushing toward NON_COMPLIANT (positive SHAP)
        logger.info("\n" + "="*80)
        logger.info("TOP 20 FEATURES PUSHING TOWARD 'NON_COMPLIANT' (positive SHAP):")
        logger.info("="*80)
        sorted_contributions_positive = sorted(feature_contributions, key=lambda x: x[1], reverse=True)
        for i, (name, shap_val, feat_val) in enumerate(sorted_contributions_positive[:20], 1):
            logger.info(f"{i:2d}. {name:40s} SHAP: {shap_val:+.4f}  Value: {feat_val:.4f}")

        # Breakdown by feature type
        logger.info("\n" + "="*80)
        logger.info("SHAP VALUE BREAKDOWN BY FEATURE TYPE:")
        logger.info("="*80)

        tfidf_shap = shap_for_sample[:2000]
        categorical_shap = shap_for_sample[2000:2002]
        temporal_shap = shap_for_sample[2002:2028]
        bert_shap = shap_for_sample[2028:]

        logger.info(f"TF-IDF total contribution:      {tfidf_shap.sum():+.4f}")
        logger.info(f"Categorical total contribution: {categorical_shap.sum():+.4f}")
        logger.info(f"Temporal total contribution:    {temporal_shap.sum():+.4f}")
        logger.info(f"BERT total contribution:        {bert_shap.sum():+.4f}")
        logger.info(f"Overall prediction shift:       {shap_for_sample.sum():+.4f}")
        logger.info(f"Final prediction: {base_value + shap_for_sample.sum():.4f}")

        # Determine if BERT is the culprit
        if bert_shap.sum() < -0.5 and prediction == 0:
            logger.info("\n⚠️  BERT IS STRONGLY PUSHING TOWARD COMPLIANT!")
            logger.info(f"   BERT contribution: {bert_shap.sum():.4f} (negative = toward compliant)")

        if temporal_shap.sum() < -0.3 and prediction == 0:
            logger.info("\n⚠️  TEMPORAL FEATURES PUSHING TOWARD COMPLIANT!")
            logger.info(f"   Temporal contribution: {temporal_shap.sum():.4f}")

        # Save detailed results
        results = {
            'scenario': scenario_name,
            'prediction': status,
            'confidence': float(confidence),
            'base_value': float(base_value),
            'tfidf_contribution': float(tfidf_shap.sum()),
            'categorical_contribution': float(categorical_shap.sum()),
            'temporal_contribution': float(temporal_shap.sum()),
            'bert_contribution': float(bert_shap.sum()),
            'total_shift': float(shap_for_sample.sum()),
            'final_prediction_value': float(base_value + shap_for_sample.sum()),
            'top_20_toward_compliant': [
                {'feature': name, 'shap': float(shap_val), 'value': float(feat_val)}
                for name, shap_val, feat_val in sorted_contributions[:20]
            ],
            'top_20_toward_noncompliant': [
                {'feature': name, 'shap': float(shap_val), 'value': float(feat_val)}
                for name, shap_val, feat_val in sorted_contributions_positive[:20]
            ]
        }

        return results, shap_values, X_dense

    def analyze_failed_scenarios(self):
        """Analyze all 5 failed scenarios"""

        failed_scenarios = [
            {
                'name': 'Phishing Email',
                'log': 'Email from unknown@suspicious-domain.ru blocked - Contains malicious link',
                'control': 'SI-8',
                'family': 'System and Information Integrity',
                'expected': 'non_compliant'
            },
            {
                'name': 'Insider Threat - Data Exfiltration',
                'log': 'Employee downloaded 50GB sensitive data to USB at 2am on Saturday',
                'control': 'AC-3',
                'family': 'Access Control',
                'expected': 'non_compliant'
            },
            {
                'name': 'Lateral Movement',
                'log': 'Suspicious SMB connections from workstation-05 to 20 servers in 2 minutes',
                'control': 'AC-3',
                'family': 'Access Control',
                'expected': 'non_compliant'
            },
            {
                'name': 'DDoS Attack',
                'log': 'Network traffic spike: 100,000 requests/sec from 500 IPs - Service degradation',
                'control': 'SC-5',
                'family': 'System and Communications Protection',
                'expected': 'non_compliant'
            },
            {
                'name': 'Credential Stuffing',
                'log': 'Login attempts from 200 IPs using stolen credentials - 50 accounts compromised',
                'control': 'IA-2',
                'family': 'Identification and Authentication',
                'expected': 'non_compliant'
            }
        ]

        all_results = []

        for scenario in failed_scenarios:
            results, shap_values, X_dense = self.analyze_scenario(
                scenario['name'],
                scenario['log'],
                scenario['control'],
                scenario['family']
            )
            all_results.append(results)

        # Summary analysis
        logger.info("\n\n" + "="*80)
        logger.info("SUMMARY: FEATURE TYPE CONTRIBUTIONS ACROSS ALL FAILED SCENARIOS")
        logger.info("="*80)

        summary_df = pd.DataFrame([
            {
                'Scenario': r['scenario'],
                'Prediction': r['prediction'],
                'TF-IDF': r['tfidf_contribution'],
                'Categorical': r['categorical_contribution'],
                'Temporal': r['temporal_contribution'],
                'BERT': r['bert_contribution'],
                'Total': r['total_shift']
            }
            for r in all_results
        ])

        logger.info("\n" + str(summary_df.to_string(index=False)))

        # Identify the main culprit
        logger.info("\n" + "="*80)
        logger.info("DIAGNOSIS:")
        logger.info("="*80)

        avg_bert = summary_df['BERT'].mean()
        avg_temporal = summary_df['Temporal'].mean()
        avg_tfidf = summary_df['TF-IDF'].mean()

        logger.info(f"Average BERT contribution:      {avg_bert:+.4f}")
        logger.info(f"Average Temporal contribution:  {avg_temporal:+.4f}")
        logger.info(f"Average TF-IDF contribution:    {avg_tfidf:+.4f}")

        if avg_bert < -0.5:
            logger.info("\n🔴 PRIMARY CULPRIT: BERT EMBEDDINGS")
            logger.info(f"   BERT is pushing predictions toward compliant (avg: {avg_bert:.4f})")
            logger.info("   RECOMMENDATION: Remove BERT or use security-specific BERT (SecBERT)")

        if avg_temporal < -0.3:
            logger.info("\n🟡 SECONDARY CULPRIT: TEMPORAL FEATURES")
            logger.info(f"   Temporal features contributing to bias (avg: {avg_temporal:.4f})")
            logger.info("   RECOMMENDATION: Remove or re-engineer temporal features")

        if avg_tfidf > 0.3:
            logger.info("\n🟢 TF-IDF IS WORKING CORRECTLY")
            logger.info(f"   TF-IDF pushing toward non_compliant (avg: {avg_tfidf:.4f})")
            logger.info("   TF-IDF features are detecting attack keywords properly")

        # Save summary
        summary_df.to_csv(self.output_dir / 'failed_scenarios_shap_summary.csv', index=False)

        import json
        with open(self.output_dir / 'detailed_shap_analysis.json', 'w') as f:
            json.dump(all_results, f, indent=2)

        logger.info(f"\n✅ Results saved to: {self.output_dir}")

        return all_results


def main():
    """Main analysis script"""
    analyzer = Phase2SHAPAnalyzer()

    logger.info("\n" + "="*80)
    logger.info("PHASE 2 SHAP ANALYSIS - DEBUGGING 'COMPLIANT' BIAS")
    logger.info("="*80)
    logger.info("Analyzing 5 failed scenarios to identify feature bias...")
    logger.info("")

    results = analyzer.analyze_failed_scenarios()

    logger.info("\n" + "="*80)
    logger.info("SHAP ANALYSIS COMPLETE")
    logger.info("="*80)
    logger.info("Check results/shap_analysis_phase2/ for detailed outputs")
    logger.info("")
    logger.info("Next steps:")
    logger.info("1. Review feature contributions above")
    logger.info("2. Run feature ablation tests: python feature_ablation.py")
    logger.info("3. Try without BERT: python train_phase2_ensemble.py --no-bert")
    logger.info("="*80)


if __name__ == '__main__':
    main()
