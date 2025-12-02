#!/usr/bin/env python3
"""
Add ALL 38 missing parsers to evidence_parsers.py
Bridge the intelligence gap: 9 → 47 parsers
"""

import re
from pathlib import Path

print("=" * 70)
print("🔧 ADDING 38 MISSING PARSERS TO EVIDENCE_PARSERS.PY")
print("=" * 70)

# Read existing parsers file
parsers_file = Path("engines/shared/evidence_parsers.py")
with open(parsers_file, 'r') as f:
    content = f.read()

# Find the parser_map section
parser_map_pattern = r'(parser_map = \{)(.*?)(\n        \})'
match = re.search(parser_map_pattern, content, re.DOTALL)

if not match:
    print("❌ ERROR: Could not find parser_map in evidence_parsers.py")
    exit(1)

# Existing parser_map content
existing_map = match.group(2)

# New parser mappings to add (38 controls)
new_mappings = '''
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
            "RWNCSA-AC-026": self.parse_pf_rules,'''

# Update parser_map
updated_map = existing_map + new_mappings
new_content = content.replace(match.group(0), f"{match.group(1)}{updated_map}\n        }}")

# Write back
with open(parsers_file, 'w') as f:
    f.write(new_content)

print(f"✅ Added 38 parser mappings to parser_map")
print(f"\n📝 Parser mappings updated in: {parsers_file}")
print(f"\n⏳ Next: Add actual parser function implementations...")

print("\n" + "=" * 70)
print("Parser mappings added successfully!")
print("Run next script to add parser function implementations")
print("=" * 70)
