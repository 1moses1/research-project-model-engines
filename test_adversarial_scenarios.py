#!/usr/bin/env python3
"""
Adversarial Testing for Clean Model
Test realistic attack scenarios that look benign but are actually malicious
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


class AdversarialTester:
    """Generate adversarial scenarios to test model robustness"""

    def __init__(self):
        self.classifier = XGBoostClassifier()
        model_path = Path("results/models/xgboost_no_leakage/xgboost_model_no_leakage")
        self.classifier.load_model(str(model_path))

        # Load a sample from test data to get correct schema
        test_df = pd.read_csv("data/combined_compliance/compliance_events_test.csv")
        self.template = test_df.iloc[0].to_dict()

    def create_event(self, log_message: str, true_label: str, description: str) -> dict:
        """Create an event with proper schema"""
        event = self.template.copy()

        # Update with new values
        event['log_message'] = log_message
        event['compliance_status'] = true_label
        event['description'] = description
        event['timestamp'] = datetime.now().isoformat()
        event['hour_of_day'] = random.randint(0, 23)
        event['day_of_week'] = random.randint(0, 6)
        event['is_business_hours'] = 1 if 8 <= event['hour_of_day'] <= 17 else 0

        # Remove leaky features that were deleted during retraining
        for key in ['status_code', 'anomaly_label', 'severity']:
            if key in event:
                del event[key]

        return event

    def test_benign_looking_attacks(self) -> pd.DataFrame:
        """
        Test 1: Attacks that look like normal operations
        These have benign-sounding log messages but are actually attacks
        """
        scenarios = []

        # Scenario 1: Data exfiltration disguised as backup
        scenarios.append(self.create_event(
            "Scheduled backup completed successfully - 50GB transferred to cloud storage backup-prod-server",
            "non_compliant",
            "Data exfiltration disguised as backup"
        ))

        # Scenario 2: Lateral movement disguised as admin maintenance
        scenarios.append(self.create_event(
            "System administrator performed routine maintenance on server DC-PROD-01 - all systems operational",
            "non_compliant",
            "Lateral movement with stolen admin credentials"
        ))

        # Scenario 3: Privilege escalation disguised as software update
        scenarios.append(self.create_event(
            "Software update service installed security patches - system reboot required",
            "non_compliant",
            "Malware persistence via fake update service"
        ))

        # Scenario 4: Reconnaissance disguised as monitoring
        scenarios.append(self.create_event(
            "Network monitoring agent scanned subnet 192.168.1.0/24 - discovered 45 active hosts",
            "non_compliant",
            "Network reconnaissance for attack planning"
        ))

        # Scenario 5: Command & Control disguised as DNS queries
        scenarios.append(self.create_event(
            "DNS resolver processed 1,250 queries from internal hosts - all queries resolved successfully",
            "non_compliant",
            "DNS tunneling for C2 communication"
        ))

        return pd.DataFrame(scenarios)

    def test_evasion_techniques(self) -> pd.DataFrame:
        """
        Test 2: Attacks using evasion techniques
        Obfuscated or subtle attacks
        """
        scenarios = []

        # Scenario 1: Time-delayed attack (looks like normal activity over time)
        scenarios.append(self.create_event(
            "User employee_12345 accessed customer database - retrieved 10 records for customer support case",
            "non_compliant",
            "Slow data exfiltration (10 records every hour = 240/day)"
        ))

        # Scenario 2: Living off the land (using legitimate tools)
        scenarios.append(self.create_event(
            "PowerShell script executed by administrator - system configuration updated successfully",
            "non_compliant",
            "Malicious PowerShell script using legitimate admin tools"
        ))

        # Scenario 3: Mimicking normal user behavior
        scenarios.append(self.create_event(
            "Employee logged in from home office VPN - accessed company intranet and email",
            "non_compliant",
            "Account takeover - attacker mimicking legitimate remote work"
        ))

        # Scenario 4: Low-and-slow attack
        scenarios.append(self.create_event(
            "Application server processed 5 API requests from client app - all requests completed within SLA",
            "non_compliant",
            "SQL injection using time delays (1 attempt every 10 minutes)"
        ))

        # Scenario 5: Encrypted channel abuse
        scenarios.append(self.create_event(
            "HTTPS connection established to update-server-cdn-prod.cloudfront.net - downloading application updates",
            "non_compliant",
            "Malware download over encrypted HTTPS channel"
        ))

        return pd.DataFrame(scenarios)

    def test_insider_threats(self) -> pd.DataFrame:
        """
        Test 3: Insider threats (authorized users doing unauthorized things)
        """
        scenarios = []

        # Scenario 1: Excessive data access
        scenarios.append(self.create_event(
            "HR Manager accessed 200 employee records for annual performance review preparation",
            "non_compliant",
            "Excessive access - HR manager only needs 50 direct reports"
        ))

        # Scenario 2: After-hours access
        scenarios.append(self.create_event(
            "Developer committed code changes to production repository - deployment pipeline triggered automatically",
            "non_compliant",
            "Unauthorized production changes at 2 AM (bypassing review)"
        ))

        # Scenario 3: Policy violation
        scenarios.append(self.create_event(
            "Finance analyst exported quarterly revenue report to personal cloud drive for work from home",
            "non_compliant",
            "Data policy violation - sensitive data on personal storage"
        ))

        # Scenario 4: Privilege abuse
        scenarios.append(self.create_event(
            "Database administrator ran maintenance script to optimize query performance",
            "non_compliant",
            "DBA accessing customer credit card data without justification"
        ))

        # Scenario 5: Account sharing
        scenarios.append(self.create_event(
            "Service account api_automation_prod performed batch data processing job - 10,000 records updated",
            "non_compliant",
            "Multiple users sharing service account credentials"
        ))

        return pd.DataFrame(scenarios)

    def test_zero_day_patterns(self) -> pd.DataFrame:
        """
        Test 4: Novel attack patterns (zero-days)
        """
        scenarios = []

        # Scenario 1: Supply chain compromise
        scenarios.append(self.create_event(
            "NPM package manager installed @company/shared-utils@3.5.2 - dependency tree updated successfully",
            "non_compliant",
            "Compromised NPM package with embedded backdoor"
        ))

        # Scenario 2: Container escape
        scenarios.append(self.create_event(
            "Docker container webapp-prod-container-07 restarted due to memory optimization - service resumed normally",
            "non_compliant",
            "Container escape attempt to host system"
        ))

        # Scenario 3: API abuse
        scenarios.append(self.create_event(
            "REST API endpoint /api/v2/users processed 50 requests with valid authentication tokens",
            "non_compliant",
            "API rate limit bypass using stolen tokens"
        ))

        # Scenario 4: ML model poisoning
        scenarios.append(self.create_event(
            "Machine learning model training job completed - model accuracy: 94.5% on validation set",
            "non_compliant",
            "Training data poisoned with adversarial examples"
        ))

        # Scenario 5: Cloud metadata exploitation
        scenarios.append(self.create_event(
            "EC2 instance i-0abc123def retrieved instance metadata for auto-scaling configuration",
            "non_compliant",
            "SSRF attack accessing AWS metadata endpoint for credentials"
        ))

        return pd.DataFrame(scenarios)

    def evaluate_detection(self, df: pd.DataFrame, scenario_name: str) -> dict:
        """Evaluate model's detection on adversarial scenarios"""

        predictions, probabilities = self.classifier.predict(df)

        y_true = df['compliance_status'].values
        detected = sum(1 for true, pred in zip(y_true, predictions)
                      if true == 'non_compliant' and pred == 'non_compliant')
        missed = sum(1 for true, pred in zip(y_true, predictions)
                    if true == 'non_compliant' and pred == 'compliant')

        detection_rate = detected / len(df) * 100 if len(df) > 0 else 0

        results = {
            'scenario': scenario_name,
            'total_attacks': len(df),
            'detected': detected,
            'missed': missed,
            'detection_rate': float(detection_rate),
            'avg_confidence': float(np.mean(probabilities)),
            'predictions': list(predictions),
            'true_labels': list(y_true)
        }

        return results

    def run_all_tests(self) -> dict:
        """Run all adversarial tests"""

        logger.info("Running adversarial tests on clean model...")

        all_results = {}

        # Test 1: Benign-looking attacks
        print("\n🎯 Test 1: Benign-Looking Attacks")
        print("-" * 80)
        benign_df = self.test_benign_looking_attacks()
        results1 = self.evaluate_detection(benign_df, "Benign-Looking Attacks")
        all_results['benign_looking'] = results1
        self._print_results(results1)

        # Test 2: Evasion techniques
        print("\n🎯 Test 2: Evasion Techniques")
        print("-" * 80)
        evasion_df = self.test_evasion_techniques()
        results2 = self.evaluate_detection(evasion_df, "Evasion Techniques")
        all_results['evasion'] = results2
        self._print_results(results2)

        # Test 3: Insider threats
        print("\n🎯 Test 3: Insider Threats")
        print("-" * 80)
        insider_df = self.test_insider_threats()
        results3 = self.evaluate_detection(insider_df, "Insider Threats")
        all_results['insider_threats'] = results3
        self._print_results(results3)

        # Test 4: Zero-day patterns
        print("\n🎯 Test 4: Zero-Day Patterns")
        print("-" * 80)
        zeroday_df = self.test_zero_day_patterns()
        results4 = self.evaluate_detection(zeroday_df, "Zero-Day Patterns")
        all_results['zero_day'] = results4
        self._print_results(results4)

        return all_results

    def _print_results(self, results: dict):
        """Print results for a test"""
        print(f"Total Attacks: {results['total_attacks']}")
        print(f"Detected: {results['detected']} ✅")
        print(f"Missed: {results['missed']} {'🚨' if results['missed'] > 0 else ''}")
        print(f"Detection Rate: {results['detection_rate']:.1f}%")
        print(f"Avg Confidence: {results['avg_confidence']:.2%}")


def main():
    """Main test runner"""

    print("\n" + "="*80)
    print("ADVERSARIAL SCENARIO TESTING - CLEAN MODEL")
    print("="*80)
    print()
    print("Testing realistic attack scenarios that:")
    print("  • Look like normal operations")
    print("  • Use evasion techniques")
    print("  • Come from insider threats")
    print("  • Use novel/zero-day patterns")
    print()
    print("Model: xgboost_no_leakage (99.09% accuracy, NO data leakage)")
    print("="*80)

    tester = AdversarialTester()
    results = tester.run_all_tests()

    # Overall summary
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)

    total_attacks = sum(r['total_attacks'] for r in results.values())
    total_detected = sum(r['detected'] for r in results.values())
    total_missed = sum(r['missed'] for r in results.values())
    overall_rate = (total_detected / total_attacks * 100) if total_attacks > 0 else 0

    print(f"\nTotal Adversarial Attacks: {total_attacks}")
    print(f"Total Detected: {total_detected}")
    print(f"Total Missed: {total_missed}")
    print(f"Overall Detection Rate: {overall_rate:.1f}%")
    print()

    if overall_rate >= 80:
        print("✅ EXCELLENT: Model detects >80% of novel attacks!")
        print("   Model shows strong generalization to adversarial scenarios.")
        assessment = "EXCELLENT"
    elif overall_rate >= 60:
        print("✅ GOOD: Model detects >60% of novel attacks")
        print("   Acceptable for production with monitoring.")
        assessment = "GOOD"
    elif overall_rate >= 40:
        print("⚠️  FAIR: Model detects >40% of novel attacks")
        print("   Needs improvement before production deployment.")
        assessment = "FAIR"
    else:
        print("❌ POOR: Model detects <40% of novel attacks")
        print("   Requires significant retraining with diverse data.")
        assessment = "POOR"

    # Save results
    output = {
        'test_results': results,
        'overall': {
            'total_attacks': total_attacks,
            'detected': total_detected,
            'missed': total_missed,
            'detection_rate': float(overall_rate),
            'assessment': assessment
        },
        'tested_at': datetime.now().isoformat(),
        'model': 'xgboost_no_leakage'
    }

    output_file = Path("results/models/xgboost_no_leakage/adversarial_test_results.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print("="*80)


if __name__ == '__main__':
    main()
