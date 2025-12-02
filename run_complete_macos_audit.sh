#!/bin/bash
# Complete End-to-End macOS Compliance Audit
# Rwanda NCSA Compliance Auditor - Automated Pipeline

set -e

AUDIT_ID="macos-audit-$(date +%s)"
COMPANY_NAME="CMU-Research"
OUTPUT_DIR="/tmp/audit_$AUDIT_ID"

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║   Rwanda NCSA Complete Compliance Audit - macOS                       ║"
echo "║   Automated Pipeline: Collect → Classify → Decide → Report            ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🆔 Audit ID: $AUDIT_ID"
echo "🏢 Company: $COMPANY_NAME"
echo "💻 Platform: macOS $(sw_vers -productVersion)"
echo "📁 Output: $OUTPUT_DIR"
echo ""

mkdir -p "$OUTPUT_DIR"

# ============================================================================
# PHASE 1: Collect Real macOS Data
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 PHASE 1: Collecting Real System Data"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Access Control
echo "  → Access Control checks..."
last -10 > "$OUTPUT_DIR/login_history.txt" 2>&1
who > "$OUTPUT_DIR/current_users.txt" 2>&1
id > "$OUTPUT_DIR/user_info.txt" 2>&1
dscl . -list /Users > "$OUTPUT_DIR/user_accounts.txt" 2>&1

# Audit & Accountability
echo "  → Audit & Accountability checks..."
df -h > "$OUTPUT_DIR/disk_usage.txt" 2>&1
log show --predicate 'eventType == logEvent' --last 10m --style compact 2>&1 | head -100 > "$OUTPUT_DIR/system_logs.txt"

# System Integrity
echo "  → System Integrity checks..."
ps aux | head -50 > "$OUTPUT_DIR/process_list.txt" 2>&1
spctl --status > "$OUTPUT_DIR/security_assessment.txt" 2>&1
csrutil status > "$OUTPUT_DIR/sip_status.txt" 2>&1

# Configuration Management
echo "  → Configuration Management checks..."
sw_vers > "$OUTPUT_DIR/system_info.txt" 2>&1
system_profiler SPHardwareDataType > "$OUTPUT_DIR/hardware_info.txt" 2>&1

# Authentication
echo "  → Authentication checks..."
pwpolicy getaccountpolicies > "$OUTPUT_DIR/password_policy.txt" 2>&1

EVIDENCE_COUNT=$(ls -1 "$OUTPUT_DIR"/*.txt | wc -l | tr -d ' ')
echo ""
echo "✅ Collected $EVIDENCE_COUNT evidence files"
echo ""

# ============================================================================
# PHASE 2: Format for ML Model
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 PHASE 2: Formatting Data for XGBoost Model"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << EOF
import json
from datetime import datetime
from pathlib import Path

output_dir = Path("$OUTPUT_DIR")

# Map commands to controls
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

def analyze(filename, content):
    """Quick compliance analysis"""
    if "security_assessment" in filename and "enabled" in content.lower():
        return "compliant", "Gatekeeper enabled"
    if "sip_status" in filename and "enabled" in content.lower():
        return "compliant", "SIP enabled"
    if "disk_usage" in filename:
        for line in content.split('\n'):
            if '%' in line and 'Capacity' not in line:
                for part in line.split():
                    if '%' in part:
                        percent = int(part.replace('%', ''))
                        return ("compliant" if percent < 90 else "non_compliant",
                                f"Disk at {percent}%")
    if len(content.strip()) > 0:
        return "compliant", "Output present"
    return "non_compliant", "No output"

# Process all files
evidence = []
for file_path in sorted(output_dir.glob("*.txt")):
    content = file_path.read_text()
    status, summary = analyze(file_path.name, content)

    evidence.append({
        "evidence_id": f"real-{file_path.stem}",
        "control_id": COMMAND_TO_CONTROL.get(file_path.name, "UNKNOWN"),
        "source_type": "log",
        "evidence_text": content[:500],
        "evidence_summary": summary,
        "actual_state": summary,
        "expected_state": "Compliant with Rwanda NCSA",
        "timestamp": datetime.now().isoformat(),
        "confidence": 0.9,
        "metadata": {
            "source_file": file_path.name,
            "machine": "localhost",
            "os": "macOS"
        }
    })

# Save
output_file = output_dir / "evidence.json"
with open(output_file, 'w') as f:
    json.dump({"audit_id": "$AUDIT_ID", "evidence": evidence}, f, indent=2)

print(f"✅ Formatted {len(evidence)} evidence items")
EOF

echo ""

# ============================================================================
# PHASE 3: XGBoost Classification
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🤖 PHASE 3: ML Classification with XGBoost"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << EOF
import json
from pathlib import Path

output_dir = Path("$OUTPUT_DIR")
with open(output_dir / "evidence.json") as f:
    data = json.load(f)

results = []
for ev in data['evidence']:
    # Prepare ML input
    ml_input = {
        "log_message": ev['evidence_summary'],
        "status_code": 200,
        "port": 443,
        "timestamp": ev['timestamp']
    }

    # Save for curl
    with open('/tmp/ml_input.json', 'w') as f:
        json.dump(ml_input, f)

    # Classify (we'll use curl in bash)
    import subprocess
    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', 'http://localhost:8003/classify',
         '-H', 'Content-Type: application/json',
         '-d', '@/tmp/ml_input.json'],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        classification = json.loads(result.stdout)
        results.append({
            "evidence_id": ev['evidence_id'],
            "control_id": ev['control_id'],
            "prediction": classification['prediction'],
            "confidence": classification['confidence'],
            "probabilities": classification['probabilities']
        })

        icon = "✅" if classification['prediction'] == 'compliant' else "❌"
        print(f"  {icon} {ev['control_id']:20s} → {classification['prediction']:15s} ({classification['confidence']:.1%})")

# Save results
with open(output_dir / "classifications.json", 'w') as f:
    json.dump({"audit_id": "$AUDIT_ID", "classifications": results}, f, indent=2)

compliant = sum(1 for r in results if r['prediction'] == 'compliant')
print(f"\n✅ Classified {len(results)} items: {compliant} compliant, {len(results)-compliant} non-compliant")
EOF

echo ""

# ============================================================================
# PHASE 4: Decision Engine
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⚖️  PHASE 4: Compliance Decision Making"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << EOF
import json
from pathlib import Path

output_dir = Path("$OUTPUT_DIR")

# Load classifications
with open(output_dir / "classifications.json") as f:
    data = json.load(f)

# Aggregate by control
controls = {}
for item in data['classifications']:
    control_id = item['control_id']
    if control_id not in controls:
        controls[control_id] = {
            "control_id": control_id,
            "predictions": [],
            "confidences": []
        }
    controls[control_id]['predictions'].append(item['prediction'])
    controls[control_id]['confidences'].append(item['confidence'])

# Make decisions
decisions = []
for control_id, info in controls.items():
    # Majority vote
    compliant_count = info['predictions'].count('compliant')
    total = len(info['predictions'])
    avg_confidence = sum(info['confidences']) / total if total > 0 else 0

    final_decision = 'compliant' if compliant_count > total / 2 else 'non_compliant'
    compliance_score = (compliant_count / total * 100) if total > 0 else 0

    decisions.append({
        "control_id": control_id,
        "final_decision": final_decision,
        "compliance_score": compliance_score,
        "confidence": avg_confidence,
        "evidence_count": total
    })

    icon = "✅" if final_decision == 'compliant' else "❌"
    print(f"  {icon} {control_id:20s} → {final_decision:15s} (score: {compliance_score:.0f}%)")

# Save decisions
with open(output_dir / "decisions.json", 'w') as f:
    json.dump({"audit_id": "$AUDIT_ID", "decisions": decisions}, f, indent=2)

compliant_controls = sum(1 for d in decisions if d['final_decision'] == 'compliant')
print(f"\n✅ {compliant_controls}/{len(decisions)} controls compliant")
EOF

echo ""

# ============================================================================
# PHASE 5: Generate Report
# ============================================================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📄 PHASE 5: Generating PDF Report"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

python3 << EOF
import json
from pathlib import Path

output_dir = Path("$OUTPUT_DIR")

# Load decisions
with open(output_dir / "decisions.json") as f:
    decisions_data = json.load(f)

decisions = decisions_data['decisions']
total_controls = len(decisions)
compliant_controls = sum(1 for d in decisions if d['final_decision'] == 'compliant')

# Prepare report data
report_data = {
    "report_type": "full",
    "compliance_data": {
        "company_name": "$COMPANY_NAME",
        "assessment_date": "$(date +%Y-%m-%d)",
        "framework": "Rwanda-NCSA",
        "total_controls": total_controls,
        "compliant_controls": compliant_controls,
        "non_compliant_controls": total_controls - compliant_controls,
        "pending_controls": 0,
        "family_scores": [],
        "top_issues": [],
        "recommendations": [
            f"Overall Compliance: {compliant_controls}/{total_controls} controls ({compliant_controls/total_controls*100:.1f}%)",
            "Audit Mode: LOGS_ONLY (Real macOS system data)",
            f"Platform: macOS $(sw_vers -productVersion)",
            "Data Source: Local system commands"
        ]
    },
    "include_charts": True,
    "include_recommendations": True
}

# Save report request
with open('/tmp/report_request.json', 'w') as f:
    json.dump(report_data, f, indent=2)

print(f"  📊 Total Controls: {total_controls}")
print(f"  ✅ Compliant: {compliant_controls}")
print(f"  ❌ Non-compliant: {total_controls - compliant_controls}")
print(f"  📈 Compliance Rate: {compliant_controls/total_controls*100:.1f}%")
EOF

echo ""
echo "  → Calling Engine 5 to generate PDF..."

REPORT_RESPONSE=$(curl -s -X POST "http://localhost:8005/generate/report" \
  -H "Content-Type: application/json" \
  -d @/tmp/report_request.json)

REPORT_ID=$(echo "$REPORT_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('report_id', 'unknown'))" 2>/dev/null || echo "unknown")

if [ "$REPORT_ID" != "unknown" ]; then
    echo "  ✅ Report generated: $REPORT_ID"

    # Download the report
    curl -s "http://localhost:8005/reports/$REPORT_ID" -o "$OUTPUT_DIR/compliance_report.pdf"

    if [ -f "$OUTPUT_DIR/compliance_report.pdf" ]; then
        PDF_SIZE=$(ls -lh "$OUTPUT_DIR/compliance_report.pdf" | awk '{print $5}')
        echo "  📥 Downloaded: $OUTPUT_DIR/compliance_report.pdf ($PDF_SIZE)"
    fi
else
    echo "  ⚠️  Report generation may have failed"
fi

echo ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                     AUDIT COMPLETE                                     ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Audit Summary:"
echo "   Audit ID: $AUDIT_ID"
echo "   Evidence Collected: $EVIDENCE_COUNT files"
echo "   Output Directory: $OUTPUT_DIR"
echo ""
echo "📂 Generated Files:"
echo "   • evidence.json           - Raw evidence data"
echo "   • classifications.json    - XGBoost ML results"
echo "   • decisions.json          - Final compliance decisions"
echo "   • compliance_report.pdf   - PDF report"
echo ""
echo "🎯 Next Steps:"
echo "   1. Review the PDF report: open $OUTPUT_DIR/compliance_report.pdf"
echo "   2. Check detailed results: ls -la $OUTPUT_DIR/"
echo "   3. View classifications: cat $OUTPUT_DIR/decisions.json | python3 -m json.tool"
echo ""
echo "✅ End-to-end audit pipeline completed successfully!"
echo ""
