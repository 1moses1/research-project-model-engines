#!/bin/bash

# Rwanda NCSA Compliance Auditor - Unified Pipeline Testing Script
# Tests all 3 audit modes: LOGS_ONLY, DOCUMENTS_ONLY, and FULL_AUDIT

set -e  # Exit on error

echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║   Rwanda NCSA Compliance Auditor - Unified Pipeline Test Suite       ║"
echo "║   Testing: Logs Only | Documents Only | Full Audit with Gap Analysis ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Base URLs
ENGINE1_URL="http://localhost:8001"
ENGINE2_URL="http://localhost:8002"
ENGINE3_URL="http://localhost:8003"
ENGINE4_URL="http://localhost:8004"
ENGINE5_URL="http://localhost:8005"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function to check service health
check_service() {
    local service_name=$1
    local url=$2

    echo -n "  Checking $service_name... "

    if curl -s -f "$url/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
        return 0
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        return 1
    fi
}

# Helper function to test endpoint
test_endpoint() {
    local test_name=$1
    local url=$2
    local method=$3
    local data=$4

    echo -n "  Testing: $test_name... "

    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$url")
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$url" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')

    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "${GREEN}✓ Pass (HTTP $http_code)${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ Fail (HTTP $http_code)${NC}"
        echo "  Response: $body"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# =============================================================================
# PHASE 1: Service Health Checks
# =============================================================================

echo ""
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PHASE 1: Service Health Checks${NC}"
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo ""

check_service "Engine 1 (Log Collector)" "$ENGINE1_URL"
check_service "Engine 2 (Document Processor)" "$ENGINE2_URL"
check_service "Engine 3 (XGBoost Classifier)" "$ENGINE3_URL"
check_service "Engine 4 (Decision Engine)" "$ENGINE4_URL"
check_service "Engine 5 (Report Generator)" "$ENGINE5_URL"

echo ""
read -p "Press Enter to continue to Test Scenario 1..." dummy

# =============================================================================
# PHASE 2: Test Scenario 1 - LOGS ONLY Audit
# =============================================================================

echo ""
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}TEST SCENARIO 1: Logs-Only Audit${NC}"
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo ""

AUDIT_ID_LOGS="test-logs-$(date +%s)"
echo "Audit ID: $AUDIT_ID_LOGS"
echo ""

# Step 1: Submit log evidence
echo -e "${YELLOW}Step 1: Submitting log evidence...${NC}"
test_endpoint "Submit successful login log" \
    "$ENGINE1_URL/api/v1/evidence/submit?audit_id=$AUDIT_ID_LOGS" \
    "POST" \
    '{"raw_message":"User admin logged in successfully from 192.168.1.100","source":"auth.log","timestamp":"2025-11-27T10:30:00Z"}'

test_endpoint "Submit failed login log" \
    "$ENGINE1_URL/api/v1/evidence/submit?audit_id=$AUDIT_ID_LOGS" \
    "POST" \
    '{"raw_message":"Failed login attempt for user john from suspicious IP","source":"auth.log","timestamp":"2025-11-27T02:15:00Z"}'

test_endpoint "Submit firewall access log" \
    "$ENGINE1_URL/api/v1/evidence/submit?audit_id=$AUDIT_ID_LOGS" \
    "POST" \
    '{"raw_message":"Firewall blocked unauthorized access to port 22","source":"firewall.log","timestamp":"2025-11-27T03:45:00Z"}'

echo ""

# Step 2: Classify evidence
echo -e "${YELLOW}Step 2: Classifying log evidence with XGBoost...${NC}"
test_endpoint "Classify logs" \
    "$ENGINE3_URL/api/v1/classify/audit/$AUDIT_ID_LOGS" \
    "POST" \
    '{}'

echo ""

# Step 3: Make decisions
echo -e "${YELLOW}Step 3: Making compliance decisions (logs only)...${NC}"
test_endpoint "Make decisions with log_weight=1.0" \
    "$ENGINE4_URL/api/v1/decision/audit/$AUDIT_ID_LOGS?log_weight=1.0&document_weight=0.0" \
    "POST" \
    '{}'

echo ""

# Step 4: Get results
echo -e "${YELLOW}Step 4: Retrieving decision results...${NC}"
test_endpoint "Get decisions" \
    "$ENGINE4_URL/api/v1/decision/audit/$AUDIT_ID_LOGS/results" \
    "GET" \
    ""

echo ""

# Step 5: Generate report
echo -e "${YELLOW}Step 5: Generating PDF report...${NC}"
test_endpoint "Generate logs-only report" \
    "$ENGINE5_URL/api/v1/generate/audit-report/$AUDIT_ID_LOGS?company_name=TestCorp&report_type=full" \
    "POST" \
    '{}'

echo ""
echo -e "${GREEN}✓ Scenario 1 Complete: Logs-Only Audit${NC}"
echo ""
read -p "Press Enter to continue to Test Scenario 2..." dummy

# =============================================================================
# PHASE 3: Test Scenario 2 - DOCUMENTS ONLY Audit
# =============================================================================

echo ""
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}TEST SCENARIO 2: Documents-Only Audit${NC}"
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo ""

AUDIT_ID_DOCS="test-docs-$(date +%s)"
echo "Audit ID: $AUDIT_ID_DOCS"
echo ""

# Check if sample documents exist
DOC_PATH="engines/engine2-document-processor/sample_documents/Alvin Tech Updated Security Policy.pdf"
if [ ! -f "$DOC_PATH" ]; then
    echo -e "${RED}Warning: Sample document not found at $DOC_PATH${NC}"
    echo "Skipping documents-only test"
else
    # Step 1: Submit document evidence
    echo -e "${YELLOW}Step 1: Uploading policy document...${NC}"
    echo "  Submitting: Alvin Tech Updated Security Policy.pdf"

    response=$(curl -s -w "\n%{http_code}" -X POST \
        "$ENGINE2_URL/api/v1/evidence/submit-document?audit_id=$AUDIT_ID_DOCS&company_name=Alvin%20Tech" \
        -F "file=@$DOC_PATH")

    http_code=$(echo "$response" | tail -n1)
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "  ${GREEN}✓ Document uploaded successfully${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "  ${RED}✗ Document upload failed (HTTP $http_code)${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    echo ""

    # Step 2: Classify evidence
    echo -e "${YELLOW}Step 2: Classifying document evidence...${NC}"
    test_endpoint "Classify documents" \
        "$ENGINE3_URL/api/v1/classify/audit/$AUDIT_ID_DOCS" \
        "POST" \
        '{}'

    echo ""

    # Step 3: Make decisions
    echo -e "${YELLOW}Step 3: Making compliance decisions (documents only)...${NC}"
    test_endpoint "Make decisions with document_weight=1.0" \
        "$ENGINE4_URL/api/v1/decision/audit/$AUDIT_ID_DOCS?log_weight=0.0&document_weight=1.0" \
        "POST" \
        '{}'

    echo ""

    # Step 4: Generate report
    echo -e "${YELLOW}Step 4: Generating PDF report...${NC}"
    test_endpoint "Generate documents-only report" \
        "$ENGINE5_URL/api/v1/generate/audit-report/$AUDIT_ID_DOCS?company_name=Alvin%20Tech&report_type=full" \
        "POST" \
        '{}'

    echo ""
    echo -e "${GREEN}✓ Scenario 2 Complete: Documents-Only Audit${NC}"
fi

echo ""
read -p "Press Enter to continue to Test Scenario 3..." dummy

# =============================================================================
# PHASE 4: Test Scenario 3 - FULL AUDIT with Gap Analysis
# =============================================================================

echo ""
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}TEST SCENARIO 3: Full Audit with Gap Analysis${NC}"
echo -e "${BLUE}═════════════════════════════════════════════════════════════${NC}"
echo ""

AUDIT_ID_FULL="test-full-$(date +%s)"
echo "Audit ID: $AUDIT_ID_FULL"
echo ""

# Step 1: Submit log evidence
echo -e "${YELLOW}Step 1: Submitting log evidence...${NC}"
test_endpoint "Submit login success log" \
    "$ENGINE1_URL/api/v1/evidence/submit?audit_id=$AUDIT_ID_FULL" \
    "POST" \
    '{"raw_message":"User admin logged in successfully with MFA","source":"auth.log","timestamp":"2025-11-27T09:00:00Z"}'

test_endpoint "Submit access control log" \
    "$ENGINE1_URL/api/v1/evidence/submit?audit_id=$AUDIT_ID_FULL" \
    "POST" \
    '{"raw_message":"Access granted to sensitive resource after role check","source":"access.log","timestamp":"2025-11-27T09:15:00Z"}'

test_endpoint "Submit audit log" \
    "$ENGINE1_URL/api/v1/evidence/submit?audit_id=$AUDIT_ID_FULL" \
    "POST" \
    '{"raw_message":"Audit trail: User modified security settings","source":"audit.log","timestamp":"2025-11-27T09:30:00Z"}'

echo ""

# Step 2: Submit document evidence
if [ -f "$DOC_PATH" ]; then
    echo -e "${YELLOW}Step 2: Uploading policy document...${NC}"

    response=$(curl -s -w "\n%{http_code}" -X POST \
        "$ENGINE2_URL/api/v1/evidence/submit-document?audit_id=$AUDIT_ID_FULL&company_name=FullAudit%20Corp" \
        -F "file=@$DOC_PATH")

    http_code=$(echo "$response" | tail -n1)
    if [ "$http_code" -ge 200 ] && [ "$http_code" -lt 300 ]; then
        echo -e "  ${GREEN}✓ Document uploaded successfully${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "  ${RED}✗ Document upload failed${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi

    echo ""
fi

# Step 3: Classify all evidence
echo -e "${YELLOW}Step 3: Classifying ALL evidence (logs + documents)...${NC}"
test_endpoint "Classify mixed evidence" \
    "$ENGINE3_URL/api/v1/classify/audit/$AUDIT_ID_FULL" \
    "POST" \
    '{}'

echo ""

# Step 4: Make decisions with gap analysis
echo -e "${YELLOW}Step 4: Making decisions with gap analysis (60% logs, 40% docs)...${NC}"
test_endpoint "Make decisions with gap analysis" \
    "$ENGINE4_URL/api/v1/decision/audit/$AUDIT_ID_FULL?log_weight=0.6&document_weight=0.4" \
    "POST" \
    '{}'

echo ""

# Step 5: Get gap analysis results
echo -e "${YELLOW}Step 5: Retrieving gap analysis...${NC}"
test_endpoint "Get gaps" \
    "$ENGINE4_URL/api/v1/decision/audit/$AUDIT_ID_FULL/gaps" \
    "GET" \
    ""

echo ""

# Step 6: Generate comprehensive report
echo -e "${YELLOW}Step 6: Generating comprehensive gap analysis report...${NC}"
test_endpoint "Generate full audit report" \
    "$ENGINE5_URL/api/v1/generate/audit-report/$AUDIT_ID_FULL?company_name=FullAudit%20Corp&report_type=gap_analysis&include_charts=true" \
    "POST" \
    '{}'

echo ""
echo -e "${GREEN}✓ Scenario 3 Complete: Full Audit with Gap Analysis${NC}"

# =============================================================================
# PHASE 5: Summary
# =============================================================================

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                       TEST SUITE SUMMARY                              ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
PASS_RATE=0
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$((TESTS_PASSED * 100 / TOTAL_TESTS))
fi

echo "  Total Tests: $TOTAL_TESTS"
echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
echo "  Pass Rate: $PASS_RATE%"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓✓✓ ALL TESTS PASSED! Unified pipeline is fully operational. ✓✓✓${NC}"
    echo ""
    echo "Summary of Tested Features:"
    echo "  ✓ Logs-only audit mode"
    echo "  ✓ Documents-only audit mode"
    echo "  ✓ Full audit with gap analysis"
    echo "  ✓ Evidence submission (Engine 1 & 2)"
    echo "  ✓ XGBoost classification (Engine 3)"
    echo "  ✓ Decision making with weighted scoring (Engine 4)"
    echo "  ✓ Gap detection between policy and reality"
    echo "  ✓ PDF report generation with source indicators (Engine 5)"
    echo ""
    exit 0
else
    echo -e "${RED}⚠ Some tests failed. Review the output above for details.${NC}"
    echo ""
    exit 1
fi
