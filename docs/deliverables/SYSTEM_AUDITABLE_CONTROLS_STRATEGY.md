# System-Auditable Controls Implementation Strategy
## Complete Rwanda NCSA Coverage - 169 Requirements

**Date**: November 28, 2025
**Current Status**: 30/169 controls implemented (17.8%)
**Target**: Define all 169 controls with intelligent parsing logic

---

## 🎯 Executive Summary

**Rwanda NCSA Framework**: 169 cybersecurity requirements across 14 control families
**Implementation Approach**: Tier-based strategy matching audit capability

| Tier | Type | Count | Audit Method |
|------|------|-------|--------------|
| **Tier 1** | System-Auditable | ~50-60 | macOS CLI commands |
| **Tier 2** | Document Review | ~90 | Engine 2 + LLM analysis |
| **Tier 3** | Manual/Physical | ~24 | Checklist + Evidence |
| **TOTAL** | | **169** | Multi-modal |

---

## 📊 Current Implementation Status

### ✅ Completed: 30 Controls (17.8%)

**By Family**:
- **Access Control (AC)**: 8/26 (30.8%)
  - AC-001: Login History Monitoring ✅
  - AC-002: User Account Control ✅
  - AC-003: Administrative Access ✅
  - AC-004: SSH Configuration ✅ (CRITICAL)
  - AC-005: File Permissions ✅
  - AC-006: Sudo Configuration ✅
  - AC-007: Screen Lock ✅
  - AC-008: Remote Desktop Security ✅
  - AC-010: Session Control ✅

- **Audit & Accountability (AU)**: 6/26 (23.1%)
  - AU-001: Audit System ✅
  - AU-002: Audit Events ✅
  - AU-003: Time Sync ✅
  - AU-004: Disk Storage ✅

- **Configuration Management (CO)**: 4/14 (28.6%)
  - CO-001: Software Inventory ✅
  - CO-002: System Baseline ✅
  - CO-003: Patch Management ✅ (CRITICAL)
  - CO-004: Configuration Profiles ✅

- **Identity & Authentication (ID)**: 2/13 (15.4%)
  - ID-002: Biometric Authentication ✅
  - ID-005: Password Policy ✅ (CRITICAL)

- **System Protection (SY)**: 9/17 (52.9%)
  - SY-001: Firewall ✅ (CRITICAL)
  - SY-002: FileVault ✅ (CRITICAL)
  - SY-003: Bluetooth ✅
  - SY-004: Network Config ✅
  - SY-005: Anti-Malware ✅
  - SY-006: File Sharing ✅
  - SY-007: Wi-Fi Security ✅
  - SY-008: VPN Configuration ✅
  - SY-009: DNS Security ✅

- **System Integrity (SI)**: 1/4 (25%)
  - SI-007: System Integrity (SIP/Gatekeeper) ✅ (CRITICAL)

**Coverage by Severity**:
- CRITICAL: 6/6 (100%) ✅
- HIGH: 15/15 (100%) ✅
- MEDIUM: 9/9 (100%) ✅

---

## 🎯 Tier 1: System-Auditable Controls (50-60 controls)

### Definition
Controls that can be audited via:
- macOS CLI commands
- File system inspection
- Configuration file parsing
- System API queries
- Log file analysis

### Implementation Status: 30/60 (50%)

### Remaining 20-30 Controls to Implement

#### **Access Control (AC) - 18 remaining**

| Control ID | Name | Severity | macOS Command | Parser Type |
|-----------|------|----------|---------------|-------------|
| AC-009 | Multi-Factor Authentication Status | HIGH | `security find-identity -p certificates` | Binary Check |
| AC-011 | Account Lockout Policy | MEDIUM | `pwpolicy -getaccountpolicies` | Config Parser |
| AC-012 | Guest Account Status | MEDIUM | `dscl . -read /Users/Guest` | Binary Check |
| AC-013 | Automatic Login Disabled | HIGH | `defaults read /Library/Preferences/com.apple.loginwindow autoLoginUser` | Binary Check |
| AC-014 | Fast User Switching | LOW | `defaults read /Library/Preferences/.GlobalPreferences MultipleSessionEnabled` | Binary Check |
| AC-015 | Password Reset Requirements | MEDIUM | `pwpolicy -getaccountpolicies` | Config Parser |
| AC-016 | Inactive Account Detection | MEDIUM | `dscl . -list /Users | while read user; do dscl . -read /Users/$user lastlogin; done` | Threshold Check |
| AC-017 | Root Account Status | CRITICAL | `dscl . -read /Users/root AuthenticationAuthority` | Binary Check |
| AC-018 | User Home Directory Permissions | HIGH | `ls -la /Users` | Permission Check |
| AC-019 | Shared Folder Permissions | MEDIUM | `sharing -l` | Permission Check |
| AC-020 | Login Banner Configuration | LOW | `cat /etc/motd` | Config Parser |
| AC-021 | Login Grace Time | MEDIUM | `defaults read /Library/Preferences/com.apple.loginwindow LoginwindowText` | Config Parser |
| AC-022 | System Preferences Access Control | MEDIUM | `security authorizationdb read system.preferences` | Config Parser |
| AC-023 | Keychain Access Control | HIGH | `security list-keychains` | Inventory Parser |
| AC-024 | Terminal Access Restrictions | MEDIUM | `ls -l /Applications/Utilities/Terminal.app` | Permission Check |
| AC-025 | SSH Key Authentication | HIGH | `cat ~/.ssh/authorized_keys` | Config Parser |
| AC-026 | Network Access Control | MEDIUM | `pfctl -s rules` | Config Parser |

#### **Audit & Accountability (AU) - 20 remaining**

| Control ID | Name | Severity | macOS Command | Parser Type |
|-----------|------|----------|---------------|-------------|
| AU-005 | Audit Log Forwarding | HIGH | `cat /etc/syslog.conf` | Config Parser |
| AU-006 | Audit Record Retention | MEDIUM | `sudo audit -s` | Config Parser |
| AU-007 | Log Integrity Protection | HIGH | `ls -la /var/audit` | Permission Check |
| AU-008 | Remote Logging Configuration | MEDIUM | `cat /etc/asl.conf` | Config Parser |
| AU-009 | Audit Failure Alerting | MEDIUM | `launchctl list | grep audit` | Binary Check |
| AU-010 | Log Rotation Configuration | LOW | `cat /etc/newsyslog.conf` | Config Parser |
| AU-011 | System Event Logging | MEDIUM | `log show --predicate 'eventMessage contains "security"' --last 1h` | Threshold Check |
| AU-012 | Login Attempt Logging | HIGH | `log show --predicate 'process == "loginwindow"' --last 24h` | Threshold Check |
| AU-013 | Failed Access Attempts | HIGH | `log show --predicate 'eventMessage contains "authentication failure"' --last 24h` | Threshold Check |
| AU-014 | Privilege Escalation Logging | HIGH | `log show --predicate 'process == "sudo"' --last 24h` | Threshold Check |
| AU-015 | File Access Auditing | MEDIUM | `sudo praudit /var/audit/*` | Log Parser |
| AU-016 | Network Connection Logging | MEDIUM | `log show --predicate 'subsystem == "com.apple.network"' --last 1h` | Log Parser |
| AU-017 | Software Installation Logging | MEDIUM | `system_profiler SPInstallHistoryDataType` | Log Parser |
| AU-018 | Configuration Change Logging | HIGH | `log show --predicate 'eventMessage contains "configuration"' --last 24h` | Log Parser |
| AU-019 | User Action Auditing | MEDIUM | `last -100` | Log Parser |
| AU-020 | Clock Synchronization Status | MEDIUM | `systemsetup -getusingnetworktime` | Binary Check |
| AU-021 | Audit Service Status | HIGH | `launchctl list | grep auditd` | Binary Check |
| AU-022 | Audit Policy Configuration | HIGH | `sudo audit -c` | Config Parser |
| AU-023 | Audit Trail Protection | HIGH | `ls -la /var/audit` | Permission Check |
| AU-024 | Log Storage Capacity | MEDIUM | `df -h /var` | Threshold Check |

#### **Configuration Management (CO) - 10 remaining**

| Control ID | Name | Severity | macOS Command | Parser Type |
|-----------|------|----------|---------------|-------------|
| CO-005 | Unauthorized Software Detection | HIGH | `system_profiler SPApplicationsDataType | grep -v "Apple Inc."` | Inventory Parser |
| CO-006 | Boot Configuration Security | HIGH | `nvram -p` | Config Parser |
| CO-007 | Kernel Extensions Inventory | HIGH | `kextstat` | Inventory Parser |
| CO-008 | Launch Daemons Inventory | MEDIUM | `launchctl list` | Inventory Parser |
| CO-009 | System Preferences Enforcement | MEDIUM | `defaults read /Library/Preferences/com.apple.MCX` | Config Parser |
| CO-010 | Security Update Status | CRITICAL | `softwareupdate -l` | Binary Check |
| CO-011 | Application Update Policy | MEDIUM | `defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled` | Binary Check |
| CO-012 | Configuration Profile Signatures | HIGH | `profiles -P -v` | Signature Check |
| CO-013 | System Extension Management | HIGH | `systemextensionsctl list` | Inventory Parser |
| CO-014 | Homebrew Package Inventory | LOW | `brew list --versions` | Inventory Parser |

#### **Identity & Authentication (ID) - 11 remaining**

| Control ID | Name | Severity | macOS Command | Parser Type |
|-----------|------|----------|---------------|-------------|
| ID-001 | Keychain Security Configuration | HIGH | `security dump-keychain` | Config Parser |
| ID-003 | Certificate Store Validation | HIGH | `security find-certificate -a` | Inventory Parser |
| ID-004 | Kerberos Configuration | MEDIUM | `klist -A` | Binary Check |
| ID-006 | LDAP/Directory Integration | MEDIUM | `dsconfigad -show` | Config Parser |
| ID-007 | Smart Card Authentication | MEDIUM | `security smartcards` | Binary Check |
| ID-008 | Token-Based Authentication | MEDIUM | `sc_auth list` | Inventory Parser |
| ID-009 | Password History Enforcement | MEDIUM | `pwpolicy -getaccountpolicies | grep passwordHistoryDepth` | Config Parser |
| ID-010 | Password Complexity Requirements | HIGH | `pwpolicy -getaccountpolicies` | Config Parser |
| ID-011 | Authentication Timeout | MEDIUM | `defaults read /Library/Preferences/com.apple.screensaver askForPasswordDelay` | Threshold Check |
| ID-012 | Credential Caching Policy | MEDIUM | `defaults read /Library/Preferences/com.apple.loginwindow SHOWFULLNAME` | Binary Check |
| ID-013 | Biometric Failure Fallback | MEDIUM | `bioutil -r -s` | Config Parser |

#### **Incident Response (IN) - 2-3 system-auditable**

| Control ID | Name | Severity | macOS Command | Parser Type |
|-----------|------|----------|---------------|-------------|
| IN-001 | Incident Logging Status | MEDIUM | `log show --predicate 'subsystem == "com.apple.securityd"' --last 1h` | Binary Check |
| IN-002 | Crash Report Configuration | LOW | `defaults read com.apple.CrashReporter DialogType` | Config Parser |
| IN-003 | Diagnostic Reporting Status | LOW | `defaults read /Library/Application\ Support/CrashReporter/DiagnosticMessagesHistory.plist` | Binary Check |

#### **Maintenance (MA) - 3-4 system-auditable**

| Control ID | Name | Severity | macOS Command | Parser Type |
|-----------|------|----------|---------------|-------------|
| MA-001 | System Update Status | CRITICAL | `softwareupdate -l` | Binary Check |
| MA-002 | Maintenance Scheduling | LOW | `launchctl list | grep softwareupdate` | Binary Check |
| MA-003 | Remote Maintenance Controls | MEDIUM | `systemsetup -getremotelogin` | Binary Check |
| MA-004 | Diagnostic Data Collection | LOW | `system_profiler SPDiagnosticsDataType` | Binary Check |

#### **Media Protection (ME) - 4-5 system-auditable**

| Control ID | Name | Severity | macOS Command | Parser Type |
|-----------|------|----------|---------------|-------------|
| ME-001 | USB Device Restrictions | MEDIUM | `system_profiler SPUSBDataType` | Inventory Parser |
| ME-002 | External Media Encryption | HIGH | `diskutil list` | Config Parser |
| ME-003 | Removable Media Policy | MEDIUM | `system_profiler SPCardReaderDataType` | Inventory Parser |
| ME-004 | Media Sanitization Tools | LOW | `diskutil secureErase` | Binary Check |
| ME-005 | Thunderbolt Security | MEDIUM | `system_profiler SPThunderboltDataType` | Config Parser |

#### **System Protection (SY) - 8 remaining**

| Control ID | Name | Severity | macOS Command | Parser Type |
|-----------|------|----------|---------------|-------------|
| SY-010 | Proxy Configuration Security | MEDIUM | `networksetup -getwebproxy Wi-Fi` | Config Parser |
| SY-011 | Network Services Inventory | MEDIUM | `networksetup -listallnetworkservices` | Inventory Parser |
| SY-012 | Port Security Configuration | HIGH | `lsof -i -P -n` | Inventory Parser |
| SY-013 | Protocol Restrictions | MEDIUM | `networksetup -listallnetworkservices` | Config Parser |
| SY-014 | Encryption Standards | HIGH | `system_profiler SPSoftwareDataType | grep Encryption` | Config Parser |
| SY-015 | Network Segmentation | MEDIUM | `ifconfig` | Config Parser |
| SY-016 | Wireless Security Standards | HIGH | `networksetup -getinfo Wi-Fi` | Config Parser |
| SY-017 | Airdrop Security | MEDIUM | `defaults read com.apple.NetworkBrowser DisableAirDrop` | Binary Check |

---

## 🔧 Implementation Strategy: Template-Based Approach

Instead of writing 60 unique functions, we'll use **5 core templates** that cover 80% of system-auditable controls:

### Template 1: Binary Check (enabled/disabled)
**Use Cases**: 20-25 controls
**Examples**: Firewall, FileVault, SIP, Guest account, Auto-login, Root account

```python
def parse_binary_feature(content, control_id, feature_name, enabled_pattern, disabled_pattern):
    """
    Template for features that are either ON or OFF
    Returns: COMPLIANT if enabled, NON_COMPLIANT if disabled
    """
    is_enabled = enabled_pattern.lower() in content.lower()
    is_disabled = disabled_pattern.lower() in content.lower()

    gaps = []
    if not is_enabled:
        gaps.append({
            "requirement": f"{feature_name} must be enabled",
            "actual": f"{feature_name} is DISABLED",
            "severity": control['severity'],
            "remediation": control['remediation']['steps'],
            "risk": control['risk_assessment']['if_non_compliant']
        })

    return {
        "evidence_summary": f"{feature_name}: {'ENABLED' if is_enabled else 'DISABLED'}",
        "actual_state": {f"{feature_name.lower()}_enabled": is_enabled},
        "expected_state": {f"{feature_name.lower()}_enabled": True},
        "compliance_status": "COMPLIANT" if is_enabled else "NON_COMPLIANT",
        "compliance_score": 100.0 if is_enabled else 0.0,
        "gaps": gaps,
        "confidence": 0.99  # High confidence for binary checks
    }
```

**Controls Using This Template**:
- AC-012: Guest Account
- AC-013: Automatic Login
- AC-017: Root Account
- AU-009: Audit Failure Alerting
- AU-020: Clock Synchronization
- AU-021: Audit Service Status
- CO-010: Security Update Status
- CO-011: Application Update Policy
- ID-004: Kerberos
- ID-007: Smart Card Auth
- IN-001: Incident Logging
- IN-002: Crash Reporting
- IN-003: Diagnostic Reporting
- MA-001: System Updates
- MA-002: Maintenance Scheduling
- MA-003: Remote Maintenance
- MA-004: Diagnostic Data
- ME-004: Media Sanitization
- SY-017: Airdrop Security

### Template 2: Configuration File Parser
**Use Cases**: 15-20 controls
**Examples**: SSH config, Sudo config, Password policy, Audit config

```python
def parse_config_file(content, control_id, required_settings):
    """
    Template for parsing configuration files
    Returns: COMPLIANT if all required settings match
    """
    actual_settings = {}
    gaps = []

    # Extract settings from content
    for key, expected_value in required_settings.items():
        # Parse setting from content (regex, line splitting, etc.)
        actual_value = extract_setting(content, key)
        actual_settings[key] = actual_value

        # Compare with requirement
        if actual_value != expected_value:
            gaps.append({
                "requirement": f"{key} should be {expected_value}",
                "actual": f"{key} is {actual_value}",
                "severity": "HIGH" if is_security_critical(key) else "MEDIUM",
                "remediation": f"Set {key}={expected_value} in config",
                "risk": get_risk_for_setting(key)
            })

    compliance_score = (len(required_settings) - len(gaps)) / len(required_settings) * 100
    is_compliant = len(gaps) == 0

    return {
        "evidence_summary": f"{len(required_settings)} settings checked, {len(gaps)} gaps",
        "actual_state": actual_settings,
        "expected_state": required_settings,
        "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
        "compliance_score": compliance_score,
        "gaps": gaps,
        "confidence": 0.92  # High confidence for config parsing
    }
```

**Controls Using This Template**:
- AC-004: SSH Configuration (PermitRootLogin, PasswordAuthentication, etc.)
- AC-006: Sudo Configuration
- AC-011: Account Lockout Policy
- AC-015: Password Reset Requirements
- AC-020: Login Banner
- AC-021: Login Grace Time
- AC-022: System Preferences ACL
- AC-025: SSH Key Auth
- AC-026: Network Access Control
- AU-005: Log Forwarding
- AU-006: Audit Retention
- AU-008: Remote Logging
- AU-010: Log Rotation
- AU-022: Audit Policy
- CO-006: Boot Configuration
- CO-009: System Preferences
- ID-001: Keychain Security
- ID-006: LDAP Integration
- ID-009: Password History
- ID-010: Password Complexity
- SY-010: Proxy Configuration
- SY-013: Protocol Restrictions
- SY-014: Encryption Standards
- SY-015: Network Segmentation
- SY-016: Wireless Security

### Template 3: Inventory/List Parser
**Use Cases**: 10-15 controls
**Examples**: Software inventory, running processes, kernel extensions, user list

```python
def parse_inventory(content, control_id, expected_items=None, forbidden_items=None, max_items=None):
    """
    Template for parsing lists and inventories
    Returns: COMPLIANT if inventory meets requirements
    """
    actual_items = parse_list(content)  # Extract list items from output
    gaps = []

    # Check for required items
    if expected_items:
        missing = set(expected_items) - set(actual_items)
        if missing:
            gaps.append({
                "requirement": f"Required items must be present",
                "actual": f"Missing: {', '.join(missing)}",
                "severity": "HIGH",
                "remediation": f"Install/enable: {', '.join(missing)}",
                "risk": "Incomplete security configuration"
            })

    # Check for forbidden items
    if forbidden_items:
        unauthorized = set(actual_items) & set(forbidden_items)
        if unauthorized:
            gaps.append({
                "requirement": "No unauthorized items allowed",
                "actual": f"Found: {', '.join(unauthorized)}",
                "severity": "CRITICAL",
                "remediation": f"Remove: {', '.join(unauthorized)}",
                "risk": "Unauthorized software/services"
            })

    # Check for maximum items
    if max_items and len(actual_items) > max_items:
        gaps.append({
            "requirement": f"Maximum {max_items} items allowed",
            "actual": f"Found {len(actual_items)} items",
            "severity": "MEDIUM",
            "remediation": "Review and remove unnecessary items",
            "risk": "Excessive complexity, increased attack surface"
        })

    is_compliant = len(gaps) == 0
    compliance_score = 100.0 if is_compliant else max(0, 100 - len(gaps) * 20)

    return {
        "evidence_summary": f"{len(actual_items)} items inventoried, {len(gaps)} issues",
        "actual_state": {"items": actual_items, "count": len(actual_items)},
        "expected_state": {"expected": expected_items, "forbidden": forbidden_items},
        "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
        "compliance_score": compliance_score,
        "gaps": gaps,
        "confidence": 0.88  # Good confidence for inventory checks
    }
```

**Controls Using This Template**:
- AC-023: Keychain Access
- CO-001: Software Inventory
- CO-005: Unauthorized Software
- CO-007: Kernel Extensions
- CO-008: Launch Daemons
- CO-012: Profile Signatures
- CO-013: System Extensions
- CO-014: Homebrew Packages
- ID-003: Certificate Store
- ID-008: Token-Based Auth
- ME-001: USB Devices
- ME-003: Removable Media
- ME-005: Thunderbolt
- SY-011: Network Services
- SY-012: Port Security

### Template 4: Threshold Check
**Use Cases**: 8-10 controls
**Examples**: Disk usage, password age, session timeout, log size

```python
def parse_threshold_value(content, control_id, threshold, operator, unit):
    """
    Template for checking numeric thresholds
    Returns: COMPLIANT if value meets threshold requirement
    """
    actual_value = extract_number(content)  # Extract numeric value

    # Perform comparison based on operator
    is_compliant = False
    if operator == "<=":
        is_compliant = actual_value <= threshold
    elif operator == ">=":
        is_compliant = actual_value >= threshold
    elif operator == "<":
        is_compliant = actual_value < threshold
    elif operator == ">":
        is_compliant = actual_value > threshold
    elif operator == "==":
        is_compliant = actual_value == threshold

    gaps = []
    if not is_compliant:
        gaps.append({
            "requirement": f"Value must be {operator} {threshold} {unit}",
            "actual": f"Current value: {actual_value} {unit}",
            "severity": calculate_severity_by_deviation(actual_value, threshold, operator),
            "remediation": f"Adjust value to meet {operator} {threshold} {unit} requirement",
            "risk": get_risk_for_threshold_violation(control_id, actual_value, threshold)
        })

    # Calculate score based on proximity to threshold
    compliance_score = calculate_proximity_score(actual_value, threshold, operator)

    return {
        "evidence_summary": f"Value: {actual_value} {unit} (threshold: {operator} {threshold} {unit})",
        "actual_state": {"value": actual_value, "unit": unit},
        "expected_state": {"threshold": threshold, "operator": operator, "unit": unit},
        "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
        "compliance_score": compliance_score,
        "gaps": gaps,
        "confidence": 0.90  # High confidence for threshold checks
    }
```

**Controls Using This Template**:
- AC-016: Inactive Account Detection (days since last login <= 90)
- AU-004: Disk Storage (usage <= 80%)
- AU-011: System Event Logging (events per hour >= 10)
- AU-012: Login Attempt Logging (logs present)
- AU-013: Failed Access Attempts (failures per hour <= 10)
- AU-014: Privilege Escalation Logging (sudo events logged)
- AU-024: Log Storage Capacity (free space >= 20%)
- ID-011: Authentication Timeout (timeout <= 300 seconds)

### Template 5: Permission Check
**Use Cases**: 6-8 controls
**Examples**: File permissions, directory ownership, ACLs

```python
def parse_permissions(content, control_id, required_permissions):
    """
    Template for checking file/directory permissions
    Returns: COMPLIANT if permissions meet security requirements
    """
    permission_issues = []
    gaps = []

    # Parse ls -la output or similar
    for line in content.split('\n'):
        parsed = parse_permission_line(line)
        if not parsed:
            continue

        path = parsed['path']
        mode = parsed['mode']
        owner = parsed['owner']
        group = parsed['group']

        # Check against required permissions
        required = required_permissions.get(path, {})

        if 'mode' in required and mode != required['mode']:
            permission_issues.append({
                "path": path,
                "issue": "Incorrect permissions",
                "actual": mode,
                "expected": required['mode']
            })

        if 'owner' in required and owner != required['owner']:
            permission_issues.append({
                "path": path,
                "issue": "Incorrect owner",
                "actual": owner,
                "expected": required['owner']
            })

        if 'max_mode' in required and is_more_permissive(mode, required['max_mode']):
            permission_issues.append({
                "path": path,
                "issue": "Too permissive",
                "actual": mode,
                "expected": f"No more than {required['max_mode']}"
            })

    # Generate gaps
    for issue in permission_issues:
        gaps.append({
            "requirement": f"{issue['path']}: {issue['issue']}",
            "actual": f"Current: {issue['actual']}",
            "severity": "HIGH" if is_critical_path(issue['path']) else "MEDIUM",
            "remediation": f"chmod {issue['expected']} {issue['path']}",
            "risk": "Unauthorized access, privilege escalation"
        })

    is_compliant = len(gaps) == 0
    compliance_score = max(0, 100 - len(gaps) * 15)

    return {
        "evidence_summary": f"Checked {len(required_permissions)} paths, {len(gaps)} issues",
        "actual_state": {"permission_issues": permission_issues},
        "expected_state": required_permissions,
        "compliance_status": "COMPLIANT" if is_compliant else "NON_COMPLIANT",
        "compliance_score": compliance_score,
        "gaps": gaps,
        "confidence": 0.95  # Very high confidence for permission checks
    }
```

**Controls Using This Template**:
- AC-005: File Permissions (sensitive system files)
- AC-018: User Home Directory Permissions
- AC-019: Shared Folder Permissions
- AC-024: Terminal Access Restrictions
- AU-007: Log Integrity Protection (/var/audit permissions)
- AU-023: Audit Trail Protection

---

## 📋 Weekly Implementation Plan

### Week 1: Access Control (18 controls)
**Days 1-2**: Binary checks (8 controls)
- AC-012, AC-013, AC-017, AC-014, AC-023

**Days 3-4**: Configuration parsers (7 controls)
- AC-011, AC-015, AC-020, AC-021, AC-022, AC-025, AC-026

**Day 5**: Permission checks (3 controls)
- AC-018, AC-019, AC-024

### Week 2: Audit & Accountability (20 controls)
**Days 1-2**: Binary and threshold checks (8 controls)
- AU-009, AU-020, AU-021, AU-011, AU-012, AU-013, AU-014, AU-024

**Days 3-4**: Configuration parsers (7 controls)
- AU-005, AU-006, AU-008, AU-010, AU-022

**Day 5**: Log parsers (5 controls)
- AU-015, AU-016, AU-017, AU-018, AU-019

### Week 3: Configuration & Identity (21 controls)
**Days 1-2**: Configuration Management (10 controls)
- CO-005, CO-006, CO-007, CO-008, CO-009, CO-010, CO-011, CO-012, CO-013, CO-014

**Days 3-5**: Identity & Authentication (11 controls)
- ID-001, ID-003, ID-004, ID-006, ID-007, ID-008, ID-009, ID-010, ID-011, ID-012, ID-013

### Week 4: System Protection & Others (11 controls)
**Days 1-2**: System Protection (8 controls)
- SY-010, SY-011, SY-012, SY-013, SY-014, SY-015, SY-016, SY-017

**Days 3-4**: Maintenance & Media (7 controls)
- MA-001, MA-002, MA-003, MA-004
- ME-001, ME-002, ME-003, ME-004, ME-005

**Day 5**: Incident Response (3 controls)
- IN-001, IN-002, IN-003

---

## 🎯 Tier 2: Document Review Controls (~90 controls)

### Definition
Controls that require policy/procedure documents to verify compliance.

### Families (Document Review Heavy):
1. **Security Policy (SE)**: 16 controls - 100% document review
2. **Awareness & Training (AW)**: 7 controls - 100% document review
3. **Personnel Security (PE)**: 11 controls - 100% document review
4. **Risk Assessment (RI)**: 3 controls - 100% document review
5. **Portions of AU, IN, CO**: ~50-60 controls require policy documents

### Implementation Approach: Engine 2 + LLM Enhancement

**Current Capability**: Engine 2 can process PDFs and extract text

**Enhancement Needed**:
```python
# Document Analysis Pipeline
def analyze_compliance_document(pdf_path, control_id):
    """
    1. Extract text from policy document
    2. Load Rwanda NCSA requirement for control
    3. Use LLM to compare document content vs requirement
    4. Return compliance status with evidence
    """

    # Extract document content
    doc_text = extract_text_from_pdf(pdf_path)

    # Load control requirement
    requirement = load_rwanda_ncsa_control(control_id)

    # LLM analysis
    prompt = f"""
    Analyze this policy document against Rwanda NCSA requirement:

    Requirement: {control_id} - {requirement['name']}
    Description: {requirement['description']}
    Compliance Criteria:
    - Pass: {requirement['compliance_criteria']['pass_conditions']}
    - Fail: {requirement['compliance_criteria']['fail_conditions']}

    Document Content:
    {doc_text[:4000]}  # First 4000 chars

    Determine:
    1. Does this document satisfy the requirement? (YES/NO)
    2. What specific sections address this requirement?
    3. What gaps exist if non-compliant?
    4. Confidence level (0-1)
    """

    llm_response = call_openai_gpt4(prompt)

    return {
        "control_id": control_id,
        "document_analyzed": pdf_path,
        "compliance_status": extract_status(llm_response),
        "evidence": extract_evidence(llm_response),
        "gaps": extract_gaps(llm_response),
        "confidence": extract_confidence(llm_response)
    }
```

**Document-Based Controls Examples**:
- SE-001: Information Security Policy exists and is documented
- SE-002: ISP approved by management
- SE-003: ISP communicated to employees
- SE-004: ISP reviewed annually
- AW-001: Security awareness training program exists
- AW-002: Training provided to all employees
- PE-001: Personnel screening procedures documented
- RI-001: Risk assessment methodology documented

**Implementation Timeline**: (after all system-auditable controls complete)

---

## 🎯 Tier 3: Manual/Physical Audit Controls (~24 controls)

### Definition
Controls requiring physical inspection or human verification.

### Families (Manual Audit Heavy):
1. **Physical Protection (PH)**: 10 controls - 100% manual
2. **Portions of AC, ME, IN**: ~14 controls require physical verification

### Implementation Approach: Checklist + Evidence Upload

**Workflow**:
```
1. Generate PDF checklist for manual controls
2. Auditor performs physical inspection
3. Auditor uploads photos/evidence via web UI
4. LLM verifies evidence completeness
5. Auditor marks control as verified
6. System records verification in audit report
```

**Manual Controls Examples**:
- PH-001: Physical access controls (badges, locks)
- PH-002: Server room access logs
- PH-003: Environmental controls (HVAC, fire suppression)
- PH-004: Physical security perimeter
- PH-005: Visitor management procedures
- PH-006: Equipment inventory and tracking
- PH-007: Secure disposal of equipment
- ME-004: Media sanitization procedures (physical verification)
- AC-020: Physical access to terminals

**Checklist Generator**:
```python
def generate_manual_audit_checklist(control_ids):
    """
    Generate PDF checklist for manual audit controls
    """
    pdf = PDFDocument()

    for control_id in control_ids:
        control = load_rwanda_ncsa_control(control_id)

        pdf.add_section(f"{control_id}: {control['name']}")
        pdf.add_text(f"Description: {control['description']}")
        pdf.add_text(f"Severity: {control['severity']}")

        pdf.add_checklist("Verification Steps:", control['manual_verification_steps'])

        pdf.add_evidence_upload_box("Upload photos/evidence:")
        pdf.add_signature_box("Auditor Signature:")
        pdf.add_date_field("Date:")
        pdf.add_notes_field("Notes:")

    pdf.save("manual_audit_checklist.pdf")
```

**Implementation Timeline**: (after all automated controls complete)

---

## 📊 Complete 169 Control Breakdown

| Family | Code | Total | System-Audit | Document | Manual | Implemented | Remaining |
|--------|------|-------|--------------|----------|--------|-------------|-----------|
| Security Policy | SE | 16 | 0 | 16 | 0 | 0 | 16 |
| Access Control | AC | 26 | 18 | 2 | 6 | 9 | 17 |
| Awareness & Training | AW | 7 | 0 | 7 | 0 | 0 | 7 |
| Audit & Accountability | AU | 26 | 24 | 2 | 0 | 6 | 20 |
| Configuration Mgmt | CO | 14 | 14 | 0 | 0 | 4 | 10 |
| Identity & Auth | ID | 13 | 13 | 0 | 0 | 2 | 11 |
| Incident Response | IN | 6 | 3 | 3 | 0 | 0 | 6 |
| Maintenance | MA | 7 | 4 | 3 | 0 | 0 | 7 |
| Media Protection | ME | 9 | 5 | 0 | 4 | 0 | 9 |
| Personnel Security | PE | 11 | 0 | 11 | 0 | 0 | 11 |
| Physical Protection | PH | 10 | 0 | 0 | 10 | 0 | 10 |
| Risk Assessment | RI | 3 | 0 | 3 | 0 | 0 | 3 |
| Security Assessment | SE | 4 | 2 | 2 | 0 | 0 | 4 |
| System Protection | SY | 17 | 17 | 0 | 0 | 9 | 8 |
| System Integrity | SI | 4 | 3 | 1 | 0 | 1 | 3 |
| **TOTAL** | | **169** | **103** | **50** | **20** | **30** | **139** |

**Note**: Numbers adjusted based on realistic macOS auditability. Original estimate of 50-60 system-auditable was conservative; actual count is ~100.

---

## ✅ Success Criteria

### Phase 1: Tier 1 Complete (Week 4 end)
- [ ] All 103 system-auditable controls defined in `rwanda_ncsa_controls.json`
- [ ] 103 intelligent parsers implemented in `evidence_parsers.py`
- [ ] 103 control-specific decisions in `rwanda_decision_engine.py`
- [ ] All parsers tested with real macOS data
- [ ] Non-compliance detection verified
- [ ] Gap analysis with remediation for all controls

### Phase 2: Tier 2 Complete (Week 6 end)
- [ ] 50 document-review controls defined
- [ ] Engine 2 enhanced with LLM document analysis
- [ ] Policy document parsing operational
- [ ] Document-based compliance scoring working

### Phase 3: Tier 3 Complete (Week 7 end)
- [ ] 20 manual audit controls defined
- [ ] PDF checklist generator operational
- [ ] Evidence upload workflow implemented
- [ ] Manual verification tracking in database

### Phase 4: Full 169 Coverage (Week 7 end)
- [ ] All 169 Rwanda NCSA controls defined
- [ ] Multi-modal audit capability (system + document + manual)
- [ ] Comprehensive compliance reports
- [ ] LLM prompts enhanced with full Rwanda NCSA context
- [ ] Ready for production deployment

---

## 🚀 Next Immediate Steps

1. **Execute this strategy** 
2. Implement AC binary checks (5 controls)
3. Implement AC config parsers (7 controls)
4. Implement AC permission checks (3 controls)
5. **Continue systematic implementation** plan

---

## 💡 Template Usage Statistics

| Template | Controls | Percentage |
|----------|----------|------------|
| Binary Check | 25 | 41.7% |
| Config Parser | 25 | 41.7% |
| Inventory Parser | 15 | 25.0% |
| Threshold Check | 10 | 16.7% |
| Permission Check | 6 | 10.0% |

**Efficiency Gain**: With 5 templates covering 81 controls (135% due to overlaps), we reduce development time by ~85% compared to writing unique logic for each control.

---

**Status**: Strategy complete, ready for systematic implementation
**Timeline**: 2 weeks to full 169 control coverage
**Current Progress**: 30/169 (17.8%) - 139 controls remaining
**Next Milestone**: 50/169 (29.6%) by this week end - 20 AC controls added
