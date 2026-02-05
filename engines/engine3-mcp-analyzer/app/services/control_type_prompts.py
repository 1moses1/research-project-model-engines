"""
Control-Type Specific Prompts for MCP+LLM Analysis.

This module provides specialized prompts for different control audit types:
- system: Log-based evidence analysis
- policy: Document/policy evidence analysis
- physical: Physical control verification
- mixed: Combined technical + policy analysis

The MCP+LLM architecture enables us to handle ALL 169 Rwanda NCSA controls,
not just the 47 system-auditable ones.
"""

from typing import Dict, Any, List, Optional


# =============================================================================
# Control Type Definitions
# =============================================================================

CONTROL_AUDIT_TYPES = {
    "system": {
        "description": "System-auditable via CLI commands and log analysis",
        "evidence_sources": ["system logs", "command outputs", "configuration files", "audit trails"],
        "llm_role": "Analyze technical evidence to determine compliance"
    },
    "policy": {
        "description": "Policy-based controls requiring document analysis",
        "evidence_sources": ["policy documents", "procedures", "acknowledgments", "training records"],
        "llm_role": "Evaluate policy documentation completeness and currency"
    },
    "physical": {
        "description": "Physical and environmental controls",
        "evidence_sources": ["access logs", "inspection reports", "photos", "checklists"],
        "llm_role": "Assess physical security evidence and verification records"
    },
    "mixed": {
        "description": "Combined technical and policy controls",
        "evidence_sources": ["system logs", "policy documents", "test results", "audit reports"],
        "llm_role": "Evaluate both technical implementation and policy compliance"
    }
}


# =============================================================================
# System-Auditable Control Prompt (Logs and Configs)
# =============================================================================

SYSTEM_CONTROL_PROMPT = """You are a cybersecurity compliance auditor specializing in Rwanda's National Cyber Security Authority (NCSA) Minimum Cybersecurity Standards.

## Your Task
Analyze the following SYSTEM EVIDENCE (log entry, command output, or configuration) to determine compliance with the specified control.

## Control Being Evaluated
- **Control ID**: {control_id}
- **Control Name**: {control_name}
- **Control Family**: {control_family}
- **Description**: {control_description}
- **NIST Mapping**: {nist_mapping}

## Evidence to Analyze
```
{evidence}
```

## Context Information
- Timestamp: {timestamp}
- Source IP: {source_ip}
- User ID: {user_id}
- System: {system}

## Classification Rules

**Mark as COMPLIANT if:**
{compliant_indicators}

**Mark as NON_COMPLIANT if:**
{non_compliant_indicators}

## Response Format
Respond with valid JSON:
{{
    "control_id": "{control_id}",
    "compliance_status": "compliant|non_compliant|partial",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation of your determination",
    "evidence_found": ["specific evidence from the input"],
    "gaps_identified": ["any compliance gaps found"],
    "recommended_actions": ["remediation steps if non-compliant"]
}}
"""


# =============================================================================
# Policy-Based Control Prompt (Documents and Procedures)
# =============================================================================

POLICY_CONTROL_PROMPT = """You are a cybersecurity compliance auditor specializing in Rwanda's National Cyber Security Authority (NCSA) Minimum Cybersecurity Standards.

## Your Task
Analyze the following POLICY EVIDENCE (document, procedure, or administrative record) to determine compliance with the specified control.

## Control Being Evaluated
- **Control ID**: {control_id}
- **Control Name**: {control_name}
- **Control Family**: {control_family}
- **Description**: {control_description}
- **Compliance Type**: {compliance_type}

## Policy Evidence to Analyze
```
{evidence}
```

## What to Look For

**For Policy-Based Controls, evaluate:**
1. **Document Existence**: Is there a documented policy/procedure?
2. **Currency**: Is the document current (reviewed within required period)?
3. **Completeness**: Does it cover all required elements?
4. **Approval**: Is it approved by appropriate management?
5. **Communication**: Is there evidence of communication to staff?
6. **Acknowledgment**: Are there staff acknowledgments on file?

## Classification Rules

**Mark as COMPLIANT if:**
- Policy document exists and is current
- All required elements are addressed
- Evidence of management approval
- Staff have acknowledged/received training

**Mark as NON_COMPLIANT if:**
- No policy document exists
- Document is outdated (>1 year without review)
- Missing required elements
- No evidence of communication

**Mark as PARTIAL if:**
- Document exists but is incomplete
- Some elements missing
- Approval pending
- Partial staff acknowledgment

## Response Format
Respond with valid JSON:
{{
    "control_id": "{control_id}",
    "compliance_status": "compliant|non_compliant|partial",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation of your determination",
    "document_status": {{
        "exists": true/false,
        "current": true/false,
        "complete": true/false,
        "approved": true/false,
        "communicated": true/false
    }},
    "gaps_identified": ["any compliance gaps found"],
    "recommended_actions": ["steps to achieve compliance"]
}}
"""


# =============================================================================
# Physical Control Prompt (Physical Security)
# =============================================================================

PHYSICAL_CONTROL_PROMPT = """You are a cybersecurity compliance auditor specializing in Rwanda's National Cyber Security Authority (NCSA) Minimum Cybersecurity Standards.

## Your Task
Analyze the following PHYSICAL SECURITY EVIDENCE to determine compliance with the specified control.

## Control Being Evaluated
- **Control ID**: {control_id}
- **Control Name**: {control_name}
- **Control Family**: {control_family}
- **Description**: {control_description}

## Physical Security Evidence
```
{evidence}
```

## What to Look For

**For Physical Controls, evaluate:**
1. **Access Controls**: Badge systems, locks, visitor logs
2. **Surveillance**: CCTV coverage, recording retention
3. **Environmental**: Fire suppression, temperature, humidity
4. **Power**: UPS, generators, redundancy
5. **Inspections**: Regular inspection records

## Classification Rules

**Mark as COMPLIANT if:**
- Physical controls are in place and functioning
- Access logs are maintained
- Environmental controls meet specifications
- Regular inspections are conducted

**Mark as NON_COMPLIANT if:**
- Physical controls missing or non-functional
- No access logging
- Environmental controls failing
- No inspection records

**Mark as PARTIAL if:**
- Controls exist but have gaps
- Inconsistent logging
- Some environmental issues
- Irregular inspections

## Response Format
Respond with valid JSON:
{{
    "control_id": "{control_id}",
    "compliance_status": "compliant|non_compliant|partial",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation of your determination",
    "physical_controls_status": {{
        "access_controls": "compliant|non_compliant|partial|not_assessed",
        "surveillance": "compliant|non_compliant|partial|not_assessed",
        "environmental": "compliant|non_compliant|partial|not_assessed",
        "power": "compliant|non_compliant|partial|not_assessed"
    }},
    "gaps_identified": ["any compliance gaps found"],
    "recommended_actions": ["steps to achieve compliance"]
}}
"""


# =============================================================================
# Mixed Control Prompt (Technical + Policy)
# =============================================================================

MIXED_CONTROL_PROMPT = """You are a cybersecurity compliance auditor specializing in Rwanda's National Cyber Security Authority (NCSA) Minimum Cybersecurity Standards.

## Your Task
Analyze the following MIXED EVIDENCE (both technical and policy) to determine compliance with the specified control.

## Control Being Evaluated
- **Control ID**: {control_id}
- **Control Name**: {control_name}
- **Control Family**: {control_family}
- **Description**: {control_description}
- **NIST Mapping**: {nist_mapping}

## Evidence to Analyze

### Technical Evidence
```
{technical_evidence}
```

### Policy Evidence
```
{policy_evidence}
```

## What to Look For

**For Mixed Controls, evaluate BOTH:**

1. **Technical Implementation**:
   - Are technical controls configured correctly?
   - Are logs being collected?
   - Are settings meeting requirements?

2. **Policy Documentation**:
   - Is there documented policy/procedure?
   - Is it current and approved?
   - Is there evidence of implementation?

## Classification Rules

**Mark as COMPLIANT if:**
- Technical controls are properly implemented
- Policy documentation is complete and current
- Evidence shows consistent implementation

**Mark as NON_COMPLIANT if:**
- Technical controls missing or misconfigured
- No policy documentation
- Significant gaps between policy and implementation

**Mark as PARTIAL if:**
- Technical controls partially implemented
- Policy exists but incomplete
- Some gaps between policy and practice

## Response Format
Respond with valid JSON:
{{
    "control_id": "{control_id}",
    "compliance_status": "compliant|non_compliant|partial",
    "confidence": 0.0-1.0,
    "reasoning": "Detailed explanation of your determination",
    "technical_status": "compliant|non_compliant|partial",
    "policy_status": "compliant|non_compliant|partial",
    "gaps_identified": ["any compliance gaps found"],
    "recommended_actions": ["steps to achieve compliance"]
}}
"""


# =============================================================================
# Helper Functions
# =============================================================================

def get_prompt_for_control_type(audit_type: str) -> str:
    """Get the appropriate prompt template for a control's audit type."""
    prompts = {
        "system": SYSTEM_CONTROL_PROMPT,
        "policy": POLICY_CONTROL_PROMPT,
        "physical": PHYSICAL_CONTROL_PROMPT,
        "mixed": MIXED_CONTROL_PROMPT
    }
    return prompts.get(audit_type, SYSTEM_CONTROL_PROMPT)


def format_control_prompt(
    control: Dict[str, Any],
    evidence: str,
    context: Optional[Dict[str, Any]] = None,
    technical_evidence: Optional[str] = None,
    policy_evidence: Optional[str] = None
) -> str:
    """
    Format the appropriate prompt for a control based on its audit type.

    Args:
        control: The control definition from ncsa_controls_expanded
        evidence: Primary evidence to analyze
        context: Optional context (timestamp, IP, user, etc.)
        technical_evidence: For mixed controls, technical evidence
        policy_evidence: For mixed controls, policy evidence

    Returns:
        Formatted prompt string ready for LLM
    """
    audit_type = control.get("audit_type", "system")
    prompt_template = get_prompt_for_control_type(audit_type)

    context = context or {}

    # Format compliant/non-compliant indicators as bullet points
    compliant_indicators = "\n".join([
        f"- {ind}" for ind in control.get("compliant_indicators", [])
    ])
    non_compliant_indicators = "\n".join([
        f"- {ind}" for ind in control.get("non_compliant_indicators", [])
    ])

    # Base format arguments
    format_args = {
        "control_id": control.get("control_id", ""),
        "control_name": control.get("control_name", ""),
        "control_family": control.get("control_family", ""),
        "control_description": control.get("description", ""),
        "nist_mapping": control.get("nist_mapping", "N/A"),
        "compliance_type": control.get("compliance_type", "Basic"),
        "evidence": evidence,
        "timestamp": context.get("timestamp", "Unknown"),
        "source_ip": context.get("source_ip", "Unknown"),
        "user_id": context.get("user_id", "Unknown"),
        "system": context.get("system", "Unknown"),
        "compliant_indicators": compliant_indicators,
        "non_compliant_indicators": non_compliant_indicators,
    }

    # Add mixed-control specific fields
    if audit_type == "mixed":
        format_args["technical_evidence"] = technical_evidence or evidence
        format_args["policy_evidence"] = policy_evidence or "No policy evidence provided"

    return prompt_template.format(**format_args)


def determine_evidence_type(evidence: str) -> str:
    """
    Heuristically determine what type of evidence is provided.

    Returns:
        'log' - System log entry
        'config' - Configuration output
        'policy' - Policy document text
        'mixed' - Combination
    """
    evidence_lower = evidence.lower()

    # Check for log indicators
    log_indicators = ["failed", "accepted", "session", "login", "logout", "error",
                      "warning", "info", "debug", "audit", "syslog"]
    has_log = any(ind in evidence_lower for ind in log_indicators)

    # Check for config indicators
    config_indicators = ["enabled", "disabled", "setting", "configuration",
                         "status:", "value:", "="]
    has_config = any(ind in evidence_lower for ind in config_indicators)

    # Check for policy indicators
    policy_indicators = ["policy", "procedure", "shall", "must", "requirement",
                         "approved", "documented", "section", "chapter"]
    has_policy = any(ind in evidence_lower for ind in policy_indicators)

    if has_policy and (has_log or has_config):
        return "mixed"
    elif has_policy:
        return "policy"
    elif has_config:
        return "config"
    else:
        return "log"


# =============================================================================
# Control Type Statistics
# =============================================================================

def get_control_type_stats(controls: Dict[str, Dict]) -> Dict[str, int]:
    """Get statistics on control audit types."""
    stats = {"system": 0, "policy": 0, "physical": 0, "mixed": 0}
    for ctrl in controls.values():
        audit_type = ctrl.get("audit_type", "system")
        stats[audit_type] = stats.get(audit_type, 0) + 1
    return stats
