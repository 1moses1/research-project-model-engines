"""
Fraud Detection Simulation Test for XGBoost Model

Simulates various fraud scenarios to evaluate XGBoost's detection capabilities:
1. Financial fraud (unauthorized transactions)
2. Account takeover attacks
3. Privilege escalation
4. Data exfiltration
5. Authentication bypass
6. Insider threats

Author: Moise Iradukunda (CMU)
Date: October 2025
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))
from src.models.xgboost_classifier import XGBoostClassifier
from src.utils.logger import setup_logger


class FraudSimulator:
    """Simulate various fraud scenarios for model testing."""

    def __init__(self):
        """Initialize fraud simulator."""
        self.logger = setup_logger("fraud_simulator", "logs/fraud_simulation.log")
        self.model = XGBoostClassifier()

        # Load the trained model
        model_path = Path("results/explainability/xgboost_model")
        if model_path.exists():
            self.logger.info(f"Loading trained model from {model_path}")
            self.model.load_model(str(model_path))
            self.logger.info("Model loaded successfully")
        else:
            raise FileNotFoundError(f"Trained model not found at {model_path}")

        self.logger.info("Fraud Simulator initialized with XGBoost model")

    def generate_financial_fraud(self, num_samples: int = 100) -> pd.DataFrame:
        """
        Simulate financial fraud scenarios.

        Examples:
        - Unauthorized money transfers
        - Card fraud
        - Account manipulation
        """
        self.logger.info(f"Generating {num_samples} financial fraud scenarios")

        fraud_scenarios = []

        fraud_templates = [
            # Unauthorized transfers
            "Unauthorized wire transfer of ${amount} to account {account} from IP {ip} - Access denied",
            "Failed transaction: Insufficient privileges for user {user} attempting ${amount} transfer",
            "Suspicious transfer detected: ${amount} to offshore account {account} - Blocked",
            "Multiple failed authorization attempts for transaction ${amount} from {user}",
            "Alert: Large withdrawal ${amount} outside business hours by {user}",

            # Card fraud
            "Card not present transaction ${amount} declined - velocity check failed",
            "Suspicious card activity: {user} card used in {country} while active in Rwanda",
            "CVV mismatch on transaction ${amount} - Card declined",
            "Multiple declined transactions from IP {ip} - Possible card testing",
            "High-risk merchant transaction ${amount} blocked for account {account}",

            # Account manipulation
            "Unauthorized account balance modification attempt by {user} - Audit log AC-2",
            "Privilege escalation detected: {user} attempting admin access to financial records",
            "Database query from {user}: SELECT * FROM accounts WHERE balance > 1000000 - Blocked",
            "SQL injection attempt in transaction API from IP {ip} - Attack blocked",
            "Attempted modification of transaction history by {user} at {time} - Failed",

            # Money laundering patterns
            "Structured transactions detected: {count} deposits of ${small_amount} by {user}",
            "Round-dollar transaction pattern: ${amount} - Possible structuring",
            "Rapid transfer cycle: ${amount} through {count} accounts in {minutes} minutes",
            "Cross-border transfer ${amount} to high-risk jurisdiction - Flagged",
            "Unusual transaction pattern: {count} transfers to new beneficiaries in 24 hours"
        ]

        for i in range(num_samples):
            template = random.choice(fraud_templates)

            log_message = template.format(
                amount=random.randint(10000, 5000000),
                account=f"ACC{random.randint(100000, 999999)}",
                ip=f"41.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                user=random.choice(['admin', 'cashier', 'teller', 'manager', 'clerk']) + str(random.randint(1, 50)),
                country=random.choice(['Nigeria', 'Kenya', 'UAE', 'China', 'Russia']),
                time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                count=random.randint(3, 15),
                small_amount=random.randint(500, 9500),
                minutes=random.randint(5, 30)
            )

            # Map to appropriate controls
            if 'transfer' in log_message.lower() or 'transaction' in log_message.lower():
                control_id = 'AC-3'  # Access Enforcement
                control_family = 'Access Control'
            elif 'privilege' in log_message.lower() or 'admin' in log_message.lower():
                control_id = 'AC-6'  # Least Privilege
                control_family = 'Access Control'
            elif 'sql' in log_message.lower() or 'database' in log_message.lower():
                control_id = 'SI-3'  # Malicious Code Protection
                control_family = 'System and Information Integrity'
            else:
                control_id = 'AU-6'  # Audit Review
                control_family = 'Audit and Accountability'

            fraud_scenarios.append({
                'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 720))).isoformat(),
                'log_message': log_message,
                'control_id': control_id,
                'control_family': control_family,
                'framework': 'NIST',
                'source_ip': f"41.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'user': random.choice(['admin', 'cashier', 'teller', 'manager', 'clerk']) + str(random.randint(1, 50)),
                'expected_status': 'non-compliant',
                'fraud_type': 'financial_fraud'
            })

        return pd.DataFrame(fraud_scenarios)

    def generate_account_takeover(self, num_samples: int = 100) -> pd.DataFrame:
        """Simulate account takeover attacks."""
        self.logger.info(f"Generating {num_samples} account takeover scenarios")

        takeover_scenarios = []

        takeover_templates = [
            # Credential theft
            "Multiple failed login attempts for {user} from IP {ip} - Account locked after 5 failures",
            "Login from unusual location: {user} accessed from {country} (normal: Rwanda)",
            "Password change request from unverified device for user {user}",
            "Brute force attack detected: {attempts} login attempts in {minutes} minutes for {user}",
            "Suspicious login: {user} session from {ip} - Device fingerprint mismatch",

            # Session hijacking
            "Session token reuse detected for user {user} - Possible session hijacking",
            "Concurrent sessions from different countries for {user}: Rwanda and {country}",
            "Session timeout bypassed for user {user} - Unauthorized access attempt",
            "Cookie manipulation detected for session {session_id} - Access denied",
            "User {user} session active from {count} different IPs simultaneously",

            # MFA bypass attempts
            "MFA challenge failed {count} times for user {user}",
            "Attempted MFA bypass using old authentication token for {user}",
            "SMS verification code requested {count} times in {minutes} minutes for {user}",
            "MFA device enrollment from suspicious IP {ip} for user {user}",
            "Backup codes used after recent password change for {user} - Flagged",

            # Account manipulation
            "Unauthorized email change attempt for user {user} from IP {ip}",
            "Phone number modification without MFA verification for {user}",
            "Security questions reset from unrecognized device for {user}",
            "Account recovery initiated from high-risk IP {ip} for user {user}",
            "Simultaneous password reset requests from {count} different IPs for {user}"
        ]

        for i in range(num_samples):
            template = random.choice(takeover_templates)

            log_message = template.format(
                user=random.choice(['john.doe', 'jane.smith', 'admin', 'manager', 'ceo']) + str(random.randint(1, 100)),
                ip=f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                country=random.choice(['Nigeria', 'China', 'Russia', 'Ukraine', 'Iran']),
                attempts=random.randint(10, 100),
                minutes=random.randint(1, 10),
                session_id=f"SID{random.randint(100000, 999999)}",
                count=random.randint(3, 20)
            )

            takeover_scenarios.append({
                'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 720))).isoformat(),
                'log_message': log_message,
                'control_id': 'IA-2',  # Identification and Authentication
                'control_family': 'Identification and Authentication',
                'framework': 'NIST',
                'source_ip': f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'user': random.choice(['john.doe', 'jane.smith', 'admin', 'manager']) + str(random.randint(1, 100)),
                'expected_status': 'non-compliant',
                'fraud_type': 'account_takeover',
            })

        return pd.DataFrame(takeover_scenarios)

    def generate_privilege_escalation(self, num_samples: int = 100) -> pd.DataFrame:
        """Simulate privilege escalation attacks."""
        self.logger.info(f"Generating {num_samples} privilege escalation scenarios")

        escalation_scenarios = []

        escalation_templates = [
            # Unauthorized admin access
            "User {user} attempted to access admin panel without authorization - Denied",
            "Privilege escalation detected: {user} trying to execute admin commands",
            "Unauthorized sudo attempt by {user} on server {server}",
            "User {user} attempted to modify user roles from 'user' to 'admin'",
            "Failed attempt to add {user} to administrators group by non-admin account",

            # System exploitation
            "Buffer overflow attempt detected in service {service} from user {user}",
            "Kernel exploit attempt: {user} trying to gain root access on {server}",
            "DLL injection detected in process {process} initiated by {user}",
            "SetUID bit manipulation attempt on binary {binary} by {user}",
            "Registry modification attempt: {user} trying to disable UAC on {server}",

            # Permission abuse
            "User {user} attempting to read /etc/shadow file - Permission denied",
            "Unauthorized access to confidential database by {user} - Access log AC-6",
            "File permission modification attempt: {user} trying to chmod 777 on {file}",
            "Service account {user} attempting interactive login - Policy violation",
            "User {user} trying to access CEO mailbox without delegation rights",

            # Token manipulation
            "Access token manipulation detected for user {user} - Session terminated",
            "Attempted privilege escalation via token impersonation by {user}",
            "Kerberos ticket granting ticket (TGT) forgery attempt from {user}",
            "NTLM hash pass-the-hash attack detected from IP {ip}",
            "Delegation abuse: {user} attempting to impersonate domain admin"
        ]

        for i in range(num_samples):
            template = random.choice(escalation_templates)

            log_message = template.format(
                user=random.choice(['developer', 'analyst', 'intern', 'contractor', 'guest']) + str(random.randint(1, 50)),
                server=random.choice(['WEB-SRV-01', 'DB-SRV-01', 'APP-SRV-01', 'FILE-SRV-01']),
                service=random.choice(['apache', 'nginx', 'mysql', 'postgresql', 'redis']),
                process=random.choice(['svchost.exe', 'lsass.exe', 'winlogon.exe', 'explorer.exe']),
                binary=random.choice(['/bin/bash', '/usr/bin/sudo', '/sbin/init', '/usr/sbin/sshd']),
                file=random.choice(['/etc/passwd', '/etc/sudoers', 'C:\\Windows\\System32\\config\\SAM']),
                ip=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
            )

            escalation_scenarios.append({
                'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 720))).isoformat(),
                'log_message': log_message,
                'control_id': 'AC-6',  # Least Privilege
                'control_family': 'Access Control',
                'framework': 'NIST',
                'source_ip': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'user': random.choice(['developer', 'analyst', 'intern', 'contractor']) + str(random.randint(1, 50)),
                'expected_status': 'non-compliant',
                'fraud_type': 'privilege_escalation',
            })

        return pd.DataFrame(escalation_scenarios)

    def generate_data_exfiltration(self, num_samples: int = 100) -> pd.DataFrame:
        """Simulate data exfiltration attempts."""
        self.logger.info(f"Generating {num_samples} data exfiltration scenarios")

        exfiltration_scenarios = []

        exfiltration_templates = [
            # Mass data download
            "Unusual data access: {user} downloaded {records} customer records in {minutes} minutes",
            "Large file transfer detected: {user} uploaded {size}GB to external storage",
            "Mass email export: {user} downloaded {count} emails from executive mailboxes",
            "Database dump detected: {user} exported entire {database} database ({records} records)",
            "Bulk download alert: {user} accessed {count} sensitive files in {minutes} minutes",

            # Unauthorized sharing
            "External file sharing detected: {user} shared {count} confidential files via {service}",
            "Email forwarding rule created by {user} to external address {email}",
            "USB device {device} connected by {user} - Unauthorized data copy detected",
            "Cloud sync initiated: {user} syncing {size}GB to personal {service} account",
            "Print job: {user} printed {pages} pages of classified documents",

            # Network exfiltration
            "Unusual outbound traffic: {size}GB transferred to IP {ip} by {user}",
            "DNS tunneling detected from {user} workstation to domain {domain}",
            "Encrypted channel established by {user} to external server {ip}",
            "FTP upload detected: {user} transferred {files} files to {ip}",
            "TOR browser usage detected on {user} workstation - Policy violation",

            # Steganography and covert channels
            "Suspicious image uploads: {user} uploaded {count} large PNG files to {service}",
            "Encoded data in HTTP headers detected from {user} session",
            "Unusual packet timing patterns from {user} - Possible covert channel",
            "Large clipboard copy detected: {user} copied {size}MB to clipboard",
            "Screen recording software detected on {user} workstation"
        ]

        for i in range(num_samples):
            template = random.choice(exfiltration_templates)

            log_message = template.format(
                user=random.choice(['employee', 'contractor', 'intern', 'manager', 'executive']) + str(random.randint(1, 100)),
                records=random.randint(1000, 100000),
                minutes=random.randint(5, 30),
                size=random.randint(1, 500),
                count=random.randint(50, 5000),
                database=random.choice(['customers', 'financials', 'employees', 'transactions']),
                service=random.choice(['Dropbox', 'Google Drive', 'OneDrive', 'WeTransfer']),
                email=f"{random.choice(['attacker', 'competitor', 'external'])}@{random.choice(['gmail.com', 'yahoo.com', 'outlook.com'])}",
                device=f"USB-{random.randint(1000, 9999)}",
                pages=random.randint(100, 1000),
                ip=f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                domain=f"{random.choice(['malicious', 'exfil', 'data'])}.{random.choice(['com', 'net', 'org'])}",
                files=random.randint(10, 1000)
            )

            exfiltration_scenarios.append({
                'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 720))).isoformat(),
                'log_message': log_message,
                'control_id': 'AC-3',  # Access Enforcement
                'control_family': 'Access Control',
                'framework': 'NIST',
                'source_ip': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'user': random.choice(['employee', 'contractor', 'intern', 'manager']) + str(random.randint(1, 100)),
                'expected_status': 'non-compliant',
                'fraud_type': 'data_exfiltration',
            })

        return pd.DataFrame(exfiltration_scenarios)

    def generate_insider_threats(self, num_samples: int = 100) -> pd.DataFrame:
        """Simulate insider threat scenarios."""
        self.logger.info(f"Generating {num_samples} insider threat scenarios")

        insider_scenarios = []

        insider_templates = [
            # Disgruntled employee
            "After-hours access: {user} logged in at {time} - Recently submitted resignation",
            "Source code repository cloned by {user} to personal account - Employee on notice",
            "Unusual interest in sensitive projects: {user} accessed {count} unrelated files",
            "Performance review access: {user} viewed peer reviews without authorization",
            "Salary database queried by {user} - HR access only",

            # Sabotage
            "Critical system configuration changed by {user} outside change window",
            "Backup deletion detected: {user} removed {count} backup sets",
            "Production database credentials changed by {user} without approval",
            "Service disruption: {user} disabled monitoring on {count} critical servers",
            "Malware deployment: {user} uploaded suspicious binary {binary} to shared drive",

            # Espionage
            "Competitive intelligence access: {user} downloaded {competitor} analysis files",
            "Patent application accessed by {user} - Currently interviewing at {competitor}",
            "Trade secret file opened by {user} from home IP {ip}",
            "R&D database queried by {user}: SELECT * FROM unreleased_products",
            "Meeting notes downloaded: {user} accessed executive strategic planning documents",

            # Policy violations
            "Personal project detected: {user} running crypto mining on company server {server}",
            "Moonlighting alert: {user} accessing freelance platform during work hours",
            "Unauthorized software: {user} installed {software} without IT approval",
            "Data hoarding: {user} maintains {size}GB of obsolete customer data",
            "Expense fraud detected: {user} submitted duplicate receipts for ${amount}"
        ]

        for i in range(num_samples):
            template = random.choice(insider_templates)

            log_message = template.format(
                user=random.choice(['disgruntled.emp', 'contractor.exit', 'manager.fired', 'exec.leaving']) + str(random.randint(1, 50)),
                time=f"{random.randint(18, 23)}:{random.randint(0, 59):02d}",
                count=random.randint(10, 500),
                binary=f"suspicious_{random.randint(1000, 9999)}.exe",
                competitor=random.choice(['CompetitorA', 'CompetitorB', 'RivalCorp']),
                ip=f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
                server=random.choice(['PROD-SRV-01', 'APP-SRV-01', 'DB-SRV-01']),
                software=random.choice(['TeamViewer', 'AnyDesk', 'BitTorrent', 'Tor']),
                size=random.randint(10, 500),
                amount=random.randint(500, 5000)
            )

            insider_scenarios.append({
                'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 720))).isoformat(),
                'log_message': log_message,
                'control_id': 'AU-6',  # Audit Review
                'control_family': 'Audit and Accountability',
                'framework': 'NIST',
                'source_ip': f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                'user': random.choice(['disgruntled.emp', 'contractor.exit', 'manager.fired']) + str(random.randint(1, 50)),
                'expected_status': 'non-compliant',
                'fraud_type': 'insider_threat',
            })

        return pd.DataFrame(insider_scenarios)

    def evaluate_fraud_detection(self, fraud_data: pd.DataFrame, fraud_type: str) -> Dict:
        """
        Evaluate model's fraud detection performance.

        Args:
            fraud_data: DataFrame with fraud scenarios
            fraud_type: Type of fraud being tested

        Returns:
            Dictionary with evaluation metrics
        """
        self.logger.info(f"Evaluating fraud detection for: {fraud_type}")

        # Get predictions (returns tuple of labels and probabilities)
        predictions, probabilities = self.model.predict(fraud_data)

        # Calculate metrics
        total = len(fraud_data)
        detected = sum(1 for pred in predictions if pred == 'non_compliant')
        missed = total - detected
        detection_rate = (detected / total) * 100

        # Confidence analysis
        avg_confidence = np.mean(probabilities)
        high_confidence = sum(1 for prob in probabilities if prob > 0.9)
        medium_confidence = sum(1 for prob in probabilities if 0.7 <= prob <= 0.9)
        low_confidence = sum(1 for prob in probabilities if prob < 0.7)

        results = {
            'fraud_type': fraud_type,
            'total_samples': total,
            'detected': detected,
            'missed': missed,
            'detection_rate': round(detection_rate, 2),
            'avg_confidence': round(avg_confidence, 4),
            'high_confidence_count': high_confidence,
            'medium_confidence_count': medium_confidence,
            'low_confidence_count': low_confidence,
            'predictions': list(predictions),
            'probabilities': [float(p) for p in probabilities]
        }

        self.logger.info(f"{fraud_type} - Detection Rate: {detection_rate:.2f}%")
        self.logger.info(f"{fraud_type} - Avg Confidence: {avg_confidence:.4f}")

        return results

    def run_comprehensive_test(self, samples_per_type: int = 100) -> Dict:
        """
        Run comprehensive fraud detection test across all scenarios.

        Args:
            samples_per_type: Number of samples per fraud type

        Returns:
            Complete evaluation results
        """
        print("\n" + "=" * 80)
        print("FRAUD DETECTION SIMULATION TEST")
        print("=" * 80)
        print(f"XGBoost Model Evaluation - {samples_per_type} samples per fraud type")
        print("=" * 80 + "\n")

        all_results = {}
        all_fraud_data = []

        # Test each fraud type
        fraud_generators = [
            ('Financial Fraud', self.generate_financial_fraud),
            ('Account Takeover', self.generate_account_takeover),
            ('Privilege Escalation', self.generate_privilege_escalation),
            ('Data Exfiltration', self.generate_data_exfiltration),
            ('Insider Threats', self.generate_insider_threats)
        ]

        for fraud_name, generator_func in fraud_generators:
            print(f"📊 Testing {fraud_name}...")

            # Generate fraud data
            fraud_data = generator_func(samples_per_type)
            all_fraud_data.append(fraud_data)

            # Evaluate detection
            results = self.evaluate_fraud_detection(fraud_data, fraud_name)
            all_results[fraud_name] = results

            print(f"   ✅ Detection Rate: {results['detection_rate']}%")
            print(f"   📈 Avg Confidence: {results['avg_confidence']:.2%}")
            print(f"   🎯 Detected: {results['detected']}/{results['total_samples']}")
            print(f"   ⚠️  Missed: {results['missed']}")
            print()

        # Combined statistics
        total_fraud = sum(r['total_samples'] for r in all_results.values())
        total_detected = sum(r['detected'] for r in all_results.values())
        overall_detection = (total_detected / total_fraud) * 100

        print("=" * 80)
        print("OVERALL RESULTS")
        print("=" * 80)
        print(f"Total Fraud Scenarios: {total_fraud}")
        print(f"Total Detected: {total_detected}")
        print(f"Total Missed: {total_fraud - total_detected}")
        print(f"Overall Detection Rate: {overall_detection:.2f}%")
        print("=" * 80)

        # Save detailed results
        combined_df = pd.concat(all_fraud_data, ignore_index=True)
        combined_df.to_csv('results/fraud_simulation_data.csv', index=False)

        with open('results/fraud_detection_metrics.json', 'w') as f:
            json.dump(all_results, f, indent=2)

        print(f"\n✅ Results saved:")
        print(f"   - Fraud data: results/fraud_simulation_data.csv")
        print(f"   - Metrics: results/fraud_detection_metrics.json")

        return all_results


def main():
    """Main execution."""
    simulator = FraudSimulator()

    # Run comprehensive test
    results = simulator.run_comprehensive_test(samples_per_type=100)

    # Print summary table
    print("\n" + "=" * 80)
    print("DETECTION SUMMARY BY FRAUD TYPE")
    print("=" * 80)
    print(f"{'Fraud Type':<25} {'Samples':<10} {'Detected':<10} {'Missed':<10} {'Rate':<10}")
    print("-" * 80)

    for fraud_type, metrics in results.items():
        print(f"{fraud_type:<25} {metrics['total_samples']:<10} {metrics['detected']:<10} "
              f"{metrics['missed']:<10} {metrics['detection_rate']:.2f}%")

    print("=" * 80)


if __name__ == "__main__":
    main()
