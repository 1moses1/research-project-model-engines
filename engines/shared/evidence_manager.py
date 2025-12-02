"""
Evidence Manager for Rwanda NCSA Compliance Auditor
====================================================

Manages the flow of ComplianceEvidence through the engine pipeline.
Handles caching, batching, and inter-engine communication via Redis.

Flow:
1. Engine 1/2 → create evidence → cache in Redis
2. Evidence Manager → batch evidence → send to Engine 3
3. Engine 3 → classify → return results → cache in Redis
4. Evidence Manager → aggregate → send to Engine 4
5. Engine 4 → decide → store in PostgreSQL + Redis
"""

import json
import asyncio
from datetime import datetime
from typing import Optional, Dict, List, Any
from .models import (
    ComplianceEvidence,
    ClassificationResult,
    ComplianceDecision,
    EvidenceBatch,
    AuditConfig,
    AuditSummary,
    EvidenceSourceType,
    ComplianceStatus,
    AuditMode,
    SeverityLevel
)
from .redis_client import RedisClient


class EvidenceManager:
    """
    Manages compliance evidence flow through the engine pipeline.
    Uses Redis for caching and inter-engine communication.
    """

    # Redis key patterns
    EVIDENCE_KEY = "audit:{audit_id}:evidence:{evidence_id}"
    EVIDENCE_LIST_KEY = "audit:{audit_id}:evidence:list"
    EVIDENCE_BY_SOURCE_KEY = "audit:{audit_id}:evidence:source:{source_type}"
    EVIDENCE_BY_CONTROL_KEY = "audit:{audit_id}:evidence:control:{control_id}"
    CLASSIFICATION_KEY = "audit:{audit_id}:classification:{evidence_id}"
    DECISION_KEY = "audit:{audit_id}:decision:{control_id}"
    DECISIONS_LIST_KEY = "audit:{audit_id}:decisions:list"
    CONFIG_KEY = "audit:{audit_id}:config"
    SUMMARY_KEY = "audit:{audit_id}:summary"

    # TTL for cached data (2 hours)
    DEFAULT_TTL = 7200

    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client

    # =========================================================================
    # Audit Configuration
    # =========================================================================

    async def set_audit_config(self, config: AuditConfig) -> bool:
        """Store audit configuration"""
        key = self.CONFIG_KEY.format(audit_id=config.audit_id)
        return await self.redis.set(key, config.model_dump(), ttl=self.DEFAULT_TTL)

    async def get_audit_config(self, audit_id: str) -> Optional[AuditConfig]:
        """Get audit configuration"""
        key = self.CONFIG_KEY.format(audit_id=audit_id)
        data = await self.redis.get(key)
        if data:
            return AuditConfig(**data)
        return None

    # =========================================================================
    # Evidence Storage & Retrieval
    # =========================================================================

    async def store_evidence(self, evidence: ComplianceEvidence) -> bool:
        """
        Store evidence and index it for retrieval.
        Called by Engine 1 (logs) and Engine 2 (documents).
        """
        audit_id = evidence.audit_id
        evidence_id = evidence.evidence_id

        # Store the evidence
        key = self.EVIDENCE_KEY.format(audit_id=audit_id, evidence_id=evidence_id)
        success = await self.redis.set(key, evidence.model_dump(), ttl=self.DEFAULT_TTL)

        if success:
            # Add to main evidence list
            list_key = self.EVIDENCE_LIST_KEY.format(audit_id=audit_id)
            await self._list_append(list_key, evidence_id)

            # Index by source type
            source_key = self.EVIDENCE_BY_SOURCE_KEY.format(
                audit_id=audit_id,
                source_type=evidence.source_type.value
            )
            await self._list_append(source_key, evidence_id)

            # Index by control
            control_key = self.EVIDENCE_BY_CONTROL_KEY.format(
                audit_id=audit_id,
                control_id=evidence.control_id
            )
            await self._list_append(control_key, evidence_id)

            # Publish event for real-time updates
            await self.redis.publish(
                f"audit:{audit_id}:evidence:new",
                {
                    "evidence_id": evidence_id,
                    "control_id": evidence.control_id,
                    "source_type": evidence.source_type.value,
                    "timestamp": datetime.now().isoformat()
                }
            )

        return success

    async def store_evidence_batch(self, batch: EvidenceBatch) -> Dict[str, Any]:
        """Store a batch of evidence items"""
        results = {"success": 0, "failed": 0, "evidence_ids": []}

        for evidence in batch.evidence_items:
            if await self.store_evidence(evidence):
                results["success"] += 1
                results["evidence_ids"].append(evidence.evidence_id)
            else:
                results["failed"] += 1

        batch.processed_count = results["success"]
        batch.failed_count = results["failed"]

        return results

    async def get_evidence(self, audit_id: str, evidence_id: str) -> Optional[ComplianceEvidence]:
        """Get a single evidence item"""
        key = self.EVIDENCE_KEY.format(audit_id=audit_id, evidence_id=evidence_id)
        data = await self.redis.get(key)
        if data:
            return ComplianceEvidence(**data)
        return None

    async def get_all_evidence(self, audit_id: str) -> List[ComplianceEvidence]:
        """Get all evidence for an audit"""
        list_key = self.EVIDENCE_LIST_KEY.format(audit_id=audit_id)
        evidence_ids = await self._list_get_all(list_key)

        evidence_list = []
        for eid in evidence_ids:
            evidence = await self.get_evidence(audit_id, eid)
            if evidence:
                evidence_list.append(evidence)

        return evidence_list

    async def get_evidence_by_source(
        self,
        audit_id: str,
        source_type: EvidenceSourceType
    ) -> List[ComplianceEvidence]:
        """Get evidence filtered by source type"""
        source_key = self.EVIDENCE_BY_SOURCE_KEY.format(
            audit_id=audit_id,
            source_type=source_type.value
        )
        evidence_ids = await self._list_get_all(source_key)

        evidence_list = []
        for eid in evidence_ids:
            evidence = await self.get_evidence(audit_id, eid)
            if evidence:
                evidence_list.append(evidence)

        return evidence_list

    async def get_evidence_by_control(
        self,
        audit_id: str,
        control_id: str
    ) -> List[ComplianceEvidence]:
        """Get evidence filtered by control ID"""
        control_key = self.EVIDENCE_BY_CONTROL_KEY.format(
            audit_id=audit_id,
            control_id=control_id
        )
        evidence_ids = await self._list_get_all(control_key)

        evidence_list = []
        for eid in evidence_ids:
            evidence = await self.get_evidence(audit_id, eid)
            if evidence:
                evidence_list.append(evidence)

        return evidence_list

    async def get_evidence_counts(self, audit_id: str) -> Dict[str, int]:
        """Get evidence counts by source type"""
        log_key = self.EVIDENCE_BY_SOURCE_KEY.format(
            audit_id=audit_id,
            source_type=EvidenceSourceType.LOG.value
        )
        doc_key = self.EVIDENCE_BY_SOURCE_KEY.format(
            audit_id=audit_id,
            source_type=EvidenceSourceType.DOCUMENT.value
        )

        log_count = await self._list_length(log_key)
        doc_count = await self._list_length(doc_key)

        return {
            "log": log_count,
            "document": doc_count,
            "total": log_count + doc_count
        }

    # =========================================================================
    # Classification Results (Engine 3 Output)
    # =========================================================================

    async def store_classification(self, result: ClassificationResult) -> bool:
        """Store classification result from Engine 3"""
        key = self.CLASSIFICATION_KEY.format(
            audit_id=result.audit_id,
            evidence_id=result.evidence_id
        )
        return await self.redis.set(key, result.model_dump(), ttl=self.DEFAULT_TTL)

    async def get_classification(
        self,
        audit_id: str,
        evidence_id: str
    ) -> Optional[ClassificationResult]:
        """Get classification result"""
        key = self.CLASSIFICATION_KEY.format(audit_id=audit_id, evidence_id=evidence_id)
        data = await self.redis.get(key)
        if data:
            return ClassificationResult(**data)
        return None

    async def get_classifications_for_control(
        self,
        audit_id: str,
        control_id: str
    ) -> List[ClassificationResult]:
        """Get all classifications for a control"""
        evidence_list = await self.get_evidence_by_control(audit_id, control_id)
        classifications = []

        for evidence in evidence_list:
            classification = await self.get_classification(audit_id, evidence.evidence_id)
            if classification:
                classifications.append(classification)

        return classifications

    # =========================================================================
    # Compliance Decisions (Engine 4 Output)
    # =========================================================================

    async def store_decision(self, decision: ComplianceDecision) -> bool:
        """Store compliance decision from Engine 4"""
        key = self.DECISION_KEY.format(
            audit_id=decision.audit_id,
            control_id=decision.control_id
        )
        success = await self.redis.set(key, decision.model_dump(), ttl=self.DEFAULT_TTL)

        if success:
            # Add to decisions list
            list_key = self.DECISIONS_LIST_KEY.format(audit_id=decision.audit_id)
            await self._list_append(list_key, decision.control_id)

            # Publish for real-time updates
            await self.redis.publish(
                f"audit:{decision.audit_id}:decision:new",
                {
                    "control_id": decision.control_id,
                    "status": decision.final_status.value,
                    "confidence": decision.weighted_confidence,
                    "timestamp": datetime.now().isoformat()
                }
            )

        return success

    async def get_decision(
        self,
        audit_id: str,
        control_id: str
    ) -> Optional[ComplianceDecision]:
        """Get decision for a control"""
        key = self.DECISION_KEY.format(audit_id=audit_id, control_id=control_id)
        data = await self.redis.get(key)
        if data:
            return ComplianceDecision(**data)
        return None

    async def get_all_decisions(self, audit_id: str) -> List[ComplianceDecision]:
        """Get all decisions for an audit"""
        list_key = self.DECISIONS_LIST_KEY.format(audit_id=audit_id)
        control_ids = await self._list_get_all(list_key)

        decisions = []
        for cid in control_ids:
            decision = await self.get_decision(audit_id, cid)
            if decision:
                decisions.append(decision)

        return decisions

    # =========================================================================
    # Audit Summary
    # =========================================================================

    async def store_summary(self, summary: AuditSummary) -> bool:
        """Store audit summary"""
        key = self.SUMMARY_KEY.format(audit_id=summary.audit_id)
        return await self.redis.set(key, summary.model_dump(), ttl=self.DEFAULT_TTL)

    async def get_summary(self, audit_id: str) -> Optional[AuditSummary]:
        """Get audit summary"""
        key = self.SUMMARY_KEY.format(audit_id=audit_id)
        data = await self.redis.get(key)
        if data:
            return AuditSummary(**data)
        return None

    async def compute_summary(self, audit_id: str) -> AuditSummary:
        """Compute audit summary from all decisions"""
        config = await self.get_audit_config(audit_id)
        decisions = await self.get_all_decisions(audit_id)
        evidence_counts = await self.get_evidence_counts(audit_id)

        # Determine audit mode
        has_logs = evidence_counts["log"] > 0
        has_docs = evidence_counts["document"] > 0

        if has_logs and has_docs:
            audit_mode = AuditMode.FULL_AUDIT
        elif has_logs:
            audit_mode = AuditMode.LOGS_ONLY
        else:
            audit_mode = AuditMode.DOCUMENTS_ONLY

        # Count statuses
        compliant = sum(1 for d in decisions if d.final_status == ComplianceStatus.COMPLIANT)
        non_compliant = sum(1 for d in decisions if d.final_status == ComplianceStatus.NON_COMPLIANT)
        partial = sum(1 for d in decisions if d.final_status == ComplianceStatus.PARTIAL)
        gaps = sum(1 for d in decisions if d.gap_detected)

        # Create summary
        summary = AuditSummary(
            audit_id=audit_id,
            audit_mode=audit_mode,
            framework=config.framework if config else "Rwanda-NCSA",
            target_host=config.target_host if config else "",
            target_os=config.target_os if config else "",
            started_at=datetime.now(),
            total_evidence_collected=evidence_counts["total"],
            log_evidence_count=evidence_counts["log"],
            document_evidence_count=evidence_counts["document"],
            controls_assessed=len(decisions),
            compliant_count=compliant,
            non_compliant_count=non_compliant,
            partial_count=partial,
            not_assessed_count=196 - len(decisions),  # Rwanda NCSA total
            gaps_detected=gaps,
            gap_descriptions=[d.gap_description for d in decisions if d.gap_detected],
            overall_score=0.0,
            decisions=decisions
        )

        # Compute scores
        summary.compute_score()
        summary.generate_source_description()

        # Compute family scores
        family_scores = {}
        family_counts = {}
        for d in decisions:
            family = d.control_family or "Unknown"
            if family not in family_scores:
                family_scores[family] = 0
                family_counts[family] = 0

            if d.final_status == ComplianceStatus.COMPLIANT:
                family_scores[family] += 100
            elif d.final_status == ComplianceStatus.PARTIAL:
                family_scores[family] += 50

            family_counts[family] += 1

        for family in family_scores:
            if family_counts[family] > 0:
                family_scores[family] = round(
                    family_scores[family] / family_counts[family], 1
                )

        summary.family_scores = family_scores

        # Store and return
        await self.store_summary(summary)
        return summary

    # =========================================================================
    # Pipeline Helpers
    # =========================================================================

    async def prepare_for_classification(self, audit_id: str) -> List[Dict[str, Any]]:
        """
        Prepare all evidence for Engine 3 classification.
        Returns evidence in the format expected by XGBoost.
        """
        evidence_list = await self.get_all_evidence(audit_id)

        classification_inputs = []
        for evidence in evidence_list:
            classification_inputs.append(evidence.to_classification_input())

        return classification_inputs

    async def aggregate_for_decision(
        self,
        audit_id: str,
        control_id: str
    ) -> Dict[str, Any]:
        """
        Aggregate all evidence and classifications for a control.
        Returns data ready for Engine 4 decision making.
        """
        evidence_list = await self.get_evidence_by_control(audit_id, control_id)
        classifications = await self.get_classifications_for_control(audit_id, control_id)
        config = await self.get_audit_config(audit_id)

        # Separate by source
        log_evidence = [e for e in evidence_list if e.source_type == EvidenceSourceType.LOG]
        doc_evidence = [e for e in evidence_list if e.source_type == EvidenceSourceType.DOCUMENT]

        log_classifications = [
            c for c in classifications if c.source_type == EvidenceSourceType.LOG
        ]
        doc_classifications = [
            c for c in classifications if c.source_type == EvidenceSourceType.DOCUMENT
        ]

        return {
            "audit_id": audit_id,
            "control_id": control_id,
            "config": config.model_dump() if config else {},
            "log_evidence": [e.model_dump() for e in log_evidence],
            "document_evidence": [e.model_dump() for e in doc_evidence],
            "log_classifications": [c.model_dump() for c in log_classifications],
            "document_classifications": [c.model_dump() for c in doc_classifications],
            "has_log_evidence": len(log_evidence) > 0,
            "has_document_evidence": len(doc_evidence) > 0
        }

    async def get_controls_to_decide(self, audit_id: str) -> List[str]:
        """Get list of unique control IDs that need decisions"""
        evidence_list = await self.get_all_evidence(audit_id)
        control_ids = set(e.control_id for e in evidence_list)
        return list(control_ids)

    # =========================================================================
    # Internal Helpers
    # =========================================================================

    async def _list_append(self, key: str, value: str) -> bool:
        """Append to a Redis list"""
        if not self.redis.is_connected():
            return False
        try:
            await self.redis._redis.rpush(key, value)
            await self.redis._redis.expire(key, self.DEFAULT_TTL)
            return True
        except Exception as e:
            print(f"Redis list append error: {e}")
            return False

    async def _list_get_all(self, key: str) -> List[str]:
        """Get all items from a Redis list"""
        if not self.redis.is_connected():
            return []
        try:
            items = await self.redis._redis.lrange(key, 0, -1)
            return items if items else []
        except Exception:
            return []

    async def _list_length(self, key: str) -> int:
        """Get length of a Redis list"""
        if not self.redis.is_connected():
            return 0
        try:
            return await self.redis._redis.llen(key)
        except Exception:
            return 0


# =============================================================================
# Factory Function
# =============================================================================

def create_evidence_manager(redis_client: RedisClient) -> EvidenceManager:
    """Create an EvidenceManager instance"""
    return EvidenceManager(redis_client)
