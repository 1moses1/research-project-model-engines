#!/usr/bin/env python3
"""
Test script for Rwanda NCSA Compliance Monitoring in Kubernetes
Tests real-time violation detection from simulated pods

Author: Moise Iradukunda (CMU)
Date: November 2025
"""

import requests
import json
import time
from datetime import datetime
from typing import List, Dict

# API endpoint
API_URL = "http://localhost:8080"

# Test scenarios mapping to violation pods
VIOLATION_SCENARIOS = [
    {
        "name": "Unauthorized SSH Access",
        "log_message": "FAILED SSH login attempt from 192.168.1.100 for user admin - Access denied",
        "control_id": "AC-3",
        "control_family": "Access Control",
        "framework": "NIST",
        "expected": "non_compliant",
        "pod": "violation-unauthorized-ssh",
        "severity": "HIGH"
    },
    {
        "name": "Phishing Detection",
        "log_message": "ALERT: Suspicious email detected from external domain - Potential phishing attempt blocked",
        "control_id": "SI-4",
        "control_family": "System and Information Integrity",
        "framework": "NIST",
        "expected": "non_compliant",
        "pod": "violation-phishing",
        "severity": "HIGH"
    },
    {
        "name": "Data Exfiltration",
        "log_message": "WARNING: Large data transfer detected to unknown IP 203.0.113.50 - 5GB in 10 minutes",
        "control_id": "AC-4",
        "control_family": "Access Control",
        "framework": "NIST",
        "expected": "non_compliant",
        "pod": "violation-data-exfil",
        "severity": "CRITICAL"
    },
    {
        "name": "Privilege Escalation",
        "log_message": "CRITICAL: User jdoe attempted sudo privilege escalation - Permission denied",
        "control_id": "AC-6",
        "control_family": "Access Control",
        "framework": "NIST",
        "expected": "non_compliant",
        "pod": "violation-priv-escalation",
        "severity": "CRITICAL"
    },
    {
        "name": "Malware Detection",
        "log_message": "ALERT: Malicious file detected - trojan.exe quarantined by antivirus",
        "control_id": "SI-3",
        "control_family": "System and Information Integrity",
        "framework": "NIST",
        "expected": "non_compliant",
        "pod": "violation-malware",
        "severity": "CRITICAL"
    },
    {
        "name": "DDoS Attack",
        "log_message": "CRITICAL: DDoS attack detected - 100000 requests/sec from botnet - Rate limiting activated",
        "control_id": "SC-5",
        "control_family": "System and Communications Protection",
        "framework": "NIST",
        "expected": "non_compliant",
        "pod": "violation-ddos",
        "severity": "CRITICAL"
    },
    {
        "name": "Insider Threat",
        "log_message": "WARNING: Employee accessing sensitive customer database outside business hours - Anomalous behavior flagged",
        "control_id": "PS-3",
        "control_family": "Personnel Security",
        "framework": "NIST",
        "expected": "non_compliant",
        "pod": "violation-insider-threat",
        "severity": "MEDIUM"
    },
    {
        "name": "Compliant Activity (Baseline)",
        "log_message": "INFO: User logged in successfully with MFA - Account access granted",
        "control_id": "AC-2",
        "control_family": "Access Control",
        "framework": "NIST",
        "expected": "compliant",
        "pod": "compliant-activity",
        "severity": "NONE"
    }
]

def test_health():
    """Test API health endpoint"""
    print("\n" + "="*80)
    print("TESTING API HEALTH")
    print("="*80)

    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ API Status: {data['status']}")
            print(f"✓ Model: {data['model']}")
            print(f"✓ Version: {data['version']}")
            print(f"✓ Accuracy: {data['accuracy']}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_prediction(scenario: Dict) -> Dict:
    """Test a single prediction"""
    payload = {
        "log_message": scenario["log_message"],
        "control_id": scenario["control_id"],
        "control_family": scenario["control_family"],
        "framework": scenario["framework"]
    }

    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()

            # Check if prediction matches expected
            correct = result["compliance_status"] == scenario["expected"]

            return {
                "success": True,
                "correct": correct,
                "result": result,
                "scenario": scenario
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "scenario": scenario
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "scenario": scenario
        }

def run_tests():
    """Run all violation detection tests"""
    print("\n" + "="*80)
    print("TESTING COMPLIANCE VIOLATION DETECTION")
    print("="*80)
    print(f"\nTesting {len(VIOLATION_SCENARIOS)} scenarios...\n")

    results = []
    correct_predictions = 0
    total_tests = len(VIOLATION_SCENARIOS)

    for i, scenario in enumerate(VIOLATION_SCENARIOS, 1):
        print(f"\n[{i}/{total_tests}] Testing: {scenario['name']}")
        print(f"    Pod: {scenario['pod']}")
        print(f"    Control: {scenario['control_id']} ({scenario['control_family']})")
        print(f"    Severity: {scenario['severity']}")
        print(f"    Log: {scenario['log_message'][:80]}...")

        result = test_prediction(scenario)
        results.append(result)

        if result["success"]:
            prediction = result["result"]
            confidence = prediction["confidence"]
            status = prediction["compliance_status"]

            if result["correct"]:
                print(f"    ✓ CORRECT: {status.upper()} (confidence: {confidence:.1%})")
                correct_predictions += 1
            else:
                print(f"    ✗ WRONG: Predicted {status}, expected {scenario['expected']}")
                print(f"      Confidence: {confidence:.1%}")
        else:
            print(f"    ✗ ERROR: {result['error']}")

        time.sleep(0.5)  # Avoid overwhelming the API

    return results, correct_predictions, total_tests

def print_summary(results: List[Dict], correct: int, total: int):
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    accuracy = (correct / total) * 100 if total > 0 else 0

    print(f"\nTotal Tests: {total}")
    print(f"Correct Predictions: {correct}")
    print(f"Wrong Predictions: {total - correct}")
    print(f"Test Accuracy: {accuracy:.2f}%")

    # Breakdown by severity
    print("\n" + "-"*80)
    print("BREAKDOWN BY SEVERITY")
    print("-"*80)

    severity_stats = {}
    for result in results:
        if result["success"]:
            severity = result["scenario"]["severity"]
            if severity not in severity_stats:
                severity_stats[severity] = {"total": 0, "correct": 0}
            severity_stats[severity]["total"] += 1
            if result["correct"]:
                severity_stats[severity]["correct"] += 1

    for severity in ["CRITICAL", "HIGH", "MEDIUM", "NONE"]:
        if severity in severity_stats:
            stats = severity_stats[severity]
            sev_accuracy = (stats["correct"] / stats["total"]) * 100
            print(f"{severity:>10}: {stats['correct']}/{stats['total']} correct ({sev_accuracy:.1f}%)")

    # Breakdown by compliance status
    print("\n" + "-"*80)
    print("BREAKDOWN BY EXPECTED STATUS")
    print("-"*80)

    compliant_stats = {"total": 0, "correct": 0}
    non_compliant_stats = {"total": 0, "correct": 0}

    for result in results:
        if result["success"]:
            if result["scenario"]["expected"] == "compliant":
                compliant_stats["total"] += 1
                if result["correct"]:
                    compliant_stats["correct"] += 1
            else:
                non_compliant_stats["total"] += 1
                if result["correct"]:
                    non_compliant_stats["correct"] += 1

    if compliant_stats["total"] > 0:
        comp_acc = (compliant_stats["correct"] / compliant_stats["total"]) * 100
        print(f"Compliant Events: {compliant_stats['correct']}/{compliant_stats['total']} correct ({comp_acc:.1f}%)")

    if non_compliant_stats["total"] > 0:
        non_comp_acc = (non_compliant_stats["correct"] / non_compliant_stats["total"]) * 100
        print(f"Non-Compliant Events: {non_compliant_stats['correct']}/{non_compliant_stats['total']} correct ({non_comp_acc:.1f}%)")

    # Detailed results
    print("\n" + "-"*80)
    print("DETAILED RESULTS")
    print("-"*80)

    for result in results:
        if result["success"] and result["result"]:
            scenario = result["scenario"]
            prediction = result["result"]

            status_icon = "✓" if result["correct"] else "✗"
            print(f"\n{status_icon} {scenario['name']}")
            print(f"   Pod: {scenario['pod']}")
            print(f"   Expected: {scenario['expected']}")
            print(f"   Predicted: {prediction['compliance_status']}")
            print(f"   Confidence: {prediction['confidence']:.1%}")
            print(f"   Probabilities:")
            print(f"      - Compliant: {prediction['probabilities']['compliant']:.1%}")
            print(f"      - Non-Compliant: {prediction['probabilities']['non_compliant']:.1%}")

def save_results(results: List[Dict]):
    """Save results to JSON file"""
    output_file = "k8s_compliance_test_results.json"

    output = {
        "test_date": datetime.utcnow().isoformat() + "Z",
        "total_tests": len(results),
        "results": []
    }

    for result in results:
        if result["success"]:
            output["results"].append({
                "scenario": result["scenario"]["name"],
                "pod": result["scenario"]["pod"],
                "control_id": result["scenario"]["control_id"],
                "severity": result["scenario"]["severity"],
                "expected": result["scenario"]["expected"],
                "predicted": result["result"]["compliance_status"],
                "confidence": result["result"]["confidence"],
                "correct": result["correct"]
            })

    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\n✓ Results saved to: {output_file}")

def main():
    """Main test function"""
    print("="*80)
    print("Rwanda NCSA Compliance Monitoring - Kubernetes Test Suite")
    print("="*80)
    print(f"Test Date: {datetime.utcnow().isoformat()}Z")
    print(f"API Endpoint: {API_URL}")

    # Test health
    if not test_health():
        print("\n✗ Health check failed. Exiting.")
        return 1

    # Run violation tests
    results, correct, total = run_tests()

    # Print summary
    print_summary(results, correct, total)

    # Save results
    save_results(results)

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

    return 0 if correct == total else 1

if __name__ == "__main__":
    exit(main())
