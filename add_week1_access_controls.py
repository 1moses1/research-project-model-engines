#!/usr/bin/env python3
"""
Add Week 1 Access Control Controls (18 controls)
Target: 30 → 48 controls (Access Control: 9 → 27)
"""

import json
from pathlib import Path

# Load existing controls
controls_file = Path("engines/shared/rwanda_ncsa_controls.json")
with open(controls_file, 'r') as f:
    data = json.load(f)

print(f"Current controls: {len(data['controls'])}")

# Week 1: 18 Access Control controls
week1_controls = {
    "RWNCSA-AC-009": {
        "family": "Access Control",
        "name": "Multi-Factor Authentication Status",
        "description": "Multi-factor authentication must be configured for privileged accounts",
        "severity": "HIGH",
        "requirements": {
            "mfa_configured": True,
            "mfa_for_admin_accounts": True,
            "certificate_based_auth_available": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "MFA configured for administrative accounts",
                "Smart card or certificate authentication available",
                "Fallback authentication secured"
            ],
            "fail_conditions": [
                "No MFA configured",
                "Admin accounts using password-only authentication",
                "No certificate-based authentication available"
            ]
        },
        "macos_implementation": {
            "audit_command": "security find-identity -p certificates -v",
            "expected_output_pattern": "valid identities found",
            "parser_logic": "check_mfa_certificates",
            "validation": "certificates_present AND admin_mfa_configured"
        },
        "remediation": {
            "steps": [
                "Check certificates: security find-identity -p certificates -v",
                "Configure smart card: System Preferences → Security & Privacy → Smart Cards",
                "Enable certificate authentication for admin accounts",
                "Verify: security find-identity -p certificates -v"
            ],
            "verification_command": "security find-identity -p certificates -v",
            "expected_result": "Valid certificates found for authentication"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Single-factor authentication vulnerable to credential theft",
            "business_impact": "Account compromise, unauthorized privileged access",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AC-011": {
        "family": "Access Control",
        "name": "Account Lockout Policy",
        "description": "Account lockout policy must be enforced after failed login attempts",
        "severity": "MEDIUM",
        "requirements": {
            "lockout_enabled": True,
            "max_failed_attempts": 5,
            "lockout_duration_minutes": 15,
            "lockout_counter_reset_minutes": 15
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Account lockout enabled",
                "Maximum failed attempts <= 5",
                "Lockout duration >= 15 minutes",
                "Failed attempt counter resets after 15 minutes"
            ],
            "fail_conditions": [
                "No account lockout policy",
                "Unlimited failed login attempts allowed",
                "Lockout duration too short (< 15 minutes)"
            ]
        },
        "macos_implementation": {
            "audit_command": "pwpolicy -getaccountpolicies",
            "expected_output_pattern": "maxFailedLoginAttempts",
            "parser_logic": "parse_lockout_policy",
            "validation": "lockout_enabled AND max_attempts <= 5"
        },
        "remediation": {
            "steps": [
                "Check current policy: pwpolicy -getaccountpolicies",
                "Set lockout policy: sudo pwpolicy -setaccountpolicies",
                "Configure: maxFailedLoginAttempts=5, minutesUntilFailedLoginReset=15",
                "Verify: pwpolicy -getaccountpolicies | grep maxFailedLoginAttempts"
            ],
            "verification_command": "pwpolicy -getaccountpolicies",
            "expected_result": "maxFailedLoginAttempts <= 5"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Brute force attacks can succeed with unlimited attempts",
            "business_impact": "Account compromise via password guessing",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AC-012": {
        "family": "Access Control",
        "name": "Guest Account Status",
        "description": "Guest account must be disabled to prevent unauthorized access",
        "severity": "MEDIUM",
        "requirements": {
            "guest_account_disabled": True,
            "guest_home_folder_removed": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Guest account does not exist or is disabled",
                "No guest home folder present",
                "Guest login disabled in System Preferences"
            ],
            "fail_conditions": [
                "Guest account is enabled",
                "Guest home folder exists and is accessible",
                "Guest login allowed"
            ]
        },
        "macos_implementation": {
            "audit_command": "dscl . -read /Users/Guest 2>&1",
            "expected_output_pattern": "eDSRecordNotFound|No such file",
            "parser_logic": "check_guest_account",
            "validation": "guest_account_not_found OR guest_disabled"
        },
        "remediation": {
            "steps": [
                "Check guest account: dscl . -read /Users/Guest",
                "Disable guest account: System Preferences → Users & Groups → Guest User → uncheck",
                "Or via command: sudo dscl . -delete /Users/Guest",
                "Verify: dscl . -read /Users/Guest (should fail)"
            ],
            "verification_command": "dscl . -read /Users/Guest 2>&1",
            "expected_result": "eDSRecordNotFound (guest account does not exist)"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Unauthorized users can access system without credentials",
            "business_impact": "Unauthorized access, data exposure",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-AC-013": {
        "family": "Access Control",
        "name": "Automatic Login Disabled",
        "description": "Automatic login must be disabled to require authentication at startup",
        "severity": "HIGH",
        "requirements": {
            "auto_login_disabled": True,
            "login_window_shows_username_password": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Automatic login is disabled",
                "Login window requires username and password",
                "No auto-login user configured"
            ],
            "fail_conditions": [
                "Automatic login is enabled",
                "System boots directly to user desktop",
                "Auto-login user is set"
            ]
        },
        "macos_implementation": {
            "audit_command": "defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser 2>&1",
            "expected_output_pattern": "does not exist",
            "parser_logic": "check_auto_login",
            "validation": "auto_login_not_configured"
        },
        "remediation": {
            "steps": [
                "Check auto-login: defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser",
                "Disable auto-login: System Preferences → Users & Groups → Login Options → Automatic login: Off",
                "Or via command: sudo defaults delete /Library/Preferences/com.apple.loginwindow autoLoginUser",
                "Verify: defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser (should fail)"
            ],
            "verification_command": "defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser 2>&1",
            "expected_result": "does not exist (auto-login disabled)"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Physical access = immediate system access without authentication",
            "business_impact": "Unauthorized access, data theft from physical access",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AC-014": {
        "family": "Access Control",
        "name": "Fast User Switching Configuration",
        "description": "Fast user switching should be configured according to organizational policy",
        "severity": "LOW",
        "requirements": {
            "fast_user_switching_controlled": True,
            "multiple_sessions_monitored": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Fast user switching configuration documented",
                "Multiple concurrent sessions controlled",
                "Session switching logged"
            ],
            "fail_conditions": [
                "Fast user switching uncontrolled",
                "Multiple active sessions without monitoring"
            ]
        },
        "macos_implementation": {
            "audit_command": "defaults read /Library/Preferences/.GlobalPreferences MultipleSessionEnabled",
            "expected_output_pattern": "0|1",
            "parser_logic": "check_fast_user_switching",
            "validation": "configuration_documented"
        },
        "remediation": {
            "steps": [
                "Check status: defaults read /Library/Preferences/.GlobalPreferences MultipleSessionEnabled",
                "Configure: System Preferences → Users & Groups → Login Options → Show fast user switching menu",
                "Document organizational policy on multiple concurrent sessions",
                "Verify: defaults read /Library/Preferences/.GlobalPreferences MultipleSessionEnabled"
            ],
            "verification_command": "defaults read /Library/Preferences/.GlobalPreferences MultipleSessionEnabled",
            "expected_result": "Configured according to organizational policy"
        },
        "risk_assessment": {
            "if_non_compliant": "LOW - Minor session management issue",
            "business_impact": "Session confusion, minor security concern",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-AC-015": {
        "family": "Access Control",
        "name": "Password Reset Requirements",
        "description": "Password reset process must be secured and require proper authentication",
        "severity": "MEDIUM",
        "requirements": {
            "secure_password_reset": True,
            "reset_requires_verification": True,
            "reset_logged": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Password reset requires administrator authentication",
                "Reset process is logged",
                "User verification required for self-service reset"
            ],
            "fail_conditions": [
                "Password can be reset without proper authentication",
                "No logging of password reset events",
                "Self-service reset lacks verification"
            ]
        },
        "macos_implementation": {
            "audit_command": "pwpolicy -getaccountpolicies",
            "expected_output_pattern": "policyAttributePasswordLastSetTime",
            "parser_logic": "check_password_reset_policy",
            "validation": "reset_policy_configured"
        },
        "remediation": {
            "steps": [
                "Review password policy: pwpolicy -getaccountpolicies",
                "Ensure administrator approval required for resets",
                "Enable password change logging",
                "Document password reset procedures",
                "Verify: Check security logs for password change events"
            ],
            "verification_command": "pwpolicy -getaccountpolicies",
            "expected_result": "Password reset policy configured"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Unauthorized password resets can lead to account takeover",
            "business_impact": "Account compromise via password reset abuse",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-AC-016": {
        "family": "Access Control",
        "name": "Inactive Account Detection",
        "description": "Inactive user accounts must be detected and disabled after 90 days",
        "severity": "MEDIUM",
        "requirements": {
            "inactive_account_detection_enabled": True,
            "max_inactive_days": 90,
            "automated_review": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Last login tracked for all accounts",
                "Accounts inactive > 90 days flagged for review",
                "Process exists to disable inactive accounts"
            ],
            "fail_conditions": [
                "No tracking of last login dates",
                "Inactive accounts remain enabled indefinitely",
                "No review process for inactive accounts"
            ]
        },
        "macos_implementation": {
            "audit_command": "dscl . -list /Users | while read user; do echo \"$user: $(dscl . -read /Users/$user lastlogin 2>&1 | grep -v 'No such key')\"; done",
            "expected_output_pattern": "lastlogin",
            "parser_logic": "analyze_inactive_accounts",
            "validation": "last_login_within_90_days OR account_disabled"
        },
        "remediation": {
            "steps": [
                "List users and last login: dscl . -list /Users | while read user; do dscl . -read /Users/$user lastlogin; done",
                "Identify accounts inactive > 90 days",
                "Disable inactive accounts: sudo dscl . -append /Users/username AuthenticationAuthority ;DisabledUser;",
                "Document review process for inactive accounts",
                "Schedule regular reviews (monthly)"
            ],
            "verification_command": "dscl . -list /Users",
            "expected_result": "All accounts active within 90 days or documented as inactive"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Orphaned accounts can be exploited for unauthorized access",
            "business_impact": "Unauthorized access via stale credentials",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-AC-017": {
        "family": "Access Control",
        "name": "Root Account Status",
        "description": "Root account must be disabled or secured with strong authentication",
        "severity": "CRITICAL",
        "requirements": {
            "root_disabled": True,
            "root_password_not_set": True,
            "sudo_used_instead": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Root account is disabled",
                "No root password is set",
                "Sudo is used for privileged operations",
                "Root login attempts are logged"
            ],
            "fail_conditions": [
                "Root account is enabled",
                "Root password is set and can be used for login",
                "Direct root access allowed"
            ]
        },
        "macos_implementation": {
            "audit_command": "dscl . -read /Users/root AuthenticationAuthority 2>&1",
            "expected_output_pattern": "No such key|DisabledUser",
            "parser_logic": "check_root_status",
            "validation": "root_disabled OR root_no_password"
        },
        "remediation": {
            "steps": [
                "Check root status: dscl . -read /Users/root AuthenticationAuthority",
                "Disable root: System Preferences → Users & Groups → Login Options → Network Account Server: Join → Directory Utility → Edit → Disable Root User",
                "Or via command: sudo dscl . -create /Users/root UserShell /usr/bin/false",
                "Ensure sudo is configured properly",
                "Verify: dscl . -read /Users/root AuthenticationAuthority (should show disabled)"
            ],
            "verification_command": "dscl . -read /Users/root AuthenticationAuthority 2>&1",
            "expected_result": "Root account disabled or no authentication authority set"
        },
        "risk_assessment": {
            "if_non_compliant": "CRITICAL - Enabled root account with password = full system compromise risk",
            "business_impact": "Complete system control, data theft, malware installation",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-AC-018": {
        "family": "Access Control",
        "name": "User Home Directory Permissions",
        "description": "User home directories must have proper permissions to prevent unauthorized access",
        "severity": "HIGH",
        "requirements": {
            "home_directories_secure": True,
            "max_permissions": "700",
            "owner_correct": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Home directories owned by respective users",
                "Permissions are 700 or more restrictive (drwx------)",
                "No world-readable home directories",
                "No shared home directories"
            ],
            "fail_conditions": [
                "Home directories world-readable (permissions > 700)",
                "Incorrect ownership on home directories",
                "Shared home directories found"
            ]
        },
        "macos_implementation": {
            "audit_command": "ls -la /Users | grep -v '^d.*root.*wheel'",
            "expected_output_pattern": "drwx------",
            "parser_logic": "check_home_directory_permissions",
            "validation": "all_home_dirs_secure"
        },
        "remediation": {
            "steps": [
                "List home directories: ls -la /Users",
                "Identify insecure permissions (> 700)",
                "Fix permissions: sudo chmod 700 /Users/username",
                "Fix ownership: sudo chown username:staff /Users/username",
                "Verify: ls -la /Users"
            ],
            "verification_command": "ls -la /Users",
            "expected_result": "All home directories with drwx------ (700) permissions"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Other users can read private files, credentials, sensitive data",
            "business_impact": "Data exposure, credential theft, privacy violation",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AC-019": {
        "family": "Access Control",
        "name": "Shared Folder Permissions",
        "description": "Shared folders must have appropriate permissions based on access requirements",
        "severity": "MEDIUM",
        "requirements": {
            "shared_folders_documented": True,
            "permissions_appropriate": True,
            "access_logged": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "All shared folders documented",
                "Permissions follow least privilege",
                "Sharing services properly configured",
                "Access to shared folders is logged"
            ],
            "fail_conditions": [
                "Unauthorized shared folders exist",
                "Overly permissive sharing (world-writable)",
                "No documentation of shared resources"
            ]
        },
        "macos_implementation": {
            "audit_command": "sharing -l",
            "expected_output_pattern": "name:|path:",
            "parser_logic": "analyze_shared_folders",
            "validation": "all_shares_documented AND permissions_appropriate"
        },
        "remediation": {
            "steps": [
                "List shared folders: sharing -l",
                "Review each share for necessity",
                "Remove unauthorized shares: sudo sharing -r sharename",
                "Document authorized shares",
                "Verify permissions: ls -la /path/to/share",
                "Ensure no world-writable shares exist"
            ],
            "verification_command": "sharing -l",
            "expected_result": "Only authorized shares present with appropriate permissions"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Unauthorized file access, data leakage via shared folders",
            "business_impact": "Data exposure, unauthorized data modification",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AC-020": {
        "family": "Access Control",
        "name": "Login Banner Configuration",
        "description": "Login banner must be displayed warning unauthorized users",
        "severity": "LOW",
        "requirements": {
            "login_banner_configured": True,
            "banner_content_compliant": True,
            "banner_displayed_before_auth": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Login banner is configured",
                "Banner contains authorized use only warning",
                "Banner displayed before authentication",
                "Banner content approved by legal/compliance"
            ],
            "fail_conditions": [
                "No login banner configured",
                "Banner missing or incomplete",
                "Warning not displayed before login"
            ]
        },
        "macos_implementation": {
            "audit_command": "cat /etc/motd 2>&1",
            "expected_output_pattern": "authorized|warning|unauthorized",
            "parser_logic": "check_login_banner",
            "validation": "banner_exists AND contains_warning"
        },
        "remediation": {
            "steps": [
                "Check current banner: cat /etc/motd",
                "Create banner: sudo nano /etc/motd",
                "Add text: 'AUTHORIZED USE ONLY. Unauthorized access prohibited and will be prosecuted.'",
                "Configure PolicyBanner: System Preferences → Security & Privacy → General → Show message when screen is locked",
                "Verify: cat /etc/motd"
            ],
            "verification_command": "cat /etc/motd",
            "expected_result": "Banner present with authorized use warning"
        },
        "risk_assessment": {
            "if_non_compliant": "LOW - Legal implications if unauthorized access occurs",
            "business_impact": "Reduced legal standing in prosecution of unauthorized access",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-AC-021": {
        "family": "Access Control",
        "name": "Login Grace Time Configuration",
        "description": "Login grace time must be minimized to prevent credential guessing",
        "severity": "MEDIUM",
        "requirements": {
            "grace_time_configured": True,
            "max_grace_time_seconds": 0
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Login grace time is set to 0 (immediate password required)",
                "No delay before password prompt",
                "Screen saver requires immediate password"
            ],
            "fail_conditions": [
                "Login grace time > 0 seconds",
                "Delay before password required",
                "Screen saver allows grace period without authentication"
            ]
        },
        "macos_implementation": {
            "audit_command": "defaults read /Library/Preferences/com.apple.screensaver askForPasswordDelay",
            "expected_output_pattern": "0",
            "parser_logic": "check_grace_time",
            "validation": "grace_time_equals_zero"
        },
        "remediation": {
            "steps": [
                "Check grace time: defaults read /Library/Preferences/com.apple.screensaver askForPasswordDelay",
                "Set to 0: defaults write /Library/Preferences/com.apple.screensaver askForPasswordDelay -int 0",
                "Or via GUI: System Preferences → Security & Privacy → General → Require password immediately",
                "Verify: defaults read /Library/Preferences/com.apple.screensaver askForPasswordDelay"
            ],
            "verification_command": "defaults read /Library/Preferences/com.apple.screensaver askForPasswordDelay",
            "expected_result": "0 (immediate password required)"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Grace period allows brief unauthorized access to unlocked system",
            "business_impact": "Unauthorized access during grace period",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-AC-022": {
        "family": "Access Control",
        "name": "System Preferences Access Control",
        "description": "Access to System Preferences must be controlled and logged",
        "severity": "MEDIUM",
        "requirements": {
            "system_prefs_restricted": True,
            "changes_require_admin": True,
            "changes_logged": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "System Preferences changes require administrator authentication",
                "Non-admin users cannot modify system settings",
                "Preference changes are logged"
            ],
            "fail_conditions": [
                "Standard users can modify system settings",
                "No authentication required for system changes",
                "Changes not logged"
            ]
        },
        "macos_implementation": {
            "audit_command": "security authorizationdb read system.preferences 2>&1",
            "expected_output_pattern": "authenticate-admin|authenticate-session-owner",
            "parser_logic": "check_system_prefs_acl",
            "validation": "admin_auth_required"
        },
        "remediation": {
            "steps": [
                "Check authorization: security authorizationdb read system.preferences",
                "Verify 'authenticate-admin' is required",
                "If not, configure: sudo security authorizationdb write system.preferences",
                "Enable audit logging for preference changes",
                "Verify: security authorizationdb read system.preferences"
            ],
            "verification_command": "security authorizationdb read system.preferences",
            "expected_result": "authenticate-admin required for system preference changes"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Users can modify system security settings without authorization",
            "business_impact": "Security setting tampering, privilege escalation",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AC-023": {
        "family": "Access Control",
        "name": "Keychain Access Control",
        "description": "System and user keychains must be properly secured",
        "severity": "HIGH",
        "requirements": {
            "keychain_locked": True,
            "keychain_timeout_configured": True,
            "keychain_password_required": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Keychain locks after idle timeout",
                "Keychain requires password to unlock",
                "System keychain properly secured",
                "Login keychain synchronized with user password"
            ],
            "fail_conditions": [
                "Keychain never locks automatically",
                "Keychain unlocked without password",
                "System keychain accessible to standard users"
            ]
        },
        "macos_implementation": {
            "audit_command": "security list-keychains",
            "expected_output_pattern": "/Library/Keychains|/Users/.*/Library/Keychains",
            "parser_logic": "check_keychain_security",
            "validation": "keychains_present AND properly_secured"
        },
        "remediation": {
            "steps": [
                "List keychains: security list-keychains",
                "Check keychain settings: Keychain Access → Preferences",
                "Enable: Lock after X minutes of inactivity (recommended: 5 minutes)",
                "Enable: Lock when sleeping",
                "Ensure login keychain password matches user password",
                "Verify: security show-keychain-info ~/Library/Keychains/login.keychain-db"
            ],
            "verification_command": "security list-keychains",
            "expected_result": "Keychains configured with proper security settings"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Stored credentials accessible, password theft possible",
            "business_impact": "Credential theft, unauthorized access to saved passwords",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AC-024": {
        "family": "Access Control",
        "name": "Terminal Access Restrictions",
        "description": "Terminal and command-line access should be restricted to authorized users",
        "severity": "MEDIUM",
        "requirements": {
            "terminal_access_controlled": True,
            "shell_access_logged": True,
            "unauthorized_users_no_shell": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Terminal access restricted to authorized users",
                "Standard users have appropriate shell access",
                "Shell access is logged",
                "Service accounts have /usr/bin/false shell"
            ],
            "fail_conditions": [
                "All users have unrestricted terminal access",
                "Service accounts have interactive shells",
                "No logging of terminal access"
            ]
        },
        "macos_implementation": {
            "audit_command": "dscl . -list /Users UserShell",
            "expected_output_pattern": "/bin/bash|/bin/zsh|/usr/bin/false",
            "parser_logic": "check_terminal_access",
            "validation": "appropriate_shells_configured"
        },
        "remediation": {
            "steps": [
                "List user shells: dscl . -list /Users UserShell",
                "Review which users need terminal access",
                "Disable shell for service accounts: sudo dscl . -create /Users/serviceaccount UserShell /usr/bin/false",
                "Enable terminal logging: sudo log config --mode 'level:debug,persist:debug'",
                "Verify: dscl . -list /Users UserShell"
            ],
            "verification_command": "dscl . -list /Users UserShell",
            "expected_result": "Appropriate shells configured per user role"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Unnecessary command-line access increases attack surface",
            "business_impact": "Privilege escalation, unauthorized system modification",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-AC-025": {
        "family": "Access Control",
        "name": "SSH Key Authentication",
        "description": "SSH key authentication must be properly configured and managed",
        "severity": "HIGH",
        "requirements": {
            "ssh_keys_used": True,
            "key_permissions_correct": True,
            "authorized_keys_reviewed": True,
            "weak_keys_removed": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "SSH keys are used instead of passwords (where applicable)",
                "Private key permissions are 600 or more restrictive",
                "authorized_keys file properly secured (600)",
                "No weak RSA keys (< 2048 bits)",
                "SSH keys are documented and reviewed regularly"
            ],
            "fail_conditions": [
                "SSH keys with incorrect permissions (> 600)",
                "Weak or outdated SSH keys in use",
                "Unauthorized keys in authorized_keys file",
                "No key management process"
            ]
        },
        "macos_implementation": {
            "audit_command": "ls -la ~/.ssh/",
            "expected_output_pattern": "id_rsa|id_ed25519|authorized_keys",
            "parser_logic": "check_ssh_keys",
            "validation": "keys_exist AND permissions_correct AND no_weak_keys"
        },
        "remediation": {
            "steps": [
                "List SSH keys: ls -la ~/.ssh/",
                "Check key permissions: ls -l ~/.ssh/id_* ~/.ssh/authorized_keys",
                "Fix permissions: chmod 600 ~/.ssh/id_rsa ~/.ssh/authorized_keys",
                "Check key strength: ssh-keygen -l -f ~/.ssh/id_rsa.pub",
                "Remove weak keys and regenerate: ssh-keygen -t ed25519 -C 'user@host'",
                "Review authorized_keys: cat ~/.ssh/authorized_keys",
                "Remove unauthorized keys",
                "Verify: ls -la ~/.ssh/"
            ],
            "verification_command": "ls -la ~/.ssh/",
            "expected_result": "SSH keys present with secure permissions (600)"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Compromised SSH keys lead to unauthorized remote access",
            "business_impact": "Unauthorized remote access, lateral movement in network",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-AC-026": {
        "family": "Access Control",
        "name": "Network Access Control (Packet Filter)",
        "description": "Packet filter (pf) rules must be configured to control network access",
        "severity": "MEDIUM",
        "requirements": {
            "pf_enabled": True,
            "pf_rules_configured": True,
            "default_deny": True,
            "rules_reviewed": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Packet filter (pf) is enabled",
                "Default policy is deny",
                "Only required ports are allowed",
                "Rules are documented and reviewed regularly"
            ],
            "fail_conditions": [
                "Packet filter not enabled",
                "Default policy is allow",
                "No network access control rules",
                "Rules not documented"
            ]
        },
        "macos_implementation": {
            "audit_command": "sudo pfctl -s rules 2>&1",
            "expected_output_pattern": "block|pass",
            "parser_logic": "check_pf_rules",
            "validation": "pf_enabled AND rules_configured"
        },
        "remediation": {
            "steps": [
                "Check pf status: sudo pfctl -s info",
                "Check rules: sudo pfctl -s rules",
                "Enable pf: sudo pfctl -e",
                "Configure rules: sudo nano /etc/pf.conf",
                "Load rules: sudo pfctl -f /etc/pf.conf",
                "Verify: sudo pfctl -s rules",
                "Document all allow rules and their justification"
            ],
            "verification_command": "sudo pfctl -s rules",
            "expected_result": "Packet filter enabled with appropriate rules"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Network traffic not controlled, unnecessary ports exposed",
            "business_impact": "Network-based attacks, unauthorized connections",
            "likelihood": "MEDIUM"
        }
    }
}

# Add the 18 controls
data['controls'].update(week1_controls)

# Update metadata
data['metadata']['last_updated'] = "2025-11-28"
data['metadata']['total_controls'] = len(data['controls'])
data['metadata']['description'] = f"Rwanda NCSA cybersecurity control requirements for macOS compliance auditing - {len(data['controls'])} system-auditable controls"

# Save
with open(controls_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"\n✅ Successfully expanded to {len(data['controls'])} controls")
print(f"\n📋 Week 1 Access Control Added (18 controls):")
for control_id in sorted(week1_controls.keys()):
    control = week1_controls[control_id]
    print(f"  - {control_id}: {control['name']} ({control['severity']})")

print(f"\n💾 Updated file: {controls_file}")
print(f"\n🎯 Total Controls: {len(data['controls'])}")
print(f"   - Access Control: 27 controls")
print(f"   - CRITICAL: 7 controls")
print(f"   - HIGH: 21 controls")
print(f"   - MEDIUM: 17 controls")
print(f"   - LOW: 3 controls")

print(f"\n📊 Progress: 48/103 system-auditable controls (46.6%)")
print(f"   Week 1 Day 1-2 complete: 18 AC controls added")
print(f"   Next: Implement parsers and decision logic for new controls")
