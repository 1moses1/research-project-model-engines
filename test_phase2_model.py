#!/usr/bin/env python3
"""
Test Phase 2 Model on Real-World Scenarios
Expected: 90-95%+ accuracy with BERT + Temporal features
"""

import joblib
import numpy as np
from pathlib import Path
from scipy.sparse import hstack, csr_matrix
import logging
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.bert_feature_extractor import BERTFeatureExtractor
from models.temporal_feature_extractor import TemporalFeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Phase2ModelTester:
    """Test Phase 2 model (XGBoost + BERT + Temporal)"""

    def __init__(self, model_dir: str = "results/models/xgboost_phase2"):
        self.model_dir = Path(model_dir)

        logger.info("Loading Phase 2 model...")
        try:
            self.model = joblib.load(self.model_dir / "xgboost_phase2.pkl")
            self.tfidf_vectorizer = joblib.load(self.model_dir / "tfidf_vectorizer.pkl")
            self.control_encoder = joblib.load(self.model_dir / "control_encoder.pkl")
            self.family_encoder = joblib.load(self.model_dir / "family_encoder.pkl")
            logger.info("  ✅ Phase 2 model loaded successfully!")
        except FileNotFoundError:
            logger.error("  ❌ Phase 2 model not found - run train_phase2_ensemble.py first")
            raise

        # Initialize BERT and temporal extractors
        logger.info("Initializing feature extractors...")
        self.bert_extractor = BERTFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()
        logger.info("  ✅ Feature extractors ready!")

    def extract_features(self, log_message, control_id='SI-4',
                        control_family='System and Information Integrity'):
        """Extract all features: TF-IDF + BERT + Temporal"""

        # 1. TF-IDF features
        tfidf_features = self.tfidf_vectorizer.transform([log_message])

        # 2. Categorical features
        try:
            control_encoded = self.control_encoder.transform([control_id])
        except:
            control_encoded = np.array([0])

        try:
            family_encoded = self.family_encoder.transform([control_family])
        except:
            family_encoded = np.array([0])

        # 3. Temporal features - extract from log message
        import pandas as pd
        from datetime import datetime

        # Create a dummy dataframe for temporal extraction
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

        # Get temporal feature values
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
                # Convert day of week to numeric if needed
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

        # 4. BERT embeddings
        bert_embeddings = self.bert_extractor.extract_embeddings([log_message])

        # Combine all features
        categorical_sparse = csr_matrix(np.column_stack([control_encoded, family_encoded]))
        temporal_sparse = csr_matrix(temporal_features)
        bert_sparse = csr_matrix(bert_embeddings)

        X = hstack([tfidf_features, categorical_sparse, temporal_sparse, bert_sparse])

        return X

    def predict(self, log_message, control_id='SI-4',
               control_family='System and Information Integrity'):
        """Make prediction with all Phase 2 features"""

        X = self.extract_features(log_message, control_id, control_family)
        prediction = self.model.predict(X)[0]
        probability = self.model.predict_proba(X)[0]

        status = 'non_compliant' if prediction == 1 else 'compliant'
        confidence = probability[1] if prediction == 1 else probability[0]

        return status, confidence

    def run_comprehensive_tests(self):
        """Test on 12 real-world scenarios"""

        test_scenarios = [
            # Previously PASSED scenarios
            {
                'name': 'Unauthorized SSH Access',
                'log': 'Failed SSH login attempt from 192.168.1.100 to root@10.0.0.5 - Access denied',
                'control': 'AC-3',
                'family': 'Access Control',
                'expected': 'non_compliant',
                'phase1_result': 'PASS'
            },
            {
                'name': 'Successful Compliance Check',
                'log': 'Security audit passed: All patches applied, firewall enabled, logs encrypted',
                'control': 'SI-2',
                'family': 'System and Information Integrity',
                'expected': 'compliant',
                'phase1_result': 'PASS'
            },
            {
                'name': 'Phishing Email Detected',
                'log': 'Email from unknown@suspicious-domain.ru blocked - Contains malicious link',
                'control': 'SI-8',
                'family': 'System and Information Integrity',
                'expected': 'non_compliant',
                'phase1_result': 'FAIL (regression)'
            },
            {
                'name': 'Unpatched Critical Vulnerability',
                'log': 'CVE-2023-12345 detected on server-prod-01 - Critical severity, no patch applied',
                'control': 'RA-5',
                'family': 'Risk Assessment',
                'expected': 'non_compliant',
                'phase1_result': 'PASS'
            },
            {
                'name': 'Encryption Enabled',
                'log': 'All databases encrypted at rest using AES-256, key rotation completed',
                'control': 'SC-28',
                'family': 'System and Communications Protection',
                'expected': 'compliant',
                'phase1_result': 'PASS'
            },
            {
                'name': 'Backup Failure',
                'log': 'Backup job failed for 7 consecutive days - Data loss risk',
                'control': 'CP-9',
                'family': 'Contingency Planning',
                'expected': 'non_compliant',
                'phase1_result': 'PASS'
            },

            # Previously FAILED scenarios (critical ones)
            {
                'name': 'Ransomware Attack',
                'log': 'File encryption detected: 10,000 files encrypted with .locked extension in 5 minutes',
                'control': 'SI-4',
                'family': 'System and Information Integrity',
                'expected': 'non_compliant',
                'phase1_result': 'PASS (FIXED in Phase 1)'
            },
            {
                'name': 'Insider Threat - Data Exfiltration',
                'log': 'Employee downloaded 50GB sensitive data to USB at 2am on Saturday',
                'control': 'AC-3',
                'family': 'Access Control',
                'expected': 'non_compliant',
                'phase1_result': 'FAIL'
            },

            # Additional challenging scenarios
            {
                'name': 'SQL Injection Attack',
                'log': "HTTP GET /api/users?id=1' OR '1'='1 - SQL injection attempt detected",
                'control': 'SI-4',
                'family': 'System and Information Integrity',
                'expected': 'non_compliant',
                'phase1_result': 'PASS'
            },
            {
                'name': 'Lateral Movement',
                'log': 'Suspicious SMB connections from workstation-05 to 20 servers in 2 minutes',
                'control': 'AC-3',
                'family': 'Access Control',
                'expected': 'non_compliant',
                'phase1_result': 'FAIL'
            },
            {
                'name': 'DDoS Attack',
                'log': 'Network traffic spike: 100,000 requests/sec from 500 IPs - Service degradation',
                'control': 'SC-5',
                'family': 'System and Communications Protection',
                'expected': 'non_compliant',
                'phase1_result': 'FAIL'
            },
            {
                'name': 'Credential Stuffing',
                'log': 'Login attempts from 200 IPs using stolen credentials - 50 accounts compromised',
                'control': 'IA-2',
                'family': 'Identification and Authentication',
                'expected': 'non_compliant',
                'phase1_result': 'FAIL'
            }
        ]

        logger.info("\n" + "="*100)
        logger.info("TESTING PHASE 2 MODEL ON REAL-WORLD SCENARIOS")
        logger.info("="*100 + "\n")

        results = []
        passed = 0
        failed = 0
        phase1_fixes = 0

        for i, scenario in enumerate(test_scenarios, 1):
            logger.info(f"{i}. Testing: {scenario['name']}")
            logger.info(f"   Phase 1 Result: {scenario['phase1_result']}")

            status, confidence = self.predict(
                scenario['log'],
                scenario['control'],
                scenario['family']
            )

            is_correct = (status == scenario['expected'])
            result_icon = "✅" if is_correct else "❌"

            logger.info(f"   Expected: {scenario['expected']}")
            logger.info(f"   Predicted: {status} (confidence: {confidence*100:.1f}%)")
            logger.info(f"   Result: {result_icon} {'PASS' if is_correct else 'FAIL'}")

            # Track if we fixed a Phase 1 failure
            if is_correct and 'FAIL' in scenario['phase1_result']:
                phase1_fixes += 1
                logger.info(f"   🎯 FIXED Phase 1 failure!")

            if is_correct:
                passed += 1
            else:
                failed += 1

            results.append({
                'scenario': scenario['name'],
                'expected': scenario['expected'],
                'predicted': status,
                'confidence': confidence,
                'correct': is_correct,
                'phase1_result': scenario['phase1_result']
            })

            print()

        # Summary
        logger.info("="*100)
        logger.info("RESULTS SUMMARY")
        logger.info("="*100)
        logger.info(f"Total Scenarios: {len(test_scenarios)}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Accuracy: {passed/len(test_scenarios)*100:.1f}%")
        print()

        # Comparison
        logger.info("PHASE COMPARISON:")
        logger.info("-"*100)
        logger.info("Baseline (original): 6/8 (75%)")
        logger.info("Phase 1 (Real Data): 7/8 original scenarios (87.5%)")
        logger.info(f"Phase 2 (BERT + Temporal): {passed}/{len(test_scenarios)} ({passed/len(test_scenarios)*100:.1f}%)")
        logger.info(f"Phase 1 Failures Fixed: {phase1_fixes}")
        print()

        # Check critical scenarios
        insider_result = [r for r in results if 'Insider Threat' in r['scenario']][0]
        lateral_result = [r for r in results if 'Lateral Movement' in r['scenario']][0]
        ddos_result = [r for r in results if 'DDoS' in r['scenario']][0]
        credential_result = [r for r in results if 'Credential Stuffing' in r['scenario']][0]

        logger.info("CRITICAL SCENARIOS (Previously Failed):")
        logger.info(f"  - Insider Threat: {'✅ FIXED' if insider_result['correct'] else '❌ STILL FAILING'}")
        logger.info(f"  - Lateral Movement: {'✅ FIXED' if lateral_result['correct'] else '❌ STILL FAILING'}")
        logger.info(f"  - DDoS Attack: {'✅ FIXED' if ddos_result['correct'] else '❌ STILL FAILING'}")
        logger.info(f"  - Credential Stuffing: {'✅ FIXED' if credential_result['correct'] else '❌ STILL FAILING'}")
        print()

        logger.info("="*100)
        logger.info("PHASE 2 ASSESSMENT:")
        logger.info("="*100)

        improvement = (passed/len(test_scenarios)*100) - 87.5
        logger.info(f"Baseline: 75%")
        logger.info(f"Phase 1:  87.5%")
        logger.info(f"Phase 2:  {passed/len(test_scenarios)*100:.1f}%")
        logger.info(f"Phase 2 Improvement: {'+' if improvement > 0 else ''}{improvement:.1f} percentage points")
        print()

        if passed/len(test_scenarios) >= 0.95:
            logger.info("🎯 TARGET ACHIEVED: ≥95% accuracy!")
            logger.info("   ✅ Production-ready for Rwanda SOC deployment")
            logger.info("   ✅ Meets industry benchmarks (DeepLog: 95.6%, LogAnomaly: 96.7%)")
        elif passed/len(test_scenarios) >= 0.90:
            logger.info("✅ STRONG PERFORMANCE: 90-95% accuracy")
            logger.info("   Ready for deployment with minor refinements")
        elif passed/len(test_scenarios) >= 0.85:
            logger.info("⚠️  GOOD PROGRESS: 85-90% accuracy")
            logger.info("   Phase 2 features helping but need fine-tuning")
        else:
            logger.info("❌ BELOW TARGET: <85% accuracy")
            logger.info("   Need to investigate feature engineering issues")

        logger.info("="*100)

        return results


def main():
    """Main test script"""
    try:
        tester = Phase2ModelTester()
        results = tester.run_comprehensive_tests()

        print("\n" + "="*100)
        print("CONCLUSION:")
        print("="*100)

        passed = sum(1 for r in results if r['correct'])
        total = len(results)
        accuracy = passed / total

        if accuracy >= 0.95:
            print("✅ Phase 2 COMPLETE - Model ready for production!")
            print("   Next: Deploy to Rwanda SOC environment")
        elif accuracy >= 0.90:
            print("⚠️  Phase 2 STRONG - Minor improvements needed")
            print("   Next: Fine-tune on specific failure cases")
        else:
            print("❌ Phase 2 INCOMPLETE - More work needed")
            print("   Next: Analyze failures and add targeted features")

        print("="*100)

    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
