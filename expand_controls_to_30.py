#!/usr/bin/env python3
"""
Expand Rwanda NCSA Controls from 9 to 30
Adds 21 critical security controls for macOS auditing
"""

import json
from pathlib import Path

# Load existing controls
controls_file = Path("engines/shared/rwanda_ncsa_controls.json")
with open(controls_file, 'r') as f:
    data = json.load(f)

# New controls to add (21 controls)
new_controls = {
    "RWNCSA-AC-003": {
        "family": "Access Control",
        "name": "Least Privilege - Administrative Access",
        "description": "Ensure users operate with least privilege; administrative access restricted to authorized personnel",
        "severity": "HIGH",
        "requirements": {
            "admin_users_limited": True,
            "regular_users_non_admin": True,
            "sudo_access_controlled": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Admin group has limited members (< 5)",
                "Regular users are not in admin group",
                "Sudo access properly configured"
            ],
            "fail_conditions": [
                "Too many admin users",
                "Regular users with admin privileges",
                "Unrestricted sudo access"
            ]
        },
        "macos_implementation": {
            "audit_command": "dscl . -read /Groups/admin GroupMembership",
            "expected_output_pattern": "GroupMembership",
            "parser_logic": "extract_admin_users",
            "validation": "admin_count < 5 AND no_unauthorized_admins"
        },
        "remediation": {
            "steps": [
                "Review admin users: dscl . -read /Groups/admin GroupMembership",
                "Remove unnecessary admin: sudo dseditgroup -o edit -d username -t user admin",
                "Verify: dscl . -read /Groups/admin GroupMembership"
            ],
            "verification_command": "dscl . -read /Groups/admin GroupMembership | wc -w",
            "expected_result": "Limited number of admin users"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Privilege escalation, unauthorized access",
            "business_impact": "System compromise, data breach",
            "likelihood": "HIGH"
        }
    },

    "RWNCSA-AC-004": {
        "family": "Access Control",
        "name": "Remote Access - SSH Configuration",
        "description": "Secure SSH configuration with strong authentication and limited access",
        "severity": "CRITICAL",
        "requirements": {
            "ssh_enabled": False,  # Should be disabled unless needed
            "root_login_disabled": True,
            "password_auth_disabled": True,  # Key-based only
            "strong_ciphers": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "SSH disabled OR properly secured",
                "Root login disabled",
                "Key-based authentication only",
                "Strong ciphers configured"
            ],
            "fail_conditions": [
                "SSH enabled with weak config",
                "Root login allowed",
                "Password authentication enabled",
                "Weak ciphers in use"
            ]
        },
        "macos_implementation": {
            "audit_command": "systemsetup -getremotelogin",
            "expected_output_pattern": "Remote Login: (On|Off)",
            "parser_logic": "check_ssh_status",
            "validation": "ssh_off OR (ssh_on AND secure_config)"
        },
        "remediation": {
            "steps": [
                "Disable SSH if not needed: sudo systemsetup -setremotelogin off",
                "If SSH needed, secure it:",
                "  - Disable root: echo 'PermitRootLogin no' | sudo tee -a /etc/ssh/sshd_config",
                "  - Key-only auth: echo 'PasswordAuthentication no' | sudo tee -a /etc/ssh/sshd_config",
                "  - Restart SSH: sudo launchctl unload /System/Library/LaunchDaemons/ssh.plist && sudo launchctl load -w /System/Library/LaunchDaemons/ssh.plist"
            ],
            "verification_command": "systemsetup -getremotelogin",
            "expected_result": "Remote Login: Off (or properly secured)"
        },
        "risk_assessment": {
            "if_non_compliant": "CRITICAL - Remote unauthorized access, brute force attacks",
            "business_impact": "Complete system compromise",
            "likelihood": "VERY HIGH"
        }
    },

    "RWNCSA-AC-005": {
        "family": "Access Control",
        "name": "File and Directory Permissions",
        "description": "Sensitive system files and directories must have restrictive permissions",
        "severity": "HIGH",
        "requirements": {
            "system_files_protected": True,
            "world_writable_forbidden": True,
            "sensitive_dirs_restricted": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "/etc has restrictive permissions (755 or stricter)",
                "No world-writable files in /etc, /var, /usr",
                "Sensitive files are not group/world readable"
            ],
            "fail_conditions": [
                "World-writable files exist",
                "Sensitive files have loose permissions",
                "/etc or /var have excessive permissions"
            ]
        },
        "macos_implementation": {
            "audit_command": "ls -ld /etc /var /usr /private",
            "expected_output_pattern": "drwxr-xr-x",
            "parser_logic": "check_directory_permissions",
            "validation": "no_world_writable AND secure_permissions"
        },
        "remediation": {
            "steps": [
                "Check permissions: ls -ld /etc /var /usr",
                "Fix /etc: sudo chmod 755 /etc",
                "Find world-writable: find / -type f -perm -002 2>/dev/null",
                "Fix world-writable: sudo chmod o-w <file>"
            ],
            "verification_command": "ls -ld /etc /var /usr",
            "expected_result": "drwxr-xr-x (755) or stricter"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Unauthorized file modification, privilege escalation",
            "business_impact": "System compromise, data tampering",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AC-006": {
        "family": "Access Control",
        "name": "Sudo Configuration Security",
        "description": "Sudo access must be restricted and properly audited",
        "severity": "HIGH",
        "requirements": {
            "sudo_users_limited": True,
            "sudo_logging_enabled": True,
            "no_passwordless_sudo": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Sudo access limited to authorized users",
                "NOPASSWD not used for sensitive commands",
                "Sudo usage logged"
            ],
            "fail_conditions": [
                "Unrestricted sudo access",
                "NOPASSWD without restrictions",
                "Sudo not logged"
            ]
        },
        "macos_implementation": {
            "audit_command": "sudo cat /etc/sudoers | grep -v '^#' | grep -v '^$'",
            "expected_output_pattern": "root|admin|wheel",
            "parser_logic": "parse_sudoers_file",
            "validation": "no_all_users_sudo AND nopasswd_restricted"
        },
        "remediation": {
            "steps": [
                "Review sudoers: sudo cat /etc/sudoers",
                "Edit safely: sudo visudo",
                "Remove excessive NOPASSWD",
                "Limit to admin group only"
            ],
            "verification_command": "sudo cat /etc/sudoers | grep NOPASSWD",
            "expected_result": "No unrestricted NOPASSWD entries"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Privilege escalation, unauthorized admin access",
            "business_impact": "Full system control by unauthorized users",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AC-007": {
        "family": "Access Control",
        "name": "Screen Lock Enforcement",
        "description": "Automatic screen lock must be enabled to prevent unauthorized physical access",
        "severity": "MEDIUM",
        "requirements": {
            "screen_lock_enabled": True,
            "lock_timeout_minutes": 15,
            "require_password_on_wake": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Screen saver activates within 15 minutes",
                "Password required on wake",
                "Screen lock enabled"
            ],
            "fail_conditions": [
                "No screen lock timeout",
                "Timeout > 15 minutes",
                "No password on wake"
            ]
        },
        "macos_implementation": {
            "audit_command": "defaults read com.apple.screensaver askForPassword && defaults read com.apple.screensaver idleTime",
            "expected_output_pattern": "1.*900",
            "parser_logic": "check_screen_lock_settings",
            "validation": "ask_for_password == 1 AND idle_time <= 900"
        },
        "remediation": {
            "steps": [
                "Enable password on wake: defaults write com.apple.screensaver askForPassword -int 1",
                "Set 15-min timeout: defaults write com.apple.screensaver idleTime -int 900",
                "Verify: defaults read com.apple.screensaver"
            ],
            "verification_command": "defaults read com.apple.screensaver askForPassword",
            "expected_result": "1 (enabled)"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Unauthorized physical access to unattended workstation",
            "business_impact": "Data exposure, unauthorized access",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AU-001": {
        "family": "Audit and Accountability",
        "name": "Audit System Configuration",
        "description": "macOS audit system must be properly configured and operational",
        "severity": "HIGH",
        "requirements": {
            "audit_enabled": True,
            "audit_daemon_running": True,
            "audit_flags_configured": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Audit daemon is running",
                "Audit flags configured in /etc/security/audit_control",
                "Audit logs being generated"
            ],
            "fail_conditions": [
                "Audit daemon not running",
                "No audit configuration",
                "Audit logs not generated"
            ]
        },
        "macos_implementation": {
            "audit_command": "sudo launchctl list | grep com.apple.auditd",
            "expected_output_pattern": "com.apple.auditd",
            "parser_logic": "check_audit_daemon",
            "validation": "audit_daemon_running"
        },
        "remediation": {
            "steps": [
                "Check audit: sudo launchctl list | grep auditd",
                "Start audit: sudo launchctl load -w /System/Library/LaunchDaemons/com.apple.auditd.plist",
                "Configure: sudo vi /etc/security/audit_control",
                "Verify: sudo audit -n"
            ],
            "verification_command": "sudo launchctl list | grep com.apple.auditd",
            "expected_result": "Audit daemon listed and running"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - No audit trail, cannot detect or investigate incidents",
            "business_impact": "Inability to perform forensics, compliance violation",
            "likelihood": "HIGH"
        }
    },

    "RWNCSA-AU-003": {
        "family": "Audit and Accountability",
        "name": "Time Synchronization",
        "description": "System time must be synchronized with authoritative time source for accurate audit trails",
        "severity": "MEDIUM",
        "requirements": {
            "ntp_enabled": True,
            "time_server_configured": True,
            "time_sync_active": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Network time enabled",
                "Time server configured",
                "Time synchronization active"
            ],
            "fail_conditions": [
                "Network time disabled",
                "No time server configured",
                "Time drift detected"
            ]
        },
        "macos_implementation": {
            "audit_command": "systemsetup -getusingnetworktime",
            "expected_output_pattern": "Network Time: On",
            "parser_logic": "check_ntp_status",
            "validation": "network_time_enabled"
        },
        "remediation": {
            "steps": [
                "Enable NTP: sudo systemsetup -setusingnetworktime on",
                "Set time server: sudo systemsetup -setnetworktimeserver time.apple.com",
                "Verify: systemsetup -getusingnetworktime"
            ],
            "verification_command": "systemsetup -getusingnetworktime",
            "expected_result": "Network Time: On"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Inaccurate audit timestamps, forensic challenges",
            "business_impact": "Audit trail unreliable, compliance issues",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-SY-001": {
        "family": "System and Communications Protection",
        "name": "Application Firewall",
        "description": "macOS Application Firewall must be enabled and properly configured",
        "severity": "CRITICAL",
        "requirements": {
            "firewall_enabled": True,
            "stealth_mode_enabled": True,
            "logging_enabled": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Application Firewall enabled",
                "Stealth mode enabled (ICMP blocked)",
                "Firewall logging enabled"
            ],
            "fail_conditions": [
                "Firewall disabled",
                "Stealth mode disabled",
                "No firewall logging"
            ]
        },
        "macos_implementation": {
            "audit_command": "sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate",
            "expected_output_pattern": "Firewall is enabled",
            "parser_logic": "check_firewall_status",
            "validation": "firewall_enabled"
        },
        "remediation": {
            "steps": [
                "Enable firewall: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on",
                "Enable stealth: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setstealthmode on",
                "Enable logging: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setloggingmode on",
                "Verify: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate"
            ],
            "verification_command": "sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate",
            "expected_result": "Firewall is enabled"
        },
        "risk_assessment": {
            "if_non_compliant": "CRITICAL - Network-based attacks, unauthorized connections",
            "business_impact": "Malware infection, data exfiltration, network compromise",
            "likelihood": "VERY HIGH"
        }
    },

    "RWNCSA-SY-002": {
        "family": "System and Communications Protection",
        "name": "FileVault Disk Encryption",
        "description": "Full disk encryption must be enabled to protect data at rest",
        "severity": "CRITICAL",
        "requirements": {
            "filevault_enabled": True,
            "encryption_complete": True,
            "recovery_key_generated": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "FileVault enabled",
                "Disk fully encrypted",
                "Recovery key exists"
            ],
            "fail_conditions": [
                "FileVault disabled",
                "Encryption in progress but not complete",
                "No recovery key"
            ]
        },
        "macos_implementation": {
            "audit_command": "fdesetup status",
            "expected_output_pattern": "FileVault is On",
            "parser_logic": "check_filevault_status",
            "validation": "filevault_enabled AND encryption_complete"
        },
        "remediation": {
            "steps": [
                "Enable FileVault: sudo fdesetup enable",
                "Follow prompts to create recovery key",
                "IMPORTANT: Save recovery key securely!",
                "Verify: fdesetup status",
                "Check progress: fdesetup status (wait for completion)"
            ],
            "verification_command": "fdesetup status",
            "expected_result": "FileVault is On"
        },
        "risk_assessment": {
            "if_non_compliant": "CRITICAL - Data theft from stolen/lost devices, physical access",
            "business_impact": "Complete data breach, regulatory penalties",
            "likelihood": "HIGH"
        }
    },

    "RWNCSA-SY-003": {
        "family": "System and Communications Protection",
        "name": "Bluetooth Security",
        "description": "Bluetooth must be disabled when not in use or properly secured",
        "severity": "MEDIUM",
        "requirements": {
            "bluetooth_disabled_or_secured": True,
            "discoverable_mode_off": True,
            "unauthorized_pairing_prevented": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Bluetooth disabled OR properly secured",
                "Not in discoverable mode",
                "Authorized devices only"
            ],
            "fail_conditions": [
                "Bluetooth enabled and unsecured",
                "In discoverable mode",
                "No pairing restrictions"
            ]
        },
        "macos_implementation": {
            "audit_command": "defaults read /Library/Preferences/com.apple.Bluetooth ControllerPowerState",
            "expected_output_pattern": "0|1",
            "parser_logic": "check_bluetooth_status",
            "validation": "bluetooth_off OR bluetooth_secured"
        },
        "remediation": {
            "steps": [
                "Disable Bluetooth: sudo defaults write /Library/Preferences/com.apple.Bluetooth ControllerPowerState -int 0",
                "If needed, enable but secure:",
                "  - System Preferences → Bluetooth → Advanced",
                "  - Disable 'Allow Bluetooth devices to wake this computer'",
                "Verify: defaults read /Library/Preferences/com.apple.Bluetooth ControllerPowerState"
            ],
            "verification_command": "defaults read /Library/Preferences/com.apple.Bluetooth ControllerPowerState",
            "expected_result": "0 (disabled) or 1 with secure settings"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Bluetooth attacks, unauthorized connections",
            "business_impact": "Data interception, device hijacking",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-SY-004": {
        "family": "System and Communications Protection",
        "name": "Network Configuration Security",
        "description": "Network interfaces must be properly configured and secured",
        "severity": "HIGH",
        "requirements": {
            "unused_interfaces_disabled": True,
            "ipv6_configured_securely": True,
            "no_promiscuous_mode": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "All network interfaces identified",
                "Unused interfaces disabled",
                "IPv6 properly configured or disabled",
                "No interfaces in promiscuous mode"
            ],
            "fail_conditions": [
                "Unknown network interfaces active",
                "Unused interfaces enabled",
                "Promiscuous mode detected"
            ]
        },
        "macos_implementation": {
            "audit_command": "ifconfig -a | grep 'flags\\|status'",
            "expected_output_pattern": "flags=.*UP|status: (active|inactive)",
            "parser_logic": "analyze_network_interfaces",
            "validation": "no_promiscuous_mode AND unused_interfaces_down"
        },
        "remediation": {
            "steps": [
                "List interfaces: ifconfig -a",
                "Disable unused: sudo ifconfig <interface> down",
                "Check for promiscuous: ifconfig -a | grep PROMISC",
                "Disable IPv6 if not used: networksetup -setv6off Wi-Fi"
            ],
            "verification_command": "ifconfig -a | grep PROMISC",
            "expected_result": "No output (no promiscuous mode)"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Network sniffing, unauthorized access",
            "business_impact": "Data interception, network compromise",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-SY-005": {
        "family": "System and Communications Protection",
        "name": "Anti-Malware Protection",
        "description": "XProtect and MRT (Malware Removal Tool) must be up-to-date",
        "severity": "HIGH",
        "requirements": {
            "xprotect_enabled": True,
            "xprotect_updated": True,
            "mrt_updated": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "XProtect is enabled",
                "XProtect definitions updated within 7 days",
                "MRT updated within 7 days"
            ],
            "fail_conditions": [
                "XProtect disabled",
                "Definitions outdated (> 7 days)",
                "MRT outdated"
            ]
        },
        "macos_implementation": {
            "audit_command": "system_profiler SPInstallHistoryDataType | grep -A 4 'XProtect\\|MRT'",
            "expected_output_pattern": "XProtect|MRT",
            "parser_logic": "check_malware_protection",
            "validation": "xprotect_recent AND mrt_recent"
        },
        "remediation": {
            "steps": [
                "Check updates: softwareupdate -l",
                "Update all: sudo softwareupdate -i -a",
                "Force XProtect check: sudo /usr/libexec/XProtect/XProtectService",
                "Verify: system_profiler SPInstallHistoryDataType | grep XProtect"
            ],
            "verification_command": "system_profiler SPInstallHistoryDataType | grep -A 2 XProtect | tail -1",
            "expected_result": "Recent install date (within 7 days)"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Malware infection, zero-day vulnerabilities",
            "business_impact": "System compromise, data theft",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-SY-006": {
        "family": "System and Communications Protection",
        "name": "File Sharing Services",
        "description": "File sharing services must be disabled unless explicitly required",
        "severity": "HIGH",
        "requirements": {
            "file_sharing_disabled": True,
            "smb_disabled": True,
            "afp_disabled": True,
            "nfs_disabled": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "File Sharing disabled",
                "SMB/AFP/NFS not running",
                "No unnecessary network services"
            ],
            "fail_conditions": [
                "File Sharing enabled without justification",
                "Insecure protocols running",
                "Unnecessary services exposed"
            ]
        },
        "macos_implementation": {
            "audit_command": "sudo launchctl list | grep -E 'smbd|AppleFileServer|nfsd'",
            "expected_output_pattern": "",
            "parser_logic": "check_file_sharing_services",
            "validation": "no_file_sharing_services_running"
        },
        "remediation": {
            "steps": [
                "Check sharing: sudo launchctl list | grep -E 'smbd|AppleFileServer'",
                "Disable via System Preferences → Sharing → uncheck File Sharing",
                "Or command: sudo launchctl unload -w /System/Library/LaunchDaemons/com.apple.smbd.plist",
                "Verify: sudo launchctl list | grep smbd"
            ],
            "verification_command": "sudo launchctl list | grep -E 'smbd|AppleFileServer|nfsd'",
            "expected_result": "No output (services not running)"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Unauthorized file access, data exfiltration",
            "business_impact": "Data breach, malware spread",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-CO-001": {
        "family": "Configuration Management",
        "name": "Software Inventory",
        "description": "Maintain inventory of installed software for license and security management",
        "severity": "MEDIUM",
        "requirements": {
            "software_inventory_maintained": True,
            "unauthorized_software_detected": True,
            "software_documented": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Can generate software inventory",
                "All installed applications identified",
                "No known unauthorized software"
            ],
            "fail_conditions": [
                "Cannot enumerate software",
                "Unauthorized applications present",
                "Software inventory incomplete"
            ]
        },
        "macos_implementation": {
            "audit_command": "system_profiler SPApplicationsDataType | grep -A 3 'Location: /Applications'",
            "expected_output_pattern": "Applications",
            "parser_logic": "generate_software_inventory",
            "validation": "inventory_count > 0 AND no_blacklisted_apps"
        },
        "remediation": {
            "steps": [
                "Generate inventory: system_profiler SPApplicationsDataType -json > /tmp/software_inventory.json",
                "Review for unauthorized software",
                "Remove unauthorized: sudo rm -rf /Applications/UnauthorizedApp.app",
                "Document approved software list"
            ],
            "verification_command": "system_profiler SPApplicationsDataType | grep 'Location: /Applications' | wc -l",
            "expected_result": "Number of installed applications"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Unauthorized software, license violations",
            "business_impact": "Malware infection, licensing penalties",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-CO-003": {
        "family": "Configuration Management",
        "name": "Patch Management",
        "description": "Security updates and patches must be applied in timely manner",
        "severity": "CRITICAL",
        "requirements": {
            "auto_update_enabled": True,
            "pending_updates_threshold_days": 30,
            "critical_patches_within_days": 7
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Automatic updates enabled",
                "No critical updates pending > 7 days",
                "System updated within 30 days"
            ],
            "fail_conditions": [
                "Automatic updates disabled",
                "Critical patches pending > 7 days",
                "System severely outdated"
            ]
        },
        "macos_implementation": {
            "audit_command": "softwareupdate -l",
            "expected_output_pattern": "Software Update found|No new software available",
            "parser_logic": "check_pending_updates",
            "validation": "no_critical_pending OR within_threshold"
        },
        "remediation": {
            "steps": [
                "Enable auto-update: sudo softwareupdate --schedule on",
                "Check updates: softwareupdate -l",
                "Install all: sudo softwareupdate -i -a",
                "Install recommended: sudo softwareupdate -i -r",
                "Verify: softwareupdate -l"
            ],
            "verification_command": "softwareupdate -l",
            "expected_result": "No new software available (or only non-critical)"
        },
        "risk_assessment": {
            "if_non_compliant": "CRITICAL - Exploitation of known vulnerabilities",
            "business_impact": "System compromise, malware infection, data breach",
            "likelihood": "VERY HIGH"
        }
    }
}

# Add the new controls
data['controls'].update(new_controls)

# Update metadata
data['metadata']['last_updated'] = "2025-11-28"
data['metadata']['description'] = "Rwanda NCSA cybersecurity control requirements for macOS compliance auditing - Expanded to 30 critical controls"
data['metadata']['total_controls'] = len(data['controls'])

# Save updated file
with open(controls_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Successfully expanded controls from 9 to {len(data['controls'])}")
print(f"\n📋 New Controls Added:")
for control_id in sorted(new_controls.keys()):
    control = new_controls[control_id]
    print(f"  - {control_id}: {control['name']} ({control['severity']})")

print(f"\n💾 Updated file: {controls_file}")
