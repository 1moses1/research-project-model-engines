"""
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

    # -------------------------------------------------------------------------
    # Access Control (26 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-AC-17": {
        "control_id": "RWNCSA-AC-17",
        "control_name": "Access Control - 5-1",
        "control_family": "Access Control",
        "description": """The institution limits system access to authorized users, processes acting on behalf of authorized users, and devices (including other systems).""",
        "nist_mapping": "AC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'access', 'authorization', 'limits', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-18": {
        "control_id": "RWNCSA-AC-18",
        "control_name": "Access Control - 5-2",
        "control_family": "Access Control",
        "description": """The institution limits system access to the types of transactions and functions that authorized users are permitted to execute (role -based access control) . PRACTICE S""",
        "nist_mapping": "AC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'access', 'authorization', 'limits', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-19": {
        "control_id": "RWNCSA-AC-19",
        "control_name": "Access Control - 5-3",
        "control_family": "Access Control",
        "description": """The organization should have a procedure for removal of access rights (termination) for all departing or resigning personnel, both employees and contractors/third parties . This procedure should coordinate management decision with the system administrator/p ersonnel who is responsible for executi ng""",
        "nist_mapping": "AC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'procedure', 'access', 'authorization', 'compliance check', 'organization'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-20": {
        "control_id": "RWNCSA-AC-20",
        "control_name": "Access Control - 5-4",
        "control_family": "Access Control",
        "description": """In case of malicious activity done by the employee, or contractor (third -party employee) , access rights should be immediately revoked according to the incident response procedure.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'activity', 'audit log', 'login', 'logout', 'permission', 'contractor', 'access', 'authorization', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-21": {
        "control_id": "RWNCSA-AC-21",
        "control_name": "Access Control - 5-5",
        "control_family": "Access Control",
        "description": """The institution monitors the flow of NPI following approved authorizations.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'monitors', 'audit log', 'login', 'logout', 'permission', 'institution', 'following', 'access', 'authorization'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-22": {
        "control_id": "RWNCSA-AC-22",
        "control_name": "Access Control - 5-6",
        "control_family": "Access Control",
        "description": """The institution separate s the duties of individuals to reduce the risk of malevolent activity without collusion.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'individuals', 'login', 'logout', 'permission', 'institution', 'separate', 'reduce', 'audit log', 'access'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-23": {
        "control_id": "RWNCSA-AC-23",
        "control_name": "Access Control - 5-7",
        "control_family": "Access Control",
        "description": """The institution uses the principle of least privilege, including specific security functions and privileged accounts.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'principle', 'least', 'login', 'logout', 'permission', 'institution', 'including', 'audit log', 'access'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-24": {
        "control_id": "RWNCSA-AC-24",
        "control_name": "Access Control - 5-8",
        "control_family": "Access Control",
        "description": """The institution uses non-privileged accounts or ro les when accessing non-security functions.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'access', 'authorization', 'compliance check', 'accessing'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-25": {
        "control_id": "RWNCSA-AC-25",
        "control_name": "Access Control - 5-9",
        "control_family": "Access Control",
        "description": """The institution prevent s non-privileged users from executing privileged functions and captures the execution of such functions in audit logs. PRACTICES to 5-7, 5-8, 5-9, 5-17, 9-5, 9-6 The institution should manage privileged access rights as follow s: 1 Privileged access rights should be i dentifi""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'prevent', 'privileged', 'access', 'executing'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-26": {
        "control_id": "RWNCSA-AC-26",
        "control_name": "Access Control - 5-10",
        "control_family": "Access Control",
        "description": """The institution limit s unsuccessful logon attempts.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'access', 'authorization', 'limit', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-27": {
        "control_id": "RWNCSA-AC-27",
        "control_name": "Access Control - 5-11",
        "control_family": "Access Control",
        "description": """The institution provide s privacy and security notices consistent with applicable NPI rules.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'access', 'notices', 'authorization', 'policy updated'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-28": {
        "control_id": "RWNCSA-AC-28",
        "control_name": "Access Control - 5-12",
        "control_family": "Access Control",
        "description": """The institution's computer workstations have session lock enabled to prevent access and viewing of data after a period of inactivity .""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'workstations', 'enabled', 'prevent', 'access', 'authorization'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-29": {
        "control_id": "RWNCSA-AC-29",
        "control_name": "Access Control - 5-13",
        "control_family": "Access Control",
        "description": """The institution terminate s (automatically) a user sess ion after a defined condition.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'terminate', 'login', 'logout', 'permission', 'institution', 'after', 'audit log', 'access', 'authorization'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-30": {
        "control_id": "RWNCSA-AC-30",
        "control_name": "Access Control - 5-14",
        "control_family": "Access Control",
        "description": """The institution monitor s and control s all internal and remote access sessions.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'internal', 'remote', 'access', 'monitor'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-31": {
        "control_id": "RWNCSA-AC-31",
        "control_name": "Access Control - 5-15",
        "control_family": "Access Control",
        "description": """The institution uses cryptographic mechanisms to protect the confidentiality of remote access sessions.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'mechanisms', 'protect', 'confidentiality', 'access'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-32": {
        "control_id": "RWNCSA-AC-32",
        "control_name": "Access Control - 5-16",
        "control_family": "Access Control",
        "description": """The institution route s remote access via m anaged access control points.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'remote', 'anaged', 'access', 'authorization'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-33": {
        "control_id": "RWNCSA-AC-33",
        "control_name": "Access Control - 5-17",
        "control_family": "Access Control",
        "description": """The institution authorize s remote execution of privileged commands and remote access to security -relevant information.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'authorize', 'login', 'logout', 'permission', 'institution', 'remote', 'privileged', 'audit log', 'execution'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-34": {
        "control_id": "RWNCSA-AC-34",
        "control_name": "Access Control - 5-18",
        "control_family": "Access Control",
        "description": """The institution authorize s wireless access prior to allowing such connections.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'authorize', 'login', 'logout', 'permission', 'institution', 'audit log', 'prior', 'wireless', 'access'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-35": {
        "control_id": "RWNCSA-AC-35",
        "control_name": "Access Control - 5-19",
        "control_family": "Access Control",
        "description": """The institution protect s wireless access using authentication and encryption.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'protect', 'using', 'wireless', 'access'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-36": {
        "control_id": "RWNCSA-AC-36",
        "control_name": "Access Control - 5-20",
        "control_family": "Access Control",
        "description": """The institution control s the connection of corporate endpoints or mobile devices.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'connection', 'audit log', 'login', 'logout', 'permission', 'institution', 'corporate', 'access', 'control'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-37": {
        "control_id": "RWNCSA-AC-37",
        "control_name": "Access Control - 5-21",
        "control_family": "Access Control",
        "description": """The institution encrypt s NPI on mobile devices and mobile computing platforms. PRACTICES to 5-20, 5-21 1 Procedures and mechanisms for securing own mobi le devices outside the institution's premises should include at least: • requirements for physical protection of devices, • software installation """,
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'mobile', 'access', 'authorization', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-38": {
        "control_id": "RWNCSA-AC-38",
        "control_name": "Access Control - 5-22",
        "control_family": "Access Control",
        "description": """The institution verifies and control s/limit s connections to and use of external systems. Minimum Cybersecurity Standards for Public Institutions 19 5-23. The institution limits the use of portable storage devices.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'access', 'control', 'authorization', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-39": {
        "control_id": "RWNCSA-AC-39",
        "control_name": "Access Control - 5-24",
        "control_family": "Access Control",
        "description": """The institution control s NPI posted or processed on publicly accessible systems. PRACTICE 4 The insti tution should control the connection of mobile devices or other end -points in the following way s:""",
        "nist_mapping": "AC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'posted', 'login', 'logout', 'permission', 'institution', 'processed', 'audit log', 'publicly', 'access'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-40": {
        "control_id": "RWNCSA-AC-40",
        "control_name": "Access Control - 5-1",
        "control_family": "Access Control",
        "description": """The institution periodically – at le ast once a year - assess es the risk to organizational operations (including mission, functions, image, or reputation), organizational assets, and individuals resulting from the operation of organizational systems and the associated processing, storage, or transm""",
        "nist_mapping": "AC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'periodically', 'audit log', 'login', 'logout', 'permission', 'institution', 'operations', 'access', 'authorization'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-41": {
        "control_id": "RWNCSA-AC-41",
        "control_name": "Access Control - 5-2",
        "control_family": "Access Control",
        "description": """The institution scans for vulnerabilities in organizational ICT systems and applications periodically and when new vulnerabilities affecting those systems and applications are identified.""",
        "nist_mapping": "AC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'vulnerabilities', 'access', 'authorization', 'scans'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },
    "RWNCSA-AC-42": {
        "control_id": "RWNCSA-AC-42",
        "control_name": "Access Control - 5-3",
        "control_family": "Access Control",
        "description": """The institution remediate s vulnerabilities following risk assessments . PRACTICE S to 15-2, 15-3 The institution should monitor and obtain information on technical vulnerabilities of the ICT system s used on an ongoing basis and assess the organization's exposure to them, as well as take appropriat""",
        "nist_mapping": "AC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'audit log', 'login', 'logout', 'permission', 'institution', 'following', 'vulnerabilities', 'access', 'authorization'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Access Control requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Audit and Accountability (26 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-AU-50": {
        "control_id": "RWNCSA-AU-50",
        "control_name": "Audit and Accountability - 7-1",
        "control_family": "Audit and Accountability",
        "description": """The institution create s and retain s system audit logs and records to the extent needed to enable the monitoring, analysis, investigation, and reporting of unlawful or unauthorized system activity.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'institution', 'record', 'trail', 'retain', 'audit', 'create', 'policy updated', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-51": {
        "control_id": "RWNCSA-AU-51",
        "control_name": "Audit and Accountability - 7-2",
        "control_family": "Audit and Accountability",
        "description": """The institution ensures that the actions of individual system users can be uniquely traced to those users, so they can be held accountable for their actions. PRACTICES to 7-1, 7-2 Audit logs and records should meet the following requirements: 1 An event logging system in networks and ICT systems sho""",
        "nist_mapping": "AU-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'ensures', 'institution', 'record', 'trail', 'actions', 'individual', 'audit', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-52": {
        "control_id": "RWNCSA-AU-52",
        "control_name": "Audit and Accountability - 7-3",
        "control_family": "Audit and Accountability",
        "description": """The institution reviews , and updates logged events.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'institution', 'record', 'trail', 'updates', 'audit', 'logged', 'policy updated', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-53": {
        "control_id": "RWNCSA-AU-53",
        "control_name": "Audit and Accountability - 7-4",
        "control_family": "Audit and Accountability",
        "description": """The institution alerts in the event of an audit logging process failure.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'institution', 'record', 'trail', 'audit', 'policy updated', 'alerts', 'compliance check', 'log', 'logging'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-54": {
        "control_id": "RWNCSA-AU-54",
        "control_name": "Audit and Accountability - 7-5",
        "control_family": "Audit and Accountability",
        "description": """The institution correlate s audit record review, analysis, and reporting processes for investigation and response to indications of unlawful, unauthorized, suspicious, or unusual activity. PRACTICES to 7-3, 7-4, 7-5, 7-8 1 SIEM tool s or equivalent service can store, correlate, normalize and analyze""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'institution', 'record', 'trail', 'correlate', 'reporting', 'audit', 'policy updated', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-55": {
        "control_id": "RWNCSA-AU-55",
        "control_name": "Audit and Accountability - 7-6",
        "control_family": "Audit and Accountability",
        "description": """The institution provides audit record reduction and report generation to support on -demand analysis and reporting.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'reduction', 'institution', 'record', 'trail', 'audit', 'policy updated', 'provides', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-56": {
        "control_id": "RWNCSA-AU-56",
        "control_name": "Audit and Accountability - 7-7",
        "control_family": "Audit and Accountability",
        "description": """The institution provides a system capability that compares and synchronizes internal sy stem clocks with an authoritative source (NTP servers) to generate time stamps for audit records. PRACTICE The time source can be the time servers of pool. ntp.org.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'institution', 'record', 'trail', 'capability', 'audit', 'policy updated', 'provides', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-57": {
        "control_id": "RWNCSA-AU-57",
        "control_name": "Audit and Accountability - 7-8",
        "control_family": "Audit and Accountability",
        "description": """The institution protects audit information and audit logging tools from unauthorized access, modification, and deletion.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'protects', 'institution', 'record', 'trail', 'information', 'audit', 'policy updated', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-58": {
        "control_id": "RWNCSA-AU-58",
        "control_name": "Audit and Accountability - 7-9",
        "control_family": "Audit and Accountability",
        "description": """The institution limits management of audit logging functionality to a subset of privileged users. Minimum Cybersecurity Standards for Public Institutions 24 8 Configuration Management""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['management', 'audit log', 'institution', 'record', 'trail', 'audit', 'limits', 'policy updated', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-59": {
        "control_id": "RWNCSA-AU-59",
        "control_name": "Audit and Accountability - 7-1",
        "control_family": "Audit and Accountability",
        "description": """The institution monitors, controls, and protects communications (i.e., information transmitted or received by organizational systems) at the external and key internal boundaries of organizational ICT systems.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['transmitted', 'audit log', 'protects', 'institution', 'record', 'trail', 'information', 'audit', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-60": {
        "control_id": "RWNCSA-AU-60",
        "control_name": "Audit and Accountability - 7-2",
        "control_family": "Audit and Accountability",
        "description": """The institution uses architectural designs, software development techniques, and systems engine ering principles that promote effective information security within organizational ICT systems. PRACTICES to 17-1, 17-2, 17-5, 17-8, 17-9 as well as 5-1, 5-2, 5-22 (Access Control domain) The institution """,
        "nist_mapping": "AU-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'institution', 'record', 'trail', 'development', 'audit', 'architectural', 'policy updated', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-61": {
        "control_id": "RWNCSA-AU-61",
        "control_name": "Audit and Accountability - 7-3",
        "control_family": "Audit and Accountability",
        "description": """The institution separate s user functionality from system management functionality.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['management', 'audit log', 'separate', 'institution', 'record', 'trail', 'audit', 'policy updated', 'functionality', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-62": {
        "control_id": "RWNCSA-AU-62",
        "control_name": "Audit and Accountability - 7-4",
        "control_family": "Audit and Accountability",
        "description": """The institution prevents unauthorized and unintended information transfer via shared system resources.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['unauthorized', 'audit log', 'institution', 'record', 'trail', 'unintended', 'information', 'audit', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-63": {
        "control_id": "RWNCSA-AU-63",
        "control_name": "Audit and Accountability - 7-5",
        "control_family": "Audit and Accountability",
        "description": """The institution implement s subnetworks for publicly accessible system components that are physically or logically separated from internal networks.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'accessible', 'institution', 'record', 'trail', 'subnetworks', 'publicly', 'audit', 'implement', 'policy updated'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-64": {
        "control_id": "RWNCSA-AU-64",
        "control_name": "Audit and Accountability - 7-6",
        "control_family": "Audit and Accountability",
        "description": """The institution denies traffi c by default and allow s traffic by exception (i.e., deny all, permit by exception).""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'institution', 'record', 'trail', 'traffi', 'audit', 'allow', 'policy updated', 'denies', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-65": {
        "control_id": "RWNCSA-AU-65",
        "control_name": "Audit and Accountability - 7-7",
        "control_family": "Audit and Accountability",
        "description": """The institution prevents remote devices from simultaneously establishing non -remote connections with organizational systems and communicating via some other connection to resources in external networks (i.e., split tunne lling).""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'remote', 'institution', 'record', 'trail', 'simultaneously', 'audit', 'policy updated', 'compliance check', 'prevents'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-66": {
        "control_id": "RWNCSA-AU-66",
        "control_name": "Audit and Accountability - 7-8",
        "control_family": "Audit and Accountability",
        "description": """The institution implement s cryptographic mechanisms to prevent unauthorized disclosure of NPI during transmission unless otherwise protected by alternative physical safeguards.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'prevent', 'mechanisms', 'institution', 'record', 'trail', 'audit', 'implement', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-67": {
        "control_id": "RWNCSA-AU-67",
        "control_name": "Audit and Accountability - 7-9",
        "control_family": "Audit and Accountability",
        "description": """The institution termina tes network connections associated with communications sessions at the end of the sessions or after a defined period of inactivity.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'institution', 'record', 'trail', 'termina', 'audit', 'associated', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-68": {
        "control_id": "RWNCSA-AU-68",
        "control_name": "Audit and Accountability - 7-10",
        "control_family": "Audit and Accountability",
        "description": """The institution establish es and manage s cryptographic keys for cryptography used in organizational ICT systems.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['establish', 'audit log', 'institution', 'record', 'trail', 'manage', 'audit', 'policy updated', 'compliance check', 'cryptography'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-69": {
        "control_id": "RWNCSA-AU-69",
        "control_name": "Audit and Accountability - 7-11",
        "control_family": "Audit and Accountability",
        "description": """The institut ion uses strong cryptography when used to protect the confidentiality of NPI. Minimum Cybersecurity Standards for Public Institutions 46 PRACTICE Recommendation for strong cryptography mechanisms - See Appendix 1""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'protect', 'confidentiality', 'record', 'trail', 'audit', 'strong', 'policy updated', 'institut', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-70": {
        "control_id": "RWNCSA-AU-70",
        "control_name": "Audit and Accountability - 7-12",
        "control_family": "Audit and Accountability",
        "description": """The institution prohibit s remote activation of collaborative computing devices (networked whiteboards, cameras, and microphones) and provides the information to the users when the device is enabled.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'remote', 'institution', 'record', 'trail', 'audit', 'prohibit', 'collaborative', 'policy updated', 'activation'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-71": {
        "control_id": "RWNCSA-AU-71",
        "control_name": "Audit and Accountability - 7-13",
        "control_family": "Audit and Accountability",
        "description": """The institution controls and monitors the use of mobile code. PRACTI CE Mobile code technologies include Java, JavaScript, ActiveX, Postscript, PDF, Flash animations, and VBScript. Decisions regarding the use of mobile code in organizational systems should base on the potential for the code to cause""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['monitors', 'audit log', 'institution', 'record', 'trail', 'mobile', 'audit', 'policy updated', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-72": {
        "control_id": "RWNCSA-AU-72",
        "control_name": "Audit and Accountability - 7-14",
        "control_family": "Audit and Accountability",
        "description": """The institution controls and monitors Voice over Internet Protocol (VoIP) technologies.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['voice', 'monitors', 'internet', 'audit log', 'institution', 'record', 'trail', 'audit', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-73": {
        "control_id": "RWNCSA-AU-73",
        "control_name": "Audit and Accountability - 7-15",
        "control_family": "Audit and Accountability",
        "description": """The institution protects the authenticity of communications sessions.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'protects', 'institution', 'record', 'trail', 'authenticity', 'audit', 'policy updated', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-74": {
        "control_id": "RWNCSA-AU-74",
        "control_name": "Audit and Accountability - 7-16",
        "control_family": "Audit and Accountability",
        "description": """The institution protects the confidentiality of NPI at rest.""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'protects', 'confidentiality', 'institution', 'record', 'trail', 'audit', 'policy updated', 'compliance check', 'log'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },
    "RWNCSA-AU-75": {
        "control_id": "RWNCSA-AU-75",
        "control_name": "Audit and Accountability - 7-17",
        "control_family": "Audit and Accountability",
        "description": """The institution protect s its web application against cyber threats inherent in web technologies. PRACTI CE 1 Proper design and implementation of web applications, along with their deployment on secure execution platforms (e.g., PHP, Java, etc.) and application servers (such as Apache, Glassfish, We""",
        "nist_mapping": "AU-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['audit log', 'protect', 'cyber', 'institution', 'record', 'trail', 'against', 'application', 'audit', 'policy updated'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Audit and Accountability requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Awareness and Training (7 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-AT-43": {
        "control_id": "RWNCSA-AT-43",
        "control_name": "Awareness and Training - 6-1",
        "control_family": "Awareness and Training",
        "description": """The institution ensure s that executives, senior management , managers, systems administrators, and users of organizational systems are made aware of the security risks associated with their activities and of the applicable policies, standards, and procedures related to the security of those systems""",
        "nist_mapping": "AT-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['awareness', 'management', 'audit log', 'institution', 'certification', 'ensure', 'competency', 'senior', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Awareness and Training requirements per NCSA standards"
    },
    "RWNCSA-AT-44": {
        "control_id": "RWNCSA-AT-44",
        "control_name": "Awareness and Training - 6-2",
        "control_family": "Awareness and Training",
        "description": """The institution ensure s personnel are trained to carry out their assigned cybersecurity related duties and responsibilities. PRACTI CES""",
        "nist_mapping": "AT-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['awareness', 'audit log', 'institution', 'trained', 'personnel', 'carry', 'certification', 'ensure', 'competency', 'policy updated'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Awareness and Training requirements per NCSA standards"
    },
    "RWNCSA-AT-45": {
        "control_id": "RWNCSA-AT-45",
        "control_name": "Awareness and Training - 6-3",
        "control_family": "Awareness and Training",
        "description": """The institution provide s security awareness training on recognizing and reporting potential indicators of insider threat. PRACTICE 1 The good way to perfo rm security awareness training is to present real examples of attacks (phishing, ransomware infection, etc .) and their impact on the user and h""",
        "nist_mapping": "AT-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['awareness', 'audit log', 'institution', 'certification', 'competency', 'provide', 'policy updated', 'security', 'policy acknowledgment', 'compliance check'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Awareness and Training requirements per NCSA standards"
    },
    "RWNCSA-AT-46": {
        "control_id": "RWNCSA-AT-46",
        "control_name": "Awareness and Training - 6-1",
        "control_family": "Awareness and Training",
        "description": """The institution periodically assess es the security controls in organizational systems to determine if the controls are effective in their application.""",
        "nist_mapping": "AT-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['periodically', 'awareness', 'audit log', 'institution', 'certification', 'competency', 'policy updated', 'security', 'policy acknowledgment', 'compliance check'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Awareness and Training requirements per NCSA standards"
    },
    "RWNCSA-AT-47": {
        "control_id": "RWNCSA-AT-47",
        "control_name": "Awareness and Training - 6-2",
        "control_family": "Awareness and Training",
        "description": """The institution develop s and implement s action plans designed to correct deficiencies and reduce or eliminate vulnerabilities in organizational ICT systems.""",
        "nist_mapping": "AT-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['awareness', 'audit log', 'institution', 'certification', 'action', 'competency', 'implement', 'plans', 'policy updated', 'policy acknowledgment'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Awareness and Training requirements per NCSA standards"
    },
    "RWNCSA-AT-48": {
        "control_id": "RWNCSA-AT-48",
        "control_name": "Awareness and Training - 6-3",
        "control_family": "Awareness and Training",
        "description": """The institution monitor s security controls on a regular basis to ensure the continued effectiveness of the controls.""",
        "nist_mapping": "AT-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['awareness', 'audit log', 'institution', 'certification', 'competency', 'monitor', 'policy updated', 'security', 'policy acknowledgment', 'compliance check'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Awareness and Training requirements per NCSA standards"
    },
    "RWNCSA-AT-49": {
        "control_id": "RWNCSA-AT-49",
        "control_name": "Awareness and Training - 6-4",
        "control_family": "Awareness and Training",
        "description": """The institution develop s, document s, and periodically update s system security plans that describe system boundaries, system environments of operation, how security requirements are implemented, and the relationships with or connections to other ICT systems . PRACTICES 1 1 The best way to perform """,
        "nist_mapping": "AT-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['update', 'periodically', 'awareness', 'audit log', 'institution', 'document', 'certification', 'competency', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Awareness and Training requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Configuration Management (14 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-CM-76": {
        "control_id": "RWNCSA-CM-76",
        "control_name": "Configuration Management - 8-1",
        "control_family": "Configuration Management",
        "description": """The institution establish es and maintain s baseline configurations and inventories of organizational systems (including hardware, software, firmware, and documentation) throughout the respective system development life cycles. The i nventory should contain information about all users and all accoun""",
        "nist_mapping": "CM-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['update', 'establish', 'baseline', 'audit log', 'maintain', 'institution', 'configurations', 'policy updated', 'compliance check', 'change'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-77": {
        "control_id": "RWNCSA-CM-77",
        "control_name": "Configuration Management - 8-2",
        "control_family": "Configuration Management",
        "description": """The institution establish es and enforce s security configuration settings for information technology products employed in organizational systems.""",
        "nist_mapping": "CM-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['update', 'establish', 'baseline', 'audit log', 'institution', 'policy updated', 'enforce', 'security', 'compliance check', 'change'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-78": {
        "control_id": "RWNCSA-CM-78",
        "control_name": "Configuration Management - 8-3",
        "control_family": "Configuration Management",
        "description": """The institution tracks, reviews, app roves or disapproves, and logs configuration changes to the organizational systems.""",
        "nist_mapping": "CM-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['update', 'baseline', 'roves', 'audit log', 'institution', 'changes', 'policy updated', 'compliance check', 'organizational', 'change'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-79": {
        "control_id": "RWNCSA-CM-79",
        "control_name": "Configuration Management - 8-4",
        "control_family": "Configuration Management",
        "description": """The institution analyzes the security impact of changes prior to implementation.""",
        "nist_mapping": "CM-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['update', 'baseline', 'impact', 'audit log', 'analyzes', 'institution', 'changes', 'policy updated', 'security', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-80": {
        "control_id": "RWNCSA-CM-80",
        "control_name": "Configuration Management - 8-5",
        "control_family": "Configuration Management",
        "description": """The institution define s document s, approve s, and enforce s physical and logical access restr ictions associated with changes to organizational systems. In particular : a) development, testing and production environments shall be separated and secured ; b) before a change in the configuration is i""",
        "nist_mapping": "CM-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['update', 'baseline', 'audit log', 'institution', 'define', 'document', 'approve', 'policy updated', 'enforce', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-81": {
        "control_id": "RWNCSA-CM-81",
        "control_name": "Configuration Management - 8-6",
        "control_family": "Configuration Management",
        "description": """The institution uses the principle of least functionality by configuring organizational systems to provide only nece ssary capabilities. PRACTICES to 8-5, 8-6, 8-9 1 Procedures for the supervision of software installation in a production environment should include at least: • rules for updating prod""",
        "nist_mapping": "CM-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['update', 'baseline', 'principle', 'least', 'audit log', 'institution', 'policy updated', 'functionality', 'compliance check', 'change'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-82": {
        "control_id": "RWNCSA-CM-82",
        "control_name": "Configuration Management - 8-7",
        "control_family": "Configuration Management",
        "description": """The institution restric ts, disable s, or p revent s the use of unnecessary or dangerous programs, functions, ports, protocols, and services.""",
        "nist_mapping": "CM-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['update', 'baseline', 'audit log', 'restric', 'institution', 'disable', 'revent', 'policy updated', 'compliance check', 'unnecessary'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-83": {
        "control_id": "RWNCSA-CM-83",
        "control_name": "Configuration Management - 8-8",
        "control_family": "Configuration Management",
        "description": """The institution applies deny -by-exception (blacklisting) policy to prevent the use of unauthorized software or deny -all (permit -by-exception) policy to allow the execution of authorized software.""",
        "nist_mapping": "CM-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['update', 'baseline', 'policy', 'prevent', 'unauthorized', 'audit log', 'institution', 'policy updated', 'compliance check', 'applies'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-84": {
        "control_id": "RWNCSA-CM-84",
        "control_name": "Configuration Management - 8-9",
        "control_family": "Configuration Management",
        "description": """The institution controls and monitors user -installed software. PRACTICE S to 8-9 The institution should have implemented policies and mechanisms for installing software by users, as follows: 1 Prevent users from installing software. Authorizations to install software allowed (specified) by the oper""",
        "nist_mapping": "CM-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['update', 'monitors', 'baseline', 'audit log', 'institution', 'practice', 'policy updated', 'compliance check', 'change', 'patch'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-85": {
        "control_id": "RWNCSA-CM-85",
        "control_name": "Configuration Management - 8-1",
        "control_family": "Configuration Management",
        "description": """The institution identif ies, report s, and correct s system security flaws on time .""",
        "nist_mapping": "CM-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['update', 'report', 'baseline', 'audit log', 'institution', 'identif', 'policy updated', 'compliance check', 'correct', 'change'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-86": {
        "control_id": "RWNCSA-CM-86",
        "control_name": "Configuration Management - 8-2",
        "control_family": "Configuration Management",
        "description": """The institution protects malicious code (malware) within organizational ICT systems and updates malicious code protection mechanisms when new releases are available. Detected malicious software is addressed. PRACTICES Protection against malware should rely on the use of a number of the following tec""",
        "nist_mapping": "CM-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['update', 'baseline', 'audit log', 'protects', 'institution', 'within', 'policy updated', 'compliance check', 'malicious', 'organizational'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-87": {
        "control_id": "RWNCSA-CM-87",
        "control_name": "Configuration Management - 8-3",
        "control_family": "Configuration Management",
        "description": """The institution monitor s system security alerts and advisories and takes action as soon as they are published.""",
        "nist_mapping": "CM-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['update', 'baseline', 'audit log', 'institution', 'monitor', 'policy updated', 'security', 'alerts', 'compliance check', 'change'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-88": {
        "control_id": "RWNCSA-CM-88",
        "control_name": "Configuration Management - 8-4",
        "control_family": "Configuration Management",
        "description": """The institution perform s periodic scans of organizational systems and real -time scans of files from external sources as files are downloaded, opened, or executed.""",
        "nist_mapping": "CM-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['update', 'baseline', 'audit log', 'perform', 'institution', 'scans', 'policy updated', 'compliance check', 'organizational', 'change'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },
    "RWNCSA-CM-89": {
        "control_id": "RWNCSA-CM-89",
        "control_name": "Configuration Management - 8-5",
        "control_family": "Configuration Management",
        "description": """The institution monito rs organizational systems, including inbound and outbound communications traffic, to detect att acks and indicators of potential attacks . Minimum Cybersecurity Standards for Public Institutions 49 19 PII Processing and Transparency""",
        "nist_mapping": "CM-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['update', 'baseline', 'inbound', 'audit log', 'including', 'monito', 'institution', 'policy updated', 'compliance check', 'organizational'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Configuration Management requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Identity Management and Authentication (13 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-IA-90": {
        "control_id": "RWNCSA-IA-90",
        "control_name": "Identity Management and Authentication - 9-1",
        "control_family": "Identity Management and Authentication",
        "description": """The institution identif ies system users, processes acting on behalf of users, and devices.""",
        "nist_mapping": "IA-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'audit log', 'acting', 'institution', 'biometric', 'identif', 'processes', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-91": {
        "control_id": "RWNCSA-IA-91",
        "control_name": "Identity Management and Authentication - 9-2",
        "control_family": "Identity Management and Authentication",
        "description": """The institution authenticate s (or verifies ) the identities of users, processes, or devices as a prerequisite to allowing access to organizational systems.""",
        "nist_mapping": "IA-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'identities', 'audit log', 'institution', 'biometric', 'authenticate', 'policy updated', 'verifies', 'devices'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-92": {
        "control_id": "RWNCSA-IA-92",
        "control_name": "Identity Management and Authentication - 9-3",
        "control_family": "Identity Management and Authentication",
        "description": """The institution enforces a minimum p assword complexity and change of characters when new passwords are created.""",
        "nist_mapping": "IA-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'audit log', 'minimum', 'complexity', 'institution', 'enforces', 'biometric', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-93": {
        "control_id": "RWNCSA-IA-93",
        "control_name": "Identity Management and Authentication - 9-4",
        "control_family": "Identity Management and Authentication",
        "description": """The institution allows temporary password use for system logons with an immediate change to a permanent password.""",
        "nist_mapping": "IA-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'audit log', 'institution', 'biometric', 'policy updated', 'compliance check', 'allows', 'multi-factor', 'system'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-94": {
        "control_id": "RWNCSA-IA-94",
        "control_name": "Identity Management and Authentication - 9-5",
        "control_family": "Identity Management and Authentication",
        "description": """The institution uses multifactor au thentication for local and remote (network ) access to privileged accounts and to non -privileged accounts , acco rding to Table 3. High criticality/sensitivity system Medium/Low criticality/sensitivity system Local access (LAN) Remote access (WAN/Internet) Local """,
        "nist_mapping": "IA-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'thentication', 'audit log', 'remote', 'institution', 'multifactor', 'biometric', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-95": {
        "control_id": "RWNCSA-IA-95",
        "control_name": "Identity Management and Authentication - 9-6",
        "control_family": "Identity Management and Authentication",
        "description": """The institution uses replay -resistant authentication mechanisms for network access to privileged and non -privileged accounts.""",
        "nist_mapping": "IA-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'network', 'audit log', 'mechanisms', 'institution', 'biometric', 'policy updated', 'compliance check', 'multi-factor'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-96": {
        "control_id": "RWNCSA-IA-96",
        "control_name": "Identity Management and Authentication - 9-7",
        "control_family": "Identity Management and Authentication",
        "description": """The institution prevents the reuse of identifiers for a defined period.""",
        "nist_mapping": "IA-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'audit log', 'institution', 'biometric', 'policy updated', 'identifiers', 'prevents', 'compliance check', 'multi-factor'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-97": {
        "control_id": "RWNCSA-IA-97",
        "control_name": "Identity Management and Authentication - 9-8",
        "control_family": "Identity Management and Authentication",
        "description": """The institution disable s identifiers after a limit ed period of inactivity.""",
        "nist_mapping": "IA-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'audit log', 'after', 'institution', 'biometric', 'disable', 'limit', 'identifiers', 'policy updated'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-98": {
        "control_id": "RWNCSA-IA-98",
        "control_name": "Identity Management and Authentication - 9-9",
        "control_family": "Identity Management and Authentication",
        "description": """The institution prohibit s password reuse for a specified number of generations.""",
        "nist_mapping": "IA-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'specified', 'audit log', 'institution', 'biometric', 'prohibit', 'policy updated', 'compliance check', 'multi-factor'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-99": {
        "control_id": "RWNCSA-IA-99",
        "control_name": "Identity Management and Authentication - 9-10",
        "control_family": "Identity Management and Authentication",
        "description": """The institution store s and transm its only cryptographically -protected passwords.""",
        "nist_mapping": "IA-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'store', 'audit log', 'institution', 'biometric', 'cryptographically', 'policy updated', 'compliance check', 'transm'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-100": {
        "control_id": "RWNCSA-IA-100",
        "control_name": "Identity Management and Authentication - 9-11",
        "control_family": "Identity Management and Authentication",
        "description": """The institution obscure s feedback on authentication information. PRACTICE S 1 The i nstitution should have procedure (s) for transferring and storing user authentication data, ensuring the confidentiality of this data . Procedure (s) should take into account the following : Minimum Cybersecurity St""",
        "nist_mapping": "IA-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'audit log', 'institution', 'biometric', 'feedback', 'policy updated', 'compliance check', 'multi-factor', 'practice'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-101": {
        "control_id": "RWNCSA-IA-101",
        "control_name": "Identity Management and Authentication - 9-1",
        "control_family": "Identity Management and Authentication",
        "description": """The institution identif ies and meets the requirements for preserving privacy and protecting PII according to applicable laws and regulations and contrac tual requirements.""",
        "nist_mapping": "IA-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'preserving', 'audit log', 'institution', 'biometric', 'identif', 'requirements', 'policy updated', 'meets'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },
    "RWNCSA-IA-102": {
        "control_id": "RWNCSA-IA-102",
        "control_name": "Identity Management and Authentication - 9-2",
        "control_family": "Identity Management and Authentication",
        "description": """The institution compl ies with the current law relating to the protection of personal data and privacy in Rwanda. Minimum Cybersecurity Standards for Public Institutions 50 20 Contingency Planning""",
        "nist_mapping": "IA-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['authentication', 'MFA', 'current', 'audit log', 'institution', 'protection', 'biometric', 'policy updated', 'compliance check', 'compl'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement Identity Management and Authentication requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Incident Response (6 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-IR-103": {
        "control_id": "RWNCSA-IR-103",
        "control_name": "Incident Response - 10-1",
        "control_family": "Incident Response",
        "description": """The institution has an operational incident -handling capability for organizational systems , including preparation, detection, analysis, c ontainment, recovery, and user response activities.""",
        "nist_mapping": "IR-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['incident', 'audit log', 'eradication', 'institution', 'capability', 'breach', 'policy updated', 'containment', 'compliance check', 'alert'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Incident Response requirements per NCSA standards"
    },
    "RWNCSA-IR-104": {
        "control_id": "RWNCSA-IR-104",
        "control_name": "Incident Response - 10-2",
        "control_family": "Incident Response",
        "description": """The institution must notify the public authority in charge of cybersecurity about every incident . This also pertains to the incident s that can be handled by the institution itself . If the institution cann ot handle the incident and/or the incident concerns critical public safety , the institution""",
        "nist_mapping": "IR-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['incident', 'public', 'audit log', 'eradication', 'institution', 'authority', 'breach', 'compliance check', 'containment', 'charge'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Incident Response requirements per NCSA standards"
    },
    "RWNCSA-IR-105": {
        "control_id": "RWNCSA-IR-105",
        "control_name": "Incident Response - 10-3",
        "control_family": "Incident Response",
        "description": """The institution has d ocumented and implemented procedures for responding to cyber security incidents. The procedures should include at least: • reporting information security incidents, • planning and preparing to respond t o incidents, • monitoring, detecting, analyzing and reporting events and in""",
        "nist_mapping": "IR-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['incident', 'audit log', 'eradication', 'institution', 'responding', 'breach', 'compliance check', 'containment', 'alert', 'ocumented'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Incident Response requirements per NCSA standards"
    },
    "RWNCSA-IR-106": {
        "control_id": "RWNCSA-IR-106",
        "control_name": "Incident Response - 10-4",
        "control_family": "Incident Response",
        "description": """The public institution ensures tha t incident -handling capability is supported at the appropriate level by human, technical, information and financial resources . PRACTICE 1 Competent staff is the most important element of incident response . PRACTICE 2 The number of events requiring constant analy""",
        "nist_mapping": "IR-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['incident', 'public', 'audit log', 'ensures', 'eradication', 'institution', 'capability', 'breach', 'compliance check', 'containment'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Incident Response requirements per NCSA standards"
    },
    "RWNCSA-IR-107": {
        "control_id": "RWNCSA-IR-107",
        "control_name": "Incident Response - 10-6",
        "control_family": "Incident Response",
        "description": """The institution tests the institution al incident response capability.""",
        "nist_mapping": "IR-1",
        "compliance_type": "Enhanced",
        "audit_type": "mixed",
        "evidence_patterns": ['incident', 'audit log', 'eradication', 'institution', 'breach', 'compliance check', 'containment', 'alert', 'tests', 'policy updated'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Incident Response requirements per NCSA standards"
    },
    "RWNCSA-IR-108": {
        "control_id": "RWNCSA-IR-108",
        "control_name": "Incident Response - 10-7",
        "control_family": "Incident Response",
        "description": """The institution collects and analyzes information relating to cyber security threats to produce cyber threat intelligence. PRACTICE 3 The best method to produce CTI is to use existing feeds, for example , from own CTI team or other teams, services and sources in the following way s: a) Receive syste""",
        "nist_mapping": "IR-1",
        "compliance_type": "Enhanced",
        "audit_type": "mixed",
        "evidence_patterns": ['incident', 'audit log', 'analyzes', 'eradication', 'institution', 'information', 'breach', 'compliance check', 'containment', 'alert'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Incident Response requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Maintenance (7 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-MA-109": {
        "control_id": "RWNCSA-MA-109",
        "control_name": "Maintenance - 11-1",
        "control_family": "Maintenance",
        "description": """The institution should perform maintenance on organizational ICT systems.""",
        "nist_mapping": "MA-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['update', 'audit log', 'patch', 'upgrade', 'institution', 'service', 'repair', 'policy updated', 'compliance check', 'organizational'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Maintenance requirements per NCSA standards"
    },
    "RWNCSA-MA-110": {
        "control_id": "RWNCSA-MA-110",
        "control_name": "Maintenance - 11-2",
        "control_family": "Maintenance",
        "description": """The institution provide s controls on the tools, techniques, mechanisms and personnel used to conduct system maintenance.""",
        "nist_mapping": "MA-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['update', 'audit log', 'patch', 'upgrade', 'institution', 'mechanisms', 'personnel', 'service', 'repair', 'provide'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Maintenance requirements per NCSA standards"
    },
    "RWNCSA-MA-111": {
        "control_id": "RWNCSA-MA-111",
        "control_name": "Maintenance - 11-3",
        "control_family": "Maintenance",
        "description": """The institution ensures equipment removed for off -site maintenance is sanitized of any NPI.""",
        "nist_mapping": "MA-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['update', 'audit log', 'patch', 'upgrade', 'institution', 'ensures', 'equipment', 'service', 'repair', 'removed'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Maintenance requirements per NCSA standards"
    },
    "RWNCSA-MA-112": {
        "control_id": "RWNCSA-MA-112",
        "control_name": "Maintenance - 11-4",
        "control_family": "Maintenance",
        "description": """The institution checks media containing diagnostic and test programs for malicious code before the media are used in organizational systems.""",
        "nist_mapping": "MA-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['update', 'checks', 'diagnostic', 'audit log', 'patch', 'upgrade', 'institution', 'media', 'service', 'repair'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Maintenance requirements per NCSA standards"
    },
    "RWNCSA-MA-113": {
        "control_id": "RWNCSA-MA-113",
        "control_name": "Maintenance - 11-5",
        "control_family": "Maintenance",
        "description": """The institution require s multifactor authentication , according to Table 3, to establish nonlocal maintenance sessions via external network connections and terminate such conne ctions when nonlocal maintenance is complete.""",
        "nist_mapping": "MA-1",
        "compliance_type": "Enhanced",
        "audit_type": "mixed",
        "evidence_patterns": ['update', 'authentication', 'audit log', 'patch', 'upgrade', 'institution', 'multifactor', 'service', 'repair', 'require'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Maintenance requirements per NCSA standards"
    },
    "RWNCSA-MA-114": {
        "control_id": "RWNCSA-MA-114",
        "control_name": "Maintenance - 11-6",
        "control_family": "Maintenance",
        "description": """The ins titution must organize and supervise the maintenance activities of maintenance personnel , which are usually performed without required access authorization , except those who are pre -authorized to perform .""",
        "nist_mapping": "MA-1",
        "compliance_type": "Enhanced",
        "audit_type": "mixed",
        "evidence_patterns": ['update', 'audit log', 'patch', 'upgrade', 'organize', 'service', 'repair', 'policy updated', 'compliance check', 'titution'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Maintenance requirements per NCSA standards"
    },
    "RWNCSA-MA-115": {
        "control_id": "RWNCSA-MA-115",
        "control_name": "Maintenance - 11-7",
        "control_family": "Maintenance",
        "description": """The institution applies the rules of secure design, development and modification of software and systems . PRACTICE S Rules of secure design, development and modification of software and systems include: a) Information security should be integrated into project management; b) Rules for the secure de""",
        "nist_mapping": "MA-1",
        "compliance_type": "Enhanced",
        "audit_type": "mixed",
        "evidence_patterns": ['update', 'rules', 'audit log', 'patch', 'upgrade', 'institution', 'service', 'development', 'repair', 'policy updated'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Maintenance requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Media Protection (9 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-MP-116": {
        "control_id": "RWNCSA-MP-116",
        "control_name": "Media Protection - 12-1",
        "control_family": "Media Protection",
        "description": """The institution protect s (i.e., physically control and securely store) system media containing paper and digital NPI . PRACTICES An important aspect of media protection after termination of employment is the return of all resources (system medi a containing NPI) that have been transferred to the em""",
        "nist_mapping": "MP-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['audit log', 'protect', 'media', 'institution', 'sanitization', 'transport', 'securely', 'storage', 'control', 'compliance check'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Media Protection requirements per NCSA standards"
    },
    "RWNCSA-MP-117": {
        "control_id": "RWNCSA-MP-117",
        "control_name": "Media Protection - 12-2",
        "control_family": "Media Protection",
        "description": """The institution limit s access to NPI on system media to authorized users.""",
        "nist_mapping": "MP-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['audit log', 'media', 'institution', 'sanitization', 'transport', 'storage', 'access', 'limit', 'compliance check', 'disposal'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Media Protection requirements per NCSA standards"
    },
    "RWNCSA-MP-118": {
        "control_id": "RWNCSA-MP-118",
        "control_name": "Media Protection - 12-3",
        "control_family": "Media Protection",
        "description": """The institution sanitize s or destroy s system media containing NPI before disposal or r elease for reuse. PRACTICES The institution should have procedures for dealing with data carriers and ICT equipment withdrawn from current use, as follow s: 1 Implement the categorization of data carriers (e.g .""",
        "nist_mapping": "MP-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['destroy', 'audit log', 'media', 'institution', 'sanitization', 'transport', 'storage', 'compliance check', 'disposal', 'system'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Media Protection requirements per NCSA standards"
    },
    "RWNCSA-MP-119": {
        "control_id": "RWNCSA-MP-119",
        "control_name": "Media Protection - 12-4",
        "control_family": "Media Protection",
        "description": """The p ublic institution ensures identification of records and their retention period, consi dering legislation or regulations and community or societal expectations, if applicable. Legislation that should be considered is, e.g., Law Nº 058/2021 of 13/10/2021 relating to the protection of personal da""",
        "nist_mapping": "MP-1",
        "compliance_type": "Basic",
        "audit_type": "mixed",
        "evidence_patterns": ['audit log', 'media', 'ensures', 'ublic', 'sanitization', 'transport', 'institution', 'storage', 'records', 'compliance check'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Media Protection requirements per NCSA standards"
    },
    "RWNCSA-MP-120": {
        "control_id": "RWNCSA-MP-120",
        "control_name": "Media Protection - 12-5",
        "control_family": "Media Protection",
        "description": """The institution mark s media with necessary NPI markings and distribution limitations. Minimum Cybersecurity Standards for Public Institutions 32 12-6. The institution control s access to media containing NPI and maintains accountability for media during transport outside of controlled areas. PRACTI""",
        "nist_mapping": "MP-1",
        "compliance_type": "Enhanced",
        "audit_type": "mixed",
        "evidence_patterns": ['audit log', 'media', 'institution', 'sanitization', 'transport', 'distribution', 'storage', 'compliance check', 'disposal', 'markings'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Media Protection requirements per NCSA standards"
    },
    "RWNCSA-MP-121": {
        "control_id": "RWNCSA-MP-121",
        "control_name": "Media Protection - 12-7",
        "control_family": "Media Protection",
        "description": """The institution implement s cryptographic mechanisms to protect the confidentiality of NPI stored on digital media during transport unless otherwise protected by alternati ve physical safeguards. PRACTI CE Recommendation for strong cryptography mechanisms - See Appendix 1.""",
        "nist_mapping": "MP-1",
        "compliance_type": "Enhanced",
        "audit_type": "mixed",
        "evidence_patterns": ['audit log', 'protect', 'media', 'mechanisms', 'institution', 'sanitization', 'transport', 'storage', 'implement', 'compliance check'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Media Protection requirements per NCSA standards"
    },
    "RWNCSA-MP-122": {
        "control_id": "RWNCSA-MP-122",
        "control_name": "Media Protection - 12-8",
        "control_family": "Media Protection",
        "description": """The institution control s the use of removable media on system components. PRACTICE Control the use of removable media on system components by: a. Establishin g a policy that outlines the acceptable use of removable media, including types of media, devices, and circumstances under which their use is""",
        "nist_mapping": "MP-1",
        "compliance_type": "Enhanced",
        "audit_type": "mixed",
        "evidence_patterns": ['audit log', 'media', 'institution', 'sanitization', 'transport', 'storage', 'control', 'compliance check', 'removable', 'disposal'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Media Protection requirements per NCSA standards"
    },
    "RWNCSA-MP-123": {
        "control_id": "RWNCSA-MP-123",
        "control_name": "Media Protection - 12-9",
        "control_family": "Media Protection",
        "description": """The institution prohibit s the use of non-corporate portable storage devices.""",
        "nist_mapping": "MP-1",
        "compliance_type": "Enhanced",
        "audit_type": "mixed",
        "evidence_patterns": ['audit log', 'media', 'institution', 'sanitization', 'transport', 'storage', 'prohibit', 'compliance check', 'disposal', 'portable'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Media Protection requirements per NCSA standards"
    },
    "RWNCSA-MP-124": {
        "control_id": "RWNCSA-MP-124",
        "control_name": "Media Protection - 12-10",
        "control_family": "Media Protection",
        "description": """The institution protects the confidentiality of backup NPI at storage locations. Minimum Cybersecurity Standards for Public Institutions 33 13 Personnel Security Note 1: It is important to ensur e personnel security is an integral part of the risk management process in the public institution. It sho""",
        "nist_mapping": "MP-1",
        "compliance_type": "Enhanced",
        "audit_type": "mixed",
        "evidence_patterns": ['audit log', 'media', 'protects', 'institution', 'sanitization', 'transport', 'confidentiality', 'storage', 'compliance check', 'backup'],
        "compliant_indicators": ['Technical controls configured', 'Policy documentation complete', 'Regular testing performed', 'Audit evidence available'],
        "non_compliant_indicators": ['Technical gaps identified', 'Policy documentation incomplete', 'No testing evidence', 'Audit findings unresolved'],
        "remediation_guidance": "Review and implement Media Protection requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Personnel Security (11 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-XX-125": {
        "control_id": "RWNCSA-XX-125",
        "control_name": "Personnel Security - 13-1",
        "control_family": "Personnel Security",
        "description": """The p ublic institution identifies (inventories) its own human resources. For each official position with access to NPI, the scope of duties and the analyzed security requirements are defined (the level of access to zones, rooms, docum ents, systems etc.) PRACTICE 1 The analysis of security requirem""",
        "nist_mapping": "PS-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['official', 'audit log', 'screening', 'ublic', 'institution', 'personnel', 'termination', 'human', 'compliance check', 'transfer'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },
    "RWNCSA-XX-126": {
        "control_id": "RWNCSA-XX-126",
        "control_name": "Personnel Security - 13-2",
        "control_family": "Personnel Security",
        "description": """The p ublic institution verifie s the identity of employees and job candidates based on the submitted original documents (containing names, surname s, date of birth, address and photo) . PRACTICE 1 The identity of a person consists of attributes given after birth (name, surname, date and place of bi""",
        "nist_mapping": "PS-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['audit log', 'screening', 'ublic', 'institution', 'personnel', 'termination', 'policy updated', 'transfer', 'access revocation', 'compliance check'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },
    "RWNCSA-XX-127": {
        "control_id": "RWNCSA-XX-127",
        "control_name": "Personnel Security - 13-3",
        "control_family": "Personnel Security",
        "description": """The institution screens individuals prior to hiring them as well as taking up a role related to access to sensiti ve information. In particular, it does so before authorizing access to ICT systems of organizations containing NPI.""",
        "nist_mapping": "PS-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['individuals', 'audit log', 'screening', 'institution', 'screens', 'personnel', 'termination', 'prior', 'compliance check', 'transfer'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },
    "RWNCSA-XX-128": {
        "control_id": "RWNCSA-XX-128",
        "control_name": "Personnel Security - 13-4",
        "control_family": "Personnel Security",
        "description": """The institution ensures that organizational systems containing NPI are protected during and after personnel actions such as terminations and transfers. Minimum Cybersecurity Standards for Public Institutions 34 13-5. The institution provides basic training on information security upon commencement o""",
        "nist_mapping": "PS-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['audit log', 'screening', 'ensures', 'institution', 'personnel', 'termination', 'containing', 'transfer', 'access revocation', 'policy updated'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },
    "RWNCSA-XX-129": {
        "control_id": "RWNCSA-XX-129",
        "control_name": "Personnel Security - 13-6",
        "control_family": "Personnel Security",
        "description": """The institution ensures the identification of people having access to the facilities by introducing mandatory identifiers (badges).""",
        "nist_mapping": "PS-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['audit log', 'screening', 'ensures', 'institution', 'personnel', 'termination', 'compliance check', 'transfer', 'access revocation', 'background check'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },
    "RWNCSA-XX-130": {
        "control_id": "RWNCSA-XX-130",
        "control_name": "Personnel Security - 13-7",
        "control_family": "Personnel Security",
        "description": """The institution ensures that security personnel are immediately provided with information on the denial of access for the departing employee .""",
        "nist_mapping": "PS-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['audit log', 'screening', 'ensures', 'institution', 'personnel', 'termination', 'immediately', 'compliance check', 'transfer', 'access revocation'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },
    "RWNCSA-XX-131": {
        "control_id": "RWNCSA-XX-131",
        "control_name": "Personnel Security - 13-8",
        "control_family": "Personnel Security",
        "description": """The institution ensures periodic verification of physic al access and authorizations for employees and external subcontractors related to position and work performed. PRACTICE 1 At least the authorizations to: a) access to the facility, b) access to particular zones - if de termined , c) access to I""",
        "nist_mapping": "PS-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['audit log', 'screening', 'ensures', 'institution', 'verification', 'personnel', 'termination', 'physic', 'compliance check', 'transfer'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },
    "RWNCSA-XX-132": {
        "control_id": "RWNCSA-XX-132",
        "control_name": "Personnel Security - 13-9",
        "control_family": "Personnel Security",
        "description": """The public institution provides all employees with awareness training in social engineering threats. Completion of the training is documented by: the training program, its duration, the instructor and the trainee's signature . PRACTICE The training should inform employees of the characteristics of s""",
        "nist_mapping": "PS-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['public', 'awareness', 'audit log', 'screening', 'institution', 'personnel', 'termination', 'compliance check', 'transfer', 'access revocation'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },
    "RWNCSA-XX-133": {
        "control_id": "RWNCSA-XX-133",
        "control_name": "Personnel Security - 13-10",
        "control_family": "Personnel Security",
        "description": """The public institution has procedures f or verifying the qualifications of candidates and employees . PRACTICE Verification of information contained in the presented documents includes: a) education, b) professional experience, c) predispositions .""",
        "nist_mapping": "PS-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['public', 'audit log', 'screening', 'institution', 'personnel', 'termination', 'verifying', 'compliance check', 'transfer', 'access revocation'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },
    "RWNCSA-XX-134": {
        "control_id": "RWNCSA-XX-134",
        "control_name": "Personnel Security - 13-11",
        "control_family": "Personnel Security",
        "description": """The institution ensures that people with no criminal record are employed in key positions. This is done by a job candidate submitting a Criminal Record Certificate issued by the National Public Prosecution Authority (NPPA) . Minimum Cybersecurity Standards for Public Institutions 35 13.2 Enhanced Se""",
        "nist_mapping": "PS-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['criminal', 'audit log', 'screening', 'ensures', 'institution', 'record', 'personnel', 'termination', 'compliance check', 'transfer'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },
    "RWNCSA-XX-135": {
        "control_id": "RWNCSA-XX-135",
        "control_name": "Personnel Security - 13-12",
        "control_family": "Personnel Security",
        "description": """Public institutions follow a public procurement law that determines what the external parties have to present. For example: a) The Ministerial Order No 002/20/10/TC of 19/05/2020 establishing regulations on public procurement ; b) Guidelines for GoR [GOV] that give out some guidelines on how to proc""",
        "nist_mapping": "PS-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['public', 'audit log', 'screening', 'personnel', 'termination', 'follow', 'institutions', 'compliance check', 'transfer', 'access revocation'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Personnel Security requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Physical and Environmental Protection (10 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-PE-136": {
        "control_id": "RWNCSA-PE-136",
        "control_name": "Physical and Environmental Protection - 14-1",
        "control_family": "Physical and Environmental Protection",
        "description": """The institution divides the area it manages into security zones based on risk assessment to ensure physical security. PRACTICE 1 Each of the zones must be designed in such a way as to eliminate the anticipated attack scenarios and where it is impossible to slow down the actions of a poten tial attac""",
        "nist_mapping": "PE-1",
        "compliance_type": "Basic",
        "audit_type": "physical",
        "evidence_patterns": ['zones', 'CCTV', 'audit log', 'camera', 'institution', 'visitor', 'physical access', 'compliance check', 'security', 'divides'],
        "compliant_indicators": ['Physical controls in place', 'Access logs maintained', 'Environmental controls active', 'Regular inspections conducted'],
        "non_compliant_indicators": ['Physical controls missing', 'No access logging', 'Environmental controls failing', 'No inspection records'],
        "remediation_guidance": "Review and implement Physical and Environmental Protection requirements per NCSA standards"
    },
    "RWNCSA-PE-137": {
        "control_id": "RWNCSA-PE-137",
        "control_name": "Physical and Environmental Protection - 14-2",
        "control_family": "Physical and Environmental Protection",
        "description": """The institution provides, limited by the scope of official duties, access to particular security zones. The principle of necessary access applies (need to have).""",
        "nist_mapping": "PE-1",
        "compliance_type": "Basic",
        "audit_type": "physical",
        "evidence_patterns": ['scope', 'official', 'audit log', 'CCTV', 'camera', 'institution', 'visitor', 'access', 'physical access', 'limited'],
        "compliant_indicators": ['Physical controls in place', 'Access logs maintained', 'Environmental controls active', 'Regular inspections conducted'],
        "non_compliant_indicators": ['Physical controls missing', 'No access logging', 'Environmental controls failing', 'No inspection records'],
        "remediation_guidance": "Review and implement Physical and Environmental Protection requirements per NCSA standards"
    },
    "RWNCSA-PE-138": {
        "control_id": "RWNCSA-PE-138",
        "control_name": "Physical and Environmental Protection - 14-3",
        "control_family": "Physical and Environmental Protection",
        "description": """The institution limits authorised individuals' physical access to organizational systems, equipment, and the respective operating environment s. PRACTICE 1 The requirement applies to employees, contractors, suppliers, subcontractors and visitors . PRACTICE 2 Rules f or entering and leaving t he secu""",
        "nist_mapping": "PE-1",
        "compliance_type": "Basic",
        "audit_type": "physical",
        "evidence_patterns": ['audit log', 'CCTV', 'physical', 'camera', 'institution', 'visitor', 'access', 'physical access', 'limits', 'compliance check'],
        "compliant_indicators": ['Physical controls in place', 'Access logs maintained', 'Environmental controls active', 'Regular inspections conducted'],
        "non_compliant_indicators": ['Physical controls missing', 'No access logging', 'Environmental controls failing', 'No inspection records'],
        "remediation_guidance": "Review and implement Physical and Environmental Protection requirements per NCSA standards"
    },
    "RWNCSA-PE-139": {
        "control_id": "RWNCSA-PE-139",
        "control_name": "Physical and Environmental Protection - 14-4",
        "control_family": "Physical and Environmental Protection",
        "description": """The institution provides employees with basic physical security training. PRACTICE""",
        "nist_mapping": "PE-1",
        "compliance_type": "Basic",
        "audit_type": "physical",
        "evidence_patterns": ['audit log', 'CCTV', 'physical', 'camera', 'institution', 'visitor', 'physical access', 'basic', 'provides', 'compliance check'],
        "compliant_indicators": ['Physical controls in place', 'Access logs maintained', 'Environmental controls active', 'Regular inspections conducted'],
        "non_compliant_indicators": ['Physical controls missing', 'No access logging', 'Environmental controls failing', 'No inspection records'],
        "remediation_guidance": "Review and implement Physical and Environmental Protection requirements per NCSA standards"
    },
    "RWNCSA-PE-140": {
        "control_id": "RWNCSA-PE-140",
        "control_name": "Physical and Environmental Protection - 14-5",
        "control_family": "Physical and Environmental Protection",
        "description": """The institution protects and monitors the physical facility and support s infrastructure for organizational systems.""",
        "nist_mapping": "PE-1",
        "compliance_type": "Enhanced",
        "audit_type": "physical",
        "evidence_patterns": ['monitors', 'audit log', 'CCTV', 'protects', 'physical', 'camera', 'institution', 'visitor', 'physical access', 'compliance check'],
        "compliant_indicators": ['Physical controls in place', 'Access logs maintained', 'Environmental controls active', 'Regular inspections conducted'],
        "non_compliant_indicators": ['Physical controls missing', 'No access logging', 'Environmental controls failing', 'No inspection records'],
        "remediation_guidance": "Review and implement Physical and Environmental Protection requirements per NCSA standards"
    },
    "RWNCSA-PE-141": {
        "control_id": "RWNCSA-PE-141",
        "control_name": "Physical and Environmental Protection - 14-6",
        "control_family": "Physical and Environmental Protection",
        "description": """The institution prevents or reduces the consequences of events originating from physical and environmental threats such as fire, flood, earthquake, explosion, civil unrest, toxic waste, environmental emissions and other forms of natural disaster or disaster caused by human beings. PRACTICE Physical """,
        "nist_mapping": "PE-1",
        "compliance_type": "Enhanced",
        "audit_type": "physical",
        "evidence_patterns": ['events', 'audit log', 'CCTV', 'camera', 'institution', 'visitor', 'physical access', 'compliance check', 'prevents', 'consequences'],
        "compliant_indicators": ['Physical controls in place', 'Access logs maintained', 'Environmental controls active', 'Regular inspections conducted'],
        "non_compliant_indicators": ['Physical controls missing', 'No access logging', 'Environmental controls failing', 'No inspection records'],
        "remediation_guidance": "Review and implement Physical and Environmental Protection requirements per NCSA standards"
    },
    "RWNCSA-PE-142": {
        "control_id": "RWNCSA-PE-142",
        "control_name": "Physical and Environmental Protection - 14-7",
        "control_family": "Physical and Environmental Protection",
        "description": """The institution maintain s audit logs of physical access. Audit l ogs should be stored for a minimal 12 months period.""",
        "nist_mapping": "PE-1",
        "compliance_type": "Enhanced",
        "audit_type": "physical",
        "evidence_patterns": ['audit log', 'CCTV', 'physical', 'maintain', 'camera', 'institution', 'visitor', 'audit', 'physical access', 'compliance check'],
        "compliant_indicators": ['Physical controls in place', 'Access logs maintained', 'Environmental controls active', 'Regular inspections conducted'],
        "non_compliant_indicators": ['Physical controls missing', 'No access logging', 'Environmental controls failing', 'No inspection records'],
        "remediation_guidance": "Review and implement Physical and Environmental Protection requirements per NCSA standards"
    },
    "RWNCSA-PE-143": {
        "control_id": "RWNCSA-PE-143",
        "control_name": "Physical and Environmental Protection - 14-8",
        "control_family": "Physical and Environmental Protection",
        "description": """The institution control s and manage s physical access devices (badges/keys/PIN codes/cards) . PRACTICE 1 Physical access devi ces should be registered and individualized, e.g ., by labe lling or numbering . PRACTICE 2 The rules for storing and issuing keys to protec ted rooms and zones, the periodi""",
        "nist_mapping": "PE-1",
        "compliance_type": "Enhanced",
        "audit_type": "physical",
        "evidence_patterns": ['audit log', 'CCTV', 'physical', 'camera', 'institution', 'manage', 'visitor', 'control', 'physical access', 'access'],
        "compliant_indicators": ['Physical controls in place', 'Access logs maintained', 'Environmental controls active', 'Regular inspections conducted'],
        "non_compliant_indicators": ['Physical controls missing', 'No access logging', 'Environmental controls failing', 'No inspection records'],
        "remediation_guidance": "Review and implement Physical and Environmental Protection requirements per NCSA standards"
    },
    "RWNCSA-PE-144": {
        "control_id": "RWNCSA-PE-144",
        "control_name": "Physical and Environmental Protection - 14-9",
        "control_family": "Physical and Environmental Protection",
        "description": """The institution enforce s safeguarding measures for NPI processing at alternate work sites (e.g., Disaster recovery site ). PRACTICE 1 Physical security training should include: a) Understanding the disaster type; b) Emergency preparedness includes the location of emergency exits, how to carry out e""",
        "nist_mapping": "PE-1",
        "compliance_type": "Enhanced",
        "audit_type": "physical",
        "evidence_patterns": ['audit log', 'CCTV', 'camera', 'institution', 'measures', 'visitor', 'physical access', 'compliance check', 'enforce', 'safeguarding'],
        "compliant_indicators": ['Physical controls in place', 'Access logs maintained', 'Environmental controls active', 'Regular inspections conducted'],
        "non_compliant_indicators": ['Physical controls missing', 'No access logging', 'Environmental controls failing', 'No inspection records'],
        "remediation_guidance": "Review and implement Physical and Environmental Protection requirements per NCSA standards"
    },
    "RWNCSA-PE-145": {
        "control_id": "RWNCSA-PE-145",
        "control_name": "Physical and Environmental Protection - 14-10",
        "control_family": "Physical and Environmental Protection",
        "description": """The institution assists and monitors visitors ’ activit ies. PRACTICE Visitors should access the facility under the supervision of an authorized employee of the institution from the moment of entering to the moment of leaving the facility. Minimum Cybersecurity Standards for Public Institutions 39 1""",
        "nist_mapping": "PE-1",
        "compliance_type": "Enhanced",
        "audit_type": "physical",
        "evidence_patterns": ['monitors', 'audit log', 'CCTV', 'assists', 'camera', 'institution', 'visitor', 'physical access', 'compliance check', 'visitors'],
        "compliant_indicators": ['Physical controls in place', 'Access logs maintained', 'Environmental controls active', 'Regular inspections conducted'],
        "non_compliant_indicators": ['Physical controls missing', 'No access logging', 'Environmental controls failing', 'No inspection records'],
        "remediation_guidance": "Review and implement Physical and Environmental Protection requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Risk Assessment (3 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-RA-146": {
        "control_id": "RWNCSA-RA-146",
        "control_name": "Risk Assessment - 15-1",
        "control_family": "Risk Assessment",
        "description": """The institution periodically – at le ast once a year - assess es the risk to organizational operations (including mission, functions, image, or reputation), organizational assets, and individuals resulting from the operation of organizational systems and the associated processing, storage, or transm""",
        "nist_mapping": "RA-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['periodically', 'impact', 'audit log', 'risk', 'assessment', 'institution', 'operations', 'policy updated', 'compliance check', 'threat'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Risk Assessment requirements per NCSA standards"
    },
    "RWNCSA-RA-147": {
        "control_id": "RWNCSA-RA-147",
        "control_name": "Risk Assessment - 15-2",
        "control_family": "Risk Assessment",
        "description": """The institution scans for vulnerabilities in organizational ICT systems and applications periodically and when new vulnerabilities affecting those systems and applications are identified.""",
        "nist_mapping": "RA-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['impact', 'audit log', 'risk', 'assessment', 'institution', 'vulnerabilities', 'scans', 'policy updated', 'compliance check', 'threat'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Risk Assessment requirements per NCSA standards"
    },
    "RWNCSA-RA-148": {
        "control_id": "RWNCSA-RA-148",
        "control_name": "Risk Assessment - 15-3",
        "control_family": "Risk Assessment",
        "description": """The institution remediate s vulnerabilities following risk assessments . PRACTICE S to 15-2, 15-3 The institution should monitor and obtain information on technical vulnerabilities of the ICT system s used on an ongoing basis and assess the organization's exposure to them, as well as take appropriat""",
        "nist_mapping": "RA-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['impact', 'audit log', 'risk', 'assessment', 'institution', 'following', 'vulnerabilities', 'compliance check', 'assessments', 'threat'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Risk Assessment requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Security Assessment (4 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-XX-149": {
        "control_id": "RWNCSA-XX-149",
        "control_name": "Security Assessment - 16-1",
        "control_family": "Security Assessment",
        "description": """The institution periodically assess es the security controls in organizational systems to determine if the controls are effective in their application.""",
        "nist_mapping": "CA-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['periodically', 'audit log', 'vulnerability scan', 'assessment', 'institution', 'audit', 'compliance check', 'security', 'penetration test', 'assess'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Assessment requirements per NCSA standards"
    },
    "RWNCSA-XX-150": {
        "control_id": "RWNCSA-XX-150",
        "control_name": "Security Assessment - 16-2",
        "control_family": "Security Assessment",
        "description": """The institution develop s and implement s action plans designed to correct deficiencies and reduce or eliminate vulnerabilities in organizational ICT systems.""",
        "nist_mapping": "CA-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['audit log', 'vulnerability scan', 'assessment', 'institution', 'audit', 'implement', 'compliance check', 'plans', 'policy updated', 'penetration test'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Assessment requirements per NCSA standards"
    },
    "RWNCSA-XX-151": {
        "control_id": "RWNCSA-XX-151",
        "control_name": "Security Assessment - 16-3",
        "control_family": "Security Assessment",
        "description": """The institution monitor s security controls on a regular basis to ensure the continued effectiveness of the controls.""",
        "nist_mapping": "CA-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['audit log', 'vulnerability scan', 'assessment', 'institution', 'audit', 'monitor', 'compliance check', 'security', 'penetration test', 'control assessment'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Assessment requirements per NCSA standards"
    },
    "RWNCSA-XX-152": {
        "control_id": "RWNCSA-XX-152",
        "control_name": "Security Assessment - 16-4",
        "control_family": "Security Assessment",
        "description": """The institution develop s, document s, and periodically update s system security plans that describe system boundaries, system environments of operation, how security requirements are implemented, and the relationships with or connections to other ICT systems . PRACTICES 1 1 The best way to perform """,
        "nist_mapping": "CA-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['update', 'periodically', 'audit log', 'vulnerability scan', 'assessment', 'institution', 'document', 'audit', 'compliance check', 'penetration test'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Assessment requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # Security Policy and Procedures (16 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-SP-1": {
        "control_id": "RWNCSA-SP-1",
        "control_name": "Security Policy and Procedures - 4-1",
        "control_family": "Security Policy and Procedures",
        "description": """The public institution has, as a minimum , a documented Information Security Policy (ISP) based on information security requirements defined in this document and applicable legal, statutory and regulatory requirements.""",
        "nist_mapping": "PL-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['public', 'policy', 'minimum', 'audit log', 'governance', 'procedure', 'institution', 'information', 'guideline', 'policy updated'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-2": {
        "control_id": "RWNCSA-SP-2",
        "control_name": "Security Policy and Procedures - 4-2",
        "control_family": "Security Policy and Procedures",
        "description": """Information security and topic -specific policies shall be defined, approved by management, published, communicate d to and acknowledged by relevant personnel and interested parties, and reviewed at planned intervals and if significant changes occur. PRACTIC E ISP and procedures should be reviewed a""",
        "nist_mapping": "PL-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['policy', 'audit log', 'governance', 'procedure', 'information', 'topic', 'guideline', 'shall', 'policy updated', 'security'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-3": {
        "control_id": "RWNCSA-SP-3",
        "control_name": "Security Policy and Procedures - 4-3",
        "control_family": "Security Policy and Procedures",
        "description": """The institution can create topic -specific policies, extending and supplementing the ISP related to chapters of this standard.""",
        "nist_mapping": "PL-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['policy', 'audit log', 'governance', 'procedure', 'institution', 'topic', 'guideline', 'policy updated', 'compliance check', 'standard'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-4": {
        "control_id": "RWNCSA-SP-4",
        "control_name": "Security Policy and Procedures - 4-4",
        "control_family": "Security Policy and Procedures",
        "description": """The institution has documented operating procedures for information processing facilities. Operating procedures must be available to personnel who need them. Operating procedures are reviewed at planned intervals , and if significant changes occur. PRACTICE 1 ISP and procedures should be reviewed at""",
        "nist_mapping": "PL-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['policy', 'audit log', 'governance', 'procedure', 'institution', 'operating', 'information', 'guideline', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-5": {
        "control_id": "RWNCSA-SP-5",
        "control_name": "Security Policy and Procedures - 4-5",
        "control_family": "Security Policy and Procedures",
        "description": """The institution develops, documents, periodically (at least once per year or when needed) updates, and implements security plans for organizational information systems .""",
        "nist_mapping": "PL-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['periodically', 'least', 'policy', 'audit log', 'governance', 'procedure', 'institution', 'guideline', 'policy updated', 'security'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-6": {
        "control_id": "RWNCSA-SP-6",
        "control_name": "Security Policy and Procedures - 4-6",
        "control_family": "Security Policy and Procedures",
        "description": """Security plans should describe the controls in place (or planned ) for the information systems and the rules of behavio ur for individuals accessing the information systems . 1 e.g. in ISO 19011 - annual audit program, audit plans, auditing techniques, codes of conduct for auditors, audit reports wi""",
        "nist_mapping": "PL-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['policy', 'audit log', 'governance', 'procedure', 'guideline', 'describe', 'plans', 'security', 'standard', 'policy updated'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-7": {
        "control_id": "RWNCSA-SP-7",
        "control_name": "Security Policy and Procedures - 4-1",
        "control_family": "Security Policy and Procedures",
        "description": """The institution divides the area it manages into security zones based on risk assessment to ensure physical security. PRACTICE 1 Each of the zones must be designed in such a way as to eliminate the anticipated attack scenarios and where it is impossible to slow down the actions of a poten tial attac""",
        "nist_mapping": "PL-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['policy', 'zones', 'audit log', 'governance', 'procedure', 'institution', 'guideline', 'policy updated', 'security', 'standard'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-8": {
        "control_id": "RWNCSA-SP-8",
        "control_name": "Security Policy and Procedures - 4-2",
        "control_family": "Security Policy and Procedures",
        "description": """The institution provides, limited by the scope of official duties, access to particular security zones. The principle of necessary access applies (need to have).""",
        "nist_mapping": "PL-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['scope', 'official', 'policy', 'audit log', 'governance', 'procedure', 'institution', 'guideline', 'access', 'limited'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-9": {
        "control_id": "RWNCSA-SP-9",
        "control_name": "Security Policy and Procedures - 4-3",
        "control_family": "Security Policy and Procedures",
        "description": """The institution limits authorised individuals' physical access to organizational systems, equipment, and the respective operating environment s. PRACTICE 1 The requirement applies to employees, contractors, suppliers, subcontractors and visitors . PRACTICE 2 Rules f or entering and leaving t he secu""",
        "nist_mapping": "PL-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['policy', 'audit log', 'physical', 'governance', 'procedure', 'institution', 'guideline', 'access', 'limits', 'policy updated'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-10": {
        "control_id": "RWNCSA-SP-10",
        "control_name": "Security Policy and Procedures - 4-4",
        "control_family": "Security Policy and Procedures",
        "description": """The institution provides employees with basic physical security training. PRACTICE""",
        "nist_mapping": "PL-1",
        "compliance_type": "Basic",
        "audit_type": "policy",
        "evidence_patterns": ['policy', 'audit log', 'physical', 'governance', 'procedure', 'institution', 'guideline', 'policy updated', 'provides', 'standard'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-11": {
        "control_id": "RWNCSA-SP-11",
        "control_name": "Security Policy and Procedures - 4-5",
        "control_family": "Security Policy and Procedures",
        "description": """The institution protects and monitors the physical facility and support s infrastructure for organizational systems.""",
        "nist_mapping": "PL-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['monitors', 'policy', 'audit log', 'protects', 'governance', 'procedure', 'institution', 'physical', 'guideline', 'policy updated'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-12": {
        "control_id": "RWNCSA-SP-12",
        "control_name": "Security Policy and Procedures - 4-6",
        "control_family": "Security Policy and Procedures",
        "description": """The institution prevents or reduces the consequences of events originating from physical and environmental threats such as fire, flood, earthquake, explosion, civil unrest, toxic waste, environmental emissions and other forms of natural disaster or disaster caused by human beings. PRACTICE Physical """,
        "nist_mapping": "PL-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['events', 'policy', 'audit log', 'governance', 'procedure', 'institution', 'guideline', 'policy updated', 'compliance check', 'standard'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-13": {
        "control_id": "RWNCSA-SP-13",
        "control_name": "Security Policy and Procedures - 4-7",
        "control_family": "Security Policy and Procedures",
        "description": """The institution maintain s audit logs of physical access. Audit l ogs should be stored for a minimal 12 months period.""",
        "nist_mapping": "PL-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['policy', 'audit log', 'physical', 'governance', 'procedure', 'institution', 'maintain', 'guideline', 'audit', 'policy updated'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-14": {
        "control_id": "RWNCSA-SP-14",
        "control_name": "Security Policy and Procedures - 4-8",
        "control_family": "Security Policy and Procedures",
        "description": """The institution control s and manage s physical access devices (badges/keys/PIN codes/cards) . PRACTICE 1 Physical access devi ces should be registered and individualized, e.g ., by labe lling or numbering . PRACTICE 2 The rules for storing and issuing keys to protec ted rooms and zones, the periodi""",
        "nist_mapping": "PL-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['policy', 'audit log', 'physical', 'governance', 'procedure', 'institution', 'manage', 'guideline', 'control', 'access'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-15": {
        "control_id": "RWNCSA-SP-15",
        "control_name": "Security Policy and Procedures - 4-9",
        "control_family": "Security Policy and Procedures",
        "description": """The institution enforce s safeguarding measures for NPI processing at alternate work sites (e.g., Disaster recovery site ). PRACTICE 1 Physical security training should include: a) Understanding the disaster type; b) Emergency preparedness includes the location of emergency exits, how to carry out e""",
        "nist_mapping": "PL-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['policy', 'audit log', 'governance', 'procedure', 'institution', 'measures', 'guideline', 'policy updated', 'enforce', 'standard'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },
    "RWNCSA-SP-16": {
        "control_id": "RWNCSA-SP-16",
        "control_name": "Security Policy and Procedures - 4-10",
        "control_family": "Security Policy and Procedures",
        "description": """The institution assists and monitors visitors ’ activit ies. PRACTICE Visitors should access the facility under the supervision of an authorized employee of the institution from the moment of entering to the moment of leaving the facility. Minimum Cybersecurity Standards for Public Institutions 39 1""",
        "nist_mapping": "PL-1",
        "compliance_type": "Enhanced",
        "audit_type": "policy",
        "evidence_patterns": ['monitors', 'policy', 'assists', 'audit log', 'governance', 'procedure', 'institution', 'guideline', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Policy document exists and current', 'Procedures documented and followed', 'Regular review conducted', 'Staff acknowledgment on file'],
        "non_compliant_indicators": ['No policy document', 'Outdated procedures', 'No evidence of review', 'Missing acknowledgments'],
        "remediation_guidance": "Review and implement Security Policy and Procedures requirements per NCSA standards"
    },

    # -------------------------------------------------------------------------
    # System and Communications Protection (17 controls)
    # -------------------------------------------------------------------------
    "RWNCSA-SC-153": {
        "control_id": "RWNCSA-SC-153",
        "control_name": "System and Communications Protection - 17-1",
        "control_family": "System and Communications Protection",
        "description": """The institution monitors, controls, and protects communications (i.e., information transmitted or received by organizational systems) at the external and key internal boundaries of organizational ICT systems.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['transmitted', 'network', 'audit log', 'protects', 'institution', 'information', 'SSL', 'policy updated', 'compliance check', 'communications'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-154": {
        "control_id": "RWNCSA-SC-154",
        "control_name": "System and Communications Protection - 17-2",
        "control_family": "System and Communications Protection",
        "description": """The institution uses architectural designs, software development techniques, and systems engine ering principles that promote effective information security within organizational ICT systems. PRACTICES to 17-1, 17-2, 17-5, 17-8, 17-9 as well as 5-1, 5-2, 5-22 (Access Control domain) The institution """,
        "nist_mapping": "SC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'institution', 'SSL', 'development', 'software', 'architectural', 'policy updated', 'compliance check', 'systems'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-155": {
        "control_id": "RWNCSA-SC-155",
        "control_name": "System and Communications Protection - 17-3",
        "control_family": "System and Communications Protection",
        "description": """The institution separate s user functionality from system management functionality.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['network', 'management', 'audit log', 'separate', 'institution', 'SSL', 'policy updated', 'functionality', 'compliance check', 'system'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-156": {
        "control_id": "RWNCSA-SC-156",
        "control_name": "System and Communications Protection - 17-4",
        "control_family": "System and Communications Protection",
        "description": """The institution prevents unauthorized and unintended information transfer via shared system resources.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Basic",
        "audit_type": "system",
        "evidence_patterns": ['network', 'unauthorized', 'audit log', 'institution', 'unintended', 'SSL', 'information', 'policy updated', 'compliance check', 'prevents'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-157": {
        "control_id": "RWNCSA-SC-157",
        "control_name": "System and Communications Protection - 17-5",
        "control_family": "System and Communications Protection",
        "description": """The institution implement s subnetworks for publicly accessible system components that are physically or logically separated from internal networks.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'accessible', 'institution', 'SSL', 'subnetworks', 'publicly', 'implement', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-158": {
        "control_id": "RWNCSA-SC-158",
        "control_name": "System and Communications Protection - 17-6",
        "control_family": "System and Communications Protection",
        "description": """The institution denies traffi c by default and allow s traffic by exception (i.e., deny all, permit by exception).""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'institution', 'SSL', 'traffi', 'allow', 'policy updated', 'denies', 'compliance check', 'default'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-159": {
        "control_id": "RWNCSA-SC-159",
        "control_name": "System and Communications Protection - 17-7",
        "control_family": "System and Communications Protection",
        "description": """The institution prevents remote devices from simultaneously establishing non -remote connections with organizational systems and communicating via some other connection to resources in external networks (i.e., split tunne lling).""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'remote', 'institution', 'simultaneously', 'SSL', 'policy updated', 'compliance check', 'prevents', 'devices'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-160": {
        "control_id": "RWNCSA-SC-160",
        "control_name": "System and Communications Protection - 17-8",
        "control_family": "System and Communications Protection",
        "description": """The institution implement s cryptographic mechanisms to prevent unauthorized disclosure of NPI during transmission unless otherwise protected by alternative physical safeguards.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'prevent', 'mechanisms', 'institution', 'SSL', 'implement', 'policy updated', 'compliance check', 'cryptographic'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-161": {
        "control_id": "RWNCSA-SC-161",
        "control_name": "System and Communications Protection - 17-9",
        "control_family": "System and Communications Protection",
        "description": """The institution termina tes network connections associated with communications sessions at the end of the sessions or after a defined period of inactivity.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'institution', 'termina', 'SSL', 'associated', 'policy updated', 'compliance check', 'connections', 'boundary'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-162": {
        "control_id": "RWNCSA-SC-162",
        "control_name": "System and Communications Protection - 17-10",
        "control_family": "System and Communications Protection",
        "description": """The institution establish es and manage s cryptographic keys for cryptography used in organizational ICT systems.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['establish', 'network', 'audit log', 'institution', 'manage', 'SSL', 'policy updated', 'compliance check', 'cryptography', 'cryptographic'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-163": {
        "control_id": "RWNCSA-SC-163",
        "control_name": "System and Communications Protection - 17-11",
        "control_family": "System and Communications Protection",
        "description": """The institut ion uses strong cryptography when used to protect the confidentiality of NPI. Minimum Cybersecurity Standards for Public Institutions 46 PRACTICE Recommendation for strong cryptography mechanisms - See Appendix 1""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'protect', 'confidentiality', 'SSL', 'strong', 'policy updated', 'institut', 'cryptography', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-164": {
        "control_id": "RWNCSA-SC-164",
        "control_name": "System and Communications Protection - 17-12",
        "control_family": "System and Communications Protection",
        "description": """The institution prohibit s remote activation of collaborative computing devices (networked whiteboards, cameras, and microphones) and provides the information to the users when the device is enabled.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'remote', 'institution', 'SSL', 'prohibit', 'collaborative', 'policy updated', 'activation', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-165": {
        "control_id": "RWNCSA-SC-165",
        "control_name": "System and Communications Protection - 17-13",
        "control_family": "System and Communications Protection",
        "description": """The institution controls and monitors the use of mobile code. PRACTI CE Mobile code technologies include Java, JavaScript, ActiveX, Postscript, PDF, Flash animations, and VBScript. Decisions regarding the use of mobile code in organizational systems should base on the potential for the code to cause""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['monitors', 'network', 'controls', 'audit log', 'institution', 'SSL', 'mobile', 'policy updated', 'compliance check', 'practi'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-166": {
        "control_id": "RWNCSA-SC-166",
        "control_name": "System and Communications Protection - 17-14",
        "control_family": "System and Communications Protection",
        "description": """The institution controls and monitors Voice over Internet Protocol (VoIP) technologies.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['voice', 'monitors', 'network', 'controls', 'internet', 'audit log', 'institution', 'SSL', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-167": {
        "control_id": "RWNCSA-SC-167",
        "control_name": "System and Communications Protection - 17-15",
        "control_family": "System and Communications Protection",
        "description": """The institution protects the authenticity of communications sessions.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'protects', 'institution', 'SSL', 'authenticity', 'policy updated', 'compliance check', 'communications', 'boundary'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-168": {
        "control_id": "RWNCSA-SC-168",
        "control_name": "System and Communications Protection - 17-16",
        "control_family": "System and Communications Protection",
        "description": """The institution protects the confidentiality of NPI at rest.""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'protects', 'confidentiality', 'institution', 'SSL', 'policy updated', 'compliance check', 'boundary', 'encryption'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
    "RWNCSA-SC-169": {
        "control_id": "RWNCSA-SC-169",
        "control_name": "System and Communications Protection - 17-17",
        "control_family": "System and Communications Protection",
        "description": """The institution protect s its web application against cyber threats inherent in web technologies. PRACTI CE 1 Proper design and implementation of web applications, along with their deployment on secure execution platforms (e.g., PHP, Java, etc.) and application servers (such as Apache, Glassfish, We""",
        "nist_mapping": "SC-1",
        "compliance_type": "Enhanced",
        "audit_type": "system",
        "evidence_patterns": ['network', 'audit log', 'protect', 'cyber', 'institution', 'SSL', 'against', 'application', 'policy updated', 'compliance check'],
        "compliant_indicators": ['Control enabled and configured', 'Settings meet requirements', 'Monitoring active', 'Logs being collected'],
        "non_compliant_indicators": ['Control not enabled', 'Settings below requirements', 'No monitoring configured', 'Missing log entries'],
        "remediation_guidance": "Review and implement System and Communications Protection requirements per NCSA standards"
    },
}


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
    print(f"\nBy Audit Type:")
    for t, count in stats['by_audit_type'].items():
        print(f"  {t}: {count}")
    print(f"\nBy Compliance Type:")
    for t, count in stats['by_compliance_type'].items():
        print(f"  {t}: {count}")
