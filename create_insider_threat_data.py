#!/usr/bin/env python3
"""
Create Insider Threat Dataset

Based on CERT Insider Threat Database patterns:
1. Data exfiltration (USB, email, cloud uploads)
2. Unusual access patterns (after hours, weekends)
3. Large data transfers
4. Access to sensitive resources
5. Privilege abuse
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


class InsiderThreatDataGenerator:
    """Generate insider threat logs"""

    def __init__(self, output_dir: str = "data/targeted/insider_threat"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_insider_threat_logs(self, num_samples: int = 5000):
        """Generate insider threat scenarios"""

        logger.info(f"Generating {num_samples:,} insider threat logs...")

        threat_patterns = [
            {
                'category': 'Data Exfiltration - USB',
                'templates': [
                    'Employee {user} copied {size}GB sensitive data to USB drive at {time}',
                    'USB device connected - User {user} transferred {size}GB confidential files at {time}',
                    '{user} downloaded {size}GB classified data to external storage at {time}',
                    'Data exfiltration detected: {user} copied {size}GB to removable media at {time}',
                    'Large file transfer to USB: {user} moved {size}GB sensitive files at {time}'
                ],
                'sizes': [10, 20, 30, 50, 75, 100, 150, 200],
                'times': ['2am', '3am', '11pm', '1am on weekend', 'Saturday 2am', 'Sunday night']
            },
            {
                'category': 'Data Exfiltration - Email',
                'templates': [
                    '{user} emailed {size}GB confidential documents to personal account at {time}',
                    'Email security alert: {user} sent {size}GB sensitive data to external email at {time}',
                    'Large email attachment: {user} transferred {size}GB proprietary files at {time}',
                    'Data leakage detected: {user} forwarded {size}GB classified files to personal email',
                    '{user} sent {size}GB sensitive data to competitor domain at {time}'
                ],
                'sizes': [1, 2, 5, 10, 15, 20],
                'times': ['after hours', 'weekend', 'late night', '3am', 'off-hours']
            },
            {
                'category': 'Data Exfiltration - Cloud',
                'templates': [
                    '{user} uploaded {size}GB sensitive files to personal cloud storage at {time}',
                    'Cloud upload alert: {user} transferred {size}GB confidential data to Dropbox',
                    '{user} synced {size}GB proprietary files to personal Google Drive at {time}',
                    'Unauthorized cloud access: {user} uploaded {size}GB classified data at {time}',
                    '{user} backed up {size}GB company secrets to personal OneDrive'
                ],
                'sizes': [5, 10, 25, 50, 100, 200],
                'times': ['weekend', 'after hours', 'late night', '2am Saturday']
            },
            {
                'category': 'Unusual Access Patterns',
                'templates': [
                    '{user} accessed 500+ sensitive files in 1 hour at {time}',
                    'Abnormal access pattern: {user} opened 200 classified documents at {time}',
                    '{user} downloaded entire database of customer records at {time}',
                    'Privilege abuse: {user} accessed executive files without authorization at {time}',
                    '{user} queried sensitive tables 300 times in 30 minutes at {time}'
                ],
                'sizes': [0],  # Not size-based
                'times': ['2am', 'Sunday night', 'after termination notice', 'last day of employment']
            },
            {
                'category': 'After-Hours Activity',
                'templates': [
                    '{user} logged in from unusual location at {time} - accessing sensitive systems',
                    'VPN access at {time}: {user} connected from foreign IP address',
                    '{user} accessed payroll database at {time} from home network',
                    'Off-hours access: {user} logged into HR systems at {time}',
                    '{user} accessed financial records at {time} - unusual time pattern'
                ],
                'sizes': [0],
                'times': ['3am weekend', 'holiday 2am', 'Christmas Eve midnight', 'New Year 1am']
            },
            {
                'category': 'Credential Abuse',
                'templates': [
                    '{user} used admin credentials to access files outside their department',
                    'Privilege escalation detected: {user} elevated access without approval',
                    '{user} accessed competitor research files - not within job role',
                    'Authorization violation: {user} viewed salary information for all employees',
                    '{user} used another employee\'s credentials to access restricted data'
                ],
                'sizes': [0],
                'times': ['during business hours', 'afternoon', 'morning']
            }
        ]

        logs = []
        start_date = datetime.now() - timedelta(days=365)

        for i in range(num_samples):
            pattern = random.choice(threat_patterns)
            template = random.choice(pattern['templates'])

            # Random timestamp (bias toward after-hours for insider threats)
            if random.random() < 0.6:  # 60% after hours
                hour = random.choice([0, 1, 2, 3, 4, 5, 22, 23])
                is_weekend = random.choice([0, 1]) < 0.4
            else:
                hour = random.randint(9, 17)
                is_weekend = 0

            day_offset = random.randint(0, 365)
            if is_weekend:
                # Force weekend
                day_offset = day_offset - (day_offset % 7) + 5  # Saturday

            timestamp = start_date + timedelta(
                days=day_offset,
                hours=hour,
                minutes=random.randint(0, 59)
            )

            # Generate log message
            user = f'employee{random.randint(1, 100)}'
            size = random.choice(pattern['sizes']) if pattern['sizes'][0] > 0 else 0
            time_desc = random.choice(pattern['times'])

            log_message = template.format(
                user=user,
                size=size if size > 0 else '',
                time=time_desc
            ).replace('  ', ' ')  # Clean double spaces

            logs.append({
                'timestamp': timestamp,
                'log_message': log_message,
                'control_id': 'AC-3',  # Access Enforcement
                'control_family': 'Access Control',
                'framework': 'NIST-800-53',
                'compliance_status': 'non_compliant',
                'severity': random.choice(['high', 'critical']),
                'user_id': user,
                'source_ip': f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'action': pattern['category'].lower().replace(' ', '_'),
                'resource': random.choice(['file_server', 'database', 'email_system', 'cloud_storage']),
                'anomaly_type': 'insider_threat',
                'threat_category': pattern['category'],
                'dataset_source': 'insider_threat_patterns'
            })

        df = pd.DataFrame(logs)
        logger.info(f"  Generated {len(df):,} insider threat logs")
        logger.info(f"  Categories: {df['threat_category'].value_counts().to_dict()}")

        return df

    def generate_normal_employee_activity(self, num_samples: int = 3000):
        """Generate normal employee access logs"""

        logger.info(f"Generating {num_samples:,} normal employee activity logs...")

        normal_templates = [
            'User {user} accessed assigned project files',
            '{user} opened department documents - normal work activity',
            'File access: {user} modified project deliverables',
            '{user} reviewed team documents during business hours',
            'Normal access: {user} edited assigned files',
            '{user} collaborated on shared team folder',
            '{user} accessed work email and calendar',
            'Standard file access: {user} opened work documents',
            '{user} saved project files to network drive',
            'Routine activity: {user} accessed department resources'
        ]

        logs = []
        start_date = datetime.now() - timedelta(days=365)

        for i in range(num_samples):
            # Business hours only
            timestamp = start_date + timedelta(
                days=random.randint(0, 365),
                hours=random.randint(9, 17),
                minutes=random.randint(0, 59)
            )

            # Weekdays only
            while timestamp.weekday() >= 5:  # Skip weekends
                timestamp += timedelta(days=1)

            user = f'employee{random.randint(1, 100)}'
            log_message = random.choice(normal_templates).format(user=user)

            logs.append({
                'timestamp': timestamp,
                'log_message': log_message,
                'control_id': 'AC-3',
                'control_family': 'Access Control',
                'framework': 'NIST-800-53',
                'compliance_status': 'compliant',
                'severity': 'info',
                'user_id': user,
                'source_ip': f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}',
                'action': 'file_access',
                'resource': 'file_server',
                'anomaly_type': 'none',
                'threat_category': 'normal_activity',
                'dataset_source': 'normal_employee_activity'
            })

        df = pd.DataFrame(logs)
        logger.info(f"  Generated {len(df):,} normal activity logs")

        return df

    def create_insider_threat_dataset(self, threat_count: int = 5000,
                                     normal_count: int = 3000):
        """Create complete insider threat dataset"""

        logger.info("\n" + "="*80)
        logger.info("CREATING INSIDER THREAT DATASET")
        logger.info("="*80 + "\n")

        # Generate insider threats
        threat_df = self.generate_insider_threat_logs(threat_count)

        # Generate normal activity
        normal_df = self.generate_normal_employee_activity(normal_count)

        # Combine
        combined_df = pd.concat([threat_df, normal_df], ignore_index=True)

        # Shuffle
        combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)

        logger.info(f"\nDataset Summary:")
        logger.info(f"  Total samples: {len(combined_df):,}")
        logger.info(f"  Insider threats (non_compliant): {len(threat_df):,} ({len(threat_df)/len(combined_df)*100:.1f}%)")
        logger.info(f"  Normal activity (compliant): {len(normal_df):,} ({len(normal_df)/len(combined_df)*100:.1f}%)")

        # Split into train/val/test (70/15/15)
        train_size = int(len(combined_df) * 0.7)
        val_size = int(len(combined_df) * 0.15)

        train_df = combined_df[:train_size]
        val_df = combined_df[train_size:train_size + val_size]
        test_df = combined_df[train_size + val_size:]

        logger.info(f"\nSplit:")
        logger.info(f"  Train: {len(train_df):,}")
        logger.info(f"  Val:   {len(val_df):,}")
        logger.info(f"  Test:  {len(test_df):,}")

        # Save
        train_df.to_csv(self.output_dir / 'insider_threat_train.csv', index=False)
        val_df.to_csv(self.output_dir / 'insider_threat_val.csv', index=False)
        test_df.to_csv(self.output_dir / 'insider_threat_test.csv', index=False)
        combined_df.to_csv(self.output_dir / 'insider_threat_complete.csv', index=False)

        logger.info(f"\n✅ Insider threat dataset saved to: {self.output_dir}")

        # Statistics
        stats = {
            'total_samples': len(combined_df),
            'threat_samples': len(threat_df),
            'normal_samples': len(normal_df),
            'threat_ratio': float(len(threat_df) / len(combined_df)),
            'threat_categories': threat_df['threat_category'].value_counts().to_dict(),
            'train_samples': len(train_df),
            'val_samples': len(val_df),
            'test_samples': len(test_df),
            'creation_date': datetime.now().isoformat(),
            'source': 'Synthetic insider threat patterns based on CERT database characteristics'
        }

        with open(self.output_dir / 'insider_threat_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)

        return train_df, val_df, test_df


def main():
    """Main script"""
    generator = InsiderThreatDataGenerator()

    # Create dataset with 5K threats + 3K normal = 8K total
    train_df, val_df, test_df = generator.create_insider_threat_dataset(
        threat_count=5000,
        normal_count=3000
    )

    print("\n" + "="*80)
    print("INSIDER THREAT DATASET CREATION COMPLETE")
    print("="*80)
    print(f"Total samples: {len(train_df) + len(val_df) + len(test_df):,}")
    print(f"Train: {len(train_df):,}")
    print(f"Val:   {len(val_df):,}")
    print(f"Test:  {len(test_df):,}")
    print("\nNext steps:")
    print("1. Review data/targeted/insider_threat/insider_threat_complete.csv")
    print("2. Run: python integrate_targeted_datasets.py")
    print("="*80)


if __name__ == '__main__':
    main()
