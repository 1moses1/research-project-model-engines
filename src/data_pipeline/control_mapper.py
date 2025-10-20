"""
Control Definitions Mapper for NIST SP 800-53 and Rwanda NCSA Standards.

This module maps regulatory controls to structured definitions for ML training.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config_loader import ConfigLoader
from utils.logger import setup_logger


class ControlMapper:
    """
    Maps NIST SP 800-53 and Rwanda NCSA controls to structured definitions.
    """

    def __init__(self, output_dir: str = "data/processed"):
        """
        Initialize ControlMapper.

        Args:
            output_dir: Directory to save control mappings
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.config_loader = ConfigLoader()
        self.logger = setup_logger("control_mapper", "logs/control_mapper.log")

        self.nist_controls = self.config_loader.get_nist_controls()
        self.rwanda_controls = self.config_loader.get_rwanda_controls()

        self.logger.info(f"Loaded {len(self.nist_controls)} NIST controls")
        self.logger.info(f"Loaded {len(self.rwanda_controls)} Rwanda controls")

    def create_nist_control_definitions(self) -> List[Dict[str, Any]]:
        """
        Create structured definitions for NIST SP 800-53 controls.

        Returns:
            List of control definition dictionaries
        """
        # NIST Control metadata (based on SP 800-53 Rev 5)
        nist_definitions = {
            "AC-2": {
                "name": "Account Management",
                "family": "Access Control",
                "description": "Manage system accounts including creation, modification, and deletion",
                "log_indicators": ["user creation", "account modification", "privilege escalation", "account deletion", "account disabled"],
                "compliance_criteria": {
                    "must_have": ["audit trail", "authorization", "periodic review"],
                    "frequency": "continuous",
                    "retention": "90 days"
                }
            },
            "AC-3": {
                "name": "Access Enforcement",
                "family": "Access Control",
                "description": "Enforce approved authorizations for logical access to information and system resources",
                "log_indicators": ["access denied", "permission check", "authorization failure", "unauthorized access attempt"],
                "compliance_criteria": {
                    "must_have": ["access control policy", "enforcement mechanism", "audit logging"],
                    "frequency": "continuous",
                    "retention": "180 days"
                }
            },
            "AC-6": {
                "name": "Least Privilege",
                "family": "Access Control",
                "description": "Employ the principle of least privilege",
                "log_indicators": ["privilege escalation", "admin access", "elevated permissions", "sudo command"],
                "compliance_criteria": {
                    "must_have": ["privilege review", "justification", "temporary elevation"],
                    "frequency": "quarterly",
                    "retention": "365 days"
                }
            },
            "AC-17": {
                "name": "Remote Access",
                "family": "Access Control",
                "description": "Establish and document usage restrictions for remote access",
                "log_indicators": ["remote login", "VPN connection", "SSH access", "remote desktop"],
                "compliance_criteria": {
                    "must_have": ["encryption", "multi-factor authentication", "access logging"],
                    "frequency": "continuous",
                    "retention": "180 days"
                }
            },
            "AU-2": {
                "name": "Event Logging",
                "family": "Audit and Accountability",
                "description": "Determine which events to audit and coordinate with related organizations",
                "log_indicators": ["event logged", "audit record created", "system activity", "user action"],
                "compliance_criteria": {
                    "must_have": ["comprehensive logging", "event correlation", "timestamp accuracy"],
                    "frequency": "continuous",
                    "retention": "365 days"
                }
            },
            "AU-3": {
                "name": "Content of Audit Records",
                "family": "Audit and Accountability",
                "description": "Ensure audit records contain information necessary for investigations",
                "log_indicators": ["timestamp", "user ID", "event type", "outcome", "source IP"],
                "compliance_criteria": {
                    "must_have": ["event type", "timestamp", "subject identity", "outcome", "object identity"],
                    "frequency": "continuous",
                    "retention": "365 days"
                }
            },
            "AU-6": {
                "name": "Audit Review and Analysis",
                "family": "Audit and Accountability",
                "description": "Review and analyze system audit records for inappropriate activity",
                "log_indicators": ["audit review", "anomaly detected", "security violation", "pattern analysis"],
                "compliance_criteria": {
                    "must_have": ["regular review", "automated analysis", "incident reporting"],
                    "frequency": "weekly",
                    "retention": "365 days"
                }
            },
            "AU-9": {
                "name": "Protection of Audit Information",
                "family": "Audit and Accountability",
                "description": "Protect audit information and audit logging tools from unauthorized access",
                "log_indicators": ["audit log access", "log tampering attempt", "audit tool modification"],
                "compliance_criteria": {
                    "must_have": ["access restrictions", "integrity protection", "backup"],
                    "frequency": "continuous",
                    "retention": "indefinite"
                }
            },
            "AU-12": {
                "name": "Audit Record Generation",
                "family": "Audit and Accountability",
                "description": "Provide audit record generation capability for defined events",
                "log_indicators": ["audit record generated", "logging enabled", "capture event data"],
                "compliance_criteria": {
                    "must_have": ["configurable logging", "timestamp synchronization", "event correlation"],
                    "frequency": "continuous",
                    "retention": "365 days"
                }
            },
            "CM-2": {
                "name": "Baseline Configuration",
                "family": "Configuration Management",
                "description": "Develop, document, and maintain baseline configurations",
                "log_indicators": ["configuration change", "baseline update", "system modification"],
                "compliance_criteria": {
                    "must_have": ["documented baseline", "change control", "version management"],
                    "frequency": "quarterly",
                    "retention": "indefinite"
                }
            },
            "CM-6": {
                "name": "Configuration Settings",
                "family": "Configuration Management",
                "description": "Establish and document mandatory configuration settings",
                "log_indicators": ["configuration changed", "setting modified", "policy violation"],
                "compliance_criteria": {
                    "must_have": ["approved settings", "deviation tracking", "remediation"],
                    "frequency": "continuous",
                    "retention": "365 days"
                }
            },
            "CM-7": {
                "name": "Least Functionality",
                "family": "Configuration Management",
                "description": "Configure systems to provide only essential capabilities",
                "log_indicators": ["service disabled", "unnecessary protocol", "port closure"],
                "compliance_criteria": {
                    "must_have": ["minimal services", "prohibited function list", "periodic review"],
                    "frequency": "quarterly",
                    "retention": "365 days"
                }
            },
            "CP-2": {
                "name": "Contingency Plan",
                "family": "Contingency Planning",
                "description": "Develop and maintain a contingency plan",
                "log_indicators": ["contingency plan update", "recovery procedure", "plan test"],
                "compliance_criteria": {
                    "must_have": ["documented plan", "recovery procedures", "annual testing"],
                    "frequency": "annually",
                    "retention": "indefinite"
                }
            },
            "CP-9": {
                "name": "System Backup",
                "family": "Contingency Planning",
                "description": "Conduct backups of system-level and user-level information",
                "log_indicators": ["backup completed", "backup failed", "restore operation", "backup verification"],
                "compliance_criteria": {
                    "must_have": ["regular backups", "offsite storage", "integrity verification"],
                    "frequency": "daily",
                    "retention": "90 days"
                }
            },
            "IA-2": {
                "name": "User Identification and Authentication",
                "family": "Identification and Authentication",
                "description": "Uniquely identify and authenticate organizational users",
                "log_indicators": ["login attempt", "authentication success", "authentication failure", "multi-factor auth"],
                "compliance_criteria": {
                    "must_have": ["unique identifiers", "authentication mechanism", "failed attempt logging"],
                    "frequency": "continuous",
                    "retention": "180 days"
                }
            },
            "IA-4": {
                "name": "Identifier Management",
                "family": "Identification and Authentication",
                "description": "Manage system identifiers",
                "log_indicators": ["identifier created", "identifier modified", "identifier revoked"],
                "compliance_criteria": {
                    "must_have": ["unique identifiers", "identifier lifecycle", "reuse prevention"],
                    "frequency": "continuous",
                    "retention": "365 days"
                }
            },
            "IA-5": {
                "name": "Authenticator Management",
                "family": "Identification and Authentication",
                "description": "Manage system authenticators (passwords, tokens, etc.)",
                "log_indicators": ["password change", "password reset", "authenticator update", "weak password"],
                "compliance_criteria": {
                    "must_have": ["strength requirements", "periodic change", "secure distribution"],
                    "frequency": "90 days",
                    "retention": "365 days"
                }
            },
            "IR-4": {
                "name": "Incident Handling",
                "family": "Incident Response",
                "description": "Implement incident handling capability",
                "log_indicators": ["incident detected", "incident reported", "incident response", "containment action"],
                "compliance_criteria": {
                    "must_have": ["incident response plan", "detection capability", "reporting procedure"],
                    "frequency": "continuous",
                    "retention": "indefinite"
                }
            },
            "IR-5": {
                "name": "Incident Monitoring",
                "family": "Incident Response",
                "description": "Track and document system security incidents",
                "log_indicators": ["incident tracked", "monitoring alert", "security event", "incident status"],
                "compliance_criteria": {
                    "must_have": ["tracking system", "trend analysis", "metrics collection"],
                    "frequency": "continuous",
                    "retention": "indefinite"
                }
            },
            "IR-6": {
                "name": "Incident Reporting",
                "family": "Incident Response",
                "description": "Require personnel to report suspected security incidents",
                "log_indicators": ["incident reported", "report submitted", "notification sent"],
                "compliance_criteria": {
                    "must_have": ["reporting procedure", "timely reporting", "designated personnel"],
                    "frequency": "immediate",
                    "retention": "indefinite"
                }
            },
            "RA-3": {
                "name": "Risk Assessment",
                "family": "Risk Assessment",
                "description": "Conduct risk assessments regularly",
                "log_indicators": ["risk assessment", "vulnerability identified", "threat analysis"],
                "compliance_criteria": {
                    "must_have": ["documented methodology", "risk identification", "mitigation plans"],
                    "frequency": "annually",
                    "retention": "indefinite"
                }
            },
            "RA-5": {
                "name": "Vulnerability Monitoring and Scanning",
                "family": "Risk Assessment",
                "description": "Monitor and scan for vulnerabilities",
                "log_indicators": ["vulnerability scan", "patch available", "security update", "CVE identified"],
                "compliance_criteria": {
                    "must_have": ["regular scanning", "vulnerability database", "remediation tracking"],
                    "frequency": "monthly",
                    "retention": "365 days"
                }
            },
            "SC-7": {
                "name": "Boundary Protection",
                "family": "System and Communications Protection",
                "description": "Monitor and control communications at system boundaries",
                "log_indicators": ["firewall block", "boundary violation", "traffic filtered", "connection denied"],
                "compliance_criteria": {
                    "must_have": ["firewall", "intrusion detection", "traffic monitoring"],
                    "frequency": "continuous",
                    "retention": "180 days"
                }
            },
            "SC-8": {
                "name": "Transmission Confidentiality and Integrity",
                "family": "System and Communications Protection",
                "description": "Protect the confidentiality and integrity of transmitted information",
                "log_indicators": ["encrypted transmission", "TLS connection", "unencrypted traffic", "cipher negotiation"],
                "compliance_criteria": {
                    "must_have": ["encryption", "integrity protection", "approved protocols"],
                    "frequency": "continuous",
                    "retention": "180 days"
                }
            },
            "SC-12": {
                "name": "Cryptographic Key Establishment and Management",
                "family": "System and Communications Protection",
                "description": "Establish and manage cryptographic keys",
                "log_indicators": ["key generated", "key rotated", "key expired", "key revoked"],
                "compliance_criteria": {
                    "must_have": ["key lifecycle", "secure generation", "rotation schedule"],
                    "frequency": "annually",
                    "retention": "indefinite"
                }
            },
            "SI-2": {
                "name": "Flaw Remediation",
                "family": "System and Information Integrity",
                "description": "Identify, report, and correct system flaws",
                "log_indicators": ["patch installed", "flaw identified", "update applied", "remediation completed"],
                "compliance_criteria": {
                    "must_have": ["flaw tracking", "patch management", "testing before deployment"],
                    "frequency": "monthly",
                    "retention": "365 days"
                }
            },
            "SI-3": {
                "name": "Malicious Code Protection",
                "family": "System and Information Integrity",
                "description": "Implement malicious code protection mechanisms",
                "log_indicators": ["malware detected", "virus scan", "quarantine action", "signature update"],
                "compliance_criteria": {
                    "must_have": ["anti-malware software", "regular updates", "real-time protection"],
                    "frequency": "continuous",
                    "retention": "180 days"
                }
            },
            "SI-4": {
                "name": "System Monitoring",
                "family": "System and Information Integrity",
                "description": "Monitor the system to detect attacks and indicators of potential attacks",
                "log_indicators": ["intrusion detected", "anomaly identified", "security alert", "monitoring event"],
                "compliance_criteria": {
                    "must_have": ["continuous monitoring", "alert generation", "analysis capability"],
                    "frequency": "continuous",
                    "retention": "365 days"
                }
            },
            "SI-7": {
                "name": "Software, Firmware, and Information Integrity",
                "family": "System and Information Integrity",
                "description": "Detect unauthorized changes to software and information",
                "log_indicators": ["integrity check", "checksum verification", "unauthorized modification", "file change"],
                "compliance_criteria": {
                    "must_have": ["integrity verification tools", "baseline comparison", "alert on change"],
                    "frequency": "continuous",
                    "retention": "365 days"
                }
            }
        }

        control_definitions = []

        for control_id in self.nist_controls:
            if control_id in nist_definitions:
                definition = {
                    "control_id": control_id,
                    "framework": "NIST-800-53",
                    **nist_definitions[control_id]
                }
                control_definitions.append(definition)
            else:
                self.logger.warning(f"No definition found for NIST control: {control_id}")

        self.logger.info(f"Created {len(control_definitions)} NIST control definitions")
        return control_definitions

    def create_rwanda_control_definitions(self) -> List[Dict[str, Any]]:
        """
        Create structured definitions for Rwanda NCSA controls.

        Returns:
            List of control definition dictionaries
        """
        # Rwanda control metadata (based on NCSA Minimum Cybersecurity Standards)
        rwanda_definitions = {
            "RW-AC-001": {
                "name": "User Account Management",
                "family": "Access Control",
                "description": "Manage user accounts according to Rwanda NCSA standards",
                "nist_mapping": ["AC-2", "IA-4"],
                "log_indicators": ["account created", "user added", "account removed", "access granted"],
                "compliance_criteria": {
                    "must_have": ["approval process", "periodic review", "termination procedure"],
                    "frequency": "continuous",
                    "retention": "180 days"
                }
            },
            "RW-AC-002": {
                "name": "Access Control Policies",
                "family": "Access Control",
                "description": "Implement and enforce access control policies",
                "nist_mapping": ["AC-3", "AC-6"],
                "log_indicators": ["access policy", "permission check", "authorization"],
                "compliance_criteria": {
                    "must_have": ["documented policy", "enforcement mechanism", "annual review"],
                    "frequency": "continuous",
                    "retention": "indefinite"
                }
            },
            "RW-AC-003": {
                "name": "Privilege Management",
                "family": "Access Control",
                "description": "Control privileged access to critical systems",
                "nist_mapping": ["AC-6"],
                "log_indicators": ["admin access", "privileged operation", "elevated rights"],
                "compliance_criteria": {
                    "must_have": ["least privilege", "privilege review", "justification"],
                    "frequency": "quarterly",
                    "retention": "365 days"
                }
            },
            "RW-AU-001": {
                "name": "Audit Logging Requirements",
                "family": "Audit and Accountability",
                "description": "Implement comprehensive audit logging",
                "nist_mapping": ["AU-2", "AU-3", "AU-12"],
                "log_indicators": ["event logged", "audit record", "logging enabled"],
                "compliance_criteria": {
                    "must_have": ["comprehensive logging", "timestamp", "event details"],
                    "frequency": "continuous",
                    "retention": "365 days"
                }
            },
            "RW-AU-002": {
                "name": "Log Retention Standards",
                "family": "Audit and Accountability",
                "description": "Maintain audit logs per Rwanda requirements",
                "nist_mapping": ["AU-9", "AU-11"],
                "log_indicators": ["log archived", "retention compliance", "log backup"],
                "compliance_criteria": {
                    "must_have": ["minimum 1 year retention", "secure storage", "integrity protection"],
                    "frequency": "continuous",
                    "retention": "365 days"
                }
            },
            "RW-AU-003": {
                "name": "Audit Review Procedures",
                "family": "Audit and Accountability",
                "description": "Regular review of audit logs",
                "nist_mapping": ["AU-6"],
                "log_indicators": ["log review", "audit analysis", "anomaly detection"],
                "compliance_criteria": {
                    "must_have": ["regular review", "documented procedures", "incident escalation"],
                    "frequency": "weekly",
                    "retention": "365 days"
                }
            },
            "RW-IR-001": {
                "name": "Incident Response Plan",
                "family": "Incident Response",
                "description": "Maintain incident response plan per NCSA requirements",
                "nist_mapping": ["IR-8", "IR-4"],
                "log_indicators": ["IR plan updated", "response procedure", "plan tested"],
                "compliance_criteria": {
                    "must_have": ["documented plan", "contact information", "annual testing"],
                    "frequency": "annually",
                    "retention": "indefinite"
                }
            },
            "RW-IR-002": {
                "name": "Incident Reporting Requirements",
                "family": "Incident Response",
                "description": "Report incidents to NCSA as required",
                "nist_mapping": ["IR-6"],
                "log_indicators": ["incident reported", "NCSA notification", "report submitted"],
                "compliance_criteria": {
                    "must_have": ["24-hour reporting", "incident classification", "NCSA contact"],
                    "frequency": "immediate",
                    "retention": "indefinite"
                }
            },
            "RW-IR-003": {
                "name": "Incident Response Team",
                "family": "Incident Response",
                "description": "Establish and maintain incident response team",
                "nist_mapping": ["IR-4"],
                "log_indicators": ["team activated", "incident handled", "response initiated"],
                "compliance_criteria": {
                    "must_have": ["designated team", "training", "contact list"],
                    "frequency": "continuous",
                    "retention": "indefinite"
                }
            },
            "RW-VM-001": {
                "name": "Vulnerability Assessment",
                "family": "Vulnerability Management",
                "description": "Conduct regular vulnerability assessments",
                "nist_mapping": ["RA-5"],
                "log_indicators": ["vulnerability scan", "assessment completed", "findings documented"],
                "compliance_criteria": {
                    "must_have": ["quarterly scans", "remediation plan", "tracking"],
                    "frequency": "quarterly",
                    "retention": "365 days"
                }
            },
            "RW-VM-002": {
                "name": "Patch Management",
                "family": "Vulnerability Management",
                "description": "Apply security patches in timely manner",
                "nist_mapping": ["SI-2"],
                "log_indicators": ["patch installed", "update applied", "patching delayed"],
                "compliance_criteria": {
                    "must_have": ["30-day critical patches", "testing", "documentation"],
                    "frequency": "monthly",
                    "retention": "365 days"
                }
            },
            "RW-VM-003": {
                "name": "Security Updates",
                "family": "Vulnerability Management",
                "description": "Maintain current security updates",
                "nist_mapping": ["SI-2"],
                "log_indicators": ["security update", "version current", "update status"],
                "compliance_criteria": {
                    "must_have": ["update tracking", "current versions", "EOL monitoring"],
                    "frequency": "continuous",
                    "retention": "180 days"
                }
            },
            "RW-SH-001": {
                "name": "System Hardening Standards",
                "family": "System Hardening",
                "description": "Harden systems according to Rwanda standards",
                "nist_mapping": ["CM-6", "CM-7"],
                "log_indicators": ["hardening applied", "configuration secured", "unnecessary service disabled"],
                "compliance_criteria": {
                    "must_have": ["hardening checklist", "verification", "documentation"],
                    "frequency": "at deployment",
                    "retention": "indefinite"
                }
            },
            "RW-SH-002": {
                "name": "Secure Configuration",
                "family": "System Hardening",
                "description": "Implement secure configuration baselines",
                "nist_mapping": ["CM-2", "CM-6"],
                "log_indicators": ["configuration applied", "baseline compliance", "setting verified"],
                "compliance_criteria": {
                    "must_have": ["approved baseline", "deviation tracking", "remediation"],
                    "frequency": "continuous",
                    "retention": "indefinite"
                }
            },
            "RW-SH-003": {
                "name": "Baseline Security Settings",
                "family": "System Hardening",
                "description": "Maintain baseline security settings",
                "nist_mapping": ["CM-2"],
                "log_indicators": ["baseline verified", "configuration drift", "setting changed"],
                "compliance_criteria": {
                    "must_have": ["documented baseline", "compliance checking", "annual review"],
                    "frequency": "quarterly",
                    "retention": "indefinite"
                }
            },
            "RW-BC-001": {
                "name": "Business Continuity Planning",
                "family": "Business Continuity",
                "description": "Maintain business continuity plan",
                "nist_mapping": ["CP-2"],
                "log_indicators": ["BC plan updated", "continuity test", "plan reviewed"],
                "compliance_criteria": {
                    "must_have": ["documented plan", "annual testing", "update procedure"],
                    "frequency": "annually",
                    "retention": "indefinite"
                }
            },
            "RW-BC-002": {
                "name": "Backup and Recovery",
                "family": "Business Continuity",
                "description": "Implement backup and recovery procedures",
                "nist_mapping": ["CP-9", "CP-10"],
                "log_indicators": ["backup completed", "backup verified", "recovery tested"],
                "compliance_criteria": {
                    "must_have": ["daily backups", "offsite storage", "recovery testing"],
                    "frequency": "daily",
                    "retention": "90 days"
                }
            },
            "RW-BC-003": {
                "name": "Disaster Recovery",
                "family": "Business Continuity",
                "description": "Maintain disaster recovery capabilities",
                "nist_mapping": ["CP-10"],
                "log_indicators": ["DR test", "recovery procedure", "failover tested"],
                "compliance_criteria": {
                    "must_have": ["DR plan", "RTO/RPO defined", "annual testing"],
                    "frequency": "annually",
                    "retention": "indefinite"
                }
            },
            "RW-DP-001": {
                "name": "Data Protection Standards",
                "family": "Data Protection",
                "description": "Protect sensitive data per Rwanda requirements",
                "nist_mapping": ["MP-2", "MP-6", "SC-8"],
                "log_indicators": ["data encrypted", "data classification", "protection applied"],
                "compliance_criteria": {
                    "must_have": ["data classification", "encryption", "access control"],
                    "frequency": "continuous",
                    "retention": "indefinite"
                }
            },
            "RW-DP-002": {
                "name": "Encryption Requirements",
                "family": "Data Protection",
                "description": "Encrypt data at rest and in transit",
                "nist_mapping": ["SC-8", "SC-12", "SC-13"],
                "log_indicators": ["encryption enabled", "data encrypted", "TLS used"],
                "compliance_criteria": {
                    "must_have": ["AES-256 or equivalent", "key management", "transport encryption"],
                    "frequency": "continuous",
                    "retention": "indefinite"
                }
            },
            "RW-DP-003": {
                "name": "Data Classification",
                "family": "Data Protection",
                "description": "Classify and label data appropriately",
                "nist_mapping": ["MP-3"],
                "log_indicators": ["data classified", "label applied", "classification reviewed"],
                "compliance_criteria": {
                    "must_have": ["classification scheme", "labeling", "handling procedures"],
                    "frequency": "at creation",
                    "retention": "indefinite"
                }
            }
        }

        control_definitions = []

        for control_id in self.rwanda_controls:
            if control_id in rwanda_definitions:
                definition = {
                    "control_id": control_id,
                    "framework": "Rwanda-NCSA",
                    **rwanda_definitions[control_id]
                }
                control_definitions.append(definition)
            else:
                self.logger.warning(f"No definition found for Rwanda control: {control_id}")

        self.logger.info(f"Created {len(control_definitions)} Rwanda control definitions")
        return control_definitions

    def create_control_taxonomy(self) -> Dict[str, Any]:
        """
        Create complete control taxonomy combining NIST and Rwanda.

        Returns:
            Dictionary containing all control definitions and mappings
        """
        nist_defs = self.create_nist_control_definitions()
        rwanda_defs = self.create_rwanda_control_definitions()

        taxonomy = {
            "metadata": {
                "total_controls": len(nist_defs) + len(rwanda_defs),
                "nist_controls": len(nist_defs),
                "rwanda_controls": len(rwanda_defs),
                "generated_at": str(Path(__file__).parent)
            },
            "nist": nist_defs,
            "rwanda": rwanda_defs,
            "control_families": self._extract_control_families(nist_defs + rwanda_defs)
        }

        return taxonomy

    def _extract_control_families(self, controls: List[Dict]) -> Dict[str, List[str]]:
        """Extract unique control families and their controls."""
        families = {}

        for control in controls:
            family = control.get("family", "Unknown")
            if family not in families:
                families[family] = []
            families[family].append(control["control_id"])

        return families

    def save_control_taxonomy(self, filename: str = "control_taxonomy.json"):
        """
        Save control taxonomy to JSON file.

        Args:
            filename: Output filename
        """
        taxonomy = self.create_control_taxonomy()
        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(taxonomy, f, indent=2)

        self.logger.info(f"Control taxonomy saved to: {output_path}")
        self.logger.info(f"Total controls: {taxonomy['metadata']['total_controls']}")

        return output_path


if __name__ == "__main__":
    # Create control mapper and generate taxonomy
    mapper = ControlMapper()

    # Create and save control taxonomy
    output_path = mapper.save_control_taxonomy()

    print(f"\n✅ Control taxonomy created successfully!")
    print(f"📁 Output: {output_path}")

    # Print summary
    taxonomy = mapper.create_control_taxonomy()
    print(f"\n📊 Summary:")
    print(f"  - Total Controls: {taxonomy['metadata']['total_controls']}")
    print(f"  - NIST Controls: {taxonomy['metadata']['nist_controls']}")
    print(f"  - Rwanda Controls: {taxonomy['metadata']['rwanda_controls']}")
    print(f"  - Control Families: {len(taxonomy['control_families'])}")

    print(f"\n🏷️  Control Families:")
    for family, controls in taxonomy['control_families'].items():
        print(f"  - {family}: {len(controls)} controls")
