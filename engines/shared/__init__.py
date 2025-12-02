"""
Shared utilities for Rwanda NCSA Compliance Auditor Engines
============================================================

This package provides shared models, utilities, and infrastructure
that all engines use for consistent data flow and communication.

Architecture:
- models.py: Unified data models (ComplianceEvidence, ClassificationResult, etc.)
- redis_client.py: Redis client for caching and pub/sub
- audit_state.py: Audit state tracking
- evidence_manager.py: Evidence flow management between engines
"""

from .redis_client import RedisClient, get_redis_client, init_redis
from .audit_state import AuditState, AuditStage, AuditStateManager
from .models import (
    # Enums
    EvidenceSourceType,
    ComplianceStatus,
    SeverityLevel,
    AuditMode,
    # Core models
    ComplianceEvidence,
    ClassificationResult,
    ComplianceDecision,
    AuditConfig,
    AuditSummary,
    EvidenceBatch,
    ControlDefinition,
)
from .evidence_manager import EvidenceManager, create_evidence_manager

__all__ = [
    # Redis
    "RedisClient",
    "get_redis_client",
    "init_redis",
    # Audit state
    "AuditState",
    "AuditStage",
    "AuditStateManager",
    # Enums
    "EvidenceSourceType",
    "ComplianceStatus",
    "SeverityLevel",
    "AuditMode",
    # Models
    "ComplianceEvidence",
    "ClassificationResult",
    "ComplianceDecision",
    "AuditConfig",
    "AuditSummary",
    "EvidenceBatch",
    "ControlDefinition",
    # Evidence manager
    "EvidenceManager",
    "create_evidence_manager",
]
