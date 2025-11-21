#!/usr/bin/env python3
"""
Compliance API - REST endpoints for security system integration
FastAPI-based service for real-time compliance analysis
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.xgboost_classifier import XGBoostClassifier
from nlp.unstructured_processor import UnstructuredSecurityProcessor
from nlp.rag_engine import RAGComplianceEngine
from integrations.siem_soar_adapter import SecuritySystemIntegration

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Rwanda NCSA Compliance API",
    description="AI-powered compliance analysis with RAG and XGBoost",
    version="1.0.0"
)

# CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global models (loaded once at startup)
xgboost_model = None
nlp_processor = None
rag_engine = None
siem_integrator = None


# Pydantic models for request/response
class ComplianceRequest(BaseModel):
    """Single compliance analysis request"""
    text: str = Field(..., description="Unstructured security text (log, alert, report)")
    source_type: str = Field(default="unknown", description="Source type (log, alert, email, etc.)")
    use_rag: bool = Field(default=True, description="Use RAG for context augmentation")


class BatchComplianceRequest(BaseModel):
    """Batch compliance analysis request"""
    texts: List[str] = Field(..., description="List of unstructured security texts")
    source_types: Optional[List[str]] = Field(default=None, description="Source types for each text")
    use_rag: bool = Field(default=True, description="Use RAG for context augmentation")


class SIEMFormatRequest(BaseModel):
    """Request to format for SIEM system"""
    text: str
    target_system: str = Field(..., description="Target system (splunk, qradar, elk, arcsight)")


class SOARIncidentRequest(BaseModel):
    """Request to create SOAR incident"""
    text: str
    platform: str = Field(default="xsoar", description="SOAR platform (xsoar, phantom)")


class ComplianceResponse(BaseModel):
    """Compliance analysis response"""
    compliance_status: str
    confidence_score: float
    severity: str
    control_id: str
    control_family: str
    framework: str
    mitre_tactics: List[str]
    log_message: str
    processed_timestamp: str
    rag_context: Optional[Dict] = None
    metadata: Dict


# Startup event - load models
@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    global xgboost_model, nlp_processor, rag_engine, siem_integrator

    logger.info("Loading models...")

    try:
        # Load XGBoost model
        xgboost_model = XGBoostClassifier()
        model_path = "results/models/xgboost_no_leakage/xgboost_model_no_leakage"
        xgboost_model.load_model(model_path)
        logger.info("  ✓ XGBoost model loaded")

        # Load NLP processor
        nlp_processor = UnstructuredSecurityProcessor()
        logger.info("  ✓ NLP processor loaded")

        # Load RAG engine
        rag_engine = RAGComplianceEngine(model_path)
        logger.info("  ✓ RAG engine loaded")

        # Load SIEM integrator
        siem_integrator = SecuritySystemIntegration()
        logger.info("  ✓ SIEM integrator loaded")

        logger.info("API ready!")

    except Exception as e:
        logger.error(f"Failed to load models: {e}")
        raise


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": {
            "xgboost": xgboost_model is not None,
            "nlp": nlp_processor is not None,
            "rag": rag_engine is not None,
            "siem": siem_integrator is not None
        }
    }


# Main compliance analysis endpoint
@app.post("/analyze", response_model=ComplianceResponse)
async def analyze_compliance(request: ComplianceRequest):
    """
    Analyze unstructured security text for compliance

    **Example Request:**
    ```json
    {
      "text": "Unauthorized access attempt from IP 192.168.1.100 to database server",
      "source_type": "firewall_log",
      "use_rag": true
    }
    ```

    **Returns:** Structured compliance analysis with NCSA context
    """
    try:
        # Process with RAG engine
        result = rag_engine.analyze(request.text, use_rag=request.use_rag)

        return ComplianceResponse(**result)

    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# Batch analysis endpoint
@app.post("/analyze/batch")
async def analyze_batch(request: BatchComplianceRequest):
    """
    Analyze multiple security texts in batch

    **Example Request:**
    ```json
    {
      "texts": [
        "User login successful via VPN",
        "Malware detected on workstation",
        "Database backup completed"
      ],
      "use_rag": true
    }
    ```

    **Returns:** List of compliance analyses
    """
    try:
        results = rag_engine.batch_analyze(request.texts, use_rag=request.use_rag)

        return {
            "total": len(results),
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Batch analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch analysis failed: {str(e)}")


# SIEM formatting endpoint
@app.post("/format/siem")
async def format_for_siem(request: SIEMFormatRequest):
    """
    Analyze and format for SIEM system (CEF, LEEF, JSON, Syslog)

    **Supported Systems:**
    - splunk (JSON)
    - elk (JSON)
    - qradar (LEEF)
    - arcsight (CEF)
    - syslog (RFC 5424)

    **Example Request:**
    ```json
    {
      "text": "Unauthorized access attempt from IP 192.168.1.100",
      "target_system": "splunk"
    }
    ```
    """
    try:
        # Analyze
        result = rag_engine.analyze(request.text, use_rag=False)

        # Format for SIEM
        formatted = siem_integrator.format_for_system(result, request.target_system)

        return {
            "target_system": request.target_system,
            "formatted_event": formatted,
            "original_analysis": result
        }

    except Exception as e:
        logger.error(f"SIEM formatting failed: {e}")
        raise HTTPException(status_code=500, detail=f"Formatting failed: {str(e)}")


# SOAR incident creation endpoint
@app.post("/soar/incident")
async def create_soar_incident(request: SOARIncidentRequest):
    """
    Analyze and create SOAR incident/container

    **Supported Platforms:**
    - xsoar (Cortex XSOAR)
    - phantom (Splunk Phantom/SOAR)
    - demisto (Demisto)

    **Example Request:**
    ```json
    {
      "text": "Ransomware detected on file server - immediate action required",
      "platform": "xsoar"
    }
    ```
    """
    try:
        # Analyze
        result = rag_engine.analyze(request.text, use_rag=True)

        # Create SOAR incident
        incident = siem_integrator.create_soar_incident(result, request.platform)

        return {
            "platform": request.platform,
            "incident": incident,
            "original_analysis": result
        }

    except Exception as e:
        logger.error(f"SOAR incident creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Incident creation failed: {str(e)}")


# RAG retrieval endpoint
@app.post("/rag/retrieve")
async def retrieve_standards(query: str, top_k: int = 5):
    """
    Retrieve relevant NCSA standards for a query

    **Example:**
    ```
    POST /rag/retrieve?query=access control&top_k=3
    ```
    """
    try:
        results = rag_engine.knowledge_base.retrieve(query, top_k=top_k)

        return {
            "query": query,
            "top_k": top_k,
            "results": results
        }

    except Exception as e:
        logger.error(f"RAG retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


# Explain prediction endpoint
@app.post("/explain")
async def explain_prediction(text: str):
    """
    Get SHAP explanation for prediction

    **Example:**
    ```
    POST /explain?text=Unauthorized access denied
    ```
    """
    try:
        # This would integrate with explain_predictions_cli.py
        # For now, return basic analysis
        result = rag_engine.analyze(text, use_rag=True)

        return {
            "text": text,
            "prediction": result['compliance_status'],
            "confidence": result['confidence_score'],
            "reasoning": result.get('compliance_reasoning', ''),
            "rag_context": result.get('rag_context', {})
        }

    except Exception as e:
        logger.error(f"Explanation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Explanation failed: {str(e)}")


# Statistics endpoint
@app.get("/stats")
async def get_statistics():
    """Get API usage statistics"""
    # This would track real usage stats
    return {
        "api_version": "1.0.0",
        "model_version": "xgboost_no_leakage",
        "uptime": "operational",
        "capabilities": [
            "compliance_analysis",
            "rag_augmentation",
            "siem_integration",
            "soar_integration",
            "batch_processing",
            "explainability"
        ]
    }


# Model info endpoint
@app.get("/model/info")
async def model_info():
    """Get model information"""
    return {
        "model_type": "XGBoost Binary Classifier",
        "version": "1.0",
        "accuracy": 0.9909,
        "training_date": "2025-10-29",
        "features": {
            "text": "TF-IDF (1000 features)",
            "controls": "NIST SP 800-53",
            "frameworks": "NIST-800-53, MITRE ATT&CK, Rwanda NCSA",
            "temporal": "Hour, day of week, business hours"
        },
        "no_data_leakage": True,
        "adversarial_tested": True
    }


def main():
    """Run API server"""
    import uvicorn

    uvicorn.run(
        "compliance_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
