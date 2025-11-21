#!/usr/bin/env python3
"""
Side-by-Side Comparison: Phase 2 vs Phase 2.5

Tests both models on identical scenarios to verify:
1. Phase 2 results are reproducible
2. Phase 2.5 improvements are genuine
3. Metrics are consistent
"""

import pandas as pd
import numpy as np
import joblib
import logging
from pathlib import Path
from scipy.sparse import hstack, csr_matrix
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.bert_feature_extractor import BERTFeatureExtractor
from models.temporal_feature_extractor import TemporalFeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelComparator:
    """Compare Phase 2 and Phase 2.5 models side-by-side"""

    def __init__(self):
        # Initialize feature extractors (shared by both models)
        logger.info("Initializing feature extractors...")
        self.bert_extractor = BERTFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()

        # Load Phase 2 model
        logger.info("\nLoading Phase 2 model...")
        phase2_dir = Path("results/models/xgboost_phase2")
        try:
            self.phase2_model = joblib.load(phase2_dir / "xgboost_phase2.pkl")
            self.phase2_tfidf = joblib.load(phase2_dir / "tfidf_vectorizer.pkl")
            self.phase2_control_enc = joblib.load(phase2_dir / "control_encoder.pkl")
            self.phase2_family_enc = joblib.load(phase2_dir / "family_encoder.pkl")
            logger.info("  ✅ Phase 2 model loaded")
        except FileNotFoundError:
            logger.error("  ❌ Phase 2 model not found")
            self.phase2_model = None

        # Load Phase 2.5 model
        logger.info("\nLoading Phase 2.5 model...")
        phase25_dir = Path("results/models/xgboost_phase2_5")
        try:
            self.phase25_model = joblib.load(phase25_dir / "xgboost_phase2_5.pkl")
            self.phase25_tfidf = joblib.load(phase25_dir / "tfidf_vectorizer.pkl")
            self.phase25_control_enc = joblib.load(phase25_dir / "control_encoder.pkl")
            self.phase25_family_enc = joblib.load(phase25_dir / "family_encoder.pkl")
            logger.info("  ✅ Phase 2.5 model loaded")
        except FileNotFoundError:
            logger.error("  ❌ Phase 2.5 model not found")
            self.phase25_model = None

    def extract_features(self, log_message, control_id, control_family, model_type='phase2'):
        """Extract features for specified model"""

        # Select vectorizers based on model type
        if model_type == 'phase2':
            tfidf_vectorizer = self.phase2_tfidf
            control_encoder = self.phase2_control_enc
            family_encoder = self.phase2_family_enc
        else:
            tfidf_vectorizer = self.phase25_tfidf
            control_encoder = self.phase25_control_enc
            family_encoder = self.phase25_family_enc

        # 1. TF-IDF
        tfidf_features = tfidf_vectorizer.transform([log_message])

        # 2. Categorical
        try:
            control_encoded = control_encoder.transform([control_id])
        except:
            control_encoded = np.array([0])

        try:
            family_encoded = family_encoder.transform([control_family])
        except:
            family_encoded = np.array([0])

        # 3. Temporal
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

        temporal_cols = [
            'hour', 'minute', 'day_of_week', 'day_of_month', 'month',
            'is_weekend', 'is_business_hours', 'is_late_night', 'is_unusual_time',
            'events_last_5min', 'failed_attempts_last_5min',
            'unique_ips_last_5min', 'unique_users_last_5min', 'rapid_succession',
            'large_transfer', 'usb_access', 'sensitive_data',
            'multiple_connections', 'smb_rdp_ssh', 'high_volume',
            'spike_traffic', 'credential_related', 'multiple_ips',
            'encryption_activity', 'file_modification', 'anomaly_score'
        ]

        temporal_values = []
        for col in temporal_cols:
            if col in df_enhanced.columns:
                val = df_enhanced[col].iloc[0]
                if col == 'day_of_week' and isinstance(val, str):
                    day_mapping = {
                        'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3,
                        'Friday': 4, 'Saturday': 5, 'Sunday': 6
                    }
                    val = day_mapping.get(val, 0)
                elif col == 'time_of_day' and isinstance(val, str):
                    time_mapping = {'night': 0, 'morning': 1, 'afternoon': 2, 'evening': 3}
                    val = time_mapping.get(val, 1)
                temporal_values.append(float(val) if pd.notna(val) else 0.0)
            else:
                temporal_values.append(0.0)

        temporal_features = np.array([temporal_values])

        # 4. BERT
        bert_embeddings = self.bert_extractor.extract_embeddings([log_message])

        # Combine
        categorical_sparse = csr_matrix(np.column_stack([control_encoded, family_encoded]))
        temporal_sparse = csr_matrix(temporal_features)
        bert_sparse = csr_matrix(bert_embeddings)

        X = hstack([tfidf_features, categorical_sparse, temporal_sparse, bert_sparse])

        return X

    def predict_both(self, log_message, control_id, control_family):
        """Get predictions from both models"""

        results = {}

        # Phase 2 prediction
        if self.phase2_model:
            X = self.extract_features(log_message, control_id, control_family, 'phase2')
            prediction = self.phase2_model.predict(X)[0]
            probability = self.phase2_model.predict_proba(X)[0]

            status = 'non_compliant' if prediction == 1 else 'compliant'
            confidence = probability[1] if prediction == 1 else probability[0]

            results['phase2'] = {
                'status': status,
                'confidence': confidence,
                'prediction': prediction,
                'probabilities': probability
            }
        else:
            results['phase2'] = None

        # Phase 2.5 prediction
        if self.phase25_model:
            X = self.extract_features(log_message, control_id, control_family, 'phase2.5')
            prediction = self.phase25_model.predict(X)[0]
            probability = self.phase25_model.predict_proba(X)[0]

            status = 'non_compliant' if prediction == 1 else 'compliant'
            confidence = probability[1] if prediction == 1 else probability[0]

            results['phase2.5'] = {
                'status': status,
                'confidence': confidence,
                'prediction': prediction,
                'probabilities': probability
            }
        else:
            results['phase2.5'] = None

        return results

    def compare_all_scenarios(self):
        """Compare both models on all 12 test scenarios"""

        logger.info("\n" + "="*120)
        logger.info("SIDE-BY-SIDE COMPARISON: PHASE 2 vs PHASE 2.5")
        logger.info("="*120 + "\n")

        test_scenarios = [
            {
                'name': 'Unauthorized SSH Access',
                'log': 'Failed SSH login attempt from 192.168.1.100 to root@10.0.0.5 - Access denied',
                'control': 'AC-3',
                'family': 'Access Control',
                'expected': 'non_compliant'
            },
            {
                'name': 'Successful Compliance Check',
                'log': 'Security audit passed: All patches applied, firewall enabled, logs encrypted',
                'control': 'SI-2',
                'family': 'System and Information Integrity',
                'expected': 'compliant'
            },
            {
                'name': 'Phishing Email Detected',
                'log': 'Email from unknown@suspicious-domain.ru blocked - Contains malicious link',
                'control': 'SI-8',
                'family': 'System and Information Integrity',
                'expected': 'non_compliant'
            },
            {
                'name': 'Unpatched Critical Vulnerability',
                'log': 'CVE-2023-12345 detected on server-prod-01 - Critical severity, no patch applied',
                'control': 'RA-5',
                'family': 'Risk Assessment',
                'expected': 'non_compliant'
            },
            {
                'name': 'Encryption Enabled',
                'log': 'All databases encrypted at rest using AES-256, key rotation completed',
                'control': 'SC-28',
                'family': 'System and Communications Protection',
                'expected': 'compliant'
            },
            {
                'name': 'Backup Failure',
                'log': 'Backup job failed for 7 consecutive days - Data loss risk',
                'control': 'CP-9',
                'family': 'Contingency Planning',
                'expected': 'non_compliant'
            },
            {
                'name': 'Ransomware Attack',
                'log': 'File encryption detected: 10,000 files encrypted with .locked extension in 5 minutes',
                'control': 'SI-4',
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
                'name': 'SQL Injection Attack',
                'log': "HTTP GET /api/users?id=1' OR '1'='1 - SQL injection attempt detected",
                'control': 'SI-4',
                'family': 'System and Information Integrity',
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

        # Track results
        phase2_passed = 0
        phase25_passed = 0
        comparison_data = []

        for i, scenario in enumerate(test_scenarios, 1):
            logger.info(f"{i}. {scenario['name']}")
            logger.info(f"   Expected: {scenario['expected']}")

            # Get predictions from both models
            results = self.predict_both(
                scenario['log'],
                scenario['control'],
                scenario['family']
            )

            # Phase 2 results
            if results['phase2']:
                p2_status = results['phase2']['status']
                p2_confidence = results['phase2']['confidence']
                p2_correct = (p2_status == scenario['expected'])

                logger.info(f"   Phase 2:   {p2_status} ({p2_confidence*100:.1f}%) {'✅' if p2_correct else '❌'}")
                if p2_correct:
                    phase2_passed += 1
            else:
                p2_status = 'N/A'
                p2_confidence = 0
                p2_correct = False
                logger.info(f"   Phase 2:   Model not available")

            # Phase 2.5 results
            if results['phase2.5']:
                p25_status = results['phase2.5']['status']
                p25_confidence = results['phase2.5']['confidence']
                p25_correct = (p25_status == scenario['expected'])

                logger.info(f"   Phase 2.5: {p25_status} ({p25_confidence*100:.1f}%) {'✅' if p25_correct else '❌'}")
                if p25_correct:
                    phase25_passed += 1
            else:
                p25_status = 'N/A'
                p25_confidence = 0
                p25_correct = False
                logger.info(f"   Phase 2.5: Model not available")

            # Improvement indicator
            if results['phase2'] and results['phase2.5']:
                if not p2_correct and p25_correct:
                    logger.info(f"   🎯 IMPROVED: Phase 2 FAILED → Phase 2.5 FIXED")
                elif p2_correct and not p25_correct:
                    logger.warning(f"   ⚠️  REGRESSION: Phase 2 PASSED → Phase 2.5 FAILED")
                elif p2_correct and p25_correct:
                    # Check confidence change
                    if abs(p25_confidence - p2_confidence) > 0.1:
                        direction = "↑" if p25_confidence > p2_confidence else "↓"
                        logger.info(f"   {direction} Confidence change: {abs(p25_confidence - p2_confidence)*100:.1f}%")

            comparison_data.append({
                'scenario': scenario['name'],
                'expected': scenario['expected'],
                'phase2_status': p2_status,
                'phase2_confidence': p2_confidence,
                'phase2_correct': p2_correct,
                'phase2.5_status': p25_status,
                'phase2.5_confidence': p25_confidence,
                'phase2.5_correct': p25_correct
            })

            print()

        # Summary
        logger.info("="*120)
        logger.info("COMPARISON SUMMARY")
        logger.info("="*120)

        total = len(test_scenarios)
        logger.info(f"\nTotal Scenarios: {total}")
        logger.info(f"Phase 2 Accuracy:   {phase2_passed}/{total} ({phase2_passed/total*100:.1f}%)")
        logger.info(f"Phase 2.5 Accuracy: {phase25_passed}/{total} ({phase25_passed/total*100:.1f}%)")

        improvement = phase25_passed - phase2_passed
        if improvement > 0:
            logger.info(f"\n✅ IMPROVEMENT: +{improvement} scenarios fixed ({improvement/total*100:.1f}% improvement)")
        elif improvement < 0:
            logger.warning(f"\n⚠️  REGRESSION: {abs(improvement)} scenarios broken")
        else:
            logger.info(f"\n➡️  NO CHANGE: Same accuracy")

        # Identify specific improvements
        logger.info("\n" + "-"*120)
        logger.info("SCENARIO-BY-SCENARIO BREAKDOWN")
        logger.info("-"*120)

        for data in comparison_data:
            phase2_result = "✅ PASS" if data['phase2_correct'] else "❌ FAIL"
            phase25_result = "✅ PASS" if data['phase2.5_correct'] else "❌ FAIL"

            if data['phase2_correct'] and data['phase2.5_correct']:
                status = "✅ Both Pass"
            elif not data['phase2_correct'] and not data['phase2.5_correct']:
                status = "❌ Both Fail"
            elif not data['phase2_correct'] and data['phase2.5_correct']:
                status = "🎯 FIXED"
            else:
                status = "⚠️  BROKEN"

            logger.info(f"{data['scenario']:40} | {phase2_result:8} ({data['phase2_confidence']*100:5.1f}%) | {phase25_result:8} ({data['phase2.5_confidence']*100:5.1f}%) | {status}")

        logger.info("="*120)

        # Save comparison
        df_comparison = pd.DataFrame(comparison_data)
        output_path = Path("results/models/phase2_vs_phase2_5_comparison.csv")
        df_comparison.to_csv(output_path, index=False)
        logger.info(f"\nComparison saved to: {output_path}")

        return comparison_data, phase2_passed, phase25_passed


def main():
    """Main comparison script"""
    try:
        comparator = ModelComparator()
        comparison_data, phase2_passed, phase25_passed = comparator.compare_all_scenarios()

        print("\n" + "="*120)
        print("VERIFICATION COMPLETE")
        print("="*120)
        print(f"\nPhase 2:   {phase2_passed}/12 scenarios ({phase2_passed/12*100:.1f}%)")
        print(f"Phase 2.5: {phase25_passed}/12 scenarios ({phase25_passed/12*100:.1f}%)")
        print(f"\nImprovement: +{phase25_passed - phase2_passed} scenarios ({(phase25_passed - phase2_passed)/12*100:.1f}%)")
        print("="*120)

    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
