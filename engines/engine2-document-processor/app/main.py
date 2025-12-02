"""
ENGINE 2: Document Processing Engine
Rwanda NCSA Compliance Auditor v3.0.0

LLM-powered document processing for policy analysis and control extraction.
Extracts compliance requirements from PDF, DOCX, XLSX documents.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import tempfile
import json

from app.extractors.pdf_extractor import PDFExtractor
from app.extractors.docx_extractor import DOCXExtractor
from app.extractors.excel_extractor import ExcelExtractor
from app.services.llm_processor import LLMProcessor
from app.services.control_mapper import ControlMapper
from app.services.semantic_matcher import SemanticControlMatcher
from app.services.evidence_converter import DocumentEvidenceConverter, get_document_evidence_converter

# Import shared models for unified pipeline
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))
try:
    from shared import (
        RedisClient, get_redis_client, init_redis,
        ComplianceEvidence, EvidenceSourceType, EvidenceBatch,
        EvidenceManager, create_evidence_manager
    )
    SHARED_AVAILABLE = True
except ImportError:
    SHARED_AVAILABLE = False
    print("⚠️ Shared module not available - running in standalone mode")

# Initialize FastAPI app
app = FastAPI(
    title="Rwanda NCSA Document Processing Engine",
    version="3.0.0",
    description="ENGINE 2: LLM-powered document processing and control extraction"
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
pdf_extractor = None
docx_extractor = None
excel_extractor = None
llm_processor = None
control_mapper = None
semantic_matcher = None
evidence_converter = None
evidence_manager = None

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


class DocumentMetadata(BaseModel):
    """Metadata about uploaded document"""
    filename: str
    file_type: str
    size_bytes: int
    company_name: Optional[str] = "Unknown"
    framework: str = "Rwanda-NCSA"


class ExtractedControl(BaseModel):
    """Single extracted control requirement"""
    control_id: str
    control_name: str
    description: str
    family: str
    requirements: List[str]
    mapped_rwanda_controls: List[str]
    confidence: float


class ProcessingResult(BaseModel):
    """Result of document processing"""
    document_id: str
    filename: str
    status: str
    extracted_text_length: int
    controls_extracted: int
    controls: List[ExtractedControl]
    processing_time_seconds: float
    timestamp: str


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global pdf_extractor, docx_extractor, excel_extractor, llm_processor, control_mapper, semantic_matcher
    global evidence_converter, evidence_manager

    print("=" * 80)
    print("ENGINE 2: Document Processing Engine - Starting Up")
    print("=" * 80)

    # Initialize extractors
    pdf_extractor = PDFExtractor()
    docx_extractor = DOCXExtractor()
    excel_extractor = ExcelExtractor()

    # Initialize LLM processor
    if OPENAI_API_KEY:
        llm_processor = LLMProcessor(api_key=OPENAI_API_KEY)
        print("✅ OpenAI LLM processor initialized")
    else:
        print("⚠️  OpenAI API key not found - using mock processor")
        llm_processor = LLMProcessor(api_key=None)  # Mock mode

    # Initialize control mapper (loads taxonomy automatically in __init__)
    control_mapper = ControlMapper()

    # Initialize semantic matcher (AI embeddings)
    try:
        semantic_matcher = SemanticControlMatcher()
        if semantic_matcher.available:
            print("✅ Semantic matcher initialized (AI-powered)")
        else:
            print("⚠️  Semantic matcher unavailable (falling back to fuzzy matching)")
    except Exception as e:
        print(f"⚠️  Semantic matcher failed to initialize: {str(e)}")
        semantic_matcher = None

    # Initialize unified pipeline components
    if SHARED_AVAILABLE:
        try:
            # Initialize evidence converter
            evidence_converter = get_document_evidence_converter()

            # Initialize Redis client
            redis_client = get_redis_client()
            await init_redis(redis_client, host=REDIS_HOST, port=REDIS_PORT)

            # Create evidence manager
            evidence_manager = create_evidence_manager(redis_client)

            print(f"🔄 Unified Pipeline: Active")
            print(f"   - Redis: Connected ({REDIS_HOST}:{REDIS_PORT})")
            print(f"   - Evidence Manager: Initialized")
            print(f"   - Document Evidence Converter: Ready")
            print(f"   - ComplianceEvidence format: Enabled")
        except Exception as e:
            print(f"⚠️  Unified Pipeline: Failed to initialize - {str(e)}")
            print(f"   - Running in standalone mode")
            evidence_manager = None
            evidence_converter = get_document_evidence_converter()  # Still create converter
    else:
        print(f"⚠️  Unified Pipeline: Not available (shared module not found)")
        print(f"   - Running in standalone mode")
        evidence_converter = get_document_evidence_converter()

    print("\n✅ All services initialized")
    print("=" * 80)
    print("✅ ENGINE 2 READY - Document Processing Engine Online")
    print("=" * 80)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "ENGINE 2: Document Processing Engine",
        "version": "3.0.0",
        "status": "running",
        "capabilities": [
            "PDF Extraction",
            "DOCX Parsing",
            "Excel Reading",
            "LLM-powered Control Extraction",
            "Rwanda NCSA Mapping"
        ],
        "llm_enabled": llm_processor.is_enabled() if llm_processor else False
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    semantic_stats = semantic_matcher.get_statistics() if semantic_matcher else {
        "available": False,
        "model_name": None,
        "total_controls": 0
    }

    return {
        "status": "healthy",
        "pdf_extractor_ready": pdf_extractor is not None,
        "docx_extractor_ready": docx_extractor is not None,
        "excel_extractor_ready": excel_extractor is not None,
        "llm_processor_ready": llm_processor is not None,
        "llm_enabled": llm_processor.is_enabled() if llm_processor else False,
        "control_mapper_ready": control_mapper is not None,
        "semantic_matcher_ready": semantic_matcher is not None,
        "semantic_matcher_enabled": semantic_stats.get("available", False),
        "semantic_model": semantic_stats.get("model_name"),
        "total_rwanda_controls": control_mapper.get_control_count() if control_mapper else 0,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/process/document", response_model=ProcessingResult)
async def process_document(
    file: UploadFile = File(...),
    company_name: str = "Demo Company",
    framework: str = "Rwanda-NCSA",
    background_tasks: BackgroundTasks = None
):
    """
    Process uploaded document and extract compliance controls

    Workflow:
    1. Save uploaded file temporarily
    2. Extract text based on file type (PDF/DOCX/XLSX)
    3. Send text to LLM for control extraction
    4. Map extracted controls to Rwanda NCSA framework
    5. Return structured control data
    """
    import time
    start_time = time.time()

    try:
        # Generate document ID
        doc_id = f"doc_{int(datetime.utcnow().timestamp())}"

        # Get file extension
        file_ext = os.path.splitext(file.filename)[1].lower()

        # Validate file type
        if file_ext not in ['.pdf', '.docx', '.xlsx', '.txt', '.md']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported: PDF, DOCX, XLSX, TXT, MD"
            )

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Extract text based on file type
        print(f"\n📄 Processing: {file.filename} ({file_ext})")

        if file_ext == '.pdf':
            extracted_text = pdf_extractor.extract(tmp_path)
        elif file_ext == '.docx':
            extracted_text = docx_extractor.extract(tmp_path)
        elif file_ext == '.xlsx':
            extracted_text = excel_extractor.extract(tmp_path)
        elif file_ext in ['.txt', '.md']:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        else:
            extracted_text = ""

        print(f"✅ Extracted {len(extracted_text)} characters")

        # Clean up temp file
        os.unlink(tmp_path)

        # Process with LLM to extract controls
        print(f"🤖 Processing with LLM...")
        llm_result = await llm_processor.extract_controls(
            text=extracted_text,
            framework=framework,
            company_name=company_name
        )

        # Map to Rwanda NCSA controls
        print(f"🗺️  Mapping to Rwanda NCSA controls...")

        # Use find_matching_controls with the extracted controls list
        matched_results = control_mapper.find_matching_controls(
            extracted_controls=llm_result['controls'],
            threshold=0.6
        )

        mapped_controls = []
        for match_result in matched_results:
            control = match_result['extracted']
            matched = match_result.get('matched')

            # Get matched control IDs
            matched_ids = []
            if matched:
                matched_ids = [matched['control_id']]

            mapped_controls.append(ExtractedControl(
                control_id=control.get('control_id', 'UNKNOWN'),
                control_name=control.get('control_name', 'Unknown Control'),
                description=control.get('description', ''),
                family=control.get('family', 'General'),
                requirements=control.get('requirements', []),
                mapped_rwanda_controls=matched_ids,
                confidence=match_result.get('match_score', 0.0)
            ))

        processing_time = time.time() - start_time

        print(f"✅ Processing complete: {len(mapped_controls)} controls extracted in {processing_time:.2f}s")

        return ProcessingResult(
            document_id=doc_id,
            filename=file.filename,
            status="completed",
            extracted_text_length=len(extracted_text),
            controls_extracted=len(mapped_controls),
            controls=mapped_controls,
            processing_time_seconds=round(processing_time, 2),
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        print(f"❌ Error processing document: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@app.post("/process/batch")
async def process_batch_documents(
    files: List[UploadFile] = File(...),
    company_name: str = "Demo Company",
    framework: str = "Rwanda-NCSA"
):
    """
    Process multiple documents in batch

    Args:
        files: List of uploaded files
        company_name: Company name for processing
        framework: Compliance framework (default: Rwanda-NCSA)

    Returns:
        List of processing results for each document
    """
    import time
    import asyncio

    start_time = time.time()
    results = []

    print(f"\n📦 Processing batch of {len(files)} documents")

    for idx, file in enumerate(files, 1):
        try:
            print(f"\n[{idx}/{len(files)}] Processing: {file.filename}")

            # Reuse single document processing logic
            # Generate document ID
            doc_id = f"doc_{int(datetime.utcnow().timestamp())}_{idx}"

            # Get file extension
            file_ext = os.path.splitext(file.filename)[1].lower()

            # Validate file type
            if file_ext not in ['.pdf', '.docx', '.xlsx', '.txt', '.md']:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": f"Unsupported file type: {file_ext}"
                })
                continue

            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_path = tmp_file.name

            # Extract text
            if file_ext == '.pdf':
                extracted_text = pdf_extractor.extract(tmp_path)
            elif file_ext == '.docx':
                extracted_text = docx_extractor.extract(tmp_path)
            elif file_ext == '.xlsx':
                extracted_text = excel_extractor.extract(tmp_path)
            elif file_ext in ['.txt', '.md']:
                with open(tmp_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
            else:
                extracted_text = ""

            # Clean up temp file
            os.unlink(tmp_path)

            # Process with LLM
            llm_result = await llm_processor.extract_controls(
                text=extracted_text,
                framework=framework,
                company_name=company_name
            )

            # Map to Rwanda NCSA controls
            matched_results = control_mapper.find_matching_controls(
                extracted_controls=llm_result['controls'],
                threshold=0.6
            )

            # Build result
            results.append({
                "document_id": doc_id,
                "filename": file.filename,
                "status": "success",
                "extracted_text_length": len(extracted_text),
                "controls_extracted": len(matched_results),
                "controls": matched_results
            })

            print(f"✅ [{idx}/{len(files)}] {file.filename}: {len(matched_results)} controls extracted")

        except Exception as e:
            print(f"❌ [{idx}/{len(files)}] Error processing {file.filename}: {str(e)}")
            results.append({
                "filename": file.filename,
                "status": "error",
                "error": str(e)
            })

    total_time = time.time() - start_time
    successful = sum(1 for r in results if r.get('status') == 'success')

    return {
        "batch_id": f"batch_{int(datetime.utcnow().timestamp())}",
        "total_files": len(files),
        "successful": successful,
        "failed": len(files) - successful,
        "processing_time_seconds": round(total_time, 2),
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/extract/text")
async def extract_text_only(file: UploadFile = File(...)):
    """
    Extract text from document without LLM processing
    (Faster, cheaper alternative)
    """
    try:
        file_ext = os.path.splitext(file.filename)[1].lower()

        if file_ext not in ['.pdf', '.docx', '.xlsx', '.txt', '.md']:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}")

        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Extract text
        if file_ext == '.pdf':
            extracted_text = pdf_extractor.extract(tmp_path)
        elif file_ext == '.docx':
            extracted_text = docx_extractor.extract(tmp_path)
        elif file_ext == '.xlsx':
            extracted_text = excel_extractor.extract(tmp_path)
        else:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()

        os.unlink(tmp_path)

        return {
            "filename": file.filename,
            "text": extracted_text,
            "length": len(extracted_text),
            "word_count": len(extracted_text.split())
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction error: {str(e)}")


@app.get("/controls/search")
async def search_controls(query: str, limit: int = 10):
    """
    Search Rwanda NCSA controls by keyword

    Args:
        query: Search term
        limit: Max results to return
    """
    if not control_mapper:
        raise HTTPException(status_code=503, detail="Control mapper not initialized")

    results = control_mapper.search_controls(query)

    # Limit results
    results = results[:limit]

    return {
        "query": query,
        "results_count": len(results),
        "controls": results
    }


@app.get("/controls/families")
async def get_control_families():
    """
    Get all Rwanda NCSA control families
    """
    if not control_mapper:
        raise HTTPException(status_code=503, detail="Control mapper not initialized")

    families = control_mapper.get_families()

    return {
        "total_families": len(families),
        "families": families
    }


@app.get("/controls/{control_id}")
async def get_control_details(control_id: str):
    """
    Get details for a specific control
    """
    if not control_mapper:
        raise HTTPException(status_code=503, detail="Control mapper not initialized")

    control = control_mapper.get_control(control_id)

    if not control:
        raise HTTPException(status_code=404, detail=f"Control {control_id} not found")

    return control


@app.get("/metrics")
async def get_metrics():
    """
    Get runtime metrics for monitoring
    """
    return {
        "total_rwanda_controls": control_mapper.get_control_count() if control_mapper else 0,
        "llm_enabled": llm_processor.is_enabled() if llm_processor else False,
        "supported_formats": ["PDF", "DOCX", "XLSX", "TXT", "MD"],
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Unified Pipeline Evidence Endpoints
# ============================================================================

@app.post("/api/v1/evidence/submit-document")
async def submit_document_evidence(
    audit_id: str,
    file: UploadFile = File(...),
    company_name: str = "Unknown Company"
):
    """
    Process document and submit extracted controls as evidence to unified pipeline.

    This endpoint:
    1. Processes the uploaded document
    2. Extracts controls using LLM
    3. Maps to Rwanda NCSA taxonomy
    4. Converts to ComplianceEvidence format
    5. Stores in Redis via EvidenceManager

    Args:
        audit_id: Parent audit ID
        file: Uploaded policy document
        company_name: Organization name
    """
    if not SHARED_AVAILABLE or not evidence_manager:
        raise HTTPException(
            status_code=503,
            detail="Unified pipeline not available - shared module or Redis not initialized"
        )

    try:
        import time
        import uuid
        start_time = time.time()

        # Get file extension
        file_ext = os.path.splitext(file.filename)[1].lower()

        # Validate file type
        if file_ext not in ['.pdf', '.docx', '.xlsx', '.txt', '.md']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}"
            )

        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        # Extract text based on file type
        print(f"\n📄 Processing: {file.filename} for audit {audit_id}")

        if file_ext == '.pdf':
            extracted_text = pdf_extractor.extract(tmp_path)
        elif file_ext == '.docx':
            extracted_text = docx_extractor.extract(tmp_path)
        elif file_ext == '.xlsx':
            extracted_text = excel_extractor.extract(tmp_path)
        elif file_ext in ['.txt', '.md']:
            with open(tmp_path, 'r', encoding='utf-8') as f:
                extracted_text = f.read()
        else:
            extracted_text = ""

        # Clean up temp file
        os.unlink(tmp_path)

        # Process with LLM to extract controls
        print(f"🤖 Extracting controls with LLM...")
        llm_result = await llm_processor.extract_controls(
            text=extracted_text,
            framework="Rwanda-NCSA",
            company_name=company_name
        )

        # Map to Rwanda NCSA controls
        print(f"🗺️  Mapping to Rwanda NCSA...")
        matched_results = control_mapper.find_matching_controls(
            extracted_controls=llm_result['controls'],
            threshold=0.6
        )

        # Convert all extracted controls to ComplianceEvidence
        evidence_items = []
        for match_result in matched_results:
            control = match_result['extracted']

            # Use matched Rwanda controls if available
            rwanda_matches = match_result.get('matches', [])
            if rwanda_matches:
                # Add matched Rwanda control IDs to metadata
                control['mapped_rwanda_controls'] = [m['control_id'] for m in rwanda_matches]

            # Convert to ComplianceEvidence
            evidence = evidence_converter.convert_extracted_control(
                extracted_control=control,
                audit_id=audit_id,
                source_file=file.filename,
                document_metadata={
                    "type": file_ext[1:],  # Remove dot
                    "company_name": company_name,
                    "size_bytes": len(content)
                }
            )
            evidence_items.append(evidence)

        # Create evidence batch
        batch = EvidenceBatch(
            batch_id=str(uuid.uuid4()),
            audit_id=audit_id,
            source_type=EvidenceSourceType.DOCUMENT,
            evidence_items=evidence_items,
            total_count=len(evidence_items),
            processed_count=len(evidence_items),
            failed_count=0
        )

        # Store batch in Redis
        success = await evidence_manager.store_evidence_batch(batch)

        if not success:
            raise HTTPException(status_code=500, detail="Failed to store evidence batch in Redis")

        processing_time = time.time() - start_time

        print(f"✅ Document evidence batch {batch.batch_id} stored: {batch.processed_count} controls for audit {audit_id}")

        return {
            "success": True,
            "batch_id": batch.batch_id,
            "audit_id": audit_id,
            "filename": file.filename,
            "controls_extracted": batch.processed_count,
            "processing_time_seconds": round(processing_time, 2)
        }

    except Exception as e:
        print(f"⚠️ Document evidence submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")


@app.get("/api/v1/evidence/audit/{audit_id}/documents")
async def get_document_evidence(audit_id: str):
    """
    Retrieve all document evidence for an audit.

    Args:
        audit_id: Audit ID
    """
    if not SHARED_AVAILABLE or not evidence_manager:
        raise HTTPException(
            status_code=503,
            detail="Unified pipeline not available"
        )

    try:
        # Get all document evidence
        evidence_list = await evidence_manager.get_evidence_by_source(
            audit_id,
            EvidenceSourceType.DOCUMENT
        )

        return {
            "audit_id": audit_id,
            "total_count": len(evidence_list),
            "source_type": "document",
            "evidence": [e.model_dump() if hasattr(e, 'model_dump') else e for e in evidence_list]
        }

    except Exception as e:
        print(f"⚠️ Document evidence retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Evidence retrieval failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
