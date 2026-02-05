"""
ENGINE 4: Decision & Scoring Engine
Rwanda NCSA Compliance Auditor v3.0.0

Orchestrates compliance scoring, risk assessment, and continuous learning.
Consumes ENGINE 3 predictions and produces aggregated compliance scores.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio
import httpx
from enum import Enum
import os
import sys
from pathlib import Path

from app.services.scoring import ComplianceScorer
from app.services.risk import RiskAssessor
from app.services.learning import ContinuousLearner
from app.services.database import DatabaseService
from app.services.gap_analyzer import GapAnalyzer, GapType, GapSeverity

# Import shared models for unified pipeline
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared'))
try:
    from shared import (
        RedisClient, get_redis_client, init_redis,
        ComplianceEvidence, EvidenceSourceType,
        ClassificationResult as SharedClassificationResult,
        ComplianceDecision, ComplianceStatus,
        EvidenceManager, create_evidence_manager
    )
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False
    print("⚠️ Shared module not available - running in standalone mode")

# Initialize FastAPI app
app = FastAPI(
    title="Rwanda NCSA Decision & Scoring Engine",
    version="3.0.0",
    description="ENGINE 4: Orchestrates compliance scoring, risk assessment, and continuous learning"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
scorer = None
risk_assessor = None
learner = None
db_service = None
gap_analyzer = None
evidence_manager = None

# Configuration
ENGINE3_URL = os.getenv("ENGINE3_URL", "http://mcp-analyzer:8000")  # Updated for MCP+LLM Engine 3
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class LogEvent(BaseModel):
    """Log event for processing"""
    event_id: Optional[str] = None
    log_message: str
    status_code: Optional[int] = 200
    hour_of_day: Optional[int] = 12
    port: Optional[int] = 443
    user_id: Optional[str] = None
    resource: Optional[str] = None
    source_ip: Optional[str] = None
    timestamp: Optional[str] = None


class ControlInfo(BaseModel):
    """NCSA Control information from MCP Analyzer"""
    control_id: Optional[str] = None
    control_name: Optional[str] = None
    control_family: Optional[str] = None
    compliance_status: Optional[str] = None
    confidence: Optional[float] = None
    relevance: Optional[float] = None


class ClassificationResult(BaseModel):
    """Result from ENGINE 3 (MCP+LLM Analyzer) classification"""
    event_id: str
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    timestamp: str
    route_decision: str
    needs_human_review: bool

    # Enhanced MCP+LLM fields
    primary_control: Optional[ControlInfo] = None
    secondary_controls: Optional[List[ControlInfo]] = None
    reasoning: Optional[str] = None
    evidence_indicators: Optional[List[str]] = None
    risk_indicators: Optional[List[str]] = None
    recommended_actions: Optional[List[str]] = None
    model_used: Optional[str] = None


class ComplianceScoreResponse(BaseModel):
    """Compliance score for a control family"""
    family: str
    compliant_events: int
    total_events: int
    compliance_percentage: float
    risk_level: str


class RiskScoreResponse(BaseModel):
    """Risk assessment result"""
    event_id: str
    risk_score: float
    risk_level: str
    severity: str
    likelihood: float
    business_impact: float


class FeedbackRequest(BaseModel):
    """Human feedback for continuous learning"""
    event_id: str
    predicted_label: str
    correct_label: str
    reviewer: str
    notes: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global scorer, risk_assessor, learner, db_service, gap_analyzer, evidence_manager

    print("=" * 80)
    print("ENGINE 4: Decision & Scoring Engine - Starting Up")
    print("=" * 80)

    # Initialize services
    scorer = ComplianceScorer()
    risk_assessor = RiskAssessor()
    learner = ContinuousLearner()
    db_service = DatabaseService()

    await db_service.initialize()

    # Initialize unified pipeline components
    if SHARED_AVAILABLE:
        try:
            print("\n🔄 Initializing unified pipeline components...")

            # Initialize Redis connection
            redis_client = await init_redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=0
            )

            # Initialize Evidence Manager
            evidence_manager = create_evidence_manager(redis_client)

            # Initialize Gap Analyzer
            gap_analyzer = GapAnalyzer()

            print("✅ Redis connected and Evidence Manager initialized")
            print("✅ Gap Analyzer initialized for policy-reality comparison")
            print("📊 Unified pipeline: ACTIVE (Logs + Documents with Gap Analysis)")
        except Exception as e:
            print(f"⚠️ Failed to initialize unified pipeline: {e}")
            print("⚠️ Running in standalone mode (legacy decision engine only)")
            gap_analyzer = None
            evidence_manager = None
    else:
        print("\n⚠️ Shared module not available - running in standalone mode")

    print("\n✅ All services initialized")
    print("=" * 80)
    print("✅ ENGINE 4 READY - Decision & Scoring Engine Online")
    print("=" * 80)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "ENGINE 4: Decision & Scoring Engine",
        "version": "3.0.0",
        "status": "running",
        "capabilities": [
            "Compliance Scoring",
            "Risk Assessment",
            "Confidence Routing",
            "Continuous Learning",
            "Control Family Aggregation"
        ]
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "scorer_ready": scorer is not None,
        "risk_assessor_ready": risk_assessor is not None,
        "learner_ready": learner is not None,
        "database_ready": db_service is not None and await db_service.is_healthy(),
        "engine3_connection": await check_engine3_connection(),
        "timestamp": datetime.utcnow().isoformat()
    }


async def check_engine3_connection() -> bool:
    """Check if ENGINE 3 is reachable"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{ENGINE3_URL}/health", timeout=5.0)
            return response.status_code == 200
    except Exception:
        return False


@app.post("/process/event", response_model=ClassificationResult)
async def process_single_event(event: LogEvent, background_tasks: BackgroundTasks):
    """
    Process a single log event through the complete pipeline:
    1. Call ENGINE 3 (MCP+LLM Analyzer) for classification
    2. Apply confidence routing
    3. Calculate risk score
    4. Store in database
    5. Update compliance scores
    """
    try:
        # Generate event ID if not provided
        if not event.event_id:
            event.event_id = f"evt_{datetime.utcnow().timestamp()}"

        # Step 1: Call ENGINE 3 (MCP+LLM Analyzer) for classification
        async with httpx.AsyncClient() as client:
            classify_response = await client.post(
                f"{ENGINE3_URL}/classify",
                json={
                    "log_message": event.log_message,
                    "status_code": event.status_code,
                    "hour_of_day": event.hour_of_day,
                    "port": event.port,
                    "context": {
                        "user_id": event.user_id,
                        "resource": event.resource,
                        "source_ip": event.source_ip
                    },
                    "include_reasoning": True
                },
                timeout=15.0  # Increased timeout for LLM analysis
            )
            classify_response.raise_for_status()
            classification = classify_response.json()

        # Step 2: Apply confidence routing
        confidence = classification.get('confidence', 0.5)
        prediction = classification.get('prediction', 'unknown')

        # Extract MCP+LLM enhanced data
        primary_control = classification.get('primary_control', {})
        reasoning = classification.get('reasoning')
        risk_indicators = classification.get('risk_indicators', [])

        # Determine route decision based on confidence and risk
        if confidence >= 0.90:
            if prediction == 'compliant':
                route_decision = "auto_accept"
                needs_review = False
            else:  # non-compliant with high confidence
                route_decision = "flag_for_review"
                needs_review = True
        elif confidence >= 0.70:
            # Medium confidence - check for risk indicators
            if risk_indicators:
                route_decision = "flag_for_review"
                needs_review = True
            else:
                route_decision = "queue_for_verification"
                needs_review = True
        else:  # Low confidence
            route_decision = "queue_for_verification"
            needs_review = True

        # Step 3: Calculate risk score (background task)
        background_tasks.add_task(
            calculate_and_store_risk,
            event.event_id,
            prediction,
            confidence,
            event.status_code or 200
        )

        # Step 4: Store classification result with enhanced data
        await db_service.store_classification(
            event_id=event.event_id,
            log_message=event.log_message,
            prediction=prediction,
            confidence=confidence,
            route_decision=route_decision,
            timestamp=datetime.utcnow().isoformat(),
            # Enhanced MCP data
            control_id=primary_control.get('control_id'),
            control_name=primary_control.get('control_name'),
            reasoning=reasoning,
            model_used=classification.get('model_used')
        )

        # Step 5: Update compliance scores (background)
        background_tasks.add_task(scorer.update_scores, prediction)

        # Build response with MCP+LLM enhanced data
        return ClassificationResult(
            event_id=event.event_id,
            prediction=prediction,
            confidence=confidence,
            probabilities=classification.get('probabilities', {'compliant': 0.5, 'non_compliant': 0.5}),
            timestamp=classification.get('timestamp', datetime.utcnow().isoformat()),
            route_decision=route_decision,
            needs_human_review=needs_review,
            # Enhanced MCP+LLM fields
            primary_control=ControlInfo(**primary_control) if primary_control else None,
            secondary_controls=[ControlInfo(**c) for c in classification.get('secondary_controls', [])],
            reasoning=reasoning,
            evidence_indicators=classification.get('evidence_indicators', []),
            risk_indicators=risk_indicators,
            recommended_actions=classification.get('recommended_actions', []),
            model_used=classification.get('model_used')
        )

    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"ENGINE 3 (MCP Analyzer) connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/process/batch")
async def process_batch_events(events: List[LogEvent], background_tasks: BackgroundTasks):
    """
    Process multiple events in batch through MCP+LLM Analyzer
    """
    try:
        # Prepare batch for ENGINE 3 (MCP+LLM format)
        log_entries = []
        for e in events:
            log_entries.append({
                "log_message": e.log_message,
                "status_code": e.status_code,
                "hour_of_day": e.hour_of_day,
                "port": e.port,
                "timestamp": e.timestamp,
                "source_ip": e.source_ip,
                "user_id": e.user_id,
                "resource": e.resource
            })

        # Call ENGINE 3 batch endpoint (MCP+LLM format)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ENGINE3_URL}/classify/batch",
                json={
                    "logs": log_entries,
                    "include_reasoning": True,
                    "include_recommendations": True
                },
                timeout=60.0  # Increased timeout for LLM batch processing
            )
            response.raise_for_status()
            batch_results = response.json()

        # Get results from new format (uses 'results' instead of 'predictions')
        classification_results = batch_results.get('results', batch_results.get('predictions', []))

        # Process each result
        results = []
        for i, (event, prediction_result) in enumerate(zip(events, classification_results)):
            event_id = event.event_id or f"evt_batch_{i}_{datetime.utcnow().timestamp()}"

            confidence = prediction_result.get('confidence', 0.5)
            prediction = prediction_result.get('prediction', 'unknown')
            primary_control = prediction_result.get('primary_control', {})
            risk_indicators = prediction_result.get('risk_indicators', [])

            # Apply routing logic with risk awareness
            if confidence >= 0.90:
                route_decision = "auto_accept" if prediction == 'compliant' else "flag_for_review"
                needs_review = prediction != 'compliant'
            elif confidence >= 0.70 and risk_indicators:
                route_decision = "flag_for_review"
                needs_review = True
            else:
                route_decision = "queue_for_verification"
                needs_review = True

            # Store result with enhanced MCP data
            await db_service.store_classification(
                event_id=event_id,
                log_message=event.log_message,
                prediction=prediction,
                confidence=confidence,
                route_decision=route_decision,
                timestamp=datetime.utcnow().isoformat(),
                control_id=primary_control.get('control_id'),
                control_name=primary_control.get('control_name'),
                reasoning=prediction_result.get('reasoning'),
                model_used=prediction_result.get('model_used')
            )

            results.append({
                "event_id": event_id,
                "prediction": prediction,
                "confidence": confidence,
                "route_decision": route_decision,
                "needs_human_review": needs_review,
                "primary_control": primary_control,
                "reasoning": prediction_result.get('reasoning'),
                "model_used": prediction_result.get('model_used')
            })

        # Update scores in background
        for result in classification_results:
            background_tasks.add_task(scorer.update_scores, result.get('prediction', 'unknown'))

        return {
            "total_processed": len(results),
            "results": results,
            "compliant_count": batch_results.get('compliant_count', 0),
            "non_compliant_count": batch_results.get('non_compliant_count', 0),
            "average_confidence": batch_results.get('average_confidence', 0),
            "total_latency_ms": batch_results.get('total_latency_ms', 0),
            "model_used": batch_results.get('model_used', 'unknown')
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")


@app.get("/scores/compliance", response_model=List[ComplianceScoreResponse])
async def get_compliance_scores():
    """
    Get compliance scores aggregated by control family
    """
    scores = await scorer.get_family_scores()
    return scores


@app.get("/scores/overall")
async def get_overall_compliance():
    """
    Get overall compliance percentage
    """
    overall = await scorer.get_overall_score()
    return {
        "overall_compliance_percentage": overall['percentage'],
        "total_events": overall['total'],
        "compliant_events": overall['compliant'],
        "non_compliant_events": overall['non_compliant'],
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/risk/events")
async def get_high_risk_events(limit: int = 10):
    """
    Get top high-risk events
    """
    high_risk = await db_service.get_high_risk_events(limit)
    return {
        "high_risk_events": high_risk,
        "count": len(high_risk)
    }


@app.post("/feedback/submit")
async def submit_feedback(feedback: FeedbackRequest):
    """
    Submit human feedback for continuous learning
    """
    try:
        # Store feedback
        await learner.add_feedback(
            event_id=feedback.event_id,
            predicted_label=feedback.predicted_label,
            correct_label=feedback.correct_label,
            reviewer=feedback.reviewer,
            notes=feedback.notes
        )

        # Check if retraining threshold reached
        feedback_count = await learner.get_feedback_count()
        if feedback_count >= 100:  # Retrain after 100 feedback items
            # Trigger retraining (background task)
            asyncio.create_task(learner.trigger_retraining())

        return {
            "status": "feedback_recorded",
            "event_id": feedback.event_id,
            "feedback_count": feedback_count,
            "retraining_threshold": 100
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback submission error: {str(e)}")


@app.get("/learning/stats")
async def get_learning_stats():
    """
    Get continuous learning statistics
    """
    stats = await learner.get_stats()
    return stats


@app.get("/metrics")
async def get_metrics():
    """
    Get runtime metrics for monitoring
    """
    return {
        "total_events_processed": await db_service.count_events(),
        "compliance_percentage": (await scorer.get_overall_score())['percentage'],
        "high_confidence_rate": await calculate_high_confidence_rate(),
        "feedback_count": await learner.get_feedback_count(),
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# UNIFIED PIPELINE ENDPOINTS - Gap Analysis & Decision Making
# ============================================================================

@app.post("/api/v1/decision/audit/{audit_id}")
async def make_audit_decisions(
    audit_id: str,
    log_weight: float = 0.6,
    document_weight: float = 0.4
):
    """
    Make compliance decisions for an audit with gap analysis.

    This endpoint:
    1. Retrieves all classifications from Redis (both log and document evidence)
    2. Groups them by control_id
    3. Performs gap analysis comparing policy claims vs log findings
    4. Applies weighted scoring (default: 60% logs, 40% documents)
    5. Stores ComplianceDecision results back to Redis

    Args:
        audit_id: The audit identifier
        log_weight: Weight for log-based evidence (default: 0.6)
        document_weight: Weight for document-based evidence (default: 0.4)

    Returns:
        Decision summary with gap analysis results
    """
    if not SHARED_AVAILABLE or not evidence_manager or not gap_analyzer:
        raise HTTPException(
            status_code=503,
            detail="Unified pipeline not available. Gap analysis requires shared module."
        )

    try:
        # Validate weights
        if not abs(log_weight + document_weight - 1.0) < 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Weights must sum to 1.0 (got {log_weight + document_weight})"
            )

        print(f"\n{'='*80}")
        print(f"🎯 Making compliance decisions for audit: {audit_id}")
        print(f"   Log weight: {log_weight:.0%} | Document weight: {document_weight:.0%}")
        print(f"{'='*80}\n")

        # Get all evidence for this audit
        all_evidence = await evidence_manager.get_all_evidence(audit_id)

        if not all_evidence:
            return {
                "success": False,
                "audit_id": audit_id,
                "error": "No evidence found for this audit",
                "decisions_made": 0
            }

        # Group evidence by control_id
        evidence_by_control = {}
        for evidence in all_evidence:
            control_id = evidence.control_id
            if control_id not in evidence_by_control:
                evidence_by_control[control_id] = {
                    "log_evidence": [],
                    "document_evidence": [],
                    "control_name": evidence.control_name,
                    "control_family": evidence.control_family
                }

            if evidence.source_type == EvidenceSourceType.LOG:
                evidence_by_control[control_id]["log_evidence"].append(evidence)
            elif evidence.source_type == EvidenceSourceType.DOCUMENT:
                evidence_by_control[control_id]["document_evidence"].append(evidence)

        print(f"📊 Found evidence for {len(evidence_by_control)} controls")

        # Process each control
        decisions_made = 0
        gaps_detected = 0

        for control_id, control_data in evidence_by_control.items():
            log_evidence = control_data["log_evidence"]
            doc_evidence = control_data["document_evidence"]

            print(f"\n  Processing {control_id}: {len(log_evidence)} logs, {len(doc_evidence)} docs")

            # Get classifications for this control
            log_classifications = []
            doc_classifications = []

            for evidence in log_evidence:
                classification = await evidence_manager.get_classification(audit_id, evidence.evidence_id)
                if classification:
                    log_classifications.append(classification)

            for evidence in doc_evidence:
                classification = await evidence_manager.get_classification(audit_id, evidence.evidence_id)
                if classification:
                    doc_classifications.append(classification)

            # Perform gap analysis
            gap = gap_analyzer.analyze_control(
                control_id=control_id,
                control_name=control_data["control_name"],
                log_classifications=log_classifications,
                doc_classifications=doc_classifications,
                log_evidence=[e.model_dump() if hasattr(e, 'model_dump') else e for e in log_evidence],
                doc_evidence=[e.model_dump() if hasattr(e, 'model_dump') else e for e in doc_evidence]
            )

            if gap:
                gaps_detected += 1
                print(f"    ⚠️  Gap detected: {gap.gap_type.value} (severity: {gap.severity.value})")

            # Calculate weighted compliance score
            log_score = _calculate_compliance_score(log_classifications)
            doc_score = _calculate_compliance_score(doc_classifications)

            # Apply weights
            if log_classifications and doc_classifications:
                # Both sources available - use weighted average
                final_score = (log_weight * log_score) + (document_weight * doc_score)
                audit_mode = "FULL_AUDIT"
            elif log_classifications:
                # Only logs available
                final_score = log_score
                audit_mode = "LOGS_ONLY"
            elif doc_classifications:
                # Only documents available
                final_score = doc_score
                audit_mode = "DOCUMENTS_ONLY"
            else:
                # No classifications (shouldn't happen)
                final_score = 0.0
                audit_mode = "UNKNOWN"

            # Determine final status
            if final_score >= 0.80:
                final_status = ComplianceStatus.COMPLIANT
            elif final_score >= 0.50:
                final_status = ComplianceStatus.PARTIAL
            else:
                final_status = ComplianceStatus.NON_COMPLIANT

            # Calculate confidence
            all_classifications = log_classifications + doc_classifications
            avg_confidence = sum(c.confidence for c in all_classifications) / len(all_classifications) if all_classifications else 0.0

            # Create ComplianceDecision
            decision = ComplianceDecision(
                decision_id=f"decision_{control_id}_{audit_id[:8]}",
                audit_id=audit_id,
                control_id=control_id,
                control_name=control_data["control_name"],
                control_family=control_data["control_family"],
                final_status=final_status,
                confidence=avg_confidence,
                compliance_score=final_score,
                log_evidence_count=len(log_evidence),
                document_evidence_count=len(doc_evidence),
                log_score=log_score,
                document_score=doc_score,
                weights_applied={
                    "log_weight": log_weight,
                    "document_weight": document_weight
                },
                gap_detected=gap is not None,
                gap_type=gap.gap_type.value if gap else None,
                gap_severity=gap.severity.value if gap else None,
                gap_description=gap.description if gap else None,
                recommendation=gap.recommendation if gap else "No gaps detected - control is properly implemented and documented",
                evidence_ids=[e.evidence_id for e in log_evidence + doc_evidence],
                decided_at=datetime.utcnow()
            )

            # Store decision in Redis
            await evidence_manager.store_decision(decision)
            decisions_made += 1

            print(f"    ✅ Decision: {final_status.value} (score: {final_score:.2f}, confidence: {avg_confidence:.2f})")

        # Get gap summary
        gap_summary = gap_analyzer.get_gap_summary()

        print(f"\n{'='*80}")
        print(f"✅ Completed: {decisions_made} decisions made, {gaps_detected} gaps detected")
        print(f"{'='*80}\n")

        return {
            "success": True,
            "audit_id": audit_id,
            "decisions_made": decisions_made,
            "controls_assessed": len(evidence_by_control),
            "gaps_detected": gaps_detected,
            "gap_summary": gap_summary,
            "weights_used": {
                "log_weight": log_weight,
                "document_weight": document_weight
            },
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        print(f"❌ Error making decisions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Decision making error: {str(e)}")


@app.get("/api/v1/decision/audit/{audit_id}/gaps")
async def get_audit_gaps(audit_id: str):
    """
    Get all detected gaps for an audit.

    Returns:
        List of gaps with details and recommendations
    """
    if not SHARED_AVAILABLE or not gap_analyzer:
        raise HTTPException(
            status_code=503,
            detail="Gap analysis not available. Requires unified pipeline."
        )

    gaps = gap_analyzer.get_all_gaps()
    gap_summary = gap_analyzer.get_gap_summary()

    return {
        "audit_id": audit_id,
        "total_gaps": len(gaps),
        "gaps": [gap.to_dict() for gap in gaps],
        "summary": gap_summary
    }


@app.get("/api/v1/decision/audit/{audit_id}/results")
async def get_audit_decisions(audit_id: str):
    """
    Get all compliance decisions for an audit.

    Returns:
        List of decisions with scores and gap information
    """
    if not SHARED_AVAILABLE or not evidence_manager:
        raise HTTPException(
            status_code=503,
            detail="Unified pipeline not available"
        )

    try:
        # Get all evidence to determine control IDs
        all_evidence = await evidence_manager.get_all_evidence(audit_id)

        if not all_evidence:
            return {
                "audit_id": audit_id,
                "decisions": [],
                "total_controls": 0
            }

        # Get unique control IDs
        control_ids = list(set(e.control_id for e in all_evidence))

        # Get decisions for each control
        decisions = []
        for control_id in control_ids:
            decision = await evidence_manager.get_decision(audit_id, control_id)
            if decision:
                decisions.append(decision.model_dump() if hasattr(decision, 'model_dump') else decision)

        # Calculate summary statistics
        compliant_count = sum(1 for d in decisions if d.get('final_status') == 'compliant')
        non_compliant_count = sum(1 for d in decisions if d.get('final_status') == 'non_compliant')
        partial_count = sum(1 for d in decisions if d.get('final_status') == 'partial')

        gaps_count = sum(1 for d in decisions if d.get('gap_detected', False))

        return {
            "audit_id": audit_id,
            "total_controls": len(decisions),
            "decisions": decisions,
            "summary": {
                "compliant": compliant_count,
                "non_compliant": non_compliant_count,
                "partial": partial_count,
                "compliance_rate": (compliant_count / len(decisions) * 100) if decisions else 0,
                "gaps_detected": gaps_count
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving decisions: {str(e)}")


def _calculate_compliance_score(classifications: List) -> float:
    """
    Calculate compliance score from a list of classifications.

    Args:
        classifications: List of ClassificationResult objects

    Returns:
        Compliance score between 0.0 and 1.0
    """
    if not classifications:
        return 0.0

    # Count statuses
    compliant_count = 0
    partial_count = 0
    non_compliant_count = 0

    for cls in classifications:
        status = cls.prediction if hasattr(cls, 'prediction') else cls.get('prediction')

        if hasattr(status, 'value'):
            status = status.value

        if status == 'compliant' or status == ComplianceStatus.COMPLIANT:
            compliant_count += 1
        elif status == 'partial' or status == ComplianceStatus.PARTIAL:
            partial_count += 1
        else:
            non_compliant_count += 1

    total = len(classifications)

    # Calculate weighted score
    # Compliant = 1.0, Partial = 0.5, Non-compliant = 0.0
    score = (compliant_count * 1.0 + partial_count * 0.5) / total

    return score


# ============================================================================
# END UNIFIED PIPELINE ENDPOINTS
# ============================================================================


async def calculate_and_store_risk(event_id: str, prediction: str, confidence: float, status_code: int):
    """Background task to calculate and store risk score"""
    try:
        risk_score = await risk_assessor.calculate_risk(
            prediction=prediction,
            confidence=confidence,
            status_code=status_code
        )

        await db_service.store_risk_score(
            event_id=event_id,
            risk_score=risk_score['score'],
            risk_level=risk_score['level']
        )
    except Exception as e:
        print(f"⚠️ Error calculating risk for {event_id}: {str(e)}")


async def calculate_high_confidence_rate() -> float:
    """Calculate percentage of high confidence predictions"""
    stats = await db_service.get_confidence_stats()
    if stats['total'] == 0:
        return 0.0
    return (stats['high_confidence'] / stats['total']) * 100


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
