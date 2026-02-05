"""
Engine 3: MCP-based Compliance Analyzer

FastAPI service that provides LLM-powered compliance analysis
for Rwanda NCSA Minimum Cybersecurity Standards.

This replaces the XGBoost classifier with semantic analysis using
Claude or GPT models via the Model Context Protocol (MCP).

Author: Moise Iradukunda Ingabire
Institution: Carnegie Mellon University Africa
"""

import os
import time
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .models.schemas import (
    LogEntry, AnalysisRequest, BatchAnalysisRequest,
    AnalysisResult, BatchAnalysisResult, HealthResponse,
    ControlMapping
)
# Try to import expanded controls (169 controls), fall back to original (47 controls)
try:
    from .models.ncsa_controls_expanded import (
        get_all_controls, get_control, get_control_families,
        find_relevant_controls, NCSA_CONTROLS, get_control_statistics,
        get_system_auditable_controls, get_policy_based_controls,
        get_controls_by_audit_type
    )
    USING_EXPANDED_CONTROLS = True
    print("✅ Using expanded NCSA controls (169 controls)")
except ImportError:
    from .models.ncsa_controls import (
        get_all_controls, get_control, get_control_families,
        find_relevant_controls, NCSA_CONTROLS
    )
    USING_EXPANDED_CONTROLS = False
    print("⚠️ Using original NCSA controls (47 controls)")

from .services.llm_client import ComplianceLLMClient
from .services.control_type_prompts import (
    format_control_prompt, determine_evidence_type,
    CONTROL_AUDIT_TYPES
)
from .services.evidence_parsers import (
    parse_audit_output, evaluate_compliance, PARSER_REGISTRY
)
from .services.audit_executor import AsyncAuditExecutor, get_async_audit_executor


# =============================================================================
# Configuration
# =============================================================================

class Settings:
    """Application settings from environment."""
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "anthropic")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ENABLE_CACHE: bool = os.getenv("ENABLE_CACHE", "true").lower() == "true"
    CACHE_SIZE: int = int(os.getenv("CACHE_SIZE", "10000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    # Fallback to rule-based for obvious cases
    USE_HYBRID_MODE: bool = os.getenv("USE_HYBRID_MODE", "true").lower() == "true"
    HYBRID_CONFIDENCE_THRESHOLD: float = float(os.getenv("HYBRID_CONFIDENCE_THRESHOLD", "0.95"))


settings = Settings()

# =============================================================================
# Application State
# =============================================================================

class AppState:
    """Global application state."""
    llm_client: Optional[ComplianceLLMClient] = None
    audit_executor: Optional[AsyncAuditExecutor] = None
    start_time: float = 0
    requests_processed: int = 0
    errors_count: int = 0


state = AppState()


# =============================================================================
# Lifecycle
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    state.start_time = time.time()

    # Initialize LLM client
    try:
        state.llm_client = ComplianceLLMClient(
            provider=settings.LLM_PROVIDER,
            model=settings.LLM_MODEL,
            enable_cache=settings.ENABLE_CACHE,
            cache_size=settings.CACHE_SIZE
        )
        print(f"LLM Client initialized: {settings.LLM_PROVIDER}/{settings.LLM_MODEL}")
    except Exception as e:
        print(f"Warning: LLM client initialization failed: {e}")
        print("Service will run in rule-based fallback mode")

    # Initialize audit executor
    try:
        state.audit_executor = get_async_audit_executor()
        auditable_count = len(state.audit_executor.get_auditable_controls())
        print(f"Audit Executor initialized: {auditable_count} auditable controls")
    except Exception as e:
        print(f"Warning: Audit executor initialization failed: {e}")

    yield

    # Shutdown
    if state.llm_client:
        stats = state.llm_client.get_usage_stats()
        print(f"Shutdown - Usage stats: {stats}")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="Engine 3: MCP Compliance Analyzer",
    description="LLM-powered compliance analysis for Rwanda NCSA standards",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Rule-Based Fallback
# =============================================================================

def rule_based_analysis(log_message: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fast rule-based analysis for obvious compliance patterns.
    Used as fallback or for high-confidence patterns in hybrid mode.
    """
    log_lower = log_message.lower()
    start_time = time.time()

    # High-confidence patterns
    patterns = {
        # Non-compliant patterns
        "failed password": ("RWNCSA-IA-98", "non_compliant", 0.98),
        "authentication failure": ("RWNCSA-AC-37", "non_compliant", 0.98),
        "invalid user": ("RWNCSA-AC-38", "non_compliant", 0.98),
        "did not receive identification": ("RWNCSA-IA-100", "non_compliant", 0.95),
        "access denied": ("RWNCSA-AC-37", "non_compliant", 0.95),

        # Compliant patterns
        "accepted password": ("RWNCSA-IA-97", "compliant", 0.98),
        "accepted publickey": ("RWNCSA-IA-99", "compliant", 0.98),
        "session opened": ("RWNCSA-AU-68", "compliant", 0.95),
        "session closed": ("RWNCSA-AU-69", "compliant", 0.95),
        "connection closed": ("RWNCSA-SC-155", "compliant", 0.90),
        "cron": ("RWNCSA-CM-83", "compliant", 0.90),
    }

    for pattern, (control_id, status, confidence) in patterns.items():
        if pattern in log_lower:
            ctrl = get_control(control_id)
            latency = (time.time() - start_time) * 1000

            return {
                "prediction": status,
                "confidence": confidence,
                "probabilities": {
                    "compliant": confidence if status == "compliant" else 1 - confidence,
                    "non_compliant": confidence if status == "non_compliant" else 1 - confidence
                },
                "primary_control": {
                    "control_id": control_id,
                    "control_name": ctrl.get("control_name", "Unknown"),
                    "control_family": ctrl.get("control_family", "Unknown"),
                    "compliance_status": status,
                    "confidence": confidence,
                    "relevance": 1.0
                },
                "secondary_controls": [],
                "reasoning": f"Rule-based match: pattern '{pattern}' detected in log",
                "evidence_indicators": [f"Matched pattern: {pattern}"],
                "risk_indicators": [] if status == "compliant" else [f"Security event: {pattern}"],
                "recommended_actions": [] if status == "compliant" else [ctrl.get("remediation_guidance", "Review security configuration")],
                "model_used": "rule-based",
                "latency_ms": latency,
                "cached": False,
                "timestamp": datetime.utcnow().isoformat()
            }

    # No high-confidence match - return None to trigger LLM analysis
    return None


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    control_count = len(NCSA_CONTROLS)
    return {
        "service": "Engine 3: MCP Compliance Analyzer",
        "version": "2.0.0",
        "status": "running",
        "provider": settings.LLM_PROVIDER,
        "model": settings.LLM_MODEL,
        "controls_loaded": control_count,
        "using_expanded_controls": USING_EXPANDED_CONTROLS
    }


@app.get("/controls/stats", tags=["Controls"])
async def get_controls_statistics():
    """
    Get statistics about loaded NCSA controls.

    Shows breakdown by:
    - Total controls
    - Audit type (system, policy, physical, mixed)
    - Control family
    - Compliance type (Basic, Enhanced)
    """
    if USING_EXPANDED_CONTROLS:
        stats = get_control_statistics()
        return {
            "total_controls": stats["total_controls"],
            "expanded_controls": True,
            "by_audit_type": stats["by_audit_type"],
            "by_compliance_type": stats["by_compliance_type"],
            "by_family": stats["by_family"],
            "audit_type_descriptions": CONTROL_AUDIT_TYPES
        }
    else:
        # Original controls don't have audit_type
        return {
            "total_controls": len(NCSA_CONTROLS),
            "expanded_controls": False,
            "note": "Using original 47 controls. Run expand_ncsa_controls.py to generate all 169 controls."
        }


@app.get("/controls/{control_id}", tags=["Controls"])
async def get_control_details(control_id: str):
    """Get details for a specific control."""
    control = get_control(control_id)
    if not control:
        raise HTTPException(status_code=404, detail=f"Control {control_id} not found")
    return control


@app.get("/controls/family/{family}", tags=["Controls"])
async def get_controls_by_family_endpoint(family: str):
    """Get all controls in a specific family."""
    # Filter controls by family
    controls = [
        ctrl for ctrl in NCSA_CONTROLS.values()
        if ctrl.get("control_family") == family
    ]
    return {
        "family": family,
        "count": len(controls),
        "controls": controls
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    uptime = time.time() - state.start_time

    status = "healthy"
    if state.llm_client is None:
        status = "degraded"
    if state.errors_count > 100:
        status = "unhealthy"

    cache_size = 0
    if state.llm_client and state.llm_client.cache:
        cache_size = len(state.llm_client.cache.cache)

    return HealthResponse(
        status=status,
        version="2.0.0",
        llm_provider=settings.LLM_PROVIDER,
        llm_model=settings.LLM_MODEL,
        cache_enabled=settings.ENABLE_CACHE,
        cache_size=cache_size,
        uptime_seconds=uptime
    )


@app.post("/classify", tags=["Classification"])
async def classify_log(request: AnalysisRequest):
    """
    Classify a single log entry.

    Backward compatible with XGBoost Engine 3 API.
    """
    state.requests_processed += 1

    context = {
        "status_code": request.status_code,
        "hour_of_day": request.hour_of_day or datetime.now().hour,
        "port": request.port,
        **(request.context or {})
    }

    # Try rule-based first in hybrid mode
    if settings.USE_HYBRID_MODE:
        rule_result = rule_based_analysis(request.log_message, context)
        if rule_result and rule_result["confidence"] >= settings.HYBRID_CONFIDENCE_THRESHOLD:
            return rule_result

    # Fall back to LLM analysis
    if state.llm_client:
        try:
            result = await state.llm_client.analyze_log(
                log_message=request.log_message,
                context=context,
                include_reasoning=request.include_reasoning
            )
            return result
        except Exception as e:
            state.errors_count += 1
            # Fall back to rule-based with lower confidence
            rule_result = rule_based_analysis(request.log_message, context)
            if rule_result:
                rule_result["reasoning"] = f"LLM error, using rule-based: {str(e)}"
                rule_result["confidence"] *= 0.8  # Lower confidence
                return rule_result

            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    else:
        # No LLM client - use rule-based only
        rule_result = rule_based_analysis(request.log_message, context)
        if rule_result:
            return rule_result

        # Return default for unknown patterns
        return {
            "prediction": "unknown",
            "confidence": 0.5,
            "probabilities": {"compliant": 0.5, "non_compliant": 0.5},
            "primary_control": {
                "control_id": "RWNCSA-AU-70",
                "control_name": "General Audit Events",
                "control_family": "Audit and Accountability",
                "compliance_status": "unknown",
                "confidence": 0.5,
                "relevance": 0.5
            },
            "secondary_controls": [],
            "reasoning": "No LLM client available and no rule-based match",
            "evidence_indicators": [],
            "risk_indicators": [],
            "recommended_actions": ["Manual review required"],
            "model_used": "fallback",
            "latency_ms": 0,
            "cached": False
        }


@app.post("/classify/batch", tags=["Classification"])
async def classify_batch(request: BatchAnalysisRequest):
    """
    Classify multiple log entries.

    Returns aggregated results with summary statistics.
    """
    state.requests_processed += len(request.logs)
    start_time = time.time()

    results = []
    compliant_count = 0
    non_compliant_count = 0
    partial_count = 0
    total_confidence = 0

    for log_entry in request.logs:
        context = {
            "timestamp": log_entry.timestamp,
            "source_ip": log_entry.source_ip,
            "destination_ip": log_entry.destination_ip,
            "port": log_entry.port,
            "status_code": log_entry.status_code,
            "hour_of_day": log_entry.hour_of_day,
            "is_business_hours": log_entry.is_business_hours,
            "user_id": log_entry.user_id,
            "action": log_entry.action
        }

        # Try rule-based first
        result = None
        if settings.USE_HYBRID_MODE:
            result = rule_based_analysis(log_entry.log_message, context)

        # Use LLM if rule-based didn't match or confidence too low
        if not result or result["confidence"] < settings.HYBRID_CONFIDENCE_THRESHOLD:
            if state.llm_client:
                try:
                    result = await state.llm_client.analyze_log(
                        log_message=log_entry.log_message,
                        context=context,
                        include_reasoning=request.include_reasoning
                    )
                except Exception as e:
                    state.errors_count += 1
                    if not result:
                        result = {
                            "prediction": "unknown",
                            "confidence": 0.0,
                            "error": str(e)
                        }

        if not result:
            result = {
                "prediction": "unknown",
                "confidence": 0.5,
                "probabilities": {"compliant": 0.5, "non_compliant": 0.5}
            }

        results.append(result)

        # Update counts
        prediction = result.get("prediction", "unknown")
        if prediction == "compliant":
            compliant_count += 1
        elif prediction == "non_compliant":
            non_compliant_count += 1
        elif prediction == "partial":
            partial_count += 1

        total_confidence += result.get("confidence", 0.5)

    total_latency = (time.time() - start_time) * 1000
    avg_confidence = total_confidence / len(results) if results else 0

    return {
        "results": results,
        "total_logs": len(request.logs),
        "compliant_count": compliant_count,
        "non_compliant_count": non_compliant_count,
        "partial_count": partial_count,
        "average_confidence": avg_confidence,
        "total_latency_ms": total_latency,
        "model_used": settings.LLM_MODEL
    }


@app.get("/controls", tags=["Controls"])
async def list_controls():
    """List all available NCSA controls."""
    return {
        "total_controls": len(NCSA_CONTROLS),
        "controls": list(NCSA_CONTROLS.keys()),
        "families": get_control_families()
    }


@app.get("/controls/{control_id}", tags=["Controls"])
async def get_control_details(control_id: str):
    """Get details for a specific control."""
    ctrl = get_control(control_id)
    if not ctrl:
        raise HTTPException(status_code=404, detail=f"Control not found: {control_id}")
    return ctrl


@app.get("/stats", tags=["Statistics"])
async def get_statistics():
    """Get service statistics."""
    stats = {
        "service": "Engine 3: MCP Compliance Analyzer",
        "uptime_seconds": time.time() - state.start_time,
        "requests_processed": state.requests_processed,
        "errors_count": state.errors_count,
        "settings": {
            "provider": settings.LLM_PROVIDER,
            "model": settings.LLM_MODEL,
            "hybrid_mode": settings.USE_HYBRID_MODE,
            "cache_enabled": settings.ENABLE_CACHE
        }
    }

    if state.llm_client:
        stats["llm_usage"] = state.llm_client.get_usage_stats()

    return stats


# =============================================================================
# Audit Execution Endpoints
# =============================================================================

class AuditRequest(BaseModel):
    """Request for batch audit execution."""
    control_ids: List[str] = Field(..., description="List of control IDs to audit")
    timeout: int = Field(default=10, description="Command timeout in seconds")


@app.get("/audit/{control_id}", tags=["Audit"])
async def audit_single_control(control_id: str, timeout: int = 10):
    """
    Execute audit for a single control.

    Runs the macOS audit command for the specified control and
    parses the output to determine compliance status.

    Args:
        control_id: NCSA control ID (e.g., 'RWNCSA-AC-001')
        timeout: Command timeout in seconds (default: 10)

    Returns:
        Audit result with compliance status and evidence
    """
    if not state.audit_executor:
        raise HTTPException(status_code=503, detail="Audit executor not initialized")

    result = await state.audit_executor.audit_control_async(control_id, timeout)

    if not result.get("success") and "not found" in str(result.get("error", "")):
        raise HTTPException(status_code=404, detail=f"Control {control_id} not found")

    return result


@app.post("/audit/batch", tags=["Audit"])
async def audit_batch_controls(request: AuditRequest):
    """
    Execute audits for multiple controls.

    Args:
        request: AuditRequest with control_ids and timeout

    Returns:
        Batch audit results with summary statistics
    """
    if not state.audit_executor:
        raise HTTPException(status_code=503, detail="Audit executor not initialized")

    result = await state.audit_executor.audit_controls_batch_async(
        request.control_ids,
        request.timeout
    )

    return result


@app.get("/audit/family/{family}", tags=["Audit"])
async def audit_family(family: str, timeout: int = 10):
    """
    Execute audits for all controls in a family.

    Args:
        family: Control family name (e.g., 'Access Control')
        timeout: Command timeout in seconds

    Returns:
        Family audit results with compliance summary
    """
    if not state.audit_executor:
        raise HTTPException(status_code=503, detail="Audit executor not initialized")

    # Get controls in family
    control_ids = [
        ctrl_id for ctrl_id, ctrl in state.audit_executor.controls.items()
        if ctrl.get('family') == family
    ]

    if not control_ids:
        raise HTTPException(status_code=404, detail=f"No controls found for family: {family}")

    result = await state.audit_executor.audit_controls_batch_async(
        control_ids,
        timeout
    )
    result["family"] = family

    return result


@app.get("/audit/families", tags=["Audit"])
async def list_auditable_families():
    """
    List all control families available for auditing.

    Returns:
        List of families with control counts
    """
    if not state.audit_executor:
        raise HTTPException(status_code=503, detail="Audit executor not initialized")

    families = {}
    for ctrl in state.audit_executor.controls.values():
        family = ctrl.get('family', 'Unknown')
        if family not in families:
            families[family] = 0
        families[family] += 1

    return {
        "families": families,
        "total_families": len(families),
        "total_controls": sum(families.values())
    }


@app.get("/parsers", tags=["Audit"])
async def list_parsers():
    """
    List all available evidence parsers.

    Returns:
        List of parser names and count
    """
    return {
        "parsers": sorted(PARSER_REGISTRY.keys()),
        "total_parsers": len(PARSER_REGISTRY)
    }


# =============================================================================
# Backward Compatibility Endpoints (match XGBoost Engine 3)
# =============================================================================

@app.post("/api/v1/classify", tags=["Legacy"])
async def legacy_classify(request: AnalysisRequest):
    """Legacy endpoint for backward compatibility with Engine 4."""
    return await classify_log(request)


@app.post("/api/v1/classify/batch", tags=["Legacy"])
async def legacy_batch_classify(request: BatchAnalysisRequest):
    """Legacy batch endpoint."""
    return await classify_batch(request)


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )
