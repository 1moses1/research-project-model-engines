"""
Rwanda NCSA Minimum Cybersecurity Standards Control Database.

This module contains the complete mapping of Rwanda NCSA controls
with their descriptions, evidence patterns, and compliance indicators.
Used by the LLM for semantic compliance analysis.

Reference: Rwanda NCSA Minimum Cybersecurity Standards (2024)
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
    "SA": "System and Services Acquisition"
}

# =============================================================================
# NCSA Controls Database (47 Implemented + Key Controls)
# =============================================================================

NCSA_CONTROLS: Dict[str, Dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # Access Control (AC)
    # -------------------------------------------------------------------------
    "RWNCSA-AC-01": {
        "control_id": "RWNCSA-AC-01",
        "control_name": "Access Control Policy",
        "control_family": "Access Control",
        "description": "Establish and maintain access control policies and procedures",
        "nist_mapping": "AC-1",
        "evidence_patterns": [
            "access policy",
            "access control",
            "authorization policy"
        ],
        "compliant_indicators": [
            "Policy document exists and is current",
            "Access procedures documented",
            "Annual review completed"
        ],
        "non_compliant_indicators": [
            "No access policy",
            "Outdated procedures",
            "Missing documentation"
        ],
        "remediation_guidance": "Create and maintain documented access control policies"
    },
    "RWNCSA-AC-02": {
        "control_id": "RWNCSA-AC-02",
        "control_name": "Account Management",
        "control_family": "Access Control",
        "description": "Manage system accounts including creation, modification, and removal",
        "nist_mapping": "AC-2",
        "evidence_patterns": [
            "user account",
            "account created",
            "account disabled",
            "useradd",
            "userdel",
            "passwd"
        ],
        "compliant_indicators": [
            "Accounts reviewed periodically",
            "Inactive accounts disabled",
            "Account creation approved"
        ],
        "non_compliant_indicators": [
            "Orphan accounts exist",
            "No account review process",
            "Unauthorized account creation"
        ],
        "remediation_guidance": "Implement account lifecycle management process"
    },
    "RWNCSA-AC-37": {
        "control_id": "RWNCSA-AC-37",
        "control_name": "Failed Authentication Monitoring",
        "control_family": "Access Control",
        "description": "Monitor and alert on failed authentication attempts",
        "nist_mapping": "AC-7",
        "evidence_patterns": [
            "Failed password",
            "authentication failure",
            "Invalid user",
            "Access denied",
            "login failed",
            "invalid credentials"
        ],
        "compliant_indicators": [
            "Failed attempts logged",
            "Alerts configured for threshold",
            "Account lockout enabled"
        ],
        "non_compliant_indicators": [
            "No logging of failures",
            "No alert on repeated failures",
            "Unlimited login attempts"
        ],
        "remediation_guidance": "Enable failed authentication logging and alerting"
    },
    "RWNCSA-AC-38": {
        "control_id": "RWNCSA-AC-38",
        "control_name": "Invalid User Access Attempts",
        "control_family": "Access Control",
        "description": "Log and respond to access attempts for non-existent users",
        "nist_mapping": "AC-7",
        "evidence_patterns": [
            "Invalid user",
            "unknown user",
            "user not found",
            "no such user"
        ],
        "compliant_indicators": [
            "Invalid user attempts logged",
            "Security team notified",
            "IP blocking for repeated attempts"
        ],
        "non_compliant_indicators": [
            "No logging of invalid users",
            "No response to enumeration attacks"
        ],
        "remediation_guidance": "Configure logging for invalid user access attempts"
    },
    "RWNCSA-AC-42": {
        "control_id": "RWNCSA-AC-42",
        "control_name": "Privileged Access Management",
        "control_family": "Access Control",
        "description": "Control and monitor privileged access (sudo, root)",
        "nist_mapping": "AC-6",
        "evidence_patterns": [
            "sudo",
            "root",
            "privilege",
            "admin",
            "elevated",
            "superuser"
        ],
        "compliant_indicators": [
            "Sudo usage logged",
            "Least privilege enforced",
            "Privileged actions reviewed"
        ],
        "non_compliant_indicators": [
            "Unrestricted sudo access",
            "No logging of privileged commands",
            "Shared admin accounts"
        ],
        "remediation_guidance": "Implement sudo logging and least privilege"
    },

    # -------------------------------------------------------------------------
    # Audit and Accountability (AU)
    # -------------------------------------------------------------------------
    "RWNCSA-AU-01": {
        "control_id": "RWNCSA-AU-01",
        "control_name": "Audit Policy",
        "control_family": "Audit and Accountability",
        "description": "Establish audit logging policies and procedures",
        "nist_mapping": "AU-1",
        "evidence_patterns": [
            "audit policy",
            "logging policy",
            "audit trail"
        ],
        "compliant_indicators": [
            "Audit policy documented",
            "Log retention defined",
            "Audit review procedures"
        ],
        "non_compliant_indicators": [
            "No audit policy",
            "Undefined retention",
            "No review process"
        ],
        "remediation_guidance": "Document and implement audit logging policy"
    },
    "RWNCSA-AU-68": {
        "control_id": "RWNCSA-AU-68",
        "control_name": "Session Initiation Logging",
        "control_family": "Audit and Accountability",
        "description": "Log all session initiation events",
        "nist_mapping": "AU-14",
        "evidence_patterns": [
            "session opened",
            "session started",
            "login successful",
            "Accepted password",
            "Accepted publickey"
        ],
        "compliant_indicators": [
            "All sessions logged",
            "User identified in logs",
            "Timestamp recorded"
        ],
        "non_compliant_indicators": [
            "Sessions not logged",
            "Missing user information"
        ],
        "remediation_guidance": "Enable PAM session logging"
    },
    "RWNCSA-AU-69": {
        "control_id": "RWNCSA-AU-69",
        "control_name": "Session Termination Logging",
        "control_family": "Audit and Accountability",
        "description": "Log all session termination events",
        "nist_mapping": "AU-14",
        "evidence_patterns": [
            "session closed",
            "session ended",
            "logout",
            "disconnected"
        ],
        "compliant_indicators": [
            "Session end logged",
            "Duration trackable"
        ],
        "non_compliant_indicators": [
            "No session end logging"
        ],
        "remediation_guidance": "Enable session termination logging"
    },
    "RWNCSA-AU-70": {
        "control_id": "RWNCSA-AU-70",
        "control_name": "General Audit Events",
        "control_family": "Audit and Accountability",
        "description": "Log general system and security events",
        "nist_mapping": "AU-2",
        "evidence_patterns": [
            "audit",
            "syslog",
            "event",
            "log"
        ],
        "compliant_indicators": [
            "Events logged to central system",
            "Log integrity maintained"
        ],
        "non_compliant_indicators": [
            "Missing event categories",
            "Log tampering possible"
        ],
        "remediation_guidance": "Configure comprehensive audit logging"
    },

    # -------------------------------------------------------------------------
    # Identification and Authentication (IA)
    # -------------------------------------------------------------------------
    "RWNCSA-IA-01": {
        "control_id": "RWNCSA-IA-01",
        "control_name": "Identification and Authentication Policy",
        "control_family": "Identification and Authentication",
        "description": "Establish identification and authentication policies",
        "nist_mapping": "IA-1",
        "evidence_patterns": [
            "authentication policy",
            "password policy",
            "identity management"
        ],
        "compliant_indicators": [
            "Policy documented",
            "MFA requirements defined",
            "Password complexity set"
        ],
        "non_compliant_indicators": [
            "No authentication policy",
            "Weak password requirements"
        ],
        "remediation_guidance": "Document authentication policy with MFA requirements"
    },
    "RWNCSA-IA-97": {
        "control_id": "RWNCSA-IA-97",
        "control_name": "Password Authentication Success",
        "control_family": "Identification and Authentication",
        "description": "Log successful password authentications",
        "nist_mapping": "IA-2",
        "evidence_patterns": [
            "Accepted password",
            "password authentication successful",
            "login successful"
        ],
        "compliant_indicators": [
            "Successful logins logged",
            "User and source recorded"
        ],
        "non_compliant_indicators": [
            "No success logging"
        ],
        "remediation_guidance": "Enable successful authentication logging"
    },
    "RWNCSA-IA-98": {
        "control_id": "RWNCSA-IA-98",
        "control_name": "Password Authentication Failure",
        "control_family": "Identification and Authentication",
        "description": "Log failed password authentication attempts",
        "nist_mapping": "IA-2",
        "evidence_patterns": [
            "Failed password",
            "password authentication failed",
            "incorrect password",
            "wrong password"
        ],
        "compliant_indicators": [
            "Failed attempts logged with details",
            "Source IP recorded",
            "Timestamp accurate"
        ],
        "non_compliant_indicators": [
            "No failure logging",
            "Missing source information"
        ],
        "remediation_guidance": "Enable failed password logging with full context"
    },
    "RWNCSA-IA-99": {
        "control_id": "RWNCSA-IA-99",
        "control_name": "Public Key Authentication",
        "control_family": "Identification and Authentication",
        "description": "Support and log public key authentication",
        "nist_mapping": "IA-2",
        "evidence_patterns": [
            "Accepted publickey",
            "public key authentication",
            "ssh key",
            "RSA key"
        ],
        "compliant_indicators": [
            "PKI authentication enabled",
            "Key-based auth logged"
        ],
        "non_compliant_indicators": [
            "PKI not configured",
            "Key auth not logged"
        ],
        "remediation_guidance": "Enable and log public key authentication"
    },
    "RWNCSA-IA-100": {
        "control_id": "RWNCSA-IA-100",
        "control_name": "Connection Identification",
        "control_family": "Identification and Authentication",
        "description": "Require identification for all connections",
        "nist_mapping": "IA-3",
        "evidence_patterns": [
            "Did not receive identification",
            "no identification",
            "anonymous connection"
        ],
        "compliant_indicators": [
            "All connections identified",
            "Unidentified connections rejected"
        ],
        "non_compliant_indicators": [
            "Anonymous connections allowed",
            "Missing identification requirements"
        ],
        "remediation_guidance": "Require identification for all connections"
    },
    "RWNCSA-IA-101": {
        "control_id": "RWNCSA-IA-101",
        "control_name": "PAM Authentication",
        "control_family": "Identification and Authentication",
        "description": "Use PAM for centralized authentication management",
        "nist_mapping": "IA-2",
        "evidence_patterns": [
            "PAM",
            "pam_unix",
            "pam_ldap",
            "pam_sss"
        ],
        "compliant_indicators": [
            "PAM configured correctly",
            "Authentication modules active"
        ],
        "non_compliant_indicators": [
            "PAM misconfigured",
            "Weak PAM modules"
        ],
        "remediation_guidance": "Configure PAM with appropriate security modules"
    },

    # -------------------------------------------------------------------------
    # Configuration Management (CM)
    # -------------------------------------------------------------------------
    "RWNCSA-CM-01": {
        "control_id": "RWNCSA-CM-01",
        "control_name": "Configuration Management Policy",
        "control_family": "Configuration Management",
        "description": "Establish configuration management policies",
        "nist_mapping": "CM-1",
        "evidence_patterns": [
            "configuration policy",
            "baseline configuration",
            "configuration management"
        ],
        "compliant_indicators": [
            "CM policy documented",
            "Baselines established",
            "Change control process"
        ],
        "non_compliant_indicators": [
            "No CM policy",
            "Ad-hoc configurations"
        ],
        "remediation_guidance": "Document configuration management policy"
    },
    "RWNCSA-CM-83": {
        "control_id": "RWNCSA-CM-83",
        "control_name": "Scheduled Task Management",
        "control_family": "Configuration Management",
        "description": "Manage and audit scheduled tasks (cron jobs)",
        "nist_mapping": "CM-7",
        "evidence_patterns": [
            "CRON",
            "crontab",
            "scheduled task",
            "systemd timer"
        ],
        "compliant_indicators": [
            "Cron jobs documented",
            "Task execution logged",
            "Authorized tasks only"
        ],
        "non_compliant_indicators": [
            "Undocumented cron jobs",
            "Unauthorized scheduled tasks"
        ],
        "remediation_guidance": "Document and review all scheduled tasks"
    },

    # -------------------------------------------------------------------------
    # System and Communications Protection (SC)
    # -------------------------------------------------------------------------
    "RWNCSA-SC-01": {
        "control_id": "RWNCSA-SC-01",
        "control_name": "System and Communications Policy",
        "control_family": "System and Communications Protection",
        "description": "Establish system and communications protection policies",
        "nist_mapping": "SC-1",
        "evidence_patterns": [
            "security policy",
            "communications protection",
            "network security"
        ],
        "compliant_indicators": [
            "Policy documented",
            "Encryption requirements defined"
        ],
        "non_compliant_indicators": [
            "No communications policy"
        ],
        "remediation_guidance": "Document communications protection policy"
    },
    "RWNCSA-SC-155": {
        "control_id": "RWNCSA-SC-155",
        "control_name": "Connection Termination",
        "control_family": "System and Communications Protection",
        "description": "Properly terminate network connections",
        "nist_mapping": "SC-10",
        "evidence_patterns": [
            "Connection closed",
            "connection terminated",
            "session timeout",
            "disconnect"
        ],
        "compliant_indicators": [
            "Connections properly closed",
            "Timeouts configured",
            "No orphan connections"
        ],
        "non_compliant_indicators": [
            "Orphan connections",
            "No timeout configured"
        ],
        "remediation_guidance": "Configure connection timeouts and cleanup"
    },

    # -------------------------------------------------------------------------
    # System and Information Integrity (SI)
    # -------------------------------------------------------------------------
    "RWNCSA-SI-01": {
        "control_id": "RWNCSA-SI-01",
        "control_name": "System Integrity Policy",
        "control_family": "System and Information Integrity",
        "description": "Establish system and information integrity policies",
        "nist_mapping": "SI-1",
        "evidence_patterns": [
            "integrity policy",
            "malware protection",
            "system monitoring"
        ],
        "compliant_indicators": [
            "Integrity policy documented",
            "Monitoring configured"
        ],
        "non_compliant_indicators": [
            "No integrity policy"
        ],
        "remediation_guidance": "Document system integrity policy"
    },
    "RWNCSA-SI-03": {
        "control_id": "RWNCSA-SI-03",
        "control_name": "Malware Protection",
        "control_family": "System and Information Integrity",
        "description": "Implement malware detection and prevention",
        "nist_mapping": "SI-3",
        "evidence_patterns": [
            "antivirus",
            "malware",
            "virus detected",
            "threat detected",
            "quarantine"
        ],
        "compliant_indicators": [
            "AV software installed",
            "Signatures updated",
            "Real-time scanning enabled"
        ],
        "non_compliant_indicators": [
            "No AV protection",
            "Outdated signatures",
            "Scanning disabled"
        ],
        "remediation_guidance": "Install and configure malware protection"
    },
    "RWNCSA-SI-04": {
        "control_id": "RWNCSA-SI-04",
        "control_name": "System Monitoring",
        "control_family": "System and Information Integrity",
        "description": "Monitor systems for security-relevant events",
        "nist_mapping": "SI-4",
        "evidence_patterns": [
            "monitoring",
            "alert",
            "intrusion detection",
            "IDS",
            "SIEM"
        ],
        "compliant_indicators": [
            "Monitoring active",
            "Alerts configured",
            "Events reviewed"
        ],
        "non_compliant_indicators": [
            "No monitoring",
            "Alerts ignored"
        ],
        "remediation_guidance": "Implement security monitoring"
    },
    "RWNCSA-SI-10": {
        "control_id": "RWNCSA-SI-10",
        "control_name": "Input Validation",
        "control_family": "System and Information Integrity",
        "description": "Validate all input to prevent injection attacks",
        "nist_mapping": "SI-10",
        "evidence_patterns": [
            "input validation",
            "sanitization",
            "injection",
            "XSS",
            "SQL injection"
        ],
        "compliant_indicators": [
            "Input validated",
            "Injection attempts blocked"
        ],
        "non_compliant_indicators": [
            "No input validation",
            "Injection vulnerabilities"
        ],
        "remediation_guidance": "Implement comprehensive input validation"
    },

    # -------------------------------------------------------------------------
    # Incident Response (IR)
    # -------------------------------------------------------------------------
    "RWNCSA-IR-01": {
        "control_id": "RWNCSA-IR-01",
        "control_name": "Incident Response Policy",
        "control_family": "Incident Response",
        "description": "Establish incident response policies and procedures",
        "nist_mapping": "IR-1",
        "evidence_patterns": [
            "incident response",
            "incident handling",
            "security incident"
        ],
        "compliant_indicators": [
            "IR policy documented",
            "Response procedures defined",
            "Contact list maintained"
        ],
        "non_compliant_indicators": [
            "No IR policy",
            "No response procedures"
        ],
        "remediation_guidance": "Document incident response policy and procedures"
    },

    # -------------------------------------------------------------------------
    # Risk Assessment (RA)
    # -------------------------------------------------------------------------
    "RWNCSA-RA-01": {
        "control_id": "RWNCSA-RA-01",
        "control_name": "Risk Assessment Policy",
        "control_family": "Risk Assessment",
        "description": "Establish risk assessment policies",
        "nist_mapping": "RA-1",
        "evidence_patterns": [
            "risk assessment",
            "vulnerability assessment",
            "threat assessment"
        ],
        "compliant_indicators": [
            "Risk assessment conducted",
            "Vulnerabilities identified"
        ],
        "non_compliant_indicators": [
            "No risk assessment"
        ],
        "remediation_guidance": "Conduct periodic risk assessments"
    }
}


def get_control(control_id: str) -> Dict[str, Any]:
    """Get a specific control by ID."""
    return NCSA_CONTROLS.get(control_id, {})


def get_controls_by_family(family: str) -> List[Dict[str, Any]]:
    """Get all controls in a family."""
    family_code = family.upper()[:2]
    return [
        ctrl for ctrl_id, ctrl in NCSA_CONTROLS.items()
        if family_code in ctrl_id
    ]


def get_all_controls() -> Dict[str, Dict[str, Any]]:
    """Get all controls."""
    return NCSA_CONTROLS


def find_relevant_controls(log_message: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Find controls relevant to a log message based on pattern matching."""
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
