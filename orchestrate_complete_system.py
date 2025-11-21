#!/usr/bin/env python3
"""
Complete System Orchestrator
Coordinates all components: Dataset download, NLP processing, RAG, XGBoost, SIEM/SOAR integration
"""

import sys
from pathlib import Path
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_pipeline.dataset_downloader import SecurityDatasetDownloader
from nlp.unstructured_processor import UnstructuredSecurityProcessor
from nlp.rag_engine import RAGComplianceEngine
from integrations.siem_soar_adapter import SecuritySystemIntegration
from training.continuous_learning_pipeline import ContinuousLearningPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ComplianceSystemOrchestrator:
    """
    Master orchestrator for complete compliance system
    """

    def __init__(self):
        self.dataset_downloader = None
        self.nlp_processor = None
        self.rag_engine = None
        self.siem_integrator = None
        self.learning_pipeline = None

        self.initialization_log = []

    def initialize_system(self, download_datasets: bool = False):
        """Initialize all system components"""
        logger.info("\n" + "="*100)
        logger.info("INITIALIZING COMPLETE COMPLIANCE SYSTEM")
        logger.info("="*100 + "\n")

        # Step 1: Download datasets (if requested)
        if download_datasets:
            logger.info("Step 1: Downloading security datasets...")
            try:
                self.dataset_downloader = SecurityDatasetDownloader()
                download_results = self.dataset_downloader.download_all(parallel=True)
                self.initialization_log.append({
                    'step': 'dataset_download',
                    'status': 'success',
                    'details': download_results
                })
                logger.info("  ✓ Datasets downloaded")
            except Exception as e:
                logger.error(f"  ✗ Dataset download failed: {e}")
                self.initialization_log.append({
                    'step': 'dataset_download',
                    'status': 'failed',
                    'error': str(e)
                })
        else:
            logger.info("Step 1: Skipping dataset download (download_datasets=False)")
            self.initialization_log.append({
                'step': 'dataset_download',
                'status': 'skipped'
            })

        # Step 2: Initialize NLP processor
        logger.info("\nStep 2: Initializing NLP processor...")
        try:
            self.nlp_processor = UnstructuredSecurityProcessor()
            self.initialization_log.append({
                'step': 'nlp_processor',
                'status': 'success'
            })
            logger.info("  ✓ NLP processor ready")
        except Exception as e:
            logger.error(f"  ✗ NLP processor failed: {e}")
            self.initialization_log.append({
                'step': 'nlp_processor',
                'status': 'failed',
                'error': str(e)
            })

        # Step 3: Initialize RAG engine
        logger.info("\nStep 3: Initializing RAG engine...")
        try:
            self.rag_engine = RAGComplianceEngine(
                xgboost_model_path="results/models/xgboost_no_leakage/xgboost_model_no_leakage"
            )
            self.initialization_log.append({
                'step': 'rag_engine',
                'status': 'success'
            })
            logger.info("  ✓ RAG engine ready")
        except Exception as e:
            logger.warning(f"  ⚠ RAG engine failed (non-critical): {e}")
            self.initialization_log.append({
                'step': 'rag_engine',
                'status': 'warning',
                'error': str(e)
            })

        # Step 4: Initialize SIEM/SOAR integrator
        logger.info("\nStep 4: Initializing SIEM/SOAR integrator...")
        try:
            self.siem_integrator = SecuritySystemIntegration()
            self.initialization_log.append({
                'step': 'siem_integrator',
                'status': 'success'
            })
            logger.info("  ✓ SIEM/SOAR integrator ready")
        except Exception as e:
            logger.error(f"  ✗ SIEM/SOAR integrator failed: {e}")
            self.initialization_log.append({
                'step': 'siem_integrator',
                'status': 'failed',
                'error': str(e)
            })

        # Step 5: Initialize continuous learning pipeline
        logger.info("\nStep 5: Initializing continuous learning pipeline...")
        try:
            self.learning_pipeline = ContinuousLearningPipeline()
            self.initialization_log.append({
                'step': 'learning_pipeline',
                'status': 'success'
            })
            logger.info("  ✓ Continuous learning pipeline ready")
        except Exception as e:
            logger.error(f"  ✗ Learning pipeline failed: {e}")
            self.initialization_log.append({
                'step': 'learning_pipeline',
                'status': 'failed',
                'error': str(e)
            })

        logger.info("\n" + "="*100)
        logger.info("SYSTEM INITIALIZATION COMPLETE")
        logger.info("="*100 + "\n")

        return self.initialization_log

    def process_unstructured_input(self, raw_text: str, output_format: str = 'json') -> Dict:
        """
        Complete pipeline: unstructured text → structured analysis → SIEM format

        Args:
            raw_text: Any unstructured security text
            output_format: Output format (json, cef, leef, syslog, xsoar, phantom)

        Returns:
            Complete analysis with formatting
        """
        logger.info(f"Processing unstructured input ({len(raw_text)} chars)...")

        # Step 1: Process with NLP
        structured = self.nlp_processor.process(raw_text)

        # Step 2: Augment with RAG (if available)
        if self.rag_engine:
            augmented = self.rag_engine.knowledge_base.augment_with_context(raw_text, structured)
        else:
            augmented = structured

        # Step 3: Format for SIEM/SOAR (if requested)
        if output_format != 'json':
            if output_format in ['xsoar', 'phantom']:
                formatted = self.siem_integrator.create_soar_incident(augmented, output_format)
            else:
                formatted = self.siem_integrator.format_for_system(augmented, output_format)

            augmented['formatted_output'] = formatted
            augmented['output_format'] = output_format

        logger.info(f"  ✓ Processed: {augmented['compliance_status']} ({augmented['confidence_score']:.1%})")

        return augmented

    def batch_process(self, inputs: List[str], output_format: str = 'json') -> List[Dict]:
        """Process multiple inputs"""
        logger.info(f"Batch processing {len(inputs)} inputs...")

        results = []
        for i, text in enumerate(inputs, 1):
            logger.info(f"  Processing {i}/{len(inputs)}...")
            result = self.process_unstructured_input(text, output_format)
            results.append(result)

        return results

    def demonstrate_system(self):
        """Demonstrate complete system with real-world examples"""
        logger.info("\n" + "="*100)
        logger.info("SYSTEM DEMONSTRATION - END-TO-END PIPELINE")
        logger.info("="*100 + "\n")

        # Real-world test cases
        test_cases = [
            {
                'name': 'Unauthorized Access Attempt',
                'text': '2025-11-02T14:30:00 - CRITICAL: Unauthorized wire transfer of $50,000 to external account ACC-789 denied by fraud detection system. Source IP: 192.168.1.100, User: finance_admin',
                'expected': 'non_compliant'
            },
            {
                'name': 'Successful Authentication',
                'text': '2025-11-02T09:15:00 - INFO: User john.doe@company.rw successfully authenticated via multi-factor authentication. Login from IP: 10.0.0.25, VPN connection established.',
                'expected': 'compliant'
            },
            {
                'name': 'Ransomware Detection',
                'text': '2025-11-02T02:45:00 - ALERT: Ransomware activity detected on file server FS-PROD-01. Process: encrypt.exe (SHA256: abc123...). 500 files encrypted in last 60 seconds. Immediate containment required!',
                'expected': 'non_compliant'
            },
            {
                'name': 'Phishing Email Blocked',
                'text': 'Email Security Gateway blocked phishing attempt: From attacker@malicious.com, Subject: "Urgent: Update your credentials", Malware attachment: invoice.pdf.exe. Recipient: finance_team@company.rw',
                'expected': 'non_compliant'
            },
            {
                'name': 'System Backup Completed',
                'text': '2025-11-02T03:00:00 - SUCCESS: Automated system backup completed. 2TB data backed up to secure cloud storage. Encryption verified. Backup integrity check passed.',
                'expected': 'compliant'
            },
            {
                'name': 'Vulnerability Scan Results',
                'text': 'Vulnerability scan completed on web-server-prod. Found: CVE-2024-1234 (Critical - SQL Injection), CVE-2024-5678 (High - XSS). Remediation required within 48 hours per NCSA standards.',
                'expected': 'non_compliant'
            },
            {
                'name': 'Insider Threat - Excessive Data Access',
                'text': '2025-11-02T23:30:00 - WARNING: HR Manager accessed 500 employee records outside business hours. Normal pattern: 20 records/day during business hours. Potential data exfiltration.',
                'expected': 'non_compliant'
            },
            {
                'name': 'Compliance Audit Passed',
                'text': 'Annual Rwanda NCSA compliance audit completed. All 15 minimum cybersecurity standards verified. Access controls: PASS, Incident response: PASS, Data protection: PASS, Network security: PASS.',
                'expected': 'compliant'
            }
        ]

        results = []

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*100}")
            print(f"Test Case {i}: {test_case['name']}")
            print(f"{'='*100}")
            print(f"Input: {test_case['text'][:80]}...")
            print()

            # Process
            result = self.process_unstructured_input(test_case['text'], output_format='json')

            # Display results
            print(f"Prediction: {result['compliance_status'].upper()}")
            print(f"Expected: {test_case['expected'].upper()}")
            print(f"Confidence: {result['confidence_score']:.1%}")
            print(f"Severity: {result['severity']}")
            print(f"Control: {result['control_id']} - {result['control_family']}")
            print(f"MITRE Tactics: {', '.join(result['mitre_tactics'][:3])}")

            if 'rag_context' in result:
                rag = result['rag_context']
                print(f"RAG Context: {rag.get('retrieved_documents', 0)} documents retrieved")

            # Correctness
            correct = result['compliance_status'] == test_case['expected']
            print(f"Correctness: {'✓ CORRECT' if correct else '✗ INCORRECT'}")

            # Format for SIEM systems
            print(f"\nSIEM Formats:")
            print(f"  CEF: {self.siem_integrator.format_for_system(result, 'cef')[:100]}...")
            print(f"  LEEF: {self.siem_integrator.format_for_system(result, 'leef')[:100]}...")

            results.append({
                'test_case': test_case['name'],
                'expected': test_case['expected'],
                'predicted': result['compliance_status'],
                'confidence': result['confidence_score'],
                'correct': correct
            })

        # Summary
        print(f"\n{'='*100}")
        print("DEMONSTRATION SUMMARY")
        print(f"{'='*100}")

        total = len(results)
        correct = sum(1 for r in results if r['correct'])
        accuracy = correct / total * 100

        print(f"\nTotal Test Cases: {total}")
        print(f"Correct Predictions: {correct}")
        print(f"Accuracy: {accuracy:.1f}%")
        print()

        for result in results:
            status = "✓" if result['correct'] else "✗"
            print(f"{status} {result['test_case']}: {result['predicted']} ({result['confidence']:.1%})")

        print(f"\n{'='*100}\n")

        return results

    def save_report(self, results: List[Dict], filename: str = "system_test_report.json"):
        """Save test results to file"""
        report = {
            'test_timestamp': datetime.now().isoformat(),
            'initialization_log': self.initialization_log,
            'test_results': results,
            'summary': {
                'total_tests': len(results),
                'correct_predictions': sum(1 for r in results if r['correct']),
                'accuracy': sum(1 for r in results if r['correct']) / len(results) if results else 0
            }
        }

        output_file = Path(filename)
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"Report saved to: {output_file}")

        return report


def main():
    """Main orchestrator entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Complete Compliance System Orchestrator")
    parser.add_argument('--download', action='store_true', help='Download security datasets')
    parser.add_argument('--demo', action='store_true', help='Run system demonstration')
    parser.add_argument('--input', type=str, help='Process single input text')
    parser.add_argument('--format', type=str, default='json',
                       choices=['json', 'cef', 'leef', 'syslog', 'xsoar', 'phantom'],
                       help='Output format')

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = ComplianceSystemOrchestrator()
    orchestrator.initialize_system(download_datasets=args.download)

    # Run demonstration
    if args.demo:
        results = orchestrator.demonstrate_system()
        orchestrator.save_report(results)

    # Process single input
    elif args.input:
        result = orchestrator.process_unstructured_input(args.input, output_format=args.format)
        print("\n" + "="*100)
        print("RESULT")
        print("="*100)
        print(json.dumps(result, indent=2, default=str))

    else:
        print("\nUsage:")
        print("  # Run full demonstration:")
        print("  python orchestrate_complete_system.py --demo")
        print()
        print("  # Download datasets and run demo:")
        print("  python orchestrate_complete_system.py --download --demo")
        print()
        print("  # Process single input:")
        print('  python orchestrate_complete_system.py --input "Unauthorized access denied" --format cef')


if __name__ == '__main__':
    main()
