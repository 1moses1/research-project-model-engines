"""
Log to Compliance Mapper

Maps real-world public log datasets to Rwanda NCSA and NIST controls.
This creates training data that combines:
- Real log complexity (from public datasets like HDFS, BGL)
- Rwanda/NIST compliance rules (from control_mapper.py)

Strategy:
1. Parse real logs to extract event types, severity, patterns
2. Map log events to relevant Rwanda NCSA/NIST controls
3. Label as compliant/non-compliant based on log indicators
4. Create training dataset with real log messages + compliance labels

Author: Moise Iradukunda (CMU)
Date: October 2025
"""

import os
import sys
import json
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

# Import control mapper
from src.data_pipeline.control_mapper import ControlMapper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/log_to_compliance_mapper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LogToComplianceMapper:
    """Map real logs to compliance controls"""

    def __init__(self, control_taxonomy_path: str = "data/processed/control_taxonomy.json"):
        """
        Initialize mapper

        Args:
            control_taxonomy_path: Path to control taxonomy JSON
        """
        self.control_taxonomy_path = control_taxonomy_path
        self.load_control_taxonomy()

        # Compliance indicators (patterns that suggest compliance/non-compliance)
        self.compliance_indicators = self._build_compliance_indicators()

        logger.info("Initialized LogToComplianceMapper")
        logger.info(f"Loaded {len(self.controls)} controls from {len(self.families)} families")

    def load_control_taxonomy(self):
        """Load control taxonomy"""
        with open(self.control_taxonomy_path, 'r') as f:
            data = json.load(f)

        # Combine NIST and Rwanda controls
        self.controls = []
        if 'nist' in data:
            for control in data['nist']:
                self.controls.append({
                    'id': control['control_id'],
                    'name': control['name'],
                    'family': control['family'],
                    'framework': 'NIST',
                    'description': control.get('description', ''),
                    'log_indicators': control.get('log_indicators', [])
                })

        if 'rwanda' in data:
            for control in data['rwanda']:
                self.controls.append({
                    'id': control['control_id'],
                    'name': control['name'],
                    'family': control['family'],
                    'framework': 'Rwanda',
                    'description': control.get('description', ''),
                    'log_indicators': control.get('log_indicators', [])
                })

        # Extract unique families
        self.families = list(set([c['family'] for c in self.controls]))
        self.control_map = {c['id']: c for c in self.controls}

        logger.info(f"Loaded control taxonomy: {len(self.controls)} controls from {len(self.families)} families")

    def _build_compliance_indicators(self) -> Dict[str, Dict]:
        """
        Build compliance indicators for each control family

        Returns:
            Dictionary mapping control families to compliance patterns
        """
        indicators = {
            'AC': {  # Access Control
                'compliant_patterns': [
                    r'auth.*success', r'login.*success', r'authenticated',
                    r'authorized', r'permission.*granted', r'access.*allowed'
                ],
                'non_compliant_patterns': [
                    r'auth.*fail', r'login.*fail', r'unauthorized', r'forbidden',
                    r'permission.*denied', r'access.*denied', r'invalid.*credentials'
                ]
            },
            'AU': {  # Audit and Accountability
                'compliant_patterns': [
                    r'audit.*enabled', r'logging.*active', r'event.*recorded',
                    r'log.*written', r'monitored'
                ],
                'non_compliant_patterns': [
                    r'audit.*disabled', r'logging.*failed', r'log.*error',
                    r'unmonitored', r'audit.*missing'
                ]
            },
            'SI': {  # System and Information Integrity
                'compliant_patterns': [
                    r'scan.*complete', r'virus.*removed', r'patch.*applied',
                    r'update.*success', r'integrity.*check.*pass'
                ],
                'non_compliant_patterns': [
                    r'malware.*detected', r'virus.*found', r'vulnerability.*found',
                    r'patch.*failed', r'integrity.*violation', r'corruption'
                ]
            },
            'CM': {  # Configuration Management
                'compliant_patterns': [
                    r'config.*valid', r'baseline.*match', r'settings.*approved',
                    r'configuration.*verified'
                ],
                'non_compliant_patterns': [
                    r'config.*error', r'misconfigured', r'unauthorized.*change',
                    r'baseline.*drift', r'config.*mismatch'
                ]
            },
            'IR': {  # Incident Response
                'compliant_patterns': [
                    r'incident.*resolved', r'alert.*handled', r'response.*complete',
                    r'threat.*mitigated'
                ],
                'non_compliant_patterns': [
                    r'incident.*detected', r'alert.*triggered', r'breach.*detected',
                    r'compromise', r'intrusion.*detected'
                ]
            },
            'SC': {  # System and Communications Protection
                'compliant_patterns': [
                    r'encrypted', r'tls.*enabled', r'ssl.*success', r'secure.*connection',
                    r'firewall.*allow', r'protected'
                ],
                'non_compliant_patterns': [
                    r'unencrypted', r'plaintext', r'weak.*cipher', r'insecure',
                    r'firewall.*blocked', r'connection.*refused'
                ]
            },
            'IA': {  # Identification and Authentication
                'compliant_patterns': [
                    r'mfa.*success', r'2fa.*verified', r'strong.*password',
                    r'identity.*verified', r'token.*valid'
                ],
                'non_compliant_patterns': [
                    r'weak.*password', r'password.*expired', r'token.*invalid',
                    r'identity.*mismatch', r'mfa.*failed'
                ]
            }
        }

        return indicators

    def classify_log_event(self, log_message: str, control_family: str) -> Tuple[str, float]:
        """
        Classify a log event as compliant or non-compliant

        Args:
            log_message: Raw log message
            control_family: Full control family name

        Returns:
            Tuple of (status, confidence)
        """
        # Map full family names to short codes for indicator lookup
        family_map = {
            'Access Control': 'AC',
            'Audit and Accountability': 'AU',
            'Configuration Management': 'CM',
            'System and Information Integrity': 'SI',
            'Incident Response': 'IR',
            'System and Communications Protection': 'SC',
            'Identification and Authentication': 'IA'
        }

        family_code = family_map.get(control_family, None)

        if not family_code or family_code not in self.compliance_indicators:
            # Default to random classification for unmapped families
            return ('compliant' if np.random.random() > 0.3 else 'non_compliant', 0.5)

        indicators = self.compliance_indicators[family_code]
        log_lower = log_message.lower()

        # Check for non-compliant patterns first (higher priority)
        non_compliant_score = 0
        for pattern in indicators['non_compliant_patterns']:
            if re.search(pattern, log_lower):
                non_compliant_score += 1

        # Check for compliant patterns
        compliant_score = 0
        for pattern in indicators['compliant_patterns']:
            if re.search(pattern, log_lower):
                compliant_score += 1

        # Determine status based on scores
        if non_compliant_score > compliant_score:
            confidence = min(0.95, 0.6 + (non_compliant_score * 0.1))
            return ('non_compliant', confidence)
        elif compliant_score > 0:
            confidence = min(0.95, 0.6 + (compliant_score * 0.1))
            return ('compliant', confidence)
        else:
            # No patterns matched - use log severity heuristics
            if any(word in log_lower for word in ['error', 'fail', 'critical', 'alert', 'warn']):
                return ('non_compliant', 0.6)
            else:
                return ('compliant', 0.6)

    def map_hdfs_logs(self, hdfs_log_path: str, output_path: str, sample_size: Optional[int] = None):
        """
        Map HDFS logs to compliance dataset

        Args:
            hdfs_log_path: Path to HDFS log file
            output_path: Path to save compliance dataset
            sample_size: Number of logs to sample (None = all)
        """
        logger.info(f"Mapping HDFS logs from: {hdfs_log_path}")

        # Read HDFS logs
        logs = []
        with open(hdfs_log_path, 'r', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line:
                    logs.append(line)

        logger.info(f"Read {len(logs)} HDFS log lines")

        # Sample if requested
        if sample_size and sample_size < len(logs):
            logs = np.random.choice(logs, size=sample_size, replace=False).tolist()
            logger.info(f"Sampled {sample_size} logs")

        # Map to compliance events
        compliance_events = []

        # Assign logs to different control families with distribution (using full names)
        control_families = [
            'Access Control',
            'Audit and Accountability',
            'System and Information Integrity',
            'Configuration Management',
            'Incident Response',
            'System and Communications Protection',
            'Identification and Authentication'
        ]
        family_weights = [0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]  # More realistic distribution

        for log in logs:
            # Assign control family
            family = np.random.choice(control_families, p=family_weights)

            # Get controls in this family
            family_controls = [c for c in self.controls if c['family'] == family]
            if not family_controls:
                continue

            control = np.random.choice(family_controls)

            # Classify log
            status, confidence = self.classify_log_event(log, family)

            # Create compliance event
            event = {
                'timestamp': datetime.now().isoformat(),
                'log_message': log,
                'control_id': control['id'],
                'control_name': control['name'],
                'control_family': family,
                'framework': control['framework'],
                'status': status,
                'confidence': confidence,
                'source': 'HDFS'
            }

            compliance_events.append(event)

        # Convert to DataFrame
        df = pd.DataFrame(compliance_events)

        # Add derived features
        df['log_length'] = df['log_message'].str.len()
        df['word_count'] = df['log_message'].str.split().str.len()

        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)

        logger.info(f"✅ Mapped {len(df)} HDFS logs to compliance events")
        logger.info(f"   Compliant: {len(df[df['status'] == 'compliant'])} ({len(df[df['status'] == 'compliant']) / len(df) * 100:.1f}%)")
        logger.info(f"   Non-compliant: {len(df[df['status'] == 'non_compliant'])} ({len(df[df['status'] == 'non_compliant']) / len(df) * 100:.1f}%)")
        logger.info(f"   Saved to: {output_path}")

        return df

    def map_bgl_logs(self, bgl_log_path: str, output_path: str, sample_size: Optional[int] = None):
        """
        Map BGL logs to compliance dataset

        Args:
            bgl_log_path: Path to BGL log file
            output_path: Path to save compliance dataset
            sample_size: Number of logs to sample
        """
        logger.info(f"Mapping BGL logs from: {bgl_log_path}")

        # BGL format: Label Content
        logs = []
        labels = []

        with open(bgl_log_path, 'r', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # BGL format: first word is label, rest is content
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    label = parts[0]  # '-' = normal, else = alert
                    content = parts[1]
                    logs.append(content)
                    labels.append(label)

        logger.info(f"Read {len(logs)} BGL log lines")

        # Sample if requested
        if sample_size and sample_size < len(logs):
            indices = np.random.choice(len(logs), size=sample_size, replace=False)
            logs = [logs[i] for i in indices]
            labels = [labels[i] for i in indices]
            logger.info(f"Sampled {sample_size} logs")

        # Map to compliance events
        compliance_events = []
        # Use full family names to match control taxonomy
        control_families = [
            'Access Control',
            'Audit and Accountability',
            'System and Information Integrity',
            'Configuration Management',
            'Incident Response',
            'System and Communications Protection',
            'Identification and Authentication'
        ]
        family_weights = [0.25, 0.20, 0.15, 0.15, 0.10, 0.10, 0.05]

        for log, bgl_label in zip(logs, labels):
            # Assign control family
            family = np.random.choice(control_families, p=family_weights)

            # Get controls
            family_controls = [c for c in self.controls if c['family'] == family]
            if not family_controls:
                continue

            control = np.random.choice(family_controls)

            # Classify log (use BGL label as hint)
            if bgl_label == '-':
                # Normal log - more likely to be compliant
                status, confidence = self.classify_log_event(log, family)
                if status == 'non_compliant' and np.random.random() < 0.5:
                    status = 'compliant'  # Override some to be compliant
            else:
                # Alert log - more likely to be non-compliant
                status, confidence = self.classify_log_event(log, family)
                if status == 'compliant' and np.random.random() < 0.7:
                    status = 'non_compliant'  # Override most to be non-compliant

            event = {
                'timestamp': datetime.now().isoformat(),
                'log_message': log,
                'control_id': control['id'],
                'control_name': control['name'],
                'control_family': family,
                'framework': control['framework'],
                'status': status,
                'confidence': confidence,
                'source': 'BGL',
                'original_label': bgl_label
            }

            compliance_events.append(event)

        # Convert to DataFrame
        df = pd.DataFrame(compliance_events)

        # Add features
        df['log_length'] = df['log_message'].str.len()
        df['word_count'] = df['log_message'].str.split().str.len()

        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)

        logger.info(f"✅ Mapped {len(df)} BGL logs to compliance events")
        logger.info(f"   Compliant: {len(df[df['status'] == 'compliant'])} ({len(df[df['status'] == 'compliant']) / len(df) * 100:.1f}%)")
        logger.info(f"   Non-compliant: {len(df[df['status'] == 'non_compliant'])} ({len(df[df['status'] == 'non_compliant']) / len(df) * 100:.1f}%)")
        logger.info(f"   Saved to: {output_path}")

        return df

    def create_train_val_test_split(self, input_path: str, output_dir: str, split_ratios: Tuple[float, float, float] = (0.7, 0.15, 0.15)):
        """
        Split compliance dataset into train/val/test

        Args:
            input_path: Path to full compliance dataset
            output_dir: Directory to save splits
            split_ratios: (train, val, test) ratios
        """
        logger.info(f"Creating train/val/test split from: {input_path}")

        # Read data
        df = pd.read_csv(input_path)
        total = len(df)

        # Shuffle
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)

        # Split
        train_size = int(total * split_ratios[0])
        val_size = int(total * split_ratios[1])

        train_df = df[:train_size]
        val_df = df[train_size:train_size + val_size]
        test_df = df[train_size + val_size:]

        # Save
        os.makedirs(output_dir, exist_ok=True)

        train_path = os.path.join(output_dir, 'train.csv')
        val_path = os.path.join(output_dir, 'val.csv')
        test_path = os.path.join(output_dir, 'test.csv')

        train_df.to_csv(train_path, index=False)
        val_df.to_csv(val_path, index=False)
        test_df.to_csv(test_path, index=False)

        logger.info(f"✅ Created splits:")
        logger.info(f"   Train: {len(train_df)} samples ({len(train_df) / total * 100:.1f}%) → {train_path}")
        logger.info(f"   Val: {len(val_df)} samples ({len(val_df) / total * 100:.1f}%) → {val_path}")
        logger.info(f"   Test: {len(test_df)} samples ({len(test_df) / total * 100:.1f}%) → {test_path}")

        return train_df, val_df, test_df


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Map public logs to compliance dataset')
    parser.add_argument(
        '--dataset',
        type=str,
        required=True,
        choices=['hdfs', 'bgl'],
        help='Dataset to map'
    )
    parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Path to input log file'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Path to output compliance CSV'
    )
    parser.add_argument(
        '--sample',
        type=int,
        default=None,
        help='Number of logs to sample (default: all)'
    )
    parser.add_argument(
        '--split',
        action='store_true',
        help='Create train/val/test split after mapping'
    )

    args = parser.parse_args()

    # Initialize mapper
    mapper = LogToComplianceMapper()

    # Map dataset
    if args.dataset == 'hdfs':
        df = mapper.map_hdfs_logs(args.input, args.output, sample_size=args.sample)
    elif args.dataset == 'bgl':
        df = mapper.map_bgl_logs(args.input, args.output, sample_size=args.sample)

    # Create split if requested
    if args.split:
        output_dir = os.path.dirname(args.output)
        split_dir = os.path.join(output_dir, 'splits')
        mapper.create_train_val_test_split(args.output, split_dir)


if __name__ == "__main__":
    main()
