"""
Public Dataset Preprocessor for Compliance Monitoring

Converts public security datasets to compliance event format:
1. NSL-KDD - Network intrusion → Compliance violations
2. LogHub - System logs → Compliance events
3. HDFS - Anomaly detection → Compliance monitoring

Author: Moise Iradukunda (CMU)
Date: October 2025
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import logging
import random
import re

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import setup_logger
from data_pipeline.control_mapper import ControlMapper


class PublicDatasetPreprocessor:
    """Preprocess public datasets into compliance format."""

    def __init__(self, input_dir: str = "data/public", output_dir: str = "data/public_formatted"):
        """
        Initialize preprocessor.

        Args:
            input_dir: Directory containing downloaded datasets
            output_dir: Directory to save preprocessed data
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger("public_preprocessor", "logs/public_preprocessor.log")
        self.control_mapper = ControlMapper()

        # NSL-KDD attack type to compliance control mapping
        self.attack_control_map = {
            # Unauthorized access attacks → Access Control
            'back': 'AC-3',           # Buffer overflow → Access Enforcement
            'buffer_overflow': 'AC-3',
            'rootkit': 'AC-6',        # Privilege escalation → Least Privilege
            'perl': 'AC-6',
            'loadmodule': 'AC-6',
            'ftp_write': 'AC-3',      # Unauthorized file write
            'guess_passwd': 'IA-5',   # Password guessing → Authenticator Management
            'imap': 'IA-2',           # IMAP attacks → Identification & Authentication

            # DoS attacks → System Protection
            'neptune': 'SC-5',        # DoS → Denial of Service Protection
            'smurf': 'SC-5',
            'pod': 'SC-5',
            'teardrop': 'SC-5',
            'land': 'SC-5',
            'apache2': 'SC-5',
            'udpstorm': 'SC-5',
            'processtable': 'SC-5',
            'mailbomb': 'SC-5',

            # Probe/Scan attacks → Monitoring
            'satan': 'SI-4',          # Network scanning → Information System Monitoring
            'ipsweep': 'SI-4',
            'nmap': 'SI-4',
            'portsweep': 'SI-4',
            'mscan': 'SI-4',
            'saint': 'SI-4',

            # R2L (Remote to Local) → Access Control
            'warezclient': 'AC-3',
            'warezmaster': 'AC-3',
            'phf': 'AC-3',
            'spy': 'AC-3',
            'multihop': 'AC-3',
            'named': 'AC-3',
            'sendmail': 'AC-3',
            'xterm': 'AC-3',
            'xlock': 'AC-3',
            'xsnoop': 'AC-3',
            'snmpgetattack': 'SI-4',
            'snmpguess': 'IA-5',
            'httptunnel': 'SC-7',     # Boundary Protection

            # U2R (User to Root) → Privilege Management
            'ps': 'AC-6',
            'sqlattack': 'AC-6',
            'worm': 'SI-3',           # Malicious Code Protection
        }

        # LogHub log patterns to controls
        self.log_pattern_map = {
            r'(error|fail|exception)': ('non-compliant', 'AU-6'),  # Audit Review
            r'(warning|warn)': ('non-compliant', 'AU-12'),         # Audit Generation
            r'(authentication|login).*success': ('compliant', 'IA-2'),
            r'(authentication|login).*fail': ('non-compliant', 'IA-2'),
            r'(access|permission).*denied': ('non-compliant', 'AC-3'),
            r'(start|started|running)': ('compliant', 'SC-7'),
            r'(connection|connected)': ('compliant', 'SC-7'),
            r'(disconnect|timeout)': ('non-compliant', 'SC-10'),   # Network Disconnect
        }

        self.logger.info("Public Dataset Preprocessor initialized")

    def preprocess_nsl_kdd(self) -> pd.DataFrame:
        """
        Preprocess NSL-KDD dataset into compliance format.

        Returns:
            DataFrame with compliance events
        """
        self.logger.info("Preprocessing NSL-KDD dataset")

        train_path = self.input_dir / "NSL-KDD" / "KDDTrain+.csv"
        test_path = self.input_dir / "NSL-KDD" / "KDDTest+.csv"

        if not train_path.exists():
            self.logger.warning(f"NSL-KDD not found at {train_path}")
            return pd.DataFrame()

        # Load datasets
        train_df = pd.read_csv(train_path)
        test_df = pd.read_csv(test_path)

        # Combine train and test
        df = pd.concat([train_df, test_df], ignore_index=True)

        self.logger.info(f"Loaded {len(df)} NSL-KDD records")

        # Convert to compliance format
        compliance_events = []

        for idx, row in df.iterrows():
            label = str(row['label']).strip().lower()

            # Determine compliance status and control
            if label == 'normal':
                status = 'compliant'
                control_id = 'AC-2'  # Default for normal traffic
            else:
                status = 'non-compliant'
                # Map attack type to control
                control_id = self.attack_control_map.get(label, 'SI-4')

            # Get control info
            control_info = self._get_control_info(control_id)

            # Generate log message from network features
            log_message = self._generate_log_from_nsl_kdd(row, label)

            # Create compliance event
            event = {
                'timestamp': self._generate_timestamp(idx, len(df)),
                'log_message': log_message,
                'control_id': control_id,
                'control_family': control_info['family'],
                'framework': control_info['framework'],
                'status': status,
                'source_ip': self._generate_ip(),
                'user': self._generate_user(),
                'severity': self._determine_severity(status, control_info['family']),
                'source': 'NSL-KDD'
            }

            compliance_events.append(event)

            if (idx + 1) % 10000 == 0:
                self.logger.info(f"Processed {idx + 1}/{len(df)} NSL-KDD records")

        result_df = pd.DataFrame(compliance_events)
        self.logger.info(f"Generated {len(result_df)} compliance events from NSL-KDD")

        return result_df

    def preprocess_loghub(self) -> pd.DataFrame:
        """
        Preprocess LogHub system logs into compliance format.

        Returns:
            DataFrame with compliance events
        """
        self.logger.info("Preprocessing LogHub datasets")

        compliance_events = []

        # Process OpenStack logs
        openstack_dir = self.input_dir / "LogHub" / "OpenStack"
        if openstack_dir.exists():
            for log_file in openstack_dir.glob("*.log"):
                events = self._process_log_file(log_file, "LogHub-OpenStack")
                compliance_events.extend(events)

        # Process Hadoop logs
        hadoop_dir = self.input_dir / "LogHub" / "Hadoop"
        if hadoop_dir.exists():
            for log_file in hadoop_dir.rglob("*.log"):
                if log_file.is_file():
                    events = self._process_log_file(log_file, "LogHub-Hadoop", max_lines=1000)
                    compliance_events.extend(events)

        # Process Linux logs
        linux_dir = self.input_dir / "LogHub" / "Linux"
        if linux_dir.exists():
            for log_file in linux_dir.glob("*.log"):
                events = self._process_log_file(log_file, "LogHub-Linux")
                compliance_events.extend(events)

        result_df = pd.DataFrame(compliance_events)
        self.logger.info(f"Generated {len(result_df)} compliance events from LogHub")

        return result_df

    def _process_log_file(self, log_path: Path, source: str, max_lines: int = 5000) -> List[Dict]:
        """Process a single log file into compliance events."""
        self.logger.info(f"Processing {log_path.name}")

        events = []

        try:
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:max_lines]  # Limit lines per file

            for idx, line in enumerate(lines):
                line = line.strip()
                if not line or len(line) < 10:
                    continue

                # Match log patterns to determine status and control
                status, control_id = self._classify_log_line(line)

                # Get control info
                control_info = self._get_control_info(control_id)

                # Create compliance event
                event = {
                    'timestamp': self._generate_timestamp(idx, len(lines)),
                    'log_message': line[:500],  # Limit message length
                    'control_id': control_id,
                    'control_family': control_info['family'],
                    'framework': control_info['framework'],
                    'status': status,
                    'source_ip': self._generate_ip(),
                    'user': self._generate_user(),
                    'severity': self._determine_severity(status, control_info['family']),
                    'source': source
                }

                events.append(event)

        except Exception as e:
            self.logger.error(f"Error processing {log_path}: {e}")

        return events

    def _classify_log_line(self, log_line: str) -> Tuple[str, str]:
        """
        Classify log line into compliance status and control.

        Returns:
            Tuple of (status, control_id)
        """
        log_lower = log_line.lower()

        # Check patterns
        for pattern, (status, control_id) in self.log_pattern_map.items():
            if re.search(pattern, log_lower):
                return status, control_id

        # Default: compliant system operation
        return 'compliant', 'AU-2'  # Audit Events

    def _generate_log_from_nsl_kdd(self, row: pd.Series, label: str) -> str:
        """Generate realistic log message from NSL-KDD features."""
        protocol = row.get('protocol_type', 'tcp')
        service = row.get('service', 'http')
        src_bytes = int(row.get('src_bytes', 0))
        dst_bytes = int(row.get('dst_bytes', 0))
        flag = row.get('flag', 'SF')

        if label == 'normal':
            messages = [
                f"Connection established: {protocol.upper()} {service} ({src_bytes} bytes sent, {dst_bytes} bytes received) - Status: {flag}",
                f"Successful {protocol.upper()} connection to {service} service - Data transfer: {src_bytes + dst_bytes} bytes",
                f"{protocol.upper()} session completed for {service} - Connection normal",
            ]
        else:
            messages = [
                f"Suspicious {protocol.upper()} activity detected on {service} - Attack: {label} - {src_bytes} bytes",
                f"Security alert: {label} attack attempt via {protocol.upper()} {service} - {dst_bytes} bytes transferred",
                f"Anomalous {protocol.upper()} traffic to {service} - Pattern: {label} - Flag: {flag}",
                f"Intrusion detected: {label} targeting {service} via {protocol.upper()} - Blocked",
            ]

        return random.choice(messages)

    def _get_control_info(self, control_id: str) -> Dict:
        """Get control information."""
        # Get all controls
        nist_controls = self.control_mapper.create_nist_control_definitions()
        rwanda_controls = self.control_mapper.create_rwanda_control_definitions()
        all_controls = nist_controls + rwanda_controls

        # Find control
        control_info = next((c for c in all_controls if c['control_id'] == control_id), None)

        if control_info:
            return {
                'family': control_info['family'],
                'framework': control_info['framework']
            }
        else:
            # Default
            return {
                'family': 'System and Information Integrity',
                'framework': 'NIST'
            }

    def _generate_timestamp(self, idx: int, total: int) -> str:
        """Generate realistic timestamps spread over 30 days."""
        base_time = datetime(2025, 10, 1, 0, 0, 0)
        offset_seconds = (idx / total) * (30 * 24 * 60 * 60)  # 30 days
        timestamp = base_time + timedelta(seconds=offset_seconds)
        return timestamp.isoformat()

    def _generate_ip(self) -> str:
        """Generate random IP address."""
        return f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"

    def _generate_user(self) -> str:
        """Generate random username."""
        users = ['admin', 'user', 'system', 'service', 'operator', 'manager', 'analyst']
        return random.choice(users) + str(random.randint(1, 100))

    def _determine_severity(self, status: str, control_family: str) -> str:
        """Determine event severity based on status and control family."""
        if status == 'compliant':
            return 'normal'

        # High severity families
        high_severity_families = [
            'Access Control',
            'Identification and Authentication',
            'System and Communications Protection'
        ]

        if control_family in high_severity_families:
            return random.choice(['critical', 'high'])
        else:
            return random.choice(['medium', 'high'])

    def merge_datasets(self, nsl_kdd_df: pd.DataFrame, loghub_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge all preprocessed datasets.

        Args:
            nsl_kdd_df: NSL-KDD compliance events
            loghub_df: LogHub compliance events

        Returns:
            Combined DataFrame
        """
        self.logger.info("Merging datasets")

        # Combine all datasets
        combined = pd.concat([nsl_kdd_df, loghub_df], ignore_index=True)

        # Shuffle
        combined = combined.sample(frac=1.0, random_state=42).reset_index(drop=True)

        self.logger.info(f"Merged dataset size: {len(combined)} events")
        self.logger.info(f"Compliance distribution: {combined['status'].value_counts().to_dict()}")
        self.logger.info(f"Severity distribution: {combined['severity'].value_counts().to_dict()}")

        return combined

    def split_dataset(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split dataset into train/val/test (70/15/15).

        Args:
            df: Combined dataset

        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        self.logger.info("Splitting dataset into train/val/test")

        # Calculate split sizes
        total_size = len(df)
        train_size = int(0.70 * total_size)
        val_size = int(0.15 * total_size)

        # Split
        train_df = df.iloc[:train_size]
        val_df = df.iloc[train_size:train_size + val_size]
        test_df = df.iloc[train_size + val_size:]

        self.logger.info(f"Train: {len(train_df)} | Val: {len(val_df)} | Test: {len(test_df)}")

        return train_df, val_df, test_df

    def save_datasets(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame):
        """Save preprocessed datasets."""
        self.logger.info(f"Saving datasets to {self.output_dir}")

        # Save train/val/test
        train_df.to_csv(self.output_dir / "compliance_events_train.csv", index=False)
        val_df.to_csv(self.output_dir / "compliance_events_val.csv", index=False)
        test_df.to_csv(self.output_dir / "compliance_events_test.csv", index=False)

        # Save combined
        combined = pd.concat([train_df, val_df, test_df], ignore_index=True)
        combined.to_csv(self.output_dir / "compliance_events_all.csv", index=False)

        self.logger.info("Datasets saved successfully")

        # Print statistics
        self._print_statistics(train_df, val_df, test_df)

    def _print_statistics(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame):
        """Print dataset statistics."""
        print("\n" + "=" * 80)
        print("DATASET STATISTICS")
        print("=" * 80)

        for name, df in [("Training", train_df), ("Validation", val_df), ("Test", test_df)]:
            print(f"\n{name} Set ({len(df)} events):")
            print(f"  Compliance: {df['status'].value_counts().to_dict()}")
            print(f"  Severity: {df['severity'].value_counts().to_dict()}")
            print(f"  Sources: {df['source'].value_counts().to_dict()}")
            print(f"  Top 5 Controls: {df['control_id'].value_counts().head().to_dict()}")

        print("\n" + "=" * 80)

    def run(self):
        """Run complete preprocessing pipeline."""
        print("""
╔══════════════════════════════════════════════════════════════╗
║   Public Dataset Preprocessor                                ║
║   Rwanda NCSA Compliance Monitoring Project                  ║
╚══════════════════════════════════════════════════════════════╝
        """)

        # Preprocess NSL-KDD
        print("\n📥 Preprocessing NSL-KDD dataset...")
        nsl_kdd_df = self.preprocess_nsl_kdd()

        # Preprocess LogHub
        print("\n📥 Preprocessing LogHub datasets...")
        loghub_df = self.preprocess_loghub()

        # Merge datasets
        print("\n🔗 Merging datasets...")
        combined_df = self.merge_datasets(nsl_kdd_df, loghub_df)

        # Split into train/val/test
        print("\n✂️  Splitting into train/val/test...")
        train_df, val_df, test_df = self.split_dataset(combined_df)

        # Save datasets
        print(f"\n💾 Saving datasets to {self.output_dir}...")
        self.save_datasets(train_df, val_df, test_df)

        print("\n✅ Preprocessing complete!")
        print(f"📁 Preprocessed data saved to: {self.output_dir}")
        print("\n💡 Next steps:")
        print("   1. Review dataset statistics above")
        print("   2. Train models with preprocessed data")
        print("   3. Evaluate cross-dataset performance")


def main():
    """Main entry point."""
    preprocessor = PublicDatasetPreprocessor()
    preprocessor.run()


if __name__ == "__main__":
    main()
