#!/bin/bash
################################################################################
# Test script for Rwanda NCSA Compliance Monitoring in Kubernetes
# Tests real-time violation detection from simulated pods
#
# Author: Moise Iradukunda (CMU)
# Date: November 2025
################################################################################

API_URL="http://localhost:8080"

echo "================================================================================"
echo "Rwanda NCSA Compliance Monitoring - Kubernetes Test Suite"
echo "================================================================================"
echo "Test Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "API Endpoint: $API_URL"
echo ""

# Test health
echo "================================================================================"
echo "TESTING API HEALTH"
echo "================================================================================"
HEALTH=$(curl -s "$API_URL/health")
echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
echo ""

# Counter for results
TOTAL_TESTS=0
CORRECT=0
WRONG=0

# Function to test prediction
test_prediction() {
    local NAME="$1"
    local POD="$2"
    local LOG_MESSAGE="$3"
    local CONTROL_ID="$4"
    local CONTROL_FAMILY="$5"
    local EXPECTED="$6"
    local SEVERITY="$7"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo "--------------------------------------------------------------------------------"
    echo "[$TOTAL_TESTS] Testing: $NAME"
    echo "    Pod: $POD"
    echo "    Control: $CONTROL_ID ($CONTROL_FAMILY)"
    echo "    Severity: $SEVERITY"
    echo "    Expected: $EXPECTED"

    # Create JSON payload
    PAYLOAD=$(cat <<EOF
{
    "log_message": "$LOG_MESSAGE",
    "control_id": "$CONTROL_ID",
    "control_family": "$CONTROL_FAMILY",
    "framework": "NIST"
}
EOF
)

    # Make prediction
    RESPONSE=$(curl -s -X POST "$API_URL/predict" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD")

    # Extract status and confidence
    STATUS=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('compliance_status', 'error'))" 2>/dev/null)
    CONFIDENCE=$(echo "$RESPONSE" | python3 -c "import sys, json; print('{:.1%}'.format(json.load(sys.stdin).get('confidence', 0)))" 2>/dev/null)

    if [ "$STATUS" == "$EXPECTED" ]; then
        echo "    ✓ CORRECT: $STATUS (confidence: $CONFIDENCE)"
        CORRECT=$((CORRECT + 1))
    else
        echo "    ✗ WRONG: Predicted $STATUS, expected $EXPECTED (confidence: $CONFIDENCE)"
        WRONG=$((WRONG + 1))
    fi

    sleep 0.5
}

echo "================================================================================"
echo "TESTING COMPLIANCE VIOLATION DETECTION"
echo "================================================================================"
echo ""

# Test 1: Unauthorized SSH Access
test_prediction \
    "Unauthorized SSH Access" \
    "violation-unauthorized-ssh" \
    "FAILED SSH login attempt from 192.168.1.100 for user admin - Access denied" \
    "AC-3" \
    "Access Control" \
    "non_compliant" \
    "HIGH"

# Test 2: Phishing Detection
test_prediction \
    "Phishing Detection" \
    "violation-phishing" \
    "ALERT: Suspicious email detected from external domain - Potential phishing attempt blocked" \
    "SI-4" \
    "System and Information Integrity" \
    "non_compliant" \
    "HIGH"

# Test 3: Data Exfiltration (using AC-17 - Remote Access)
test_prediction \
    "Data Exfiltration" \
    "violation-data-exfil" \
    "WARNING: Large data transfer detected to unknown IP 203.0.113.50 - 5GB in 10 minutes" \
    "AC-17" \
    "Access Control" \
    "non_compliant" \
    "CRITICAL"

# Test 4: Privilege Escalation
test_prediction \
    "Privilege Escalation" \
    "violation-priv-escalation" \
    "CRITICAL: User jdoe attempted sudo privilege escalation - Permission denied" \
    "AC-6" \
    "Access Control" \
    "non_compliant" \
    "CRITICAL"

# Test 5: Malware Detection
test_prediction \
    "Malware Detection" \
    "violation-malware" \
    "ALERT: Malicious file detected - trojan.exe quarantined by antivirus" \
    "SI-3" \
    "System and Information Integrity" \
    "non_compliant" \
    "CRITICAL"

# Test 6: DDoS Attack
test_prediction \
    "DDoS Attack" \
    "violation-ddos" \
    "CRITICAL: DDoS attack detected - 100000 requests/sec from botnet - Rate limiting activated" \
    "SC-5" \
    "System and Communications Protection" \
    "non_compliant" \
    "CRITICAL"

# Test 7: Insider Threat
test_prediction \
    "Insider Threat" \
    "violation-insider-threat" \
    "WARNING: Employee accessing sensitive customer database outside business hours - Anomalous behavior flagged" \
    "PS-3" \
    "Personnel Security" \
    "non_compliant" \
    "MEDIUM"

# Test 8: Compliant Activity (Baseline)
test_prediction \
    "Compliant Activity (Baseline)" \
    "compliant-activity" \
    "INFO: User logged in successfully with MFA - Account access granted" \
    "AC-2" \
    "Access Control" \
    "compliant" \
    "NONE"

# Print summary
echo ""
echo "================================================================================"
echo "TEST SUMMARY"
echo "================================================================================"
echo ""
echo "Total Tests: $TOTAL_TESTS"
echo "Correct Predictions: $CORRECT"
echo "Wrong Predictions: $WRONG"

ACCURACY=$(python3 -c "print(f'{($CORRECT / $TOTAL_TESTS * 100):.2f}%')")
echo "Test Accuracy: $ACCURACY"
echo ""

if [ $WRONG -eq 0 ]; then
    echo "✓ ALL TESTS PASSED!"
    exit 0
else
    echo "✗ SOME TESTS FAILED"
    exit 1
fi
