"""
Evidence Converter for Engine 2 (Document Processor)
=====================================================

Converts extracted policy controls to the unified ComplianceEvidence format
for consistent data flow through the engine pipeline.

This enables:
1. Unified format across all engines
2. Proper correlation with log-based evidence (Engine 1)
3. Source tracking through classification and decision
4. Gap analysis in full audits (policy claims vs actual logs)
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

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


# Try to import from shared module
try:
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'shared'))
    from shared.models import (
        ComplianceEvidence,
        EvidenceSourceType,
        EvidenceBatch
    )
except ImportError:
    # Fallback for standalone operation
    from pydantic import BaseModel, Field
    from enum import Enum

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
        source_type: EvidenceSourceType = EvidenceSourceType.DOCUMENT
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
        source_type: EvidenceSourceType = EvidenceSourceType.DOCUMENT
        evidence_items: List[ComplianceEvidence] = Field(default_factory=list)
        total_count: int = 0
        processed_count: int = 0
        failed_count: int = 0


class DocumentEvidenceConverter:
    """
    Converts extracted policy controls to ComplianceEvidence format.

    Features:
    - Extract policy requirements as expected_state
    - Map to Rwanda NCSA taxonomy
    - Generate ML features for classification
    - Track source document
    """

    def __init__(self, control_taxonomy: Optional[Dict] = None):
        """
        Initialize converter with optional control taxonomy.

        Args:
            control_taxonomy: Rwanda NCSA control definitions
        """
        self.control_taxonomy = control_taxonomy or {}

    def convert_extracted_control(
        self,
        extracted_control: Dict[str, Any],
        audit_id: str,
        source_file: str,
        document_metadata: Optional[Dict] = None
    ) -> ComplianceEvidence:
        """
        Convert an extracted control from LLM to ComplianceEvidence.

        Args:
            extracted_control: Control extracted by LLM (from llm_processor.py)
            audit_id: Parent audit ID
            source_file: Original document filename
            document_metadata: Additional document info

        Returns:
            ComplianceEvidence instance
        """
        document_metadata = document_metadata or {}

        # Extract control info
        control_id = extracted_control.get("control_id", "UNKNOWN")
        control_name = extracted_control.get("control_name", extracted_control.get("name", ""))

        # Determine control family from ID
        family_code = control_id.split("-")[0] if "-" in control_id else control_id[:2]
        family_name = CONTROL_FAMILIES.get(family_code, "Unknown")

        # Get requirements - this is what the policy CLAIMS
        requirements = extracted_control.get("requirements", [])
        if isinstance(requirements, list):
            requirements_text = "; ".join(requirements)
        else:
            requirements_text = str(requirements)

        # The evidence text is the extracted content from the document
        evidence_text = extracted_control.get("description", "")
        if not evidence_text and requirements_text:
            evidence_text = requirements_text

        # Build expected state from policy requirements
        # This is what the organization CLAIMS to do
        expected_state = self._build_expected_state(extracted_control)

        # For document evidence, actual_state is initially empty
        # It will be filled by comparing with log evidence in Engine 4
        actual_state = "Verification required from system logs"

        # Generate evidence summary
        evidence_summary = self._generate_summary(extracted_control, source_file)

        # Extract confidence from LLM extraction
        confidence = extracted_control.get("confidence", 0.0)
        if isinstance(confidence, str):
            try:
                confidence = float(confidence)
            except ValueError:
                confidence = 0.5

        # Extract features for ML classification
        features = self._extract_features(extracted_control, evidence_text)

        # Build metadata
        metadata = {
            "source_document": source_file,
            "document_type": document_metadata.get("type", "unknown"),
            "page_number": extracted_control.get("page", None),
            "section": extracted_control.get("section", ""),
            "llm_extracted": True,
            "extraction_method": extracted_control.get("extraction_method", "gpt-4"),
            "mapped_controls": extracted_control.get("mapped_rwanda_controls", []),
        }

        # Clean None values
        metadata = {k: v for k, v in metadata.items() if v is not None}

        return ComplianceEvidence(
            audit_id=audit_id,
            control_id=control_id,
            control_name=control_name,
            control_family=family_name,
            source_type=EvidenceSourceType.DOCUMENT,
            source_file=source_file,
            source_line=extracted_control.get("line_number"),
            evidence_text=evidence_text,
            evidence_summary=evidence_summary,
            expected_state=expected_state,
            actual_state=actual_state,
            timestamp=datetime.now(),
            collected_at=datetime.now(),
            confidence=confidence,
            relevance_score=self._calculate_relevance(extracted_control),
            features=features,
            metadata=metadata
        )

    def convert_batch(
        self,
        extracted_controls: List[Dict[str, Any]],
        audit_id: str,
        source_file: str,
        document_metadata: Optional[Dict] = None
    ) -> EvidenceBatch:
        """
        Convert a batch of extracted controls to EvidenceBatch.

        Args:
            extracted_controls: List of controls from LLM extraction
            audit_id: Parent audit ID
            source_file: Source document filename
            document_metadata: Additional document info

        Returns:
            EvidenceBatch instance
        """
        batch = EvidenceBatch(
            batch_id=str(uuid.uuid4()),
            audit_id=audit_id,
            source_type=EvidenceSourceType.DOCUMENT
        )

        for control in extracted_controls:
            try:
                evidence = self.convert_extracted_control(
                    extracted_control=control,
                    audit_id=audit_id,
                    source_file=source_file,
                    document_metadata=document_metadata
                )
                batch.evidence_items.append(evidence)
            except Exception as e:
                print(f"Failed to convert control {control.get('control_id', 'unknown')}: {e}")
                batch.failed_count += 1

        batch.total_count = len(batch.evidence_items) + batch.failed_count
        batch.processed_count = len(batch.evidence_items)

        return batch

    def _build_expected_state(self, control: Dict[str, Any]) -> str:
        """
        Build expected state description from policy requirements.
        This describes what SHOULD be true if compliant.
        """
        parts = []

        # Add requirements
        requirements = control.get("requirements", [])
        if requirements:
            if isinstance(requirements, list):
                for req in requirements[:3]:  # Limit to 3 requirements
                    parts.append(f"- {req}")
            else:
                parts.append(f"- {requirements}")

        # Add implementation guidance if available
        implementation = control.get("implementation", "")
        if implementation:
            parts.append(f"Implementation: {implementation}")

        # Add expected log indicators
        log_indicators = control.get("expected_logs", control.get("log_patterns", []))
        if log_indicators:
            parts.append("Expected log evidence:")
            if isinstance(log_indicators, list):
                for indicator in log_indicators[:2]:
                    parts.append(f"  • {indicator}")
            else:
                parts.append(f"  • {log_indicators}")

        if parts:
            return "\n".join(parts)

        # Fallback to description
        return control.get("description", "Policy compliance expected")

    def _generate_summary(self, control: Dict[str, Any], source_file: str) -> str:
        """Generate a brief summary of the policy evidence."""
        control_id = control.get("control_id", "Unknown")
        control_name = control.get("control_name", control.get("name", ""))

        summary_parts = [f"[POLICY] {control_id}"]

        if control_name:
            summary_parts.append(f"- {control_name}")

        summary_parts.append(f"from {source_file}")

        # Add requirement count
        requirements = control.get("requirements", [])
        if isinstance(requirements, list) and requirements:
            summary_parts.append(f"({len(requirements)} requirements)")

        return " ".join(summary_parts)

    def _extract_features(self, control: Dict[str, Any], evidence_text: str) -> Dict[str, Any]:
        """
        Extract features for XGBoost classification.
        Document features focus on policy content analysis.
        """
        features = {
            # Text characteristics
            "text_length": len(evidence_text),
            "word_count": len(evidence_text.split()),

            # Requirement characteristics
            "requirement_count": len(control.get("requirements", [])),
            "has_implementation": 1 if control.get("implementation") else 0,
            "has_verification": 1 if control.get("verification") or control.get("expected_logs") else 0,

            # Confidence from LLM
            "extraction_confidence": control.get("confidence", 0.5),

            # Policy language indicators
            "has_must": 1 if "must" in evidence_text.lower() else 0,
            "has_shall": 1 if "shall" in evidence_text.lower() else 0,
            "has_should": 1 if "should" in evidence_text.lower() else 0,
            "has_required": 1 if "required" in evidence_text.lower() else 0,

            # Security keywords
            "has_auth": 1 if "auth" in evidence_text.lower() else 0,
            "has_encrypt": 1 if "encrypt" in evidence_text.lower() else 0,
            "has_access": 1 if "access" in evidence_text.lower() else 0,
            "has_audit": 1 if "audit" in evidence_text.lower() else 0,
            "has_monitor": 1 if "monitor" in evidence_text.lower() else 0,

            # Source type indicator (for ML)
            "is_document_evidence": 1,
            "is_log_evidence": 0,
        }

        return features

    def _calculate_relevance(self, control: Dict[str, Any]) -> float:
        """
        Calculate relevance score for the control.
        Higher score = more relevant/complete extraction.
        """
        base_score = 0.5

        # Boost for complete extractions
        if control.get("control_id") and control.get("control_id") != "UNKNOWN":
            base_score += 0.1

        if control.get("requirements"):
            base_score += 0.1

        if control.get("description"):
            base_score += 0.1

        if control.get("confidence", 0) > 0.7:
            base_score += 0.1

        # Boost for mapped controls
        if control.get("mapped_rwanda_controls"):
            base_score += 0.1

        return min(base_score, 1.0)

    def set_control_taxonomy(self, taxonomy: Dict):
        """Update control taxonomy for better mapping."""
        self.control_taxonomy = taxonomy


# Singleton instance
_converter: Optional[DocumentEvidenceConverter] = None


def get_document_evidence_converter() -> DocumentEvidenceConverter:
    """Get or create converter singleton."""
    global _converter
    if _converter is None:
        _converter = DocumentEvidenceConverter()
    return _converter
