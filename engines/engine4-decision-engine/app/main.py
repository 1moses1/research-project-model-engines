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

from app.services.scoring import ComplianceScorer
from app.services.risk import RiskAssessor
from app.services.learning import ContinuousLearner
from app.services.database import DatabaseService

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

# Configuration
ENGINE3_URL = "http://xgboost-api:8000"


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


class ClassificationResult(BaseModel):
    """Result from ENGINE 3 classification"""
    event_id: str
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    timestamp: str
    route_decision: str
    needs_human_review: bool


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
    global scorer, risk_assessor, learner, db_service

    print("=" * 80)
    print("ENGINE 4: Decision & Scoring Engine - Starting Up")
    print("=" * 80)

    # Initialize services
    scorer = ComplianceScorer()
    risk_assessor = RiskAssessor()
    learner = ContinuousLearner()
    db_service = DatabaseService()

    await db_service.initialize()

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
    1. Call ENGINE 3 for classification
    2. Apply confidence routing
    3. Calculate risk score
    4. Store in database
    5. Update compliance scores
    """
    try:
        # Generate event ID if not provided
        if not event.event_id:
            event.event_id = f"evt_{datetime.utcnow().timestamp()}"

        # Step 1: Call ENGINE 3 for classification
        async with httpx.AsyncClient() as client:
            classify_response = await client.post(
                f"{ENGINE3_URL}/classify",
                json={
                    "log_message": event.log_message,
                    "status_code": event.status_code,
                    "hour_of_day": event.hour_of_day,
                    "port": event.port
                },
                timeout=10.0
            )
            classify_response.raise_for_status()
            classification = classify_response.json()

        # Step 2: Apply confidence routing
        confidence = classification['confidence']
        prediction = classification['prediction']

        # Determine route decision
        if confidence >= 0.90:
            if prediction == 'compliant':
                route_decision = "auto_accept"
                needs_review = False
            else:  # non-compliant with high confidence
                route_decision = "flag_for_review"
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

        # Step 4: Store classification result
        await db_service.store_classification(
            event_id=event.event_id,
            log_message=event.log_message,
            prediction=prediction,
            confidence=confidence,
            route_decision=route_decision,
            timestamp=datetime.utcnow().isoformat()
        )

        # Step 5: Update compliance scores (background)
        background_tasks.add_task(scorer.update_scores, prediction)

        return ClassificationResult(
            event_id=event.event_id,
            prediction=prediction,
            confidence=confidence,
            probabilities=classification['probabilities'],
            timestamp=classification['timestamp'],
            route_decision=route_decision,
            needs_human_review=needs_review
        )

    except httpx.HTTPError as e:
        raise HTTPException(status_code=503, detail=f"ENGINE 3 connection error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/process/batch")
async def process_batch_events(events: List[LogEvent], background_tasks: BackgroundTasks):
    """
    Process multiple events in batch
    """
    try:
        # Prepare batch for ENGINE 3
        engine3_batch = {
            "events": [
                {
                    "log_message": e.log_message,
                    "status_code": e.status_code,
                    "hour_of_day": e.hour_of_day,
                    "port": e.port
                }
                for e in events
            ]
        }

        # Call ENGINE 3 batch endpoint
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ENGINE3_URL}/classify/batch",
                json=engine3_batch,
                timeout=30.0
            )
            response.raise_for_status()
            batch_results = response.json()

        # Process each result
        results = []
        for i, (event, prediction_result) in enumerate(zip(events, batch_results['predictions'])):
            event_id = event.event_id or f"evt_batch_{i}_{datetime.utcnow().timestamp()}"

            confidence = prediction_result['confidence']
            prediction = prediction_result['prediction']

            # Apply routing logic
            if confidence >= 0.90:
                route_decision = "auto_accept" if prediction == 'compliant' else "flag_for_review"
                needs_review = prediction != 'compliant'
            else:
                route_decision = "queue_for_verification"
                needs_review = True

            # Store result
            await db_service.store_classification(
                event_id=event_id,
                log_message=event.log_message,
                prediction=prediction,
                confidence=confidence,
                route_decision=route_decision,
                timestamp=datetime.utcnow().isoformat()
            )

            results.append({
                "event_id": event_id,
                "prediction": prediction,
                "confidence": confidence,
                "route_decision": route_decision,
                "needs_human_review": needs_review
            })

        # Update scores in background
        for result in batch_results['predictions']:
            background_tasks.add_task(scorer.update_scores, result['prediction'])

        return {
            "total_processed": len(results),
            "results": results,
            "avg_inference_time_ms": batch_results.get('avg_inference_time_ms', 0)
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
