"""
Evidence Converter for Engine 1 (Log Collector)
================================================

Converts normalized log events to the unified ComplianceEvidence format
for consistent data flow through the engine pipeline.

This enables:
1. Unified format across all engines
2. Proper correlation with document-based evidence (Engine 2)
3. Source tracking through classification and decision
4. Gap analysis in full audits
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import hashlib

# Add shared module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))

try:
    from shared.models import (
        ComplianceEvidence,
        EvidenceSourceType,
        EvidenceBatch
    )
except ImportError:
    # Fallback for standalone operation
    from pydantic import BaseModel, Field
    from enum import Enum
    import uuid

    class EvidenceSourceType(str, Enum):
        LOG = "log"
        DOCUMENT = "document"
        CONFIG = "config"

    class ComplianceEvidence(BaseModel):
        evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
        audit_id: str
        control_id: str
        control_name: str = ""
        control_family: str = ""
        source_type: EvidenceSourceType = EvidenceSourceType.LOG
        source_file: str = ""
        source_line: Optional[int] = None
        evidence_text: str
        evidence_summary: str = ""
        expected_state: str = ""
        actual_state: str = ""
        timestamp: datetime = Field(default_factory=datetime.now)
        collected_at: datetime = Field(default_factory=datetime.now)
        confidence: float = 0.0
        relevance_score: float = 0.0
        features: Dict[str, Any] = Field(default_factory=dict)
        metadata: Dict[str, Any] = Field(default_factory=dict)

    class EvidenceBatch(BaseModel):
        batch_id: str = ""
        audit_id: str
        source_type: EvidenceSourceType = EvidenceSourceType.LOG
        evidence_items: List[ComplianceEvidence] = Field(default_factory=list)
        total_count: int = 0
        processed_count: int = 0
        failed_count: int = 0


# Control family mapping for Rwanda NCSA
CONTROL_FAMILIES = {
    "AC": "Access Control",
    "AU": "Audit and Accountability",
    "AT": "Awareness and Training",
    "CM": "Configuration Management",
    "CP": "Contingency Planning",
    "IA": "Identification and Authentication",
    "IR": "Incident Response",
    "MA": "Maintenance",
    "MP": "Media Protection",
    "PE": "Physical and Environmental Protection",
    "PL": "Planning",
    "PM": "Program Management",
    "PS": "Personnel Security",
    "RA": "Risk Assessment",
    "SA": "System and Services Acquisition",
    "SC": "System and Communications Protection",
    "SI": "System and Information Integrity",
    "SR": "Supply Chain Risk Management",
}


class EvidenceConverter:
    """
    Converts normalized log events to ComplianceEvidence format.

    Features:
    - Control ID extraction from log analysis
    - Feature extraction for ML classification
    - Evidence summarization
    - Source tracking
    """

    def __init__(self, control_taxonomy: Optional[Dict] = None):
        """
        Initialize converter with optional control taxonomy.

        Args:
            control_taxonomy: Rwanda NCSA control definitions
        """
        self.control_taxonomy = control_taxonomy or {}

    def convert_event(
        self,
        normalized_event: Dict[str, Any],
        audit_id: str,
        control_id: Optional[str] = None,
        control_info: Optional[Dict] = None
    ) -> ComplianceEvidence:
        """
        Convert a single normalized log event to ComplianceEvidence.

        Args:
            normalized_event: Normalized event from LogNormalizer
            audit_id: Parent audit ID
            control_id: Pre-identified control ID (from LLM analysis)
            control_info: Additional control metadata

        Returns:
            ComplianceEvidence instance
        """
        # Extract control info
        ctrl_id = control_id or normalized_event.get("control_id", "UNKNOWN")
        ctrl_info = control_info or {}

        # Determine control family
        family_code = ctrl_id.split("-")[0] if "-" in ctrl_id else ctrl_id[:2]
        family_name = CONTROL_FAMILIES.get(family_code, "Unknown")

        # Build evidence text
        evidence_text = normalized_event.get("log_message", normalized_event.get("raw_message", ""))

        # Build evidence summary
        evidence_summary = self._generate_summary(normalized_event)

        # Extract actual state from log
        actual_state = self._extract_actual_state(normalized_event)

        # Get expected state from taxonomy (if available)
        expected_state = ""
        if ctrl_id in self.control_taxonomy:
            expected_state = self.control_taxonomy[ctrl_id].get("expected_evidence", "")

        # Extract features for ML classification
        features = self._extract_features(normalized_event)

        # Calculate confidence based on control mapping
        confidence = normalized_event.get("control_confidence", 0.5)
        if control_info:
            confidence = control_info.get("confidence", confidence)

        # Build metadata
        metadata = {
            "event_id": normalized_event.get("event_id", ""),
            "source_type": normalized_event.get("source", ""),
            "severity": normalized_event.get("severity", "INFO"),
            "user": normalized_event.get("user"),
            "ip_address": normalized_event.get("ip_address"),
            "resource": normalized_event.get("resource"),
            "action": normalized_event.get("action"),
            "status_code": normalized_event.get("status_code"),
        }

        # Clean None values
        metadata = {k: v for k, v in metadata.items() if v is not None}

        return ComplianceEvidence(
            audit_id=audit_id,
            control_id=ctrl_id,
            control_name=ctrl_info.get("name", f"Control {ctrl_id}"),
            control_family=family_name,
            source_type=EvidenceSourceType.LOG,
            source_file=normalized_event.get("source", "system"),
            evidence_text=evidence_text,
            evidence_summary=evidence_summary,
            expected_state=expected_state,
            actual_state=actual_state,
            timestamp=self._parse_timestamp(normalized_event.get("timestamp")),
            collected_at=datetime.now(),
            confidence=confidence,
            relevance_score=self._calculate_relevance(normalized_event, ctrl_id),
            features=features,
            metadata=metadata
        )

    def convert_batch(
        self,
        normalized_events: List[Dict[str, Any]],
        audit_id: str,
        control_mappings: Optional[Dict[str, Dict]] = None
    ) -> EvidenceBatch:
        """
        Convert a batch of normalized events to EvidenceBatch.

        Args:
            normalized_events: List of normalized events
            audit_id: Parent audit ID
            control_mappings: Optional mapping of event_id -> control info

        Returns:
            EvidenceBatch instance
        """
        import uuid
        batch = EvidenceBatch(
            batch_id=str(uuid.uuid4()),
            audit_id=audit_id,
            source_type=EvidenceSourceType.LOG
        )

        control_mappings = control_mappings or {}

        for event in normalized_events:
            event_id = event.get("event_id", "")
            control_info = control_mappings.get(event_id, {})
            control_id = control_info.get("control_id")

            try:
                evidence = self.convert_event(
                    normalized_event=event,
                    audit_id=audit_id,
                    control_id=control_id,
                    control_info=control_info
                )
                batch.evidence_items.append(evidence)
            except Exception as e:
                print(f"Failed to convert event {event_id}: {e}")
                batch.failed_count += 1

        batch.total_count = len(batch.evidence_items) + batch.failed_count
        batch.processed_count = len(batch.evidence_items)

        return batch

    def _generate_summary(self, event: Dict[str, Any]) -> str:
        """Generate a brief summary of the log event."""
        action = event.get("action", "")
        user = event.get("user", "")
        resource = event.get("resource", "")
        severity = event.get("severity", "INFO")

        parts = []
        if severity:
            parts.append(f"[{severity}]")
        if action:
            parts.append(action)
        if user:
            parts.append(f"by {user}")
        if resource:
            parts.append(f"on {resource}")

        if parts:
            return " ".join(parts)

        # Fallback to truncated message
        msg = event.get("log_message", event.get("raw_message", ""))
        return msg[:100] + "..." if len(msg) > 100 else msg

    def _extract_actual_state(self, event: Dict[str, Any]) -> str:
        """Extract the actual state/outcome from the log event."""
        status_code = event.get("status_code")
        action = event.get("action", "")
        severity = event.get("severity", "")

        # Build state description
        parts = []

        if status_code:
            if status_code >= 200 and status_code < 300:
                parts.append("Operation succeeded")
            elif status_code >= 400:
                parts.append("Operation failed")

        if severity:
            if severity in ["ERROR", "CRITICAL"]:
                parts.append(f"Error severity: {severity}")
            elif severity == "WARNING":
                parts.append("Warning condition detected")

        if action:
            parts.append(f"Action: {action}")

        return "; ".join(parts) if parts else "State unknown"

    def _extract_features(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract features for XGBoost classification.

        Returns:
            Dictionary of features for ML model
        """
        msg = event.get("log_message", event.get("raw_message", ""))

        # Text-based features
        features = {
            # Message characteristics
            "message_length": len(msg),
            "word_count": len(msg.split()),
            "has_ip": 1 if event.get("ip_address") else 0,
            "has_user": 1 if event.get("user") else 0,
            "has_timestamp": 1 if event.get("timestamp") else 0,

            # Severity encoding
            "severity_level": self._encode_severity(event.get("severity", "INFO")),

            # Status code features
            "status_code": event.get("status_code", 0) or 0,
            "status_success": 1 if event.get("status_code") and 200 <= event.get("status_code", 0) < 300 else 0,
            "status_error": 1 if event.get("status_code") and event.get("status_code", 0) >= 400 else 0,

            # Security indicators
            "has_failed": 1 if "fail" in msg.lower() else 0,
            "has_denied": 1 if "denied" in msg.lower() or "deny" in msg.lower() else 0,
            "has_error": 1 if "error" in msg.lower() else 0,
            "has_success": 1 if "success" in msg.lower() else 0,
            "has_auth": 1 if "auth" in msg.lower() or "login" in msg.lower() else 0,
            "has_access": 1 if "access" in msg.lower() else 0,
            "has_admin": 1 if "admin" in msg.lower() or "root" in msg.lower() else 0,

            # Temporal features (extract from timestamp if available)
            "hour_of_day": self._extract_hour(event.get("timestamp")),
            "is_business_hours": self._is_business_hours(event.get("timestamp")),
        }

        return features

    def _encode_severity(self, severity: str) -> int:
        """Encode severity level as integer."""
        mapping = {
            "DEBUG": 0,
            "INFO": 1,
            "NOTICE": 2,
            "WARNING": 3,
            "WARN": 3,
            "ERROR": 4,
            "CRITICAL": 5,
            "ALERT": 6,
            "EMERGENCY": 7
        }
        return mapping.get(severity.upper(), 1)

    def _extract_hour(self, timestamp: Optional[str]) -> int:
        """Extract hour from timestamp."""
        if not timestamp:
            return datetime.now().hour

        try:
            if isinstance(timestamp, datetime):
                return timestamp.hour
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt.hour
        except:
            return datetime.now().hour

    def _is_business_hours(self, timestamp: Optional[str]) -> int:
        """Check if timestamp is during business hours (8-18)."""
        hour = self._extract_hour(timestamp)
        return 1 if 8 <= hour <= 18 else 0

    def _parse_timestamp(self, timestamp: Optional[str]) -> datetime:
        """Parse timestamp string to datetime."""
        if not timestamp:
            return datetime.now()

        if isinstance(timestamp, datetime):
            return timestamp

        try:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except:
            return datetime.now()

    def _calculate_relevance(self, event: Dict[str, Any], control_id: str) -> float:
        """
        Calculate relevance score for the control mapping.
        Higher score = more relevant to the control.
        """
        base_score = 0.5

        # Boost for known control patterns
        if control_id and control_id != "UNKNOWN":
            base_score = 0.7

        # Boost for security-relevant content
        msg = event.get("log_message", "").lower()
        security_keywords = ["auth", "access", "login", "permission", "security", "audit"]
        for keyword in security_keywords:
            if keyword in msg:
                base_score += 0.05

        # Cap at 1.0
        return min(base_score, 1.0)

    def set_control_taxonomy(self, taxonomy: Dict):
        """Update control taxonomy for better mapping."""
        self.control_taxonomy = taxonomy


# Singleton instance
_converter: Optional[EvidenceConverter] = None


def get_evidence_converter() -> EvidenceConverter:
    """Get or create converter singleton."""
    global _converter
    if _converter is None:
        _converter = EvidenceConverter()
    return _converter
