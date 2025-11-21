"""
ENGINE 5: Report Generation Engine
Rwanda NCSA Compliance Auditor v3.0.0

LLM-powered PDF report generation for compliance auditing
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os
from datetime import datetime
import uuid
from pathlib import Path

from .services.llm_report_generator import LLMReportGenerator
from .services.pdf_generator import PDFGenerator
from .services.scorecard_generator import ScorecardGenerator
from .services.chart_generator import ChartGenerator

# Initialize FastAPI app
app = FastAPI(
    title="ENGINE 5: Report Generation Engine",
    description="LLM-powered PDF report generation for Rwanda NCSA compliance auditing",
    version="1.0.0"
)

# Initialize services
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)
llm_generator = LLMReportGenerator(api_key=OPENAI_API_KEY)
pdf_generator = PDFGenerator()
scorecard_generator = ScorecardGenerator()
chart_generator = ChartGenerator()

# Reports directory
REPORTS_DIR = Path("/app/reports")
REPORTS_DIR.mkdir(exist_ok=True)


# ============================================================================
# Pydantic Models
# ============================================================================

class ComplianceData(BaseModel):
    """Compliance data for report generation"""
    company_name: str = Field(..., description="Company name")
    assessment_date: Optional[str] = Field(None, description="Assessment date (YYYY-MM-DD)")
    framework: str = Field(default="Rwanda-NCSA", description="Compliance framework")

    # Compliance metrics
    total_controls: int = Field(..., description="Total number of controls")
    compliant_controls: int = Field(..., description="Number of compliant controls")
    non_compliant_controls: int = Field(..., description="Number of non-compliant controls")
    pending_controls: int = Field(default=0, description="Number of pending controls")

    # Family scores
    family_scores: List[Dict] = Field(default=[], description="Scores by control family")

    # Risk data
    risk_summary: Dict = Field(default={}, description="Risk assessment summary")

    # Events data
    total_events: int = Field(default=0, description="Total events analyzed")
    compliant_events: int = Field(default=0, description="Compliant events")
    non_compliant_events: int = Field(default=0, description="Non-compliant events")

    # Top issues
    top_issues: List[Dict] = Field(default=[], description="Top compliance issues")

    # Recommendations
    recommendations: List[str] = Field(default=[], description="Compliance recommendations")


class ReportRequest(BaseModel):
    """Request model for report generation"""
    report_type: str = Field(..., description="Report type: full, executive, scorecard, gap_analysis")
    compliance_data: ComplianceData
    include_charts: bool = Field(default=True, description="Include charts and visualizations")
    include_recommendations: bool = Field(default=True, description="Include AI-generated recommendations")
    language: str = Field(default="en", description="Report language")


class ReportResponse(BaseModel):
    """Response model for report generation"""
    success: bool
    report_id: str
    report_type: str
    company_name: str
    file_path: str
    file_size: int
    generation_time: float
    llm_enabled: bool
    pages: int


# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "ENGINE 5: Report Generation Engine",
        "version": "1.0.0",
        "status": "operational",
        "description": "LLM-powered PDF report generation for Rwanda NCSA compliance",
        "endpoints": {
            "generate_report": "POST /generate/report",
            "download_report": "GET /reports/{report_id}",
            "list_reports": "GET /reports",
            "health": "GET /health",
            "stats": "GET /stats"
        }
    }


@app.post("/generate/report", response_model=ReportResponse)
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """
    Generate compliance report

    Supports:
    - Full compliance report
    - Executive summary
    - Compliance scorecard
    - Gap analysis report
    """
    start_time = datetime.now()

    try:
        # Generate unique report ID
        report_id = str(uuid.uuid4())

        # Determine report type
        report_type = request.report_type.lower()

        if report_type not in ["full", "executive", "scorecard", "gap_analysis"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid report type: {report_type}. Must be one of: full, executive, scorecard, gap_analysis"
            )

        print(f"📊 Generating {report_type} report for {request.compliance_data.company_name}")

        # Step 1: Generate report content with LLM
        if report_type == "executive":
            content = await llm_generator.generate_executive_summary(
                compliance_data=request.compliance_data.dict(),
                include_recommendations=request.include_recommendations
            )
        elif report_type == "scorecard":
            content = scorecard_generator.generate_scorecard(
                compliance_data=request.compliance_data.dict()
            )
        elif report_type == "gap_analysis":
            content = await llm_generator.generate_gap_analysis(
                compliance_data=request.compliance_data.dict()
            )
        else:  # full report
            content = await llm_generator.generate_full_report(
                compliance_data=request.compliance_data.dict(),
                include_recommendations=request.include_recommendations
            )

        # Step 2: Generate charts if requested
        charts = []
        if request.include_charts:
            charts = chart_generator.generate_charts(
                compliance_data=request.compliance_data.dict(),
                report_type=report_type
            )

        # Step 3: Generate PDF
        pdf_filename = f"{report_id}_{report_type}_report.pdf"
        pdf_path = REPORTS_DIR / pdf_filename

        pdf_info = pdf_generator.generate_pdf(
            content=content,
            charts=charts,
            output_path=str(pdf_path),
            report_type=report_type,
            company_name=request.compliance_data.company_name
        )

        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds()

        print(f"✅ Report generated: {pdf_filename} ({pdf_info['pages']} pages, {pdf_info['file_size']} bytes)")

        # Schedule cleanup (delete report after 24 hours)
        background_tasks.add_task(cleanup_old_reports, max_age_hours=24)

        return ReportResponse(
            success=True,
            report_id=report_id,
            report_type=report_type,
            company_name=request.compliance_data.company_name,
            file_path=f"/reports/{report_id}",
            file_size=pdf_info['file_size'],
            generation_time=round(generation_time, 2),
            llm_enabled=llm_generator.is_enabled(),
            pages=pdf_info['pages']
        )

    except Exception as e:
        print(f"⚠️ Report generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@app.get("/reports/{report_id}")
async def download_report(report_id: str):
    """
    Download generated report by ID
    """
    try:
        # Find report file
        report_files = list(REPORTS_DIR.glob(f"{report_id}_*.pdf"))

        if not report_files:
            raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")

        report_file = report_files[0]

        # Extract report type from filename
        filename_parts = report_file.stem.split('_')
        report_type = filename_parts[1] if len(filename_parts) > 1 else "report"

        return FileResponse(
            path=str(report_file),
            media_type="application/pdf",
            filename=f"rwanda_ncsa_{report_type}_report.pdf"
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")


@app.get("/reports")
async def list_reports(limit: int = 50):
    """
    List all generated reports
    """
    try:
        reports = []

        for pdf_file in REPORTS_DIR.glob("*.pdf"):
            file_stats = pdf_file.stat()

            # Parse report ID and type from filename
            filename_parts = pdf_file.stem.split('_')
            report_id = filename_parts[0] if filename_parts else "unknown"
            report_type = filename_parts[1] if len(filename_parts) > 1 else "unknown"

            reports.append({
                "report_id": report_id,
                "report_type": report_type,
                "filename": pdf_file.name,
                "file_size": file_stats.st_size,
                "created_at": datetime.fromtimestamp(file_stats.st_ctime).isoformat(),
                "download_url": f"/reports/{report_id}"
            })

        # Sort by creation time (newest first)
        reports.sort(key=lambda x: x['created_at'], reverse=True)

        # Limit results
        reports = reports[:limit]

        return {
            "total": len(reports),
            "reports": reports
        }

    except Exception as e:
        print(f"⚠️ List reports error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list reports: {str(e)}")


@app.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    """
    Delete a report by ID
    """
    try:
        report_files = list(REPORTS_DIR.glob(f"{report_id}_*.pdf"))

        if not report_files:
            raise HTTPException(status_code=404, detail=f"Report not found: {report_id}")

        for report_file in report_files:
            report_file.unlink()

        return {
            "success": True,
            "message": f"Report deleted: {report_id}",
            "files_deleted": len(report_files)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"⚠️ Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Report Generation Engine",
        "version": "1.0.0",
        "llm_enabled": llm_generator.is_enabled(),
        "reports_directory": str(REPORTS_DIR),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/stats")
async def get_stats():
    """Get report generation statistics"""
    try:
        # Count reports by type
        report_counts = {
            "full": 0,
            "executive": 0,
            "scorecard": 0,
            "gap_analysis": 0,
            "total": 0
        }

        total_size = 0

        for pdf_file in REPORTS_DIR.glob("*.pdf"):
            filename_parts = pdf_file.stem.split('_')
            report_type = filename_parts[1] if len(filename_parts) > 1 else "unknown"

            if report_type in report_counts:
                report_counts[report_type] += 1

            report_counts["total"] += 1
            total_size += pdf_file.stat().st_size

        return {
            "service": "Report Generation Engine",
            "llm_enabled": llm_generator.is_enabled(),
            "report_types": ["full", "executive", "scorecard", "gap_analysis"],
            "reports_generated": report_counts,
            "total_storage_bytes": total_size,
            "total_storage_mb": round(total_size / (1024 * 1024), 2),
            "reports_directory": str(REPORTS_DIR)
        }

    except Exception as e:
        print(f"⚠️ Stats error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# ============================================================================
# Background Tasks
# ============================================================================

async def cleanup_old_reports(max_age_hours: int = 24):
    """
    Delete reports older than max_age_hours
    """
    try:
        cutoff_time = datetime.now().timestamp() - (max_age_hours * 3600)
        deleted_count = 0

        for pdf_file in REPORTS_DIR.glob("*.pdf"):
            file_stats = pdf_file.stat()

            if file_stats.st_ctime < cutoff_time:
                pdf_file.unlink()
                deleted_count += 1

        if deleted_count > 0:
            print(f"🗑️ Cleaned up {deleted_count} old reports")

    except Exception as e:
        print(f"⚠️ Cleanup error: {str(e)}")


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print("=" * 70)
    print("ENGINE 5: Report Generation Engine")
    print("Rwanda NCSA Compliance Auditor v3.0.0")
    print("=" * 70)
    print(f"📊 LLM Enabled: {llm_generator.is_enabled()}")
    print(f"📁 Reports Directory: {REPORTS_DIR}")
    print(f"🎨 Chart Generator: Initialized")
    print(f"📄 PDF Generator: Initialized")
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Report Generation Engine shutting down...")
