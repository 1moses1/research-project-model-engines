"""
ENGINE 5: Report Generation Engine
Rwanda NCSA Compliance Auditor v3.0.0

LLM-powered PDF report generation for compliance auditing
Includes Redis integration for audit state updates
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import os
import json
from datetime import datetime
import uuid
from pathlib import Path
import sys

from .services.llm_report_generator import LLMReportGenerator
from .services.pdf_generator import PDFGenerator
from .services.scorecard_generator import ScorecardGenerator
from .services.chart_generator import ChartGenerator

# Import shared models for unified pipeline
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared'))
try:
    from shared import (
        RedisClient, get_redis_client, init_redis,
        ComplianceEvidence, EvidenceSourceType,
        ClassificationResult, ComplianceDecision, ComplianceStatus,
        AuditMode, AuditSummary,
        EvidenceManager, create_evidence_manager
    )
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False
    print("⚠️ Shared module not available - running in standalone mode")

# Redis integration
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
ENGINE_NAME = os.getenv("ENGINE_NAME", "engine5-report-generator")

# Redis client and evidence manager
redis_client = None
evidence_manager = None

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

# Reports directory - use /app/reports for Docker, local path otherwise
REPORTS_DIR = Path("/app/reports") if Path("/app").exists() else Path(__file__).parent.parent / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


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
# UNIFIED PIPELINE ENDPOINTS - Audit Report Generation
# ============================================================================

@app.post("/api/v1/generate/audit-report/{audit_id}")
async def generate_audit_report(
    audit_id: str,
    company_name: str,
    report_type: str = "full",
    include_charts: bool = True,
    background_tasks: BackgroundTasks = None
):
    """
    Generate compliance report from unified pipeline audit data.

    This endpoint:
    1. Retrieves evidence and decisions from Redis for the given audit_id
    2. Determines audit mode (LOGS_ONLY, DOCUMENTS_ONLY, or FULL_AUDIT)
    3. Generates report with source indicators (📄 Document, 📊 Log)
    4. Displays gap analysis results if available
    5. Creates PDF report with LLM-generated insights

    Args:
        audit_id: The audit identifier
        company_name: Company being audited
        report_type: Type of report (full, executive, scorecard, gap_analysis)
        include_charts: Whether to include charts

    Returns:
        Report response with file path and metadata
    """
    if not SHARED_AVAILABLE or not evidence_manager:
        raise HTTPException(
            status_code=503,
            detail="Unified pipeline not available. Cannot generate audit reports from Redis."
        )

    start_time = datetime.now()

    try:
        print(f"\n{'='*80}")
        print(f"📊 Generating {report_type} report for audit: {audit_id}")
        print(f"{'='*80}\n")

        # Step 1: Retrieve evidence from Redis
        all_evidence = await evidence_manager.get_all_evidence(audit_id)

        if not all_evidence:
            raise HTTPException(
                status_code=404,
                detail=f"No evidence found for audit_id: {audit_id}"
            )

        print(f"  Retrieved {len(all_evidence)} evidence items")

        # Step 2: Retrieve decisions from Redis
        control_ids = list(set(e.control_id for e in all_evidence))
        decisions = []

        for control_id in control_ids:
            decision = await evidence_manager.get_decision(audit_id, control_id)
            if decision:
                decisions.append(decision)

        print(f"  Retrieved {len(decisions)} compliance decisions")

        # Step 3: Determine audit mode
        log_evidence_count = sum(1 for e in all_evidence if e.source_type == EvidenceSourceType.LOG)
        doc_evidence_count = sum(1 for e in all_evidence if e.source_type == EvidenceSourceType.DOCUMENT)

        if log_evidence_count > 0 and doc_evidence_count > 0:
            audit_mode = AuditMode.FULL_AUDIT
            audit_mode_label = "Full Audit (Logs + Documents with Gap Analysis)"
        elif log_evidence_count > 0:
            audit_mode = AuditMode.LOGS_ONLY
            audit_mode_label = "Logs Only Audit"
        elif doc_evidence_count > 0:
            audit_mode = AuditMode.DOCUMENTS_ONLY
            audit_mode_label = "Documents Only Audit"
        else:
            audit_mode = AuditMode.LOGS_ONLY
            audit_mode_label = "Unknown Audit Mode"

        print(f"  Audit Mode: {audit_mode_label}")
        print(f"    - Log evidence: {log_evidence_count}")
        print(f"    - Document evidence: {doc_evidence_count}")

        # Step 4: Prepare compliance data with source indicators
        compliant_count = sum(1 for d in decisions if d.final_status == ComplianceStatus.COMPLIANT)
        non_compliant_count = sum(1 for d in decisions if d.final_status == ComplianceStatus.NON_COMPLIANT)
        partial_count = sum(1 for d in decisions if d.final_status == ComplianceStatus.PARTIAL)

        gaps_detected = sum(1 for d in decisions if d.gap_detected)

        # Build family scores with source indicators
        family_scores = []
        families = {}

        for decision in decisions:
            family = decision.control_family
            if family not in families:
                families[family] = {
                    "compliant": 0,
                    "non_compliant": 0,
                    "partial": 0,
                    "total": 0,
                    "log_evidence": 0,
                    "doc_evidence": 0
                }

            families[family]["total"] += 1
            families[family]["log_evidence"] += decision.log_evidence_count
            families[family]["doc_evidence"] += decision.document_evidence_count

            if decision.final_status == ComplianceStatus.COMPLIANT:
                families[family]["compliant"] += 1
            elif decision.final_status == ComplianceStatus.NON_COMPLIANT:
                families[family]["non_compliant"] += 1
            else:
                families[family]["partial"] += 1

        for family, data in families.items():
            compliance_rate = (data["compliant"] / data["total"] * 100) if data["total"] > 0 else 0

            # Add source indicators
            sources = []
            if data["log_evidence"] > 0:
                sources.append(f"📊 {data['log_evidence']} logs")
            if data["doc_evidence"] > 0:
                sources.append(f"📄 {data['doc_evidence']} docs")

            family_scores.append({
                "family": family,
                "total_controls": data["total"],
                "compliant": data["compliant"],
                "non_compliant": data["non_compliant"],
                "partial": data["partial"],
                "compliance_rate": round(compliance_rate, 1),
                "sources": ", ".join(sources),
                "audit_mode_indicator": audit_mode_label
            })

        # Build top issues with gap information
        top_issues = []
        for decision in sorted(decisions, key=lambda d: d.compliance_score):
            if decision.final_status != ComplianceStatus.COMPLIANT:
                issue = {
                    "control_id": decision.control_id,
                    "control_name": decision.control_name,
                    "status": decision.final_status.value,
                    "score": round(decision.compliance_score, 2),
                    "confidence": round(decision.confidence, 2),
                    "recommendation": decision.recommendation
                }

                # Add gap information
                if decision.gap_detected:
                    issue["gap_type"] = decision.gap_type
                    issue["gap_severity"] = decision.gap_severity
                    issue["gap_description"] = decision.gap_description
                    issue["gap_indicator"] = f"⚠️ GAP DETECTED: {decision.gap_type}"

                # Add source indicators
                sources = []
                if decision.log_evidence_count > 0:
                    sources.append(f"📊 {decision.log_evidence_count} logs")
                if decision.document_evidence_count > 0:
                    sources.append(f"📄 {decision.document_evidence_count} docs")
                issue["sources"] = ", ".join(sources)

                top_issues.append(issue)

                if len(top_issues) >= 10:
                    break

        # Build compliance data
        compliance_data_dict = {
            "company_name": company_name,
            "assessment_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "framework": "Rwanda-NCSA",
            "audit_id": audit_id,
            "audit_mode": audit_mode.value,
            "audit_mode_label": audit_mode_label,
            "total_controls": len(decisions),
            "compliant_controls": compliant_count,
            "non_compliant_controls": non_compliant_count,
            "pending_controls": partial_count,
            "family_scores": family_scores,
            "total_events": len(all_evidence),
            "log_evidence_count": log_evidence_count,
            "document_evidence_count": doc_evidence_count,
            "compliant_events": compliant_count,
            "non_compliant_events": non_compliant_count,
            "gaps_detected": gaps_detected,
            "top_issues": top_issues,
            "recommendations": [
                f"Audit Mode: {audit_mode_label}",
                f"Total Evidence: {len(all_evidence)} items ({log_evidence_count} logs, {doc_evidence_count} documents)",
                f"Gaps Detected: {gaps_detected} policy-reality discrepancies" if gaps_detected > 0 else "No gaps detected between policy and implementation"
            ]
        }

        # Step 5: Generate report content with LLM
        print(f"  Generating report content with LLM...")

        if report_type == "executive":
            content = await llm_generator.generate_executive_summary(
                compliance_data=compliance_data_dict,
                include_recommendations=True
            )
        elif report_type == "scorecard":
            content = scorecard_generator.generate_scorecard(
                compliance_data=compliance_data_dict
            )
        elif report_type == "gap_analysis":
            content = await llm_generator.generate_gap_analysis(
                compliance_data=compliance_data_dict
            )
        else:  # full report
            content = await llm_generator.generate_full_report(
                compliance_data=compliance_data_dict,
                include_recommendations=True
            )

        # Step 6: Generate charts
        charts = []
        if include_charts:
            print(f"  Generating charts...")
            charts = chart_generator.generate_charts(
                compliance_data=compliance_data_dict,
                report_type=report_type
            )

        # Step 7: Generate PDF
        report_id = str(uuid.uuid4())
        pdf_filename = f"{report_id}_{report_type}_report.pdf"
        pdf_path = REPORTS_DIR / pdf_filename

        print(f"  Generating PDF...")

        pdf_info = pdf_generator.generate_pdf(
            content=content,
            charts=charts,
            output_path=str(pdf_path),
            report_type=report_type,
            company_name=company_name
        )

        generation_time = (datetime.now() - start_time).total_seconds()

        print(f"\n✅ Report generated successfully!")
        print(f"   File: {pdf_filename}")
        print(f"   Pages: {pdf_info['pages']}")
        print(f"   Size: {pdf_info['file_size']} bytes")
        print(f"   Time: {generation_time:.2f}s")
        print(f"{'='*80}\n")

        # Schedule cleanup
        if background_tasks:
            background_tasks.add_task(cleanup_old_reports, max_age_hours=24)

        return {
            "success": True,
            "report_id": report_id,
            "report_type": report_type,
            "audit_id": audit_id,
            "audit_mode": audit_mode.value,
            "audit_mode_label": audit_mode_label,
            "company_name": company_name,
            "file_path": f"/reports/{report_id}",
            "download_url": f"/reports/{report_id}",
            "file_size": pdf_info['file_size'],
            "pages": pdf_info['pages'],
            "generation_time": round(generation_time, 2),
            "llm_enabled": llm_generator.is_enabled(),
            "evidence_summary": {
                "total_evidence": len(all_evidence),
                "log_evidence": log_evidence_count,
                "document_evidence": doc_evidence_count,
                "controls_assessed": len(decisions),
                "gaps_detected": gaps_detected
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Report generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


# ============================================================================
# END UNIFIED PIPELINE ENDPOINTS
# ============================================================================


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

async def init_redis():
    """Initialize Redis connection"""
    global redis_client
    if not REDIS_AVAILABLE:
        return False
    try:
        redis_client = aioredis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True
        )
        await redis_client.ping()
        print(f"[{ENGINE_NAME}] Connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
        return True
    except Exception as e:
        print(f"[{ENGINE_NAME}] Redis connection failed: {e}")
        redis_client = None
        return False


async def update_audit_state(audit_id: str, stage: str, progress: int, message: str, details: Optional[Dict] = None):
    """Update audit state in Redis and publish for real-time updates"""
    if not redis_client:
        return

    try:
        state = {
            "audit_id": audit_id,
            "stage": stage,
            "progress": progress,
            "message": message,
            "engine": ENGINE_NAME,
            "timestamp": datetime.now().isoformat()
        }
        if details:
            state["details"] = details

        await redis_client.set(f"audit:{audit_id}:state", json.dumps(state))
        await redis_client.publish(f"audit:{audit_id}:updates", json.dumps(state))
        print(f"[{ENGINE_NAME}] Audit {audit_id}: {stage} ({progress}%)")
    except Exception as e:
        print(f"[{ENGINE_NAME}] Redis update error: {e}")


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global evidence_manager

    print("=" * 70)
    print("ENGINE 5: Report Generation Engine")
    print("Rwanda NCSA Compliance Auditor v3.0.0")
    print("=" * 70)

    # Initialize Redis
    redis_connected = await init_redis()
    print(f"Redis Connected: {redis_connected}")

    # Initialize unified pipeline components
    if SHARED_AVAILABLE and redis_connected and redis_client:
        try:
            # Create RedisClient from shared module using existing connection
            shared_redis = get_redis_client()
            if not shared_redis:
                # Initialize shared Redis client
                shared_redis = await init_redis(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=0
                )

            # Initialize Evidence Manager
            evidence_manager = create_evidence_manager(shared_redis)
            print("✅ Evidence Manager initialized - Unified pipeline active")
            print("📊 Report generator can now access evidence from Redis")
        except Exception as e:
            print(f"⚠️ Failed to initialize unified pipeline: {e}")
            print("⚠️ Running in standalone mode (legacy reports only)")
            evidence_manager = None
    else:
        if not SHARED_AVAILABLE:
            print("⚠️ Shared module not available - running in standalone mode")
        evidence_manager = None

    print(f"LLM Enabled: {llm_generator.is_enabled()}")
    print(f"Reports Directory: {REPORTS_DIR}")
    print(f"Chart Generator: Initialized")
    print(f"PDF Generator: Initialized")
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Report Generation Engine shutting down...")
