#!/usr/bin/env python3
"""
Format real macOS audit data for XGBoost classification
Converts command outputs into the format expected by the trained model
"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Map commands to Rwanda NCSA controls
COMMAND_TO_CONTROL = {
    "login_history.txt": "RWNCSA-AC-001",
    "current_users.txt": "RWNCSA-AC-010",
    "user_info.txt": "RWNCSA-AC-002",
    "user_accounts.txt": "RWNCSA-AC-002",
    "disk_usage.txt": "RWNCSA-AU-004",
    "system_logs.txt": "RWNCSA-AU-002",
    "process_list.txt": "RWNCSA-SI-003",
    "security_assessment.txt": "RWNCSA-SI-007",
    "sip_status.txt": "RWNCSA-SI-007",
    "system_info.txt": "RWNCSA-CM-002",
    "hardware_info.txt": "RWNCSA-CM-002",
    "password_policy.txt": "RWNCSA-IA-005"
}

def analyze_output(filename, content):
    """Analyze command output and determine compliance"""

    # Gatekeeper check
    if filename == "security_assessment.txt":
        if "assessments enabled" in content.lower():
            return "compliant", "Gatekeeper is enabled - applications are being verified"
        else:
            return "non_compliant", "Gatekeeper is disabled - unverified apps can run"

    # SIP check
    if filename == "sip_status.txt":
        if "enabled" in content.lower():
            return "compliant", "System Integrity Protection is enabled"
        else:
            return "non_compliant", "System Integrity Protection is disabled"

    # Disk usage check
    if filename == "disk_usage.txt":
        lines = content.split('\n')
        for line in lines:
            if '%' in line and 'Capacity' not in line:
                # Extract percentage
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        percent = int(part.replace('%', ''))
                        if percent < 90:
                            return "compliant", f"Disk usage at {percent}% - sufficient space for audit logs"
                        else:
                            return "non_compliant", f"Disk usage at {percent}% - insufficient space"
        return "compliant", "Disk space available for audit logs"

    # System version check
    if filename == "system_info.txt":
        if "ProductVersion" in content:
            return "compliant", "macOS version information available"
        return "non_compliant", "Cannot determine macOS version"

    # Login history check
    if filename == "login_history.txt":
        if len(content.strip()) > 0 and "still logged in" in content.lower():
            return "compliant", "Login history is being recorded"
        return "partial", "Login history exists but may need review"

    # User accounts check
    if filename == "user_accounts.txt":
        users = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('_')]
        if len(users) > 0:
            return "compliant", f"User accounts are managed ({len(users)} non-system users)"
        return "non_compliant", "No user accounts found"

    # Process list check (for security software)
    if filename == "process_list.txt":
        security_indicators = ["mdworker", "coreauthd", "securityd", "trustd"]
        found = [ind for ind in security_indicators if ind.lower() in content.lower()]
        if found:
            return "compliant", f"Security processes running: {', '.join(found)}"
        return "partial", "Some security processes may not be running"

    # Password policy check
    if filename == "password_policy.txt":
        if len(content.strip()) > 50:  # Has substantial policy content
            return "compliant", "Password policy is configured"
        return "non_compliant", "Password policy not found or empty"

    # Default: if we have output, consider it compliant
    if len(content.strip()) > 0:
        return "compliant", "Command executed successfully with output"

    return "non_compliant", "Command failed or produced no output"


def main():
    if len(sys.argv) < 2:
        print("Usage: python format_for_xgboost.py <audit_output_directory>")
        sys.exit(1)

    audit_dir = Path(sys.argv[1])
    if not audit_dir.exists():
        print(f"Error: Directory {audit_dir} does not exist")
        sys.exit(1)

    print("=" * 70)
    print("Formatting Real macOS Data for XGBoost Classification")
    print("=" * 70)
    print(f"Input Directory: {audit_dir}")
    print()

    # Collect all evidence
    evidence_items = []

    for file_path in sorted(audit_dir.glob("*.txt")):
        filename = file_path.name
        control_id = COMMAND_TO_CONTROL.get(filename, "UNKNOWN")

        # Read the actual output
        content = file_path.read_text()

        # Analyze for compliance
        status, finding = analyze_output(filename, content)

        # Create evidence item in format similar to what Engine 1 would produce
        evidence = {
            "evidence_id": f"real-{filename.replace('.txt', '')}",
            "control_id": control_id,
            "source_type": "log",  # Real system command output
            "evidence_text": content[:500],  # First 500 chars for ML
            "evidence_summary": finding,
            "actual_state": finding,
            "expected_state": "System should be compliant with Rwanda NCSA standards",
            "timestamp": datetime.now().isoformat(),
            "confidence": 0.9,  # High confidence - this is real data
            "metadata": {
                "source_file": filename,
                "data_size": len(content),
                "machine": "localhost",
                "os": "macOS"
            }
        }

        evidence_items.append(evidence)

        # Print status
        status_icon = "✅" if status == "compliant" else "⚠️" if status == "partial" else "❌"
        print(f"{status_icon} {control_id:20s} | {filename:30s} | {status:15s}")

    # Save formatted data
    output_file = audit_dir / "formatted_for_xgboost.json"
    with open(output_file, 'w') as f:
        json.dump({
            "audit_id": audit_dir.name,
            "total_evidence": len(evidence_items),
            "evidence": evidence_items,
            "collected_at": datetime.now().isoformat()
        }, f, indent=2)

    print()
    print("=" * 70)
    print(f"✅ Formatted {len(evidence_items)} evidence items")
    print(f"📄 Output: {output_file}")
    print()
    print("Summary:")
    compliant = sum(1 for e in evidence_items if "compliant" in analyze_output(e["metadata"]["source_file"], e["evidence_text"])[0])
    print(f"  - Compliant: {compliant}")
    print(f"  - Non-compliant/Partial: {len(evidence_items) - compliant}")
    print()
    print("Next step: Send this to XGBoost for classification")
    print("=" * 70)

    # Save path for next step
    with open('/tmp/xgboost_input.json', 'w') as f:
        f.write(str(output_file))

if __name__ == "__main__":
    main()
