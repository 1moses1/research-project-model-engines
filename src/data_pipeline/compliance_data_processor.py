#!/usr/bin/env python3
"""
Compliance Data Processor
Processes compliance frameworks (MITRE ATT&CK, OWASP, CIS, PCI DSS, NIST NVD)
into training data for XGBoost model
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from datetime import datetime
import random

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('compliance_processor')


class ComplianceDataProcessor:
    """Process compliance frameworks into training data"""

    def __init__(self, compliance_dir: str = "data/advanced_datasets/compliance_standards"):
        self.compliance_dir = Path(compliance_dir)
        self.output_dir = Path("data/compliance_enriched")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Load existing control definitions
        self.control_definitions = self._load_control_definitions()

    def _load_control_definitions(self) -> Dict:
        """Load existing NIST/Rwanda control definitions"""
        controls_file = Path("src/data_pipeline/control_mapper.py")
        if not controls_file.exists():
            return {}

        # Basic control mapping (will be enriched with compliance data)
        return {
            'AC-3': 'Access Enforcement',
            'AC-6': 'Least Privilege',
            'AU-6': 'Audit Review, Analysis, and Reporting',
            'IA-2': 'Identification and Authentication',
            'SI-3': 'Malicious Code Protection',
            'SC-7': 'Boundary Protection',
            'CM-7': 'Least Functionality',
            'SI-4': 'System Monitoring'
        }

    def process_mitre_attck(self) -> pd.DataFrame:
        """
        Process MITRE ATT&CK framework into training data

        Returns:
            DataFrame with attack techniques as compliance events
        """
        logger.info("Processing MITRE ATT&CK framework...")

        mitre_dir = self.compliance_dir / "MITRE-ATT&CK"
        all_techniques = []

        # Process each ATT&CK matrix
        for matrix_file in ['enterprise-attack.json', 'mobile-attack.json', 'ics-attack.json']:
            file_path = mitre_dir / matrix_file
            if not file_path.exists():
                logger.warning(f"File not found: {file_path}")
                continue

            logger.info(f"Processing {matrix_file}...")

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract techniques
            for obj in data.get('objects', []):
                if obj.get('type') == 'attack-pattern':
                    technique = {
                        'id': obj.get('external_references', [{}])[0].get('external_id', ''),
                        'name': obj.get('name', ''),
                        'description': obj.get('description', '')[:500],  # Limit length
                        'tactics': ', '.join([phase.get('phase_name', '') for phase in obj.get('kill_chain_phases', [])]),
                        'platform': ', '.join(obj.get('x_mitre_platforms', [])),
                        'data_sources': ', '.join(obj.get('x_mitre_data_sources', [])),
                        'matrix': matrix_file.replace('-attack.json', '')
                    }

                    # Only include techniques with IDs
                    if technique['id']:
                        all_techniques.append(technique)

        logger.info(f"Extracted {len(all_techniques)} MITRE ATT&CK techniques")

        # Convert to compliance events
        events = []
        for tech in all_techniques:
            # Generate multiple event variations per technique
            for i in range(3):  # 3 variations per technique
                event = self._create_mitre_event(tech, variation=i)
                events.append(event)

        df = pd.DataFrame(events)
        logger.info(f"Created {len(df)} MITRE ATT&CK-based compliance events")

        return df

    def _create_mitre_event(self, technique: Dict, variation: int = 0) -> Dict:
        """Create a compliance event from MITRE technique"""

        # Map tactics to NIST controls
        tactic_to_control = {
            'initial-access': 'AC-3',
            'execution': 'CM-7',
            'persistence': 'AC-6',
            'privilege-escalation': 'AC-6',
            'defense-evasion': 'SI-3',
            'credential-access': 'IA-2',
            'discovery': 'AU-6',
            'lateral-movement': 'SC-7',
            'collection': 'AU-6',
            'exfiltration': 'SC-7',
            'command-and-control': 'SC-7',
            'impact': 'SI-4'
        }

        # Get primary tactic
        tactics = technique['tactics'].split(', ')
        primary_tactic = tactics[0] if tactics else 'discovery'
        control = tactic_to_control.get(primary_tactic, 'SI-4')

        # Generate realistic log message
        log_templates = [
            f"MITRE {technique['id']} detected: {technique['name']} - Access denied",
            f"Security alert: {technique['name']} ({technique['id']}) blocked by system",
            f"Suspicious activity matching {technique['id']}: {technique['name']} - Investigation required",
            f"Threat detected: {technique['id']} {technique['name']} - Automated response initiated"
        ]

        log_message = log_templates[variation % len(log_templates)]

        # Determine compliance status (80% compliant - blocked, 20% non-compliant - detected)
        is_compliant = random.random() < 0.8

        # Generate event
        event = {
            'timestamp': datetime.now().isoformat(),
            'log_message': log_message,
            'source': f'mitre_attck_{technique["matrix"]}',
            'event_type': 'security_alert',
            'control_id': control,
            'mitre_technique': technique['id'],
            'mitre_tactic': primary_tactic,
            'user': f'user_{random.randint(1, 100)}',
            'ip_address': f'192.168.{random.randint(1, 255)}.{random.randint(1, 255)}',
            'resource': technique['platform'].split(',')[0].strip() if technique['platform'] else 'system',
            'status_code': 200 if is_compliant else 403,
            'compliance_status': 'compliant' if is_compliant else 'non_compliant',
            'anomaly_type': 'normal' if is_compliant else 'suspicious',
            'description': technique['description'][:200]
        }

        return event

    def process_owasp(self) -> pd.DataFrame:
        """Process OWASP Top 10 into training data"""
        logger.info("Processing OWASP Top 10...")

        owasp_file = self.compliance_dir / "OWASP" / "owasp_top10_2021.json"
        if not owasp_file.exists():
            logger.warning(f"OWASP file not found: {owasp_file}")
            return pd.DataFrame()

        with open(owasp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        events = []
        for risk in data.get('risks', []):
            # Generate multiple event variations per risk
            for i in range(10):  # 10 events per risk
                event = self._create_owasp_event(risk, variation=i)
                events.append(event)

        df = pd.DataFrame(events)
        logger.info(f"Created {len(df)} OWASP-based compliance events")

        return df

    def _create_owasp_event(self, risk: Dict, variation: int = 0) -> Dict:
        """Create a compliance event from OWASP risk"""

        # Map OWASP risks to NIST controls
        risk_to_control = {
            'A01:2021': 'AC-3',  # Broken Access Control
            'A02:2021': 'SC-13',  # Cryptographic Failures
            'A03:2021': 'SI-10',  # Injection
            'A04:2021': 'CM-7',   # Insecure Design
            'A05:2021': 'CM-6',   # Security Misconfiguration
            'A06:2021': 'SA-11',  # Vulnerable Components
            'A07:2021': 'IA-2',   # Authentication Failures
            'A08:2021': 'SI-10',  # Software and Data Integrity
            'A09:2021': 'AU-6',   # Security Logging Failures
            'A10:2021': 'SC-7'    # Server-Side Request Forgery
        }

        control = risk_to_control.get(risk['rank'], 'SI-4')

        # Generate realistic web attack log
        log_templates = [
            f"Web attack blocked: {risk['name']} ({risk['rank']}) - Source IP blocked",
            f"WAF alert: {risk['name']} attempt detected - Request denied",
            f"Security scan detected {risk['name']} vulnerability - Patching required",
            f"Application firewall: {risk['name']} attack prevented"
        ]

        log_message = log_templates[variation % len(log_templates)]

        # 75% compliant (blocked), 25% non-compliant (detected)
        is_compliant = random.random() < 0.75

        event = {
            'timestamp': datetime.now().isoformat(),
            'log_message': log_message,
            'source': 'owasp_waf',
            'event_type': 'web_security',
            'control_id': control,
            'owasp_risk': risk['rank'],
            'user': f'web_user_{random.randint(1, 100)}',
            'ip_address': f'10.0.{random.randint(1, 255)}.{random.randint(1, 255)}',
            'resource': '/api/endpoint',
            'status_code': 200 if is_compliant else 403,
            'compliance_status': 'compliant' if is_compliant else 'non_compliant',
            'anomaly_type': 'normal' if is_compliant else 'suspicious',
            'description': risk['description'][:200] if 'description' in risk else risk['name']
        }

        return event

    def process_cis_controls(self) -> pd.DataFrame:
        """Process CIS Controls v8 into training data"""
        logger.info("Processing CIS Controls v8...")

        cis_file = self.compliance_dir / "CIS-Controls" / "cis_controls_v8.json"
        if not cis_file.exists():
            logger.warning(f"CIS file not found: {cis_file}")
            return pd.DataFrame()

        with open(cis_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        events = []
        for control in data.get('controls', []):
            # Generate multiple event variations per control
            for i in range(5):  # 5 events per control
                event = self._create_cis_event(control, variation=i)
                events.append(event)

        df = pd.DataFrame(events)
        logger.info(f"Created {len(df)} CIS Controls-based compliance events")

        return df

    def _create_cis_event(self, control: Dict, variation: int = 0) -> Dict:
        """Create a compliance event from CIS control"""

        # Map CIS controls to NIST
        cis_to_nist = {
            '1': 'CM-8',   # Inventory
            '2': 'CM-8',   # Software Inventory
            '3': 'CM-6',   # Data Protection
            '4': 'CM-7',   # Secure Configuration
            '5': 'AC-6',   # Account Management
            '6': 'AC-3',   # Access Control
            '7': 'SI-4',   # Continuous Monitoring
            '8': 'AU-6',   # Audit Log Management
            '9': 'IA-5',   # Email & Web Protection
            '10': 'SI-3',  # Malware Defense
            '11': 'CM-3',  # Data Recovery
            '12': 'SC-7',  # Network Infrastructure
            '13': 'SC-7',  # Network Monitoring
            '14': 'AU-6',  # Security Awareness
            '15': 'SA-15', # Service Provider Management
            '16': 'SI-4',  # Application Software Security
            '17': 'IR-4',  # Incident Response
            '18': 'CA-7'   # Penetration Testing
        }

        nist_control = cis_to_nist.get(control['id'], 'SI-4')

        log_templates = [
            f"CIS Control {control['id']} audit: {control['name']} - Compliant",
            f"CIS v8 check: {control['name']} - Configuration verified",
            f"Compliance scan: CIS Control {control['id']} ({control['name']}) - Status OK",
            f"Security baseline: {control['name']} - Meeting CIS requirements"
        ]

        log_message = log_templates[variation % len(log_templates)]

        # 85% compliant for CIS controls
        is_compliant = random.random() < 0.85

        event = {
            'timestamp': datetime.now().isoformat(),
            'log_message': log_message,
            'source': 'cis_scanner',
            'event_type': 'compliance_audit',
            'control_id': nist_control,
            'cis_control': control['id'],
            'user': f'admin_{random.randint(1, 20)}',
            'ip_address': f'172.16.{random.randint(1, 255)}.{random.randint(1, 255)}',
            'resource': 'system',
            'status_code': 200 if is_compliant else 500,
            'compliance_status': 'compliant' if is_compliant else 'non_compliant',
            'anomaly_type': 'normal' if is_compliant else 'suspicious',
            'description': control['name']
        }

        return event

    def process_pci_dss(self) -> pd.DataFrame:
        """Process PCI DSS v4 into training data"""
        logger.info("Processing PCI DSS v4...")

        pci_file = self.compliance_dir / "PCI-DSS" / "pci_dss_v4.json"
        if not pci_file.exists():
            logger.warning(f"PCI DSS file not found: {pci_file}")
            return pd.DataFrame()

        with open(pci_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        events = []
        for requirement in data.get('requirements', []):
            # Generate multiple event variations per requirement
            for i in range(8):  # 8 events per requirement
                event = self._create_pci_event(requirement, variation=i)
                events.append(event)

        df = pd.DataFrame(events)
        logger.info(f"Created {len(df)} PCI DSS-based compliance events")

        return df

    def _create_pci_event(self, requirement: Dict, variation: int = 0) -> Dict:
        """Create a compliance event from PCI DSS requirement"""

        # Map PCI DSS to NIST controls
        pci_to_nist = {
            '1': 'SC-7',   # Firewall
            '2': 'CM-6',   # Default Passwords
            '3': 'SC-28',  # Cardholder Data Protection
            '4': 'SC-13',  # Encryption
            '5': 'SI-3',   # Anti-virus
            '6': 'SI-2',   # Secure Systems
            '7': 'AC-6',   # Access Restriction
            '8': 'IA-2',   # User Authentication
            '9': 'PE-3',   # Physical Access
            '10': 'AU-2',  # Track and Monitor
            '11': 'RA-5',  # Security Testing
            '12': 'PL-1'   # Security Policy
        }

        nist_control = pci_to_nist.get(requirement['id'], 'AC-3')

        log_templates = [
            f"PCI DSS {requirement['id']} check: {requirement['name']} - Passed",
            f"Payment security: {requirement['name']} - Compliant with PCI DSS v4",
            f"Cardholder data protection: PCI requirement {requirement['id']} verified",
            f"PCI audit: {requirement['name']} - Control effective"
        ]

        log_message = log_templates[variation % len(log_templates)]

        # 90% compliant for payment security
        is_compliant = random.random() < 0.90

        event = {
            'timestamp': datetime.now().isoformat(),
            'log_message': log_message,
            'source': 'pci_dss_auditor',
            'event_type': 'payment_security',
            'control_id': nist_control,
            'pci_requirement': requirement['id'],
            'user': f'payment_admin_{random.randint(1, 10)}',
            'ip_address': f'192.168.100.{random.randint(1, 255)}',
            'resource': 'payment_gateway',
            'status_code': 200 if is_compliant else 403,
            'compliance_status': 'compliant' if is_compliant else 'non_compliant',
            'anomaly_type': 'normal' if is_compliant else 'critical',
            'description': requirement['name']
        }

        return event

    def process_nist_nvd(self) -> pd.DataFrame:
        """Process NIST NVD CVE data into training data"""
        logger.info("Processing NIST NVD CVE data...")

        nvd_dir = self.compliance_dir / "NIST-NVD"
        nvd_files = list(nvd_dir.glob("nvd_cves_*.json"))

        if not nvd_files:
            logger.warning("No NIST NVD files found")
            return pd.DataFrame()

        # Use the most recent file
        nvd_file = sorted(nvd_files)[-1]
        logger.info(f"Processing {nvd_file.name}...")

        with open(nvd_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        events = []
        vulnerabilities = data.get('vulnerabilities', [])[:500]  # Limit to 500 CVEs

        for vuln in vulnerabilities:
            cve = vuln.get('cve', {})
            event = self._create_nvd_event(cve)
            if event:
                events.append(event)

        df = pd.DataFrame(events)
        logger.info(f"Created {len(df)} NIST NVD-based compliance events")

        return df

    def _create_nvd_event(self, cve: Dict) -> Dict:
        """Create a compliance event from CVE"""

        cve_id = cve.get('id', '')
        if not cve_id:
            return None

        # Get description
        descriptions = cve.get('descriptions', [])
        description = descriptions[0].get('value', '') if descriptions else ''

        # Get CVSS score
        metrics = cve.get('metrics', {})
        cvss_v3 = metrics.get('cvssMetricV31', [])
        severity = 'UNKNOWN'
        base_score = 0.0

        if cvss_v3:
            cvss_data = cvss_v3[0].get('cvssData', {})
            severity = cvss_data.get('baseSeverity', 'UNKNOWN')
            base_score = cvss_data.get('baseScore', 0.0)

        # Map to NIST control
        control = 'SI-2'  # Flaw Remediation

        log_templates = [
            f"Vulnerability scan: {cve_id} detected ({severity}) - Patch required",
            f"CVE alert: {cve_id} ({severity}, CVSS {base_score}) - System vulnerable",
            f"Security patch available: {cve_id} - Update recommended",
            f"Threat intelligence: {cve_id} ({severity}) - Mitigation in progress"
        ]

        log_message = random.choice(log_templates)

        # High severity = non-compliant, others = compliant
        is_compliant = severity not in ['CRITICAL', 'HIGH'] or random.random() < 0.3

        event = {
            'timestamp': datetime.now().isoformat(),
            'log_message': log_message,
            'source': 'nist_nvd_scanner',
            'event_type': 'vulnerability_scan',
            'control_id': control,
            'cve_id': cve_id,
            'cvss_score': base_score,
            'severity': severity,
            'user': f'scanner_{random.randint(1, 10)}',
            'ip_address': f'10.10.{random.randint(1, 255)}.{random.randint(1, 255)}',
            'resource': 'server',
            'status_code': 200 if is_compliant else 500,
            'compliance_status': 'compliant' if is_compliant else 'non_compliant',
            'anomaly_type': 'normal' if is_compliant else 'critical' if severity == 'CRITICAL' else 'suspicious',
            'description': description[:200]
        }

        return event

    def create_enriched_dataset(self) -> Tuple[pd.DataFrame, Dict]:
        """
        Create enriched dataset combining all compliance frameworks

        Returns:
            Tuple of (DataFrame, statistics dict)
        """
        logger.info("Creating enriched compliance dataset...")

        # Process all frameworks
        mitre_df = self.process_mitre_attck()
        owasp_df = self.process_owasp()
        cis_df = self.process_cis_controls()
        pci_df = self.process_pci_dss()
        nvd_df = self.process_nist_nvd()

        # Combine all datasets
        all_dfs = [df for df in [mitre_df, owasp_df, cis_df, pci_df, nvd_df] if not df.empty]

        if not all_dfs:
            logger.error("No compliance data processed")
            return pd.DataFrame(), {}

        combined_df = pd.concat(all_dfs, ignore_index=True)

        # Shuffle dataset
        combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)

        # Calculate statistics
        stats = {
            'total_events': len(combined_df),
            'mitre_events': len(mitre_df),
            'owasp_events': len(owasp_df),
            'cis_events': len(cis_df),
            'pci_events': len(pci_df),
            'nvd_events': len(nvd_df),
            'compliance_distribution': combined_df['compliance_status'].value_counts().to_dict(),
            'anomaly_distribution': combined_df['anomaly_type'].value_counts().to_dict(),
            'source_distribution': combined_df['source'].value_counts().to_dict(),
            'created': datetime.now().isoformat()
        }

        logger.info(f"✅ Created enriched dataset with {len(combined_df)} events")
        logger.info(f"Compliance distribution: {stats['compliance_distribution']}")

        # Save dataset
        output_file = self.output_dir / "compliance_enriched_dataset.csv"
        combined_df.to_csv(output_file, index=False)
        logger.info(f"✅ Saved to: {output_file}")

        # Save statistics
        stats_file = self.output_dir / "dataset_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)
        logger.info(f"✅ Saved statistics to: {stats_file}")

        return combined_df, stats


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("COMPLIANCE DATA PROCESSOR")
    print("="*80)
    print()

    processor = ComplianceDataProcessor()
    df, stats = processor.create_enriched_dataset()

    print()
    print("="*80)
    print("PROCESSING COMPLETE")
    print("="*80)
    print(f"Total events: {stats['total_events']}")
    print(f"  - MITRE ATT&CK: {stats['mitre_events']}")
    print(f"  - OWASP Top 10: {stats['owasp_events']}")
    print(f"  - CIS Controls: {stats['cis_events']}")
    print(f"  - PCI DSS: {stats['pci_events']}")
    print(f"  - NIST NVD: {stats['nvd_events']}")
    print()
    print(f"Compliance Status:")
    for status, count in stats['compliance_distribution'].items():
        print(f"  - {status}: {count} ({count/stats['total_events']*100:.1f}%)")
    print("="*80)


if __name__ == '__main__':
    main()
