# Rwanda NCSA Control Coverage Strategy
## Systematic Approach to 169 Requirements

**Date**: November 28, 2025
**Current Status**: 9/169 requirements have intelligent parsers (5.3%)

---

## 📊 Coverage Analysis

### Total Rwanda NCSA Requirements: 169
**Source**: `rwanda_ncsa_validated_controls.json`

| Family | Code | Total Reqs | macOS Auditable | Doc Review | Manual Audit |
|--------|------|------------|-----------------|------------|--------------|
| **Security Policy** | SE | 16 | 0 | 16 | 0 |
| **Access Control** | AC | 26 | 8-10 | 10 | 6 |
| **Awareness & Training** | AW | 7 | 0 | 7 | 0 |
| **Audit & Accountability** | AU | 26 | 6-8 | 12 | 6 |
| **Configuration Mgmt** | CO | 14 | 10-12 | 4 | 0 |
| **Identity & Auth** | ID | 13 | 5-7 | 6 | 2 |
| **Incident Response** | IN | 6 | 2-3 | 4 | 0 |
| **Maintenance** | MA | 7 | 3-4 | 4 | 0 |
| **Media Protection** | ME | 9 | 4-5 | 5 | 0 |
| **Personnel Security** | PE | 11 | 0 | 11 | 0 |
| **Physical Protection** | PH | 10 | 0 | 0 | 10 |
| **Risk Assessment** | RI | 3 | 0 | 3 | 0 |
| **Security Assessment** | SE | 4 | 1-2 | 3 | 0 |
| **System Protection** | SY | 17 | 10-12 | 7 | 0 |
| **TOTAL** | | **169** | **49-70** (~35%) | **92** (~55%) | **24** (~14%) |

---

## 🎯 Priority Classification

### Tier 1: System-Auditable (macOS Commands) - **49-70 requirements**
**Can be audited via CLI commands, file inspection, configuration checks**

✅ **Already Implemented (9)**:
1. AC: Login history, user accounts, active sessions
2. AU: System logs, disk usage
3. CO: System info, hardware inventory
4. ID: Password policy
5. SY: SIP, Gatekeeper

⏳ **High Priority macOS Controls (15-20 more)**:
1. **AC** (Access Control - 8 more):
   - User privilege levels (`dscl . -read /Groups/admin`)
   - SSH configuration (`cat /etc/ssh/sshd_config`)
   - File permissions on sensitive dirs (`ls -la /etc /var`)
   - Sudo configuration (`cat /etc/sudoers`)
   - Screen lock settings (`defaults read com.apple.screensaver`)
   - Remote access settings (`systemsetup -getremotelogin`)
   - Account lockout policy
   - Multi-factor authentication status

2. **AU** (Audit & Accountability - 6 more):
   - Audit daemon status (`sudo audit -n`)
   - Log forwarding configuration
   - Time synchronization (`systemsetup -getusingnetworktime`)
   - Log integrity protection
   - Audit record retention
   - Remote logging configuration

3. **CO** (Configuration Management - 10 more):
   - Software inventory (`system_profiler SPApplicationsDataType`)
   - Patch level (`softwareupdate -l`)
   - Configuration baseline comparison
   - Unauthorized software detection
   - Secure configuration settings
   - Boot configuration (`nvram -p`)
   - Kernel extensions (`kextstat`)
   - Launch daemons (`launchctl list`)
   - Installed profiles (`profiles -P`)
   - System preferences enforcement

4. **ID** (Identity & Authentication - 5 more):
   - Keychain configuration
   - Touch ID/biometric settings
   - Certificate store validation
   - Kerberos configuration
   - LDAP/directory integration

5. **SY** (System Protection - 10 more):
   - Firewall status (`sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate`)
   - Network configuration (`ifconfig`, `networksetup`)
   - Bluetooth status (`defaults read /Library/Preferences/com.apple.Bluetooth`)
   - File vault encryption status (`fdesetup status`)
   - Anti-malware status (`system_profiler SPInstallHistoryDataType | grep -i "xprotect"`)
   - USB restrictions
   - Network services
   - Sharing services (`systemsetup -getremotelogin`)
   - Wi-Fi security (`networksetup -listpreferredwirelessnetworks`)
   - VPN configuration

### Tier 2: Document Review Required - **~92 requirements**
**Cannot be automated - require policy/procedure documents**

Examples:
- Security policies documented (SE-1 through SE-16)
- Training programs exist (AW-1 through AW-7)
- Incident response plans (IN-1 through IN-6)
- Risk assessments performed (RI-1 through RI-3)
- Personnel security clearances (PE-1 through PE-11)

**Solution**: Engine 2 (Document Processor) + LLM analysis

### Tier 3: Manual/Physical Audit - **~24 requirements**
**Require physical inspection or human verification**

Examples:
- Physical access controls (badges, locks)
- Server room environmental controls
- Visitor logs
- Equipment disposal procedures

**Solution**: Manual checklist + photo evidence upload

---

## 🚀 Implementation Strategy

### Phase 1: Complete Tier 1 (System-Auditable) - **Target: 50-60 controls**

**Step 1**: Expand `rwanda_ncsa_controls.json` (3-5 days)
- Add 40-50 more macOS-auditable controls
- Define requirements, thresholds, remediation for each
- Map to macOS commands

**Step 2**: Implement Parsers (5-7 days)
- Create 40-50 more parser functions
- Extract values from command outputs
- Compare against requirements
- Generate gaps and remediation

**Step 3**: Add Decision Logic (3-5 days)
- Implement control-specific decision functions
- Define pass/fail criteria per control
- Calculate compliance scores

**Step 4**: Test & Validate (2-3 days)
- Unit tests for each parser
- Integration tests for pipeline
- Non-compliance detection tests

**Total: 13-20 days** for complete Tier 1 coverage

### Phase 2: Integrate Tier 2 (Document Review) - **Target: 90+ controls**

**Approach**: Use existing Engine 2 + LLM enhancement

1. User uploads policy documents (PDFs)
2. Engine 2 extracts requirements
3. LLM compares document content to Rwanda NCSA requirements
4. Generate compliance report for document-based controls

**Example**:
```
Requirement SE-1: "Organization has documented ISP"
Document Found: "InfoSec_Policy_v2.1.pdf"
LLM Analysis: ✅ Document contains required sections (scope, responsibilities, enforcement)
Compliance: COMPLIANT (document-based)
```

### Phase 3: Manual Audit Workflow - **Target: 24 controls**

**Approach**: Checklist + Evidence Upload

1. Generate checklist for manual controls
2. Auditor performs physical inspection
3. Upload photos/evidence
4. LLM verifies evidence completeness
5. Mark as verified by auditor

---

## 📋 Detailed Expansion Plan

### Week 1-2: Core System Security (20 controls)

**Access Control (AC)**:
- [ ] AC-003: Account privilege management
- [ ] AC-004: SSH configuration security
- [ ] AC-005: File and directory permissions
- [ ] AC-006: Sudo configuration
- [ ] AC-007: Screen lock enforcement
- [ ] AC-008: Remote access control
- [ ] AC-011: Account lockout policy
- [ ] AC-012: Multi-factor authentication

**Audit & Accountability (AU)**:
- [ ] AU-001: Audit daemon configuration
- [ ] AU-003: Time synchronization
- [ ] AU-005: Log forwarding
- [ ] AU-006: Audit record retention
- [ ] AU-007: Log integrity
- [ ] AU-008: Remote logging

**System Protection (SY)**:
- [ ] SY-001: Firewall configuration
- [ ] SY-002: FileVault encryption
- [ ] SY-003: Bluetooth security
- [ ] SY-004: Network configuration
- [ ] SY-005: Anti-malware status
- [ ] SY-006: Sharing services

### Week 3-4: Configuration & Identity (20 controls)

**Configuration Management (CO)**:
- [ ] CO-001: Software inventory
- [ ] CO-003: Patch management
- [ ] CO-004: Baseline compliance
- [ ] CO-005: Unauthorized software detection
- [ ] CO-006: Boot configuration
- [ ] CO-007: Kernel extensions
- [ ] CO-008: Launch daemons
- [ ] CO-009: Configuration profiles
- [ ] CO-010: System preferences

**Identity & Authentication (ID)**:
- [ ] ID-001: Keychain security
- [ ] ID-002: Biometric settings
- [ ] ID-003: Certificate store
- [ ] ID-004: Kerberos configuration
- [ ] ID-006: Directory integration

**Maintenance (MA)**:
- [ ] MA-001: System update status
- [ ] MA-002: Maintenance scheduling
- [ ] MA-003: Remote maintenance controls

**Media Protection (ME)**:
- [ ] ME-001: USB device restrictions
- [ ] ME-002: External media encryption
- [ ] ME-003: Removable media policy
- [ ] ME-004: Media sanitization

### Week 5: Network & Communications (10 controls)

**System Protection (SY) - Continued**:
- [ ] SY-007: Wi-Fi security
- [ ] SY-008: VPN configuration
- [ ] SY-009: DNS configuration
- [ ] SY-010: Proxy settings
- [ ] SY-011: Network services
- [ ] SY-012: Port security
- [ ] SY-013: Protocol restrictions
- [ ] SY-014: Encryption standards
- [ ] SY-015: Network segmentation
- [ ] SY-016: Wireless security

---

## 🎯 Realistic Near-Term Goal

### Target: 30 Controls by End of Week 1

**Already Done (9)**:
- AC-001, AC-002, AC-010
- AU-002, AU-004
- CO-002
- ID-005
- SY-003, SY-007

**Add This Week (21)**:
1. **Access Control (6)**:
   - AC-003: Privilege management
   - AC-004: SSH security
   - AC-005: File permissions
   - AC-006: Sudo config
   - AC-007: Screen lock
   - AC-008: Remote access

2. **Audit (5)**:
   - AU-001: Audit daemon
   - AU-003: Time sync
   - AU-005: Log forwarding
   - AU-006: Retention
   - AU-008: Remote logging

3. **System Protection (8)**:
   - SY-001: Firewall
   - SY-002: FileVault
   - SY-003: Bluetooth
   - SY-004: Network
   - SY-005: Anti-malware
   - SY-006: Sharing
   - SY-007: Wi-Fi
   - SY-008: VPN

4. **Configuration (2)**:
   - CO-001: Software inventory
   - CO-003: Patch status

---

## 💡 Smart Approach: Templating

Instead of writing 169 unique functions, **use templates for similar controls**:

### Template 1: Binary Check (enabled/disabled)
Used for: Firewall, FileVault, SIP, Gatekeeper, Bluetooth, etc.
```python
def parse_binary_feature(content, control_id, feature_name, enabled_pattern):
    is_enabled = enabled_pattern in content.lower()
    is_compliant = is_enabled
    # ... standard gap analysis
```

### Template 2: Configuration File Parser
Used for: SSH config, Sudo config, Profiles, etc.
```python
def parse_config_file(content, control_id, required_settings):
    actual_settings = extract_settings(content)
    gaps = compare_with_required(actual_settings, required_settings)
    # ... standard compliance check
```

### Template 3: List/Inventory Parser
Used for: Software inventory, user list, process list, etc.
```python
def parse_inventory(content, control_id, expected_items, forbidden_items):
    actual_items = parse_list(content)
    missing = expected_items - actual_items
    unauthorized = actual_items & forbidden_items
    # ... generate gaps
```

### Template 4: Threshold Check
Used for: Disk usage, password age, session count, etc.
```python
def parse_threshold_value(content, control_id, threshold, operator):
    actual_value = extract_number(content)
    is_compliant = compare(actual_value, threshold, operator)
    # ... score based on proximity to threshold
```

**With 4-5 templates, we can cover 80% of the 50-60 system-auditable controls!**

---

## 🎓 Recommendation

### Immediate Action (This Week):
1. ✅ **Accept 9 controls as MVP** - Core security working
2. 🚀 **Expand to 30 controls** - Add critical security controls (firewall, encryption, network)
3. 📝 **Document templating strategy** - Reuse patterns for rapid expansion

### Medium Term (2-3 Weeks):
4. 📊 **Reach 50-60 system-auditable controls** - Full Tier 1 coverage
5. 🤖 **Enhance Engine 2 for document review** - Cover Tier 2 (90 controls)
6. ✅ **Add manual audit workflow** - Cover Tier 3 (24 controls)

### Long Term (1-2 Months):
7. 🎯 **Full 169 control coverage** - All Rwanda NCSA requirements
8. 🔄 **Add Linux & Windows support** - Multi-platform auditing
9. 📈 **Continuous compliance monitoring** - Real-time dashboards

---

## 📈 Coverage Roadmap

```
Current:     9/169 (5.3%)  [=========================>                      ]
Week 1:     30/169 (17.8%) [==========>                                       ]
Month 1:    60/169 (35.5%) [===================>                              ]
Month 2:   120/169 (71.0%) [====================================>             ]
Month 3:   169/169 (100%)  [==================================================]
```

---

## ✅ Decision Point

**Question**: Should we:
- **Option A**: Complete all 169 controls systematically (3 months, 100% coverage)
- **Option B**: Focus on 30-50 critical system-auditable controls (2 weeks, 80/20 rule)
- **Option C**: Current 9 controls are sufficient for MVP demo (ship now, expand later)

**Recommendation**: **Option B** - Expand to 30 critical controls this week (firewall, encryption, network, patches). This covers the most important security posture checks and demonstrates intelligence without 3-month development cycle.

**Reasoning**:
- 9 controls prove the intelligent parser concept ✅
- 30 controls cover critical security areas ✅
- 169 controls is comprehensive but not urgent for MVP ⏰
- Template-based approach makes future expansion easy 🚀

---

*Status*: Strategy documented, ready for expansion plan execution
*Next*: Decide coverage target and begin systematic expansion
