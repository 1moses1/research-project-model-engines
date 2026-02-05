#!/usr/bin/env python3
"""
NCSA Control Expansion Script

This script generates the expanded ncsa_controls.py with all 169 Rwanda NCSA controls
from the control_taxonomy_validated.json file.

The MCP+LLM architecture allows us to handle ALL control types:
1. System-Auditable: CLI commands + LLM fallback for semantic analysis
2. Policy-Based: Pure LLM document analysis (no CLI needed)
3. Physical: LLM + checklist verification
4. Mixed: Combination of system audit + policy review

Usage:
    python scripts/expand_ncsa_controls.py
"""

import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
TAXONOMY_FILE = PROJECT_ROOT / "engines/engine1-log-collector/data/control_taxonomy_validated.json"
OUTPUT_FILE = PROJECT_ROOT / "engines/engine3-mcp-analyzer/app/models/ncsa_controls_expanded.py"

# Control family to audit type mapping
CONTROL_AUDIT_TYPES = {
    # System-Auditable (can verify via CLI commands)
    "Access Control": "system",
    "Audit and Accountability": "system",
    "System and Communications Protection": "system",
    "Configuration Management": "system",
    "Identity Management and Authentication": "system",
    "Incident Response": "mixed",

    # Policy-Based (LLM document analysis)
    "Security Policy and Procedures": "policy",
    "Risk Assessment": "policy",
    "Security Assessment": "policy",
    "Awareness and Training": "policy",
    "Personnel Security": "policy",

    # Physical (manual + checklist)
    "Physical and Environmental Protection": "physical",

    # Mixed (system + policy)
    "Media Protection": "mixed",
    "Maintenance": "mixed",
}

# Evidence patterns by family (for LLM keyword matching)
FAMILY_EVIDENCE_PATTERNS = {
    "Access Control": [
        "access", "permission", "authorization", "authentication", "login", "logout",
        "session", "account", "user", "role", "privilege", "sudo", "admin", "root",
        "denied", "granted", "locked", "unlocked", "password", "credential"
    ],
    "Audit and Accountability": [
        "audit", "log", "event", "record", "trail", "monitoring", "syslog",
        "journald", "timestamp", "retention", "backup", "archive", "review"
    ],
    "Awareness and Training": [
        "training", "awareness", "education", "policy acknowledgment", "certification",
        "competency", "security awareness", "phishing test", "training record"
    ],
    "Configuration Management": [
        "configuration", "baseline", "change", "update", "patch", "version",
        "inventory", "software", "firmware", "settings", "profile", "policy"
    ],
    "Identity Management and Authentication": [
        "identity", "authentication", "MFA", "multi-factor", "password", "biometric",
        "certificate", "token", "SSO", "LDAP", "Active Directory", "PAM"
    ],
    "Incident Response": [
        "incident", "breach", "alert", "response", "containment", "eradication",
        "recovery", "lessons learned", "post-incident", "forensics", "CSIRT"
    ],
    "Maintenance": [
        "maintenance", "repair", "service", "update", "patch", "upgrade",
        "scheduled", "preventive", "corrective", "remote maintenance"
    ],
    "Media Protection": [
        "media", "storage", "encryption", "sanitization", "disposal", "transport",
        "USB", "removable", "backup", "archive", "data destruction"
    ],
    "Personnel Security": [
        "personnel", "background check", "screening", "termination", "transfer",
        "access revocation", "NDA", "confidentiality", "security clearance"
    ],
    "Physical and Environmental Protection": [
        "physical access", "badge", "visitor", "CCTV", "camera", "alarm",
        "fire", "flood", "temperature", "humidity", "power", "UPS", "generator"
    ],
    "Risk Assessment": [
        "risk", "threat", "vulnerability", "impact", "likelihood", "assessment",
        "risk register", "risk treatment", "risk acceptance", "mitigation"
    ],
    "Security Assessment": [
        "assessment", "audit", "penetration test", "vulnerability scan",
        "compliance check", "control assessment", "POA&M", "remediation"
    ],
    "Security Policy and Procedures": [
        "policy", "procedure", "standard", "guideline", "framework",
        "governance", "compliance", "regulatory", "documentation"
    ],
    "System and Communications Protection": [
        "encryption", "TLS", "SSL", "firewall", "network", "boundary",
        "segmentation", "VPN", "transmission", "cryptographic", "certificate"
    ],
}

# Compliant/Non-compliant indicators by audit type
COMPLIANCE_INDICATORS = {
    "system": {
        "compliant": [
            "Control enabled and configured",
            "Settings meet requirements",
            "Monitoring active",
            "Logs being collected"
        ],
        "non_compliant": [
            "Control not enabled",
            "Settings below requirements",
            "No monitoring configured",
            "Missing log entries"
        ]
    },
    "policy": {
        "compliant": [
            "Policy document exists and current",
            "Procedures documented and followed",
            "Regular review conducted",
            "Staff acknowledgment on file"
        ],
        "non_compliant": [
            "No policy document",
            "Outdated procedures",
            "No evidence of review",
            "Missing acknowledgments"
        ]
    },
    "physical": {
        "compliant": [
            "Physical controls in place",
            "Access logs maintained",
            "Environmental controls active",
            "Regular inspections conducted"
        ],
        "non_compliant": [
            "Physical controls missing",
            "No access logging",
            "Environmental controls failing",
            "No inspection records"
        ]
    },
    "mixed": {
        "compliant": [
            "Technical controls configured",
            "Policy documentation complete",
            "Regular testing performed",
            "Audit evidence available"
        ],
        "non_compliant": [
            "Technical gaps identified",
            "Policy documentation incomplete",
            "No testing evidence",
            "Audit findings unresolved"
        ]
    }
}


def load_taxonomy() -> Dict[str, Any]:
    """Load the control taxonomy file."""
    with open(TAXONOMY_FILE, 'r') as f:
        return json.load(f)


def generate_evidence_patterns(control: Dict, family: str) -> List[str]:
    """Generate evidence patterns for a control based on its family and description."""
    patterns = set()

    # Add family-specific patterns
    if family in FAMILY_EVIDENCE_PATTERNS:
        patterns.update(FAMILY_EVIDENCE_PATTERNS[family][:6])  # Top 6 patterns

    # Extract keywords from description
    description = control.get('description', '').lower()
    keywords = [
        word for word in description.split()
        if len(word) > 4 and word.isalpha()
    ][:5]  # Top 5 meaningful words
    patterns.update(keywords)

    # Add log_indicators if present
    if 'log_indicators' in control:
        patterns.update(control['log_indicators'])

    return list(patterns)[:10]  # Limit to 10 patterns


def generate_nist_mapping(control: Dict) -> str:
    """Extract NIST mapping from control."""
    nist = control.get('nist_mapping', [])
    if isinstance(nist, list) and nist:
        return nist[0]
    elif isinstance(nist, str):
        return nist
    return "N/A"


def generate_control_entry(control: Dict) -> Dict[str, Any]:
    """Generate a control entry for ncsa_controls.py."""
    family = control.get('family', 'Unknown')
    audit_type = CONTROL_AUDIT_TYPES.get(family, 'mixed')

    indicators = COMPLIANCE_INDICATORS.get(audit_type, COMPLIANCE_INDICATORS['mixed'])

    return {
        "control_id": control['control_id'],
        "control_name": control['name'],
        "control_family": family,
        "description": control.get('description', '')[:500],  # Truncate long descriptions
        "nist_mapping": generate_nist_mapping(control),
        "compliance_type": control.get('compliance_type', 'Basic'),
        "audit_type": audit_type,
        "evidence_patterns": generate_evidence_patterns(control, family),
        "compliant_indicators": indicators['compliant'],
        "non_compliant_indicators": indicators['non_compliant'],
        "remediation_guidance": f"Review and implement {family} requirements per NCSA standards"
    }


def generate_python_file(controls: List[Dict]) -> str:
    """Generate the Python file content."""

    # Group controls by family for organization
    by_family = defaultdict(list)
    for ctrl in controls:
        by_family[ctrl['control_family']].append(ctrl)

    # Build the file content
    content = '''"""
Rwanda NCSA Minimum Cybersecurity Standards - Complete Control Database (169 Controls)

This module contains the COMPLETE mapping of Rwanda NCSA controls for MCP+LLM analysis.
Generated from control_taxonomy_validated.json.

Control Types:
- system: System-auditable via CLI commands + LLM semantic analysis
- policy: Policy-based, analyzed by LLM from documents
- physical: Physical controls, LLM + checklist verification
- mixed: Combination of system audit + policy review

Reference: Rwanda NCSA Minimum Cybersecurity Standards (2024)
Total Controls: 169 Rwanda NCSA + 27 NIST Reference = 196
"""

from typing import Dict, List, Any


# =============================================================================
# NCSA Control Families
# =============================================================================

CONTROL_FAMILIES = {
    "AC": "Access Control",
    "AU": "Audit and Accountability",
    "AT": "Awareness and Training",
    "CM": "Configuration Management",
    "CP": "Contingency Planning",
    "IA": "Identification and Authentication",
    "IR": "Incident Response",
    "MA": "Maintenance",
    "MP": "Media Protection",
    "PE": "Physical and Environmental Protection",
    "PL": "Planning",
    "PS": "Personnel Security",
    "RA": "Risk Assessment",
    "CA": "Security Assessment and Authorization",
    "SC": "System and Communications Protection",
    "SI": "System and Information Integrity",
    "PM": "Program Management",
    "SA": "System and Services Acquisition",
    "SP": "Security Policy and Procedures"
}

# Control audit types for routing
AUDIT_TYPES = {
    "system": "System-auditable via CLI commands",
    "policy": "Policy-based, requires document analysis",
    "physical": "Physical controls, requires manual verification",
    "mixed": "Combination of technical and policy controls"
}


# =============================================================================
# NCSA Controls Database - 169 Rwanda NCSA Controls
# =============================================================================

NCSA_CONTROLS: Dict[str, Dict[str, Any]] = {
'''

    # Add controls grouped by family
    for family in sorted(by_family.keys()):
        family_controls = by_family[family]
        content += f'''
    # -------------------------------------------------------------------------
    # {family} ({len(family_controls)} controls)
    # -------------------------------------------------------------------------
'''
        for ctrl in family_controls:
            content += f'''    "{ctrl['control_id']}": {{
        "control_id": "{ctrl['control_id']}",
        "control_name": "{ctrl['control_name'].replace('"', "'")}",
        "control_family": "{ctrl['control_family']}",
        "description": """{ctrl['description'].replace('"', "'")}""",
        "nist_mapping": "{ctrl['nist_mapping']}",
        "compliance_type": "{ctrl['compliance_type']}",
        "audit_type": "{ctrl['audit_type']}",
        "evidence_patterns": {ctrl['evidence_patterns']},
        "compliant_indicators": {ctrl['compliant_indicators']},
        "non_compliant_indicators": {ctrl['non_compliant_indicators']},
        "remediation_guidance": "{ctrl['remediation_guidance']}"
    }},
'''

    content += '''}


# =============================================================================
# Helper Functions
# =============================================================================

def get_control(control_id: str) -> Dict[str, Any]:
    """Get a specific control by ID."""
    return NCSA_CONTROLS.get(control_id, {})


def get_controls_by_family(family: str) -> List[Dict[str, Any]]:
    """Get all controls in a family."""
    return [
        ctrl for ctrl in NCSA_CONTROLS.values()
        if ctrl.get("control_family") == family
    ]


def get_controls_by_audit_type(audit_type: str) -> List[Dict[str, Any]]:
    """Get all controls of a specific audit type (system, policy, physical, mixed)."""
    return [
        ctrl for ctrl in NCSA_CONTROLS.values()
        if ctrl.get("audit_type") == audit_type
    ]


def get_system_auditable_controls() -> List[Dict[str, Any]]:
    """Get all system-auditable controls (can be verified via CLI)."""
    return get_controls_by_audit_type("system")


def get_policy_based_controls() -> List[Dict[str, Any]]:
    """Get all policy-based controls (require document analysis)."""
    return get_controls_by_audit_type("policy")


def get_all_controls() -> Dict[str, Dict[str, Any]]:
    """Get all controls."""
    return NCSA_CONTROLS


def find_relevant_controls(log_message: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Find controls relevant to a log message based on pattern matching.
    Used by MCP+LLM to provide context for semantic analysis.
    """
    log_lower = log_message.lower()
    scored_controls = []

    for ctrl_id, ctrl in NCSA_CONTROLS.items():
        score = 0
        for pattern in ctrl.get("evidence_patterns", []):
            if pattern.lower() in log_lower:
                score += 1

        if score > 0:
            scored_controls.append((score, ctrl))

    # Sort by score descending
    scored_controls.sort(key=lambda x: x[0], reverse=True)

    return [ctrl for _, ctrl in scored_controls[:top_k]]


def get_control_families() -> Dict[str, str]:
    """Get all control families."""
    return CONTROL_FAMILIES


def get_control_statistics() -> Dict[str, Any]:
    """Get statistics about the control database."""
    by_family = {}
    by_audit_type = {"system": 0, "policy": 0, "physical": 0, "mixed": 0}
    by_compliance_type = {"Basic": 0, "Enhanced": 0}

    for ctrl in NCSA_CONTROLS.values():
        family = ctrl.get("control_family", "Unknown")
        by_family[family] = by_family.get(family, 0) + 1

        audit_type = ctrl.get("audit_type", "mixed")
        by_audit_type[audit_type] = by_audit_type.get(audit_type, 0) + 1

        comp_type = ctrl.get("compliance_type", "Basic")
        by_compliance_type[comp_type] = by_compliance_type.get(comp_type, 0) + 1

    return {
        "total_controls": len(NCSA_CONTROLS),
        "by_family": by_family,
        "by_audit_type": by_audit_type,
        "by_compliance_type": by_compliance_type
    }


# Print statistics when run directly
if __name__ == "__main__":
    stats = get_control_statistics()
    print(f"Total NCSA Controls: {stats['total_controls']}")
    print(f"\\nBy Audit Type:")
    for t, count in stats['by_audit_type'].items():
        print(f"  {t}: {count}")
    print(f"\\nBy Compliance Type:")
    for t, count in stats['by_compliance_type'].items():
        print(f"  {t}: {count}")
'''

    return content


def main():
    """Main function to generate expanded controls."""
    print("Loading control taxonomy...")
    taxonomy = load_taxonomy()

    rwanda_controls = taxonomy.get('rwanda', [])
    print(f"Found {len(rwanda_controls)} Rwanda NCSA controls")

    # Generate control entries
    print("Generating control entries...")
    control_entries = []
    for ctrl in rwanda_controls:
        entry = generate_control_entry(ctrl)
        control_entries.append(entry)

    # Generate Python file
    print("Generating Python file...")
    content = generate_python_file(control_entries)

    # Write output
    print(f"Writing to {OUTPUT_FILE}...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        f.write(content)

    # Print summary
    by_type = defaultdict(int)
    for entry in control_entries:
        by_type[entry['audit_type']] += 1

    print("\n" + "=" * 60)
    print("CONTROL EXPANSION COMPLETE")
    print("=" * 60)
    print(f"Total controls generated: {len(control_entries)}")
    print(f"\nBy Audit Type:")
    for t, count in sorted(by_type.items()):
        print(f"  {t}: {count}")
    print(f"\nOutput: {OUTPUT_FILE}")
    print("\nTo use the expanded controls:")
    print("  1. Review the generated file")
    print("  2. Replace ncsa_controls.py with ncsa_controls_expanded.py")
    print("  3. Or import from ncsa_controls_expanded in your code")


if __name__ == "__main__":
    main()
