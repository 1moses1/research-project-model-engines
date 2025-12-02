#!/usr/bin/env python3
"""
Add final 6 controls to reach 30 total
Focus: Wi-Fi, VPN, DNS, Biometrics, Profiles, Remote Desktop
"""

import json
from pathlib import Path

# Load existing controls
controls_file = Path("engines/shared/rwanda_ncsa_controls.json")
with open(controls_file, 'r') as f:
    data = json.load(f)

print(f"Current controls: {len(data['controls'])}")

# Final 6 controls
final_6_controls = {
    "RWNCSA-SY-007": {
        "family": "System and Communications Protection",
        "name": "Wi-Fi Security Configuration",
        "description": "Wireless network connections must use strong encryption and authentication",
        "severity": "HIGH",
        "requirements": {
            "wpa3_or_wpa2_required": True,
            "open_networks_forbidden": True,
            "auto_join_disabled_for_unknown": True,
            "preferred_networks_documented": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "All Wi-Fi networks use WPA2 or WPA3",
                "No open/unsecured networks configured",
                "Auto-join disabled for unknown networks",
                "Preferred networks list maintained"
            ],
            "fail_conditions": [
                "Open networks configured",
                "WEP encryption in use",
                "Auto-join enabled for public networks"
            ]
        },
        "macos_implementation": {
            "audit_command": "networksetup -listpreferredwirelessnetworks en0",
            "expected_output_pattern": "Preferred networks on en0",
            "parser_logic": "analyze_wifi_security",
            "validation": "no_open_networks AND wpa2_or_higher"
        },
        "remediation": {
            "steps": [
                "List Wi-Fi networks: networksetup -listpreferredwirelessnetworks en0",
                "Remove insecure: networksetup -removepreferredwirelessnetwork en0 'NetworkName'",
                "Disable auto-join: networksetup -setairportpower en0 off (when not needed)",
                "Configure WPA2/WPA3: System Preferences → Network → Wi-Fi → Advanced"
            ],
            "verification_command": "networksetup -listpreferredwirelessnetworks en0",
            "expected_result": "Only secure networks listed"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Man-in-the-middle attacks, traffic interception",
            "business_impact": "Data theft, credential compromise",
            "likelihood": "MEDIUM"
        }
    },

    "RWNCSA-SY-008": {
        "family": "System and Communications Protection",
        "name": "VPN Configuration and Usage",
        "description": "VPN must be used for remote connections and properly configured",
        "severity": "HIGH",
        "requirements": {
            "vpn_configured": True,
            "vpn_encryption_strong": True,
            "split_tunneling_disabled": True,
            "vpn_always_on_recommended": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "VPN client configured",
                "Strong encryption (AES-256 or equivalent)",
                "Split tunneling disabled for corporate VPN",
                "VPN logs available"
            ],
            "fail_conditions": [
                "No VPN configured",
                "Weak encryption",
                "Split tunneling enabled",
                "VPN not enforced for remote access"
            ]
        },
        "macos_implementation": {
            "audit_command": "scutil --nc list",
            "expected_output_pattern": "IPSec|IKEv2|L2TP",
            "parser_logic": "check_vpn_configuration",
            "validation": "vpn_configured AND secure_protocol"
        },
        "remediation": {
            "steps": [
                "List VPN connections: scutil --nc list",
                "Configure VPN: System Preferences → Network → + → VPN",
                "Select IKEv2 or IPSec for strong encryption",
                "Disable split tunneling in VPN settings",
                "Verify: scutil --nc status <VPN-Name>"
            ],
            "verification_command": "scutil --nc list",
            "expected_result": "VPN service configured with secure protocol"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Unencrypted remote access, data exposure",
            "business_impact": "Data interception, unauthorized access",
            "likelihood": "HIGH"
        }
    },

    "RWNCSA-SY-009": {
        "family": "System and Communications Protection",
        "name": "DNS Security Configuration",
        "description": "DNS must be configured securely to prevent spoofing and malicious redirection",
        "severity": "MEDIUM",
        "requirements": {
            "trusted_dns_servers": True,
            "dns_over_https_recommended": True,
            "no_suspicious_dns": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "DNS servers are trusted (corporate or reputable public)",
                "DNS-over-HTTPS (DoH) or DNS-over-TLS enabled",
                "No suspicious DNS servers (known malicious IPs)"
            ],
            "fail_conditions": [
                "Unknown DNS servers configured",
                "No DNS encryption",
                "Suspicious DNS IPs detected"
            ]
        },
        "macos_implementation": {
            "audit_command": "networksetup -getdnsservers Wi-Fi && networksetup -getdnsservers Ethernet",
            "expected_output_pattern": "\\d+\\.\\d+\\.\\d+\\.\\d+",
            "parser_logic": "analyze_dns_configuration",
            "validation": "dns_servers_trusted AND no_suspicious_ips"
        },
        "remediation": {
            "steps": [
                "Check DNS: networksetup -getdnsservers Wi-Fi",
                "Set trusted DNS: networksetup -setdnsservers Wi-Fi 1.1.1.1 1.0.0.1 (Cloudflare)",
                "Or Google: networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4",
                "Enable DoH: Configure in DNS preferences or via profile",
                "Verify: networksetup -getdnsservers Wi-Fi"
            ],
            "verification_command": "networksetup -getdnsservers Wi-Fi",
            "expected_result": "Trusted DNS servers (corporate or 1.1.1.1, 8.8.8.8, etc.)"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - DNS spoofing, malware redirection",
            "business_impact": "Phishing, malware infection",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-ID-002": {
        "family": "Identity Management and Authentication",
        "name": "Biometric Authentication Configuration",
        "description": "Touch ID/Face ID must be properly configured for enhanced security",
        "severity": "MEDIUM",
        "requirements": {
            "biometric_enabled": True,
            "fallback_password_required": True,
            "biometric_for_sudo_recommended": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Touch ID enabled (if hardware supports)",
                "Password fallback required",
                "Biometric data properly secured"
            ],
            "fail_conditions": [
                "Biometric disabled when hardware available",
                "No password fallback",
                "Biometric configured insecurely"
            ]
        },
        "macos_implementation": {
            "audit_command": "bioutil -r -s",
            "expected_output_pattern": "Touch ID|Biometric",
            "parser_logic": "check_biometric_status",
            "validation": "biometric_enabled OR hardware_not_available"
        },
        "remediation": {
            "steps": [
                "Check status: bioutil -r -s",
                "Enable Touch ID: System Preferences → Touch ID",
                "Add fingerprints for authorized users",
                "Enable for sudo: sudo pam_touchid enable (if available)",
                "Verify: bioutil -r -s"
            ],
            "verification_command": "bioutil -r -s",
            "expected_result": "Biometric authentication configured"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Weaker authentication, password-only access",
            "business_impact": "Easier unauthorized access",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-CO-004": {
        "family": "Configuration Management",
        "name": "Configuration Profiles Management",
        "description": "Configuration profiles must be documented and authorized",
        "severity": "MEDIUM",
        "requirements": {
            "profiles_documented": True,
            "unauthorized_profiles_absent": True,
            "mdm_profiles_verified": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "All installed profiles documented",
                "No unauthorized profiles",
                "MDM profiles from trusted source",
                "Profiles properly signed"
            ],
            "fail_conditions": [
                "Unknown profiles installed",
                "Unsigned profiles present",
                "Unauthorized MDM profiles"
            ]
        },
        "macos_implementation": {
            "audit_command": "profiles -P -v",
            "expected_output_pattern": "Configuration profiles|There are no configuration profiles",
            "parser_logic": "analyze_configuration_profiles",
            "validation": "all_profiles_known AND all_profiles_signed"
        },
        "remediation": {
            "steps": [
                "List profiles: profiles -P -v",
                "Review each profile: profiles show -type configuration",
                "Remove unauthorized: sudo profiles -R -p <ProfileIdentifier>",
                "Document approved profiles",
                "Verify: profiles -P"
            ],
            "verification_command": "profiles -P",
            "expected_result": "Only authorized profiles installed (or none)"
        },
        "risk_assessment": {
            "if_non_compliant": "MEDIUM - Unauthorized configuration changes, backdoors",
            "business_impact": "System compromise, data theft",
            "likelihood": "LOW"
        }
    },

    "RWNCSA-AC-008": {
        "family": "Access Control",
        "name": "Remote Desktop and Screen Sharing Security",
        "description": "Remote desktop and screen sharing must be disabled unless explicitly required and secured",
        "severity": "HIGH",
        "requirements": {
            "screen_sharing_disabled": True,
            "remote_management_disabled": True,
            "vnc_disabled": True,
            "if_enabled_encrypted_and_logged": True
        },
        "compliance_criteria": {
            "pass_conditions": [
                "Screen Sharing disabled (unless justified and secured)",
                "Remote Management disabled",
                "VNC access disabled",
                "If enabled: encryption + authentication + logging"
            ],
            "fail_conditions": [
                "Screen Sharing enabled without justification",
                "Remote Management enabled unnecessarily",
                "VNC with weak/no password",
                "No logging of remote access"
            ]
        },
        "macos_implementation": {
            "audit_command": "sudo launchctl list | grep -E 'screensharing|RemoteDesktop|vnc'",
            "expected_output_pattern": "",
            "parser_logic": "check_remote_access_services",
            "validation": "no_remote_services_running OR properly_secured"
        },
        "remediation": {
            "steps": [
                "Check services: sudo launchctl list | grep -E 'screensharing|RemoteDesktop'",
                "Disable Screen Sharing: System Preferences → Sharing → uncheck Screen Sharing",
                "Disable Remote Management: System Preferences → Sharing → uncheck Remote Management",
                "If needed, enable with: VNC password, user authentication, logging",
                "Verify: sudo launchctl list | grep screensharing"
            ],
            "verification_command": "sudo launchctl list | grep -E 'screensharing|RemoteDesktop|vnc'",
            "expected_result": "No output (services not running) or secured configuration"
        },
        "risk_assessment": {
            "if_non_compliant": "HIGH - Unauthorized remote access, screen hijacking",
            "business_impact": "Data theft, system control by attacker",
            "likelihood": "MEDIUM"
        }
    }
}

# Add the final 6 controls
data['controls'].update(final_6_controls)

# Update metadata
data['metadata']['last_updated'] = "2025-11-28"
data['metadata']['total_controls'] = len(data['controls'])
data['metadata']['description'] = "Rwanda NCSA cybersecurity control requirements for macOS compliance auditing - 30 critical system-auditable controls"

# Save
with open(controls_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"✅ Successfully expanded to {len(data['controls'])} controls")
print(f"\n📋 Final 6 Controls Added:")
for control_id in sorted(final_6_controls.keys()):
    control = final_6_controls[control_id]
    print(f"  - {control_id}: {control['name']} ({control['severity']})")

print(f"\n💾 Updated file: {controls_file}")
print(f"\n🎯 Total System-Auditable Controls: 30")
print(f"   - CRITICAL: 6")
print(f"   - HIGH: 15")
print(f"   - MEDIUM: 9")
