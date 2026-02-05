"""
Audit Service - Orchestrates the complete audit pipeline for UI integration.

This service provides:
- Audit session management
- Document association with audits
- Progress tracking with real-time updates
- Report generation coordination
"""

import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import httpx
import sys

# Add parent path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class AuditType(str, Enum):
    LOG_ANALYSIS = "log_analysis"
    DOCUMENT_ANALYSIS = "document_analysis"
    FULL_AUDIT = "full"


class AuditStatus(str, Enum):
    PENDING = "pending"
    CONFIGURING = "configuring"
    RUNNING = "running"
    ANALYZING = "analyzing"
    GENERATING_REPORT = "generating_report"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AuditConfig:
    """Configuration for an audit session"""
    audit_type: AuditType = AuditType.FULL_AUDIT
    log_sources: List[Dict] = field(default_factory=list)
    document_ids: List[str] = field(default_factory=list)
    control_families: List[str] = field(default_factory=list)
    time_range: Optional[Dict] = None
    target_host: str = "localhost"
    company_name: str = "Demo Organization"
    framework: str = "Rwanda-NCSA"

    def to_dict(self) -> Dict:
        return {
            "audit_type": self.audit_type.value if isinstance(self.audit_type, AuditType) else self.audit_type,
            "log_sources": self.log_sources,
            "document_ids": self.document_ids,
            "control_families": self.control_families,
            "time_range": self.time_range,
            "target_host": self.target_host,
            "company_name": self.company_name,
            "framework": self.framework
        }


@dataclass
class AuditSession:
    """Represents an audit session with all its state"""
    audit_id: str
    config: AuditConfig
    status: AuditStatus = AuditStatus.PENDING
    progress: int = 0
    current_stage: str = "initialized"
    message: str = "Audit session created"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    results: Optional[Dict] = None
    error: Optional[str] = None
    documents: List[Dict] = field(default_factory=list)
    log_analysis: List[Dict] = field(default_factory=list)
    document_analysis: List[Dict] = field(default_factory=list)
    control_families_breakdown: Dict = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "audit_id": self.audit_id,
            "config": self.config.to_dict() if isinstance(self.config, AuditConfig) else self.config,
            "status": self.status.value if isinstance(self.status, AuditStatus) else self.status,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "message": self.message,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "results": self.results,
            "error": self.error,
            "documents": self.documents,
            "log_analysis": self.log_analysis,
            "document_analysis": self.document_analysis,
            "control_families_breakdown": self.control_families_breakdown
        }


class AuditService:
    """
    Main audit service that orchestrates the compliance audit pipeline.
    Coordinates between Engine 1 (Logs), Engine 2 (Documents),
    Engine 3 (MCP+LLM), Engine 4 (Decisions), and Engine 5 (Reports).
    """

    def __init__(
        self,
        engine1_url: str = "http://localhost:8001",
        engine2_url: str = "http://localhost:8002",
        engine3_url: str = "http://localhost:8003",
        engine4_url: str = "http://localhost:8004",
        engine5_url: str = "http://localhost:8005"
    ):
        self.engine_urls = {
            "log_collector": engine1_url,
            "document_processor": engine2_url,
            "mcp_analyzer": engine3_url,
            "decision_engine": engine4_url,
            "report_generator": engine5_url
        }
        self.sessions: Dict[str, AuditSession] = {}
        self.update_callbacks: Dict[str, List[Callable]] = {}

    def generate_audit_id(self) -> str:
        """Generate unique audit ID"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        short_uuid = str(uuid.uuid4())[:8]
        return f"AUDIT-{timestamp}-{short_uuid}"

    async def create_session(self, config: AuditConfig) -> AuditSession:
        """Create a new audit session"""
        audit_id = self.generate_audit_id()
        session = AuditSession(
            audit_id=audit_id,
            config=config,
            status=AuditStatus.PENDING,
            started_at=datetime.now().isoformat()
        )
        self.sessions[audit_id] = session
        return session

    def get_session(self, audit_id: str) -> Optional[AuditSession]:
        """Get an audit session by ID"""
        return self.sessions.get(audit_id)

    def list_sessions(self, limit: int = 50) -> List[AuditSession]:
        """List recent audit sessions"""
        sessions = list(self.sessions.values())
        sessions.sort(key=lambda s: s.started_at or "", reverse=True)
        return sessions[:limit]

    async def update_session(
        self,
        audit_id: str,
        status: Optional[AuditStatus] = None,
        progress: Optional[int] = None,
        stage: Optional[str] = None,
        message: Optional[str] = None,
        results: Optional[Dict] = None,
        error: Optional[str] = None
    ) -> Optional[AuditSession]:
        """Update audit session state and notify callbacks"""
        session = self.sessions.get(audit_id)
        if not session:
            return None

        if status:
            session.status = status
        if progress is not None:
            session.progress = progress
        if stage:
            session.current_stage = stage
        if message:
            session.message = message
        if results:
            session.results = results
        if error:
            session.error = error
            session.status = AuditStatus.FAILED

        # Notify registered callbacks
        if audit_id in self.update_callbacks:
            for callback in self.update_callbacks[audit_id]:
                try:
                    await callback(session.to_dict())
                except Exception as e:
                    print(f"Callback error: {e}")

        return session

    def register_callback(self, audit_id: str, callback: Callable):
        """Register a callback for audit updates"""
        if audit_id not in self.update_callbacks:
            self.update_callbacks[audit_id] = []
        self.update_callbacks[audit_id].append(callback)

    def unregister_callback(self, audit_id: str, callback: Callable):
        """Unregister a callback"""
        if audit_id in self.update_callbacks:
            self.update_callbacks[audit_id] = [
                cb for cb in self.update_callbacks[audit_id] if cb != callback
            ]

    async def run_audit(
        self,
        audit_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict:
        """
        Execute the complete audit pipeline.

        Flow:
        1. Collect logs (Engine 1)
        2. Process documents (Engine 2)
        3. Analyze with MCP+LLM (Engine 3)
        4. Make decisions (Engine 4)
        5. Generate report (Engine 5)
        """
        session = self.sessions.get(audit_id)
        if not session:
            raise ValueError(f"Audit session not found: {audit_id}")

        if progress_callback:
            self.register_callback(audit_id, progress_callback)

        try:
            # Stage 1: Initialize
            await self.update_session(
                audit_id,
                status=AuditStatus.RUNNING,
                progress=5,
                stage="initializing",
                message="Initializing audit pipeline..."
            )

            config = session.config
            all_results = {
                "log_analysis": [],
                "document_analysis": [],
                "classifications": [],
                "decisions": [],
                "summary": {}
            }

            # Stage 2: Log Collection (if applicable)
            if config.audit_type in [AuditType.LOG_ANALYSIS, AuditType.FULL_AUDIT]:
                await self.update_session(
                    audit_id,
                    progress=15,
                    stage="collecting_logs",
                    message="Collecting system logs..."
                )

                log_results = await self._collect_logs(config)
                all_results["log_analysis"] = log_results
                session.log_analysis = log_results

                await self.update_session(
                    audit_id,
                    progress=30,
                    stage="logs_collected",
                    message=f"Collected {len(log_results)} log entries"
                )

            # Stage 3: Document Processing (if applicable)
            if config.audit_type in [AuditType.DOCUMENT_ANALYSIS, AuditType.FULL_AUDIT]:
                if config.document_ids:
                    await self.update_session(
                        audit_id,
                        progress=35,
                        stage="processing_documents",
                        message="Processing policy documents..."
                    )

                    doc_results = await self._process_documents(config.document_ids)
                    all_results["document_analysis"] = doc_results
                    session.document_analysis = doc_results

                    await self.update_session(
                        audit_id,
                        progress=45,
                        stage="documents_processed",
                        message=f"Processed {len(doc_results)} documents"
                    )

            # Stage 4: MCP+LLM Analysis
            await self.update_session(
                audit_id,
                progress=50,
                stage="analyzing",
                message="Analyzing compliance with MCP+LLM..."
            )

            analysis_results = await self._analyze_compliance(
                all_results["log_analysis"],
                all_results["document_analysis"],
                config
            )
            all_results["classifications"] = analysis_results

            await self.update_session(
                audit_id,
                progress=70,
                stage="analysis_complete",
                message=f"Analyzed {len(analysis_results)} items"
            )

            # Stage 5: Decision Making
            await self.update_session(
                audit_id,
                progress=75,
                stage="making_decisions",
                message="Making compliance decisions..."
            )

            decisions = await self._make_decisions(analysis_results, config)
            all_results["decisions"] = decisions

            # Calculate summary
            compliant = sum(1 for d in decisions if d.get("status") == "compliant")
            non_compliant = sum(1 for d in decisions if d.get("status") == "non_compliant")
            partial = sum(1 for d in decisions if d.get("status") == "partial")
            total = len(decisions)

            compliance_rate = (compliant / total * 100) if total > 0 else 0
            risk_level = "LOW" if compliance_rate >= 80 else "MEDIUM" if compliance_rate >= 60 else "HIGH"

            all_results["summary"] = {
                "compliance_rate": round(compliance_rate, 1),
                "risk_level": risk_level,
                "total_controls": total,
                "compliant": compliant,
                "non_compliant": non_compliant,
                "partial": partial,
                "logs_analyzed": len(all_results["log_analysis"]),
                "documents_analyzed": len(all_results["document_analysis"])
            }

            # Group by control family
            family_breakdown = {}
            for decision in decisions:
                family = decision.get("control_family", "Unknown")
                if family not in family_breakdown:
                    family_breakdown[family] = {"compliant": 0, "non_compliant": 0, "partial": 0}
                status = decision.get("status", "unknown")
                if status in family_breakdown[family]:
                    family_breakdown[family][status] += 1

            session.control_families_breakdown = family_breakdown
            all_results["control_families"] = family_breakdown

            await self.update_session(
                audit_id,
                progress=85,
                stage="decisions_complete",
                message=f"Compliance: {compliance_rate:.1f}% ({risk_level} risk)"
            )

            # Stage 6: Report Generation
            await self.update_session(
                audit_id,
                progress=90,
                stage="generating_report",
                message="Generating compliance report..."
            )

            report_info = await self._generate_report(audit_id, all_results, config)
            all_results["report"] = report_info

            # Complete
            session.completed_at = datetime.now().isoformat()
            session.results = all_results

            await self.update_session(
                audit_id,
                status=AuditStatus.COMPLETED,
                progress=100,
                stage="completed",
                message=f"Audit completed! Compliance: {compliance_rate:.1f}%",
                results=all_results
            )

            return all_results

        except Exception as e:
            await self.update_session(
                audit_id,
                status=AuditStatus.FAILED,
                stage="error",
                message=f"Audit failed: {str(e)}",
                error=str(e)
            )
            raise

    async def _collect_logs(self, config: AuditConfig) -> List[Dict]:
        """Collect logs from Engine 1 or local sources"""
        logs = []

        try:
            # Try to call Engine 1
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.engine_urls['log_collector']}/api/collect",
                    json={
                        "sources": config.log_sources,
                        "time_range": config.time_range
                    }
                )
                if response.status_code == 200:
                    logs = response.json().get("logs", [])
        except Exception as e:
            print(f"Engine 1 not available, using local log collection: {e}")
            # Fallback to local log collection
            logs = await self._collect_local_logs(config)

        return logs

    async def _collect_local_logs(self, config: AuditConfig) -> List[Dict]:
        """Collect logs locally as fallback"""
        logs = []

        # Try to load sample logs from project
        sample_log_path = Path(__file__).parent.parent.parent.parent / "datasets/real_world/linux_auth.log"
        if sample_log_path.exists():
            try:
                with open(sample_log_path, 'r') as f:
                    for i, line in enumerate(f):
                        if i >= 100:  # Limit to 100 logs
                            break
                        logs.append({
                            "id": f"log-{i}",
                            "source": "local",
                            "raw_message": line.strip(),
                            "timestamp": datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"Error reading sample logs: {e}")

        return logs

    async def _process_documents(self, document_ids: List[str]) -> List[Dict]:
        """Process documents with Engine 2"""
        doc_results = []

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                for doc_id in document_ids:
                    try:
                        response = await client.get(
                            f"{self.engine_urls['document_processor']}/api/documents/{doc_id}/analysis"
                        )
                        if response.status_code == 200:
                            doc_results.append(response.json())
                    except Exception:
                        pass
        except Exception as e:
            print(f"Engine 2 not available: {e}")

        return doc_results

    async def _analyze_compliance(
        self,
        logs: List[Dict],
        documents: List[Dict],
        config: AuditConfig
    ) -> List[Dict]:
        """Analyze with Engine 3 (MCP+LLM)"""
        results = []

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                # Analyze logs
                if logs:
                    for log in logs[:50]:  # Limit batch size
                        try:
                            response = await client.post(
                                f"{self.engine_urls['mcp_analyzer']}/api/v3/analyze",
                                json={
                                    "log_entry": log.get("raw_message", ""),
                                    "framework": config.framework
                                }
                            )
                            if response.status_code == 200:
                                result = response.json()
                                result["source_type"] = "log"
                                result["source_id"] = log.get("id")
                                results.append(result)
                        except Exception:
                            pass
        except Exception as e:
            print(f"Engine 3 not available, using rule-based analysis: {e}")
            # Fallback to simple rule-based analysis
            results = self._rule_based_analysis(logs, documents, config)

        return results

    def _rule_based_analysis(
        self,
        logs: List[Dict],
        documents: List[Dict],
        config: AuditConfig
    ) -> List[Dict]:
        """Simple rule-based analysis as fallback"""
        results = []

        # Define compliance patterns
        compliance_patterns = {
            "session opened": {"status": "compliant", "control": "AU-68", "family": "Audit and Accountability"},
            "session closed": {"status": "compliant", "control": "AU-69", "family": "Audit and Accountability"},
            "Accepted password": {"status": "compliant", "control": "IA-100", "family": "Identification and Authentication"},
            "Accepted publickey": {"status": "compliant", "control": "IA-100", "family": "Identification and Authentication"},
            "Invalid user": {"status": "non_compliant", "control": "AC-38", "family": "Access Control"},
            "Failed password": {"status": "non_compliant", "control": "AC-38", "family": "Access Control"},
            "FAILED LOGIN": {"status": "non_compliant", "control": "AC-37", "family": "Access Control"},
            "sudo": {"status": "partial", "control": "AC-6", "family": "Access Control"},
            "connection from": {"status": "compliant", "control": "SC-155", "family": "System and Communications Protection"},
        }

        for log in logs:
            message = log.get("raw_message", "")
            matched = False

            for pattern, info in compliance_patterns.items():
                if pattern.lower() in message.lower():
                    results.append({
                        "source_type": "log",
                        "source_id": log.get("id"),
                        "raw_message": message,
                        "status": info["status"],
                        "control_id": info["control"],
                        "control_family": info["family"],
                        "confidence": 0.75,
                        "analysis_method": "rule_based"
                    })
                    matched = True
                    break

            if not matched:
                results.append({
                    "source_type": "log",
                    "source_id": log.get("id"),
                    "raw_message": message,
                    "status": "unknown",
                    "control_id": "UNCLASSIFIED",
                    "control_family": "Unknown",
                    "confidence": 0.5,
                    "analysis_method": "rule_based"
                })

        return results

    async def _make_decisions(
        self,
        analysis_results: List[Dict],
        config: AuditConfig
    ) -> List[Dict]:
        """Make final compliance decisions with Engine 4"""
        decisions = []

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.engine_urls['decision_engine']}/api/v3/decide",
                    json={
                        "classifications": analysis_results,
                        "framework": config.framework
                    }
                )
                if response.status_code == 200:
                    decisions = response.json().get("decisions", [])
        except Exception as e:
            print(f"Engine 4 not available, using analysis results directly: {e}")
            # Use analysis results as decisions
            decisions = analysis_results

        return decisions

    async def _generate_report(
        self,
        audit_id: str,
        results: Dict,
        config: AuditConfig
    ) -> Dict:
        """Generate report with Engine 5"""
        report_info = {
            "audit_id": audit_id,
            "generated_at": datetime.now().isoformat(),
            "formats_available": ["json"]
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.engine_urls['report_generator']}/api/v3/generate",
                    json={
                        "audit_id": audit_id,
                        "results": results,
                        "config": config.to_dict(),
                        "format": "pdf"
                    }
                )
                if response.status_code == 200:
                    report_data = response.json()
                    report_info.update(report_data)
                    report_info["formats_available"].append("pdf")
        except Exception as e:
            print(f"Engine 5 not available: {e}")

        return report_info

    async def get_report(
        self,
        audit_id: str,
        format: str = "json"
    ) -> Optional[Dict]:
        """Get report for an audit"""
        session = self.sessions.get(audit_id)
        if not session or not session.results:
            return None

        if format == "json":
            return {
                "audit_id": audit_id,
                "format": "json",
                "data": session.to_dict()
            }
        elif format == "pdf":
            # Try to get PDF from Engine 5
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        f"{self.engine_urls['report_generator']}/api/v3/reports/{audit_id}/download"
                    )
                    if response.status_code == 200:
                        return {
                            "audit_id": audit_id,
                            "format": "pdf",
                            "content": response.content,
                            "content_type": "application/pdf"
                        }
            except Exception:
                pass

        return None

    def cancel_audit(self, audit_id: str) -> bool:
        """Cancel a running audit"""
        session = self.sessions.get(audit_id)
        if session and session.status == AuditStatus.RUNNING:
            session.status = AuditStatus.CANCELLED
            session.message = "Audit cancelled by user"
            return True
        return False


# Singleton instance
_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    """Get singleton AuditService instance"""
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditService()
    return _audit_service
