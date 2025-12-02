#!/bin/bash
# Collect REAL macOS compliance data from THIS machine
# Based on Rwanda NCSA macOS taxonomy

set -e

AUDIT_ID="real-macos-$(date +%s)"
OUTPUT_DIR="/tmp/macos_audit_$AUDIT_ID"
mkdir -p "$OUTPUT_DIR"

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   Rwanda NCSA - Real macOS Compliance Data Collection        ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Audit ID: $AUDIT_ID"
echo "Output Dir: $OUTPUT_DIR"
echo ""

# ============================================================================
# Access Control Family
# ============================================================================
echo "📋 Access Control Checks..."

# AC-001: Login history
echo "  1. Checking login history..."
last -10 > "$OUTPUT_DIR/login_history.txt" 2>&1 || echo "Command failed" > "$OUTPUT_DIR/login_history.txt"

# AC-010: Current users
echo "  2. Checking active users..."
who > "$OUTPUT_DIR/current_users.txt" 2>&1 || echo "Command failed" > "$OUTPUT_DIR/current_users.txt"

# AC-002: User info
echo "  3. Checking user identity..."
id > "$OUTPUT_DIR/user_info.txt" 2>&1 || echo "Command failed" > "$OUTPUT_DIR/user_info.txt"

# AC-002: User accounts list
echo "  4. Listing all user accounts..."
dscl . -list /Users > "$OUTPUT_DIR/user_accounts.txt" 2>&1 || echo "Command failed" > "$OUTPUT_DIR/user_accounts.txt"

# ============================================================================
# Audit and Accountability Family
# ============================================================================
echo "📊 Audit & Accountability Checks..."

# AU-004: Disk usage
echo "  5. Checking disk usage..."
df -h > "$OUTPUT_DIR/disk_usage.txt" 2>&1 || echo "Command failed" > "$OUTPUT_DIR/disk_usage.txt"

# AU-002: Recent system logs (last 10 minutes)
echo "  6. Collecting recent system logs..."
log show --predicate 'eventType == logEvent' --last 10m --style compact 2>&1 | head -100 > "$OUTPUT_DIR/system_logs.txt" || echo "Command failed" > "$OUTPUT_DIR/system_logs.txt"

# ============================================================================
# System and Information Integrity Family
# ============================================================================
echo "🔒 System Integrity Checks..."

# SI-003: Running processes (security software)
echo "  7. Checking running processes..."
ps aux | head -50 > "$OUTPUT_DIR/process_list.txt" 2>&1 || echo "Command failed" > "$OUTPUT_DIR/process_list.txt"

# SI-007: Gatekeeper status
echo "  8. Checking Gatekeeper status..."
spctl --status > "$OUTPUT_DIR/security_assessment.txt" 2>&1 || echo "Command failed" > "$OUTPUT_DIR/security_assessment.txt"

# SI-007: System Integrity Protection
echo "  9. Checking SIP status..."
csrutil status > "$OUTPUT_DIR/sip_status.txt" 2>&1 || echo "Requires reboot to Recovery mode" > "$OUTPUT_DIR/sip_status.txt"

# ============================================================================
# Configuration Management Family
# ============================================================================
echo "⚙️  Configuration Management Checks..."

# CM-002: System version
echo "  10. Getting macOS version..."
sw_vers > "$OUTPUT_DIR/system_info.txt" 2>&1 || echo "Command failed" > "$OUTPUT_DIR/system_info.txt"

# CM-002: Hardware info
echo "  11. Getting hardware info..."
system_profiler SPHardwareDataType > "$OUTPUT_DIR/hardware_info.txt" 2>&1 || echo "Command failed" > "$OUTPUT_DIR/hardware_info.txt"

# ============================================================================
# Identification and Authentication Family
# ============================================================================
echo "🔑 Authentication Checks..."

# IA-005: Password policy
echo "  12. Checking password policy..."
pwpolicy getaccountpolicies > "$OUTPUT_DIR/password_policy.txt" 2>&1 || echo "Command failed" > "$OUTPUT_DIR/password_policy.txt"

# ============================================================================
# Summary
# ============================================================================
echo ""
echo "✅ Data collection complete!"
echo ""
echo "Collected files:"
ls -lh "$OUTPUT_DIR/"
echo ""
echo "Total files: $(ls -1 "$OUTPUT_DIR/" | wc -l | tr -d ' ')"
echo ""
echo "Next step: Format this data for XGBoost model"
echo "Output directory: $OUTPUT_DIR"
echo "$OUTPUT_DIR" > /tmp/last_macos_audit_dir.txt
