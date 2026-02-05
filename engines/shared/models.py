"""
Unified Data Models for Rwanda NCSA Compliance Auditor
=====================================================

This module defines the shared data models used across all engines to ensure
consistent data flow and enable proper correlation between log-based and
document-based compliance evidence.

Architecture:
- Engine 1 (Log Collector) → outputs ComplianceEvidence (source_type="log")
- Engine 2 (Document Processor) → outputs ComplianceEvidence (source_type="document")
- Both feed into Engine 3 (MCP+LLM Analyzer) for semantic compliance analysis
- Engine 4 (Decision Engine) compares and weights both sources
- Engine 5 (Report Generator) shows evidence from both sources

Engine 3 Evolution:
- Original: XGBoost classifier (rule-based ML)
- Current: MCP+LLM Analyzer (hybrid: rules + LLM semantic analysis)
- Uses Claude/GPT for context-aware compliance reasoning
- Maps events to Rwanda NCSA controls with explainable reasoning

Supports:
- Single source audits (logs only OR documents only)
- Dual source audits (logs AND documents - full gap analysis)
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, List, Any, Union
from pydantic import BaseModel, Field
import hashlib
import uuid


# =============================================================================
# Enums for Type Safety
# =============================================================================

class EvidenceSourceType(str, Enum):
    """Type of evidence source"""
    LOG = "log"                    # System logs (Engine 1)
    DOCUMENT = "document"          # Policy documents (Engine 2)
    CONFIG = "config"              # Configuration files
    MANUAL = "manual"              # Manual assessment
    MIXED = "mixed"                # Combined from multiple sources


class ComplianceStatus(str, Enum):
    """Compliance status classification"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_ASSESSED = "not_assessed"
    NOT_APPLICABLE = "not_applicable"


class SeverityLevel(str, Enum):
    """Severity level for non-compliance"""
    CRITICAL = "critical"          # Immediate action required
    HIGH = "high"                  # Action required within 24 hours
    MEDIUM = "medium"              # Action required within 7 days
    LOW = "low"                    # Action required within 30 days
    INFO = "info"                  # Informational only


class AuditMode(str, Enum):
    """Audit mode based on available sources"""
    LOGS_ONLY = "logs_only"                # Only log evidence
    DOCUMENTS_ONLY = "documents_only"      # Only document evidence
    FULL_AUDIT = "full_audit"              # Both logs and documents (gap analysis)


# =============================================================================
# Core Evidence Model
# =============================================================================

class ComplianceEvidence(BaseModel):
    """
    Unified model for compliance evidence from any source.

    This is the CORE data structure that flows through all engines.
    Both Engine 1 (logs) and Engine 2 (documents) output this format.
    Engine 3 classifies it, Engine 4 decides, Engine 5 reports.
    """

    # Unique identifier
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_id: str = Field(description="Parent audit ID")

    # Control mapping (Rwanda NCSA taxonomy)
    control_id: str = Field(description="Rwanda NCSA control ID (e.g., 'AC-2', 'IA-5')")
    control_name: str = Field(description="Human-readable control name")
    control_family: str = Field(default="", description="Control family (e.g., 'Access Control')")

    # Source information
    source_type: EvidenceSourceType = Field(description="Source type: log, document, config")
    source_file: str = Field(default="", description="Original source file/system name")
    source_line: Optional[int] = Field(default=None, description="Line number in source")

    # Evidence content
    evidence_text: str = Field(description="The actual evidence (log line or policy text)")
    evidence_summary: str = Field(default="", description="Brief summary of the evidence")

    # State comparison (for gap analysis)
    expected_state: str = Field(default="", description="What compliance looks like (from policy)")
    actual_state: str = Field(default="", description="What we found (from logs/reality)")

    # Timestamps
    timestamp: datetime = Field(default_factory=datetime.now)
    collected_at: datetime = Field(default_factory=datetime.now)

    # Confidence and scoring
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Relevance to control")

    # ML Features (for XGBoost classification)
    features: Dict[str, Any] = Field(default_factory=dict, description="Extracted features for ML")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_classification_input(self) -> Dict[str, Any]:
        """Convert to format expected by Engine 3 (MCP+LLM Analyzer)"""
        return {
            "log_message": self.evidence_text,
            "timestamp": self.timestamp.isoformat(),
            "source_ip": self.metadata.get("source_ip"),
            "destination_ip": self.metadata.get("destination_ip"),
            "port": self.metadata.get("port", 22),
            "status_code": self.metadata.get("status_code", 200),
            "hour_of_day": self.timestamp.hour if self.timestamp else None,
            "is_business_hours": 9 <= self.timestamp.hour <= 17 if self.timestamp else None,
            "user_id": self.metadata.get("user_id"),
            "resource": self.metadata.get("resource"),
            "action": self.metadata.get("action"),
            # Legacy fields for backward compatibility
            "evidence_id": self.evidence_id,
            "audit_id": self.audit_id,
            "control_id": self.control_id,
            "source_type": self.source_type.value,
        }

    def compute_hash(self) -> str:
        """Compute a unique hash for deduplication"""
        content = f"{self.control_id}:{self.source_type}:{self.evidence_text}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# =============================================================================
# Control Info Model (MCP+LLM Output)
# =============================================================================

class ControlInfo(BaseModel):
    """
    NCSA Control information from MCP+LLM Analyzer.
    Represents a mapped control with compliance status and confidence.
    """
    control_id: Optional[str] = Field(None, description="NCSA control ID (e.g., RWNCSA-AC-37)")
    control_name: Optional[str] = Field(None, description="Human-readable control name")
    control_family: Optional[str] = Field(None, description="Control family (e.g., Access Control)")
    compliance_status: Optional[str] = Field(None, description="compliant|non_compliant|partial|unknown")
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score")
    relevance: Optional[float] = Field(None, ge=0.0, le=1.0, description="Relevance to the log")


# =============================================================================
# Classification Result Model
# =============================================================================

class ClassificationResult(BaseModel):
    """
    Result from Engine 3 (MCP+LLM Analyzer).
    Contains the semantic compliance analysis with explainable reasoning.

    Evolution:
    - v1.0: XGBoost classifier (rule-based ML features)
    - v2.0: MCP+LLM Analyzer (hybrid semantic analysis with LLM reasoning)
    """

    evidence_id: Optional[str] = None
    audit_id: Optional[str] = None
    control_id: Optional[str] = None
    source_type: Optional[EvidenceSourceType] = None

    # Core classification outcome (backward compatible)
    prediction: ComplianceStatus = Field(description="Compliance prediction")
    confidence: float = Field(ge=0.0, le=1.0, description="Prediction confidence")
    probabilities: Dict[str, float] = Field(
        default_factory=lambda: {"compliant": 0.5, "non_compliant": 0.5},
        description="Class probabilities"
    )

    # Enhanced MCP+LLM control mapping
    primary_control: Optional[ControlInfo] = Field(
        None, description="Primary NCSA control from LLM analysis"
    )
    secondary_controls: List[ControlInfo] = Field(
        default_factory=list, description="Secondary related controls"
    )

    # LLM reasoning and explainability
    reasoning: Optional[str] = Field(
        None, description="LLM explanation of compliance determination"
    )
    evidence_indicators: List[str] = Field(
        default_factory=list, description="Evidence from the log supporting the decision"
    )
    risk_indicators: List[str] = Field(
        default_factory=list, description="Identified security risks"
    )
    recommended_actions: List[str] = Field(
        default_factory=list, description="Remediation recommendations"
    )

    # Model info
    model_used: str = Field(default="mcp-llm-analyzer", description="Model/analyzer identifier")
    latency_ms: float = Field(default=0.0, description="Analysis latency in milliseconds")
    cached: bool = Field(default=False, description="Whether result was from cache")
    timestamp: Optional[datetime] = Field(default=None, description="Analysis timestamp")

    # Legacy fields for backward compatibility
    model_version: str = Field(default="mcp-llm-v2.0")
    inference_time_ms: float = Field(default=0.0)  # Alias for latency_ms
    top_features: List[Dict[str, float]] = Field(default_factory=list)

    # Original evidence reference
    original_evidence: Optional[ComplianceEvidence] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def get_control_id(self) -> str:
        """Get the primary control ID from either source"""
        if self.primary_control and self.primary_control.control_id:
            return self.primary_control.control_id
        return self.control_id or "UNKNOWN"

    def get_control_family(self) -> str:
        """Get the control family from primary control"""
        if self.primary_control and self.primary_control.control_family:
            return self.primary_control.control_family
        return ""

    def to_legacy_format(self) -> Dict[str, Any]:
        """Convert to legacy XGBoost-compatible format for backward compatibility"""
        return {
            "evidence_id": self.evidence_id,
            "audit_id": self.audit_id,
            "control_id": self.get_control_id(),
            "prediction": self.prediction.value if isinstance(self.prediction, ComplianceStatus) else self.prediction,
            "confidence": self.confidence,
            "model_version": self.model_version,
            "inference_time_ms": self.latency_ms,
        }


# =============================================================================
# Decision Model (Engine 4 Output)
# =============================================================================

class ComplianceDecision(BaseModel):
    """
    Final compliance decision from Engine 4 (Decision Engine).
    Combines evidence from multiple sources with weighted scoring.
    """

    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_id: str
    control_id: str
    control_name: str
    control_family: str = ""

    # Final decision
    final_status: ComplianceStatus
    severity: SeverityLevel = SeverityLevel.INFO
    risk_score: float = Field(ge=0.0, le=100.0, description="Risk score 0-100")

    # Evidence sources
    has_log_evidence: bool = False
    has_document_evidence: bool = False
    audit_mode: AuditMode = AuditMode.LOGS_ONLY

    # Log-based findings
    log_evidence_count: int = 0
    log_status: Optional[ComplianceStatus] = None
    log_confidence: float = 0.0
    log_summary: str = ""

    # Document-based findings
    document_evidence_count: int = 0
    document_status: Optional[ComplianceStatus] = None
    document_confidence: float = 0.0
    document_summary: str = ""
    policy_requirement: str = ""  # What the policy says

    # Gap analysis (only for FULL_AUDIT mode)
    gap_detected: bool = False
    gap_description: str = ""

    # Weighted decision
    weighted_confidence: float = Field(ge=0.0, le=1.0)
    decision_rationale: str = ""

    # Routing
    needs_review: bool = False
    auto_accepted: bool = False

    # Recommendations
    remediation_priority: int = Field(default=5, ge=1, le=5)  # 1=highest
    remediation_steps: List[str] = Field(default_factory=list)

    # Timestamps
    decided_at: datetime = Field(default_factory=datetime.now)

    # All supporting evidence
    evidence_ids: List[str] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# =============================================================================
# Audit Configuration
# =============================================================================

class AuditConfig(BaseModel):
    """
    Configuration for an audit run.
    Specifies what sources to use and weighting.
    """

    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    # Target info
    target_host: str = ""
    target_os: str = ""
    framework: str = "Rwanda-NCSA"

    # Audit mode
    mode: AuditMode = AuditMode.LOGS_ONLY

    # Source flags
    include_logs: bool = True
    include_documents: bool = False
    document_ids: List[str] = Field(default_factory=list)  # Which documents to use

    # Weighting (for FULL_AUDIT mode)
    log_weight: float = Field(default=0.6, ge=0.0, le=1.0)
    document_weight: float = Field(default=0.4, ge=0.0, le=1.0)

    # Thresholds
    confidence_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    auto_accept_threshold: float = Field(default=0.90, ge=0.0, le=1.0)

    # Options
    enable_gap_analysis: bool = True
    enable_remediation_suggestions: bool = True

    def validate_weights(self):
        """Ensure weights sum to 1.0"""
        total = self.log_weight + self.document_weight
        if abs(total - 1.0) > 0.001:
            # Normalize
            self.log_weight = self.log_weight / total
            self.document_weight = self.document_weight / total


# =============================================================================
# Audit Summary Model (for Reports)
# =============================================================================

class AuditSummary(BaseModel):
    """
    Summary of an audit for report generation.
    Aggregates all decisions and provides statistics.
    """

    audit_id: str
    audit_mode: AuditMode
    framework: str = "Rwanda-NCSA"

    # Target info
    target_host: str
    target_os: str = ""

    # Timing
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0

    # Evidence statistics
    total_evidence_collected: int = 0
    log_evidence_count: int = 0
    document_evidence_count: int = 0

    # Decision statistics
    total_controls: int = 196  # Rwanda NCSA total
    controls_assessed: int = 0
    compliant_count: int = 0
    non_compliant_count: int = 0
    partial_count: int = 0
    not_assessed_count: int = 0

    # Scoring
    overall_score: float = Field(ge=0.0, le=100.0)
    risk_level: SeverityLevel = SeverityLevel.INFO

    # Gap analysis (for FULL_AUDIT)
    gaps_detected: int = 0
    gap_descriptions: List[str] = Field(default_factory=list)

    # By family breakdown
    family_scores: Dict[str, float] = Field(default_factory=dict)

    # Source indicator for report
    sources_used: List[str] = Field(default_factory=list)  # ["logs", "documents"]
    source_description: str = ""  # Human-readable description

    # Decisions
    decisions: List[ComplianceDecision] = Field(default_factory=list)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def compute_score(self):
        """Compute overall compliance score"""
        if self.controls_assessed == 0:
            self.overall_score = 0.0
            return

        # Compliant = 100%, Partial = 50%, Non-compliant = 0%
        score = (
            (self.compliant_count * 100) +
            (self.partial_count * 50)
        ) / self.controls_assessed

        self.overall_score = round(score, 1)

        # Set risk level
        if self.overall_score >= 90:
            self.risk_level = SeverityLevel.LOW
        elif self.overall_score >= 70:
            self.risk_level = SeverityLevel.MEDIUM
        elif self.overall_score >= 50:
            self.risk_level = SeverityLevel.HIGH
        else:
            self.risk_level = SeverityLevel.CRITICAL

    def generate_source_description(self):
        """Generate human-readable source description for report"""
        if self.audit_mode == AuditMode.LOGS_ONLY:
            self.sources_used = ["logs"]
            self.source_description = (
                f"This audit was performed using SYSTEM LOGS ONLY. "
                f"{self.log_evidence_count} log entries were analyzed from {self.target_host}. "
                f"No policy documents were included in this assessment."
            )
        elif self.audit_mode == AuditMode.DOCUMENTS_ONLY:
            self.sources_used = ["documents"]
            self.source_description = (
                f"This audit was performed using POLICY DOCUMENTS ONLY. "
                f"{self.document_evidence_count} policy requirements were extracted. "
                f"No system logs were collected for this assessment."
            )
        else:  # FULL_AUDIT
            self.sources_used = ["logs", "documents"]
            self.source_description = (
                f"This audit performed a FULL GAP ANALYSIS using both system logs and policy documents. "
                f"{self.log_evidence_count} log entries and {self.document_evidence_count} policy requirements were analyzed. "
                f"{self.gaps_detected} gaps were detected between stated policies and actual system behavior."
            )


# =============================================================================
# Evidence Batch (for bulk processing)
# =============================================================================

class EvidenceBatch(BaseModel):
    """Batch of evidence for bulk processing through engines"""

    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_id: str
    source_type: EvidenceSourceType

    evidence_items: List[ComplianceEvidence] = Field(default_factory=list)

    # Batch metadata
    total_count: int = 0
    processed_count: int = 0
    failed_count: int = 0

    created_at: datetime = Field(default_factory=datetime.now)

    def add_evidence(self, evidence: ComplianceEvidence):
        """Add evidence to batch"""
        self.evidence_items.append(evidence)
        self.total_count = len(self.evidence_items)


# =============================================================================
# Control Definition (from taxonomy)
# =============================================================================

class ControlDefinition(BaseModel):
    """
    Rwanda NCSA control definition from taxonomy.
    Used for mapping evidence to controls.
    """

    control_id: str
    control_name: str
    family: str
    family_id: str = ""
    description: str = ""

    # Expected evidence patterns
    log_patterns: List[str] = Field(default_factory=list)
    policy_keywords: List[str] = Field(default_factory=list)

    # Compliance indicators
    compliant_indicators: List[str] = Field(default_factory=list)
    non_compliant_indicators: List[str] = Field(default_factory=list)

    # NIST mapping
    nist_mapping: List[str] = Field(default_factory=list)

    # Weighting
    importance_weight: float = Field(default=1.0, ge=0.0, le=5.0)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
