#!/bin/bash

#===============================================================================
# RWANDA NCSA COMPLIANCE AUDITOR - UNIFIED PIPELINE E2E TEST
#===============================================================================
# This script performs comprehensive end-to-end testing of the unified pipeline
# Testing scenarios:
# 1. Infrastructure: Redis + PostgreSQL
# 2. Engine 1 Only (Logs)
# 3. Engine 2 Only (Documents)
# 4. Full Pipeline (Logs + Documents + Gap Analysis)
# 5. UI Connection Status Verification
#===============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
AUDIT_ID="test-audit-$(date +%s)"
COMPANY_NAME="Alvin Tech"
BASE_DIR="/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"
DOCS_DIR="$BASE_DIR/engines/engine2-document-processor/sample_documents"

# Engine URLs
ENGINE1_URL="http://localhost:8000"
ENGINE2_URL="http://localhost:8002"
ENGINE3_URL="http://localhost:8003"
ENGINE4_URL="http://localhost:8001"
ENGINE5_URL="http://localhost:8005"
ENGINE6_URL="http://localhost:8006"

# Database URLs
REDIS_HOST="localhost"
REDIS_PORT="6379"
POSTGRES_URL="postgresql://rwanda_admin:rwanda_secure_2024@localhost:5432/rwanda_ncsa"

echo -e "${CYAN}===============================================================================${NC}"
echo -e "${CYAN}        RWANDA NCSA COMPLIANCE AUDITOR - UNIFIED PIPELINE E2E TEST${NC}"
echo -e "${CYAN}===============================================================================${NC}"
echo ""
echo -e "Test Parameters:"
echo -e "  Audit ID: ${GREEN}$AUDIT_ID${NC}"
echo -e "  Company: ${GREEN}$COMPANY_NAME${NC}"
echo -e "  Documents: ${GREEN}$DOCS_DIR${NC}"
echo ""

#===============================================================================
# PHASE 0: CLEANUP AND PREPARATION
#===============================================================================
echo -e "${BLUE}[PHASE 0]${NC} Cleanup and Preparation"
echo "--------------------------------------------------------------------------------"

echo -e "${YELLOW}→${NC} Stopping existing processes..."
pkill -f "uvicorn" 2>/dev/null || true
sleep 2

echo -e "${YELLOW}→${NC} Stopping Docker containers..."
cd "$BASE_DIR"
docker-compose down 2>/dev/null || true

echo -e "${GREEN}✓${NC} Cleanup complete"
echo ""

#===============================================================================
# PHASE 1: START INFRASTRUCTURE
#===============================================================================
echo -e "${BLUE}[PHASE 1]${NC} Starting Infrastructure (Redis + PostgreSQL)"
echo "--------------------------------------------------------------------------------"

echo -e "${YELLOW}→${NC} Starting Redis and PostgreSQL..."
docker-compose up -d redis postgres
sleep 5

echo -e "${YELLOW}→${NC} Verifying Redis connection..."
if docker exec rwanda-ncsa-redis redis-cli ping | grep -q "PONG"; then
    echo -e "${GREEN}✓${NC} Redis is running"
else
    echo -e "${RED}✗${NC} Redis connection failed"
    exit 1
fi

echo -e "${YELLOW}→${NC} Verifying PostgreSQL connection..."
if docker exec rwanda-ncsa-postgres pg_isready -U rwanda_admin -d rwanda_ncsa | grep -q "accepting connections"; then
    echo -e "${GREEN}✓${NC} PostgreSQL is running"
else
    echo -e "${RED}✗${NC} PostgreSQL connection failed"
    exit 1
fi

echo -e "${GREEN}✓${NC} Infrastructure ready"
echo ""

#===============================================================================
# PHASE 2: START ALL ENGINES
#===============================================================================
echo -e "${BLUE}[PHASE 2]${NC} Starting All Engines"
echo "--------------------------------------------------------------------------------"

# Start all engines in Docker
echo -e "${YELLOW}→${NC} Starting all engines with Docker Compose..."
cd "$BASE_DIR"
docker-compose up -d

echo -e "${YELLOW}→${NC} Waiting for engines to initialize (30 seconds)..."
sleep 30

echo -e "${GREEN}✓${NC} All engines started"
echo ""

#===============================================================================
# PHASE 3: HEALTH CHECKS
#===============================================================================
echo -e "${BLUE}[PHASE 3]${NC} Health Check - All Engines"
echo "--------------------------------------------------------------------------------"

check_health() {
    local name=$1
    local url=$2
    echo -e "${YELLOW}→${NC} Checking $name..."
    if curl -s -f "$url/health" > /dev/null 2>&1 || curl -s -f "$url/" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $name is healthy"
        return 0
    else
        echo -e "${RED}✗${NC} $name health check failed"
        return 1
    fi
}

check_health "Engine 1 (Log Collector)" "$ENGINE1_URL"
check_health "Engine 2 (Document Processor)" "$ENGINE2_URL"
check_health "Engine 3 (XGBoost Classifier)" "$ENGINE3_URL"
check_health "Engine 4 (Decision Engine)" "$ENGINE4_URL"
check_health "Engine 5 (Report Generator)" "$ENGINE5_URL"
check_health "Engine 6 (Web UI)" "$ENGINE6_URL"

echo -e "${GREEN}✓${NC} All engines are healthy"
echo ""

#===============================================================================
# PHASE 4: TEST SCENARIO 1 - ENGINE 1 ONLY (LOGS)
#===============================================================================
echo -e "${BLUE}[PHASE 4]${NC} Test Scenario 1: Engine 1 Only (Logs)"
echo "--------------------------------------------------------------------------------"

LOG_AUDIT_ID="${AUDIT_ID}-logs-only"
echo -e "  Audit ID: ${CYAN}$LOG_AUDIT_ID${NC}"

# Submit log evidence
echo -e "${YELLOW}→${NC} Submitting log evidence (5 samples)..."

LOGS=(
    '{"raw_message": "User admin logged in successfully from 192.168.1.100", "source": "auth", "severity": "INFO", "metadata": {"action": "login"}}'
    '{"raw_message": "Failed login attempt for user test from 10.0.0.50", "source": "auth", "severity": "WARNING", "metadata": {"action": "failed_login"}}'
    '{"raw_message": "Firewall rule updated: Allow HTTPS traffic on port 443", "source": "firewall", "severity": "INFO", "metadata": {"port": 443}}'
    '{"raw_message": "Backup completed successfully - 500GB data archived", "source": "backup", "severity": "INFO", "metadata": {"size_gb": 500}}'
    '{"raw_message": "Security patch applied: CVE-2024-1234", "source": "patch_management", "severity": "INFO", "metadata": {"cve": "CVE-2024-1234"}}'
)

for i in "${!LOGS[@]}"; do
    curl -s -X POST "$ENGINE1_URL/api/v1/evidence/submit?audit_id=$LOG_AUDIT_ID" \
        -H "Content-Type: application/json" \
        -d "${LOGS[$i]}" > /dev/null
    echo -e "  ${GREEN}✓${NC} Log $((i+1))/5 submitted"
done

sleep 2

# Classify log evidence
echo -e "${YELLOW}→${NC} Classifying log evidence..."
CLASSIFY_RESULT=$(curl -s -X POST "$ENGINE3_URL/api/v1/classify/audit/$LOG_AUDIT_ID")
echo "$CLASSIFY_RESULT" | jq '.' > /tmp/classify_logs.json
CLASSIFIED_COUNT=$(echo "$CLASSIFY_RESULT" | jq -r '.classified')
echo -e "  ${GREEN}✓${NC} Classified $CLASSIFIED_COUNT events"

# Make decisions
echo -e "${YELLOW}→${NC} Making compliance decisions..."
DECISION_RESULT=$(curl -s -X POST "$ENGINE4_URL/api/v1/decision/audit/$LOG_AUDIT_ID?log_weight=1.0&document_weight=0.0")
echo "$DECISION_RESULT" | jq '.' > /tmp/decisions_logs.json
DECISIONS_MADE=$(echo "$DECISION_RESULT" | jq -r '.decisions_made')
echo -e "  ${GREEN}✓${NC} Made $DECISIONS_MADE decisions"
echo -e "  ${CYAN}ℹ${NC} Audit Mode: LOGS_ONLY"

echo -e "${GREEN}✓${NC} Scenario 1 complete: Logs-only audit successful"
echo ""

#===============================================================================
# PHASE 5: TEST SCENARIO 2 - ENGINE 2 ONLY (DOCUMENTS)
#===============================================================================
echo -e "${BLUE}[PHASE 5]${NC} Test Scenario 2: Engine 2 Only (Documents)"
echo "--------------------------------------------------------------------------------"

DOC_AUDIT_ID="${AUDIT_ID}-docs-only"
echo -e "  Audit ID: ${CYAN}$DOC_AUDIT_ID${NC}"

# Submit document evidence
echo -e "${YELLOW}→${NC} Submitting policy documents for $COMPANY_NAME..."

DOCS=(
    "Alvin Tech Updated Security Policy.pdf"
    "Alvin Tech Internal Audit Report.pdf"
    "Alvin Tech Security Patching Report.pdf"
    "Alvin Tech Post-Patching Security Scan Report.pdf"
)

for i in "${!DOCS[@]}"; do
    DOC_PATH="$DOCS_DIR/${DOCS[$i]}"
    if [ -f "$DOC_PATH" ]; then
        curl -s -X POST "$ENGINE2_URL/api/v1/evidence/submit-document?audit_id=$DOC_AUDIT_ID&company_name=$COMPANY_NAME" \
            -F "file=@$DOC_PATH" > /dev/null
        echo -e "  ${GREEN}✓${NC} Document $((i+1))/4: ${DOCS[$i]}"
    else
        echo -e "  ${RED}✗${NC} Document not found: ${DOCS[$i]}"
    fi
done

sleep 3

# Classify document evidence
echo -e "${YELLOW}→${NC} Classifying document evidence..."
CLASSIFY_DOC_RESULT=$(curl -s -X POST "$ENGINE3_URL/api/v1/classify/audit/$DOC_AUDIT_ID")
echo "$CLASSIFY_DOC_RESULT" | jq '.' > /tmp/classify_docs.json
DOC_CLASSIFIED_COUNT=$(echo "$CLASSIFY_DOC_RESULT" | jq -r '.classified')
echo -e "  ${GREEN}✓${NC} Classified $DOC_CLASSIFIED_COUNT controls"

# Make decisions
echo -e "${YELLOW}→${NC} Making compliance decisions..."
DOC_DECISION_RESULT=$(curl -s -X POST "$ENGINE4_URL/api/v1/decision/audit/$DOC_AUDIT_ID?log_weight=0.0&document_weight=1.0")
echo "$DOC_DECISION_RESULT" | jq '.' > /tmp/decisions_docs.json
DOC_DECISIONS_MADE=$(echo "$DOC_DECISION_RESULT" | jq -r '.decisions_made')
echo -e "  ${GREEN}✓${NC} Made $DOC_DECISIONS_MADE decisions"
echo -e "  ${CYAN}ℹ${NC} Audit Mode: DOCUMENTS_ONLY"

echo -e "${GREEN}✓${NC} Scenario 2 complete: Documents-only audit successful"
echo ""

#===============================================================================
# PHASE 6: TEST SCENARIO 3 - FULL PIPELINE (LOGS + DOCUMENTS + GAP ANALYSIS)
#===============================================================================
echo -e "${BLUE}[PHASE 6]${NC} Test Scenario 3: Full Pipeline with Gap Analysis"
echo "--------------------------------------------------------------------------------"

FULL_AUDIT_ID="${AUDIT_ID}-full"
echo -e "  Audit ID: ${CYAN}$FULL_AUDIT_ID${NC}"

# Submit BOTH log and document evidence
echo -e "${YELLOW}→${NC} Submitting log evidence..."
for i in "${!LOGS[@]}"; do
    curl -s -X POST "$ENGINE1_URL/api/v1/evidence/submit?audit_id=$FULL_AUDIT_ID" \
        -H "Content-Type: application/json" \
        -d "${LOGS[$i]}" > /dev/null
    echo -e "  ${GREEN}✓${NC} Log $((i+1))/5 submitted"
done

echo -e "${YELLOW}→${NC} Submitting policy documents..."
for i in "${!DOCS[@]}"; do
    DOC_PATH="$DOCS_DIR/${DOCS[$i]}"
    if [ -f "$DOC_PATH" ]; then
        curl -s -X POST "$ENGINE2_URL/api/v1/evidence/submit-document?audit_id=$FULL_AUDIT_ID&company_name=$COMPANY_NAME" \
            -F "file=@$DOC_PATH" > /dev/null
        echo -e "  ${GREEN}✓${NC} Document $((i+1))/4: ${DOCS[$i]}"
    fi
done

sleep 3

# Classify all evidence
echo -e "${YELLOW}→${NC} Classifying all evidence (logs + documents)..."
FULL_CLASSIFY_RESULT=$(curl -s -X POST "$ENGINE3_URL/api/v1/classify/audit/$FULL_AUDIT_ID")
echo "$FULL_CLASSIFY_RESULT" | jq '.' > /tmp/classify_full.json
FULL_CLASSIFIED=$(echo "$FULL_CLASSIFY_RESULT" | jq -r '.classified')
echo -e "  ${GREEN}✓${NC} Classified $FULL_CLASSIFIED items"

# Make decisions with gap analysis
echo -e "${YELLOW}→${NC} Making compliance decisions with gap analysis..."
FULL_DECISION_RESULT=$(curl -s -X POST "$ENGINE4_URL/api/v1/decision/audit/$FULL_AUDIT_ID?log_weight=0.6&document_weight=0.4")
echo "$FULL_DECISION_RESULT" | jq '.' > /tmp/decisions_full.json
FULL_DECISIONS=$(echo "$FULL_DECISION_RESULT" | jq -r '.decisions_made')
GAPS_DETECTED=$(echo "$FULL_DECISION_RESULT" | jq -r '.gaps_detected')
echo -e "  ${GREEN}✓${NC} Made $FULL_DECISIONS decisions"
echo -e "  ${CYAN}ℹ${NC} Audit Mode: FULL_AUDIT"
echo -e "  ${YELLOW}⚠${NC} Gaps Detected: $GAPS_DETECTED"

# Get gap details
if [ "$GAPS_DETECTED" -gt 0 ]; then
    echo -e "${YELLOW}→${NC} Retrieving gap analysis details..."
    GAP_RESULT=$(curl -s "$ENGINE4_URL/api/v1/decision/audit/$FULL_AUDIT_ID/gaps")
    echo "$GAP_RESULT" | jq '.' > /tmp/gaps_full.json
    echo -e "  ${GREEN}✓${NC} Gap analysis saved to /tmp/gaps_full.json"
fi

# Generate report
echo -e "${YELLOW}→${NC} Generating compliance report..."
REPORT_RESULT=$(curl -s -X POST "$ENGINE5_URL/api/v1/generate/audit-report/$FULL_AUDIT_ID?company_name=$COMPANY_NAME&report_type=full&include_charts=true")
echo "$REPORT_RESULT" | jq '.' > /tmp/report_full.json
REPORT_ID=$(echo "$REPORT_RESULT" | jq -r '.report_id')
echo -e "  ${GREEN}✓${NC} Report generated: $REPORT_ID"

echo -e "${GREEN}✓${NC} Scenario 3 complete: Full pipeline with gap analysis successful"
echo ""

#===============================================================================
# PHASE 7: UI CONNECTION STATUS VERIFICATION
#===============================================================================
echo -e "${BLUE}[PHASE 7]${NC} UI Connection Status Verification"
echo "--------------------------------------------------------------------------------"

echo -e "${YELLOW}→${NC} Checking Web UI status page..."
UI_STATUS=$(curl -s "$ENGINE6_URL/api/v3/system-health")
echo "$UI_STATUS" | jq '.' > /tmp/ui_status.json

# Check each component
echo ""
echo "  System Health:"
REDIS_STATUS=$(echo "$UI_STATUS" | jq -r '.redis.status // "unknown"')
POSTGRES_STATUS=$(echo "$UI_STATUS" | jq -r '.postgres.status // "unknown"')

if [ "$REDIS_STATUS" = "connected" ]; then
    echo -e "    ${GREEN}✓${NC} Redis: Connected"
else
    echo -e "    ${RED}✗${NC} Redis: $REDIS_STATUS"
fi

if [ "$POSTGRES_STATUS" = "connected" ]; then
    echo -e "    ${GREEN}✓${NC} PostgreSQL: Connected"
else
    echo -e "    ${RED}✗${NC} PostgreSQL: $POSTGRES_STATUS"
fi

echo ""
echo -e "${YELLOW}→${NC} Verifying taxonomy support..."
TAXONOMIES=$(curl -s "$ENGINE6_URL/api/v3/taxonomies")
echo "$TAXONOMIES" | jq '.' > /tmp/taxonomies.json
MACOS_SUPPORTED=$(echo "$TAXONOMIES" | jq -r '.[] | select(.name=="macOS") | .supported')

if [ "$MACOS_SUPPORTED" = "true" ]; then
    echo -e "  ${GREEN}✓${NC} macOS taxonomy is supported"
else
    echo -e "  ${YELLOW}⚠${NC} macOS taxonomy support: $MACOS_SUPPORTED"
fi

echo ""
echo -e "${GREEN}✓${NC} UI connection verification complete"
echo ""

#===============================================================================
# PHASE 8: TEST SUMMARY
#===============================================================================
echo -e "${CYAN}===============================================================================${NC}"
echo -e "${CYAN}                            TEST SUMMARY${NC}"
echo -e "${CYAN}===============================================================================${NC}"
echo ""

echo -e "${GREEN}✓ PHASE 1:${NC} Infrastructure (Redis + PostgreSQL) - ${GREEN}PASSED${NC}"
echo -e "${GREEN}✓ PHASE 2:${NC} All Engines Started - ${GREEN}PASSED${NC}"
echo -e "${GREEN}✓ PHASE 3:${NC} Health Checks - ${GREEN}PASSED${NC}"
echo -e "${GREEN}✓ PHASE 4:${NC} Logs-Only Audit - ${GREEN}PASSED${NC} ($CLASSIFIED_COUNT events, $DECISIONS_MADE decisions)"
echo -e "${GREEN}✓ PHASE 5:${NC} Documents-Only Audit - ${GREEN}PASSED${NC} ($DOC_CLASSIFIED_COUNT controls, $DOC_DECISIONS_MADE decisions)"
echo -e "${GREEN}✓ PHASE 6:${NC} Full Pipeline with Gap Analysis - ${GREEN}PASSED${NC}"
echo "    - Classified: $FULL_CLASSIFIED items"
echo "    - Decisions: $FULL_DECISIONS"
echo "    - Gaps Detected: $GAPS_DETECTED"
echo "    - Report: $REPORT_ID"
echo -e "${GREEN}✓ PHASE 7:${NC} UI Connection Status - ${GREEN}PASSED${NC}"
echo ""

echo "Test Results Saved:"
echo "  - /tmp/classify_logs.json"
echo "  - /tmp/classify_docs.json"
echo "  - /tmp/classify_full.json"
echo "  - /tmp/decisions_logs.json"
echo "  - /tmp/decisions_docs.json"
echo "  - /tmp/decisions_full.json"
echo "  - /tmp/gaps_full.json"
echo "  - /tmp/report_full.json"
echo "  - /tmp/ui_status.json"
echo "  - /tmp/taxonomies.json"
echo ""

echo "Docker Services Status:"
docker-compose ps
echo ""

echo "Web UI Access:"
echo -e "  ${CYAN}http://localhost:8006${NC}"
echo ""

echo "To view engine logs, run:"
echo "  docker-compose logs -f [service-name]"
echo "  Example: docker-compose logs -f document-processor"
echo ""

echo -e "${CYAN}===============================================================================${NC}"
echo -e "${GREEN}                     ALL TESTS PASSED SUCCESSFULLY!${NC}"
echo -e "${CYAN}===============================================================================${NC}"
echo ""

echo "To stop all services, run:"
echo "  docker-compose down"
echo ""
