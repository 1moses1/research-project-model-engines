#!/usr/bin/env python3
"""
Test Enhanced Model on Real-World Scenarios
Focus on scenarios that previously failed (ransomware, insider threats)
"""

import joblib
import numpy as np
from pathlib import Path
from scipy.sparse import hstack, csr_matrix
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedModelTester:
    """Test enhanced XGBoost model on challenging real-world scenarios"""

    def __init__(self, model_dir: str = "results/models/xgboost_enhanced"):
        self.model_dir = Path(model_dir)

        # Load model and feature extractors
        logger.info("Loading enhanced model...")
        self.model = joblib.load(self.model_dir / "xgboost_enhanced.pkl")
        self.tfidf_vectorizer = joblib.load(self.model_dir / "tfidf_vectorizer.pkl")
        self.control_encoder = joblib.load(self.model_dir / "control_encoder.pkl")
        self.family_encoder = joblib.load(self.model_dir / "family_encoder.pkl")
        logger.info("  ✅ Model loaded successfully!")

    def extract_features(self, log_message, control_id='SI-4', control_family='System and Information Integrity'):
        """Extract features from log message"""

        # Text features
        tfidf_features = self.tfidf_vectorizer.transform([log_message])

        # Categorical features
        try:
            control_encoded = self.control_encoder.transform([control_id])
        except:
            control_encoded = np.array([0])

        try:
            family_encoded = self.family_encoder.transform([control_family])
        except:
            family_encoded = np.array([0])

        # Temporal features (default business hours)
        temporal_features = np.array([[14, 1, 1]])  # 2pm Monday, business hours

        # Combine
        categorical_sparse = csr_matrix(np.column_stack([control_encoded, family_encoded]))
        temporal_sparse = csr_matrix(temporal_features.astype(np.float64))

        X = hstack([tfidf_features, categorical_sparse, temporal_sparse])

        return X

    def predict(self, log_message, control_id='SI-4', control_family='System and Information Integrity'):
        """Make prediction with confidence score"""

        X = self.extract_features(log_message, control_id, control_family)
        prediction = self.model.predict(X)[0]
        probability = self.model.predict_proba(X)[0]

        status = 'non_compliant' if prediction == 1 else 'compliant'
        confidence = probability[1] if prediction == 1 else probability[0]

        return status, confidence

    def run_comprehensive_tests(self):
        """Test on 12 real-world scenarios (including previously failed ones)"""

        test_scenarios = [
            # Previously PASSED scenarios
            {
                'name': 'Unauthorized SSH Access',
                'log': 'Failed SSH login attempt from 192.168.1.100 to root@10.0.0.5 - Access denied',
                'control': 'AC-3',
                'family': 'Access Control',
                'expected': 'non_compliant',
                'previous_result': 'PASS'
            },
            {
                'name': 'Successful Compliance Check',
                'log': 'Security audit passed: All patches applied, firewall enabled, logs encrypted',
                'control': 'SI-2',
                'family': 'System and Information Integrity',
                'expected': 'compliant',
                'previous_result': 'PASS'
            },
            {
                'name': 'Phishing Email Detected',
                'log': 'Email from unknown@suspicious-domain.ru blocked - Contains malicious link',
                'control': 'SI-8',
                'family': 'System and Information Integrity',
                'expected': 'non_compliant',
                'previous_result': 'PASS'
            },
            {
                'name': 'Unpatched Critical Vulnerability',
                'log': 'CVE-2023-12345 detected on server-prod-01 - Critical severity, no patch applied',
                'control': 'RA-5',
                'family': 'Risk Assessment',
                'expected': 'non_compliant',
                'previous_result': 'PASS'
            },
            {
                'name': 'Encryption Enabled',
                'log': 'All databases encrypted at rest using AES-256, key rotation completed',
                'control': 'SC-28',
                'family': 'System and Communications Protection',
                'expected': 'compliant',
                'previous_result': 'PASS'
            },
            {
                'name': 'Backup Failure',
                'log': 'Backup job failed for 7 consecutive days - Data loss risk',
                'control': 'CP-9',
                'family': 'Contingency Planning',
                'expected': 'non_compliant',
                'previous_result': 'PASS'
            },

            # Previously FAILED scenarios (focus on these)
            {
                'name': 'Ransomware Attack',
                'log': 'File encryption detected: 10,000 files encrypted with .locked extension in 5 minutes',
                'control': 'SI-4',
                'family': 'System and Information Integrity',
                'expected': 'non_compliant',
                'previous_result': 'FAIL'
            },
            {
                'name': 'Insider Threat - Data Exfiltration',
                'log': 'Employee downloaded 50GB sensitive data to USB at 2am on Saturday',
                'control': 'AC-3',
                'family': 'Access Control',
                'expected': 'non_compliant',
                'previous_result': 'FAIL'
            },

            # Additional challenging scenarios
            {
                'name': 'SQL Injection Attack',
                'log': "HTTP GET /api/users?id=1' OR '1'='1 - SQL injection attempt detected",
                'control': 'SI-4',
                'family': 'System and Information Integrity',
                'expected': 'non_compliant',
                'previous_result': 'NEW'
            },
            {
                'name': 'Lateral Movement',
                'log': 'Suspicious SMB connections from workstation-05 to 20 servers in 2 minutes',
                'control': 'AC-3',
                'family': 'Access Control',
                'expected': 'non_compliant',
                'previous_result': 'NEW'
            },
            {
                'name': 'DDoS Attack',
                'log': 'Network traffic spike: 100,000 requests/sec from 500 IPs - Service degradation',
                'control': 'SC-5',
                'family': 'System and Communications Protection',
                'expected': 'non_compliant',
                'previous_result': 'NEW'
            },
            {
                'name': 'Credential Stuffing',
                'log': 'Login attempts from 200 IPs using stolen credentials - 50 accounts compromised',
                'control': 'IA-2',
                'family': 'Identification and Authentication',
                'expected': 'non_compliant',
                'previous_result': 'NEW'
            }
        ]

        logger.info("\n" + "="*100)
        logger.info("TESTING ENHANCED MODEL ON REAL-WORLD SCENARIOS")
        logger.info("="*100 + "\n")

        results = []
        passed = 0
        failed = 0
        critical_failures = []

        for i, scenario in enumerate(test_scenarios, 1):
            logger.info(f"{i}. Testing: {scenario['name']}")
            logger.info(f"   Previous Result: {scenario['previous_result']}")

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

            if is_correct:
                passed += 1
            else:
                failed += 1
                if scenario['previous_result'] == 'FAIL':
                    critical_failures.append(scenario['name'])

            results.append({
                'scenario': scenario['name'],
                'expected': scenario['expected'],
                'predicted': status,
                'confidence': confidence,
                'correct': is_correct,
                'previous_result': scenario['previous_result']
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

        # Performance comparison
        logger.info("COMPARISON WITH PREVIOUS MODEL:")
        logger.info("-"*100)
        logger.info("Previous Model (synthetic only):")
        logger.info("  - Overall: 6/8 (75%)")
        logger.info("  - Ransomware: 0/1 (0%) ❌")
        logger.info("  - Insider Threat: 0/1 (0%) ❌")
        print()
        logger.info("Enhanced Model (synthetic + real data):")
        logger.info(f"  - Overall: {passed}/{len(test_scenarios)} ({passed/len(test_scenarios)*100:.1f}%)")

        # Check critical scenarios
        ransomware_result = [r for r in results if 'Ransomware' in r['scenario']][0]
        insider_result = [r for r in results if 'Insider Threat' in r['scenario']][0]

        logger.info(f"  - Ransomware: {'✅ FIXED' if ransomware_result['correct'] else '❌ STILL FAILING'}")
        logger.info(f"  - Insider Threat: {'✅ FIXED' if insider_result['correct'] else '❌ STILL FAILING'}")
        print()

        if critical_failures:
            logger.info("⚠️  CRITICAL FAILURES (previously failed, still failing):")
            for failure in critical_failures:
                logger.info(f"  - {failure}")
        else:
            logger.info("✅ ALL PREVIOUSLY FAILED SCENARIOS NOW PASSING!")

        print()
        logger.info("="*100)

        # Improvement analysis
        improvement = (passed/len(test_scenarios)*100) - 75
        logger.info("IMPROVEMENT ANALYSIS:")
        logger.info("="*100)
        logger.info(f"Baseline (previous model): 75%")
        logger.info(f"Enhanced model: {passed/len(test_scenarios)*100:.1f}%")
        logger.info(f"Improvement: {'+' if improvement > 0 else ''}{improvement:.1f} percentage points")
        print()

        if passed/len(test_scenarios) >= 0.85:
            logger.info("✅ TARGET MET: ≥85% accuracy achieved!")
            logger.info("   Ready for Phase 2: BERT embeddings for 95%+ accuracy")
        elif passed/len(test_scenarios) >= 0.80:
            logger.info("⚠️  CLOSE TO TARGET: 80-85% accuracy")
            logger.info("   Recommendation: Add more attack pattern variations")
        else:
            logger.info("❌ TARGET NOT MET: <80% accuracy")
            logger.info("   Recommendation: Analyze failures and retrain with targeted data")

        logger.info("="*100)

        return results


def main():
    """Main test script"""
    tester = EnhancedModelTester()
    results = tester.run_comprehensive_tests()

    print("\n" + "="*100)
    print("NEXT STEPS:")
    print("="*100)

    # Count how many passed
    passed = sum(1 for r in results if r['correct'])
    total = len(results)
    accuracy = passed / total

    if accuracy >= 0.85:
        print("1. ✅ Phase 1 complete - Real data integration successful")
        print("2. 📊 Document results in MODEL_IMPROVEMENT_PLAN.md")
        print("3. 🚀 Begin Phase 2: BERT embeddings + temporal features")
        print("   Expected improvement: 85% → 95%+")
    elif accuracy >= 0.75:
        print("1. ⚠️  Improvement detected but target not fully met")
        print("2. 🔍 Analyze failed scenarios for patterns")
        print("3. 📊 Add more adversarial samples for failed attack types")
        print("4. 🔄 Retrain with enhanced MITRE patterns")
    else:
        print("1. ❌ Accuracy below baseline - investigate issues")
        print("2. 🔍 Check data quality and feature extraction")
        print("3. 📊 Validate MITRE/CVE integration")

    print("="*100)


if __name__ == '__main__':
    main()
