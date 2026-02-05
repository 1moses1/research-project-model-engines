# UI Integration Plan: Rwanda NCSA Compliance Auditor

## Overview

This document outlines the plan to integrate the end-to-end audit pipeline with the Web UI (Engine 6) to provide a seamless user journey for compliance auditing.

## Current Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE (Engine 6)                        │
│                     React Dashboard + WebSocket                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY / ROUTER                            │
└─────────────────────────────────────────────────────────────────────────┘
         │              │              │              │              │
         ▼              ▼              ▼              ▼              ▼
    ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
    │ENGINE 1 │   │ENGINE 2 │   │ENGINE 3 │   │ENGINE 4 │   │ENGINE 5 │
    │  Log    │   │  Doc    │   │MCP+LLM  │   │Decision │   │ Report  │
    │Collector│   │Processor│   │Analyzer │   │ Engine  │   │Generator│
    └─────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
```

## User Journey Map

### 1. Audit Dashboard Landing Page

**Route:** `/dashboard`

**Features:**
- Overview of recent audits
- Quick stats: compliance rate, risk level, pending reviews
- Start new audit button
- View historical reports

**API Endpoints:**
```
GET /api/audits/recent
GET /api/stats/overview
```

### 2. New Audit Wizard

**Route:** `/audit/new`

**Step 1: Configuration**
- Select audit type (Log Analysis, Document Analysis, Full Audit)
- Choose time range for log analysis
- Select control families to audit
- Upload policy documents

**Step 2: Log Source Selection**
- Connect to log sources (syslog, file upload, API)
- Preview sample logs
- Configure filters

**Step 3: Document Upload**
- Drag-and-drop policy documents
- Supported formats: PDF, DOCX, TXT
- Preview uploaded documents

**Step 4: Review & Start**
- Summary of audit configuration
- Estimated processing time
- Start audit button

**API Endpoints:**
```
POST /api/audit/configure
POST /api/audit/upload-documents
POST /api/audit/start
```

### 3. Real-Time Audit Progress

**Route:** `/audit/{audit_id}/progress`

**Features:**
- Real-time progress bar
- WebSocket updates for each log processed
- Live compliance chart updating
- Current control being analyzed
- Partial results display

**WebSocket Events:**
```javascript
// Subscribe to audit progress
ws.send({ type: 'subscribe', audit_id: 'AUDIT-xxx' })

// Receive updates
ws.onmessage = (event) => {
  const { type, data } = JSON.parse(event.data)
  switch(type) {
    case 'log_analyzed':
      // Update progress bar, add to results list
      break
    case 'document_processed':
      // Show document analysis results
      break
    case 'compliance_update':
      // Update compliance chart
      break
    case 'audit_complete':
      // Navigate to results page
      break
  }
}
```

### 4. Audit Results Dashboard

**Route:** `/audit/{audit_id}/results`

**Components:**

#### 4.1 Executive Summary Card
```
┌────────────────────────────────────────────────────┐
│  AUDIT-20260203-230216                             │
│  ─────────────────────────                         │
│  Organization: Alvin Tech                          │
│  Date: February 3, 2026                            │
│  Framework: Rwanda NCSA                            │
│                                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ 40%      │  │ HIGH     │  │ 5        │        │
│  │ Compliance│  │ Risk     │  │ Logs     │        │
│  └──────────┘  └──────────┘  └──────────┘        │
└────────────────────────────────────────────────────┘
```

#### 4.2 Control Family Breakdown
- Pie chart by family
- Table with drill-down capability
- Filter by status (compliant/non-compliant)

#### 4.3 Detailed Findings Table
```
| # | Log Message | Status | Control | Confidence | Actions |
|---|-------------|--------|---------|------------|---------|
| 1 | session opened... | ✓ Compliant | AU-68 | 90% | View |
| 2 | Invalid user... | ✗ Non-Compliant | AC-38 | 95% | View |
```

#### 4.4 Document Analysis Panel
- List of analyzed documents
- Control mappings
- Findings summary

### 5. Report Generation & Download

**Route:** `/audit/{audit_id}/report`

**Features:**
- Preview report in browser
- Download as PDF
- Download as JSON
- Email report option
- Schedule recurring reports

**API Endpoints:**
```
GET /api/audit/{audit_id}/report/preview
GET /api/audit/{audit_id}/report/download?format=pdf
POST /api/audit/{audit_id}/report/email
```

## Implementation Plan

### Phase 1: Backend API Enhancements (Week 1-2)

1. **Add Audit Session Management**
   ```python
   # Engine 6 Backend: api.py

   @app.post("/api/audit/start")
   async def start_audit(config: AuditConfig):
       audit_id = generate_audit_id()
       # Create audit session in Redis/PostgreSQL
       # Start background task for processing
       return {"audit_id": audit_id, "status": "started"}

   @app.get("/api/audit/{audit_id}/status")
   async def get_audit_status(audit_id: str):
       # Return current progress
       pass
   ```

2. **Add WebSocket Support for Progress**
   ```python
   @app.websocket("/ws/audit/{audit_id}")
   async def audit_websocket(websocket: WebSocket, audit_id: str):
       await websocket.accept()
       # Subscribe to Redis pub/sub for audit updates
       # Stream progress to client
   ```

3. **Add Report Download Endpoint**
   ```python
   @app.get("/api/audit/{audit_id}/report/download")
   async def download_report(audit_id: str, format: str = "pdf"):
       # Call Engine 5 or generate locally
       # Return file response
   ```

### Phase 2: Frontend Components (Week 2-3)

1. **Audit Wizard Component**
   - Multi-step form with validation
   - File upload with drag-and-drop
   - Progress stepper UI

2. **Real-Time Progress Component**
   - WebSocket connection management
   - Animated progress indicators
   - Live-updating charts (recharts/chart.js)

3. **Results Dashboard Component**
   - Executive summary cards
   - Interactive data tables (ag-grid/tanstack-table)
   - Control family visualization

4. **Report Preview Component**
   - PDF viewer (react-pdf)
   - Download buttons
   - Share functionality

### Phase 3: Integration Testing (Week 3-4)

1. **End-to-End Tests**
   - Playwright/Cypress tests for full user journey
   - API integration tests
   - WebSocket connection tests

2. **Performance Testing**
   - Load testing with multiple concurrent audits
   - WebSocket scalability testing
   - Report generation performance

## API Contract

### Start Audit
```json
POST /api/audit/start
{
  "audit_type": "full",
  "log_sources": [
    {"type": "file", "path": "/logs/auth.log"},
    {"type": "syslog", "host": "localhost", "port": 514}
  ],
  "documents": ["doc_id_1", "doc_id_2"],
  "control_families": ["Access Control", "Audit and Accountability"],
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-12-31T23:59:59Z"
  }
}

Response:
{
  "audit_id": "AUDIT-20260203-230216",
  "status": "started",
  "estimated_duration_seconds": 120
}
```

### Get Audit Results
```json
GET /api/audit/{audit_id}/results

Response:
{
  "audit_id": "AUDIT-20260203-230216",
  "status": "completed",
  "summary": {
    "compliance_rate": 40.0,
    "risk_level": "HIGH",
    "total_logs": 5,
    "compliant": 2,
    "non_compliant": 3
  },
  "log_analysis": [...],
  "document_analysis": [...],
  "control_families": {...},
  "timestamp": "2026-02-03T23:02:19Z"
}
```

### Download Report
```
GET /api/audit/{audit_id}/report/download?format=pdf

Response: Binary PDF file with Content-Disposition header
```

## UI Wireframes

### Main Dashboard
```
┌────────────────────────────────────────────────────────────────────┐
│  [Logo] Rwanda NCSA Compliance Auditor    [User] [Settings] [Help] │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌─────────────────────┐  ┌─────────────────────┐                 │
│  │  [+ New Audit]      │  │  Overall Compliance  │                 │
│  │                     │  │  ████████░░ 75%      │                 │
│  └─────────────────────┘  └─────────────────────┘                 │
│                                                                    │
│  Recent Audits                                                     │
│  ─────────────                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │ AUDIT-20260203-230216 | Alvin Tech | HIGH | 40% | [View]   │   │
│  │ AUDIT-20260201-145030 | CMU Africa | LOW  | 95% | [View]   │   │
│  │ AUDIT-20260128-091500 | Bank XYZ   | MED  | 72% | [View]   │   │
│  └────────────────────────────────────────────────────────────┘   │
│                                                                    │
│  Quick Actions                                                     │
│  ─────────────                                                     │
│  [Upload Logs] [Upload Policies] [Generate Report] [Schedule]     │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### Audit Results Page
```
┌────────────────────────────────────────────────────────────────────┐
│  ← Back to Dashboard    AUDIT-20260203-230216    [Download Report] │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Executive Summary                                                 │
│  ─────────────────                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │   40%    │  │   HIGH   │  │    5     │  │    4     │          │
│  │Compliance│  │   Risk   │  │   Logs   │  │   Docs   │          │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
│                                                                    │
│  Control Families                    Findings                      │
│  ────────────────                    ────────                      │
│  [Pie Chart]                         | Status | Control | Log     │
│    ■ Access Control: 2               |   ✓    | AU-68   | sessio..│
│    ■ Audit: 2                        |   ✗    | AC-38   | Invali..│
│    ■ Identity: 1                     |   ✗    | IA-100  | Did no..│
│                                      |   ✓    | AU-69   | sessio..│
│                                      |   ✗    | SC-155  | fatal:..│
│                                                                    │
│  Documents Analyzed                                                │
│  ──────────────────                                                │
│  ✓ Alvin Tech Internal Audit Report.pdf                           │
│  ✓ Alvin Tech Security Patching Report.pdf                        │
│  ✓ Alvin Tech Post-Patching Security Scan Report.pdf              │
│  ✓ Alvin Tech Updated Security Policy.pdf                         │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework:** React 18+ with TypeScript
- **State Management:** Redux Toolkit / Zustand
- **UI Components:** Shadcn/UI + Tailwind CSS
- **Charts:** Recharts / Chart.js
- **PDF Viewer:** react-pdf
- **WebSocket:** native WebSocket API
- **Testing:** Vitest + React Testing Library + Playwright

### Backend (Engine 6)
- **Framework:** FastAPI
- **WebSocket:** FastAPI WebSocket support
- **Cache:** Redis for session management
- **Database:** PostgreSQL for audit history
- **PDF Generation:** ReportLab (already integrated)

## Timeline

| Week | Milestone |
|------|-----------|
| 1 | Backend API enhancements (audit session management) |
| 2 | WebSocket integration and report endpoints |
| 3 | Frontend components (wizard, progress, results) |
| 4 | Integration testing and polish |
| 5 | User acceptance testing and deployment |

## Success Metrics

1. **User can complete full audit in < 5 clicks**
2. **Real-time progress updates every 500ms**
3. **PDF report generation in < 5 seconds**
4. **UI responsive on all device sizes**
5. **95%+ Lighthouse accessibility score**

## Conclusion

This UI integration plan provides a comprehensive roadmap for creating a seamless user experience for the Rwanda NCSA Compliance Auditor. The implementation leverages the existing engine architecture while adding the necessary frontend components and API enhancements to support real-time audit monitoring, interactive results exploration, and one-click report generation.

---

*Document Version: 1.0*
*Last Updated: February 3, 2026*
*Author: Moise Iradukunda Ingabire, Carnegie Mellon University Africa*
