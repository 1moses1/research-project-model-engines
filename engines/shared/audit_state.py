"""
Audit State Manager for Rwanda NCSA Compliance Auditor
Tracks audit progress through the engine pipeline for real-time visibility
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Dict, List, Any


class AuditStage(str, Enum):
    """Audit stages in the compliance workflow"""

    # Stage 0: Initialization
    INITIALIZED = "initialized"

    # Stage 1: Authentication (ENGINE 7)
    AUTHENTICATING = "authenticating"
    AUTHENTICATED = "authenticated"
    AUTH_FAILED = "auth_failed"

    # Stage 2: Log Collection (ENGINE 1)
    COLLECTING_LOGS = "collecting_logs"
    LOGS_COLLECTED = "logs_collected"
    LOG_COLLECTION_FAILED = "log_collection_failed"

    # Stage 3: Document Processing (ENGINE 2) - Optional
    PROCESSING_DOCUMENTS = "processing_documents"
    DOCUMENTS_PROCESSED = "documents_processed"

    # Stage 4: Classification (ENGINE 3)
    CLASSIFYING = "classifying"
    CLASSIFIED = "classified"
    CLASSIFICATION_FAILED = "classification_failed"

    # Stage 5: Decision Making (ENGINE 4)
    MAKING_DECISIONS = "making_decisions"
    DECISIONS_MADE = "decisions_made"
    DECISION_FAILED = "decision_failed"

    # Stage 6: Report Generation (ENGINE 5)
    GENERATING_REPORT = "generating_report"
    REPORT_GENERATED = "report_generated"
    REPORT_FAILED = "report_failed"

    # Final stages
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Progress percentages for each stage
STAGE_PROGRESS = {
    AuditStage.INITIALIZED: 0,
    AuditStage.AUTHENTICATING: 5,
    AuditStage.AUTHENTICATED: 10,
    AuditStage.AUTH_FAILED: 10,
    AuditStage.COLLECTING_LOGS: 15,
    AuditStage.LOGS_COLLECTED: 30,
    AuditStage.LOG_COLLECTION_FAILED: 30,
    AuditStage.PROCESSING_DOCUMENTS: 35,
    AuditStage.DOCUMENTS_PROCESSED: 45,
    AuditStage.CLASSIFYING: 50,
    AuditStage.CLASSIFIED: 65,
    AuditStage.CLASSIFICATION_FAILED: 65,
    AuditStage.MAKING_DECISIONS: 70,
    AuditStage.DECISIONS_MADE: 85,
    AuditStage.DECISION_FAILED: 85,
    AuditStage.GENERATING_REPORT: 90,
    AuditStage.REPORT_GENERATED: 98,
    AuditStage.REPORT_FAILED: 98,
    AuditStage.COMPLETED: 100,
    AuditStage.FAILED: 100,
    AuditStage.CANCELLED: 100,
}


# Human-readable stage descriptions
STAGE_DESCRIPTIONS = {
    AuditStage.INITIALIZED: "Audit initialized",
    AuditStage.AUTHENTICATING: "Authenticating to target system...",
    AuditStage.AUTHENTICATED: "Successfully authenticated",
    AuditStage.AUTH_FAILED: "Authentication failed",
    AuditStage.COLLECTING_LOGS: "Collecting audit logs from target...",
    AuditStage.LOGS_COLLECTED: "Logs collected successfully",
    AuditStage.LOG_COLLECTION_FAILED: "Log collection failed",
    AuditStage.PROCESSING_DOCUMENTS: "Processing policy documents...",
    AuditStage.DOCUMENTS_PROCESSED: "Documents processed",
    AuditStage.CLASSIFYING: "Classifying logs to NCSA controls...",
    AuditStage.CLASSIFIED: "Classification complete",
    AuditStage.CLASSIFICATION_FAILED: "Classification failed",
    AuditStage.MAKING_DECISIONS: "Making compliance decisions...",
    AuditStage.DECISIONS_MADE: "Compliance decisions made",
    AuditStage.DECISION_FAILED: "Decision making failed",
    AuditStage.GENERATING_REPORT: "Generating compliance report...",
    AuditStage.REPORT_GENERATED: "Report generated",
    AuditStage.REPORT_FAILED: "Report generation failed",
    AuditStage.COMPLETED: "Audit completed successfully",
    AuditStage.FAILED: "Audit failed",
    AuditStage.CANCELLED: "Audit cancelled",
}


@dataclass
class AuditState:
    """
    Represents the complete state of an audit
    Used for Redis storage and WebSocket broadcasting
    """

    audit_id: str
    stage: AuditStage = AuditStage.INITIALIZED
    progress: int = 0
    message: str = ""

    # Target information
    target_host: str = ""
    target_os: str = ""
    target_user: str = ""

    # Framework info
    framework: str = "Rwanda-NCSA"
    total_controls: int = 196

    # Timestamps
    started_at: str = ""
    updated_at: str = ""
    completed_at: Optional[str] = None

    # Results summary
    logs_collected: int = 0
    controls_assessed: int = 0
    compliant_count: int = 0
    non_compliant_count: int = 0
    partial_count: int = 0
    overall_score: float = 0.0

    # Current engine
    current_engine: str = ""

    # Error information
    error: Optional[str] = None

    # Stage history
    history: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now().isoformat()
        if not self.message:
            self.message = STAGE_DESCRIPTIONS.get(self.stage, "")
        if not self.progress:
            self.progress = STAGE_PROGRESS.get(self.stage, 0)

    def update_stage(
        self,
        stage: AuditStage,
        engine: str = "",
        message: Optional[str] = None,
        details: Optional[Dict] = None
    ):
        """Update the audit stage"""
        self.stage = stage
        self.progress = STAGE_PROGRESS.get(stage, self.progress)
        self.message = message or STAGE_DESCRIPTIONS.get(stage, "")
        self.updated_at = datetime.now().isoformat()

        if engine:
            self.current_engine = engine

        # Add to history
        history_entry = {
            "stage": stage.value,
            "progress": self.progress,
            "message": self.message,
            "engine": self.current_engine,
            "timestamp": self.updated_at
        }
        if details:
            history_entry["details"] = details
        self.history.append(history_entry)

        # Mark completion
        if stage in [AuditStage.COMPLETED, AuditStage.FAILED, AuditStage.CANCELLED]:
            self.completed_at = self.updated_at

    def set_results(
        self,
        logs_collected: int = 0,
        controls_assessed: int = 0,
        compliant: int = 0,
        non_compliant: int = 0,
        partial: int = 0
    ):
        """Set the audit results"""
        self.logs_collected = logs_collected
        self.controls_assessed = controls_assessed
        self.compliant_count = compliant
        self.non_compliant_count = non_compliant
        self.partial_count = partial

        # Calculate overall score
        if controls_assessed > 0:
            self.overall_score = round(
                (compliant * 100 + partial * 50) / controls_assessed, 1
            )

    def set_error(self, error: str):
        """Set an error and mark as failed"""
        self.error = error
        self.update_stage(AuditStage.FAILED, message=f"Error: {error}")

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "audit_id": self.audit_id,
            "stage": self.stage.value,
            "progress": self.progress,
            "message": self.message,
            "target": {
                "host": self.target_host,
                "os": self.target_os,
                "user": self.target_user
            },
            "framework": self.framework,
            "total_controls": self.total_controls,
            "timestamps": {
                "started_at": self.started_at,
                "updated_at": self.updated_at,
                "completed_at": self.completed_at
            },
            "results": {
                "logs_collected": self.logs_collected,
                "controls_assessed": self.controls_assessed,
                "compliant": self.compliant_count,
                "non_compliant": self.non_compliant_count,
                "partial": self.partial_count,
                "overall_score": self.overall_score
            },
            "current_engine": self.current_engine,
            "error": self.error,
            "history": self.history
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AuditState":
        """Create from dictionary"""
        state = cls(audit_id=data.get("audit_id", ""))

        if "stage" in data:
            try:
                state.stage = AuditStage(data["stage"])
            except ValueError:
                state.stage = AuditStage.INITIALIZED

        state.progress = data.get("progress", 0)
        state.message = data.get("message", "")

        target = data.get("target", {})
        state.target_host = target.get("host", "")
        state.target_os = target.get("os", "")
        state.target_user = target.get("user", "")

        state.framework = data.get("framework", "Rwanda-NCSA")
        state.total_controls = data.get("total_controls", 196)

        timestamps = data.get("timestamps", {})
        state.started_at = timestamps.get("started_at", "")
        state.updated_at = timestamps.get("updated_at", "")
        state.completed_at = timestamps.get("completed_at")

        results = data.get("results", {})
        state.logs_collected = results.get("logs_collected", 0)
        state.controls_assessed = results.get("controls_assessed", 0)
        state.compliant_count = results.get("compliant", 0)
        state.non_compliant_count = results.get("non_compliant", 0)
        state.partial_count = results.get("partial", 0)
        state.overall_score = results.get("overall_score", 0.0)

        state.current_engine = data.get("current_engine", "")
        state.error = data.get("error")
        state.history = data.get("history", [])

        return state


class AuditStateManager:
    """
    Manages audit state with Redis backend
    Provides methods for updating state and publishing to WebSocket clients
    """

    def __init__(self, redis_client):
        self.redis = redis_client
        self._active_audits: Dict[str, AuditState] = {}

    async def create_audit(
        self,
        audit_id: str,
        target_host: str,
        target_os: str = "",
        target_user: str = "",
        framework: str = "Rwanda-NCSA"
    ) -> AuditState:
        """Create a new audit and store in Redis"""
        state = AuditState(
            audit_id=audit_id,
            target_host=target_host,
            target_os=target_os,
            target_user=target_user,
            framework=framework
        )

        self._active_audits[audit_id] = state
        await self._persist_state(state)
        await self._publish_update(state)

        return state

    async def update_stage(
        self,
        audit_id: str,
        stage: AuditStage,
        engine: str = "",
        message: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> Optional[AuditState]:
        """Update audit stage and broadcast"""
        state = await self.get_audit(audit_id)
        if not state:
            return None

        state.update_stage(stage, engine, message, details)
        await self._persist_state(state)
        await self._publish_update(state)

        return state

    async def set_results(
        self,
        audit_id: str,
        logs_collected: int = 0,
        controls_assessed: int = 0,
        compliant: int = 0,
        non_compliant: int = 0,
        partial: int = 0
    ) -> Optional[AuditState]:
        """Set audit results"""
        state = await self.get_audit(audit_id)
        if not state:
            return None

        state.set_results(logs_collected, controls_assessed, compliant, non_compliant, partial)
        await self._persist_state(state)
        await self._publish_update(state)

        return state

    async def get_audit(self, audit_id: str) -> Optional[AuditState]:
        """Get audit state from cache or Redis"""
        # Check local cache
        if audit_id in self._active_audits:
            return self._active_audits[audit_id]

        # Load from Redis
        data = await self.redis.get(f"audit:{audit_id}:state")
        if data:
            state = AuditState.from_dict(data)
            self._active_audits[audit_id] = state
            return state

        return None

    async def list_active_audits(self) -> List[Dict]:
        """List all active audits"""
        return [state.to_dict() for state in self._active_audits.values()]

    async def _persist_state(self, state: AuditState):
        """Persist state to Redis"""
        await self.redis.set(
            f"audit:{state.audit_id}:state",
            state.to_dict(),
            ttl=7200  # 2 hour TTL
        )

    async def _publish_update(self, state: AuditState):
        """Publish state update for WebSocket clients"""
        await self.redis.publish(
            f"audit:{state.audit_id}:updates",
            state.to_dict()
        )
        # Also publish to global channel for dashboard
        await self.redis.publish(
            "audit:global:updates",
            state.to_dict()
        )
