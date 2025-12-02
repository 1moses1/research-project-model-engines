#!/usr/bin/env python3
"""
Expand evidence_parsers.py with Week 1 Access Control parsers
Add parsers for AC-009, AC-011 through AC-026 (17 new parsers)
"""

import re
from pathlib import Path

# Read existing parsers file
parsers_file = Path("engines/shared/evidence_parsers.py")
with open(parsers_file, 'r') as f:
    content = f.read()

# Find the parser_map section to add new mappings
new_parser_mappings = '''
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

# New parser functions to add at the end of the class
new_parsers = '''

    # ===== Week 1 Access Control Parsers (Binary Check Template) =====

    def parse_guest_account(self, content: str, control_id: str) -> Dict:
        """Parse guest account status (AC-012) - Binary check"""
        control = self.controls_db[control_id]

        # Check if guest account does not exist or is disabled
        guest_disabled = 'eDSRecordNotFound' in content or 'No such file' in content

        gaps = []
        if not guest_disabled:
            gaps.append({
                "requirement": "Guest account must be disabled",
                "actual": "Guest account is enabled or exists",
                "severity": "MEDIUM",
                "remediation": control['remediation']['steps'],
                "risk": "Unauthorized users can access system without credentials"
            })

        return self._binary_check_result(
            control_id=control_id,
            control=control,
            is_compliant=guest_disabled,
            feature_name="Guest Account Disabled",
            actual_status="DISABLED" if guest_disabled else "ENABLED",
            gaps=gaps,
            confidence=0.98
        )

    def parse_auto_login(self, content: str, control_id: str) -> Dict:
        """Parse automatic login status (AC-013) - Binary check"""
        control = self.controls_db[control_id]

        # Auto-login is disabled if the key doesn't exist
        auto_login_disabled = 'does not exist' in content

        gaps = []
        if not auto_login_disabled:
            gaps.append({
                "requirement": "Automatic login must be disabled",
                "actual": "Automatic login is enabled",
                "severity": "HIGH",
                "remediation": control['remediation']['steps'],
                "risk": "Physical access = immediate system access without authentication"
            })

        return self._binary_check_result(
            control_id=control_id,
            control=control,
            is_compliant=auto_login_disabled,
            feature_name="Automatic Login Disabled",
            actual_status="DISABLED" if auto_login_disabled else "ENABLED",
            gaps=gaps,
            confidence=0.99
        )

    def parse_root_status(self, content: str, control_id: str) -> Dict:
        """Parse root account status (AC-017) - Binary check"""
        control = self.controls_db[control_id]

        # Root is disabled if no auth authority or disabled user
        root_disabled = 'No such key' in content or 'DisabledUser' in content or '/usr/bin/false' in content

        gaps = []
        if not root_disabled:
            gaps.append({
                "requirement": "Root account must be disabled",
                "actual": "Root account is enabled",
                "severity": "CRITICAL",
                "remediation": control['remediation']['steps'],
                "risk": "Enabled root account = full system compromise risk"
            })

        return self._binary_check_result(
            control_id=control_id,
            control=control,
            is_compliant=root_disabled,
            feature_name="Root Account Disabled",
            actual_status="DISABLED" if root_disabled else "ENABLED",
            gaps=gaps,
            confidence=0.99
        )

    def parse_fast_user_switching(self, content: str, control_id: str) -> Dict:
        """Parse fast user switching config (AC-014) - Binary check"""
        control = self.controls_db[control_id]

        # Extract value (0 or 1)
        is_configured = '0' in content or '1' in content

        # This is a policy-based control - configuration should be documented
        gaps = []
        if not is_configured:
            gaps.append({
                "requirement": "Fast user switching configuration should be documented",
                "actual": "Configuration not set",
                "severity": "LOW",
                "remediation": control['remediation']['steps'],
                "risk": "Minor session management issue"
            })

        return self._binary_check_result(
            control_id=control_id,
            control=control,
            is_compliant=is_configured,
            feature_name="Fast User Switching Configured",
            actual_status="CONFIGURED" if is_configured else "NOT CONFIGURED",
            gaps=gaps,
            confidence=0.85
        )

    # ===== Configuration Parser Template =====

    def parse_mfa_certificates(self, content: str, control_id: str) -> Dict:
        """Parse MFA certificate status (AC-009) - Config parser"""
        control = self.controls_db[control_id]

        # Count certificates
        cert_matches = re.findall(r'(\\d+)\\s+valid identities found', content)
        num_certs = int(cert_matches[0]) if cert_matches else 0

        has_certs = num_certs > 0

        gaps = []
        if not has_certs:
            gaps.append({
                "requirement": "MFA certificates should be configured for admin accounts",
                "actual": "No certificates found",
                "severity": "HIGH",
                "remediation": control['remediation']['steps'],
                "risk": "Single-factor authentication vulnerable to credential theft"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"Found {num_certs} valid certificate(s)",
            "actual_state": {
                "certificates_found": num_certs,
                "mfa_available": has_certs
            },
            "expected_state": {
                "mfa_configured": True,
                "certificates_present": True
            },
            "compliance_status": "COMPLIANT" if has_certs else "NON_COMPLIANT",
            "compliance_score": 100.0 if has_certs else 0.0,
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_lockout_policy(self, content: str, control_id: str) -> Dict:
        """Parse account lockout policy (AC-011) - Config parser"""
        control = self.controls_db[control_id]
        requirements = control['requirements']

        # Extract max failed attempts
        max_attempts_match = re.search(r'maxFailedLoginAttempts[^\\d]*(\\d+)', content)
        max_attempts = int(max_attempts_match.group(1)) if max_attempts_match else None

        lockout_enabled = max_attempts is not None
        attempts_compliant = lockout_enabled and max_attempts <= requirements['max_failed_attempts']

        gaps = []
        if not lockout_enabled:
            gaps.append({
                "requirement": "Account lockout policy must be configured",
                "actual": "No lockout policy found",
                "severity": "MEDIUM",
                "remediation": control['remediation']['steps'],
                "risk": "Brute force attacks can succeed with unlimited attempts"
            })
        elif not attempts_compliant:
            gaps.append({
                "requirement": f"Max failed attempts must be <= {requirements['max_failed_attempts']}",
                "actual": f"Max failed attempts: {max_attempts}",
                "severity": "MEDIUM",
                "remediation": control['remediation']['steps'],
                "risk": "Too many attempts allowed before lockout"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"Max failed attempts: {max_attempts if max_attempts else 'Not configured'}",
            "actual_state": {
                "lockout_enabled": lockout_enabled,
                "max_failed_attempts": max_attempts
            },
            "expected_state": {
                "lockout_enabled": True,
                "max_failed_attempts": requirements['max_failed_attempts']
            },
            "compliance_status": "COMPLIANT" if attempts_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if attempts_compliant else (50.0 if lockout_enabled else 0.0),
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_grace_time(self, content: str, control_id: str) -> Dict:
        """Parse login grace time (AC-021) - Threshold check"""
        control = self.controls_db[control_id]
        requirements = control['requirements']

        # Extract grace time value
        grace_time_match = re.search(r'(-?\\d+)', content)
        grace_time = int(grace_time_match.group(1)) if grace_time_match else None

        is_compliant = grace_time == 0

        gaps = []
        if grace_time != 0:
            gaps.append({
                "requirement": "Login grace time must be 0 (immediate password)",
                "actual": f"Grace time: {grace_time} seconds",
                "severity": "MEDIUM",
                "remediation": control['remediation']['steps'],
                "risk": "Grace period allows brief unauthorized access"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"Grace time: {grace_time} seconds" if grace_time is not None else "Not configured",
            "actual_state": {
                "grace_time_seconds": grace_time
            },
            "expected_state": {
                "grace_time_seconds": 0
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else 50.0,
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    def parse_login_banner(self, content: str, control_id: str) -> Dict:
        """Parse login banner (AC-020) - Config parser"""
        control = self.controls_db[control_id]

        # Check if banner exists and contains warning
        banner_exists = len(content.strip()) > 0 and 'No such file' not in content
        has_warning = any(keyword in content.lower() for keyword in ['authorized', 'warning', 'unauthorized', 'prohibited'])

        is_compliant = banner_exists and has_warning

        gaps = []
        if not banner_exists:
            gaps.append({
                "requirement": "Login banner must be configured",
                "actual": "No banner found",
                "severity": "LOW",
                "remediation": control['remediation']['steps'],
                "risk": "Legal implications if unauthorized access occurs"
            })
        elif not has_warning:
            gaps.append({
                "requirement": "Banner must contain authorized use warning",
                "actual": "Banner exists but lacks warning text",
                "severity": "LOW",
                "remediation": control['remediation']['steps'],
                "risk": "Reduced legal standing in prosecution"
            })

        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": "Banner configured with warning" if is_compliant else "Banner missing or incomplete",
            "actual_state": {
                "banner_exists": banner_exists,
                "has_warning": has_warning,
                "banner_text": content[:200] if banner_exists else None
            },
            "expected_state": {
                "banner_exists": True,
                "has_warning": True
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else (50.0 if banner_exists else 0.0),
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    # ===== Helper method for binary checks =====

    def _binary_check_result(self, control_id: str, control: Dict, is_compliant: bool,
                              feature_name: str, actual_status: str, gaps: List[Dict],
                              confidence: float = 0.98) -> Dict:
        """Helper method for binary check parsers"""
        return {
            "control_id": control_id,
            "control_name": control['name'],
            "parsing_successful": True,
            "evidence_summary": f"{feature_name}: {actual_status}",
            "actual_state": {
                f"{feature_name.lower().replace(' ', '_')}": is_compliant
            },
            "expected_state": {
                f"{feature_name.lower().replace(' ', '_')}": True
            },
            "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
            "compliance_score": 100.0 if is_compliant else 0.0,
            "gaps": gaps,
            "risk_level": control['severity'],
            "remediation_steps": control['remediation']['steps'] if gaps else []
        }

    # TODO: Add remaining parsers for AC-015, AC-016, AC-018, AC-019, AC-022, AC-023, AC-024, AC-025, AC-026
    # These will be implemented in next iteration with full template patterns
'''

print("📝 Parser expansion script created")
print("📋 New parsers to add:")
print("  - AC-009: MFA Certificates (config parser)")
print("  - AC-011: Lockout Policy (config parser)")
print("  - AC-012: Guest Account (binary check)")
print("  - AC-013: Auto-Login (binary check)")
print("  - AC-014: Fast User Switching (binary check)")
print("  - AC-017: Root Status (binary check)")
print("  - AC-020: Login Banner (config parser)")
print("  - AC-021: Grace Time (threshold check)")
print("\n⏳ Remaining parsers (AC-015, AC-016, AC-018, AC-019, AC-022, AC-023, AC-024, AC-025, AC-026)")
print("   Will be implemented in next batch\n")

# Write instructions
instructions = """
PARSER IMPLEMENTATION STATUS
=============================

✅ Completed (8 parsers):
  - AC-009: MFA Certificates
  - AC-011: Account Lockout Policy
  - AC-012: Guest Account
  - AC-013: Automatic Login
  - AC-014: Fast User Switching
  - AC-017: Root Account
  - AC-020: Login Banner
  - AC-021: Login Grace Time

⏳ Remaining (9 parsers):
  - AC-015: Password Reset Requirements (config parser)
  - AC-016: Inactive Account Detection (threshold check)
  - AC-018: Home Directory Permissions (permission check)
  - AC-019: Shared Folder Permissions (permission check)
  - AC-022: System Preferences ACL (config parser)
  - AC-023: Keychain Security (config parser)
  - AC-024: Terminal Access (inventory parser)
  - AC-025: SSH Keys (permission check)
  - AC-026: Packet Filter Rules (config parser)

NEXT STEPS:
1. Copy new parser mappings to parser_map in parse_evidence()
2. Copy new parser functions to end of RwandaNCSAEvidenceParser class
3. Implement remaining 9 parsers using templates
4. Add decision logic in rwanda_decision_engine.py for all 17 controls
"""

with open("PARSER_EXPANSION_STATUS.md", 'w') as f:
    f.write(instructions)

print("✅ Created: PARSER_EXPANSION_STATUS.md")
print("📋 Review this file for implementation status")
