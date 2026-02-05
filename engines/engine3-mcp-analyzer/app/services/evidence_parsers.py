"""
Evidence Parsers for Rwanda NCSA Compliance Audit Commands.

This module provides parser functions to interpret the output of macOS audit commands
and determine compliance status. Each parser returns a structured result that can be
used by the MCP+LLM analyzer for compliance evaluation.

Parser Output Format:
{
    "parsed": True/False,
    "compliance_indicators": ["list of positive indicators"],
    "non_compliance_indicators": ["list of negative indicators"],
    "raw_data": {...},  # Structured extraction
    "summary": "Human-readable summary"
}
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime


# =============================================================================
# Parser Result Structure
# =============================================================================

def create_parser_result(
    parsed: bool = True,
    compliance_indicators: List[str] = None,
    non_compliance_indicators: List[str] = None,
    raw_data: Dict[str, Any] = None,
    summary: str = ""
) -> Dict[str, Any]:
    """Create a standardized parser result."""
    return {
        "parsed": parsed,
        "compliance_indicators": compliance_indicators or [],
        "non_compliance_indicators": non_compliance_indicators or [],
        "raw_data": raw_data or {},
        "summary": summary
    }


# =============================================================================
# Access Control Parsers
# =============================================================================

def extract_login_entries(output: str) -> Dict[str, Any]:
    """
    Parse output from 'last -20' command.
    Extracts login history for access control auditing.
    """
    compliance = []
    non_compliance = []
    entries = []

    lines = output.strip().split('\n')
    for line in lines:
        if not line.strip() or line.startswith('wtmp'):
            continue

        parts = line.split()
        if len(parts) >= 3:
            entry = {
                "user": parts[0],
                "terminal": parts[1] if len(parts) > 1 else "unknown",
                "host": parts[2] if len(parts) > 2 else "local"
            }
            entries.append(entry)

            # Check for concerning patterns
            if parts[0] == "root":
                non_compliance.append(f"Root login detected from {entry.get('host', 'unknown')}")
            elif "still logged in" in line.lower():
                compliance.append(f"Active session for {parts[0]}")

    if entries:
        compliance.append(f"Login history maintained ({len(entries)} entries)")
    else:
        non_compliance.append("No login history available")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"entries": entries, "total_count": len(entries)},
        summary=f"Found {len(entries)} login entries"
    )


def parse_password_policy(output: str) -> Dict[str, Any]:
    """
    Parse output from 'pwpolicy -getaccountpolicies' command.
    Evaluates password policy compliance.
    """
    compliance = []
    non_compliance = []
    policies = {}

    # Check for common policy indicators
    if "policyAttributePassword" in output or "minChars" in output:
        compliance.append("Password policy is configured")

        # Extract minimum length
        min_length_match = re.search(r'minChars["\s:=]+(\d+)', output, re.IGNORECASE)
        if min_length_match:
            min_len = int(min_length_match.group(1))
            policies["min_length"] = min_len
            if min_len >= 8:
                compliance.append(f"Minimum password length: {min_len} characters")
            else:
                non_compliance.append(f"Minimum password length too short: {min_len}")

        # Check for complexity requirements
        if "requiresMixedCase" in output or "upper" in output.lower():
            compliance.append("Password complexity requirements enabled")
            policies["complexity"] = True

        # Check for password history
        if "policyAttributePasswordHistoryDepth" in output:
            compliance.append("Password history tracking enabled")
            policies["history"] = True

    elif "Default policy" in output or output.strip() == "":
        non_compliance.append("Using default password policy - custom policy not configured")
    else:
        compliance.append("Password policy output received")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=policies,
        summary="Password policy " + ("configured" if policies else "using defaults")
    )


def parse_user_accounts(output: str) -> Dict[str, Any]:
    """
    Parse output from 'dscl . -list /Users' command.
    Lists all user accounts for access control review.
    """
    compliance = []
    non_compliance = []
    users = []
    system_users = []

    for line in output.strip().split('\n'):
        user = line.strip()
        if not user:
            continue

        if user.startswith('_') or user in ['daemon', 'nobody', 'root']:
            system_users.append(user)
        else:
            users.append(user)

    compliance.append(f"User account inventory available ({len(users)} user accounts)")

    if len(users) > 20:
        non_compliance.append(f"Large number of user accounts ({len(users)}) - review needed")

    # Check for default/test accounts
    suspicious = [u for u in users if u.lower() in ['test', 'admin', 'guest', 'temp', 'user']]
    if suspicious:
        non_compliance.append(f"Potential default/test accounts found: {', '.join(suspicious)}")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={
            "user_accounts": users,
            "system_accounts": system_users,
            "total_users": len(users),
            "total_system": len(system_users)
        },
        summary=f"{len(users)} user accounts, {len(system_users)} system accounts"
    )


def parse_admin_access(output: str) -> Dict[str, Any]:
    """
    Parse output from 'dscl . -read /Groups/admin GroupMembership' command.
    Reviews administrative access privileges.
    """
    compliance = []
    non_compliance = []
    admins = []

    # Extract admin users from GroupMembership line
    if "GroupMembership:" in output:
        parts = output.split("GroupMembership:")
        if len(parts) > 1:
            admins = [u.strip() for u in parts[1].strip().split() if u.strip()]
    elif "no such key" in output.lower():
        admins = []
    else:
        # Try direct parsing
        admins = [u.strip() for u in output.strip().split() if u.strip() and u != "GroupMembership:"]

    if admins:
        compliance.append(f"Admin group membership documented ({len(admins)} admins)")

        if len(admins) > 5:
            non_compliance.append(f"Excessive admin accounts ({len(admins)}) - principle of least privilege violation")
        elif len(admins) <= 2:
            compliance.append("Limited admin access follows least privilege principle")

        if "root" in admins:
            non_compliance.append("Root user in admin group")
    else:
        non_compliance.append("Unable to determine admin group membership")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"admin_users": admins, "admin_count": len(admins)},
        summary=f"{len(admins)} users have administrative access"
    )


def parse_sudo_config(output: str) -> Dict[str, Any]:
    """
    Parse output from 'sudo -l' command.
    Reviews sudo/privilege configuration.
    """
    compliance = []
    non_compliance = []
    sudo_rules = []

    if "may run the following" in output.lower():
        compliance.append("Sudo access is configured")

        # Extract sudo rules
        lines = output.strip().split('\n')
        for line in lines:
            if '(' in line and ')' in line:
                sudo_rules.append(line.strip())

        # Check for NOPASSWD
        if "NOPASSWD" in output:
            non_compliance.append("NOPASSWD sudo rules detected - password bypass configured")

        # Check for ALL access
        if "(ALL : ALL) ALL" in output or "(root) ALL" in output:
            non_compliance.append("Unrestricted sudo access configured")
        else:
            compliance.append("Sudo access appears to be restricted")

    elif "not allowed" in output.lower() or "sorry" in output.lower():
        compliance.append("Current user does not have sudo access - least privilege enforced")
    elif "sudo check" in output:
        non_compliance.append("Unable to check sudo configuration")
    else:
        non_compliance.append("Sudo configuration unclear")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"sudo_rules": sudo_rules, "rule_count": len(sudo_rules)},
        summary=f"Sudo configuration with {len(sudo_rules)} rules"
    )


def parse_active_sessions(output: str) -> Dict[str, Any]:
    """
    Parse output from 'who' command.
    Lists active user sessions.
    """
    compliance = []
    non_compliance = []
    sessions = []

    lines = output.strip().split('\n')
    for line in lines:
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 2:
            session = {
                "user": parts[0],
                "terminal": parts[1] if len(parts) > 1 else "unknown",
                "login_time": " ".join(parts[2:4]) if len(parts) > 3 else "unknown"
            }
            sessions.append(session)

    if sessions:
        compliance.append(f"Active session tracking enabled ({len(sessions)} active sessions)")

        # Check for multiple sessions from same user
        users = [s["user"] for s in sessions]
        if len(users) != len(set(users)):
            non_compliance.append("Multiple concurrent sessions detected for same user")

        # Check for root sessions
        if "root" in users:
            non_compliance.append("Active root session detected")
    else:
        compliance.append("No active sessions or session tracking available")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"sessions": sessions, "session_count": len(sessions)},
        summary=f"{len(sessions)} active sessions"
    )


def parse_ssh_config(output: str) -> Dict[str, Any]:
    """
    Parse SSH configuration from sshd_config or systemsetup output.
    """
    compliance = []
    non_compliance = []
    config = {}

    output_lower = output.lower()

    # Check remote login status
    if "remote login: on" in output_lower:
        compliance.append("Remote login (SSH) is enabled")
        config["ssh_enabled"] = True
    elif "remote login: off" in output_lower:
        compliance.append("Remote login (SSH) is disabled")
        config["ssh_enabled"] = False

    # Parse sshd_config options
    if "permitrootlogin" in output_lower:
        if "permitrootlogin no" in output_lower or "permitrootlogin prohibit-password" in output_lower:
            compliance.append("Root login via SSH is disabled")
            config["root_login"] = False
        elif "permitrootlogin yes" in output_lower:
            non_compliance.append("Root login via SSH is enabled - security risk")
            config["root_login"] = True

    if "passwordauthentication" in output_lower:
        if "passwordauthentication no" in output_lower:
            compliance.append("Password authentication disabled - key-based auth enforced")
            config["password_auth"] = False
        elif "passwordauthentication yes" in output_lower:
            config["password_auth"] = True

    if "pubkeyauthentication yes" in output_lower:
        compliance.append("Public key authentication enabled")
        config["pubkey_auth"] = True

    if "maxauthtries" in output_lower:
        match = re.search(r'maxauthtries\s+(\d+)', output_lower)
        if match:
            max_tries = int(match.group(1))
            config["max_auth_tries"] = max_tries
            if max_tries <= 3:
                compliance.append(f"SSH max auth tries limited to {max_tries}")
            else:
                non_compliance.append(f"SSH max auth tries too high: {max_tries}")

    if "SSH not configured" in output:
        compliance.append("SSH server not installed - reduced attack surface")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=config,
        summary="SSH configuration analyzed"
    )


def parse_screen_lock(output: str) -> Dict[str, Any]:
    """
    Parse screen lock settings from defaults read command.
    """
    compliance = []
    non_compliance = []
    settings = {}

    try:
        value = int(output.strip())
        settings["ask_for_password"] = value

        if value == 1:
            compliance.append("Screen lock requires password")
        else:
            non_compliance.append("Screen lock does not require password")
    except ValueError:
        if "does not exist" in output.lower():
            non_compliance.append("Screen lock password setting not configured")
        else:
            non_compliance.append("Unable to determine screen lock settings")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=settings,
        summary="Screen lock " + ("requires password" if settings.get("ask_for_password") == 1 else "password not required")
    )


def parse_file_permissions(output: str) -> Dict[str, Any]:
    """
    Parse file permission listing from ls -la command.
    """
    compliance = []
    non_compliance = []
    files = []
    world_writable = []

    for line in output.strip().split('\n'):
        if line.startswith('total') or not line.strip():
            continue

        parts = line.split()
        if len(parts) >= 9:
            perms = parts[0]
            filename = parts[-1]

            file_info = {
                "permissions": perms,
                "owner": parts[2] if len(parts) > 2 else "unknown",
                "group": parts[3] if len(parts) > 3 else "unknown",
                "name": filename
            }
            files.append(file_info)

            # Check for world-writable files
            if len(perms) >= 9 and perms[8] == 'w':
                world_writable.append(filename)

    if files:
        compliance.append(f"File permissions audit completed ({len(files)} items)")

    if world_writable:
        non_compliance.append(f"World-writable files/directories found: {', '.join(world_writable[:5])}")
    else:
        compliance.append("No world-writable files in checked directories")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"files": files, "world_writable": world_writable},
        summary=f"{len(files)} files checked, {len(world_writable)} world-writable"
    )


def parse_pf_rules(output: str) -> Dict[str, Any]:
    """
    Parse packet filter (pf) firewall rules.
    """
    compliance = []
    non_compliance = []
    rules = []

    if "pf not running" in output.lower() or "pfctl: not running" in output.lower():
        non_compliance.append("Packet filter (pf) firewall is not running")
    else:
        lines = output.strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('#'):
                rules.append(line.strip())

        if rules:
            compliance.append(f"Packet filter active with {len(rules)} rules")

            # Check for default deny
            if any('block' in r.lower() for r in rules):
                compliance.append("Blocking rules configured")

            # Check for logging
            if any('log' in r.lower() for r in rules):
                compliance.append("Firewall logging enabled")
        else:
            non_compliance.append("Packet filter running but no rules configured")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"rules": rules, "rule_count": len(rules)},
        summary=f"Firewall with {len(rules)} rules"
    )


def parse_user_groups(output: str) -> Dict[str, Any]:
    """
    Parse user groups from dscl . -list /Groups command.
    """
    compliance = []
    non_compliance = []
    groups = []
    system_groups = []

    for line in output.strip().split('\n'):
        group = line.strip()
        if not group:
            continue

        if group.startswith('_') or group in ['wheel', 'daemon', 'kmem', 'sys', 'tty']:
            system_groups.append(group)
        else:
            groups.append(group)

    compliance.append(f"Group inventory available ({len(groups)} custom groups)")

    if 'admin' in groups:
        compliance.append("Admin group exists for privilege separation")

    if 'staff' in groups:
        compliance.append("Staff group exists for user separation")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={
            "custom_groups": groups,
            "system_groups": system_groups,
            "total_custom": len(groups),
            "total_system": len(system_groups)
        },
        summary=f"{len(groups)} custom groups, {len(system_groups)} system groups"
    )


# =============================================================================
# Audit and Accountability Parsers
# =============================================================================

def parse_system_logs(output: str) -> Dict[str, Any]:
    """
    Parse system log output from log show command.
    """
    compliance = []
    non_compliance = []
    log_stats = {"total_lines": 0, "error_count": 0, "warning_count": 0}

    lines = output.strip().split('\n')
    log_stats["total_lines"] = len(lines)

    for line in lines:
        line_lower = line.lower()
        if 'error' in line_lower:
            log_stats["error_count"] += 1
        if 'warning' in line_lower:
            log_stats["warning_count"] += 1

    if log_stats["total_lines"] > 0:
        compliance.append(f"System logging is active ({log_stats['total_lines']} log entries)")

        if log_stats["error_count"] > 10:
            non_compliance.append(f"High error count in logs: {log_stats['error_count']}")
    else:
        non_compliance.append("No system logs available")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=log_stats,
        summary=f"{log_stats['total_lines']} log entries, {log_stats['error_count']} errors"
    )


def parse_audit_system(output: str) -> Dict[str, Any]:
    """
    Parse audit system status from launchctl list.
    """
    compliance = []
    non_compliance = []
    services = []

    for line in output.strip().split('\n'):
        if 'audit' in line.lower():
            services.append(line.strip())

    if services:
        compliance.append(f"Audit services running: {len(services)}")

        if any('auditd' in s.lower() for s in services):
            compliance.append("auditd service is active")
    else:
        non_compliance.append("No audit services found running")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"audit_services": services},
        summary=f"{len(services)} audit-related services"
    )


def parse_audit_files(output: str) -> Dict[str, Any]:
    """
    Parse audit file listing from /var/audit.
    """
    compliance = []
    non_compliance = []
    audit_files = []

    if "No audit files" in output or "No such file" in output.lower():
        non_compliance.append("No audit files found - auditing may not be configured")
    else:
        lines = output.strip().split('\n')
        for line in lines:
            if line.strip() and not line.startswith('total'):
                audit_files.append(line.strip())

        if audit_files:
            compliance.append(f"Audit files present ({len(audit_files)} files)")

            # Check file age (basic check)
            compliance.append("Audit trail is being maintained")
        else:
            non_compliance.append("Audit directory empty")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"audit_files": audit_files, "file_count": len(audit_files)},
        summary=f"{len(audit_files)} audit files"
    )


def parse_auth_events(output: str) -> Dict[str, Any]:
    """
    Parse authentication events from log show.
    """
    compliance = []
    non_compliance = []
    events = {"success": 0, "failure": 0, "total": 0}

    lines = output.strip().split('\n')
    events["total"] = len([l for l in lines if l.strip()])

    for line in lines:
        line_lower = line.lower()
        if 'success' in line_lower or 'accepted' in line_lower:
            events["success"] += 1
        if 'fail' in line_lower or 'denied' in line_lower or 'invalid' in line_lower:
            events["failure"] += 1

    if events["total"] > 0:
        compliance.append(f"Authentication events are being logged ({events['total']} events)")

        if events["failure"] > 0:
            if events["failure"] > events["success"]:
                non_compliance.append(f"High failure rate: {events['failure']} failures vs {events['success']} successes")
            else:
                compliance.append(f"Authentication failures being tracked: {events['failure']}")
    else:
        non_compliance.append("No authentication events found")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=events,
        summary=f"{events['total']} auth events ({events['failure']} failures)"
    )


def parse_timestamps(output: str) -> Dict[str, Any]:
    """
    Parse timestamp information from date and log commands.
    """
    compliance = []
    non_compliance = []
    time_info = {}

    lines = output.strip().split('\n')
    if lines:
        time_info["current_time"] = lines[0].strip()
        compliance.append(f"System time available: {time_info['current_time']}")

        # Check if logs have timestamps
        log_lines = lines[1:] if len(lines) > 1 else []
        has_timestamps = any(re.search(r'\d{4}-\d{2}-\d{2}', line) for line in log_lines)

        if has_timestamps:
            compliance.append("Log entries contain timestamps")
            time_info["logs_timestamped"] = True
        elif log_lines:
            non_compliance.append("Log entries may lack proper timestamps")
            time_info["logs_timestamped"] = False

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=time_info,
        summary="Timestamp verification complete"
    )


def parse_log_retention(output: str) -> Dict[str, Any]:
    """
    Parse log file listing for retention analysis.
    """
    compliance = []
    non_compliance = []
    log_files = []

    for line in output.strip().split('\n'):
        if '.log' in line.lower() and not line.startswith('total'):
            log_files.append(line.strip())

    if log_files:
        compliance.append(f"Log files maintained ({len(log_files)} log files)")

        # Check for rotation (numbered/dated logs)
        rotated = [f for f in log_files if re.search(r'\.\d+|\.gz|\.bz2', f)]
        if rotated:
            compliance.append(f"Log rotation active ({len(rotated)} archived logs)")
        else:
            non_compliance.append("No log rotation detected")
    else:
        non_compliance.append("No log files found")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"log_files": log_files, "file_count": len(log_files)},
        summary=f"{len(log_files)} log files"
    )


def parse_time_sync(output: str) -> Dict[str, Any]:
    """
    Parse time synchronization settings.
    """
    compliance = []
    non_compliance = []
    time_config = {}

    output_lower = output.lower()

    if "network time: on" in output_lower:
        compliance.append("Network time synchronization enabled")
        time_config["ntp_enabled"] = True
    elif "network time: off" in output_lower:
        non_compliance.append("Network time synchronization disabled")
        time_config["ntp_enabled"] = False

    # Extract time server
    match = re.search(r'network time server:\s*(.+)', output, re.IGNORECASE)
    if match:
        server = match.group(1).strip()
        time_config["time_server"] = server
        compliance.append(f"Time server configured: {server}")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=time_config,
        summary="Time synchronization " + ("enabled" if time_config.get("ntp_enabled") else "disabled")
    )


def parse_log_protection(output: str) -> Dict[str, Any]:
    """
    Parse log directory permissions for protection assessment.
    """
    compliance = []
    non_compliance = []
    permissions = {}

    for line in output.strip().split('\n'):
        if line.startswith('total'):
            continue
        parts = line.split()
        if len(parts) >= 9:
            perms = parts[0]
            owner = parts[2]
            group = parts[3]
            name = parts[-1]

            permissions[name] = {"perms": perms, "owner": owner, "group": group}

            # Check log file protection
            if 'w' in perms[7:]:  # World-writable
                non_compliance.append(f"Log {name} is world-writable")
            else:
                compliance.append(f"Log {name} has restricted permissions")

            if owner == 'root':
                compliance.append(f"Log {name} owned by root")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=permissions,
        summary=f"{len(permissions)} log files checked for protection"
    )


def parse_log_stats(output: str) -> Dict[str, Any]:
    """
    Parse log volume statistics.
    """
    compliance = []
    non_compliance = []
    stats = {}

    try:
        count = int(output.strip())
        stats["log_count"] = count

        if count > 1000:
            compliance.append(f"Substantial logging activity ({count} entries in 24h)")
        elif count > 100:
            compliance.append(f"Moderate logging activity ({count} entries in 24h)")
        elif count > 0:
            non_compliance.append(f"Low logging activity ({count} entries in 24h)")
        else:
            non_compliance.append("No logging activity detected")
    except ValueError:
        non_compliance.append("Unable to determine log statistics")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=stats,
        summary=f"{stats.get('log_count', 0)} log entries"
    )


def parse_security_alerts(output: str) -> Dict[str, Any]:
    """
    Parse security-related alerts from logs.
    """
    compliance = []
    non_compliance = []
    alerts = []

    for line in output.strip().split('\n'):
        if line.strip() and 'fail' in line.lower():
            alerts.append(line.strip())

    if alerts:
        compliance.append(f"Security event logging active ({len(alerts)} failure events)")

        if len(alerts) > 20:
            non_compliance.append(f"High volume of failure events: {len(alerts)}")
    else:
        compliance.append("No failure events in recent logs")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"alerts": alerts[:20], "alert_count": len(alerts)},
        summary=f"{len(alerts)} security alerts"
    )


# =============================================================================
# Configuration Management Parsers
# =============================================================================

def parse_system_info(output: str) -> Dict[str, Any]:
    """
    Parse system profiler software data type.
    """
    compliance = []
    non_compliance = []
    system_info = {}

    # Extract key info
    for line in output.strip().split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            key = key.strip().lower()
            value = value.strip()

            if 'version' in key:
                system_info['os_version'] = value
            elif 'name' in key and 'system' in key:
                system_info['os_name'] = value
            elif 'boot volume' in key:
                system_info['boot_volume'] = value

    if system_info:
        compliance.append(f"System configuration documented")
        if system_info.get('os_version'):
            compliance.append(f"OS Version: {system_info['os_version']}")
    else:
        non_compliance.append("Unable to retrieve system configuration")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=system_info,
        summary=f"System: {system_info.get('os_name', 'Unknown')} {system_info.get('os_version', '')}"
    )


def parse_baseline_config(output: str) -> Dict[str, Any]:
    """
    Parse baseline configuration from defaults command.
    """
    compliance = []
    non_compliance = []
    settings = {}

    line_count = len(output.strip().split('\n'))

    if line_count > 0:
        compliance.append(f"Configuration baseline captured ({line_count} settings)")
        settings["settings_count"] = line_count

        # Check for security-relevant settings
        if 'AppleShowAllExtensions' in output:
            settings["show_extensions"] = True
        if 'NSNavPanelExpandedStateForSaveMode' in output:
            settings["expanded_save"] = True
    else:
        non_compliance.append("No baseline configuration available")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=settings,
        summary=f"{line_count} configuration settings"
    )


def parse_config_changes(output: str) -> Dict[str, Any]:
    """
    Parse configuration change events from logs.
    """
    compliance = []
    non_compliance = []
    changes = []

    for line in output.strip().split('\n'):
        if 'config' in line.lower() and line.strip():
            changes.append(line.strip())

    if changes:
        compliance.append(f"Configuration change logging active ({len(changes)} events)")

        if len(changes) > 50:
            non_compliance.append(f"High volume of config changes: {len(changes)}")
    else:
        compliance.append("No recent configuration changes logged")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"changes": changes[:20], "change_count": len(changes)},
        summary=f"{len(changes)} configuration changes"
    )


def parse_software_inventory(output: str) -> Dict[str, Any]:
    """
    Parse software inventory from system_profiler.
    """
    compliance = []
    non_compliance = []
    apps = []

    current_app = {}
    for line in output.strip().split('\n'):
        line = line.strip()
        if line.endswith(':') and not line.startswith(' '):
            if current_app:
                apps.append(current_app)
            current_app = {"name": line[:-1]}
        elif ':' in line and current_app:
            key, _, value = line.partition(':')
            current_app[key.strip().lower()] = value.strip()

    if current_app:
        apps.append(current_app)

    if apps:
        compliance.append(f"Software inventory available ({len(apps)} applications)")
    else:
        non_compliance.append("Unable to retrieve software inventory")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"applications": apps[:50], "app_count": len(apps)},
        summary=f"{len(apps)} applications inventoried"
    )


def parse_installed_packages(output: str) -> Dict[str, Any]:
    """
    Parse installed packages from pkgutil.
    """
    compliance = []
    non_compliance = []
    packages = []

    for line in output.strip().split('\n'):
        if line.strip():
            packages.append(line.strip())

    if packages:
        compliance.append(f"Package inventory available ({len(packages)} packages)")

        # Check for potentially concerning packages
        suspicious = [p for p in packages if any(x in p.lower() for x in ['crack', 'hack', 'keylog'])]
        if suspicious:
            non_compliance.append(f"Suspicious packages found: {', '.join(suspicious[:5])}")
    else:
        non_compliance.append("No packages installed or unable to retrieve")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"packages": packages[:50], "package_count": len(packages)},
        summary=f"{len(packages)} packages installed"
    )


def parse_patch_status(output: str) -> Dict[str, Any]:
    """
    Parse software update status.
    """
    compliance = []
    non_compliance = []
    updates = []

    if "No new software available" in output or "No updates" in output:
        compliance.append("System is fully patched - no updates available")
    else:
        for line in output.strip().split('\n'):
            if line.strip() and not line.startswith('Software Update'):
                updates.append(line.strip())

        if updates:
            non_compliance.append(f"Updates available: {len(updates)} pending updates")

            # Check for security updates
            security_updates = [u for u in updates if 'security' in u.lower()]
            if security_updates:
                non_compliance.append(f"Security updates pending: {len(security_updates)}")
        else:
            compliance.append("Update check completed")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"pending_updates": updates, "update_count": len(updates)},
        summary=f"{len(updates)} updates pending" if updates else "System up to date"
    )


def parse_installed_apps(output: str) -> Dict[str, Any]:
    """
    Parse installed applications from /Applications.
    """
    compliance = []
    non_compliance = []
    apps = []

    for line in output.strip().split('\n'):
        if line.strip() and not line.startswith('total'):
            parts = line.split()
            if parts:
                app_name = parts[-1] if parts else line.strip()
                apps.append(app_name)

    if apps:
        compliance.append(f"Application inventory available ({len(apps)} applications)")
    else:
        non_compliance.append("Unable to list applications")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"applications": apps, "app_count": len(apps)},
        summary=f"{len(apps)} applications"
    )


def parse_sip_status(output: str) -> Dict[str, Any]:
    """
    Parse System Integrity Protection status.
    """
    compliance = []
    non_compliance = []
    status = {}

    output_lower = output.lower()

    if "enabled" in output_lower:
        compliance.append("System Integrity Protection (SIP) is enabled")
        status["sip_enabled"] = True
    elif "disabled" in output_lower:
        non_compliance.append("System Integrity Protection (SIP) is disabled - security risk")
        status["sip_enabled"] = False
    else:
        non_compliance.append("Unable to determine SIP status")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=status,
        summary="SIP " + ("enabled" if status.get("sip_enabled") else "disabled/unknown")
    )


def parse_running_services(output: str) -> Dict[str, Any]:
    """
    Parse running services from launchctl.
    """
    compliance = []
    non_compliance = []
    services = []

    for line in output.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 3:
            service = {
                "pid": parts[0],
                "status": parts[1],
                "label": parts[2]
            }
            services.append(service)

    if services:
        compliance.append(f"Service inventory available ({len(services)} services)")

        # Count running vs stopped
        running = [s for s in services if s["pid"] != '-']
        compliance.append(f"{len(running)} services currently running")
    else:
        non_compliance.append("Unable to list services")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"services": services[:50], "service_count": len(services)},
        summary=f"{len(services)} services"
    )


# =============================================================================
# Identity and Authentication Parsers
# =============================================================================

def parse_certificates(output: str) -> Dict[str, Any]:
    """
    Parse certificate information from security command.
    """
    compliance = []
    non_compliance = []
    certs = []

    if "No certs" in output or "0 valid identities" in output:
        non_compliance.append("No valid certificates found")
    else:
        for line in output.strip().split('\n'):
            if line.strip() and ')' in line:
                certs.append(line.strip())

        if certs:
            compliance.append(f"Valid certificates found ({len(certs)})")
        else:
            compliance.append("Certificate check completed")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"certificates": certs, "cert_count": len(certs)},
        summary=f"{len(certs)} certificates"
    )


def parse_keychain_config(output: str) -> Dict[str, Any]:
    """
    Parse keychain configuration.
    """
    compliance = []
    non_compliance = []
    keychains = []

    for line in output.strip().split('\n'):
        if line.strip():
            keychain = line.strip().strip('"')
            keychains.append(keychain)

    if keychains:
        compliance.append(f"Keychain configured ({len(keychains)} keychains)")

        if any('login.keychain' in k for k in keychains):
            compliance.append("Login keychain configured")
    else:
        non_compliance.append("No keychains configured")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"keychains": keychains, "keychain_count": len(keychains)},
        summary=f"{len(keychains)} keychains configured"
    )


def parse_auth_identities(output: str) -> Dict[str, Any]:
    """
    Parse authentication identities.
    """
    compliance = []
    non_compliance = []
    identities = []

    if "No identities" in output or "0 identities" in output:
        compliance.append("No authentication identities - may be expected")
    else:
        for line in output.strip().split('\n'):
            if line.strip() and ')' in line:
                identities.append(line.strip())

        if identities:
            compliance.append(f"Authentication identities available ({len(identities)})")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"identities": identities, "identity_count": len(identities)},
        summary=f"{len(identities)} authentication identities"
    )


def parse_smart_cards(output: str) -> Dict[str, Any]:
    """
    Parse smart card configuration.
    """
    compliance = []
    non_compliance = []
    cards = {}

    if "No smart cards" in output:
        compliance.append("Smart card authentication not configured (may be expected)")
        cards["configured"] = False
    else:
        compliance.append("Smart card configuration detected")
        cards["configured"] = True
        cards["output"] = output.strip()

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=cards,
        summary="Smart cards " + ("configured" if cards.get("configured") else "not configured")
    )


def parse_biometric_config(output: str) -> Dict[str, Any]:
    """
    Parse biometric (Touch ID/Face ID) configuration.
    """
    compliance = []
    non_compliance = []
    biometrics = {}

    if "not available" in output.lower() or "Biometrics not available" in output:
        compliance.append("Biometric authentication not available on this hardware")
        biometrics["available"] = False
    else:
        compliance.append("Biometric authentication available")
        biometrics["available"] = True
        biometrics["output"] = output.strip()

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=biometrics,
        summary="Biometrics " + ("available" if biometrics.get("available") else "not available")
    )


def parse_mfa_config(output: str) -> Dict[str, Any]:
    """
    Parse multi-factor authentication configuration.
    """
    compliance = []
    non_compliance = []
    mfa_info = {}

    # Check for certificates which indicate potential MFA
    if "valid identities" in output.lower():
        match = re.search(r'(\d+)\s+valid identities', output.lower())
        if match:
            count = int(match.group(1))
            mfa_info["cert_count"] = count
            if count > 0:
                compliance.append(f"Certificate-based authentication available ({count} identities)")
            else:
                non_compliance.append("No certificate identities for MFA")
    elif "No certs" in output:
        non_compliance.append("No certificates available for MFA")
    else:
        compliance.append("MFA configuration check completed")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=mfa_info,
        summary="MFA check completed"
    )


def parse_replay_protection(output: str) -> Dict[str, Any]:
    """
    Parse replay protection from logs.
    """
    compliance = []
    non_compliance = []
    events = []

    for line in output.strip().split('\n'):
        if 'replay' in line.lower() and line.strip():
            events.append(line.strip())

    if events:
        non_compliance.append(f"Replay attack indicators found: {len(events)} events")
    else:
        compliance.append("No replay attack indicators in recent logs")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"events": events, "event_count": len(events)},
        summary=f"{len(events)} replay-related events"
    )


# =============================================================================
# Incident Response Parsers
# =============================================================================

def parse_incident_logs(output: str) -> Dict[str, Any]:
    """
    Parse incident/error logs.
    """
    compliance = []
    non_compliance = []
    incidents = []

    for line in output.strip().split('\n'):
        if 'error' in line.lower() and line.strip():
            incidents.append(line.strip())

    if incidents:
        compliance.append(f"Incident logging active ({len(incidents)} error events)")

        if len(incidents) > 50:
            non_compliance.append(f"High incident volume: {len(incidents)} errors")
    else:
        compliance.append("No error events in recent logs")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"incidents": incidents[:30], "incident_count": len(incidents)},
        summary=f"{len(incidents)} incident/error events"
    )


def parse_security_processes(output: str) -> Dict[str, Any]:
    """
    Parse security-related processes.
    """
    compliance = []
    non_compliance = []
    processes = []

    for line in output.strip().split('\n'):
        if line.strip() and not line.startswith('USER'):
            processes.append(line.strip())

    if processes:
        compliance.append(f"Security processes running ({len(processes)})")

        # Check for specific security tools
        process_text = ' '.join(processes).lower()
        if 'xprotect' in process_text or 'mrt' in process_text:
            compliance.append("Apple malware protection running")
        if 'firewall' in process_text:
            compliance.append("Firewall process active")
    else:
        non_compliance.append("No security processes detected")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"processes": processes, "process_count": len(processes)},
        summary=f"{len(processes)} security processes"
    )


def parse_monitoring_status(output: str) -> Dict[str, Any]:
    """
    Parse monitoring system status.
    """
    compliance = []
    non_compliance = []
    status = {}

    if "Monitoring active" in output or "timeout" in output.lower():
        compliance.append("Log monitoring system is accessible")
        status["monitoring_active"] = True
    else:
        # Parse any alerts captured
        lines = output.strip().split('\n')
        status["alert_count"] = len([l for l in lines if l.strip()])
        compliance.append(f"Monitoring check completed ({status['alert_count']} events)")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=status,
        summary="Monitoring " + ("active" if status.get("monitoring_active") else "checked")
    )


def parse_log_volume(output: str) -> Dict[str, Any]:
    """
    Parse log volume statistics.
    """
    return parse_log_stats(output)  # Reuse existing parser


def parse_containment_rules(output: str) -> Dict[str, Any]:
    """
    Parse containment/firewall rules for incident response.
    """
    return parse_pf_rules(output)  # Reuse existing parser


def parse_security_services(output: str) -> Dict[str, Any]:
    """
    Parse security-related services from launchctl.
    """
    compliance = []
    non_compliance = []
    services = []

    for line in output.strip().split('\n'):
        if 'security' in line.lower() and line.strip():
            services.append(line.strip())

    if services:
        compliance.append(f"Security services running ({len(services)})")
    else:
        non_compliance.append("No security services found")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"services": services, "service_count": len(services)},
        summary=f"{len(services)} security services"
    )


# =============================================================================
# System and Communications Protection Parsers
# =============================================================================

def parse_firewall_status(output: str) -> Dict[str, Any]:
    """
    Parse Application Firewall status.
    """
    compliance = []
    non_compliance = []
    status = {}

    output_lower = output.lower()

    if "enabled" in output_lower or "state = 1" in output_lower:
        compliance.append("Application Firewall is enabled")
        status["firewall_enabled"] = True
    elif "disabled" in output_lower or "state = 0" in output_lower:
        non_compliance.append("Application Firewall is disabled")
        status["firewall_enabled"] = False
    else:
        non_compliance.append("Unable to determine firewall status")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=status,
        summary="Firewall " + ("enabled" if status.get("firewall_enabled") else "disabled")
    )


def parse_firewall_apps(output: str) -> Dict[str, Any]:
    """
    Parse Application Firewall app list.
    """
    compliance = []
    non_compliance = []
    apps = []

    for line in output.strip().split('\n'):
        if line.strip() and ('allow' in line.lower() or 'block' in line.lower()):
            apps.append(line.strip())

    if apps:
        compliance.append(f"Firewall application rules configured ({len(apps)} rules)")

        blocked = [a for a in apps if 'block' in a.lower()]
        if blocked:
            compliance.append(f"{len(blocked)} applications blocked")
    else:
        non_compliance.append("No firewall application rules configured")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"apps": apps, "app_count": len(apps)},
        summary=f"{len(apps)} firewall app rules"
    )


def parse_filevault_status(output: str) -> Dict[str, Any]:
    """
    Parse FileVault disk encryption status.
    """
    compliance = []
    non_compliance = []
    status = {}

    output_lower = output.lower()

    if "filevault is on" in output_lower:
        compliance.append("FileVault disk encryption is enabled")
        status["filevault_enabled"] = True
    elif "filevault is off" in output_lower:
        non_compliance.append("FileVault disk encryption is disabled - data at rest unprotected")
        status["filevault_enabled"] = False
    elif "encryption in progress" in output_lower:
        compliance.append("FileVault encryption is in progress")
        status["filevault_enabled"] = "in_progress"
    else:
        non_compliance.append("Unable to determine FileVault status")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=status,
        summary="FileVault " + ("enabled" if status.get("filevault_enabled") == True else "disabled/unknown")
    )


def parse_network_services(output: str) -> Dict[str, Any]:
    """
    Parse network services list.
    """
    compliance = []
    non_compliance = []
    services = []

    for line in output.strip().split('\n'):
        service = line.strip()
        if service and not service.startswith('An asterisk'):
            services.append(service)

    if services:
        compliance.append(f"Network services inventory ({len(services)} services)")

        # Check for potentially risky services
        risky = [s for s in services if any(r in s.lower() for r in ['vpn', 'bluetooth', 'thunderbolt'])]
        if risky:
            compliance.append(f"Network services include: {', '.join(risky[:3])}")
    else:
        non_compliance.append("No network services found")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"services": services, "service_count": len(services)},
        summary=f"{len(services)} network services"
    )


def parse_ssl_certs(output: str) -> Dict[str, Any]:
    """
    Parse SSL client certificates.
    """
    return parse_certificates(output)  # Reuse existing parser


def parse_network_connections(output: str) -> Dict[str, Any]:
    """
    Parse network connections from netstat.
    """
    compliance = []
    non_compliance = []
    connections = {"tcp": 0, "udp": 0, "listening": 0, "established": 0}

    for line in output.strip().split('\n'):
        line_lower = line.lower()

        if 'tcp' in line_lower:
            connections["tcp"] += 1
        if 'udp' in line_lower:
            connections["udp"] += 1
        if 'listen' in line_lower:
            connections["listening"] += 1
        if 'established' in line_lower:
            connections["established"] += 1

    total = connections["tcp"] + connections["udp"]
    if total > 0:
        compliance.append(f"Network connections monitored ({total} connections)")
        compliance.append(f"{connections['listening']} listening, {connections['established']} established")

        if connections["listening"] > 50:
            non_compliance.append(f"High number of listening ports: {connections['listening']}")
    else:
        compliance.append("No active network connections")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=connections,
        summary=f"{total} network connections"
    )


def parse_network_rules(output: str) -> Dict[str, Any]:
    """
    Parse network/firewall rules.
    """
    return parse_pf_rules(output)  # Reuse existing parser


def parse_active_connections(output: str) -> Dict[str, Any]:
    """
    Parse active (established) network connections.
    """
    compliance = []
    non_compliance = []
    connections = []

    for line in output.strip().split('\n'):
        if 'ESTABLISHED' in line:
            parts = line.split()
            if len(parts) >= 5:
                conn = {
                    "protocol": parts[0],
                    "local": parts[3],
                    "remote": parts[4]
                }
                connections.append(conn)

    if connections:
        compliance.append(f"Active connections tracked ({len(connections)} established)")

        # Check for suspicious ports
        suspicious_ports = ['6666', '6667', '4444', '31337']
        for conn in connections:
            for port in suspicious_ports:
                if port in str(conn.get('remote', '')):
                    non_compliance.append(f"Suspicious port in connection: {conn['remote']}")
    else:
        compliance.append("No established connections")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"connections": connections[:20], "connection_count": len(connections)},
        summary=f"{len(connections)} active connections"
    )


def parse_resource_limits(output: str) -> Dict[str, Any]:
    """
    Parse system resource limits (DoS protection).
    """
    compliance = []
    non_compliance = []
    limits = {}

    for line in output.strip().split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            limits[key.strip()] = value.strip()

    if limits:
        compliance.append(f"Resource limits configured ({len(limits)} settings)")

        # Check for reasonable limits
        max_files = limits.get('kern.maxfiles', '0')
        try:
            if int(max_files) > 10000:
                compliance.append(f"Max files limit: {max_files}")
        except ValueError:
            pass
    else:
        non_compliance.append("Unable to retrieve resource limits")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=limits,
        summary=f"{len(limits)} resource limits"
    )


def parse_key_management(output: str) -> Dict[str, Any]:
    """
    Parse key/certificate management.
    """
    return parse_certificates(output)  # Reuse existing parser


def parse_mdm_profiles(output: str) -> Dict[str, Any]:
    """
    Parse MDM (Mobile Device Management) profiles.
    """
    compliance = []
    non_compliance = []
    profiles = []

    if "No MDM profiles" in output:
        compliance.append("No MDM profiles - device not enterprise managed (may be expected)")
    else:
        for line in output.strip().split('\n'):
            if line.strip():
                profiles.append(line.strip())

        if profiles:
            compliance.append(f"MDM profiles installed ({len(profiles)})")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"profiles": profiles, "profile_count": len(profiles)},
        summary=f"{len(profiles)} MDM profiles"
    )


def parse_wifi_config(output: str) -> Dict[str, Any]:
    """
    Parse WiFi configuration.
    """
    compliance = []
    non_compliance = []
    wifi_status = {}

    output_lower = output.lower()

    if "on" in output_lower:
        compliance.append("WiFi is enabled")
        wifi_status["wifi_enabled"] = True
    elif "off" in output_lower:
        compliance.append("WiFi is disabled - reduced wireless attack surface")
        wifi_status["wifi_enabled"] = False
    elif "WiFi check" in output:
        compliance.append("WiFi configuration checked")
    else:
        non_compliance.append("Unable to determine WiFi status")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data=wifi_status,
        summary="WiFi " + ("enabled" if wifi_status.get("wifi_enabled") else "disabled/unknown")
    )


# =============================================================================
# Generic Parser (Fallback)
# =============================================================================

def parse_generic_output(output: str) -> Dict[str, Any]:
    """
    Generic parser for unspecified command outputs.
    Provides basic analysis.
    """
    compliance = []
    non_compliance = []

    lines = output.strip().split('\n')
    line_count = len([l for l in lines if l.strip()])

    if line_count > 0:
        compliance.append(f"Command executed successfully ({line_count} lines of output)")

        # Basic checks
        output_lower = output.lower()
        if 'error' in output_lower:
            non_compliance.append("Error indicators in output")
        if 'denied' in output_lower or 'failed' in output_lower:
            non_compliance.append("Access denial or failure indicators in output")
        if 'enabled' in output_lower:
            compliance.append("Enabled status indicators found")
        if 'disabled' in output_lower:
            non_compliance.append("Disabled status indicators found")
    else:
        non_compliance.append("No output from command")

    return create_parser_result(
        compliance_indicators=compliance,
        non_compliance_indicators=non_compliance,
        raw_data={"line_count": line_count, "has_errors": 'error' in output.lower()},
        summary=f"Generic analysis: {line_count} lines"
    )


# =============================================================================
# Parser Registry
# =============================================================================

# Map parser names to functions for dynamic lookup
PARSER_REGISTRY = {
    # Access Control
    "extract_login_entries": extract_login_entries,
    "parse_password_policy": parse_password_policy,
    "parse_user_accounts": parse_user_accounts,
    "parse_admin_access": parse_admin_access,
    "parse_sudo_config": parse_sudo_config,
    "parse_active_sessions": parse_active_sessions,
    "parse_ssh_config": parse_ssh_config,
    "parse_screen_lock": parse_screen_lock,
    "parse_file_permissions": parse_file_permissions,
    "parse_pf_rules": parse_pf_rules,
    "parse_user_groups": parse_user_groups,

    # Audit and Accountability
    "parse_system_logs": parse_system_logs,
    "parse_audit_system": parse_audit_system,
    "parse_audit_files": parse_audit_files,
    "parse_auth_events": parse_auth_events,
    "parse_timestamps": parse_timestamps,
    "parse_log_retention": parse_log_retention,
    "parse_time_sync": parse_time_sync,
    "parse_log_protection": parse_log_protection,
    "parse_log_stats": parse_log_stats,
    "parse_security_alerts": parse_security_alerts,

    # Configuration Management
    "parse_system_info": parse_system_info,
    "parse_baseline_config": parse_baseline_config,
    "parse_config_changes": parse_config_changes,
    "parse_software_inventory": parse_software_inventory,
    "parse_installed_packages": parse_installed_packages,
    "parse_patch_status": parse_patch_status,
    "parse_installed_apps": parse_installed_apps,
    "parse_sip_status": parse_sip_status,
    "parse_running_services": parse_running_services,

    # Identity and Authentication
    "parse_certificates": parse_certificates,
    "parse_keychain_config": parse_keychain_config,
    "parse_auth_identities": parse_auth_identities,
    "parse_smart_cards": parse_smart_cards,
    "parse_biometric_config": parse_biometric_config,
    "parse_mfa_config": parse_mfa_config,
    "parse_replay_protection": parse_replay_protection,

    # Incident Response
    "parse_incident_logs": parse_incident_logs,
    "parse_security_processes": parse_security_processes,
    "parse_monitoring_status": parse_monitoring_status,
    "parse_log_volume": parse_log_volume,
    "parse_containment_rules": parse_containment_rules,
    "parse_security_services": parse_security_services,

    # System and Communications Protection
    "parse_firewall_status": parse_firewall_status,
    "parse_firewall_apps": parse_firewall_apps,
    "parse_filevault_status": parse_filevault_status,
    "parse_network_services": parse_network_services,
    "parse_ssl_certs": parse_ssl_certs,
    "parse_network_connections": parse_network_connections,
    "parse_network_rules": parse_network_rules,
    "parse_active_connections": parse_active_connections,
    "parse_resource_limits": parse_resource_limits,
    "parse_key_management": parse_key_management,
    "parse_mdm_profiles": parse_mdm_profiles,
    "parse_wifi_config": parse_wifi_config,

    # Generic fallback
    "parse_generic_output": parse_generic_output,
}


def get_parser(parser_name: str):
    """
    Get a parser function by name.
    Falls back to generic parser if not found.
    """
    return PARSER_REGISTRY.get(parser_name, parse_generic_output)


def parse_audit_output(output: str, parser_name: str) -> Dict[str, Any]:
    """
    Parse audit command output using the specified parser.

    Args:
        output: Raw command output
        parser_name: Name of the parser to use

    Returns:
        Parsed result dictionary
    """
    parser = get_parser(parser_name)
    try:
        return parser(output)
    except Exception as e:
        return create_parser_result(
            parsed=False,
            non_compliance_indicators=[f"Parser error: {str(e)}"],
            summary=f"Failed to parse with {parser_name}"
        )


# =============================================================================
# Compliance Evaluation Helper
# =============================================================================

def evaluate_compliance(parsed_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluate compliance based on parsed result.

    Returns compliance determination with reasoning.
    """
    compliance_count = len(parsed_result.get("compliance_indicators", []))
    non_compliance_count = len(parsed_result.get("non_compliance_indicators", []))

    if non_compliance_count == 0 and compliance_count > 0:
        status = "compliant"
        confidence = min(0.95, 0.7 + (compliance_count * 0.05))
    elif compliance_count == 0 and non_compliance_count > 0:
        status = "non_compliant"
        confidence = min(0.95, 0.7 + (non_compliance_count * 0.05))
    elif compliance_count > non_compliance_count * 2:
        status = "compliant"
        confidence = 0.7
    elif non_compliance_count > compliance_count * 2:
        status = "non_compliant"
        confidence = 0.7
    else:
        status = "partial"
        confidence = 0.5

    return {
        "compliance_status": status,
        "confidence": confidence,
        "compliance_indicators": parsed_result.get("compliance_indicators", []),
        "non_compliance_indicators": parsed_result.get("non_compliance_indicators", []),
        "reasoning": parsed_result.get("summary", ""),
        "raw_data": parsed_result.get("raw_data", {})
    }


if __name__ == "__main__":
    # Test the parsers
    print("Evidence Parsers for Rwanda NCSA Compliance")
    print("=" * 50)
    print(f"Total parsers registered: {len(PARSER_REGISTRY)}")
    print("\nAvailable parsers:")
    for name in sorted(PARSER_REGISTRY.keys()):
        print(f"  - {name}")
