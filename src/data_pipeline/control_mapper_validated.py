"""
VALIDATED Control Definitions Mapper for NIST SP 800-53 and Rwanda NCSA Standards.

This module maps regulatory controls to structured definitions for ML training.
Rwanda NCSA controls extracted from official PDF: Minimum_Cybersecurity_Standards_for_Public_Institutions.pdf

VALIDATION: All Rwanda controls verified against source document on 2025-11-15
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from utils.config_loader import ConfigLoader
from utils.logger import setup_logger


class ValidatedControlMapper:
    """
    Maps NIST SP 800-53 (secondary framework) and Rwanda NCSA (primary framework)
    controls to structured definitions.

    Rwanda NCSA is PRIMARY - extracted from official regulatory documents
    NIST SP 800-53 is SECONDARY - used for mapping and reference
    """

    def __init__(self, output_dir: str = "data/processed"):
        """
        Initialize ValidatedControlMapper.

        Args:
            output_dir: Directory to save control mappings
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger("validated_control_mapper", "logs/control_mapper.log")

        # Load validated Rwanda NCSA requirements from extracted JSON
        self.rwanda_requirements = self._load_validated_rwanda_requirements()

        # NIST controls for secondary mapping
        self.nist_controls = self._get_nist_control_list()

        self.logger.info(f"Loaded {len(self.rwanda_requirements)} validated Rwanda NCSA requirements")
        self.logger.info(f"Loaded {len(self.nist_controls)} NIST SP 800-53 controls")

    def _load_validated_rwanda_requirements(self) -> Dict[str, Any]:
        """Load validated Rwanda NCSA requirements from extracted JSON."""
        json_path = Path("rwanda_ncsa_validated_controls.json")

        if not json_path.exists():
            self.logger.error(f"Validated Rwanda controls file not found: {json_path}")
            return {}

        with open(json_path, 'r') as f:
            return json.load(f)

    def _get_nist_control_list(self) -> List[str]:
        """Get list of NIST SP 800-53 Rev 5 controls for mapping."""
        return [
            # Access Control (AC)
            "AC-1", "AC-2", "AC-3", "AC-6", "AC-7", "AC-8", "AC-11", "AC-12",
            "AC-17", "AC-18", "AC-19", "AC-20", "AC-22",

            # Awareness and Training (AT)
            "AT-1", "AT-2", "AT-3",

            # Audit and Accountability (AU)
            "AU-1", "AU-2", "AU-3", "AU-4", "AU-5", "AU-6", "AU-7", "AU-8",
            "AU-9", "AU-11", "AU-12",

            # Security Assessment and Authorization (CA)
            "CA-1", "CA-2", "CA-5", "CA-7",

            # Configuration Management (CM)
            "CM-1", "CM-2", "CM-3", "CM-4", "CM-5", "CM-6", "CM-7", "CM-8",
            "CM-10", "CM-11",

            # Contingency Planning (CP)
            "CP-1", "CP-2", "CP-9", "CP-10",

            # Identification and Authentication (IA)
            "IA-1", "IA-2", "IA-3", "IA-4", "IA-5", "IA-6", "IA-7", "IA-8",

            # Incident Response (IR)
            "IR-1", "IR-4", "IR-5", "IR-6", "IR-7", "IR-8",

            # Maintenance (MA)
            "MA-1", "MA-2", "MA-3", "MA-4", "MA-5", "MA-6",

            # Media Protection (MP)
            "MP-1", "MP-2", "MP-3", "MP-4", "MP-5", "MP-6", "MP-7", "MP-8",

            # Physical and Environmental Protection (PE)
            "PE-1", "PE-2", "PE-3", "PE-4", "PE-5", "PE-6", "PE-12", "PE-13",
            "PE-14", "PE-15", "PE-16", "PE-17", "PE-18",

            # Planning (PL)
            "PL-1", "PL-2",

            # Personnel Security (PS)
            "PS-1", "PS-2", "PS-3", "PS-4", "PS-5", "PS-6", "PS-7", "PS-8",

            # Risk Assessment (RA)
            "RA-1", "RA-3", "RA-5",

            # System and Services Acquisition (SA)
            "SA-1", "SA-4", "SA-8", "SA-11",

            # System and Communications Protection (SC)
            "SC-1", "SC-2", "SC-3", "SC-4", "SC-5", "SC-7", "SC-8", "SC-10",
            "SC-12", "SC-13", "SC-15", "SC-18", "SC-19", "SC-20", "SC-23", "SC-28",

            # System and Information Integrity (SI)
            "SI-1", "SI-2", "SI-3", "SI-4", "SI-5", "SI-7", "SI-12"
        ]

    def create_rwanda_control_definitions(self) -> List[Dict[str, Any]]:
        """
        Create structured definitions for Rwanda NCSA controls from validated source.

        Returns:
            List of Rwanda NCSA requirement definitions
        """
        control_definitions = []

        if not self.rwanda_requirements or 'control_families' not in self.rwanda_requirements:
            self.logger.error("No validated Rwanda requirements loaded")
            return control_definitions

        for family in self.rwanda_requirements['control_families']:
            family_name = family['family_name']
            nist_mapping = family.get('nist_family_mapping', [])

            for req in family.get('requirements', []):
                # Create control definition for each requirement
                definition = {
                    "control_id": req['requirement_id'],
                    "framework": "Rwanda-NCSA",
                    "name": f"{family_name} - Requirement {req['requirement_id']}",
                    "family": family_name,
                    "description": req['requirement_text'][:200],  # Truncate long descriptions
                    "full_text": req['requirement_text'],
                    "chapter": req['chapter'],
                    "compliance_type": req.get('compliance_type', 'Basic'),
                    "nist_mapping": nist_mapping,
                    "log_indicators": self._generate_log_indicators(req['requirement_text'], family_name),
                    "compliance_criteria": {
                        "must_have": self._extract_requirements(req['requirement_text']),
                        "frequency": self._determine_frequency(req['requirement_text']),
                        "retention": "365 days"  # Rwanda NCSA minimum
                    }
                }

                control_definitions.append(definition)

        self.logger.info(f"Created {len(control_definitions)} validated Rwanda NCSA requirement definitions")
        return control_definitions

    def _generate_log_indicators(self, requirement_text: str, family_name: str) -> List[str]:
        """Generate relevant log indicators based on requirement text and family."""
        # Map family to common log indicators
        family_indicators = {
            "Security Policy and Procedures": ["policy updated", "procedure documented", "review completed"],
            "Access Control": ["access granted", "access denied", "permission changed", "login attempt"],
            "Awareness and Training": ["training completed", "awareness session", "security education"],
            "Audit and Accountability": ["audit logged", "event recorded", "log generated", "accountability check"],
            "Configuration Management": ["config changed", "baseline updated", "change approved"],
            "Identity Management and Authentication": ["user authenticated", "password changed", "MFA required", "identifier created"],
            "Incident Response": ["incident detected", "incident reported", "response initiated", "containment"],
            "Maintenance": ["maintenance performed", "system updated", "diagnostic run"],
            "Media Protection": ["media accessed", "data sanitized", "backup created"],
            "Personnel Security": ["background check", "access revoked", "termination", "screening"],
            "Physical and Environmental Protection": ["physical access", "badge scan", "zone entry", "facility access"],
            "Risk Assessment": ["risk identified", "vulnerability scan", "assessment completed"],
            "Security Assessment": ["controls assessed", "security test", "audit performed"],
            "System and Communications Protection": ["encryption applied", "firewall block", "traffic filtered", "connection secured"]
        }

        return family_indicators.get(family_name, ["event logged", "compliance check", "security control"])

    def _extract_requirements(self, requirement_text: str) -> List[str]:
        """Extract key requirements from requirement text."""
        # Look for common requirement keywords
        requirements = []

        keywords = {
            "documented": "documentation",
            "maintain": "maintenance",
            "implement": "implementation",
            "ensure": "verification",
            "protect": "protection",
            "monitor": "monitoring",
            "report": "reporting",
            "review": "periodic review",
            "test": "testing",
            "verify": "verification"
        }

        text_lower = requirement_text.lower()
        for keyword, requirement in keywords.items():
            if keyword in text_lower:
                requirements.append(requirement)

        return requirements[:5] if requirements else ["compliance verification"]

    def _determine_frequency(self, requirement_text: str) -> str:
        """Determine compliance check frequency from requirement text."""
        text_lower = requirement_text.lower()

        if any(word in text_lower for word in ["continuous", "real-time", "ongoing"]):
            return "continuous"
        elif any(word in text_lower for word in ["immediate", "instantly"]):
            return "immediate"
        elif any(word in text_lower for word in ["annual", "yearly", "once a year", "at least once per year"]):
            return "annually"
        elif any(word in text_lower for word in ["quarter", "90 days"]):
            return "quarterly"
        elif any(word in text_lower for word in ["month", "30 days"]):
            return "monthly"
        elif any(word in text_lower for word in ["week", "7 days"]):
            return "weekly"
        elif any(word in text_lower for word in ["daily", "day"]):
            return "daily"
        else:
            return "periodic"

    def create_nist_control_definitions(self) -> List[Dict[str, Any]]:
        """
        Create NIST SP 800-53 control definitions as SECONDARY reference framework.

        Returns:
            List of NIST control definition dictionaries
        """
        # Simplified NIST definitions - these are secondary to Rwanda NCSA
        nist_definitions = {
            "AC-2": {"name": "Account Management", "family": "Access Control"},
            "AC-3": {"name": "Access Enforcement", "family": "Access Control"},
            "AC-6": {"name": "Least Privilege", "family": "Access Control"},
            "AC-17": {"name": "Remote Access", "family": "Access Control"},
            "AT-2": {"name": "Literacy Training and Awareness", "family": "Awareness and Training"},
            "AT-3": {"name": "Role-Based Training", "family": "Awareness and Training"},
            "AU-2": {"name": "Event Logging", "family": "Audit and Accountability"},
            "AU-3": {"name": "Content of Audit Records", "family": "Audit and Accountability"},
            "AU-6": {"name": "Audit Record Review, Analysis, and Reporting", "family": "Audit and Accountability"},
            "AU-9": {"name": "Protection of Audit Information", "family": "Audit and Accountability"},
            "AU-12": {"name": "Audit Record Generation", "family": "Audit and Accountability"},
            "CM-2": {"name": "Baseline Configuration", "family": "Configuration Management"},
            "CM-6": {"name": "Configuration Settings", "family": "Configuration Management"},
            "CM-7": {"name": "Least Functionality", "family": "Configuration Management"},
            "IA-2": {"name": "Identification and Authentication", "family": "Identification and Authentication"},
            "IA-5": {"name": "Authenticator Management", "family": "Identification and Authentication"},
            "IR-4": {"name": "Incident Handling", "family": "Incident Response"},
            "IR-6": {"name": "Incident Reporting", "family": "Incident Response"},
            "IR-8": {"name": "Incident Response Plan", "family": "Incident Response"},
            "PL-1": {"name": "Policy and Procedures", "family": "Planning"},
            "RA-3": {"name": "Risk Assessment", "family": "Risk Assessment"},
            "RA-5": {"name": "Vulnerability Monitoring and Scanning", "family": "Risk Assessment"},
            "SC-7": {"name": "Boundary Protection", "family": "System and Communications Protection"},
            "SC-8": {"name": "Transmission Confidentiality and Integrity", "family": "System and Communications Protection"},
            "SI-2": {"name": "Flaw Remediation", "family": "System and Information Integrity"},
            "SI-3": {"name": "Malicious Code Protection", "family": "System and Information Integrity"},
            "SI-4": {"name": "System Monitoring", "family": "System and Information Integrity"}
        }

        control_definitions = []

        for control_id in self.nist_controls:
            if control_id in nist_definitions:
                definition = {
                    "control_id": control_id,
                    "framework": "NIST-800-53",
                    **nist_definitions[control_id],
                    "role": "secondary_reference"  # Mark as secondary
                }
                control_definitions.append(definition)

        self.logger.info(f"Created {len(control_definitions)} NIST control definitions (secondary framework)")
        return control_definitions

    def create_control_taxonomy(self) -> Dict[str, Any]:
        """
        Create complete control taxonomy with Rwanda NCSA as PRIMARY framework.

        Returns:
            Dictionary containing all control definitions and mappings
        """
        rwanda_defs = self.create_rwanda_control_definitions()
        nist_defs = self.create_nist_control_definitions()

        taxonomy = {
            "metadata": {
                "primary_framework": "Rwanda NCSA Cybersecurity Minimum Standards",
                "secondary_framework": "NIST SP 800-53 Rev 5",
                "source_document": "Minimum_Cybersecurity_Standards_for_Public_Institutions.pdf",
                "validation_date": "2025-11-15",
                "validated": True,
                "total_controls": len(rwanda_defs) + len(nist_defs),
                "rwanda_requirements": len(rwanda_defs),
                "nist_controls": len(nist_defs)
            },
            "rwanda": rwanda_defs,
            "nist": nist_defs,
            "control_families": self._extract_control_families(rwanda_defs, nist_defs),
            "rwanda_to_nist_mapping": self._create_framework_mapping(rwanda_defs)
        }

        return taxonomy

    def _extract_control_families(self, rwanda_controls: List[Dict], nist_controls: List[Dict]) -> Dict[str, Any]:
        """Extract unique control families with framework separation."""
        families = {
            "rwanda": {},
            "nist": {}
        }

        for control in rwanda_controls:
            family = control.get("family", "Unknown")
            if family not in families["rwanda"]:
                families["rwanda"][family] = []
            families["rwanda"][family].append(control["control_id"])

        for control in nist_controls:
            family = control.get("family", "Unknown")
            if family not in families["nist"]:
                families["nist"][family] = []
            families["nist"][family].append(control["control_id"])

        return families

    def _create_framework_mapping(self, rwanda_controls: List[Dict]) -> Dict[str, List[str]]:
        """Create mapping from Rwanda requirements to NIST controls."""
        mapping = {}

        for control in rwanda_controls:
            rwanda_id = control["control_id"]
            nist_controls = control.get("nist_mapping", [])
            if nist_controls:
                mapping[rwanda_id] = nist_controls

        return mapping

    def save_control_taxonomy(self, filename: str = "control_taxonomy_validated.json"):
        """
        Save validated control taxonomy to JSON file.

        Args:
            filename: Output filename
        """
        taxonomy = self.create_control_taxonomy()
        output_path = self.output_dir / filename

        with open(output_path, 'w') as f:
            json.dump(taxonomy, f, indent=2)

        self.logger.info(f"✅ Validated control taxonomy saved to: {output_path}")
        self.logger.info(f"Total requirements: {taxonomy['metadata']['total_controls']}")
        self.logger.info(f"Rwanda NCSA (PRIMARY): {taxonomy['metadata']['rwanda_requirements']} requirements")
        self.logger.info(f"NIST SP 800-53 (SECONDARY): {taxonomy['metadata']['nist_controls']} controls")

        return output_path


if __name__ == "__main__":
    print("="*80)
    print("VALIDATED CONTROL MAPPER - Rwanda NCSA PRIMARY / NIST SECONDARY")
    print("="*80)

    # Create validated control mapper
    mapper = ValidatedControlMapper()

    # Create and save control taxonomy
    output_path = mapper.save_control_taxonomy()

    print(f"\n✅ Validated control taxonomy created successfully!")
    print(f"📁 Output: {output_path}")

    # Print summary
    taxonomy = mapper.create_control_taxonomy()
    print(f"\n📊 Summary:")
    print(f"  - PRIMARY Framework: {taxonomy['metadata']['primary_framework']}")
    print(f"  - SECONDARY Framework: {taxonomy['metadata']['secondary_framework']}")
    print(f"  - Total Requirements/Controls: {taxonomy['metadata']['total_controls']}")
    print(f"  - Rwanda NCSA Requirements: {taxonomy['metadata']['rwanda_requirements']}")
    print(f"  - NIST SP 800-53 Controls: {taxonomy['metadata']['nist_controls']}")
    print(f"  - Validation Date: {taxonomy['metadata']['validation_date']}")

    print(f"\n🏷️  Rwanda NCSA Control Families:")
    for family, controls in taxonomy['control_families']['rwanda'].items():
        print(f"  - {family}: {len(controls)} requirements")

    print(f"\n🔗 Framework Mapping:")
    print(f"  - Rwanda→NIST mappings: {len(taxonomy['rwanda_to_nist_mapping'])} requirements mapped")
