#!/usr/bin/env python3
"""
Adversarial Attack Testing - Real-World Complex Scenarios
Test the model with realistic attacks that weren't in training data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
from datetime import datetime
import random

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.xgboost_classifier import XGBoostClassifier
from utils.logger import setup_logger

logger = setup_logger('adversarial_test')


class AdversarialAttackTester:
    """Generate novel, complex attack scenarios"""

    def __init__(self):
        self.classifier = XGBoostClassifier()
        model_path = Path("results/models/xgboost_compliance_enriched/xgboost_model_compliance_enriched")
        self.classifier.load_model(str(model_path))

    def generate_novel_apt_attack(self, n=50) -> pd.DataFrame:
        """
        Generate APT (Advanced Persistent Threat) scenarios
        Multi-stage attacks not seen in training
        """
        attacks = []

        for i in range(n):
            # APT stages with realistic log messages
            scenarios = [
                # Initial reconnaissance
                {
                    'log_message': f'Normal user activity: user{i} accessed file share //fileserver/docs from 192.168.1.{i%255}',
                    'status_code': 200,  # Looks benign!
                    'true_label': 'non_compliant',  # But it's reconnaissance
                    'attack_type': 'APT Reconnaissance'
                },
                # Lateral movement with valid credentials
                {
                    'log_message': f'Successful login: admin{i} from workstation WS-{i:04d} to DC-01',
                    'status_code': 200,  # Success code!
                    'true_label': 'non_compliant',  # But stolen creds
                    'attack_type': 'Lateral Movement'
                },
                # Data exfiltration disguised as backup
                {
                    'log_message': f'Backup job completed: 15GB transferred to cloud storage backup-server-{i}.com',
                    'status_code': 201,  # Created successfully!
                    'true_label': 'non_compliant',  # But it's exfiltration
                    'attack_type': 'Data Exfiltration'
                },
                # Persistence mechanism
                {
                    'log_message': f'System service updated: WindowsUpdateService modified by SYSTEM account',
                    'status_code': 200,  # Looks like legit update
                    'true_label': 'non_compliant',  # But it's malware persistence
                    'attack_type': 'Persistence'
                },
            ]

            attack = random.choice(scenarios)
            event = {
                'timestamp': datetime.now().isoformat(),
                'log_message': attack['log_message'],
                'source': 'enterprise_logs',
                'event_type': 'system_event',
                'control_id': 'SI-4',  # System Monitoring
                'control_family': 'System and Information Integrity',
                'framework': 'NIST SP 800-53',
                'user': f'user{i}',
                'resource': 'network',
                'status_code': attack['status_code'],  # The key test!
                'compliance_status': attack['true_label'],
                'anomaly_type': 'suspicious',
                'anomaly_label': 'suspicious',
                'description': attack['attack_type'],
                'hour_of_day': random.randint(0, 23),
                'day_of_week': random.randint(0, 6),
                'is_business_hours': 1,
                'port': 443,
                'severity': 'high'
            }
            attacks.append(event)

        return pd.DataFrame(attacks)

    def generate_zero_day_exploits(self, n=50) -> pd.DataFrame:
        """
        Generate zero-day exploit scenarios
        Novel attack patterns
        """
        exploits = []

        for i in range(n):
            scenarios = [
                {
                    'log_message': f'Application performance monitoring: process memory usage spike to 95% on APP-SERVER-{i}',
                    'status_code': 200,  # Monitoring succeeded
                    'true_label': 'non_compliant',  # But it's buffer overflow attempt
                    'exploit_type': 'Buffer Overflow'
                },
                {
                    'log_message': f'Database query optimization: complex join executed in 2.5 seconds',
                    'status_code': 200,  # Query succeeded
                    'true_label': 'non_compliant',  # But it's SQL injection
                    'exploit_type': 'SQL Injection (time-based)'
                },
                {
                    'log_message': f'CDN cache refresh: fetching updated assets from origin server internal-api.{i}.local',
                    'status_code': 200,  # Cache refresh worked
                    'true_label': 'non_compliant',  # But it's SSRF attack
                    'exploit_type': 'Server-Side Request Forgery'
                },
                {
                    'log_message': f'Template engine rendered user profile page for premium_user_{i}',
                    'status_code': 200,  # Page rendered
                    'true_label': 'non_compliant',  # But SSTI vulnerability
                    'exploit_type': 'Server-Side Template Injection'
                },
            ]

            exploit = random.choice(scenarios)
            event = {
                'timestamp': datetime.now().isoformat(),
                'log_message': exploit['log_message'],
                'source': 'application_logs',
                'event_type': 'web_request',
                'control_id': 'SI-10',  # Input Validation
                'control_family': 'System and Information Integrity',
                'framework': 'OWASP',
                'user': f'web_user_{i}',
                'resource': 'web_application',
                'status_code': exploit['status_code'],  # Success codes!
                'compliance_status': exploit['true_label'],
                'anomaly_type': 'critical',
                'anomaly_label': 'critical',
                'description': exploit['exploit_type'],
                'hour_of_day': random.randint(8, 17),
                'day_of_week': random.randint(0, 4),
                'is_business_hours': 1,
                'port': 443,
                'severity': 'critical'
            }
            exploits.append(event)

        return pd.DataFrame(exploits)

    def generate_insider_threats(self, n=50) -> pd.DataFrame:
        """
        Generate insider threat scenarios
        Authorized users doing malicious things
        """
        threats = []

        for i in range(n):
            scenarios = [
                {
                    'log_message': f'Employee HR_Manager_{i} accessed 500 employee records - quarterly review process',
                    'status_code': 200,  # Authorized access
                    'true_label': 'non_compliant',  # But excessive access
                    'threat_type': 'Data Harvesting'
                },
                {
                    'log_message': f'Developer dev_{i} committed code changes to production branch - hotfix deployment',
                    'status_code': 201,  # Commit successful
                    'true_label': 'non_compliant',  # But bypassed review
                    'threat_type': 'Unauthorized Code Deployment'
                },
                {
                    'log_message': f'System administrator admin_{i} disabled audit logging for maintenance window',
                    'status_code': 200,  # Command executed
                    'true_label': 'non_compliant',  # But covering tracks
                    'threat_type': 'Audit Evasion'
                },
                {
                    'log_message': f'Finance user finance_{i} exported transaction report to personal USB drive',
                    'status_code': 200,  # Export succeeded
                    'true_label': 'non_compliant',  # But policy violation
                    'threat_type': 'Data Exfiltration'
                },
            ]

            threat = random.choice(scenarios)
            event = {
                'timestamp': datetime.now().isoformat(),
                'log_message': threat['log_message'],
                'source': 'user_activity',
                'event_type': 'user_action',
                'control_id': 'AU-6',  # Audit Review
                'control_family': 'Audit and Accountability',
                'framework': 'NIST SP 800-53',
                'user': f'insider_{i}',
                'resource': 'data',
                'status_code': threat['status_code'],  # All success!
                'compliance_status': threat['true_label'],
                'anomaly_type': 'suspicious',
                'anomaly_label': 'suspicious',
                'description': threat['threat_type'],
                'hour_of_day': random.randint(18, 23),  # After hours
                'day_of_week': random.randint(5, 6),  # Weekend
                'is_business_hours': 0,
                'port': 443,
                'severity': 'high'
            }
            threats.append(event)

        return pd.DataFrame(threats)

    def generate_supply_chain_attacks(self, n=50) -> pd.DataFrame:
        """
        Generate supply chain compromise scenarios
        """
        attacks = []

        for i in range(n):
            scenarios = [
                {
                    'log_message': f'NPM package @company/utils@1.2.{i} installed successfully - dependency update',
                    'status_code': 200,  # Install worked
                    'true_label': 'non_compliant',  # But compromised package
                    'attack_type': 'Malicious Dependency'
                },
                {
                    'log_message': f'Software update applied: VendorSoftware v{i}.0 update completed successfully',
                    'status_code': 200,  # Update successful
                    'true_label': 'non_compliant',  # But backdoored update
                    'attack_type': 'Compromised Update'
                },
                {
                    'log_message': f'Third-party API integration test passed: payment-processor-api v2.{i}',
                    'status_code': 200,  # API works
                    'true_label': 'non_compliant',  # But malicious API
                    'attack_type': 'Malicious Third-Party Service'
                },
            ]

            attack = random.choice(scenarios)
            event = {
                'timestamp': datetime.now().isoformat(),
                'log_message': attack['log_message'],
                'source': 'devops_pipeline',
                'event_type': 'deployment',
                'control_id': 'SA-11',  # Developer Testing
                'control_family': 'System and Services Acquisition',
                'framework': 'NIST SP 800-53',
                'user': f'ci_cd_bot_{i}',
                'resource': 'build_system',
                'status_code': attack['status_code'],
                'compliance_status': attack['true_label'],
                'anomaly_type': 'critical',
                'anomaly_label': 'critical',
                'description': attack['attack_type'],
                'hour_of_day': random.randint(0, 23),
                'day_of_week': random.randint(0, 6),
                'is_business_hours': 1,
                'port': 443,
                'severity': 'critical'
            }
            attacks.append(event)

        return pd.DataFrame(attacks)

    def test_all_scenarios(self) -> dict:
        """Run all adversarial tests"""
        results = {}

        # Test 1: APT Attacks
        logger.info("Testing APT attacks...")
        apt_df = self.generate_novel_apt_attack(50)
        predictions, probabilities = self.classifier.predict(apt_df)

        apt_results = self.evaluate_predictions(apt_df, predictions, probabilities)
        results['apt_attacks'] = apt_results

        # Test 2: Zero-day Exploits
        logger.info("Testing zero-day exploits...")
        zeroday_df = self.generate_zero_day_exploits(50)
        predictions, probabilities = self.classifier.predict(zeroday_df)

        zeroday_results = self.evaluate_predictions(zeroday_df, predictions, probabilities)
        results['zero_day_exploits'] = zeroday_results

        # Test 3: Insider Threats
        logger.info("Testing insider threats...")
        insider_df = self.generate_insider_threats(50)
        predictions, probabilities = self.classifier.predict(insider_df)

        insider_results = self.evaluate_predictions(insider_df, predictions, probabilities)
        results['insider_threats'] = insider_results

        # Test 4: Supply Chain Attacks
        logger.info("Testing supply chain attacks...")
        supply_df = self.generate_supply_chain_attacks(50)
        predictions, probabilities = self.classifier.predict(supply_df)

        supply_results = self.evaluate_predictions(supply_df, predictions, probabilities)
        results['supply_chain_attacks'] = supply_results

        return results

    def evaluate_predictions(self, df: pd.DataFrame, predictions: list, probabilities: np.ndarray) -> dict:
        """Evaluate prediction quality"""
        y_true = df['compliance_status'].values
        y_pred = predictions

        correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
        accuracy = correct / len(y_true)

        # Count false negatives (missed attacks)
        false_negatives = sum(1 for t, p in zip(y_true, y_pred)
                             if t == 'non_compliant' and p == 'compliant')

        # Count false positives
        false_positives = sum(1 for t, p in zip(y_true, y_pred)
                             if t == 'compliant' and p == 'non_compliant')

        return {
            'total_samples': len(y_true),
            'accuracy': float(accuracy),
            'correct': int(correct),
            'incorrect': int(len(y_true) - correct),
            'false_negatives': int(false_negatives),  # CRITICAL: Missed attacks
            'false_positives': int(false_positives),
            'avg_confidence': float(np.mean(probabilities)),
            'min_confidence': float(np.min(probabilities)),
            'max_confidence': float(np.max(probabilities))
        }


def main():
    """Main test runner"""
    print("\n" + "="*80)
    print("ADVERSARIAL ATTACK TESTING")
    print("Testing model with novel, complex attack scenarios")
    print("="*80)
    print()

    tester = AdversarialAttackTester()

    print("🎯 Generating adversarial scenarios...")
    print("   All scenarios have status_code=200/201 (success codes)")
    print("   But they are actually ATTACKS!")
    print("   Can the model detect them without relying on status codes?\n")

    results = tester.test_all_scenarios()

    print("\n" + "="*80)
    print("RESULTS")
    print("="*80)

    total_missed = 0
    total_attacks = 0

    for scenario, metrics in results.items():
        total_attacks += metrics['total_samples']
        total_missed += metrics['false_negatives']

        print(f"\n{scenario.replace('_', ' ').title()}:")
        print(f"  Samples: {metrics['total_samples']}")
        print(f"  Accuracy: {metrics['accuracy']:.2%}")
        print(f"  🚨 FALSE NEGATIVES (Missed Attacks): {metrics['false_negatives']}")
        print(f"  False Positives: {metrics['false_positives']}")
        print(f"  Avg Confidence: {metrics['avg_confidence']:.2%}")

        if metrics['false_negatives'] > 0:
            miss_rate = metrics['false_negatives'] / metrics['total_samples'] * 100
            print(f"  ⚠️  Miss Rate: {miss_rate:.1f}% of attacks went undetected!")

    print("\n" + "="*80)
    print("OVERALL ASSESSMENT")
    print("="*80)

    overall_detection = (total_attacks - total_missed) / total_attacks * 100

    print(f"\nTotal Adversarial Attacks: {total_attacks}")
    print(f"Attacks Detected: {total_attacks - total_missed}")
    print(f"Attacks Missed: {total_missed}")
    print(f"Overall Detection Rate: {overall_detection:.2%}")

    if total_missed > total_attacks * 0.5:
        print("\n❌ CRITICAL: Model missed >50% of novel attacks!")
        print("   The 100% accuracy was due to DATA LEAKAGE (status codes)")
        print("   Model is NOT learning security patterns - just memorizing labels")
        assessment = "CRITICAL_FAILURE"
    elif total_missed > total_attacks * 0.2:
        print("\n⚠️  WARNING: Model missed >20% of novel attacks")
        print("   Model may be overfitting to training data patterns")
        print("   Not generalizing well to new attack types")
        assessment = "POOR_GENERALIZATION"
    elif total_missed > 0:
        print("\n✅ ACCEPTABLE: Some attacks missed but reasonable performance")
        print("   Model shows some generalization capability")
        print("   Further training on diverse scenarios recommended")
        assessment = "ACCEPTABLE"
    else:
        print("\n🎉 EXCELLENT: All novel attacks detected!")
        print("   Model demonstrates strong generalization")
        assessment = "EXCELLENT"

    # Save results
    output = {
        'scenario_results': results,
        'overall': {
            'total_attacks': total_attacks,
            'detected': total_attacks - total_missed,
            'missed': total_missed,
            'detection_rate': float(overall_detection / 100),
            'assessment': assessment
        },
        'tested_at': datetime.now().isoformat()
    }

    output_file = Path("results/models/xgboost_compliance_enriched/adversarial_test_results.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print("="*80)


if __name__ == '__main__':
    main()
