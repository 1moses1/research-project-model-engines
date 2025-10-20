"""
Synthetic Compliance Event Generator

Generates realistic compliance events for NIST SP 800-53 and Rwanda NCSA controls.
"""

import json
import random
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config_loader import ConfigLoader
from utils.logger import setup_logger


class SyntheticEventGenerator:
    """
    Generate synthetic compliance events for ML training.
    """

    def __init__(
        self,
        control_taxonomy_path: str = "data/processed/control_taxonomy.json",
        output_dir: str = "data/synthetic"
    ):
        """
        Initialize SyntheticEventGenerator.

        Args:
            control_taxonomy_path: Path to control taxonomy JSON
            output_dir: Directory to save generated datasets
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.config_loader = ConfigLoader()
        self.config = self.config_loader.load_data_config()
        self.logger = setup_logger("synthetic_generator", "logs/synthetic_generator.log")

        # Load control taxonomy
        taxonomy_path = Path(control_taxonomy_path)
        if not taxonomy_path.exists():
            raise FileNotFoundError(f"Control taxonomy not found: {control_taxonomy_path}")

        with open(taxonomy_path, 'r') as f:
            self.taxonomy = json.load(f)

        self.nist_controls = {c['control_id']: c for c in self.taxonomy['nist']}
        self.rwanda_controls = {c['control_id']: c for c in self.taxonomy['rwanda']}
        self.all_controls = {**self.nist_controls, **self.rwanda_controls}

        self.logger.info(f"Loaded {len(self.all_controls)} controls from taxonomy")

        # Initialize data pools
        self._initialize_data_pools()

    def _initialize_data_pools(self):
        """Initialize pools of realistic usernames, IPs, resources, etc."""

        # User pools
        self.users = [
            f"user{i:04d}" for i in range(1, 101)
        ] + [
            "admin", "root", "sysadmin", "auditor", "security_officer",
            "db_admin", "network_admin", "backup_operator"
        ]

        # IP address pools
        self.internal_ips = [f"192.168.{random.randint(1, 255)}.{random.randint(1, 254)}" for _ in range(200)]
        self.external_ips = [f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}" for _ in range(100)]

        # Resource pools
        self.resources = [
            "/home/user/documents", "/var/log/syslog", "/etc/passwd", "/etc/shadow",
            "/opt/application/config", "/data/database", "/backup/files",
            "/var/www/html", "/usr/local/bin", "/tmp/cache"
        ]

        # Action types
        self.actions = [
            "login", "logout", "file_access", "file_modify", "file_delete",
            "privilege_escalation", "password_change", "account_create", "account_delete",
            "backup_start", "backup_complete", "scan_start", "patch_install",
            "configuration_change", "service_start", "service_stop", "network_connection"
        ]

        # Status codes
        self.status_codes = {
            "success": [200, 201, 204],
            "failure": [400, 401, 403, 404, 500, 503]
        }

    def _generate_timestamp(self, base_date: datetime) -> datetime:
        """Generate realistic timestamp with business hours bias."""
        # Add random days
        days_offset = random.randint(0, 365)
        timestamp = base_date + timedelta(days=days_offset)

        # Business hours bias (70% during 8am-6pm weekdays)
        if random.random() < 0.7:
            # Weekday business hours
            timestamp = timestamp.replace(
                hour=random.randint(8, 17),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )
            # Ensure weekday
            while timestamp.weekday() >= 5:  # Saturday=5, Sunday=6
                timestamp += timedelta(days=1)
        else:
            # Off-hours or weekend
            timestamp = timestamp.replace(
                hour=random.randint(0, 23),
                minute=random.randint(0, 59),
                second=random.randint(0, 59)
            )

        return timestamp

    def _generate_log_message(self, control: Dict, is_compliant: bool) -> str:
        """
        Generate realistic log message for a control.

        Args:
            control: Control definition dict
            is_compliant: Whether event is compliant

        Returns:
            Realistic log message string
        """
        control_id = control['control_id']
        indicators = control['log_indicators']

        if is_compliant:
            # Compliant log messages
            templates = {
                "AC-2": "User account {user} created with proper authorization by {admin}",
                "AC-3": "Access granted to {user} for resource {resource} - authorization verified",
                "AC-6": "Privilege elevation for {user} approved by manager - temporary admin access granted",
                "AU-2": "Event {event_type} logged successfully - audit record created",
                "AU-6": "Audit review completed - {count} events analyzed, no anomalies detected",
                "IA-2": "User {user} authenticated successfully with MFA from {ip}",
                "IR-4": "Security incident #{id} detected and response initiated within SLA",
                "SI-2": "Security patch {patch_id} installed successfully on {system}",
                "SI-3": "Malware scan completed - no threats detected on {system}",
                "CP-9": "Backup job completed successfully - {size}GB backed up to offsite storage",
            }
        else:
            # Non-compliant log messages
            templates = {
                "AC-2": "User account {user} created without proper approval workflow",
                "AC-3": "Access denied to {user} for {resource} - authorization check failed",
                "AC-6": "Unauthorized privilege escalation attempt by {user} detected",
                "AU-2": "Logging failure - events from {source} not captured",
                "AU-6": "Audit review overdue - last review {days} days ago exceeds policy",
                "IA-2": "Authentication failed for {user} from {ip} - invalid credentials",
                "IR-4": "Incident response delayed - #{id} not addressed within required timeframe",
                "SI-2": "Critical security patch {patch_id} not installed - system vulnerable",
                "SI-3": "Malware detected on {system} - quarantine action failed",
                "CP-9": "Backup job failed - {error} - data not protected",
            }

        # Get template for this control or use generic
        if control_id in templates:
            template = templates[control_id]
        else:
            # Generic templates based on compliance status
            if is_compliant:
                template = random.choice([
                    f"{random.choice(indicators)} - compliance check passed",
                    f"Control {control_id}: {random.choice(indicators)} executed successfully",
                    f"Compliance verification for {control_id} - status: compliant"
                ])
            else:
                template = random.choice([
                    f"{random.choice(indicators)} - compliance violation detected",
                    f"Control {control_id}: {random.choice(indicators)} failed verification",
                    f"Non-compliance detected for {control_id} - remediation required"
                ])

        # Fill in template variables
        message = template.format(
            user=random.choice(self.users),
            admin=random.choice(["admin", "sysadmin", "security_officer"]),
            resource=random.choice(self.resources),
            ip=random.choice(self.internal_ips + self.external_ips),
            event_type=random.choice(self.actions),
            count=random.randint(10, 1000),
            id=random.randint(1000, 9999),
            patch_id=f"KB{random.randint(1000000, 9999999)}",
            system=f"server{random.randint(1, 50):02d}",
            size=random.randint(10, 500),
            days=random.randint(30, 180),
            source=f"system{random.randint(1, 20)}",
            error="insufficient storage space"
        )

        return message

    def _determine_anomaly_label(self, is_compliant: bool) -> str:
        """
        Determine anomaly label based on compliance status and probability.

        Args:
            is_compliant: Whether event is compliant

        Returns:
            Anomaly label: 'normal', 'suspicious', or 'critical'
        """
        if is_compliant:
            # Compliant events are usually normal, occasionally suspicious
            return random.choices(
                ['normal', 'suspicious', 'critical'],
                weights=[0.95, 0.04, 0.01]
            )[0]
        else:
            # Non-compliant events more likely to be anomalous
            return random.choices(
                ['normal', 'suspicious', 'critical'],
                weights=[0.20, 0.60, 0.20]
            )[0]

    def _determine_severity(self, control_family: str, is_compliant: bool, anomaly_label: str) -> str:
        """
        Determine severity level based on control family and compliance status.

        Args:
            control_family: Control family name
            is_compliant: Compliance status
            anomaly_label: Anomaly classification

        Returns:
            Severity: 'low', 'medium', 'high', or 'critical'
        """
        # High-risk families
        high_risk_families = [
            "Access Control",
            "Incident Response",
            "System and Information Integrity"
        ]

        if is_compliant and anomaly_label == 'normal':
            return random.choice(['low', 'low', 'low', 'medium'])
        elif not is_compliant:
            if control_family in high_risk_families:
                return random.choices(
                    ['medium', 'high', 'critical'],
                    weights=[0.2, 0.5, 0.3]
                )[0]
            else:
                return random.choices(
                    ['low', 'medium', 'high', 'critical'],
                    weights=[0.1, 0.4, 0.4, 0.1]
                )[0]
        else:
            return random.choices(
                ['low', 'medium', 'high'],
                weights=[0.3, 0.5, 0.2]
            )[0]

    def generate_event(self, base_date: datetime) -> Dict[str, Any]:
        """
        Generate a single synthetic compliance event.

        Args:
            base_date: Base date for timestamp generation

        Returns:
            Dictionary containing event attributes
        """
        # Select random control
        control_id = random.choice(list(self.all_controls.keys()))
        control = self.all_controls[control_id]

        # Determine framework
        framework = control['framework']

        # Determine compliance status (75% compliant, 25% non-compliant from config)
        compliance_ratio = self.config['synthetic_events']['compliance_ratio']
        is_compliant = random.random() < compliance_ratio['compliant']
        compliance_status = 'compliant' if is_compliant else 'non_compliant'

        # Generate timestamp
        timestamp = self._generate_timestamp(base_date)

        # Generate log message
        log_message = self._generate_log_message(control, is_compliant)

        # Determine anomaly label
        anomaly_label = self._determine_anomaly_label(is_compliant)

        # Determine severity
        severity = self._determine_severity(control['family'], is_compliant, anomaly_label)

        # Generate event
        event = {
            'event_id': f"EVT-{random.randint(100000, 999999)}",
            'timestamp': timestamp.isoformat(),
            'user_id': random.choice(self.users),
            'action': random.choice(self.actions),
            'resource': random.choice(self.resources),
            'source_ip': random.choice(self.internal_ips),
            'destination_ip': random.choice(self.external_ips) if random.random() < 0.3 else random.choice(self.internal_ips),
            'port': random.choice([22, 80, 443, 3306, 5432, 8080]),
            'status_code': random.choice(self.status_codes['success'] if is_compliant else self.status_codes['failure']),
            'control_id': control_id,
            'control_name': control['name'],
            'control_family': control['family'],
            'framework': framework,
            'compliance_status': compliance_status,
            'anomaly_label': anomaly_label,
            'severity': severity,
            'log_message': log_message,
            'hour_of_day': timestamp.hour,
            'day_of_week': timestamp.strftime('%A'),
            'is_business_hours': 8 <= timestamp.hour <= 17 and timestamp.weekday() < 5
        }

        return event

    def generate_dataset(
        self,
        num_events: int = 100000,
        base_date: datetime = None
    ) -> pd.DataFrame:
        """
        Generate complete synthetic dataset.

        Args:
            num_events: Number of events to generate
            base_date: Base date for events (default: 1 year ago)

        Returns:
            DataFrame containing all generated events
        """
        if base_date is None:
            base_date = datetime.now() - timedelta(days=365)

        self.logger.info(f"Generating {num_events} synthetic compliance events...")

        events = []
        for i in range(num_events):
            if (i + 1) % 10000 == 0:
                self.logger.info(f"Generated {i + 1}/{num_events} events")

            event = self.generate_event(base_date)
            events.append(event)

        df = pd.DataFrame(events)

        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)

        self.logger.info(f"Dataset generation complete: {len(df)} events")

        return df

    def split_dataset(
        self,
        df: pd.DataFrame,
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split dataset into train/validation/test sets.

        Args:
            df: Full dataset
            train_ratio: Training set ratio
            val_ratio: Validation set ratio
            test_ratio: Test set ratio
            random_state: Random seed

        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 0.001, "Ratios must sum to 1.0"

        # Shuffle dataset
        df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)

        # Calculate split indices
        n = len(df)
        train_end = int(n * train_ratio)
        val_end = train_end + int(n * val_ratio)

        # Split
        train_df = df.iloc[:train_end].copy()
        val_df = df.iloc[train_end:val_end].copy()
        test_df = df.iloc[val_end:].copy()

        self.logger.info(f"Dataset split:")
        self.logger.info(f"  Train: {len(train_df)} events ({len(train_df)/n*100:.1f}%)")
        self.logger.info(f"  Val:   {len(val_df)} events ({len(val_df)/n*100:.1f}%)")
        self.logger.info(f"  Test:  {len(test_df)} events ({len(test_df)/n*100:.1f}%)")

        return train_df, val_df, test_df

    def save_dataset(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame,
        format: str = 'csv'
    ) -> Dict[str, Path]:
        """
        Save datasets to files.

        Args:
            train_df: Training set
            val_df: Validation set
            test_df: Test set
            format: Output format ('csv', 'json', 'parquet')

        Returns:
            Dictionary of file paths
        """
        paths = {}

        for name, df in [('train', train_df), ('val', val_df), ('test', test_df)]:
            if format == 'csv':
                path = self.output_dir / f"compliance_events_{name}.csv"
                df.to_csv(path, index=False)
            elif format == 'json':
                path = self.output_dir / f"compliance_events_{name}.json"
                df.to_json(path, orient='records', indent=2)
            elif format == 'parquet':
                path = self.output_dir / f"compliance_events_{name}.parquet"
                df.to_parquet(path, index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")

            paths[name] = path
            self.logger.info(f"Saved {name} set to {path}")

        return paths

    def generate_statistics(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Generate dataset statistics.

        Args:
            train_df: Training set
            val_df: Validation set
            test_df: Test set

        Returns:
            Dictionary of statistics
        """
        full_df = pd.concat([train_df, val_df, test_df])

        stats = {
            'total_events': len(full_df),
            'train_events': len(train_df),
            'val_events': len(val_df),
            'test_events': len(test_df),
            'compliance_distribution': full_df['compliance_status'].value_counts().to_dict(),
            'anomaly_distribution': full_df['anomaly_label'].value_counts().to_dict(),
            'severity_distribution': full_df['severity'].value_counts().to_dict(),
            'framework_distribution': full_df['framework'].value_counts().to_dict(),
            'control_family_distribution': full_df['control_family'].value_counts().to_dict(),
            'top_controls': full_df['control_id'].value_counts().head(10).to_dict(),
            'date_range': {
                'start': full_df['timestamp'].min(),
                'end': full_df['timestamp'].max()
            }
        }

        # Save statistics
        stats_path = self.output_dir / 'dataset_statistics.json'
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2, default=str)

        self.logger.info(f"Statistics saved to {stats_path}")

        return stats


def main():
    """Main function to generate synthetic dataset."""

    # Initialize generator
    generator = SyntheticEventGenerator()

    # Generate dataset (100K events)
    num_events = 100000
    df = generator.generate_dataset(num_events=num_events)

    # Split dataset (70/15/15)
    train_df, val_df, test_df = generator.split_dataset(df)

    # Save datasets
    paths = generator.save_dataset(train_df, val_df, test_df, format='csv')

    # Generate statistics
    stats = generator.generate_statistics(train_df, val_df, test_df)

    # Print summary
    print("\n" + "="*60)
    print("✅ SYNTHETIC DATASET GENERATION COMPLETE")
    print("="*60)
    print(f"\n📊 Dataset Summary:")
    print(f"  Total Events: {stats['total_events']:,}")
    print(f"  Train: {stats['train_events']:,}")
    print(f"  Validation: {stats['val_events']:,}")
    print(f"  Test: {stats['test_events']:,}")

    print(f"\n📈 Compliance Distribution:")
    for status, count in stats['compliance_distribution'].items():
        print(f"  {status}: {count:,} ({count/stats['total_events']*100:.1f}%)")

    print(f"\n🚨 Anomaly Distribution:")
    for label, count in stats['anomaly_distribution'].items():
        print(f"  {label}: {count:,} ({count/stats['total_events']*100:.1f}%)")

    print(f"\n⚠️  Severity Distribution:")
    for severity, count in stats['severity_distribution'].items():
        print(f"  {severity}: {count:,} ({count/stats['total_events']*100:.1f}%)")

    print(f"\n📁 Output Files:")
    for name, path in paths.items():
        print(f"  {name}: {path}")

    print(f"\n📄 Statistics: {generator.output_dir / 'dataset_statistics.json'}")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
