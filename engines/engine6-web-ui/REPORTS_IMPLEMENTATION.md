# Reports Management Implementation

## Overview
Successfully implemented comprehensive reports management system that integrates with the PostgreSQL database to store, retrieve, and manage compliance audit reports.

## Components Implemented

### 1. Backend API Endpoints (`backend/api.py`)

#### GET `/api/v3/reports`
- Fetches all generated reports from the database
- Returns report metadata including audit ID, framework, score, file size, timestamps
- Joins with audits table to get compliance scores

#### GET `/api/v3/reports/{report_id}/download`
- Downloads PDF report as attachment
- Validates report exists in database and file exists on disk
- Returns FileResponse with proper headers for download

#### GET `/api/v3/reports/{report_id}/view`
- Views PDF report inline in browser
- Similar to download but uses `inline` Content-Disposition
- Allows viewing without downloading

#### DELETE `/api/v3/reports/{report_id}`
- Deletes report from database and disk
- Removes file from filesystem after database deletion
- Returns success confirmation

### 2. Report Saving Integration

Modified `run_audit_workflow()` function to automatically save reports when audit completes:

```python
# Save PDF report to reports table if it was generated
pdf_path = results.get("files", {}).get("pdf_report")
if pdf_path and Path(pdf_path).exists():
    pdf_file = Path(pdf_path)
    file_size = pdf_file.stat().st_size
    filename = f"compliance_report_{audit_id}.pdf"

    await conn.execute("""
        INSERT INTO reports (audit_id, organization_id, report_type, format,
            filename, file_path, file_size)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
    """, audit_uuid, org_id, 'compliance', 'pdf',
        filename, str(pdf_file), file_size)
```

**Location**: `backend/api.py:665-679`

### 3. Frontend Reports Page (`backend/static/index.html`)

#### Reports Table Structure
- Report ID (with PDF icon)
- Audit ID (linked reference)
- Type (badge: compliance/executive/detailed)
- Framework (Rwanda-NCSA, NIST, etc.)
- Score (color-coded: green ≥70%, red <70%)
- Generated timestamp
- File size (formatted: KB/MB)
- Actions (Download, View, Delete)

#### JavaScript Functions

**`loadReports()`** - Lines 1737-1833
- Fetches reports from API
- Renders table with formatted data
- Shows empty state when no reports exist
- Handles errors with user-friendly messages

**`formatFileSize(bytes)`** - Lines 1835-1841
- Converts bytes to human-readable format (KB, MB, GB)
- Used for displaying file sizes in table

**`downloadReport(reportId)`** - Lines 1843-1845
- Opens download URL in new window
- Triggers browser download dialog

**`viewReport(reportId)`** - Lines 1847-1849
- Opens PDF viewer in new window
- Displays report inline in browser

**`deleteReport(reportId)`** - Lines 1851-1868
- Confirms deletion with user
- Calls DELETE endpoint
- Refreshes table after successful deletion
- Shows success message

### 4. Auto-load on Navigation

Updated `showPage()` function to automatically load reports when navigating to Reports page:

```javascript
if (pageId === 'reports') {
    loadReports();
}
```

**Location**: `backend/static/index.html:1359`

## Database Schema

Uses existing `reports` table from `01_schema.sql`:

```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id UUID REFERENCES audits(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id),
    report_type VARCHAR(50) DEFAULT 'compliance',
    format VARCHAR(20) DEFAULT 'pdf',
    filename VARCHAR(255),
    file_path TEXT,
    file_size BIGINT,
    generated_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Workflow Integration

1. **Audit Execution**: User starts audit via "Start Audit" page
2. **Pipeline Processing**: Engines 1-5 process the audit
3. **Report Generation**: Engine 5 generates PDF report
4. **Automatic Saving**: Backend saves report metadata to database
5. **User Access**: Reports page displays all available reports
6. **Actions**: Users can download, view, or delete reports

## Features

✅ Complete CRUD operations for reports
✅ Automatic report saving on audit completion
✅ Database and filesystem integration
✅ Professional table UI with sorting and formatting
✅ Color-coded compliance scores
✅ File size formatting
✅ Empty state handling
✅ Error handling and user feedback
✅ Delete confirmation dialogs
✅ PDF download and inline viewing

## API Testing

```bash
# List all reports
curl http://localhost:8006/api/v3/reports

# Download a report
curl http://localhost:8006/api/v3/reports/{report_id}/download -o report.pdf

# View a report (in browser)
open http://localhost:8006/api/v3/reports/{report_id}/view

# Delete a report
curl -X DELETE http://localhost:8006/api/v3/reports/{report_id}
```

## Files Modified

1. `/engines/engine6-web-ui/backend/api.py`
   - Added 4 new API endpoints (lines 1395-1562)
   - Modified audit workflow to save reports (lines 665-679)

2. `/engines/engine6-web-ui/backend/static/index.html`
   - Added Reports page HTML (lines 827-867)
   - Added JavaScript functions (lines 1737-1868)
   - Updated showPage() navigation (line 1359)

## Next Steps (Optional)

- [ ] Add report filtering by framework/date
- [ ] Add bulk delete functionality
- [ ] Add report regeneration capability
- [ ] Add custom report templates
- [ ] Add report sharing via email/link
- [ ] Add report comparison feature
- [ ] Add report search functionality

## Status

✅ **COMPLETE** - Reports management fully functional and integrated with the platform.

---
*Implementation completed: November 28, 2025*
