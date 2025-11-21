# Rwanda NCSA Compliance Auditor - Restructuring Implementation Plan

**Date**: November 21, 2025
**Objective**: Transform monolithic structure into modular, independently deployable microservices
**Status**: 📋 **PLANNING PHASE**

---

## 🎯 Goals & Requirements

### Primary Objectives
1. **Modularity**: Each engine is self-contained with all required dependencies
2. **Independent Deployment**: Each engine can deploy standalone or as part of stack
3. **Clear Repository Structure**: Easy navigation for new developers
4. **Environment Isolation**: Each engine has its own `.env` configuration
5. **Docker Optimization**: Individual Dockerfiles optimized per engine
6. **Extensibility**: Easy to add new regulatory frameworks (e.g., GDPR, HIPAA, ISO 27001)
7. **Maintainability**: Clear separation of concerns, easy to update individual components

### Critical Success Factors
- ✅ **Zero Breaking Changes**: Preserve all existing functionality
- ✅ **Data Integrity**: All model artifacts, taxonomies remain intact
- ✅ **API Compatibility**: No changes to endpoint contracts
- ✅ **Documentation**: Comprehensive README per engine + global docs
- ✅ **Testing**: End-to-end validation before deployment

---

## 📊 Current State Analysis

### Current Structure Issues
```
model-engine/
├── engines/                    # 6 engines (mixed dependencies)
├── data/                       # Shared data (causes coupling)
├── models/                     # Shared models (causes coupling)
├── src/                        # Shared utilities (causes coupling)
├── docs/                       # Mixed documentation
├── 50+ markdown files (root)   # Unorganized documentation
├── 30+ python scripts (root)   # Training/test scripts scattered
└── docker-compose.yml          # Single monolithic compose
```

### Dependency Issues Identified
1. **ENGINE 3 (xgboost_api)**: References `../../models/xgboost_196controls/`
2. **ENGINE 2 (document_processor)**: References `/app/data/processed/control_taxonomy_validated.json`
3. **ENGINE 1 (log_collector)**: References shared control taxonomy
4. **All Engines**: Share common utilities from `src/utils/`
5. **Docker Compose**: Hard-coded volume mounts to shared directories

---

## 🏗️ Target Architecture

### New Structure
```
rwanda-ncsa-compliance-auditor/
│
├── README.md                           # Main repo README
├── GETTING_STARTED.md                  # Quick start guide
├── ARCHITECTURE.md                     # System architecture
├── docker-compose.yml                  # Orchestration for all engines
├── docker-compose.dev.yml              # Development environment
├── .env.example                        # Global environment template
├── .gitignore                          # Git ignore rules
│
├── engines/
│   ├── engine1-log-collector/
│   │   ├── app/                        # Application code
│   │   │   ├── main.py
│   │   │   └── services/               # LLM analyzer, MCP, adapters
│   │   ├── data/                       # Engine-specific data
│   │   │   └── control_taxonomy_validated.json
│   │   ├── models/                     # Placeholder (uses ENGINE 3)
│   │   ├── tests/                      # Unit/integration tests
│   │   ├── Dockerfile                  # Production image
│   │   ├── Dockerfile.dev              # Development image
│   │   ├── requirements.txt            # Python dependencies
│   │   ├── .env.example                # Environment template
│   │   ├── README.md                   # Engine documentation
│   │   └── docker-compose.standalone.yml  # Standalone deployment
│   │
│   ├── engine2-document-processor/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── extractors/             # PDF, DOCX, Excel
│   │   │   └── services/               # LLM, control mapper, semantic matcher
│   │   ├── data/
│   │   │   ├── control_taxonomy_validated.json
│   │   │   └── embeddings/             # Sentence transformer cache
│   │   ├── sample_documents/           # Test PDFs from Alvin Tech
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── README.md
│   │
│   ├── engine3-xgboost-classifier/
│   │   ├── app/
│   │   │   └── main.py                 # FastAPI app
│   │   ├── models/                     # Self-contained model artifacts
│   │   │   ├── rwanda_ncsa_compliance_auditor.json
│   │   │   ├── label_encoder.pkl
│   │   │   ├── day_encoder.pkl
│   │   │   ├── tfidf_vectorizer.pkl
│   │   │   ├── features.json
│   │   │   └── model_metrics.json
│   │   ├── training/                   # Training scripts
│   │   │   ├── train_xgboost.py
│   │   │   └── generate_training_data.py
│   │   ├── data/                       # Training data cache
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── README.md
│   │
│   ├── engine4-decision-engine/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   └── services/               # Scoring, aggregation
│   │   ├── tests/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example
│   │   └── README.md
│   │
│   ├── engine5-web-ui/
│   │   ├── backend/
│   │   │   ├── app/
│   │   │   ├── Dockerfile
│   │   │   ├── requirements.txt
│   │   │   └── .env.example
│   │   ├── frontend/
│   │   │   ├── src/
│   │   │   ├── Dockerfile
│   │   │   ├── package.json
│   │   │   └── .env.example
│   │   └── README.md
│   │
│   └── engine6-report-generator/
│       ├── app/
│       │   ├── main.py
│       │   └── services/               # Report generation
│       ├── templates/                  # Report templates
│       ├── tests/
│       ├── Dockerfile
│       ├── requirements.txt
│       ├── .env.example
│       └── README.md
│
├── shared/                             # OPTIONAL: Truly shared resources
│   ├── control-taxonomies/             # Regulatory frameworks
│   │   ├── rwanda-ncsa/
│   │   │   └── control_taxonomy_validated.json
│   │   ├── nist-sp-800-53/
│   │   ├── gdpr/                       # Future framework
│   │   ├── hipaa/                      # Future framework
│   │   └── iso-27001/                  # Future framework
│   └── README.md                       # Shared resources guide
│
├── docs/                               # Consolidated documentation
│   ├── architecture/
│   │   ├── system-overview.md
│   │   ├── engine1-log-collector.md
│   │   ├── engine2-document-processor.md
│   │   ├── engine3-xgboost-classifier.md
│   │   ├── engine4-decision-engine.md
│   │   ├── engine5-web-ui.md
│   │   └── engine6-report-generator.md
│   ├── deployment/
│   │   ├── docker-deployment.md
│   │   ├── kubernetes-deployment.md
│   │   └── production-checklist.md
│   ├── api/
│   │   ├── engine1-api.md
│   │   ├── engine2-api.md
│   │   ├── engine3-api.md
│   │   └── ...
│   ├── research/
│   │   ├── phd-statement.md
│   │   ├── mathematical-formulations.pdf
│   │   └── training-results-analysis.md
│   ├── regulatory-frameworks/
│   │   ├── rwanda-ncsa-analysis.md
│   │   └── Artificial_Intelligence_Policy.pdf
│   └── sample-policy-docs/            # Alvin Tech sample docs
│       └── Company's Security Report To Audit/
│
├── scripts/                            # Utility scripts
│   ├── setup/
│   │   ├── setup.sh                   # Complete setup
│   │   └── setup-dev.sh               # Development setup
│   ├── deployment/
│   │   ├── deploy-all.sh              # Deploy all engines
│   │   ├── deploy-engine.sh           # Deploy single engine
│   │   └── health-check.sh            # Health check all
│   ├── testing/
│   │   ├── test-all-engines.sh
│   │   └── integration-test.sh
│   └── maintenance/
│       ├── backup-data.sh
│       └── cleanup.sh
│
└── tests/                              # Integration tests
    ├── integration/
    │   ├── test_full_flow.py
    │   ├── test_engine1_to_engine3.py
    │   └── test_batch_document_processing.py
    └── e2e/
        └── test_demo_scenario.py
```

---

## 📋 Detailed Implementation Plan

### Phase 1: Preparation & Backup (30 minutes)
**Goal**: Ensure safe rollback capability

#### 1.1 Backup Current State
- [ ] Create full backup of project: `rwanda-ncsa-backup-2025-11-21.tar.gz`
- [ ] Document current working state
- [ ] Tag current git commit: `v2.0.0-pre-restructure`
- [ ] Export current docker images

#### 1.2 Stop Running Services
- [ ] Stop all running Docker containers
- [ ] Kill background bash processes
- [ ] Clear dangling volumes/networks

**Commands**:
```bash
# Backup
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT"
tar -czf rwanda-ncsa-backup-2025-11-21.tar.gz model-engine/

# Stop services
cd model-engine
docker-compose down -v
docker system prune -f

# Stop background processes
# (Manually kill bash shells if needed)
```

---

### Phase 2: Create New Directory Structure (45 minutes)
**Goal**: Establish modular architecture

#### 2.1 Create Root Structure
- [ ] Create `docs/` subdirectories
- [ ] Create `scripts/` subdirectories
- [ ] Create `tests/` subdirectories
- [ ] Create `shared/control-taxonomies/`

#### 2.2 Reorganize Documentation (15 minutes)
- [ ] Move all `.md` files from root to appropriate `docs/` subdirectories
- [ ] Create master `README.md` in root
- [ ] Create `GETTING_STARTED.md` with quick start
- [ ] Create `ARCHITECTURE.md` with system diagram

**Actions**:
- Move `SESSION_SUMMARY_*.md` → `docs/research/`
- Move `ENGINE*_IMPLEMENTATION_COMPLETE.md` → `docs/architecture/`
- Move `*_DEPLOYMENT_*.md` → `docs/deployment/`
- Move `MATHEMATICAL_FORMULATIONS.*` → `docs/research/`
- Move `PhD_Statement_of_Purpose.md` → `docs/research/`

---

### Phase 3: Restructure ENGINE 3 (XGBoost Classifier) (60 minutes)
**Goal**: Make ENGINE 3 fully self-contained

#### 3.1 Copy Model Artifacts
- [ ] Copy `models/xgboost_196controls/` → `engines/engine3-xgboost-classifier/models/`
- [ ] Verify all model files present (7 files)

#### 3.2 Update Code References
- [ ] Update `main.py`: Change `MODEL_DIR` logic to use `/app/models/` (local)
- [ ] Remove relative path resolution (`../../models/`)
- [ ] Add fallback to `/app/models/` for Docker

#### 3.3 Add Training Scripts
- [ ] Copy `retrain_xgboost_optimized.py` → `engines/engine3-xgboost-classifier/training/train_xgboost.py`
- [ ] Copy `generate_full_training_data.py` → `engines/engine3-xgboost-classifier/training/`
- [ ] Update paths in training scripts to be self-contained

#### 3.4 Create Environment Configuration
- [ ] Create `.env.example`:
```env
# ENGINE 3: XGBoost Classifier Configuration
MODEL_PATH=/app/models/rwanda_ncsa_compliance_auditor.json
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

#### 3.5 Update Dockerfile
- [ ] Copy model artifacts during build
- [ ] Optimize image size
- [ ] Add healthcheck

#### 3.6 Create Standalone Deployment
- [ ] Create `docker-compose.standalone.yml`
- [ ] Test standalone deployment

---

### Phase 4: Restructure ENGINE 2 (Document Processor) (60 minutes)
**Goal**: Make ENGINE 2 self-contained with LLM capabilities

#### 4.1 Copy Dependencies
- [ ] Copy `data/processed/control_taxonomy_validated.json` → `engines/engine2-document-processor/data/`
- [ ] Create `sample_documents/` folder
- [ ] Copy Alvin Tech PDFs → `sample_documents/`

#### 4.2 Update Code References
- [ ] Update `llm_processor.py`: Change taxonomy path to `/app/data/control_taxonomy_validated.json`
- [ ] Update `control_mapper.py`: Use local data path
- [ ] Update `semantic_matcher.py`: Use local embeddings cache

#### 4.3 Add Embeddings Cache
- [ ] Create `data/embeddings/` directory
- [ ] Pre-download sentence-transformers model (all-MiniLM-L6-v2)
- [ ] Cache in Docker image to avoid download on startup

#### 4.4 Environment Configuration
- [ ] Create `.env.example`:
```env
# ENGINE 2: Document Processor Configuration
OPENAI_API_KEY=your_openai_api_key_here
CONTROL_TAXONOMY_PATH=/app/data/control_taxonomy_validated.json
EMBEDDINGS_CACHE=/app/data/embeddings
HOST=0.0.0.0
PORT=8002
MAX_FILE_SIZE_MB=50
BATCH_SIZE=10
```

#### 4.5 Create Comprehensive README
- [ ] API documentation
- [ ] Batch upload examples
- [ ] Sample document processing guide

---

### Phase 5: Restructure ENGINE 1 (Log Collector) (60 minutes)
**Goal**: Make ENGINE 1 self-contained with LLM log analysis

#### 5.1 Copy Dependencies
- [ ] Copy `data/processed/control_taxonomy_validated.json` → `engines/engine1-log-collector/data/`

#### 5.2 Update Code References
- [ ] Update `llm_log_analyzer.py`: Use `/app/data/control_taxonomy_validated.json`
- [ ] Verify all service imports are relative

#### 5.3 Add Sample Logs
- [ ] Create `sample_logs/` directory
- [ ] Generate sample syslog messages
- [ ] Add sample Windows Event Logs
- [ ] Add sample JSON logs

#### 5.4 Environment Configuration
- [ ] Create `.env.example`:
```env
# ENGINE 1: Log Collector Configuration
OPENAI_API_KEY=your_openai_api_key_here
CONTROL_TAXONOMY_PATH=/app/data/control_taxonomy_validated.json
ENGINE3_URL=http://engine3-xgboost-classifier:8000
ENGINE4_URL=http://engine4-decision-engine:8001
HOST=0.0.0.0
PORT=8001
MCP_COMMAND_TIMEOUT=30
LOG_BUFFER_SIZE=1000
```

#### 5.5 MCP Server Testing
- [ ] Add script to read local system logs
- [ ] Test `journalctl` integration
- [ ] Test `/var/log/system.log` reading

---

### Phase 6: Restructure ENGINE 4, 5, 6 (45 minutes)
**Goal**: Complete modularization

#### 6.1 ENGINE 4 (Decision Engine)
- [ ] Create `.env.example`
- [ ] Update dependencies
- [ ] Test standalone deployment

#### 6.2 ENGINE 5 (Web UI)
- [ ] Separate backend/frontend configs
- [ ] Create `.env.example` for each
- [ ] Update API endpoints to use env vars

#### 6.3 ENGINE 6 (Report Generator)
- [ ] Create `.env.example`
- [ ] Add report templates to engine directory
- [ ] Update dependencies

---

### Phase 7: Shared Resources (30 minutes)
**Goal**: Organize truly shared resources for extensibility

#### 7.1 Create Control Taxonomy Library
- [ ] Create `shared/control-taxonomies/rwanda-ncsa/`
- [ ] Copy validated taxonomy
- [ ] Create README explaining structure

#### 7.2 Prepare for Future Frameworks
- [ ] Create placeholder directories:
  - `shared/control-taxonomies/nist-sp-800-53/`
  - `shared/control-taxonomies/gdpr/`
  - `shared/control-taxonomies/hipaa/`
  - `shared/control-taxonomies/iso-27001/`
- [ ] Create template: `control_taxonomy_template.json`
- [ ] Document framework addition process

---

### Phase 8: Docker Optimization (60 minutes)
**Goal**: Optimize each Dockerfile, create orchestration

#### 8.1 Update Individual Dockerfiles
**ENGINE 1:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY data/ ./data/

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')"

EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

**ENGINE 2:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PDF/DOCX processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download sentence-transformers model
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY app/ ./app/
COPY data/ ./data/
COPY sample_documents/ ./sample_documents/

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8002/health')"

EXPOSE 8002
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
```

**ENGINE 3:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY models/ ./models/

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 8.2 Create New docker-compose.yml
```yaml
version: '3.8'

services:
  engine1-log-collector:
    build: ./engines/engine1-log-collector
    container_name: engine1-log-collector
    env_file:
      - ./engines/engine1-log-collector/.env
    ports:
      - "8001:8001"
    depends_on:
      - engine3-xgboost-classifier
      - engine4-decision-engine
    networks:
      - rwanda-ncsa-net

  engine2-document-processor:
    build: ./engines/engine2-document-processor
    container_name: engine2-document-processor
    env_file:
      - ./engines/engine2-document-processor/.env
    ports:
      - "8002:8002"
    volumes:
      - document_uploads:/app/uploads
    networks:
      - rwanda-ncsa-net

  engine3-xgboost-classifier:
    build: ./engines/engine3-xgboost-classifier
    container_name: engine3-xgboost-classifier
    env_file:
      - ./engines/engine3-xgboost-classifier/.env
    ports:
      - "8000:8000"
    networks:
      - rwanda-ncsa-net

  engine4-decision-engine:
    build: ./engines/engine4-decision-engine
    container_name: engine4-decision-engine
    env_file:
      - ./engines/engine4-decision-engine/.env
    ports:
      - "8003:8003"
    depends_on:
      - postgres
      - engine3-xgboost-classifier
    networks:
      - rwanda-ncsa-net

  engine5-web-ui-backend:
    build: ./engines/engine5-web-ui/backend
    container_name: engine5-web-ui-backend
    env_file:
      - ./engines/engine5-web-ui/backend/.env
    ports:
      - "8006:8006"
    depends_on:
      - postgres
      - redis
      - engine3-xgboost-classifier
    networks:
      - rwanda-ncsa-net

  engine5-web-ui-frontend:
    build: ./engines/engine5-web-ui/frontend
    container_name: engine5-web-ui-frontend
    env_file:
      - ./engines/engine5-web-ui/frontend/.env
    ports:
      - "3000:80"
    depends_on:
      - engine5-web-ui-backend
    networks:
      - rwanda-ncsa-net

  engine6-report-generator:
    build: ./engines/engine6-report-generator
    container_name: engine6-report-generator
    env_file:
      - ./engines/engine6-report-generator/.env
    ports:
      - "8004:8004"
    volumes:
      - report_outputs:/app/reports
    networks:
      - rwanda-ncsa-net

  postgres:
    image: postgres:15-alpine
    container_name: rwanda-ncsa-postgres
    environment:
      POSTGRES_DB: compliance_db
      POSTGRES_USER: compliance_user
      POSTGRES_PASSWORD: compliance_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - rwanda-ncsa-net

  redis:
    image: redis:7-alpine
    container_name: rwanda-ncsa-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - rwanda-ncsa-net

volumes:
  postgres_data:
  redis_data:
  document_uploads:
  report_outputs:

networks:
  rwanda-ncsa-net:
    driver: bridge
```

#### 8.3 Create Standalone docker-compose Files
- [ ] Create `docker-compose.standalone.yml` for each engine
- [ ] Test standalone deployment for each engine

---

### Phase 9: Testing & Validation (90 minutes)
**Goal**: Comprehensive end-to-end testing

#### 9.1 Unit Tests (Per Engine)
- [ ] ENGINE 1: Test log parsing, LLM analysis
- [ ] ENGINE 2: Test document processing, batch upload
- [ ] ENGINE 3: Test XGBoost inference
- [ ] ENGINE 4: Test decision logic
- [ ] ENGINE 5: Test web UI
- [ ] ENGINE 6: Test report generation

#### 9.2 Integration Tests
**Test Scenario 1: Log Processing Flow**
```python
# Test: Log → ENGINE 1 → ENGINE 3 → ENGINE 4
1. Send syslog message to ENGINE 1
2. Verify LLM analysis
3. Verify ENGINE 3 classification
4. Verify ENGINE 4 decision
5. Check results in database
```

**Test Scenario 2: Document Processing Flow**
```python
# Test: Batch Documents → ENGINE 2 → Control Mapping
1. Upload 5 Alvin Tech PDFs to ENGINE 2 (batch endpoint)
2. Verify LLM extraction
3. Verify semantic matching (196 controls)
4. Check confidence scores
5. Validate output format
```

**Test Scenario 3: Full Stack Integration**
```python
# Test: UI → Document → Classification → Report
1. Upload document via ENGINE 5 (Web UI)
2. Process via ENGINE 2
3. Classify via ENGINE 3
4. Aggregate via ENGINE 4
5. Generate report via ENGINE 6
6. Display in UI
```

#### 9.3 Performance Testing
- [ ] Measure ENGINE 3 inference time (target: <10ms)
- [ ] Measure ENGINE 2 batch processing (5 PDFs)
- [ ] Measure ENGINE 1 LLM latency (~100ms)

---

### Phase 10: Documentation (60 minutes)
**Goal**: Create comprehensive, accessible documentation

#### 10.1 Root README.md
```markdown
# Rwanda NCSA Cybersecurity Compliance Auditor

AI-powered compliance monitoring system for Rwanda NCSA Cybersecurity Minimum Standards.

## Quick Start
```bash
# Clone repository
git clone https://github.com/your-org/rwanda-ncsa-compliance-auditor.git
cd rwanda-ncsa-compliance-auditor

# Setup environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Deploy all engines
docker-compose up -d

# Access Web UI
open http://localhost:3000
```

## Architecture
- **ENGINE 1**: Log Collection & Analysis (LLM-powered)
- **ENGINE 2**: Document Processing (LLM-powered)
- **ENGINE 3**: XGBoost Compliance Classifier
- **ENGINE 4**: Decision & Scoring Engine
- **ENGINE 5**: Web UI (React + FastAPI)
- **ENGINE 6**: Report Generator

## Documentation
- [Getting Started](./GETTING_STARTED.md)
- [Architecture Overview](./docs/architecture/system-overview.md)
- [API Documentation](./docs/api/)
- [Deployment Guide](./docs/deployment/docker-deployment.md)
```

#### 10.2 Per-Engine README
Each engine gets comprehensive README with:
- Purpose & capabilities
- API endpoints
- Environment variables
- Standalone deployment
- Testing guide
- Example usage

#### 10.3 GETTING_STARTED.md
- Prerequisites (Docker, Python, API keys)
- 5-minute quick start
- Common issues & troubleshooting

---

### Phase 11: Demo Preparation (60 minutes)
**Goal**: Prepare for faculty demo

#### 11.1 Sample Data Preparation
- [ ] Create realistic syslog messages (from host machine)
- [ ] Prepare Alvin Tech PDFs for batch upload
- [ ] Create demo script/walkthrough

#### 11.2 Demo Script
```
1. System Overview (2 min)
   - Show architecture diagram
   - Explain 6 engines

2. ENGINE 3 Demo (5 min)
   - Show XGBoost API
   - Send log event
   - Show classification (196 controls)

3. ENGINE 2 Demo (5 min)
   - Batch upload 5 Alvin Tech PDFs
   - Show LLM extraction
   - Show semantic matching to Rwanda NCSA controls

4. ENGINE 1 Demo (5 min)
   - Collect logs from host machine (journalctl)
   - Show LLM semantic analysis
   - Show automatic control mapping

5. Full Stack Demo (8 min)
   - Upload document via Web UI
   - Process → Classify → Report
   - Show compliance dashboard

6. Q&A (5 min)
```

#### 11.3 Backup Plan
- [ ] Pre-generate results in case of network issues
- [ ] Screenshots of successful runs
- [ ] Recorded demo video (backup)

---

## 🔄 Execution Checklist

### Pre-Execution
- [ ] ✅ Review entire plan with user
- [ ] ✅ Get approval to proceed
- [ ] ✅ Create backup
- [ ] ✅ Document current state

### Phase Execution
- [ ] Phase 1: Preparation & Backup
- [ ] Phase 2: Create New Directory Structure
- [ ] Phase 3: Restructure ENGINE 3
- [ ] Phase 4: Restructure ENGINE 2
- [ ] Phase 5: Restructure ENGINE 1
- [ ] Phase 6: Restructure ENGINE 4, 5, 6
- [ ] Phase 7: Shared Resources
- [ ] Phase 8: Docker Optimization
- [ ] Phase 9: Testing & Validation
- [ ] Phase 10: Documentation
- [ ] Phase 11: Demo Preparation

### Post-Execution
- [ ] Full system deployment test
- [ ] Performance benchmarking
- [ ] Documentation review
- [ ] Demo rehearsal
- [ ] Commit to Git
- [ ] Tag release: `v3.0.0-modular`

---

## 🎯 Success Criteria

### Technical
- [ ] All 6 engines deploy independently
- [ ] All 6 engines deploy together via docker-compose
- [ ] All API endpoints functional
- [ ] Zero breaking changes
- [ ] All tests passing
- [ ] Performance targets met

### Documentation
- [ ] Clear root README
- [ ] Comprehensive per-engine docs
- [ ] API documentation complete
- [ ] Demo script ready

### Extensibility
- [ ] New framework addition documented
- [ ] Control taxonomy structure clear
- [ ] Easy to navigate for new developers

---

## 🚨 Risks & Mitigation

### Risk 1: Breaking Changes
**Mitigation**:
- Comprehensive backup before starting
- Test each phase before moving to next
- Rollback plan ready

### Risk 2: Path Resolution Issues
**Mitigation**:
- Test both local and Docker paths
- Use environment variables for flexibility
- Fallback logic in code

### Risk 3: Time Overrun
**Mitigation**:
- Focus on critical engines first (1, 2, 3)
- Can defer ENGINE 5, 6 if needed
- Prioritize demo functionality

---

## 📊 Estimated Timeline

| Phase | Duration | Critical Path |
|-------|----------|---------------|
| Phase 1 | 30 min | ✅ Yes |
| Phase 2 | 45 min | ✅ Yes |
| Phase 3 | 60 min | ✅ Yes (ENGINE 3 critical) |
| Phase 4 | 60 min | ✅ Yes (ENGINE 2 critical) |
| Phase 5 | 60 min | ✅ Yes (ENGINE 1 critical) |
| Phase 6 | 45 min | ⚠️ Partial (ENGINE 4 critical) |
| Phase 7 | 30 min | ❌ No (nice-to-have) |
| Phase 8 | 60 min | ✅ Yes |
| Phase 9 | 90 min | ✅ Yes |
| Phase 10 | 60 min | ⚠️ Partial |
| Phase 11 | 60 min | ✅ Yes (for demo) |
| **Total** | **9 hours** | **Core: 6-7 hours** |

---

## 🎓 Next Steps After Approval

1. **User Review**: Review this plan and provide feedback
2. **Approval**: Get go-ahead to proceed
3. **Backup**: Create complete backup (Phase 1)
4. **Execute**: Follow phases sequentially
5. **Test**: Comprehensive testing (Phase 9)
6. **Demo**: Prepare and rehearse (Phase 11)

---

**Status**: ⏸️ **AWAITING APPROVAL**
**Ready to Execute**: Upon user confirmation
**Estimated Completion**: 6-9 hours of focused work

---

**This plan ensures zero data loss, full functionality preservation, and sets foundation for extensible, production-ready microservices architecture.**
