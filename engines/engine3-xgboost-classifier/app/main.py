"""
ENGINE 3: XGBoost Compliance Classifier API
Rwanda NCSA Compliance Auditor v3.0.0

FastAPI wrapper for the trained XGBoost model.
Provides real-time compliance classification with <1ms latency.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import xgboost as xgb
import pickle
import joblib
import json
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import time
from datetime import datetime
import os
import sys

# Import shared models for unified pipeline
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'shared'))
try:
    from shared import (
        RedisClient, get_redis_client, init_redis,
        ComplianceEvidence, EvidenceSourceType,
        ClassificationResult, ComplianceStatus,
        EvidenceManager, create_evidence_manager
    )
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False
    print("⚠️ Shared module not available - running in standalone mode")

# Initialize FastAPI app
app = FastAPI(
    title="Rwanda NCSA XGBoost Compliance API",
    version="3.0.0",
    description="Real-time compliance classification using XGBoost (ENGINE 3)"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for model and artifacts
MODEL = None
LABEL_ENCODER = None
DAY_ENCODER = None  # For encoding day_of_week
VECTORIZER = None
FEATURES = None
MODEL_METADATA = {}
evidence_manager = None

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

# Paths - ENGINE 3 is now self-contained with local models
MODEL_DIR = Path("/app/models")
if not MODEL_DIR.exists():
    # Fallback to local models directory (for development)
    MODEL_DIR = Path(__file__).parent.parent / "models"
    if not MODEL_DIR.exists():
        raise FileNotFoundError(
            f"Models directory not found at {MODEL_DIR}. "
            "ENGINE 3 requires model files to be present in the 'models/' directory."
        )


class LogEvent(BaseModel):
    """Single log event for classification - realistic format"""
    timestamp: str = Field(..., description="Event timestamp (ISO format or epoch)")
    log_message: str = Field(..., description="Log message text")
    status_code: Optional[int] = Field(200, description="HTTP status code")
    port: Optional[int] = Field(443, description="Port number")

    class Config:
        schema_extra = {
            "example": {
                "timestamp": "2025-11-21T14:30:00Z",
                "log_message": "User admin logged in successfully",
                "status_code": 200,
                "port": 443
            }
        }


class BatchLogEvents(BaseModel):
    """Batch of log events for classification"""
    events: List[LogEvent] = Field(..., description="List of log events")

    class Config:
        schema_extra = {
            "example": {
                "events": [
                    {
                        "timestamp": "2025-11-21T14:30:00Z",
                        "log_message": "User admin logged in successfully",
                        "status_code": 200,
                        "port": 443
                    },
                    {
                        "timestamp": "2025-11-21T02:15:00Z",
                        "log_message": "Failed login attempt for user john",
                        "status_code": 401,
                        "port": 22
                    }
                ]
            }
        }


class PredictionResponse(BaseModel):
    """Classification result for a single event"""
    prediction: str = Field(..., description="compliant or non_compliant")
    confidence: float = Field(..., description="Prediction confidence (0-1)")
    probabilities: Dict[str, float] = Field(..., description="Class probabilities")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")
    timestamp: str = Field(..., description="Prediction timestamp")


class BatchPredictionResponse(BaseModel):
    """Batch classification results"""
    predictions: List[PredictionResponse]
    total_events: int
    total_inference_time_ms: float
    avg_inference_time_ms: float


@app.on_event("startup")
async def load_model():
    """Load XGBoost model and artifacts on startup"""
    global MODEL, LABEL_ENCODER, DAY_ENCODER, VECTORIZER, FEATURES, MODEL_METADATA, evidence_manager

    try:
        print("=" * 80)
        print("ENGINE 3: XGBoost Compliance Classifier - Starting Up")
        print("=" * 80)

        # Load XGBoost model
        model_path = MODEL_DIR / "rwanda_ncsa_compliance_auditor.json"
        print(f"\n📦 Loading model from: {model_path}")
        MODEL = xgb.XGBClassifier()
        MODEL.load_model(str(model_path))
        print("✅ XGBoost model loaded")

        # Load label encoder (use joblib for sklearn objects)
        le_path = MODEL_DIR / "label_encoder.pkl"
        print(f"📦 Loading label encoder from: {le_path}")
        LABEL_ENCODER = joblib.load(le_path)
        print(f"✅ Label encoder loaded (classes: {list(LABEL_ENCODER.classes_)})")

        # Load day encoder (optional, only in new model)
        day_enc_path = MODEL_DIR / "day_encoder.pkl"
        if day_enc_path.exists():
            print(f"📦 Loading day encoder from: {day_enc_path}")
            DAY_ENCODER = joblib.load(day_enc_path)
            print(f"✅ Day encoder loaded (classes: {list(DAY_ENCODER.classes_)})")
        else:
            print("ℹ️  Day encoder not found (using old model format)")

        # Load TF-IDF vectorizer (use joblib for sklearn objects)
        vec_path = MODEL_DIR / "tfidf_vectorizer.pkl"
        print(f"📦 Loading TF-IDF vectorizer from: {vec_path}")
        VECTORIZER = joblib.load(vec_path)
        print(f"✅ TF-IDF vectorizer loaded ({len(VECTORIZER.get_feature_names_out())} features)")

        # Load feature names
        features_path = MODEL_DIR / "features.json"
        print(f"📦 Loading feature names from: {features_path}")
        with open(features_path, 'r') as f:
            FEATURES = json.load(f)
        print(f"✅ Feature names loaded ({len(FEATURES)} features)")

        # Load model metadata
        metrics_path = MODEL_DIR / "model_metrics.json"
        if metrics_path.exists():
            with open(metrics_path, 'r') as f:
                MODEL_METADATA = json.load(f)
            print(f"✅ Model metadata loaded (F1: {MODEL_METADATA.get('f1_score', 'N/A')})")

        print("\n" + "=" * 80)
        print("✅ ENGINE 3 READY - XGBoost Compliance Classifier Online")
        print("=" * 80)
        print(f"\n📊 Model Statistics:")
        print(f"   Total Features: {len(FEATURES)}")
        print(f"   Classes: {list(LABEL_ENCODER.classes_)}")
        print(f"   Framework: Rwanda NCSA + NIST SP 800-53")
        print(f"   Total Controls: {MODEL_METADATA.get('total_controls', 196)}")
        print(f"   - Rwanda NCSA: {MODEL_METADATA.get('rwanda_controls', 169)}")
        print(f"   - NIST SP 800-53: {MODEL_METADATA.get('nist_controls', 27)}")

        # Initialize unified pipeline components
        if SHARED_AVAILABLE:
            try:
                # Initialize Redis client
                redis_client = get_redis_client()
                await init_redis(redis_client, host=REDIS_HOST, port=REDIS_PORT)

                # Create evidence manager
                evidence_manager = create_evidence_manager(redis_client)

                print(f"\n🔄 Unified Pipeline: Active")
                print(f"   - Redis: Connected ({REDIS_HOST}:{REDIS_PORT})")
                print(f"   - Evidence Manager: Initialized")
                print(f"   - Classification results will be stored in Redis")
            except Exception as e:
                print(f"\n⚠️  Unified Pipeline: Failed to initialize - {str(e)}")
                print(f"   - Running in standalone mode")
                evidence_manager = None
        else:
            print(f"\n⚠️  Unified Pipeline: Not available (shared module not found)")
            print(f"   - Running in standalone mode")

        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ ERROR loading model: {str(e)}")
        print("⚠️  ENGINE 3 will not be available")
        raise


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse timestamp from various formats (ISO, epoch, etc.)

    Returns:
        datetime object
    """
    from dateutil import parser

    try:
        # Try parsing as ISO format first
        return parser.isoparse(timestamp_str)
    except:
        try:
            # Try parsing as epoch timestamp (seconds)
            return datetime.fromtimestamp(float(timestamp_str))
        except:
            # Default to current time if parsing fails
            return datetime.utcnow()


def extract_temporal_features(timestamp_str: str) -> dict:
    """
    Extract temporal features from timestamp (like real-world systems do)

    Returns:
        dict with hour_of_day, day_of_week, is_business_hours
    """
    dt = parse_timestamp(timestamp_str)

    # Extract features
    hour_of_day = dt.hour
    day_name = dt.strftime('%A')  # Monday, Tuesday, etc.

    # Business hours: Monday-Friday, 8 AM - 6 PM
    is_business_hours = (
        dt.weekday() < 5 and  # Monday=0, Friday=4
        8 <= hour_of_day < 18
    )

    return {
        'hour_of_day': hour_of_day,
        'day_of_week': day_name,
        'is_business_hours': is_business_hours
    }


def extract_features(event: LogEvent) -> np.ndarray:
    """
    Extract features from a log event (realistic - auto-extracts from timestamp)

    Returns:
        Feature vector ready for XGBoost prediction
    """
    # Extract text features using TF-IDF
    tfidf_features = VECTORIZER.transform([event.log_message]).toarray()[0]

    # Extract temporal features from timestamp (REALISTIC!)
    temporal = extract_temporal_features(event.timestamp)

    # Encode day of week if we have a day encoder
    if DAY_ENCODER:
        try:
            day_encoded = DAY_ENCODER.transform([temporal['day_of_week']])[0]
        except:
            day_encoded = 0  # Default to Monday (0) if invalid
    else:
        day_encoded = 0

    # Build feature dict for easier mapping
    feature_dict = {
        'hour_of_day': temporal['hour_of_day'],
        'day_of_week': day_encoded,
        'is_business_hours': int(temporal['is_business_hours']),
        'status_code': event.status_code or 200,
        'port': event.port or 443
    }

    # Combine features in correct order based on FEATURES list
    feature_vector = []
    text_idx = 0

    for feat_name in FEATURES:
        if feat_name.startswith('text_') or feat_name.startswith('tfidf_'):
            # Text feature
            if text_idx < len(tfidf_features):
                feature_vector.append(tfidf_features[text_idx])
                text_idx += 1
            else:
                feature_vector.append(0.0)
        elif feat_name in feature_dict:
            # Numeric feature
            feature_vector.append(feature_dict[feat_name])
        else:
            # Unknown feature - default to 0
            feature_vector.append(0.0)

    return np.array([feature_vector])


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "ENGINE 3: XGBoost Compliance Classifier",
        "version": "3.0.0",
        "status": "running" if MODEL is not None else "model_not_loaded",
        "framework": "Rwanda NCSA Cybersecurity Minimum Standards",
        "model_loaded": MODEL is not None,
        "total_controls": MODEL_METADATA.get('total_controls', 196),
        "rwanda_controls": MODEL_METADATA.get('rwanda_controls', 169),
        "nist_controls": MODEL_METADATA.get('nist_controls', 27)
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy" if MODEL is not None else "unhealthy",
        "model_loaded": MODEL is not None,
        "vectorizer_loaded": VECTORIZER is not None,
        "label_encoder_loaded": LABEL_ENCODER is not None,
        "features_loaded": FEATURES is not None,
        "feature_count": len(FEATURES) if FEATURES else 0,
        "model_metadata": MODEL_METADATA,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/model/info")
async def model_info():
    """Get model information and statistics"""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    return {
        "model_type": "XGBoost Classifier",
        "version": "3.0.0",
        "framework": "Rwanda NCSA Cybersecurity Minimum Standards",
        "features": {
            "total": len(FEATURES),
            "numeric": 3,
            "text": len([f for f in FEATURES if f.startswith('tfidf_')])
        },
        "classes": list(LABEL_ENCODER.classes_),
        "controls": {
            "total": MODEL_METADATA.get('total_controls', 196),
            "rwanda_ncsa": MODEL_METADATA.get('rwanda_controls', 169),
            "nist_sp_800_53": MODEL_METADATA.get('nist_controls', 27)
        },
        "performance": {
            "f1_score": MODEL_METADATA.get('f1_score'),
            "accuracy": MODEL_METADATA.get('accuracy'),
            "precision": MODEL_METADATA.get('precision'),
            "recall": MODEL_METADATA.get('recall'),
            "training_time_seconds": MODEL_METADATA.get('training_time_seconds')
        },
        "cross_validation": MODEL_METADATA.get('cross_validation', {})
    }


@app.post("/classify", response_model=PredictionResponse)
async def classify_event(event: LogEvent):
    """
    Classify a single log event as compliant or non-compliant

    Args:
        event: Log event with message and metadata

    Returns:
        Classification result with confidence scores
    """
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # Start timing
        start_time = time.time()

        # Extract features
        X = extract_features(event)

        # Predict
        prediction = MODEL.predict(X)[0]
        probabilities = MODEL.predict_proba(X)[0]

        # Get class names
        predicted_class = LABEL_ENCODER.classes_[prediction]

        # Calculate inference time
        inference_time = (time.time() - start_time) * 1000  # Convert to ms

        # Build probability dict
        prob_dict = {
            LABEL_ENCODER.classes_[i]: float(probabilities[i])
            for i in range(len(LABEL_ENCODER.classes_))
        }

        return PredictionResponse(
            prediction=predicted_class,
            confidence=float(probabilities[prediction]),
            probabilities=prob_dict,
            inference_time_ms=round(inference_time, 3),
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/classify/batch", response_model=BatchPredictionResponse)
async def classify_batch(batch: BatchLogEvents):
    """
    Classify multiple log events in a single request

    Args:
        batch: List of log events

    Returns:
        Batch classification results
    """
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        start_time = time.time()
        predictions = []

        for event in batch.events:
            # Extract features
            event_start = time.time()
            X = extract_features(event)

            # Predict
            prediction = MODEL.predict(X)[0]
            probabilities = MODEL.predict_proba(X)[0]

            # Get class names
            predicted_class = LABEL_ENCODER.classes_[prediction]

            # Calculate per-event inference time
            event_time = (time.time() - event_start) * 1000

            # Build probability dict
            prob_dict = {
                LABEL_ENCODER.classes_[i]: float(probabilities[i])
                for i in range(len(LABEL_ENCODER.classes_))
            }

            predictions.append(PredictionResponse(
                prediction=predicted_class,
                confidence=float(probabilities[prediction]),
                probabilities=prob_dict,
                inference_time_ms=round(event_time, 3),
                timestamp=datetime.utcnow().isoformat()
            ))

        total_time = (time.time() - start_time) * 1000
        avg_time = total_time / len(batch.events) if batch.events else 0

        return BatchPredictionResponse(
            predictions=predictions,
            total_events=len(batch.events),
            total_inference_time_ms=round(total_time, 3),
            avg_inference_time_ms=round(avg_time, 3)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")


# ============================================================================
# Unified Pipeline Classification Endpoints
# ============================================================================

@app.post("/api/v1/classify/audit/{audit_id}")
async def classify_audit_evidence(audit_id: str, control_id: Optional[str] = None):
    """
    Classify all evidence for an audit from Redis and store results.

    This endpoint:
    1. Retrieves evidence from Redis via EvidenceManager
    2. Classifies each evidence item using XGBoost
    3. Stores ClassificationResult back to Redis
    4. Returns summary of classifications

    Args:
        audit_id: Audit ID to classify
        control_id: Optional - only classify specific control
    """
    if not SHARED_AVAILABLE or not evidence_manager:
        raise HTTPException(
            status_code=503,
            detail="Unified pipeline not available - shared module or Redis not initialized"
        )

    if MODEL is None:
        raise HTTPException(status_code=503, detail="XGBoost model not loaded")

    try:
        start_time = time.time()

        # Get evidence from Redis
        if control_id:
            evidence_list = await evidence_manager.get_evidence_by_control(audit_id, control_id)
        else:
            evidence_list = await evidence_manager.get_all_evidence(audit_id)

        if not evidence_list:
            return {
                "audit_id": audit_id,
                "total_evidence": 0,
                "classified": 0,
                "message": "No evidence found for this audit"
            }

        print(f"\n🔬 Classifying {len(evidence_list)} evidence items for audit {audit_id}")

        classified_count = 0
        results_by_status = {"compliant": 0, "non_compliant": 0, "partial": 0}

        for evidence in evidence_list:
            # Extract features from evidence
            features_dict = evidence.features if hasattr(evidence, 'features') else {}

            # Build feature vector matching training format
            feature_vector = _build_feature_vector(evidence, features_dict)

            # Classify
            prediction = MODEL.predict(feature_vector)[0]
            probabilities = MODEL.predict_proba(feature_vector)[0]

            # Decode prediction
            predicted_class = LABEL_ENCODER.inverse_transform([prediction])[0]
            confidence = float(probabilities[prediction])

            # Map to ComplianceStatus
            if predicted_class == "compliant":
                status = ComplianceStatus.COMPLIANT
            elif predicted_class == "non_compliant":
                status = ComplianceStatus.NON_COMPLIANT
            else:
                status = ComplianceStatus.PARTIAL

            results_by_status[predicted_class] = results_by_status.get(predicted_class, 0) + 1

            # Create ClassificationResult
            classification = ClassificationResult(
                evidence_id=evidence.evidence_id,
                audit_id=audit_id,
                control_id=evidence.control_id,
                prediction=status,
                confidence=confidence,
                probabilities={
                    "compliant": float(probabilities[0]) if len(probabilities) > 0 else 0.0,
                    "non_compliant": float(probabilities[1]) if len(probabilities) > 1 else 0.0
                },
                model_version=MODEL_METADATA.get('version', '3.0.0'),
                features_used=list(features_dict.keys()),
                inference_time_ms=0.0,  # Will be updated
                classified_at=datetime.utcnow()
            )

            # Store classification result in Redis
            await evidence_manager.store_classification(classification)
            classified_count += 1

        processing_time = (time.time() - start_time) * 1000

        print(f"✅ Classified {classified_count} items in {processing_time:.2f}ms")
        print(f"   Results: {results_by_status}")

        return {
            "success": True,
            "audit_id": audit_id,
            "total_evidence": len(evidence_list),
            "classified": classified_count,
            "results_summary": results_by_status,
            "processing_time_ms": round(processing_time, 2),
            "avg_time_per_item_ms": round(processing_time / len(evidence_list), 2) if evidence_list else 0
        }

    except Exception as e:
        print(f"⚠️ Classification error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")


def _build_feature_vector(evidence: Any, features_dict: Dict) -> np.ndarray:
    """
    Build feature vector from ComplianceEvidence for XGBoost prediction.

    Args:
        evidence: ComplianceEvidence object
        features_dict: Pre-extracted features from evidence

    Returns:
        Feature vector ready for XGBoost
    """
    # Extract text features using TF-IDF
    evidence_text = evidence.evidence_text if hasattr(evidence, 'evidence_text') else ""
    tfidf_features = VECTORIZER.transform([evidence_text]).toarray()[0]

    # Get temporal features from evidence timestamp
    timestamp = evidence.timestamp if hasattr(evidence, 'timestamp') else datetime.utcnow()
    if isinstance(timestamp, datetime):
        hour_of_day = timestamp.hour
        day_name = timestamp.strftime('%A')
        is_business_hours = timestamp.weekday() < 5 and 8 <= hour_of_day < 18
    else:
        hour_of_day = 12
        day_name = "Monday"
        is_business_hours = True

    # Get other features from features_dict or defaults
    status_code = features_dict.get('status_code', 200)
    port = features_dict.get('port', 443)

    # Encode day_of_week if encoder available
    if DAY_ENCODER:
        try:
            day_encoded = DAY_ENCODER.transform([day_name])[0]
        except:
            day_encoded = 0
    else:
        day_encoded = 0

    # Build complete feature vector
    other_features = np.array([
        hour_of_day,
        day_encoded,
        1 if is_business_hours else 0,
        status_code,
        port
    ])

    # Combine all features
    feature_vector = np.concatenate([tfidf_features, other_features]).reshape(1, -1)

    return feature_vector


@app.get("/metrics")
async def get_metrics():
    """
    Get runtime metrics for monitoring

    Returns:
        Prometheus-style metrics
    """
    if MODEL is None:
        return {"status": "model_not_loaded"}

    return {
        "model_loaded": 1,
        "feature_count": len(FEATURES),
        "class_count": len(LABEL_ENCODER.classes_),
        "model_f1_score": MODEL_METADATA.get('f1_score', 0),
        "model_accuracy": MODEL_METADATA.get('accuracy', 0),
        "uptime_seconds": time.time(),  # Simplified, in production track actual uptime
        "total_controls": MODEL_METADATA.get('total_controls', 196)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
