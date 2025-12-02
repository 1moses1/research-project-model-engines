#!/bin/bash
# Quick Validation Tests for Rwanda NCSA Compliance Auditor
# Run these tests to verify pipeline functionality and intelligence

set -e

BOLD='\033[1m'
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BOLD}================================${NC}"
echo -e "${BOLD}Rwanda NCSA Auditor Validation${NC}"
echo -e "${BOLD}================================${NC}"
echo ""

# ============================================================================
# TEST 1: Verify Real Data Collection
# ============================================================================
echo -e "${BOLD}TEST 1: Real Data Collection${NC}"
echo "Comparing audit evidence with actual system state..."
echo ""

# Find latest audit
LATEST_AUDIT=$(ls -td /tmp/audit_macos-audit-* 2>/dev/null | head -1)

if [ -z "$LATEST_AUDIT" ]; then
    echo -e "${RED}❌ No audit found. Run an audit first.${NC}"
    exit 1
fi

echo "Latest audit: $LATEST_AUDIT"
echo ""

# Test 1.1: SIP Status
echo -n "  SIP Status Match: "
AUDIT_SIP=$(cat "$LATEST_AUDIT/sip_status.txt" 2>/dev/null | grep -i "enabled\|disabled" || echo "NOT_FOUND")
REAL_SIP=$(csrutil status | grep -i "enabled\|disabled")

if [[ "$AUDIT_SIP" == "$REAL_SIP" ]]; then
    echo -e "${GREEN}✅ PASS${NC}"
    echo "    Audit: $AUDIT_SIP"
    echo "    Real:  $REAL_SIP"
else
    echo -e "${RED}❌ FAIL${NC}"
    echo "    Audit: $AUDIT_SIP"
    echo "    Real:  $REAL_SIP"
fi
echo ""

# Test 1.2: Disk Usage
echo -n "  Disk Usage Match: "
AUDIT_DISK=$(cat "$LATEST_AUDIT/disk_usage.txt" 2>/dev/null | grep "^/dev/disk" | head -1 | awk '{print $5}' || echo "NOT_FOUND")
REAL_DISK=$(df -h / | tail -1 | awk '{print $5}')

if [[ "$AUDIT_DISK" == "$REAL_DISK" ]]; then
    echo -e "${GREEN}✅ PASS${NC}"
    echo "    Audit: $AUDIT_DISK"
    echo "    Real:  $REAL_DISK"
else
    echo -e "${YELLOW}⚠️  APPROXIMATE${NC}"
    echo "    Audit: $AUDIT_DISK"
    echo "    Real:  $REAL_DISK"
    echo "    (Disk usage may change between runs)"
fi
echo ""

# Test 1.3: macOS Version
echo -n "  macOS Version Match: "
AUDIT_VERSION=$(cat "$LATEST_AUDIT/system_info.txt" 2>/dev/null | grep ProductVersion | awk '{print $2}' || echo "NOT_FOUND")
REAL_VERSION=$(sw_vers -productVersion)

if [[ "$AUDIT_VERSION" == "$REAL_VERSION" ]]; then
    echo -e "${GREEN}✅ PASS${NC}"
    echo "    Audit: $AUDIT_VERSION"
    echo "    Real:  $REAL_VERSION"
else
    echo -e "${RED}❌ FAIL${NC}"
    echo "    Audit: $AUDIT_VERSION"
    echo "    Real:  $REAL_VERSION"
fi
echo ""

# ============================================================================
# TEST 2: XGBoost Model Intelligence
# ============================================================================
echo -e "${BOLD}TEST 2: XGBoost Model Intelligence${NC}"
echo "Testing if model makes intelligent decisions vs random guessing..."
echo ""

# Test 2.1: Classification Confidence Diversity
echo -n "  Confidence Score Diversity: "
if [ -f "$LATEST_AUDIT/classifications.json" ]; then
    UNIQUE_CONFIDENCES=$(cat "$LATEST_AUDIT/classifications.json" | grep '"confidence"' | sort -u | wc -l | tr -d ' ')
    TOTAL_CLASSIFICATIONS=$(cat "$LATEST_AUDIT/classifications.json" | grep '"confidence"' | wc -l | tr -d ' ')

    if [ "$UNIQUE_CONFIDENCES" -eq 1 ]; then
        echo -e "${RED}❌ FAIL - All confidences identical${NC}"
        echo "    Unique: $UNIQUE_CONFIDENCES / Total: $TOTAL_CLASSIFICATIONS"
        echo "    ${YELLOW}WARNING: Model may be overfitted or using fallback logic${NC}"
    elif [ "$UNIQUE_CONFIDENCES" -ge 3 ]; then
        echo -e "${GREEN}✅ PASS - Diverse confidence scores${NC}"
        echo "    Unique: $UNIQUE_CONFIDENCES / Total: $TOTAL_CLASSIFICATIONS"
    else
        echo -e "${YELLOW}⚠️  MARGINAL - Limited diversity${NC}"
        echo "    Unique: $UNIQUE_CONFIDENCES / Total: $TOTAL_CLASSIFICATIONS"
    fi
else
    echo -e "${RED}❌ classifications.json not found${NC}"
fi
echo ""

# Test 2.2: Model Accuracy Check
echo -n "  Model Accuracy Check: "
if [ -f "engines/engine3-xgboost-classifier/models/training_metrics.json" ]; then
    TRAIN_ACC=$(cat engines/engine3-xgboost-classifier/models/training_metrics.json | grep -A 5 '"training"' | grep '"accuracy"' | awk '{print $2}' | tr -d ',')
    TEST_ACC=$(cat engines/engine3-xgboost-classifier/models/training_metrics.json | grep -A 5 '"test"' | grep '"accuracy"' | awk '{print $2}' | tr -d ',')

    if (( $(echo "$TRAIN_ACC == 1.0 && $TEST_ACC == 1.0" | bc -l) )); then
        echo -e "${RED}❌ SUSPICIOUS - 100% accuracy${NC}"
        echo "    Training: $TRAIN_ACC, Test: $TEST_ACC"
        echo "    ${YELLOW}WARNING: Perfect scores suggest overfitting${NC}"
    elif (( $(echo "$TEST_ACC >= 0.85 && $TEST_ACC < 0.95" | bc -l) )); then
        echo -e "${GREEN}✅ GOOD - Realistic accuracy${NC}"
        echo "    Training: $TRAIN_ACC, Test: $TEST_ACC"
    else
        echo -e "${YELLOW}⚠️  Review accuracy scores${NC}"
        echo "    Training: $TRAIN_ACC, Test: $TEST_ACC"
    fi
else
    echo -e "${RED}❌ training_metrics.json not found${NC}"
fi
echo ""

# ============================================================================
# TEST 3: LLM Report Quality
# ============================================================================
echo -e "${BOLD}TEST 3: LLM Report Quality${NC}"
echo "Checking if reports contain Rwanda NCSA-specific content..."
echo ""

# Test 3.1: LLM Enabled
echo -n "  LLM Integration: "
LLM_STATUS=$(curl -s http://localhost:8005/health 2>/dev/null | grep -o '"llm_enabled":[^,]*' | cut -d':' -f2 || echo "false")

if [[ "$LLM_STATUS" == *"true"* ]]; then
    echo -e "${GREEN}✅ ENABLED${NC}"
else
    echo -e "${RED}❌ DISABLED${NC}"
    echo "    ${YELLOW}WARNING: Reports may be using fallback templates${NC}"
fi
echo ""

# Test 3.2: PDF Report Exists
echo -n "  PDF Report Generated: "
PDF_REPORT=$(find "$LATEST_AUDIT" -name "compliance_report.pdf" 2>/dev/null | head -1)

if [ -f "$PDF_REPORT" ]; then
    PDF_SIZE=$(ls -lh "$PDF_REPORT" | awk '{print $5}')
    echo -e "${GREEN}✅ FOUND${NC}"
    echo "    File: $PDF_REPORT"
    echo "    Size: $PDF_SIZE"

    # Test 3.3: Extract and check content (if pdftotext available)
    if command -v pdftotext &> /dev/null; then
        echo ""
        echo -n "  Rwanda NCSA References: "
        PDF_TEXT=$(pdftotext "$PDF_REPORT" - 2>/dev/null)
        NCSA_COUNT=$(echo "$PDF_TEXT" | grep -c "RWNCSA\|Rwanda" || echo "0")

        if [ "$NCSA_COUNT" -gt 5 ]; then
            echo -e "${GREEN}✅ FOUND ($NCSA_COUNT references)${NC}"
        elif [ "$NCSA_COUNT" -gt 0 ]; then
            echo -e "${YELLOW}⚠️  LIMITED ($NCSA_COUNT references)${NC}"
        else
            echo -e "${RED}❌ NONE - Report may be generic${NC}"
        fi

        echo -n "  Technical Recommendations: "
        CMD_COUNT=$(echo "$PDF_TEXT" | grep -c "csrutil\|pwpolicy\|spctl\|sudo\|enable\|disable" || echo "0")

        if [ "$CMD_COUNT" -gt 3 ]; then
            echo -e "${GREEN}✅ FOUND ($CMD_COUNT command references)${NC}"
        else
            echo -e "${YELLOW}⚠️  LIMITED ($CMD_COUNT command references)${NC}"
            echo "    ${YELLOW}Recommendations may be generic${NC}"
        fi
    else
        echo "    ${YELLOW}Install pdftotext to validate content${NC}"
    fi
else
    echo -e "${RED}❌ NOT FOUND${NC}"
fi
echo ""

# ============================================================================
# TEST 4: Decision Engine Logic
# ============================================================================
echo -e "${BOLD}TEST 4: Decision Engine Logic${NC}"
echo "Verifying compliance decisions..."
echo ""

# Test 4.1: Decisions Exist
echo -n "  Decisions Generated: "
if [ -f "$LATEST_AUDIT/decisions.json" ]; then
    TOTAL_CONTROLS=$(cat "$LATEST_AUDIT/decisions.json" | grep '"control_id"' | wc -l | tr -d ' ')
    COMPLIANT=$(cat "$LATEST_AUDIT/decisions.json" | grep '"final_decision": "compliant"' | wc -l | tr -d ' ')
    NON_COMPLIANT=$((TOTAL_CONTROLS - COMPLIANT))

    echo -e "${GREEN}✅ PASS${NC}"
    echo "    Total Controls: $TOTAL_CONTROLS"
    echo "    Compliant: $COMPLIANT"
    echo "    Non-Compliant: $NON_COMPLIANT"

    if [ "$TOTAL_CONTROLS" -eq "$COMPLIANT" ]; then
        echo "    ${YELLOW}NOTE: 100% compliant - verify with real non-compliance test${NC}"
    fi
else
    echo -e "${RED}❌ decisions.json not found${NC}"
fi
echo ""

# ============================================================================
# TEST 5: Database Integration
# ============================================================================
echo -e "${BOLD}TEST 5: Database Integration${NC}"
echo "Checking PostgreSQL and Redis connectivity..."
echo ""

# Test 5.1: PostgreSQL
echo -n "  PostgreSQL: "
PG_STATUS=$(curl -s http://localhost:8006/api/v3/db/status 2>/dev/null | grep -o '"connected":[^,]*' | head -1 | cut -d':' -f2 || echo "false")

if [[ "$PG_STATUS" == *"true"* ]]; then
    echo -e "${GREEN}✅ CONNECTED${NC}"
    TABLE_COUNT=$(curl -s http://localhost:8006/api/v3/db/status 2>/dev/null | grep -o '"tables":[0-9]*' | cut -d':' -f2 || echo "0")
    echo "    Tables: $TABLE_COUNT"
else
    echo -e "${RED}❌ NOT CONNECTED${NC}"
fi
echo ""

# Test 5.2: Redis
echo -n "  Redis: "
REDIS_STATUS=$(curl -s http://localhost:8006/api/v3/db/status 2>/dev/null | grep -o '"redis_connected":[^,]*' | cut -d':' -f2 || echo "false")

if [[ "$REDIS_STATUS" == *"true"* ]]; then
    echo -e "${GREEN}✅ CONNECTED${NC}"
else
    echo -e "${RED}❌ NOT CONNECTED${NC}"
fi
echo ""

# ============================================================================
# SUMMARY
# ============================================================================
echo -e "${BOLD}================================${NC}"
echo -e "${BOLD}Validation Summary${NC}"
echo -e "${BOLD}================================${NC}"
echo ""

echo "Audit Analyzed: $(basename "$LATEST_AUDIT")"
echo "Report: $PDF_REPORT"
echo ""

echo -e "${BOLD}Next Steps:${NC}"
echo ""
echo "1. ${YELLOW}Test Non-Compliance Detection:${NC}"
echo "   - Disable SIP: csrutil disable (requires reboot)"
echo "   - Run audit: ./run_complete_macos_audit_clean.sh"
echo "   - Verify audit detects SIP disabled"
echo ""
echo "2. ${YELLOW}Review PDF Report:${NC}"
echo "   - Open: $PDF_REPORT"
echo "   - Check for Rwanda NCSA control references"
echo "   - Verify recommendations are specific, not generic"
echo ""
echo "3. ${YELLOW}Investigate Model:${NC}"
echo "   - If all confidences identical: Model needs retraining"
echo "   - If 100% accuracy: Likely overfitted on synthetic data"
echo ""
echo "4. ${YELLOW}Read Full Analysis:${NC}"
echo "   - cat PIPELINE_VALIDATION_ANALYSIS.md"
echo "   - cat VALIDATION_SUMMARY.md"
echo ""
echo -e "${GREEN}Validation complete!${NC}"
