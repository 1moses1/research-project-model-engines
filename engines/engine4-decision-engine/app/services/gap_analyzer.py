"""
Gap Analyzer for Engine 4 (Decision Engine)
============================================

Analyzes gaps between policy claims (documents) and actual system behavior (logs)
for comprehensive compliance assessment.

Gap Types:
1. Policy-Reality Gap: Policy says compliant, logs show non-compliant
2. Unverified Policy: Control in policy but no log evidence to verify
3. Undocumented Control: Control in logs but not in policy
4. Conflicting Evidence: Multiple sources show different status
"""

from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field


class GapType(str, Enum):
    """Types of compliance gaps"""
    POLICY_REALITY_GAP = "policy_reality_gap"       # Policy says A, logs say B
    UNVERIFIED_POLICY = "unverified_policy"         # Policy exists, no log evidence
    UNDOCUMENTED_CONTROL = "undocumented_control"   # Log evidence, not in policy
    CONFLICTING_EVIDENCE = "conflicting_evidence"   # Multiple conflicting sources
    NO_GAP = "no_gap"                               # No gap detected


class GapSeverity(str, Enum):
    """Severity of detected gaps"""
    CRITICAL = "critical"   # Immediate action required
    HIGH = "high"           # Urgent attention needed
    MEDIUM = "medium"       # Should be addressed
    LOW = "low"             # Informational
    INFO = "info"           # No action required


@dataclass
class Gap:
    """Represents a detected compliance gap"""
    gap_id: str
    control_id: str
    control_name: str
    gap_type: GapType
    severity: GapSeverity
    description: str

    # Policy side
    policy_claim: str = ""
    policy_confidence: float = 0.0

    # Log side
    log_finding: str = ""
    log_confidence: float = 0.0

    # Analysis
    root_cause: str = ""
    recommendation: str = ""

    # Evidence references
    policy_evidence_ids: List[str] = field(default_factory=list)
    log_evidence_ids: List[str] = field(default_factory=list)

    detected_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "gap_id": self.gap_id,
            "control_id": self.control_id,
            "control_name": self.control_name,
            "gap_type": self.gap_type.value,
            "severity": self.severity.value,
            "description": self.description,
            "policy_claim": self.policy_claim,
            "policy_confidence": self.policy_confidence,
            "log_finding": self.log_finding,
            "log_confidence": self.log_confidence,
            "root_cause": self.root_cause,
            "recommendation": self.recommendation,
            "policy_evidence_ids": self.policy_evidence_ids,
            "log_evidence_ids": self.log_evidence_ids,
            "detected_at": self.detected_at.isoformat()
        }


class GapAnalyzer:
    """
    Analyzes gaps between document-based and log-based compliance evidence.

    The gap analyzer compares what the policy documents claim against
    what the system logs actually show, identifying discrepancies.
    """

    def __init__(self):
        self.gaps: List[Gap] = []
        self._gap_counter = 0

    def analyze_control(
        self,
        control_id: str,
        control_name: str,
        log_classifications: List[Dict[str, Any]],
        doc_classifications: List[Dict[str, Any]],
        log_evidence: List[Dict[str, Any]],
        doc_evidence: List[Dict[str, Any]]
    ) -> Optional[Gap]:
        """
        Analyze a single control for gaps between policy and reality.

        Args:
            control_id: Rwanda NCSA control ID
            control_name: Human-readable control name
            log_classifications: Classification results from log evidence
            doc_classifications: Classification results from document evidence
            log_evidence: Raw log evidence items
            doc_evidence: Raw document evidence items

        Returns:
            Gap object if gap detected, None otherwise
        """
        has_log = len(log_classifications) > 0
        has_doc = len(doc_classifications) > 0

        # Aggregate status from classifications
        log_status, log_confidence = self._aggregate_status(log_classifications)
        doc_status, doc_confidence = self._aggregate_status(doc_classifications)

        # Extract policy claims and log findings
        policy_claim = self._extract_policy_claim(doc_evidence)
        log_finding = self._extract_log_finding(log_evidence)

        # Determine gap type
        gap_type, severity, description = self._determine_gap(
            has_log=has_log,
            has_doc=has_doc,
            log_status=log_status,
            doc_status=doc_status,
            log_confidence=log_confidence,
            doc_confidence=doc_confidence
        )

        if gap_type == GapType.NO_GAP:
            return None

        # Generate root cause and recommendation
        root_cause = self._analyze_root_cause(gap_type, log_finding, policy_claim)
        recommendation = self._generate_recommendation(gap_type, control_id)

        # Create gap object
        self._gap_counter += 1
        gap = Gap(
            gap_id=f"GAP-{self._gap_counter:04d}",
            control_id=control_id,
            control_name=control_name,
            gap_type=gap_type,
            severity=severity,
            description=description,
            policy_claim=policy_claim,
            policy_confidence=doc_confidence,
            log_finding=log_finding,
            log_confidence=log_confidence,
            root_cause=root_cause,
            recommendation=recommendation,
            policy_evidence_ids=[e.get("evidence_id", "") for e in doc_evidence],
            log_evidence_ids=[e.get("evidence_id", "") for e in log_evidence]
        )

        self.gaps.append(gap)
        return gap

    def _aggregate_status(
        self,
        classifications: List[Dict[str, Any]]
    ) -> Tuple[str, float]:
        """
        Aggregate multiple classification results into single status.

        Returns:
            Tuple of (status, confidence)
        """
        if not classifications:
            return "not_assessed", 0.0

        # Count statuses
        status_counts = {
            "compliant": 0,
            "non_compliant": 0,
            "partial": 0
        }
        total_confidence = 0.0

        for cls in classifications:
            status = cls.get("prediction", cls.get("status", "unknown"))
            confidence = cls.get("confidence", 0.5)

            if status in status_counts:
                status_counts[status] += 1
            total_confidence += confidence

        avg_confidence = total_confidence / len(classifications) if classifications else 0.0

        # Determine overall status by majority
        if status_counts["non_compliant"] > status_counts["compliant"]:
            return "non_compliant", avg_confidence
        elif status_counts["compliant"] > status_counts["non_compliant"]:
            return "compliant", avg_confidence
        elif status_counts["partial"] > 0:
            return "partial", avg_confidence
        else:
            return "compliant", avg_confidence  # Default to compliant if tied

    def _determine_gap(
        self,
        has_log: bool,
        has_doc: bool,
        log_status: str,
        doc_status: str,
        log_confidence: float,
        doc_confidence: float
    ) -> Tuple[GapType, GapSeverity, str]:
        """
        Determine the type of gap based on evidence comparison.

        Returns:
            Tuple of (gap_type, severity, description)
        """
        # Case 1: Both sources available - compare them
        if has_log and has_doc:
            # Policy says compliant, logs say non-compliant
            if doc_status == "compliant" and log_status == "non_compliant":
                return (
                    GapType.POLICY_REALITY_GAP,
                    GapSeverity.CRITICAL if log_confidence > 0.8 else GapSeverity.HIGH,
                    "Policy claims compliance but system logs show non-compliance. "
                    "This indicates a gap between documented policies and actual implementation."
                )

            # Policy says compliant, logs say partial
            if doc_status == "compliant" and log_status == "partial":
                return (
                    GapType.POLICY_REALITY_GAP,
                    GapSeverity.HIGH,
                    "Policy claims full compliance but system logs show partial implementation. "
                    "Some aspects of the control may not be fully implemented."
                )

            # Both agree non-compliant (no gap, just both bad)
            if doc_status == "non_compliant" and log_status == "non_compliant":
                return (GapType.NO_GAP, GapSeverity.INFO, "")

            # Both agree compliant (good!)
            if doc_status == "compliant" and log_status == "compliant":
                return (GapType.NO_GAP, GapSeverity.INFO, "")

            # Conflicting evidence with similar confidence
            if abs(log_confidence - doc_confidence) < 0.2:
                if log_status != doc_status:
                    return (
                        GapType.CONFLICTING_EVIDENCE,
                        GapSeverity.MEDIUM,
                        f"Conflicting evidence: Policy indicates '{doc_status}' "
                        f"while logs indicate '{log_status}'. Manual review required."
                    )

        # Case 2: Only document evidence (unverified policy)
        elif has_doc and not has_log:
            if doc_status == "compliant":
                return (
                    GapType.UNVERIFIED_POLICY,
                    GapSeverity.MEDIUM,
                    "Policy claims compliance but no system log evidence found to verify. "
                    "Implementation cannot be confirmed without log evidence."
                )
            else:
                return (GapType.NO_GAP, GapSeverity.INFO, "")

        # Case 3: Only log evidence (undocumented control)
        elif has_log and not has_doc:
            return (
                GapType.UNDOCUMENTED_CONTROL,
                GapSeverity.LOW,
                "Control implementation found in logs but not documented in policy. "
                "Consider updating policy documentation to reflect actual controls."
            )

        # No gap detected
        return (GapType.NO_GAP, GapSeverity.INFO, "")

    def _extract_policy_claim(self, doc_evidence: List[Dict[str, Any]]) -> str:
        """Extract the main policy claim from document evidence."""
        if not doc_evidence:
            return "No policy documentation available"

        # Get the most relevant evidence
        for evidence in doc_evidence:
            expected = evidence.get("expected_state", "")
            if expected:
                return expected[:500]  # Limit length

            text = evidence.get("evidence_text", "")
            if text:
                return text[:500]

        return "Policy documentation exists but claim unclear"

    def _extract_log_finding(self, log_evidence: List[Dict[str, Any]]) -> str:
        """Extract the main finding from log evidence."""
        if not log_evidence:
            return "No log evidence available"

        # Get the most relevant evidence
        findings = []
        for evidence in log_evidence:
            actual = evidence.get("actual_state", "")
            if actual and actual != "State unknown":
                findings.append(actual)

            summary = evidence.get("evidence_summary", "")
            if summary:
                findings.append(summary)

        if findings:
            return "; ".join(findings[:3])  # Limit to 3 findings

        return "Log evidence exists but findings unclear"

    def _analyze_root_cause(
        self,
        gap_type: GapType,
        log_finding: str,
        policy_claim: str
    ) -> str:
        """Analyze and describe the root cause of the gap."""
        if gap_type == GapType.POLICY_REALITY_GAP:
            return (
                "Potential root causes: "
                "(1) Policy was created but never fully implemented, "
                "(2) Implementation has degraded over time, "
                "(3) Recent changes bypassed the control, "
                "(4) Policy and implementation teams are not aligned."
            )

        elif gap_type == GapType.UNVERIFIED_POLICY:
            return (
                "Potential root causes: "
                "(1) Control is implemented but not generating logs, "
                "(2) Log collection is incomplete for this control, "
                "(3) Policy exists on paper only, "
                "(4) Implementation uses different logging mechanism."
            )

        elif gap_type == GapType.UNDOCUMENTED_CONTROL:
            return (
                "Potential root causes: "
                "(1) Control was implemented ad-hoc without documentation, "
                "(2) Policy documentation is outdated, "
                "(3) Implementation team added control without formal approval, "
                "(4) Control is inherited from system defaults."
            )

        elif gap_type == GapType.CONFLICTING_EVIDENCE:
            return (
                "Potential root causes: "
                "(1) Policy document is ambiguous, "
                "(2) Partial implementation exists, "
                "(3) Evidence collection is incomplete, "
                "(4) Different interpretations of control requirements."
            )

        return "Root cause analysis not available"

    def _generate_recommendation(self, gap_type: GapType, control_id: str) -> str:
        """Generate remediation recommendation for the gap."""
        if gap_type == GapType.POLICY_REALITY_GAP:
            return (
                f"IMMEDIATE ACTION: Investigate {control_id} implementation. "
                "1) Verify current system configuration against policy requirements. "
                "2) Implement missing controls or update policy to reflect reality. "
                "3) Establish monitoring to prevent future gaps."
            )

        elif gap_type == GapType.UNVERIFIED_POLICY:
            return (
                f"VERIFICATION NEEDED: For {control_id}, "
                "1) Confirm if control is actually implemented. "
                "2) Enable logging for this control if missing. "
                "3) Collect manual evidence if automated logging not feasible. "
                "4) Update policy if control is not implemented."
            )

        elif gap_type == GapType.UNDOCUMENTED_CONTROL:
            return (
                f"DOCUMENTATION UPDATE: For {control_id}, "
                "1) Review current implementation against compliance requirements. "
                "2) If control is valid, update policy documentation. "
                "3) Ensure implementation meets Rwanda NCSA standards. "
                "4) Add to formal change management process."
            )

        elif gap_type == GapType.CONFLICTING_EVIDENCE:
            return (
                f"MANUAL REVIEW: For {control_id}, "
                "1) Have compliance officer manually review evidence. "
                "2) Clarify policy requirements if ambiguous. "
                "3) Collect additional evidence to resolve conflict. "
                "4) Document final determination with rationale."
            )

        return "No specific recommendation available"

    def get_all_gaps(self) -> List[Gap]:
        """Get all detected gaps."""
        return self.gaps

    def get_gap_summary(self) -> Dict[str, Any]:
        """Get summary of all gaps."""
        if not self.gaps:
            return {
                "total_gaps": 0,
                "by_type": {},
                "by_severity": {},
                "critical_controls": []
            }

        by_type = {}
        by_severity = {}
        critical_controls = []

        for gap in self.gaps:
            # Count by type
            type_key = gap.gap_type.value
            by_type[type_key] = by_type.get(type_key, 0) + 1

            # Count by severity
            sev_key = gap.severity.value
            by_severity[sev_key] = by_severity.get(sev_key, 0) + 1

            # Track critical gaps
            if gap.severity in [GapSeverity.CRITICAL, GapSeverity.HIGH]:
                critical_controls.append({
                    "control_id": gap.control_id,
                    "gap_type": gap.gap_type.value,
                    "severity": gap.severity.value,
                    "description": gap.description[:200]
                })

        return {
            "total_gaps": len(self.gaps),
            "by_type": by_type,
            "by_severity": by_severity,
            "critical_controls": critical_controls
        }

    def reset(self):
        """Reset the analyzer for a new audit."""
        self.gaps = []
        self._gap_counter = 0
