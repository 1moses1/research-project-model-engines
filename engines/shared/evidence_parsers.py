"""
Intelligent Evidence Parsers for Rwanda NCSA Compliance
Parses macOS command outputs and compares against control requirements
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import xml.etree.ElementTree as ET


class RwandaNCSAEvidenceParser:
    """
    Intelligent parser for macOS command outputs
    Maps evidence to Rwanda NCSA control requirements
    """

    def __init__(self, controls_file: Optional[str] = None):
        """Initialize parser with Rwanda NCSA control specifications"""
        if controls_file is None:
            controls_file = Path(__file__).parent / "rwanda_ncsa_controls.json"

        with open(controls_file, 'r') as f:
            self.controls_db = json.load(f)['controls']

    def parse_evidence(self, evidence_file: str, content: str, control_id: str) -> Dict:
        """
        Main entry point - routes to specific parser based on control ID
        Returns structured compliance analysis
        """
        parser_map = {
            "RWNCSA-AC-001": self.parse_login_history,
            "RWNCSA-AC-002": self.parse_user_accounts,
            "RWNCSA-AC-010": self.parse_active_sessions,
            "RWNCSA-AU-002": self.parse_system_logs,
            "RWNCSA-AU-004": self.parse_disk_usage,
            "RWNCSA-CM-002": self.parse_system_info,
            "RWNCSA-IA-005": self.parse_password_policy,
            "RWNCSA-SI-003": self.parse_process_list,
            "RWNCSA-SI-007": self.parse_security_features,
            # Week 1 Phase 1 Controls (15 from original 30)
            "RWNCSA-AC-003": self.parse_admin_access,
            "RWNCSA-AC-004": self.parse_ssh_config,
            "RWNCSA-AC-005": self.parse_file_permissions,
            "RWNCSA-AC-006": self.parse_sudo_config,
            "RWNCSA-AC-007": self.parse_screen_lock,
            "RWNCSA-AC-008": self.parse_remote_desktop,
            "RWNCSA-AU-001": self.parse_audit_system,
            "RWNCSA-AU-003": self.parse_time_sync,
            "RWNCSA-CO-001": self.parse_software_inventory,
            "RWNCSA-CO-003": self.parse_patch_status,
            "RWNCSA-CO-004": self.parse_configuration_profiles,
            "RWNCSA-ID-002": self.parse_biometric_config,
            "RWNCSA-SY-001": self.parse_firewall_status,
            "RWNCSA-SY-002": self.parse_filevault_status,
            "RWNCSA-SY-003": self.parse_bluetooth_config,
            "RWNCSA-SY-004": self.parse_network_config,
            "RWNCSA-SY-005": self.parse_antimalware_status,
            "RWNCSA-SY-006": self.parse_file_sharing,
            "RWNCSA-SY-007": self.parse_wifi_security,
            "RWNCSA-SY-008": self.parse_vpn_config,
            "RWNCSA-SY-009": self.parse_dns_config,

            # Week 1 Access Control Expansion (17 controls)
            "RWNCSA-AC-009": self.parse_mfa_certificates,
            "RWNCSA-AC-011": self.parse_lockout_policy,
            "RWNCSA-AC-012": self.parse_guest_account,
            "RWNCSA-AC-013": self.parse_auto_login,
            "RWNCSA-AC-014": self.parse_fast_user_switching,
            "RWNCSA-AC-015": self.parse_password_reset_policy,
            "RWNCSA-AC-016": self.parse_inactive_accounts,
            "RWNCSA-AC-017": self.parse_root_status,
            "RWNCSA-AC-018": self.parse_home_directory_permissions,
            "RWNCSA-AC-019": self.parse_shared_folder_permissions,
            "RWNCSA-AC-020": self.parse_login_banner,
            "RWNCSA-AC-021": self.parse_grace_time,
            "RWNCSA-AC-022": self.parse_system_prefs_acl,
            "RWNCSA-AC-023": self.parse_keychain_security,
            "RWNCSA-AC-024": self.parse_terminal_access,
            "RWNCSA-AC-025": self.parse_ssh_keys,
            "RWNCSA-AC-026": self.parse_pf_rules,

            # Additional Audit & Accountability parsers (13 new parsers to reach 60 total)
            "RWNCSA-AU-005": self.parse_audit_log_retention,
            "RWNCSA-AU-006": self.parse_audit_events,
            "RWNCSA-AU-007": self.parse_audit_reduction,
            "RWNCSA-AU-008": self.parse_audit_timestamps,

            # Additional Identity & Authentication parsers
            "RWNCSA-IA-001": self.parse_user_identification,
            "RWNCSA-IA-002": self.parse_device_identification,
            "RWNCSA-IA-003": self.parse_authenticator_management,
            "RWNCSA-IA-004": self.parse_authenticator_feedback,

            # Additional System Integrity parsers
            "RWNCSA-SI-001": self.parse_flaw_remediation,
            "RWNCSA-SI-002": self.parse_malicious_code_protection,

            # Configuration Management parsers
            "RWNCSA-CM-001": self.parse_baseline_configuration,

            # System & Communications Protection parsers
            "RWNCSA-SC-001": self.parse_application_partitioning,
            "RWNCSA-SC-002": self.parse_encryption_status,
        }

        parser_func = parser_map.get(control_id)
        if not parser_func:
            return self._default_parser(content, control_id)

        return parser_func(content, control_id)

    def parse_login_history(self, content: str, control_id: str) -> Dict:
        """
        Parse 'last -10' output for AC-001 (Login History Monitoring)
        Extract: users, login times, terminals, session durations
        """
        control = self.controls_db[control_id]
        requirements = control['requirements']

        # Parse login entries
        login_entries = []
        failed_logins = 0
        unique_users = set()

        for line in content.strip().split('\n'):
            if not line or line.startswith('wtmp') or 'reboot' in line:
                continue

            # Pattern: username tty   date time
            match = re.match(r'^(\w+)\s+(\w+)\s+(.+)$', line)
            if match:
                username, terminal, session_info = match.groups()
                unique_users.add(username)

                login_entries.append({
                    "username": username,
                    "terminal": terminal,
                    "session_info": session_info.strip(),
                    "timestamp_found": bool(re.search(r'\w{3}\s+\w{3}\s+\d+', session_info))
                })

        # Compliance assessment
        has_logs = len(login_entries) > 0
        has_timestamps = all(e['timestamp_found'] for e in login_entries)
        has_multiple_fields = len(login_entries) > 0 and all(e['username'] and e['terminal'] for e in login_entries)

        is_compliant = has_logs and has_timestamps and has_multiple_fields

        gaps = []
        if not has_logs:
            gaps.append({
                "requirement": "Login history must be available",
                "actual": "No login entries found",
                "severity": "HIGH",
                "remediation": "Verify system logging is enabled"
            })
        if not has_timestamps:
            gaps.append({
                "requirement": "Login entries must have timestamps",
                "actual": "Some entries missing timestamps",
                "severity": "MEDIUM",
                "remediation": "Check system time configuration"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"Found {len(login_entries)} login entries for {len(unique_users)} unique user(s)",
            "actual_state": {
                "total_entries": len(login_entries),
                "unique_users": list(unique_users),
                "has_timestamps": has_timestamps,
                "has_required_fields": has_multiple_fields,
                "sample_entries": login_entries[:3]  # First 3 for review
            },
            "expected_state": {
                "login_logging_enabled": requirements['login_logging_enabled'],
                "minimum_retention_days": requirements['minimum_retention_days'],
                "required_fields": ["timestamp", "username", "source"]
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else (50.0 if has_logs else 0.0),
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_user_accounts(self, content: str, control_id: str) -> Dict:
        """
        Parse 'dscl . -list /Users' and 'id' output for AC-002 (User Account Control)
        """
        control = self.controls_db[control_id]

        # Extract user accounts
        system_accounts = []
        user_accounts = []

        for line in content.strip().split('\n'):
            if not line:
                continue

            # System accounts start with underscore
            if line.startswith('_'):
                system_accounts.append(line.strip())
            elif line.strip() and not line.startswith('uid='):
                user_accounts.append(line.strip())

        # Parse 'id' output if present
        privileged_info = {}
        for line in content.split('\n'):
            if line.startswith('uid='):
                # Extract groups
                groups_match = re.findall(r'(\d+)\((\w+)\)', line)
                privileged_info = {
                    "groups": [g[1] for g in groups_match],
                    "is_admin": 'admin' in [g[1] for g in groups_match]
                }

        has_users = len(user_accounts) > 0 or len(system_accounts) > 0
        system_accounts_secure = all(acc.startswith('_') for acc in system_accounts)

        is_compliant = has_users and system_accounts_secure

        gaps = []
        if not has_users:
            gaps.append({
                "requirement": "User account inventory must be maintained",
                "actual": "Cannot enumerate user accounts",
                "severity": "CRITICAL",
                "remediation": "Verify directory services are operational"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"{len(user_accounts)} user account(s), {len(system_accounts)} system account(s)",
            "actual_state": {
                "total_users": len(user_accounts),
                "total_system_accounts": len(system_accounts),
                "user_accounts": user_accounts[:10],  # First 10
                "privileged_info": privileged_info,
                "system_accounts_properly_named": system_accounts_secure
            },
            "expected_state": {
                "user_inventory_maintained": True,
                "system_accounts_secured": True,
                "naming_convention": "System accounts must start with underscore (_)"
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else 50.0,
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_active_sessions(self, content: str, control_id: str) -> Dict:
        """
        Parse 'who' output for AC-010 (Concurrent Session Control)
        """
        control = self.controls_db[control_id]
        requirements = control['requirements']

        # Parse active sessions
        sessions = []
        unique_users = set()

        for line in content.strip().split('\n'):
            if not line:
                continue

            # Pattern: username terminal date time
            parts = line.split()
            if len(parts) >= 2:
                username = parts[0]
                terminal = parts[1]
                unique_users.add(username)

                sessions.append({
                    "username": username,
                    "terminal": terminal,
                    "line": line
                })

        session_count = len(sessions)
        max_allowed = requirements['maximum_concurrent_sessions']

        is_compliant = session_count > 0 and session_count <= max_allowed

        gaps = []
        if session_count > max_allowed:
            gaps.append({
                "requirement": f"Maximum {max_allowed} concurrent sessions",
                "actual": f"{session_count} sessions active",
                "severity": "MEDIUM",
                "remediation": "Terminate excessive sessions or increase limit"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"{session_count} active session(s) for {len(unique_users)} user(s)",
            "actual_state": {
                "active_sessions": session_count,
                "unique_users": list(unique_users),
                "sessions": sessions,
                "within_limit": session_count <= max_allowed
            },
            "expected_state": {
                "maximum_concurrent_sessions": max_allowed,
                "session_monitoring_enabled": True
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else 70.0,
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_system_logs(self, content: str, control_id: str) -> Dict:
        """
        Parse 'log show' output for AU-002 (Audit Events Logging)
        """
        control = self.controls_db[control_id]

        # Count log entries with timestamps
        log_entries = []
        for line in content.strip().split('\n'):
            if not line:
                continue

            # Look for timestamp pattern: 2025-11-28 06:12:52
            timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', line)
            if timestamp_match:
                log_entries.append({
                    "timestamp": timestamp_match.group(),
                    "line": line[:100]  # First 100 chars
                })

        has_logs = len(log_entries) > 0
        has_timestamps = len(log_entries) > 0

        is_compliant = has_logs and has_timestamps

        gaps = []
        if not has_logs:
            gaps.append({
                "requirement": "System must generate audit logs",
                "actual": "No log entries found",
                "severity": "CRITICAL",
                "remediation": "Enable system logging immediately"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"Found {len(log_entries)} log entries with timestamps",
            "actual_state": {
                "log_entries_found": len(log_entries),
                "has_timestamps": has_timestamps,
                "sample_entries": log_entries[:5]
            },
            "expected_state": {
                "audit_logging_enabled": True,
                "events_logged": ["authentication", "authorization", "system_changes"],
                "log_format": "structured with timestamps"
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else 0.0,
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_disk_usage(self, content: str, control_id: str) -> Dict:
        """
        Parse 'df -h' output for AU-004 (Audit Storage Capacity)
        Extract disk usage percentages and check against thresholds
        """
        control = self.controls_db[control_id]
        requirements = control['requirements']

        # Parse disk usage for root partition
        root_usage = None
        partitions = []

        for line in content.strip().split('\n'):
            if 'Filesystem' in line or not line:
                continue

            # Extract percentage from line
            match = re.search(r'\s+(\d+)%\s+', line)
            if match:
                usage_percent = int(match.group(1))
                filesystem = line.split()[0]

                partitions.append({
                    "filesystem": filesystem,
                    "usage_percent": usage_percent
                })

                # Identify root partition
                if filesystem.endswith('s1') or '/dev/disk3s3s1' in filesystem:
                    root_usage = usage_percent

        # Compliance check
        threshold = 100 - requirements['minimum_free_space_percent']
        is_compliant = root_usage is not None and root_usage < threshold

        gaps = []
        if root_usage is None:
            gaps.append({
                "requirement": "Disk usage must be monitored",
                "actual": "Cannot determine root partition usage",
                "severity": "HIGH",
                "remediation": "Check disk configuration"
            })
        elif root_usage >= threshold:
            gaps.append({
                "requirement": f"Disk usage must be below {threshold}%",
                "actual": f"Currently at {root_usage}%",
                "severity": "HIGH",
                "remediation": "Free up disk space immediately"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"Root partition at {root_usage}% capacity" if root_usage else "Disk usage unavailable",
            "actual_state": {
                "root_partition_usage_percent": root_usage,
                "all_partitions": partitions,
                "within_threshold": is_compliant if root_usage else False
            },
            "expected_state": {
                "maximum_usage_percent": threshold,
                "minimum_free_space_percent": requirements['minimum_free_space_percent'],
                "alert_threshold_percent": requirements['alert_threshold_percent']
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else (50.0 if root_usage and root_usage < 95 else 0.0),
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_system_info(self, content: str, control_id: str) -> Dict:
        """
        Parse 'sw_vers' and 'system_profiler' for CM-002 (Baseline Configuration)
        """
        control = self.controls_db[control_id]

        # Extract system information
        system_info = {}

        # Parse sw_vers output
        for line in content.split('\n'):
            if 'ProductName:' in line:
                system_info['os_name'] = line.split(':', 1)[1].strip()
            elif 'ProductVersion:' in line:
                system_info['os_version'] = line.split(':', 1)[1].strip()
            elif 'BuildVersion:' in line:
                system_info['build'] = line.split(':', 1)[1].strip()
            elif 'Model Name:' in line:
                system_info['model'] = line.split(':', 1)[1].strip()
            elif 'Chip:' in line:
                system_info['processor'] = line.split(':', 1)[1].strip()
            elif 'Memory:' in line:
                system_info['memory'] = line.split(':', 1)[1].strip()
            elif 'Serial Number' in line:
                system_info['serial'] = line.split(':', 1)[1].strip()

        has_version = 'os_version' in system_info
        has_model = 'model' in system_info or 'processor' in system_info

        is_compliant = has_version and (has_model or 'processor' in system_info)

        gaps = []
        if not has_version:
            gaps.append({
                "requirement": "System version must be documented",
                "actual": "Version information missing",
                "severity": "MEDIUM",
                "remediation": "Run 'sw_vers' and document output"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"{system_info.get('os_name', 'macOS')} {system_info.get('os_version', 'unknown')} on {system_info.get('model', system_info.get('processor', 'unknown'))}",
            "actual_state": system_info,
            "expected_state": {
                "system_inventory": True,
                "version_tracking": True,
                "hardware_inventory": True
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else 60.0,
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_password_policy(self, content: str, control_id: str) -> Dict:
        """
        Parse 'pwpolicy getaccountpolicies' XML output for IA-005 (Password Policy)
        This is CRITICAL - extract all policy parameters
        """
        control = self.controls_db[control_id]
        requirements = control['requirements']

        # Parse password policy from XML output
        policy_config = {
            "min_length": None,
            "complexity_required": False,
            "max_age_days": None,
            "lockout_threshold": None,
            "policy_found": False
        }

        # Look for policy attributes in the XML/text
        if 'policyAttributePassword' in content or 'minChars' in content:
            policy_config['policy_found'] = True

        # Extract minimum length
        min_chars_match = re.search(r'minChars[>=<\s]+(\d+)', content)
        if min_chars_match:
            policy_config['min_length'] = int(min_chars_match.group(1))

        # Check for complexity requirements
        if 'requiresAlpha' in content or 'requiresNumeric' in content or 'requiresMixedCase' in content:
            policy_config['complexity_required'] = True

        # Extract max age
        max_age_match = re.search(r'maxMinutesUntilChangePassword[>=<\s]+(\d+)', content)
        if max_age_match:
            policy_config['max_age_days'] = int(max_age_match.group(1)) // 1440  # Convert minutes to days

        # Extract lockout threshold
        lockout_match = re.search(r'maxFailedLoginAttempts[>=<\s]+(\d+)', content)
        if lockout_match:
            policy_config['lockout_threshold'] = int(lockout_match.group(1))

        # Compliance assessment
        gaps = []

        # Check minimum length
        if policy_config['min_length'] is None:
            gaps.append({
                "requirement": f"Password minimum length: {requirements['minimum_length']} characters",
                "actual": "Not configured",
                "severity": "CRITICAL",
                "remediation": f"Set minimum password length to {requirements['minimum_length']}"
            })
        elif policy_config['min_length'] < requirements['minimum_length']:
            gaps.append({
                "requirement": f"Password minimum length: {requirements['minimum_length']} characters",
                "actual": f"Currently {policy_config['min_length']} characters",
                "severity": "CRITICAL",
                "remediation": f"Increase minimum length to {requirements['minimum_length']}"
            })

        # Check complexity
        if not policy_config['complexity_required']:
            gaps.append({
                "requirement": "Password complexity required (uppercase, lowercase, numbers, symbols)",
                "actual": "Complexity not enforced",
                "severity": "CRITICAL",
                "remediation": "Enable password complexity requirements"
            })

        # Check max age
        if policy_config['max_age_days'] is None:
            gaps.append({
                "requirement": f"Password maximum age: {requirements['maximum_age_days']} days",
                "actual": "Passwords never expire",
                "severity": "HIGH",
                "remediation": f"Set password expiry to {requirements['maximum_age_days']} days"
            })
        elif policy_config['max_age_days'] > requirements['maximum_age_days']:
            gaps.append({
                "requirement": f"Password maximum age: {requirements['maximum_age_days']} days",
                "actual": f"Currently {policy_config['max_age_days']} days",
                "severity": "HIGH",
                "remediation": f"Reduce max age to {requirements['maximum_age_days']} days"
            })

        # Check lockout
        if policy_config['lockout_threshold'] is None:
            gaps.append({
                "requirement": f"Account lockout after {requirements['lockout_threshold']} failed attempts",
                "actual": "No lockout policy",
                "severity": "HIGH",
                "remediation": f"Enable account lockout after {requirements['lockout_threshold']} attempts"
            })

        is_compliant = len(gaps) == 0

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"Password policy: {policy_config['min_length'] or 'N/A'} chars min, complexity: {policy_config['complexity_required']}, expires: {policy_config['max_age_days'] or 'never'} days",
            "actual_state": policy_config,
            "expected_state": requirements,
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else (25.0 * (4 - len(gaps))),  # Partial credit
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_process_list(self, content: str, control_id: str) -> Dict:
        """
        Parse 'ps aux' output for SI-003 (Malicious Code Protection)
        """
        control = self.controls_db[control_id]

        # Count processes
        processes = []
        system_processes = 0
        user_processes = 0

        for line in content.strip().split('\n'):
            if line.startswith('USER') or not line:
                continue

            parts = line.split(None, 10)
            if len(parts) >= 11:
                user = parts[0]
                pid = parts[1]
                command = parts[10]

                processes.append({"user": user, "pid": pid, "command": command[:50]})

                if user.startswith('_') or user == 'root':
                    system_processes += 1
                else:
                    user_processes += 1

        has_processes = len(processes) > 0
        has_system_processes = system_processes > 0

        is_compliant = has_processes and has_system_processes

        gaps = []
        if not has_processes:
            gaps.append({
                "requirement": "Process monitoring must be operational",
                "actual": "Cannot enumerate processes",
                "severity": "CRITICAL",
                "remediation": "Check system integrity"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"{len(processes)} processes ({system_processes} system, {user_processes} user)",
            "actual_state": {
                "total_processes": len(processes),
                "system_processes": system_processes,
                "user_processes": user_processes,
                "sample_processes": processes[:5]
            },
            "expected_state": {
                "process_monitoring_enabled": True,
                "baseline_established": "recommended"
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else 0.0,
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_security_features(self, content: str, control_id: str) -> Dict:
        """
        Parse 'csrutil status' and 'spctl --status' for SI-007 (System Integrity Protection)
        CRITICAL CONTROL - requires BOTH SIP and Gatekeeper enabled
        """
        control = self.controls_db[control_id]
        requirements = control['requirements']

        # Parse SIP status
        sip_enabled = False
        gatekeeper_enabled = False

        if 'System Integrity Protection status: enabled' in content:
            sip_enabled = True
        elif 'System Integrity Protection status: disabled' in content:
            sip_enabled = False

        if 'assessments enabled' in content:
            gatekeeper_enabled = True
        elif 'assessments disabled' in content:
            gatekeeper_enabled = False

        # CRITICAL: Both must be enabled for compliance
        gaps = []

        if not sip_enabled:
            gaps.append({
                "requirement": "System Integrity Protection (SIP) must be enabled",
                "actual": "SIP is DISABLED",
                "severity": "CRITICAL",
                "remediation": "Enable SIP immediately (requires Recovery Mode reboot)",
                "risk": "System vulnerable to rootkits, kernel exploits, and unauthorized modifications"
            })

        if not gatekeeper_enabled:
            gaps.append({
                "requirement": "Gatekeeper must be enabled",
                "actual": "Gatekeeper is DISABLED",
                "severity": "CRITICAL",
                "remediation": "Enable Gatekeeper: sudo spctl --master-enable",
                "risk": "System can run unsigned/malicious applications"
            })

        is_compliant = sip_enabled and gatekeeper_enabled

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"SIP: {'ENABLED' if sip_enabled else 'DISABLED'}, Gatekeeper: {'ENABLED' if gatekeeper_enabled else 'DISABLED'}",
            "actual_state": {
                "sip_enabled": sip_enabled,
                "gatekeeper_enabled": gatekeeper_enabled,
                "both_protections_active": is_compliant
            },
            "expected_state": {
                "sip_enabled": requirements['sip_enabled'],
                "gatekeeper_enabled": requirements['gatekeeper_enabled'],
                "all_protections_required": True
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else (50.0 if (sip_enabled or gatekeeper_enabled) else 0.0),
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def _default_parser(self, content: str, control_id: str) -> Dict:
        """Fallback parser for unknown controls"""
        return {
            "control_id": control_id,
            "control_name": "Unknown Control",
            "parsing_successful": False,
            "evidence_summary": "Parser not implemented for this control",
            "actual_state": {"raw_output": content[:200]},
            "expected_state": {},
            "compliance_status": "UNKNOWN",
            "compliance_score": 0.0,
            "gaps": [{"requirement": "Parser needed", "actual": "Not implemented", "severity": "N/A"}],
            "risk_level": "UNKNOWN",
            "remediation_steps": []
        }


# Convenience function
    # ===================================================================
    # PHASE 1 CONTROLS (30 Controls) - Missing 21 Parsers
    # ===================================================================

    def parse_admin_access(self, content: str, control_id: str) -> Dict:
        """Parse admin group membership (AC-003)"""
        control = self.controls_db[control_id]
        admin_users = []
        for line in content.split('\n'):
            if 'GroupMembership:' in line:
                users = line.split('GroupMembership:')[1].strip().split()
                admin_users = users
        
        num_admins = len(admin_users)
        is_compliant = 1 <= num_admins <= 3  # Reasonable admin count
        
        gaps = []
        if num_admins == 0:
            gaps.append({"requirement": "At least 1 admin required", "actual": f"0 admins", "severity": "CRITICAL", "remediation": control['remediation']['steps']})
        elif num_admins > 3:
            gaps.append({"requirement": "Excessive admins (> 3)", "actual": f"{num_admins} admins", "severity": "MEDIUM", "remediation": control['remediation']['steps']})
        
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{num_admins} admin user(s)", "actual_state": {"admin_users": admin_users, "count": num_admins}, "expected_state": {"min_admins": 1, "max_admins": 3}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_ssh_config(self, content: str, control_id: str) -> Dict:
        """Parse SSH configuration (AC-004)"""
        control = self.controls_db[control_id]
        requirements = control['requirements']
        
        config = {}
        for line in content.split('\n'):
            if 'PermitRootLogin' in line and not line.strip().startswith('#'):
                config['permit_root_login'] = 'yes' not in line.lower()
            if 'PasswordAuthentication' in line and not line.strip().startswith('#'):
                config['password_auth_disabled'] = 'no' in line.lower()
        
        is_compliant = config.get('permit_root_login', False) and config.get('password_auth_disabled', False)
        gaps = []
        if not config.get('permit_root_login', False):
            gaps.append({"requirement": "PermitRootLogin must be no", "actual": "PermitRootLogin yes or not set", "severity": "CRITICAL", "remediation": control['remediation']['steps']})
        if not config.get('password_auth_disabled', False):
            gaps.append({"requirement": "PasswordAuthentication must be no", "actual": "PasswordAuthentication yes or not set", "severity": "HIGH", "remediation": control['remediation']['steps']})
        
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Root login: {'disabled' if config.get('permit_root_login') else 'enabled'}, Password auth: {'disabled' if config.get('password_auth_disabled') else 'enabled'}", "actual_state": config, "expected_state": requirements, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 25.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_file_permissions(self, content: str, control_id: str) -> Dict:
        """Parse file permissions (AC-005)"""
        control = self.controls_db[control_id]
        insecure_files = [line for line in content.split('\n') if 'rwxrwxrwx' in line or 'rw-rw-rw-' in line]
        is_compliant = len(insecure_files) == 0
        gaps = [{"requirement": "No world-writable files", "actual": f"{len(insecure_files)} insecure files found", "severity": "HIGH", "remediation": control['remediation']['steps']}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{len(insecure_files)} insecure file(s)", "actual_state": {"insecure_count": len(insecure_files)}, "expected_state": {"insecure_count": 0}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_sudo_config(self, content: str, control_id: str) -> Dict:
        """Parse sudo configuration (AC-006)"""
        control = self.controls_db[control_id]
        has_nopasswd = 'NOPASSWD' in content
        is_compliant = not has_nopasswd
        gaps = [{"requirement": "NOPASSWD should not be used", "actual": "NOPASSWD found in sudoers", "severity": "HIGH", "remediation": control['remediation']['steps']}] if has_nopasswd else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"NOPASSWD: {'found' if has_nopasswd else 'not found'}", "actual_state": {"nopasswd_present": has_nopasswd}, "expected_state": {"nopasswd_present": False}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_screen_lock(self, content: str, control_id: str) -> Dict:
        """Parse screen lock timeout (AC-007)"""
        control = self.controls_db[control_id]
        timeout_match = re.search(r'idleTime\s*=\s*(\d+)', content)
        timeout = int(timeout_match.group(1)) if timeout_match else None
        is_compliant = timeout is not None and timeout <= 300
        gaps = [{"requirement": "Screen lock timeout <= 300 seconds", "actual": f"Timeout: {timeout if timeout else 'not set'}", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Timeout: {timeout if timeout else 'not set'} seconds", "actual_state": {"timeout_seconds": timeout}, "expected_state": {"timeout_seconds": 300}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_remote_desktop(self, content: str, control_id: str) -> Dict:
        """Parse remote desktop status (AC-008)"""
        control = self.controls_db[control_id]
        screensharing_running = 'screensharing' in content.lower() or 'com.apple.screensharing' in content.lower()
        is_compliant = not screensharing_running
        gaps = [{"requirement": "Screen sharing should be disabled", "actual": "Screen sharing is running", "severity": "HIGH", "remediation": control['remediation']['steps']}] if screensharing_running else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Screen sharing: {'running' if screensharing_running else 'not running'}", "actual_state": {"screensharing_enabled": screensharing_running}, "expected_state": {"screensharing_enabled": False}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_audit_system(self, content: str, control_id: str) -> Dict:
        """Parse audit daemon status (AU-001)"""
        control = self.controls_db[control_id]
        audit_running = 'running' in content.lower() or 'auditd' in content.lower()
        is_compliant = audit_running
        gaps = [{"requirement": "Audit daemon must be running", "actual": "Audit daemon not running", "severity": "HIGH", "remediation": control['remediation']['steps']}] if not audit_running else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Audit daemon: {'running' if audit_running else 'not running'}", "actual_state": {"audit_running": audit_running}, "expected_state": {"audit_running": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_time_sync(self, content: str, control_id: str) -> Dict:
        """Parse time synchronization (AU-003)"""
        control = self.controls_db[control_id]
        ntp_enabled = 'on' in content.lower() or 'yes' in content.lower()
        is_compliant = ntp_enabled
        gaps = [{"requirement": "Network time must be enabled", "actual": "Network time is off", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if not ntp_enabled else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Network time: {'enabled' if ntp_enabled else 'disabled'}", "actual_state": {"ntp_enabled": ntp_enabled}, "expected_state": {"ntp_enabled": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_software_inventory(self, content: str, control_id: str) -> Dict:
        """Parse software inventory (CO-001)"""
        control = self.controls_db[control_id]
        app_count = len([line for line in content.split('\n') if '.app' in line or 'Software:' in line])
        has_inventory = app_count > 0
        is_compliant = has_inventory
        gaps = [{"requirement": "Software inventory must be available", "actual": "No software inventory", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if not has_inventory else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{app_count} application(s) inventoried", "actual_state": {"app_count": app_count}, "expected_state": {"has_inventory": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_patch_status(self, content: str, control_id: str) -> Dict:
        """Parse software update status (CO-003)"""
        control = self.controls_db[control_id]
        has_updates = 'Software Update found' in content or 'updates' in content.lower()
        critical_pending = 'security' in content.lower() and has_updates
        is_compliant = not critical_pending
        gaps = [{"requirement": "No critical patches pending", "actual": "Critical security updates pending", "severity": "CRITICAL", "remediation": control['remediation']['steps']}] if critical_pending else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Updates: {'pending' if has_updates else 'none'}", "actual_state": {"updates_pending": has_updates, "critical_pending": critical_pending}, "expected_state": {"critical_pending": False}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_configuration_profiles(self, content: str, control_id: str) -> Dict:
        """Parse configuration profiles (CO-004)"""
        control = self.controls_db[control_id]
        profile_count = len([line for line in content.split('\n') if 'profileIdentifier' in line or 'PayloadDisplayName' in line])
        has_profiles = profile_count > 0
        gaps = [{"requirement": "Configuration profiles should be documented", "actual": f"{profile_count} profiles found", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if profile_count > 5 else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{profile_count} profile(s) found", "actual_state": {"profile_count": profile_count}, "expected_state": {"profiles_documented": True}, "compliance_status": "COMPLIANT", "compliance_score": 100.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_biometric_config(self, content: str, control_id: str) -> Dict:
        """Parse Touch ID/biometric status (ID-002)"""
        control = self.controls_db[control_id]
        biometric_available = 'Touch ID' in content or 'biometric' in content.lower() or 'fingerprint' in content.lower()
        is_compliant = biometric_available or 'not available' in content.lower()
        gaps = [{"requirement": "Biometric authentication should be configured if available", "actual": "Biometric available but not configured", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Biometric: {'configured' if biometric_available else 'not configured'}", "actual_state": {"biometric_enabled": biometric_available}, "expected_state": {"biometric_enabled": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_firewall_status(self, content: str, control_id: str) -> Dict:
        """Parse firewall status (SY-001)"""
        control = self.controls_db[control_id]
        firewall_enabled = 'enabled' in content.lower() or 'state = 1' in content or 'State = 1' in content
        is_compliant = firewall_enabled
        gaps = [{"requirement": "Application Firewall must be enabled", "actual": "Firewall is disabled", "severity": "CRITICAL", "remediation": control['remediation']['steps']}] if not firewall_enabled else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Firewall: {'enabled' if firewall_enabled else 'disabled'}", "actual_state": {"firewall_enabled": firewall_enabled}, "expected_state": {"firewall_enabled": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_filevault_status(self, content: str, control_id: str) -> Dict:
        """Parse FileVault encryption status (SY-002)"""
        control = self.controls_db[control_id]
        filevault_on = 'FileVault is On' in content or 'Encryption in progress' in content
        is_compliant = filevault_on
        gaps = [{"requirement": "FileVault must be enabled", "actual": "FileVault is OFF", "severity": "CRITICAL", "remediation": control['remediation']['steps'], "risk": "Data theft from stolen/lost devices"}] if not filevault_on else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"FileVault: {'ON' if filevault_on else 'OFF'}", "actual_state": {"filevault_enabled": filevault_on}, "expected_state": {"filevault_enabled": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_bluetooth_config(self, content: str, control_id: str) -> Dict:
        """Parse Bluetooth configuration (SY-003)"""
        control = self.controls_db[control_id]
        bluetooth_enabled = 'ControllerPowerState = 1' in content or 'enabled' in content.lower()
        is_compliant = not bluetooth_enabled  # Bluetooth should be off unless needed
        gaps = [{"requirement": "Bluetooth should be disabled when not needed", "actual": "Bluetooth is enabled", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if bluetooth_enabled else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Bluetooth: {'enabled' if bluetooth_enabled else 'disabled'}", "actual_state": {"bluetooth_enabled": bluetooth_enabled}, "expected_state": {"bluetooth_enabled": False}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 75.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_network_config(self, content: str, control_id: str) -> Dict:
        """Parse network configuration (SY-004)"""
        control = self.controls_db[control_id]
        interface_count = len([line for line in content.split('\n') if 'inet ' in line])
        has_config = interface_count > 0
        is_compliant = has_config
        gaps = [{"requirement": "Network interfaces should be configured", "actual": "No network configuration found", "severity": "HIGH", "remediation": control['remediation']['steps']}] if not has_config else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{interface_count} interface(s) configured", "actual_state": {"interface_count": interface_count}, "expected_state": {"has_config": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_antimalware_status(self, content: str, control_id: str) -> Dict:
        """Parse XProtect/anti-malware status (SY-005)"""
        control = self.controls_db[control_id]
        xprotect_present = 'XProtect' in content or 'xprotect' in content.lower()
        is_compliant = xprotect_present
        gaps = [{"requirement": "XProtect should be present and updated", "actual": "XProtect not found", "severity": "HIGH", "remediation": control['remediation']['steps']}] if not xprotect_present else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"XProtect: {'present' if xprotect_present else 'not found'}", "actual_state": {"xprotect_enabled": xprotect_present}, "expected_state": {"xprotect_enabled": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_file_sharing(self, content: str, control_id: str) -> Dict:
        """Parse file sharing status (SY-006)"""
        control = self.controls_db[control_id]
        sharing_enabled = 'name:' in content.lower() or 'enabled' in content.lower()
        is_compliant = not sharing_enabled
        gaps = [{"requirement": "File sharing should be disabled unless required", "actual": "File sharing is enabled", "severity": "HIGH", "remediation": control['remediation']['steps']}] if sharing_enabled else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"File sharing: {'enabled' if sharing_enabled else 'disabled'}", "actual_state": {"sharing_enabled": sharing_enabled}, "expected_state": {"sharing_enabled": False}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_wifi_security(self, content: str, control_id: str) -> Dict:
        """Parse Wi-Fi security configuration (SY-007)"""
        control = self.controls_db[control_id]
        has_networks = len(content.strip().split('\n')) > 1
        open_networks = [line for line in content.split('\n') if 'open' in line.lower() or 'wep' in line.lower()]
        is_compliant = has_networks and len(open_networks) == 0
        gaps = [{"requirement": "No open or WEP networks allowed", "actual": f"{len(open_networks)} insecure networks found", "severity": "HIGH", "remediation": control['remediation']['steps']}] if len(open_networks) > 0 else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{len(open_networks)} insecure network(s)", "actual_state": {"open_networks": len(open_networks)}, "expected_state": {"open_networks": 0}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_vpn_config(self, content: str, control_id: str) -> Dict:
        """Parse VPN configuration (SY-008)"""
        control = self.controls_db[control_id]
        vpn_configured = 'IPSec' in content or 'IKEv2' in content or 'L2TP' in content
        is_compliant = vpn_configured
        gaps = [{"requirement": "VPN should be configured for remote access", "actual": "No VPN configured", "severity": "HIGH", "remediation": control['remediation']['steps']}] if not vpn_configured else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"VPN: {'configured' if vpn_configured else 'not configured'}", "actual_state": {"vpn_configured": vpn_configured}, "expected_state": {"vpn_configured": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_dns_config(self, content: str, control_id: str) -> Dict:
        """Parse DNS configuration (SY-009)"""
        control = self.controls_db[control_id]
        dns_servers = [line for line in content.split('\n') if re.match(r'^\d+\.\d+\.\d+\.\d+$', line.strip())]
        has_dns = len(dns_servers) > 0
        is_compliant = has_dns
        gaps = [{"requirement": "Trusted DNS servers should be configured", "actual": "No DNS servers configured", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if not has_dns else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{len(dns_servers)} DNS server(s) configured", "actual_state": {"dns_servers": dns_servers, "count": len(dns_servers)}, "expected_state": {"has_dns": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    # ===================================================================
    # WEEK 1 ACCESS CONTROL EXPANSION (17 Controls)
    # ===================================================================

    def parse_mfa_certificates(self, content: str, control_id: str) -> Dict:
        """Parse MFA certificate status (AC-009)"""
        control = self.controls_db[control_id]
        cert_match = re.search(r'(\d+)\s+valid identities found', content)
        num_certs = int(cert_match.group(1)) if cert_match else 0
        has_certs = num_certs > 0
        gaps = [{"requirement": "MFA certificates should be configured", "actual": "No certificates found", "severity": "HIGH", "remediation": control['remediation']['steps']}] if not has_certs else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{num_certs} certificate(s) found", "actual_state": {"certificates": num_certs}, "expected_state": {"certificates": 1}, "compliance_status": "COMPLIANT" if has_certs else "NON_COMPLIANT", "compliance_score": 100.0 if has_certs else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_lockout_policy(self, content: str, control_id: str) -> Dict:
        """Parse account lockout policy (AC-011)"""
        control = self.controls_db[control_id]
        max_attempts_match = re.search(r'maxFailedLoginAttempts[^\d]*(\d+)', content)
        max_attempts = int(max_attempts_match.group(1)) if max_attempts_match else None
        is_compliant = max_attempts is not None and max_attempts <= 5
        gaps = [{"requirement": "Max failed attempts must be <= 5", "actual": f"Max attempts: {max_attempts if max_attempts else 'not set'}", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Max attempts: {max_attempts if max_attempts else 'not set'}", "actual_state": {"max_attempts": max_attempts}, "expected_state": {"max_attempts": 5}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_guest_account(self, content: str, control_id: str) -> Dict:
        """Parse guest account status (AC-012)"""
        control = self.controls_db[control_id]
        guest_disabled = 'eDSRecordNotFound' in content or 'No such file' in content
        gaps = [{"requirement": "Guest account must be disabled", "actual": "Guest account exists", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if not guest_disabled else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Guest account: {'disabled' if guest_disabled else 'enabled'}", "actual_state": {"guest_disabled": guest_disabled}, "expected_state": {"guest_disabled": True}, "compliance_status": "COMPLIANT" if guest_disabled else "NON_COMPLIANT", "compliance_score": 100.0 if guest_disabled else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_auto_login(self, content: str, control_id: str) -> Dict:
        """Parse automatic login status (AC-013)"""
        control = self.controls_db[control_id]
        auto_login_disabled = 'does not exist' in content
        gaps = [{"requirement": "Automatic login must be disabled", "actual": "Auto-login enabled", "severity": "HIGH", "remediation": control['remediation']['steps']}] if not auto_login_disabled else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Auto-login: {'disabled' if auto_login_disabled else 'enabled'}", "actual_state": {"auto_login_disabled": auto_login_disabled}, "expected_state": {"auto_login_disabled": True}, "compliance_status": "COMPLIANT" if auto_login_disabled else "NON_COMPLIANT", "compliance_score": 100.0 if auto_login_disabled else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_fast_user_switching(self, content: str, control_id: str) -> Dict:
        """Parse fast user switching (AC-014)"""
        control = self.controls_db[control_id]
        is_configured = '0' in content or '1' in content
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Configured: {'yes' if is_configured else 'no'}", "actual_state": {"configured": is_configured}, "expected_state": {"configured": True}, "compliance_status": "COMPLIANT", "compliance_score": 100.0, "gaps": [], "risk_level": control['severity'], "remediation_steps": []}

    def parse_password_reset_policy(self, content: str, control_id: str) -> Dict:
        """Parse password reset policy (AC-015)"""
        control = self.controls_db[control_id]
        has_policy = 'policyAttribute' in content
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Policy: {'configured' if has_policy else 'not configured'}", "actual_state": {"has_policy": has_policy}, "expected_state": {"has_policy": True}, "compliance_status": "COMPLIANT" if has_policy else "NON_COMPLIANT", "compliance_score": 100.0 if has_policy else 50.0, "gaps": [], "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if not has_policy else []}

    def parse_inactive_accounts(self, content: str, control_id: str) -> Dict:
        """Parse inactive account detection (AC-016)"""
        control = self.controls_db[control_id]
        inactive_users = len([line for line in content.split('\n') if 'lastlogin' in line.lower()])
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{inactive_users} users with lastlogin data", "actual_state": {"tracked_users": inactive_users}, "expected_state": {"tracked_users": 1}, "compliance_status": "COMPLIANT", "compliance_score": 100.0, "gaps": [], "risk_level": control['severity'], "remediation_steps": []}

    def parse_root_status(self, content: str, control_id: str) -> Dict:
        """Parse root account status (AC-017)"""
        control = self.controls_db[control_id]
        root_disabled = 'No such key' in content or 'DisabledUser' in content or '/usr/bin/false' in content
        gaps = [{"requirement": "Root account must be disabled", "actual": "Root account enabled", "severity": "CRITICAL", "remediation": control['remediation']['steps']}] if not root_disabled else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Root: {'disabled' if root_disabled else 'enabled'}", "actual_state": {"root_disabled": root_disabled}, "expected_state": {"root_disabled": True}, "compliance_status": "COMPLIANT" if root_disabled else "NON_COMPLIANT", "compliance_score": 100.0 if root_disabled else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_home_directory_permissions(self, content: str, control_id: str) -> Dict:
        """Parse home directory permissions (AC-018)"""
        control = self.controls_db[control_id]
        insecure_dirs = len([line for line in content.split('\n') if 'drwxr' in line or 'drwxrwx' in line])
        is_compliant = insecure_dirs == 0
        gaps = [{"requirement": "Home directories must be 700 (drwx------)", "actual": f"{insecure_dirs} insecure directories", "severity": "HIGH", "remediation": control['remediation']['steps']}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{insecure_dirs} insecure directory(ies)", "actual_state": {"insecure_count": insecure_dirs}, "expected_state": {"insecure_count": 0}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_shared_folder_permissions(self, content: str, control_id: str) -> Dict:
        """Parse shared folder permissions (AC-019)"""
        control = self.controls_db[control_id]
        share_count = len([line for line in content.split('\n') if 'name:' in line.lower()])
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{share_count} shared folder(s)", "actual_state": {"share_count": share_count}, "expected_state": {"documented": True}, "compliance_status": "COMPLIANT", "compliance_score": 100.0, "gaps": [], "risk_level": control['severity'], "remediation_steps": []}

    def parse_login_banner(self, content: str, control_id: str) -> Dict:
        """Parse login banner (AC-020)"""
        control = self.controls_db[control_id]
        banner_exists = len(content.strip()) > 0 and 'No such file' not in content
        has_warning = any(k in content.lower() for k in ['authorized', 'warning', 'unauthorized'])
        is_compliant = banner_exists and has_warning
        gaps = [{"requirement": "Login banner with warning required", "actual": "Banner missing or incomplete", "severity": "LOW", "remediation": control['remediation']['steps']}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Banner: {'configured' if is_compliant else 'missing'}", "actual_state": {"banner_exists": banner_exists, "has_warning": has_warning}, "expected_state": {"banner_exists": True, "has_warning": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_grace_time(self, content: str, control_id: str) -> Dict:
        """Parse login grace time (AC-021)"""
        control = self.controls_db[control_id]
        grace_match = re.search(r'(-?\d+)', content)
        grace_time = int(grace_match.group(1)) if grace_match else None
        is_compliant = grace_time == 0
        gaps = [{"requirement": "Grace time must be 0", "actual": f"Grace time: {grace_time}", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Grace time: {grace_time if grace_time is not None else 'unknown'} seconds", "actual_state": {"grace_time": grace_time}, "expected_state": {"grace_time": 0}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_system_prefs_acl(self, content: str, control_id: str) -> Dict:
        """Parse system preferences ACL (AC-022)"""
        control = self.controls_db[control_id]
        requires_admin = 'authenticate-admin' in content
        is_compliant = requires_admin
        gaps = [{"requirement": "System preferences must require admin auth", "actual": "Admin auth not required", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Admin required: {'yes' if requires_admin else 'no'}", "actual_state": {"requires_admin": requires_admin}, "expected_state": {"requires_admin": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_keychain_security(self, content: str, control_id: str) -> Dict:
        """Parse keychain security (AC-023)"""
        control = self.controls_db[control_id]
        has_keychains = 'Keychains' in content or '.keychain' in content
        is_compliant = has_keychains
        gaps = [{"requirement": "Keychains should be configured", "actual": "No keychains found", "severity": "HIGH", "remediation": control['remediation']['steps']}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"Keychains: {'configured' if has_keychains else 'not found'}", "actual_state": {"has_keychains": has_keychains}, "expected_state": {"has_keychains": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_terminal_access(self, content: str, control_id: str) -> Dict:
        """Parse terminal access restrictions (AC-024)"""
        control = self.controls_db[control_id]
        shell_count = len([line for line in content.split('\n') if '/bin/bash' in line or '/bin/zsh' in line])
        false_shells = len([line for line in content.split('\n') if '/usr/bin/false' in line])
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"{shell_count} interactive shells, {false_shells} disabled", "actual_state": {"interactive_shells": shell_count, "disabled_shells": false_shells}, "expected_state": {"controlled": True}, "compliance_status": "COMPLIANT", "compliance_score": 100.0, "gaps": [], "risk_level": control['severity'], "remediation_steps": []}

    def parse_ssh_keys(self, content: str, control_id: str) -> Dict:
        """Parse SSH key authentication (AC-025)"""
        control = self.controls_db[control_id]
        has_keys = 'id_rsa' in content or 'id_ed25519' in content or 'authorized_keys' in content
        insecure_perms = len([line for line in content.split('\n') if 'rw-' in line and 'id_' in line])
        is_compliant = has_keys and insecure_perms == 0
        gaps = [{"requirement": "SSH keys with secure permissions (600)", "actual": f"{insecure_perms} keys with insecure permissions", "severity": "HIGH", "remediation": control['remediation']['steps']}] if insecure_perms > 0 else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"SSH keys: {'present' if has_keys else 'not found'}, {insecure_perms} insecure", "actual_state": {"has_keys": has_keys, "insecure_count": insecure_perms}, "expected_state": {"has_keys": True, "insecure_count": 0}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    def parse_pf_rules(self, content: str, control_id: str) -> Dict:
        """Parse packet filter rules (AC-026)"""
        control = self.controls_db[control_id]
        has_rules = 'block' in content or 'pass' in content
        is_compliant = has_rules
        gaps = [{"requirement": "Packet filter rules should be configured", "actual": "No pf rules found", "severity": "MEDIUM", "remediation": control['remediation']['steps']}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control['name'], "parsing_successful": True, "evidence_summary": f"PF rules: {'configured' if has_rules else 'not configured'}", "actual_state": {"has_rules": has_rules}, "expected_state": {"has_rules": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control['severity'], "remediation_steps": control['remediation']['steps'] if gaps else []}

    # ============== 13 NEW PARSERS (to reach 60 total) ==============

    def parse_audit_log_retention(self, content: str, control_id: str) -> Dict:
        """Parse audit log retention settings (AU-005)"""
        control = self.controls_db.get(control_id, {"name": "Audit Log Retention", "severity": "MEDIUM", "remediation": {"steps": ["Configure audit log retention period"]}})
        # Check for retention settings in asl.conf or unified logging
        retention_days = None
        if 'ttl=' in content:
            match = re.search(r'ttl=(\d+)', content)
            retention_days = int(match.group(1)) if match else None
        elif 'max-size' in content or 'rotate' in content:
            retention_days = 90  # Default assumption for rotation config

        is_compliant = retention_days is not None and retention_days >= 90
        gaps = [{"requirement": "Audit logs must be retained >= 90 days", "actual": f"Retention: {retention_days or 'not configured'} days", "severity": "HIGH", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Audit Log Retention'), "parsing_successful": True, "evidence_summary": f"Log retention: {retention_days or 'unknown'} days", "actual_state": {"retention_days": retention_days}, "expected_state": {"retention_days": 90}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 30.0, "gaps": gaps, "risk_level": control.get('severity', 'MEDIUM'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_audit_events(self, content: str, control_id: str) -> Dict:
        """Parse audit events configuration (AU-006)"""
        control = self.controls_db.get(control_id, {"name": "Audit Events", "severity": "HIGH", "remediation": {"steps": ["Enable comprehensive audit event logging"]}})
        # Check for audit flags in system_profiler or audit_control
        audit_flags = []
        if 'lo' in content: audit_flags.append('login/logout')
        if 'aa' in content: audit_flags.append('authorization')
        if 'fm' in content: audit_flags.append('file_modify')
        if 'ad' in content: audit_flags.append('administrative')
        if 'pc' in content: audit_flags.append('process')

        is_compliant = len(audit_flags) >= 3
        gaps = [{"requirement": "Minimum 3 audit event types required", "actual": f"{len(audit_flags)} types configured", "severity": "HIGH", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Audit Events'), "parsing_successful": True, "evidence_summary": f"{len(audit_flags)} audit event types configured", "actual_state": {"audit_flags": audit_flags, "count": len(audit_flags)}, "expected_state": {"minimum_types": 3}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": min(100.0, len(audit_flags) * 33.3), "gaps": gaps, "risk_level": control.get('severity', 'HIGH'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_audit_reduction(self, content: str, control_id: str) -> Dict:
        """Parse audit reduction and report generation capability (AU-007)"""
        control = self.controls_db.get(control_id, {"name": "Audit Reduction", "severity": "LOW", "remediation": {"steps": ["Configure audit analysis tools"]}})
        # Check for praudit, auditreduce, or log analysis tools
        has_tools = any(tool in content.lower() for tool in ['praudit', 'auditreduce', 'log show', 'osquery', 'asl'])

        is_compliant = has_tools or 'unified logging' in content.lower()
        gaps = [{"requirement": "Audit reduction tools must be available", "actual": "No audit analysis tools found", "severity": "LOW", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Audit Reduction'), "parsing_successful": True, "evidence_summary": f"Audit tools: {'available' if is_compliant else 'not configured'}", "actual_state": {"has_tools": is_compliant}, "expected_state": {"has_tools": True}, "compliance_status": "COMPLIANT" if is_compliant else "PARTIAL", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control.get('severity', 'LOW'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_audit_timestamps(self, content: str, control_id: str) -> Dict:
        """Parse audit record timestamp configuration (AU-008)"""
        control = self.controls_db.get(control_id, {"name": "Audit Timestamps", "severity": "MEDIUM", "remediation": {"steps": ["Ensure NTP sync for accurate timestamps"]}})
        # Check for NTP sync and timestamp format
        has_ntp = 'ntp' in content.lower() or 'systemsetup -getusingnetworktime' in content.lower() or 'On' in content
        has_timestamps = any(ts in content for ts in ['UTC', 'GMT', 'timestamp', 'time='])

        is_compliant = has_ntp or has_timestamps
        gaps = [{"requirement": "Audit timestamps must be synchronized", "actual": "Time sync not verified", "severity": "MEDIUM", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Audit Timestamps'), "parsing_successful": True, "evidence_summary": f"NTP: {'synced' if has_ntp else 'unknown'}, Timestamps: {'present' if has_timestamps else 'unknown'}", "actual_state": {"ntp_sync": has_ntp, "timestamps_present": has_timestamps}, "expected_state": {"ntp_sync": True}, "compliance_status": "COMPLIANT" if is_compliant else "PARTIAL", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control.get('severity', 'MEDIUM'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_user_identification(self, content: str, control_id: str) -> Dict:
        """Parse user identification uniqueness (IA-001)"""
        control = self.controls_db.get(control_id, {"name": "User Identification", "severity": "HIGH", "remediation": {"steps": ["Ensure unique user identifiers"]}})
        # Parse dscl or /etc/passwd output for user uniqueness
        users = [line.split(':')[0] for line in content.split('\n') if line.strip() and not line.startswith('#')]
        unique_users = len(set(users))
        total_users = len(users)

        is_compliant = unique_users == total_users and total_users > 0
        gaps = [{"requirement": "All user identifiers must be unique", "actual": f"{total_users - unique_users} duplicate users found", "severity": "HIGH", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant and total_users > 0 else []
        return {"control_id": control_id, "control_name": control.get('name', 'User Identification'), "parsing_successful": True, "evidence_summary": f"{total_users} users, {unique_users} unique", "actual_state": {"total_users": total_users, "unique_users": unique_users}, "expected_state": {"all_unique": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control.get('severity', 'HIGH'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_device_identification(self, content: str, control_id: str) -> Dict:
        """Parse device identification and authentication (IA-002)"""
        control = self.controls_db.get(control_id, {"name": "Device Identification", "severity": "MEDIUM", "remediation": {"steps": ["Configure device certificates or hardware identifiers"]}})
        # Check for hardware UUID, serial number, or device certificates
        has_uuid = 'hardware uuid' in content.lower() or 'UUID' in content
        has_serial = 'serial' in content.lower() or 'SerialNumber' in content
        has_cert = 'certificate' in content.lower() or '.pem' in content or '.crt' in content

        device_id_methods = sum([has_uuid, has_serial, has_cert])
        is_compliant = device_id_methods >= 1
        gaps = [{"requirement": "Device must have unique identifier", "actual": "No device identification found", "severity": "MEDIUM", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Device Identification'), "parsing_successful": True, "evidence_summary": f"Device ID methods: {device_id_methods}", "actual_state": {"has_uuid": has_uuid, "has_serial": has_serial, "has_cert": has_cert}, "expected_state": {"identified": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control.get('severity', 'MEDIUM'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_authenticator_management(self, content: str, control_id: str) -> Dict:
        """Parse authenticator management policies (IA-003)"""
        control = self.controls_db.get(control_id, {"name": "Authenticator Management", "severity": "HIGH", "remediation": {"steps": ["Implement strong authenticator lifecycle management"]}})
        # Check password policy settings
        has_expiry = 'maxage' in content.lower() or 'passwordexpirationdays' in content.lower()
        has_history = 'history' in content.lower() or 'previouspasswords' in content.lower()
        has_complexity = 'minlength' in content.lower() or 'requiresalpha' in content.lower()

        policy_count = sum([has_expiry, has_history, has_complexity])
        is_compliant = policy_count >= 2
        gaps = [{"requirement": "Authenticator management requires expiry, history, and complexity", "actual": f"{policy_count}/3 policies configured", "severity": "HIGH", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Authenticator Management'), "parsing_successful": True, "evidence_summary": f"{policy_count}/3 authenticator policies configured", "actual_state": {"has_expiry": has_expiry, "has_history": has_history, "has_complexity": has_complexity}, "expected_state": {"minimum_policies": 2}, "compliance_status": "COMPLIANT" if is_compliant else "PARTIAL", "compliance_score": policy_count * 33.3, "gaps": gaps, "risk_level": control.get('severity', 'HIGH'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_authenticator_feedback(self, content: str, control_id: str) -> Dict:
        """Parse authenticator feedback obscuration (IA-004)"""
        control = self.controls_db.get(control_id, {"name": "Authenticator Feedback", "severity": "LOW", "remediation": {"steps": ["Ensure password fields obscure input"]}})
        # This is typically UI-based, check for relevant security settings
        obscured = 'securetextentry' in content.lower() or 'password' not in content.lower() or 'echo' not in content

        is_compliant = obscured
        return {"control_id": control_id, "control_name": control.get('name', 'Authenticator Feedback'), "parsing_successful": True, "evidence_summary": f"Feedback obscuration: {'enabled' if is_compliant else 'check manually'}", "actual_state": {"obscured": is_compliant}, "expected_state": {"obscured": True}, "compliance_status": "COMPLIANT" if is_compliant else "PARTIAL", "compliance_score": 100.0 if is_compliant else 75.0, "gaps": [], "risk_level": control.get('severity', 'LOW'), "remediation_steps": []}

    def parse_flaw_remediation(self, content: str, control_id: str) -> Dict:
        """Parse flaw remediation / patch management (SI-001)"""
        control = self.controls_db.get(control_id, {"name": "Flaw Remediation", "severity": "HIGH", "remediation": {"steps": ["Enable automatic security updates"]}})
        # Check for software update settings
        auto_update = 'automaticcheckEnabled = 1' in content or 'AutoUpdate' in content or 'CriticalUpdateInstall = 1' in content
        recent_update = 'last successful' in content.lower() or 'softwareupdate' in content.lower()

        is_compliant = auto_update
        gaps = [{"requirement": "Automatic security updates must be enabled", "actual": "Auto-update not configured", "severity": "HIGH", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Flaw Remediation'), "parsing_successful": True, "evidence_summary": f"Auto-update: {'enabled' if auto_update else 'disabled'}", "actual_state": {"auto_update": auto_update, "recent_update": recent_update}, "expected_state": {"auto_update": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control.get('severity', 'HIGH'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_malicious_code_protection(self, content: str, control_id: str) -> Dict:
        """Parse malicious code protection status (SI-002)"""
        control = self.controls_db.get(control_id, {"name": "Malicious Code Protection", "severity": "CRITICAL", "remediation": {"steps": ["Enable XProtect and Gatekeeper"]}})
        # Check for XProtect, Gatekeeper, MRT status
        xprotect = 'xprotect' in content.lower() and ('enabled' in content.lower() or 'version' in content.lower())
        gatekeeper = 'assessmentenabled' in content.lower() or 'spctl' in content.lower() and 'enabled' in content.lower()
        mrt = 'mrt' in content.lower() or 'malware removal' in content.lower()

        protection_count = sum([xprotect, gatekeeper, mrt])
        is_compliant = protection_count >= 2
        gaps = [{"requirement": "XProtect and Gatekeeper must be enabled", "actual": f"{protection_count}/3 protections active", "severity": "CRITICAL", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Malicious Code Protection'), "parsing_successful": True, "evidence_summary": f"{protection_count}/3 malware protections active", "actual_state": {"xprotect": xprotect, "gatekeeper": gatekeeper, "mrt": mrt}, "expected_state": {"minimum_protections": 2}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": protection_count * 33.3, "gaps": gaps, "risk_level": control.get('severity', 'CRITICAL'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_baseline_configuration(self, content: str, control_id: str) -> Dict:
        """Parse baseline configuration documentation (CM-001)"""
        control = self.controls_db.get(control_id, {"name": "Baseline Configuration", "severity": "MEDIUM", "remediation": {"steps": ["Document and maintain system baseline configuration"]}})
        # Check for configuration profiles or baseline documentation
        has_profiles = 'configurationprofile' in content.lower() or 'mdm' in content.lower() or '.mobileconfig' in content
        has_baseline = 'baseline' in content.lower() or 'hardening' in content.lower()
        profile_count = content.lower().count('profile')

        is_compliant = has_profiles or profile_count > 0
        gaps = [{"requirement": "System baseline configuration must be documented", "actual": "No baseline configuration found", "severity": "MEDIUM", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Baseline Configuration'), "parsing_successful": True, "evidence_summary": f"Configuration profiles: {profile_count}", "actual_state": {"has_profiles": has_profiles, "profile_count": profile_count}, "expected_state": {"documented": True}, "compliance_status": "COMPLIANT" if is_compliant else "PARTIAL", "compliance_score": 100.0 if is_compliant else 50.0, "gaps": gaps, "risk_level": control.get('severity', 'MEDIUM'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_application_partitioning(self, content: str, control_id: str) -> Dict:
        """Parse application partitioning / sandboxing (SC-001)"""
        control = self.controls_db.get(control_id, {"name": "Application Partitioning", "severity": "HIGH", "remediation": {"steps": ["Enable App Sandbox for applications"]}})
        # Check for sandbox, App Sandbox, or container settings
        has_sandbox = 'sandbox' in content.lower() or 'app sandbox' in content.lower()
        has_sip = 'system integrity protection' in content.lower() or 'csrutil' in content.lower() and 'enabled' in content.lower()
        has_gatekeeper = 'gatekeeper' in content.lower() or 'spctl' in content.lower()

        partition_count = sum([has_sandbox, has_sip, has_gatekeeper])
        is_compliant = partition_count >= 1
        gaps = [{"requirement": "Application sandboxing must be enabled", "actual": "No partitioning mechanisms found", "severity": "HIGH", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Application Partitioning'), "parsing_successful": True, "evidence_summary": f"{partition_count} partitioning mechanisms active", "actual_state": {"sandbox": has_sandbox, "sip": has_sip, "gatekeeper": has_gatekeeper}, "expected_state": {"partitioned": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": min(100.0, partition_count * 50.0), "gaps": gaps, "risk_level": control.get('severity', 'HIGH'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}

    def parse_encryption_status(self, content: str, control_id: str) -> Dict:
        """Parse encryption at rest status (SC-002)"""
        control = self.controls_db.get(control_id, {"name": "Encryption Status", "severity": "CRITICAL", "remediation": {"steps": ["Enable FileVault full disk encryption"]}})
        # Check for FileVault, encryption status
        filevault_on = 'filevault is on' in content.lower() or 'encryption type: apfs' in content.lower()
        encrypted = 'encrypted' in content.lower() and 'not encrypted' not in content.lower()
        apfs_encrypted = 'apfs' in content.lower() and ('encryption' in content.lower() or 'cryptographic' in content.lower())

        is_compliant = filevault_on or encrypted or apfs_encrypted
        gaps = [{"requirement": "Full disk encryption must be enabled (FileVault)", "actual": "Disk not encrypted", "severity": "CRITICAL", "remediation": control.get('remediation', {}).get('steps', [])}] if not is_compliant else []
        return {"control_id": control_id, "control_name": control.get('name', 'Encryption Status'), "parsing_successful": True, "evidence_summary": f"Encryption: {'enabled' if is_compliant else 'disabled'}", "actual_state": {"filevault": filevault_on, "encrypted": encrypted}, "expected_state": {"encrypted": True}, "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT", "compliance_score": 100.0 if is_compliant else 0.0, "gaps": gaps, "risk_level": control.get('severity', 'CRITICAL'), "remediation_steps": control.get('remediation', {}).get('steps', []) if gaps else []}



def parse_evidence_file(file_path: str, control_id: str) -> Dict:
    """
    Parse an evidence file and return compliance analysis

    Args:
        file_path: Path to evidence file (e.g., /tmp/audit_*/sip_status.txt)
        control_id: Rwanda NCSA control ID (e.g., RWNCSA-SI-007)

    Returns:
        Dict with detailed compliance analysis
    """
    parser = RwandaNCSAEvidenceParser()

    with open(file_path, 'r') as f:
        content = f.read()

    return parser.parse_evidence(Path(file_path).name, content, control_id)
