#!/usr/bin/env python3
"""
Generate Audit Commands for Rwanda NCSA System-Auditable Controls

This script generates macOS audit commands and parser configurations for
all system-auditable controls based on their family and description keywords.

The MCP+LLM analyzer will use these for:
1. CLI-based evidence collection (Engine 1)
2. Output parsing and compliance evaluation (Evidence Parsers)
3. Fallback when LLM is unavailable
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
EXPANDED_CONTROLS_FILE = PROJECT_ROOT / "engines/engine3-mcp-analyzer/app/models/ncsa_controls_expanded.py"
EXISTING_CONTROLS_FILE = PROJECT_ROOT / "engines/shared/rwanda_ncsa_controls.json"
OUTPUT_FILE = PROJECT_ROOT / "engines/shared/rwanda_ncsa_controls_expanded.json"

# =============================================================================
# Audit Command Templates by Control Family
# =============================================================================

# macOS commands for each control family
FAMILY_AUDIT_COMMANDS = {
    "Access Control": {
        "default": "dscl . -list /Users",
        "keywords": {
            "login": ("last -20", "extract_login_entries"),
            "password": ("pwpolicy -getaccountpolicies", "parse_password_policy"),
            "account": ("dscl . -list /Users", "parse_user_accounts"),
            "admin": ("dscl . -read /Groups/admin GroupMembership", "parse_admin_access"),
            "privilege": ("sudo -l 2>/dev/null || echo 'sudo check'", "parse_sudo_config"),
            "session": ("who", "parse_active_sessions"),
            "remote": ("systemsetup -getremotelogin", "parse_ssh_config"),
            "ssh": ("cat /etc/ssh/sshd_config 2>/dev/null || echo 'SSH not configured'", "parse_ssh_config"),
            "lock": ("defaults read com.apple.screensaver askForPassword 2>/dev/null || echo '0'", "parse_screen_lock"),
            "permission": ("ls -la /etc /var/log /usr/local 2>/dev/null | head -20", "parse_file_permissions"),
            "flow": ("pfctl -sr 2>/dev/null || echo 'pf not running'", "parse_pf_rules"),
            "separation": ("dscl . -list /Groups", "parse_user_groups"),
            "least": ("sudo -l 2>/dev/null || echo 'sudo check'", "parse_sudo_config"),
        }
    },
    "Audit and Accountability": {
        "default": "log show --last 1h --info | head -50",
        "keywords": {
            "log": ("log show --last 1h --info | head -50", "parse_system_logs"),
            "audit": ("launchctl list | grep -i audit", "parse_audit_system"),
            "record": ("ls -la /var/audit 2>/dev/null || echo 'No audit files'", "parse_audit_files"),
            "event": ("log show --predicate 'eventMessage contains \"auth\"' --last 1h | head -20", "parse_auth_events"),
            "timestamp": ("date && log show --last 5m | head -10", "parse_timestamps"),
            "retention": ("ls -la /var/log/*.log 2>/dev/null | head -20", "parse_log_retention"),
            "time": ("systemsetup -getusingnetworktime && systemsetup -getnetworktimeserver", "parse_time_sync"),
            "protect": ("ls -la /var/log 2>/dev/null", "parse_log_protection"),
            "review": ("log show --last 1d --info | wc -l", "parse_log_stats"),
            "alert": ("log show --predicate 'eventMessage contains \"fail\"' --last 1h | head -10", "parse_security_alerts"),
        }
    },
    "Configuration Management": {
        "default": "system_profiler SPSoftwareDataType",
        "keywords": {
            "configuration": ("system_profiler SPSoftwareDataType", "parse_system_info"),
            "baseline": ("defaults read -g 2>/dev/null | head -30", "parse_baseline_config"),
            "change": ("log show --predicate 'eventMessage contains \"config\"' --last 1d | head -20", "parse_config_changes"),
            "inventory": ("system_profiler SPApplicationsDataType | head -50", "parse_software_inventory"),
            "software": ("pkgutil --pkgs | head -30", "parse_installed_packages"),
            "update": ("softwareupdate --list 2>/dev/null || echo 'No updates'", "parse_patch_status"),
            "component": ("ls -la /Applications | head -30", "parse_installed_apps"),
            "restrict": ("csrutil status", "parse_sip_status"),
            "function": ("launchctl list | head -30", "parse_running_services"),
        }
    },
    "Identity Management and Authentication": {
        "default": "dscl . -list /Users",
        "keywords": {
            "identification": ("dscl . -list /Users", "parse_user_accounts"),
            "authentication": ("security find-identity -v -p codesigning 2>/dev/null || echo 'No certs'", "parse_certificates"),
            "credential": ("security list-keychains", "parse_keychain_config"),
            "password": ("pwpolicy -getaccountpolicies 2>/dev/null || echo 'Default policy'", "parse_password_policy"),
            "authenticator": ("security find-identity -v 2>/dev/null || echo 'No identities'", "parse_auth_identities"),
            "token": ("security list-smartcards 2>/dev/null || echo 'No smart cards'", "parse_smart_cards"),
            "biometric": ("bioutil -r 2>/dev/null || echo 'Biometrics not available'", "parse_biometric_config"),
            "multifactor": ("security find-identity -v -p codesigning 2>/dev/null || echo 'No certs'", "parse_mfa_config"),
            "replay": ("log show --predicate 'eventMessage contains \"replay\"' --last 1d | head -10", "parse_replay_protection"),
        }
    },
    "Incident Response": {
        "default": "log show --predicate 'eventMessage contains \"error\" or eventMessage contains \"fail\"' --last 1h | head -30",
        "keywords": {
            "incident": ("log show --predicate 'eventMessage contains \"error\"' --last 1h | head -30", "parse_incident_logs"),
            "response": ("ps aux | grep -i 'security\\|antivirus\\|defender' | head -10", "parse_security_processes"),
            "monitor": ("log stream --predicate 'eventMessage contains \"alert\"' --timeout 5s 2>/dev/null || echo 'Monitoring active'", "parse_monitoring_status"),
            "report": ("log show --last 1d --info | wc -l", "parse_log_volume"),
            "contain": ("pfctl -sr 2>/dev/null | head -10", "parse_containment_rules"),
            "handle": ("launchctl list | grep -i security", "parse_security_services"),
        }
    },
    "System and Communications Protection": {
        "default": "/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate",
        "keywords": {
            "boundary": ("/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate", "parse_firewall_status"),
            "firewall": ("/usr/libexec/ApplicationFirewall/socketfilterfw --listapps 2>/dev/null | head -20", "parse_firewall_apps"),
            "protection": ("csrutil status", "parse_sip_status"),
            "encryption": ("fdesetup status", "parse_filevault_status"),
            "transmission": ("networksetup -listallnetworkservices", "parse_network_services"),
            "cryptographic": ("security find-identity -v -p ssl-client 2>/dev/null | head -10", "parse_ssl_certs"),
            "network": ("netstat -an | head -30", "parse_network_connections"),
            "separation": ("pfctl -sr 2>/dev/null | head -20", "parse_network_rules"),
            "connection": ("netstat -an | grep ESTABLISHED | head -20", "parse_active_connections"),
            "denial": ("sysctl kern.maxfiles kern.maxfilesperproc 2>/dev/null", "parse_resource_limits"),
            "key": ("security find-identity -v 2>/dev/null | head -20", "parse_key_management"),
            "certificate": ("security find-certificate -a 2>/dev/null | head -30", "parse_certificates"),
            "session": ("who", "parse_active_sessions"),
            "mobile": ("profiles list 2>/dev/null || echo 'No MDM profiles'", "parse_mdm_profiles"),
            "wireless": ("networksetup -getairportpower en0 2>/dev/null || echo 'WiFi check'", "parse_wifi_config"),
        }
    }
}

# Severity mapping based on keywords
SEVERITY_KEYWORDS = {
    "CRITICAL": ["privilege", "admin", "root", "encryption", "authentication", "password", "credential"],
    "HIGH": ["access", "log", "audit", "firewall", "session", "account", "monitor"],
    "MEDIUM": ["configuration", "update", "change", "network", "software"],
    "LOW": ["inventory", "documentation", "review"]
}


def get_severity(description: str) -> str:
    """Determine severity based on description keywords."""
    desc_lower = description.lower()
    for severity, keywords in SEVERITY_KEYWORDS.items():
        if any(kw in desc_lower for kw in keywords):
            return severity
    return "MEDIUM"


def find_best_command(description: str, family: str) -> Tuple[str, str]:
    """Find the best audit command and parser for a control based on its description."""
    desc_lower = description.lower()
    family_config = FAMILY_AUDIT_COMMANDS.get(family, FAMILY_AUDIT_COMMANDS["Access Control"])

    # Check each keyword
    for keyword, (command, parser) in family_config.get("keywords", {}).items():
        if keyword in desc_lower:
            return command, parser

    # Return default for family
    return family_config["default"], "parse_generic_output"


def generate_control_entry(control: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a full control entry with audit commands."""
    family = control.get("control_family", "Access Control")
    description = control.get("description", "")
    control_id = control.get("control_id", "")

    audit_command, parser_logic = find_best_command(description, family)
    severity = get_severity(description)

    return {
        "family": family,
        "name": control.get("control_name", ""),
        "description": description,
        "severity": severity,
        "nist_mapping": control.get("nist_mapping", "N/A"),
        "compliance_type": control.get("compliance_type", "Basic"),
        "audit_type": control.get("audit_type", "system"),
        "requirements": {
            "monitoring_enabled": True,
            "evidence_collection": True,
            "regular_review": True
        },
        "compliance_criteria": {
            "pass_conditions": control.get("compliant_indicators", [
                "Control implemented as required",
                "Evidence of compliance available",
                "No gaps identified"
            ]),
            "fail_conditions": control.get("non_compliant_indicators", [
                "Control not implemented",
                "Missing evidence",
                "Compliance gaps identified"
            ])
        },
        "macos_implementation": {
            "audit_command": audit_command,
            "expected_output_pattern": ".*",
            "parser_logic": parser_logic,
            "validation": "output_not_empty AND no_error_messages"
        },
        "remediation": {
            "steps": [
                f"Review {family} requirements",
                f"Implement control: {control.get('control_name', '')}",
                "Verify implementation with audit command"
            ],
            "verification_command": audit_command,
            "expected_result": "Compliance evidence available"
        },
        "evidence_patterns": control.get("evidence_patterns", []),
        "risk_assessment": {
            "if_non_compliant": f"{severity} - {control.get('remediation_guidance', 'Review and implement control')}",
            "business_impact": f"Non-compliance with {family} requirements",
            "likelihood": "MEDIUM"
        }
    }


def load_expanded_controls() -> Dict[str, Dict]:
    """Load controls from expanded Python file."""
    with open(EXPANDED_CONTROLS_FILE, 'r') as f:
        content = f.read()

    # Execute to get NCSA_CONTROLS
    exec_globals = {}
    exec(compile(content, str(EXPANDED_CONTROLS_FILE), 'exec'), exec_globals)
    return exec_globals['NCSA_CONTROLS']


def load_existing_controls() -> Dict[str, Any]:
    """Load existing controls from JSON file."""
    with open(EXISTING_CONTROLS_FILE, 'r') as f:
        return json.load(f)


def main():
    """Generate expanded rwanda_ncsa_controls.json with all system-auditable controls."""
    print("Loading expanded controls...")
    expanded_controls = load_expanded_controls()

    print("Loading existing controls...")
    existing = load_existing_controls()
    existing_controls = existing.get('controls', {})

    # Filter system-auditable controls
    system_controls = {
        cid: ctrl for cid, ctrl in expanded_controls.items()
        if ctrl.get('audit_type') == 'system'
    }

    print(f"Found {len(system_controls)} system-auditable controls")

    # Generate full control entries
    output_controls = {}

    # Keep existing controls (they have detailed implementations)
    for cid, ctrl in existing_controls.items():
        output_controls[cid] = ctrl

    # Add new system-auditable controls
    new_count = 0
    for cid, ctrl in system_controls.items():
        if cid not in output_controls:
            output_controls[cid] = generate_control_entry(ctrl)
            new_count += 1

    print(f"Added {new_count} new system-auditable controls")

    # Create output structure
    output = {
        "metadata": {
            "framework": "Rwanda National Cyber Security Authority (NCSA)",
            "version": "2.0",
            "last_updated": "2025-02-03",
            "description": "Rwanda NCSA cybersecurity control requirements - expanded with all system-auditable controls",
            "total_controls": len(output_controls),
            "system_auditable": len([c for c in output_controls.values() if c.get("audit_type", "system") == "system"]),
            "from_original": 47,
            "from_expanded": new_count
        },
        "controls": output_controls
    }

    # Write output
    print(f"Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    print("\n" + "=" * 60)
    print("AUDIT COMMAND GENERATION COMPLETE")
    print("=" * 60)

    by_family = defaultdict(int)
    for ctrl in output_controls.values():
        by_family[ctrl.get("family", "Unknown")] += 1

    print(f"Total controls: {len(output_controls)}")
    print("\nBy family:")
    for family, count in sorted(by_family.items()):
        print(f"  {family}: {count}")

    print(f"\nOutput: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
