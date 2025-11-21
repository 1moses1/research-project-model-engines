#!/usr/bin/env python3
"""
Create DDoS Attack and Credential Stuffing Datasets

1. DDoS Attack patterns (volumetric, protocol, application-layer)
2. Credential Stuffing patterns (brute force, dictionary attacks)
"""

import pandas as pd
import numpy as np
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DDoSDataGenerator:
    """Generate DDoS attack logs"""

    def __init__(self, output_dir: str = "data/targeted/ddos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_ddos_logs(self, num_samples: int = 5000):
        """Generate DDoS attack scenarios"""

        logger.info(f"Generating {num_samples:,} DDoS attack logs...")

        ddos_patterns = [
            {
                'type': 'Volumetric - UDP Flood',
                'templates': [
                    'Network traffic spike: {volume} requests/sec from {ips} IPs - Service degradation',
                    'UDP flood detected: {volume} packets/sec from {ips} sources - Bandwidth saturation',
                    'DDoS attack: {volume} requests/sec from {ips} distributed IPs',
                    'Volumetric attack detected: {volume} packets/sec overloading network',
                    'Service disruption: {volume} requests/sec from {ips} IP addresses'
                ],
                'volumes': [50000, 100000, 200000, 500000, 1000000],
                'ip_counts': [100, 200, 500, 1000, 2000]
            },
            {
                'type': 'SYN Flood',
                'templates': [
                    'SYN flood attack: {volume} half-open connections from {ips} IPs',
                    'TCP SYN flood detected: {volume} connection attempts exhausting resources',
                    'Protocol attack: SYN flood with {volume} requests from {ips} sources',
                    'Connection table exhaustion: {volume} SYN packets from botnet',
                    'DDoS SYN flood: {volume} connection requests from {ips} distributed IPs'
                ],
                'volumes': [10000, 50000, 100000, 500000],
                'ip_counts': [50, 100, 200, 500]
            },
            {
                'type': 'HTTP Flood',
                'templates': [
                    'HTTP flood attack: {volume} GET requests/sec from {ips} IPs - Web server overwhelmed',
                    'Application layer DDoS: {volume} HTTP requests from {ips} sources',
                    'Web server under attack: {volume} requests/sec from botnet ({ips} IPs)',
                    'HTTP flood detected: {volume} requests exhausting application resources',
                    'Layer 7 DDoS: {volume} HTTP requests/sec from {ips} distributed IPs'
                ],
                'volumes': [5000, 10000, 50000, 100000],
                'ip_counts': [100, 200, 500, 1000]
            },
            {
                'type': 'DNS Amplification',
                'templates': [
                    'DNS amplification attack: {volume} queries/sec amplified traffic',
                    'Reflection attack: DNS queries from {ips} IPs generating {volume} responses',
                    'DDoS via DNS: {volume} amplified responses overwhelming server',
                    'DNS flood: {volume} queries/sec from open resolvers ({ips} sources)',
                    'Amplification DDoS: {volume} DNS responses from {ips} IP addresses'
                ],
                'volumes': [100000, 500000, 1000000],
                'ip_counts': [50, 100, 200]
            },
            {
                'type': 'Slowloris',
                'templates': [
                    'Slowloris attack detected: {volume} slow HTTP connections tying up server',
                    'Application exhaustion: {volume} persistent connections from {ips} IPs',
                    'Slow POST attack: {volume} incomplete requests keeping connections open',
                    'DDoS via slow connections: {volume} threads exhausted from {ips} sources',
                    'Resource exhaustion: {volume} slow HTTP requests from distributed sources'
                ],
                'volumes': [1000, 5000, 10000, 20000],
                'ip_counts': [20, 50, 100, 200]
            }
        ]

        logs = []
        start_date = datetime.now() - timedelta(days=365)

        for i in range(num_samples):
            pattern = random.choice(ddos_patterns)
            template = random.choice(pattern['templates'])

            timestamp = start_date + timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            volume = random.choice(pattern['volumes'])
            ips = random.choice(pattern['ip_counts'])

            log_message = template.format(volume=f'{volume:,}', ips=ips)

            logs.append({
                'timestamp': timestamp,
                'log_message': log_message,
                'control_id': 'SC-5',  # Denial of Service Protection
                'control_family': 'System and Communications Protection',
                'framework': 'NIST-800-53',
                'compliance_status': 'non_compliant',
                'severity': 'critical',
                'user_id': 'system',
                'source_ip': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'action': 'ddos_attack',
                'resource': 'network_infrastructure',
                'anomaly_type': 'ddos',
                'attack_type': pattern['type'],
                'dataset_source': 'ddos_patterns'
            })

        df = pd.DataFrame(logs)
        logger.info(f"  Generated {len(df):,} DDoS attack logs")
        logger.info(f"  Attack types: {df['attack_type'].value_counts().to_dict()}")

        return df

    def generate_normal_traffic(self, num_samples: int = 2000):
        """Generate normal network traffic logs"""

        logger.info(f"Generating {num_samples:,} normal traffic logs...")

        normal_templates = [
            'Normal traffic pattern: {volume} requests/sec within baseline',
            'HTTP traffic: {volume} requests/sec from legitimate users',
            'Network activity normal: {volume} packets/sec average load',
            'Standard web traffic: {volume} requests/sec serving users',
            'Baseline traffic: {volume} connections/sec normal operations',
            'Web server operating normally: {volume} requests/sec',
            'Network utilization: {volume} packets/sec typical load',
            'Application traffic normal: {volume} requests from users',
            'Standard operations: {volume} connections within parameters',
            'Normal load: {volume} requests/sec serving legitimate traffic'
        ]

        logs = []
        start_date = datetime.now() - timedelta(days=365)

        for i in range(num_samples):
            timestamp = start_date + timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            volume = random.choice([100, 500, 1000, 2000, 5000])  # Normal traffic volumes
            log_message = random.choice(normal_templates).format(volume=f'{volume:,}')

            logs.append({
                'timestamp': timestamp,
                'log_message': log_message,
                'control_id': 'SC-5',
                'control_family': 'System and Communications Protection',
                'framework': 'NIST-800-53',
                'compliance_status': 'compliant',
                'severity': 'info',
                'user_id': 'system',
                'source_ip': f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'action': 'normal_traffic',
                'resource': 'network_infrastructure',
                'anomaly_type': 'none',
                'attack_type': 'normal',
                'dataset_source': 'normal_traffic'
            })

        df = pd.DataFrame(logs)
        logger.info(f"  Generated {len(df):,} normal traffic logs")

        return df


class CredentialStuffingDataGenerator:
    """Generate credential stuffing attack logs"""

    def __init__(self, output_dir: str = "data/targeted/credential_stuffing"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_credential_stuffing_logs(self, num_samples: int = 5000):
        """Generate credential stuffing scenarios"""

        logger.info(f"Generating {num_samples:,} credential stuffing logs...")

        attack_patterns = [
            {
                'type': 'Credential Stuffing',
                'templates': [
                    'Login attempts from {ips} IPs using stolen credentials - {accounts} accounts compromised',
                    'Credential stuffing detected: {attempts} login attempts from {ips} sources',
                    'Automated login attacks: {attempts} attempts from {ips} IPs - {accounts} accounts breached',
                    'Stolen credentials used: {attempts} login attempts from distributed IPs',
                    'Account takeover: {ips} IPs attempting logins with leaked credentials - {accounts} successful'
                ],
                'attempts': [1000, 5000, 10000, 50000, 100000],
                'ips': [50, 100, 200, 500, 1000],
                'accounts': [10, 25, 50, 100, 200]
            },
            {
                'type': 'Brute Force',
                'templates': [
                    'Brute force attack: {attempts} password attempts from {ips} IPs',
                    'Password spray attack: {attempts} login attempts across multiple accounts',
                    'Credential brute forcing: {attempts} attempts from {ips} sources',
                    'Automated password guessing: {attempts} login attempts detected',
                    'Brute force detected: {attempts} failed logins from {ips} distributed IPs'
                ],
                'attempts': [500, 1000, 5000, 10000],
                'ips': [10, 20, 50, 100],
                'accounts': [0]  # Not always specified
            },
            {
                'type': 'Password Spray',
                'templates': [
                    'Password spray: Common passwords tried on {accounts} accounts from {ips} IPs',
                    'Distributed password attack: {attempts} attempts on {accounts} user accounts',
                    'Password spray detected: {ips} IPs attempting common passwords',
                    'Account enumeration: Password spray targeting {accounts} accounts',
                    'Coordinated attack: {ips} IPs spraying passwords across {accounts} accounts'
                ],
                'attempts': [1000, 5000, 10000],
                'ips': [20, 50, 100, 200],
                'accounts': [100, 500, 1000, 5000]
            },
            {
                'type': 'Account Takeover',
                'templates': [
                    'Multiple account compromises: {accounts} accounts accessed from {ips} IPs',
                    'Account takeover detected: {accounts} successful logins from stolen credentials',
                    'Credential reuse attack: {accounts} accounts breached via leaked passwords',
                    'Mass account compromise: {accounts} accounts accessed from {ips} IPs',
                    'Account security breach: {accounts} accounts compromised via credential stuffing'
                ],
                'attempts': [0],
                'ips': [50, 100, 200],
                'accounts': [50, 100, 200, 500]
            }
        ]

        logs = []
        start_date = datetime.now() - timedelta(days=365)

        for i in range(num_samples):
            pattern = random.choice(attack_patterns)
            template = random.choice(pattern['templates'])

            timestamp = start_date + timedelta(
                days=random.randint(0, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )

            attempts = random.choice(pattern['attempts']) if pattern['attempts'][0] > 0 else 0
            ips = random.choice(pattern['ips'])
            accounts = random.choice(pattern['accounts']) if pattern['accounts'][0] > 0 else 0

            log_message = template.format(
                attempts=f'{attempts:,}' if attempts > 0 else '',
                ips=ips,
                accounts=accounts if accounts > 0 else ''
            ).replace('  ', ' ')

            logs.append({
                'timestamp': timestamp,
                'log_message': log_message,
                'control_id': 'IA-2',  # Identification and Authentication
                'control_family': 'Identification and Authentication',
                'framework': 'NIST-800-53',
                'compliance_status': 'non_compliant',
                'severity': 'critical',
                'user_id': f'attacker{random.randint(1, 100)}',
                'source_ip': f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'action': 'credential_attack',
                'resource': 'authentication_system',
                'anomaly_type': 'credential_stuffing',
                'attack_type': pattern['type'],
                'dataset_source': 'credential_stuffing_patterns'
            })

        df = pd.DataFrame(logs)
        logger.info(f"  Generated {len(df):,} credential stuffing logs")
        logger.info(f"  Attack types: {df['attack_type'].value_counts().to_dict()}")

        return df

    def generate_normal_logins(self, num_samples: int = 2000):
        """Generate normal login activity"""

        logger.info(f"Generating {num_samples:,} normal login logs...")

        normal_templates = [
            'User authentication successful: Normal login activity',
            'Standard login: User accessed system with valid credentials',
            'Authentication complete: User logged in during business hours',
            'Normal access: Successful login from known location',
            'User session started: Standard authentication process',
            'Login successful: User credentials verified',
            'Authentication approved: Normal user access',
            'User logged in: Standard access pattern',
            'Successful authentication: Normal business activity',
            'Login completed: User accessed assigned resources'
        ]

        logs = []
        start_date = datetime.now() - timedelta(days=365)

        for i in range(num_samples):
            timestamp = start_date + timedelta(
                days=random.randint(0, 365),
                hours=random.randint(8, 17),  # Business hours
                minutes=random.randint(0, 59)
            )

            # Weekdays only
            while timestamp.weekday() >= 5:
                timestamp += timedelta(days=1)

            log_message = random.choice(normal_templates)

            logs.append({
                'timestamp': timestamp,
                'log_message': log_message,
                'control_id': 'IA-2',
                'control_family': 'Identification and Authentication',
                'framework': 'NIST-800-53',
                'compliance_status': 'compliant',
                'severity': 'info',
                'user_id': f'user{random.randint(1, 500)}',
                'source_ip': f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'action': 'normal_login',
                'resource': 'authentication_system',
                'anomaly_type': 'none',
                'attack_type': 'normal',
                'dataset_source': 'normal_logins'
            })

        df = pd.DataFrame(logs)
        logger.info(f"  Generated {len(df):,} normal login logs")

        return df


def create_all_datasets():
    """Create both DDoS and Credential Stuffing datasets"""

    logger.info("\n" + "="*80)
    logger.info("CREATING DDOS AND CREDENTIAL STUFFING DATASETS")
    logger.info("="*80 + "\n")

    # DDoS Dataset
    ddos_gen = DDoSDataGenerator()
    logger.info("DDoS Dataset:")
    logger.info("-" * 80)

    ddos_attacks = ddos_gen.generate_ddos_logs(5000)
    normal_traffic = ddos_gen.generate_normal_traffic(2000)

    ddos_combined = pd.concat([ddos_attacks, normal_traffic], ignore_index=True)
    ddos_combined = ddos_combined.sample(frac=1, random_state=42).reset_index(drop=True)

    logger.info(f"\nDDoS Dataset Summary:")
    logger.info(f"  Total: {len(ddos_combined):,}")
    logger.info(f"  Attacks: {len(ddos_attacks):,} ({len(ddos_attacks)/len(ddos_combined)*100:.1f}%)")
    logger.info(f"  Normal: {len(normal_traffic):,} ({len(normal_traffic)/len(ddos_combined)*100:.1f}%)")

    # Split DDoS dataset
    ddos_train_size = int(len(ddos_combined) * 0.7)
    ddos_val_size = int(len(ddos_combined) * 0.15)

    ddos_train = ddos_combined[:ddos_train_size]
    ddos_val = ddos_combined[ddos_train_size:ddos_train_size + ddos_val_size]
    ddos_test = ddos_combined[ddos_train_size + ddos_val_size:]

    # Save DDoS
    ddos_gen.output_dir.mkdir(parents=True, exist_ok=True)
    ddos_train.to_csv(ddos_gen.output_dir / 'ddos_train.csv', index=False)
    ddos_val.to_csv(ddos_gen.output_dir / 'ddos_val.csv', index=False)
    ddos_test.to_csv(ddos_gen.output_dir / 'ddos_test.csv', index=False)
    ddos_combined.to_csv(ddos_gen.output_dir / 'ddos_complete.csv', index=False)

    logger.info(f"✅ DDoS dataset saved to: {ddos_gen.output_dir}")

    # Credential Stuffing Dataset
    logger.info("\n" + "-" * 80)
    logger.info("Credential Stuffing Dataset:")
    logger.info("-" * 80)

    cred_gen = CredentialStuffingDataGenerator()
    cred_attacks = cred_gen.generate_credential_stuffing_logs(5000)
    normal_logins = cred_gen.generate_normal_logins(2000)

    cred_combined = pd.concat([cred_attacks, normal_logins], ignore_index=True)
    cred_combined = cred_combined.sample(frac=1, random_state=42).reset_index(drop=True)

    logger.info(f"\nCredential Stuffing Dataset Summary:")
    logger.info(f"  Total: {len(cred_combined):,}")
    logger.info(f"  Attacks: {len(cred_attacks):,} ({len(cred_attacks)/len(cred_combined)*100:.1f}%)")
    logger.info(f"  Normal: {len(normal_logins):,} ({len(normal_logins)/len(cred_combined)*100:.1f}%)")

    # Split Credential dataset
    cred_train_size = int(len(cred_combined) * 0.7)
    cred_val_size = int(len(cred_combined) * 0.15)

    cred_train = cred_combined[:cred_train_size]
    cred_val = cred_combined[cred_train_size:cred_train_size + cred_val_size]
    cred_test = cred_combined[cred_train_size + cred_val_size:]

    # Save Credential Stuffing
    cred_gen.output_dir.mkdir(parents=True, exist_ok=True)
    cred_train.to_csv(cred_gen.output_dir / 'credential_train.csv', index=False)
    cred_val.to_csv(cred_gen.output_dir / 'credential_val.csv', index=False)
    cred_test.to_csv(cred_gen.output_dir / 'credential_test.csv', index=False)
    cred_combined.to_csv(cred_gen.output_dir / 'credential_complete.csv', index=False)

    logger.info(f"✅ Credential stuffing dataset saved to: {cred_gen.output_dir}")

    # Save statistics
    stats = {
        'ddos': {
            'total_samples': len(ddos_combined),
            'attack_samples': len(ddos_attacks),
            'normal_samples': len(normal_traffic),
            'train': len(ddos_train),
            'val': len(ddos_val),
            'test': len(ddos_test)
        },
        'credential_stuffing': {
            'total_samples': len(cred_combined),
            'attack_samples': len(cred_attacks),
            'normal_samples': len(normal_logins),
            'train': len(cred_train),
            'val': len(cred_val),
            'test': len(cred_test)
        },
        'creation_date': datetime.now().isoformat()
    }

    with open('data/targeted/dataset_statistics.json', 'w') as f:
        json.dump(stats, f, indent=2)

    logger.info("\n" + "="*80)
    logger.info("ALL TARGETED DATASETS CREATED SUCCESSFULLY")
    logger.info("="*80)

    return ddos_combined, cred_combined


def main():
    """Main script"""
    Path("data/targeted").mkdir(parents=True, exist_ok=True)
    ddos_df, cred_df = create_all_datasets()

    print("\n" + "="*80)
    print("DATASET CREATION COMPLETE")
    print("="*80)
    print(f"DDoS Dataset: {len(ddos_df):,} samples")
    print(f"Credential Stuffing Dataset: {len(cred_df):,} samples")
    print("\nNext steps:")
    print("1. Review data/targeted/ directories")
    print("2. Run: python integrate_targeted_datasets.py")
    print("="*80)


if __name__ == '__main__':
    main()
