"""
Pydantic schemas for MCP Compliance Analyzer.

These schemas define the API contracts for the new LLM-based
compliance analysis engine.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


# =============================================================================
# Input Schemas
# =============================================================================

class LogEntry(BaseModel):
    """Single log entry for compliance analysis."""
    log_message: str = Field(..., description="The raw log message to analyze")
    timestamp: Optional[str] = Field(None, description="Log timestamp")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    destination_ip: Optional[str] = Field(None, description="Destination IP")
    port: Optional[int] = Field(22, description="Network port")
    status_code: Optional[int] = Field(200, description="Status code")
    hour_of_day: Optional[int] = Field(None, description="Hour (0-23)")
    is_business_hours: Optional[bool] = Field(None, description="Business hours flag")
    user_id: Optional[str] = Field(None, description="User identifier")
    resource: Optional[str] = Field(None, description="Resource accessed")
    action: Optional[str] = Field(None, description="Action performed")


class BatchAnalysisRequest(BaseModel):
    """Batch of logs for analysis."""
    logs: List[LogEntry]
    include_reasoning: bool = Field(True, description="Include LLM reasoning")
    include_recommendations: bool = Field(True, description="Include remediation")


class AnalysisRequest(BaseModel):
    """Single log analysis request."""
    log_message: str
    status_code: Optional[int] = 200
    hour_of_day: Optional[int] = None
    port: Optional[int] = 443
    context: Optional[Dict[str, Any]] = None
    include_reasoning: bool = True


# =============================================================================
# Output Schemas
# =============================================================================

class ControlMapping(BaseModel):
    """Mapping to a single NCSA control."""
    control_id: str = Field(..., description="NCSA control ID (e.g., RWNCSA-AC-37)")
    control_name: str = Field(..., description="Human-readable control name")
    control_family: str = Field(..., description="Control family")
    compliance_status: Literal["compliant", "non_compliant", "partial", "unknown"]
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    relevance: Optional[float] = Field(None, description="Relevance to the log")


class AnalysisResult(BaseModel):
    """Complete analysis result for a single log."""
    model_config = ConfigDict(protected_namespaces=())

    # Core prediction (backward compatible with XGBoost API)
    prediction: Literal["compliant", "non_compliant", "partial"]
    confidence: float = Field(..., ge=0.0, le=1.0)
    probabilities: Dict[str, float] = Field(
        default_factory=lambda: {"compliant": 0.5, "non_compliant": 0.5}
    )

    # Enhanced LLM output
    primary_control: ControlMapping
    secondary_controls: List[ControlMapping] = Field(default_factory=list)

    # Reasoning and explainability
    reasoning: Optional[str] = Field(None, description="LLM explanation")
    evidence_indicators: List[str] = Field(default_factory=list)
    risk_indicators: List[str] = Field(default_factory=list)

    # Remediation
    recommended_actions: List[str] = Field(default_factory=list)

    # Metadata
    model_used: str = Field(..., description="LLM model identifier")
    latency_ms: float = Field(..., description="Analysis latency in ms")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    cached: bool = Field(False, description="Whether result was cached")


class BatchAnalysisResult(BaseModel):
    """Results for batch analysis."""
    model_config = ConfigDict(protected_namespaces=())

    results: List[AnalysisResult]
    total_logs: int
    compliant_count: int
    non_compliant_count: int
    partial_count: int
    average_confidence: float
    total_latency_ms: float
    model_used: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: Literal["healthy", "degraded", "unhealthy"]
    version: str
    llm_provider: str
    llm_model: str
    cache_enabled: bool
    cache_size: int
    uptime_seconds: float


# =============================================================================
# NCSA Control Schemas
# =============================================================================

class NCSAControl(BaseModel):
    """Rwanda NCSA Control definition."""
    control_id: str
    control_name: str
    control_family: str
    description: str
    nist_mapping: Optional[str] = None
    evidence_patterns: List[str] = Field(default_factory=list)
    compliant_indicators: List[str] = Field(default_factory=list)
    non_compliant_indicators: List[str] = Field(default_factory=list)
    remediation_guidance: Optional[str] = None


class ControlFamilySummary(BaseModel):
    """Summary of a control family."""
    family_name: str
    control_count: int
    controls: List[str]
