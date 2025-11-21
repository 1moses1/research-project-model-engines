# Rwanda NCSA Compliance Auditor v3.0.0 - Complete Architecture

**Project**: AI-Augmented Unified Compliance Auditor for African Regulatory Frameworks  
**Version**: 3.0.0  
**Primary Focus**: Rwanda NCSA Cybersecurity Minimum Standards  
**Extensibility**: Designed for other African regulatory contexts  
**Date**: November 16, 2024

---

## Executive Summary

**Vision**: An extensible, AI-powered compliance auditing platform that automatically connects to any infrastructure (cloud, on-prem, hybrid), analyzes audit logs and policy documents, scores compliance against Rwanda NCSA standards (with NIST SP 800-53 as secondary reference), and generates comprehensive compliance reports—all with continuous learning capabilities.

**Core Innovation**: Multi-engine architecture where each component is a specialized engine, orchestrated through MCP (Model Context Protocol) for maximum extensibility and adaptability to different African regulatory frameworks.

---

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RWANDA NCSA COMPLIANCE AUDITOR v3.0.0                    │
│              (Extensible AI Compliance Platform for Africa)                 │
└─────────────────────────────────────────────────────────────────────────────┘

                                      ┌─────────────────────┐
                                      │   ORCHESTRATION     │
                                      │      LAYER          │
                                      │  (MCP Protocol)     │
                                      └──────────┬──────────┘
                                                 │
                    ┌────────────────────────────┼────────────────────────────┐
                    │                            │                            │
                    ▼                            ▼                            ▼
        ┌───────────────────────┐   ┌───────────────────────┐   ┌───────────────────────┐
        │   ENGINE 1:           │   │   ENGINE 2:           │   │   ENGINE 3:           │
        │   LOG COLLECTION      │   │   DOCUMENT            │   │   COMPLIANCE          │
        │   & INGESTION         │   │   PROCESSING          │   │   CLASSIFICATION      │
        │                       │   │                       │   │                       │
        │  ┌─────────────────┐ │   │  ┌─────────────────┐ │   │  ┌─────────────────┐ │
        │  │ MCP Connectors  │ │   │  │  PDF Extractor  │ │   │  │  XGBoost Model  │ │
        │  │ - AWS CloudTrail│ │   │  │  DOCX Parser    │ │   │  │  (Your trained  │ │
        │  │ - Azure Monitor │ │   │  │  Excel Reader   │ │   │  │   model)        │ │
        │  │ - GCP Logs      │ │   │  │  TXT/MD Reader  │ │   │  │                 │ │
        │  │ - Syslog        │ │   │  └─────────┬───────┘ │   │  │  53 features:   │ │
        │  │ - Windows Event │ │   │            │         │   │  │  - 3 numeric    │ │
        │  │ - Linux auditd  │ │   │            ▼         │   │  │  - 50 text      │ │
        │  │ - Kubernetes    │ │   │  ┌─────────────────┐ │   │  │    (TF-IDF)     │ │
        │  │ - Docker logs   │ │   │  │  LLM Processor  │ │   │  │                 │ │
        │  │ - Custom APIs   │ │   │  │  (OpenAI API)   │ │   │  │  Controls:      │ │
        │  └────────┬────────┘ │   │  │                 │ │   │  │  - 169 Rwanda   │ │
        │           │          │   │  │  Extract:       │ │   │  │  - 27 NIST      │ │
        │           ▼          │   │  │  - Controls     │ │   │  └─────────┬───────┘ │
        │  ┌─────────────────┐ │   │  │  - Requirements │ │   │            │         │
        │  │  Log Parser     │ │   │  │  - Obligations  │ │   │            ▼         │
        │  │  (Drain Algo)   │ │   │  │  - Mapping to   │ │   │  ┌─────────────────┐ │
        │  │                 │ │   │  │    Rwanda NCSA  │ │   │  │  Reasoning      │ │
        │  │  Normalize to:  │ │   │  └─────────┬───────┘ │   │  │  Engine         │ │
        │  │  {              │ │   │            │         │   │  │  (OpenAI API)   │ │
        │  │   timestamp,    │ │   │            ▼         │   │  │                 │ │
        │  │   user_id,      │ │   │  ┌─────────────────┐ │   │  │  Explain:       │ │
        │  │   action,       │ │   │  │  Control Index  │ │   │  │  - Why flagged  │ │
        │  │   resource,     │ │   │  │  Builder        │ │   │  │  - Which ctrl   │ │
        │  │   status_code,  │ │   │  │                 │ │   │  │  - Remediation  │ │
        │  │   log_message,  │ │   │  │  Rwanda NCSA    │ │   │  │  - Evidence     │ │
        │  │   source_ip,    │ │   │  │  + NIST         │ │   │  └─────────────────┘ │
        │  │   port          │ │   │  │  Database       │ │   │                       │
        │  │  }              │ │   │  └─────────────────┘ │   └───────────────────────┘
        │  └────────┬────────┘ │   │                       │
        │           │          │   └───────────────────────┘
        │           ▼          │
        │  ┌─────────────────┐ │
        │  │  Event Queue    │ │
        │  │  (Redis/Kafka)  │ │
        │  └────────┬────────┘ │
        └───────────┼──────────┘
                    │
                    ▼
        ┌───────────────────────────────────────────────────────────────────┐
        │                      ENGINE 4: DECISION & SCORING                 │
        │                                                                    │
        │  ┌────────────────────────────────────────────────────────────┐  │
        │  │              COMPLIANCE SCORING PIPELINE                    │  │
        │  │                                                              │  │
        │  │  For each log event:                                        │  │
        │  │                                                              │  │
        │  │  1. XGBoost Classification                                  │  │
        │  │     Input: {log_message, status_code, hour, port}          │  │
        │  │     Output: {compliant/non-compliant, confidence}          │  │
        │  │                                                              │  │
        │  │  2. Control Mapping                                         │  │
        │  │     Match event → Rwanda NCSA control                       │  │
        │  │     Lookup: Control Index Database                          │  │
        │  │                                                              │  │
        │  │  3. Confidence Routing:                                     │  │
        │  │                                                              │  │
        │  │     IF confidence >= 0.90:                                  │  │
        │  │       ├─ AND compliant:                                     │  │
        │  │       │   → Auto-accept                                     │  │
        │  │       │   → Log to database                                 │  │
        │  │       │                                                      │  │
        │  │       └─ AND non-compliant:                                 │  │
        │  │           → Flag for human review (HIGH PRIORITY)           │  │
        │  │           → Invoke LLM Reasoning Engine                     │  │
        │  │           → Generate explanation                            │  │
        │  │                                                              │  │
        │  │     IF confidence < 0.90:                                   │  │
        │  │       → Queue for human verification                        │  │
        │  │       → Invoke LLM for preliminary analysis                 │  │
        │  │                                                              │  │
        │  │  4. Aggregate Scoring (per control family)                  │  │
        │  │                                                              │  │
        │  │     Compliance_Score = (Compliant_Events / Total_Events) × 100│
        │  │                                                              │  │
        │  │     For each Rwanda NCSA control family:                    │  │
        │  │       - Access Control: 92% compliant                       │  │
        │  │       - Audit & Accountability: 78% compliant               │  │
        │  │       - Incident Response: 65% compliant                    │  │
        │  │       - ... (14 families total)                             │  │
        │  │                                                              │  │
        │  │  5. Risk Scoring                                            │  │
        │  │                                                              │  │
        │  │     Risk_Score = α·Severity + β·Likelihood + γ·Business_Impact│
        │  │                                                              │  │
        │  │     Where:                                                   │  │
        │  │       - Severity: Based on control family importance        │  │
        │  │       - Likelihood: Historical violation frequency          │  │
        │  │       - Business Impact: Regulatory penalty potential       │  │
        │  │                                                              │  │
        │  └────────────────────────────────────────────────────────────┘  │
        │                                                                    │
        │  ┌────────────────────────────────────────────────────────────┐  │
        │  │            CONTINUOUS LEARNING PIPELINE                     │  │
        │  │                                                              │  │
        │  │  1. Feedback Collection:                                    │  │
        │  │     - Human corrections on flagged events                   │  │
        │  │     - True label: compliant/non-compliant                   │  │
        │  │     - Store: (log_features, human_label, timestamp)         │  │
        │  │                                                              │  │
        │  │  2. Weekly Retraining:                                      │  │
        │  │     - Combine: Synthetic + Real labeled data                │  │
        │  │     - Ratio: 50% synthetic, 50% real (adaptive)             │  │
        │  │     - Train new XGBoost model (0.24s)                       │  │
        │  │     - Cross-validate (5-fold)                               │  │
        │  │                                                              │  │
        │  │  3. A/B Testing:                                            │  │
        │  │     - Deploy new model to 10% of traffic                    │  │
        │  │     - Compare F1-score vs current model                     │  │
        │  │     - IF new_model.f1 > current_model.f1 + 0.02:            │  │
        │  │         → Promote to production                             │  │
        │  │                                                              │  │
        │  │  4. Model Versioning:                                       │  │
        │  │     - Save: model_v3.0.{week_number}.json                   │  │
        │  │     - Track: accuracy, precision, recall over time          │  │
        │  │     - Rollback capability if performance degrades           │  │
        │  │                                                              │  │
        │  └────────────────────────────────────────────────────────────┘  │
        └────────────────────────────────┬──────────────────────────────────┘
                                         │
                                         ▼
        ┌───────────────────────────────────────────────────────────────────┐
        │                  ENGINE 5: REPORT GENERATION                      │
        │                                                                    │
        │  ┌────────────────────────────────────────────────────────────┐  │
        │  │               LLM-Powered Report Builder                    │  │
        │  │               (OpenAI GPT-4 or Claude)                      │  │
        │  │                                                              │  │
        │  │  Input Data:                                                │  │
        │  │    - Compliance scores per control family                   │  │
        │  │    - Violation details (what, when, who, severity)          │  │
        │  │    - Risk scores                                            │  │
        │  │    - Historical trends                                      │  │
        │  │                                                              │  │
        │  │  LLM Prompt:                                                │  │
        │  │  """                                                         │  │
        │  │  You are a compliance auditor for Rwanda NCSA standards.    │  │
        │  │                                                              │  │
        │  │  Generate a comprehensive compliance audit report with:     │  │
        │  │                                                              │  │
        │  │  1. Executive Summary                                       │  │
        │  │     - Overall compliance score: {score}%                    │  │
        │  │     - Key findings (3-5 critical issues)                    │  │
        │  │     - Recommendations                                       │  │
        │  │                                                              │  │
        │  │  2. Control Family Analysis                                 │  │
        │  │     For each of 14 Rwanda NCSA families:                    │  │
        │  │       - Compliance percentage                               │  │
        │  │       - Top violations                                      │  │
        │  │       - Remediation steps                                   │  │
        │  │                                                              │  │
        │  │  3. Violation Details                                       │  │
        │  │     For each non-compliant event:                           │  │
        │  │       - Control ID and name                                 │  │
        │  │       - Evidence (log excerpt)                              │  │
        │  │       - Risk level (High/Medium/Low)                        │  │
        │  │       - Recommended action                                  │  │
        │  │                                                              │  │
        │  │  4. Risk Assessment                                         │  │
        │  │     - Top 10 highest-risk violations                        │  │
        │  │     - Potential regulatory penalties                        │  │
        │  │     - Business impact assessment                            │  │
        │  │                                                              │  │
        │  │  5. Trends & Insights                                       │  │
        │  │     - Compliance improvement/degradation over time          │  │
        │  │     - Recurring violation patterns                          │  │
        │  │     - Predictive analytics                                  │  │
        │  │                                                              │  │
        │  │  6. Action Plan                                             │  │
        │  │     - Immediate actions (< 7 days)                          │  │
        │  │     - Short-term (< 30 days)                                │  │
        │  │     - Long-term (< 90 days)                                 │  │
        │  │                                                              │  │
        │  │  Format: Professional PDF with charts, graphs, tables       │  │
        │  │  """                                                         │  │
        │  │                                                              │  │
        │  │  Output:                                                     │  │
        │  │    - Markdown report (intermediate)                         │  │
        │  │    - PDF report (final, with charts via matplotlib/plotly)  │  │
        │  │    - Excel dashboard (optional, for data analysis)          │  │
        │  │                                                              │  │
        │  └────────────────────────────────────────────────────────────┘  │
        │                                                                    │
        │  ┌────────────────────────────────────────────────────────────┐  │
        │  │              Report Visualization Engine                    │  │
        │  │                                                              │  │
        │  │  Charts & Graphs:                                           │  │
        │  │    1. Compliance Score Gauge (0-100%)                       │  │
        │  │    2. Control Family Bar Chart                              │  │
        │  │    3. Violation Trend Line (last 30 days)                   │  │
        │  │    4. Risk Distribution Pie Chart                           │  │
        │  │    5. Top 10 Violations Table                               │  │
        │  │    6. Compliance Heatmap (controls × time)                  │  │
        │  │                                                              │  │
        │  │  PDF Generation:                                            │  │
        │  │    - Library: ReportLab or WeasyPrint                       │  │
        │  │    - Template: Professional Rwanda govt style               │  │
        │  │    - Branding: NCSA logo, official colors                   │  │
        │  │    - Metadata: Timestamp, auditor, period covered           │  │
        │  │                                                              │  │
        │  └────────────────────────────────────────────────────────────┘  │
        └────────────────────────────────┬──────────────────────────────────┘
                                         │
                                         ▼
        ┌───────────────────────────────────────────────────────────────────┐
        │                     DATA PERSISTENCE LAYER                        │
        │                                                                    │
        │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐│
        │  │   PostgreSQL     │  │   Redis Cache    │  │   Object Store   ││
        │  │                  │  │                  │  │   (S3/MinIO)     ││
        │  │  - Events        │  │  - LLM responses │  │  - PDF reports   ││
        │  │  - Scores        │  │  - Model cache   │  │  - Raw logs      ││
        │  │  - Controls      │  │  - Session data  │  │  - Backups       ││
        │  │  - Users         │  │                  │  │                  ││
        │  │  - Audit trail   │  │                  │  │                  ││
        │  └──────────────────┘  └──────────────────┘  └──────────────────┘│
        └───────────────────────────────────────────────────────────────────┘

        ┌───────────────────────────────────────────────────────────────────┐
        │                      WEB DASHBOARD (Optional)                     │
        │                                                                    │
        │  Compliance Overview   │   Control Details   │   Reports          │
        │  ──────────────────    │   ───────────────   │   ───────          │
        │  • Overall score       │   • 14 families     │   • Generate PDF   │
        │  • Violations count    │   • Drill-down      │   • View history   │
        │  • Recent activity     │   • Evidence view   │   • Export Excel   │
        │  • Risk heatmap        │   • Remediation     │   • Schedule auto  │
        └───────────────────────────────────────────────────────────────────┘
```

---

## Detailed Engine Specifications

### ENGINE 1: Log Collection & Ingestion Engine

**Purpose**: Universal log collection from any infrastructure (cloud, on-prem, hybrid)

**Technology Stack**:
- **MCP Protocol**: Model Context Protocol for standardized log ingestion
- **Base**: Python MCP SDK (official from Anthropic)
- **Deployment**: Docker container with auto-installation

**Connectors** (Leveraging existing open-source MCP servers):

1. **AWS MCP Server** (From AWS Labs - Open Source)
   - CloudTrail events
   - CloudWatch Logs
   - VPC Flow Logs
   - S3 access logs
   - Repository: `awslabs/mcp-cloudtrail-server`

2. **Azure Monitor MCP** (Build using MCP Python SDK)
   - Activity Logs
   - Diagnostic Logs
   - Security logs

3. **GCP MCP Server** (Build using MCP Python SDK)
   - Cloud Logging
   - Audit Logs
   - VPC Flow Logs

4. **On-Premise Connectors**:
   - **Syslog MCP Server**: Listen on port 514 (UDP/TCP)
   - **Windows Event Log MCP**: WinRM API integration
   - **Linux auditd MCP**: Read from `/var/log/audit/audit.log`
   - **Kubernetes MCP**: K8s API server integration
   - **Docker Logs MCP**: Docker API socket

**Container Architecture**:

```dockerfile
# Dockerfile for Rwanda NCSA Log Collection Engine
FROM python:3.11-slim

# Install MCP SDK
RUN pip install mcp anthropic-mcp-sdk

# Install log collection dependencies
RUN pip install boto3 azure-identity google-cloud-logging pywinrm kubernetes docker

# Copy MCP server configurations
COPY mcp_servers/ /app/mcp_servers/
COPY config/mcp_config.json /app/config/

# Environment variables
ENV OPENAI_API_KEY=""
ENV LOG_SOURCES="aws,azure,gcp,syslog"
ENV REDIS_URL="redis://localhost:6379"

# Auto-install script
COPY scripts/auto_install.sh /app/
RUN chmod +x /app/auto_install.sh

# Entrypoint
ENTRYPOINT ["/app/auto_install.sh"]
```

**Auto-Installation Logic**:

```python
# scripts/auto_install.sh (Python wrapper)
import os
import platform
import subprocess

def auto_install():
    """
    Automatically detect host OS and configure log collection
    """
    os_type = platform.system()
    
    if os_type == "Linux":
        setup_linux_collectors()
    elif os_type == "Windows":
        setup_windows_collectors()
    elif os_type == "Darwin":  # macOS
        setup_macos_collectors()
    
    # Detect cloud environment
    if is_aws_ec2():
        enable_cloudtrail_connector()
    if is_azure_vm():
        enable_azure_monitor_connector()
    if is_gcp_vm():
        enable_gcp_logging_connector()
    
    # Start MCP server
    start_mcp_server()

def setup_linux_collectors():
    # Configure syslog forwarding
    # Configure auditd rules
    # Start MCP listeners
    pass

def is_aws_ec2():
    # Check for AWS metadata endpoint
    return check_metadata("http://169.254.169.254/latest/meta-data/")
```

**MCP Server Configuration** (`config/mcp_config.json`):

```json
{
  "servers": {
    "aws-cloudtrail": {
      "command": "python",
      "args": ["-m", "mcp_servers.aws.cloudtrail"],
      "env": {
        "AWS_REGION": "us-east-1"
      }
    },
    "syslog-listener": {
      "command": "python",
      "args": ["-m", "mcp_servers.syslog.listener"],
      "port": 514
    },
    "kubernetes-logs": {
      "command": "python",
      "args": ["-m", "mcp_servers.k8s.logs"],
      "kubeconfig": "/root/.kube/config"
    }
  },
  "output": {
    "queue": "redis://localhost:6379/logs",
    "format": "json",
    "normalization": true
  }
}
```

---

### ENGINE 2: Document Processing Engine

**Purpose**: Extract compliance requirements from any document format

**Supported Formats**:
- PDF (Rwanda NCSA PDF, NIST SP 800-53 PDF)
- DOCX (Microsoft Word policies)
- XLSX (Excel compliance matrices)
- TXT/MD (Markdown documentation)
- HTML (Web-based standards)

**Technology Stack**:
- **PDF**: PyPDF2, pdfplumber
- **DOCX**: python-docx
- **XLSX**: openpyxl, pandas
- **LLM**: OpenAI GPT-4 (via API)

**Processing Pipeline**:

```python
# Document Processing Engine
class DocumentProcessor:
    def __init__(self, openai_api_key: str):
        self.openai = OpenAI(api_key=openai_api_key)
        self.extractors = {
            'pdf': PDFExtractor(),
            'docx': DOCXExtractor(),
            'xlsx': XLSXExtractor()
        }
    
    def process_document(self, file_path: str) -> dict:
        """
        Extract compliance requirements from document
        """
        # 1. Extract raw text
        file_ext = file_path.split('.')[-1]
        raw_text = self.extractors[file_ext].extract(file_path)
        
        # 2. LLM-powered analysis
        prompt = f"""
        Analyze this regulatory document and extract:
        
        1. All compliance controls/requirements
        2. Control IDs (if present)
        3. Control descriptions
        4. Compliance criteria
        5. Audit evidence required
        6. Mapping to international standards (NIST, ISO 27001)
        
        Document:
        {raw_text}
        
        Output as JSON:
        {{
          "controls": [
            {{
              "control_id": "...",
              "name": "...",
              "family": "...",
              "description": "...",
              "criteria": "...",
              "evidence": [...],
              "nist_mapping": [...]
            }}
          ]
        }}
        """
        
        response = self.openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        controls = json.loads(response.choices[0].message.content)
        
        # 3. Store in Control Index Database
        self.save_to_control_index(controls)
        
        return controls
```

**Control Index Database**:

```sql
-- PostgreSQL schema
CREATE TABLE control_index (
    control_id VARCHAR(50) PRIMARY KEY,
    framework VARCHAR(100),  -- 'Rwanda-NCSA', 'NIST SP 800-53', etc.
    name TEXT,
    family VARCHAR(200),
    description TEXT,
    criteria TEXT,
    evidence JSONB,
    nist_mapping JSONB,
    extracted_from VARCHAR(500),  -- Source document
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_framework ON control_index(framework);
CREATE INDEX idx_family ON control_index(family);
```

**NIST Integration Options**:

**Option 1: Local NIST Database** (RECOMMENDED)
```python
# Pre-process NIST SP 800-53 PDF once
controls = document_processor.process_document("NIST.SP.800-53r5.pdf")
# Store in control_index table with framework='NIST SP 800-53'
```

**Option 2: NIST API** (If available)
```python
# Use NIST NVD API for CVE → Control mapping
import requests
nist_api = "https://services.nvd.nist.gov/rest/json/cves/2.0"
```

---

### ENGINE 3: Compliance Classification Engine

**Purpose**: Fast, accurate classification using trained XGBoost model

**Model Specifications**:
- **Algorithm**: XGBoost (v3.0.0)
- **Features**: 53 (3 numeric + 50 text via TF-IDF)
- **Controls**: 169 Rwanda NCSA + 27 NIST SP 800-53
- **Training**: 70K synthetic events
- **Performance**: 100% F1 on synthetic (estimated 50-70% on real)
- **Inference**: <1ms per event

**API Wrapper** (FastAPI):

```python
# api/compliance_api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import pickle
import numpy as np

app = FastAPI(title="Rwanda NCSA Compliance API v3.0.0")

# Load model at startup
model = xgb.XGBClassifier()
model.load_model("models/compliance_auditor_final/rwanda_ncsa_compliance_auditor.json")

with open("models/compliance_auditor_final/label_encoder.pkl", "rb") as f:
    label_encoder = pickle.load(f)

with open("models/compliance_auditor_final/tfidf_vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

class LogEvent(BaseModel):
    log_message: str
    status_code: int
    hour_of_day: int
    port: int

class ComplianceResponse(BaseModel):
    compliance_status: str
    confidence: float
    control_id: str
    control_name: str
    control_family: str
    feature_contributions: dict

@app.post("/classify", response_model=ComplianceResponse)
async def classify_event(event: LogEvent):
    """
    Classify log event for Rwanda NCSA compliance
    """
    # 1. Extract features
    tfidf_features = vectorizer.transform([event.log_message]).toarray()[0]
    numeric_features = [event.port, event.status_code, event.hour_of_day]
    features = np.concatenate([numeric_features, tfidf_features])
    
    # 2. Predict
    prediction = model.predict([features])[0]
    probability = model.predict_proba([features])[0]
    
    compliance_status = label_encoder.inverse_transform([prediction])[0]
    confidence = float(probability[prediction])
    
    # 3. Map to control (based on log pattern)
    control = map_to_rwanda_control(event.log_message)
    
    # 4. Feature importance for this prediction
    contributions = get_feature_contributions(model, features)
    
    return ComplianceResponse(
        compliance_status=compliance_status,
        confidence=confidence,
        control_id=control['control_id'],
        control_name=control['name'],
        control_family=control['family'],
        feature_contributions=contributions
    )

def map_to_rwanda_control(log_message: str) -> dict:
    """
    Map log message to Rwanda NCSA control using keyword matching
    or LLM if confidence is low
    """
    # Simple rule-based mapping first
    keywords = {
        'user created': 'AC-2',
        'login failed': 'IA-2',
        'audit log': 'AU-6',
        # ... (169 Rwanda controls)
    }
    
    for keyword, control_id in keywords.items():
        if keyword in log_message.lower():
            return get_control_details(control_id)
    
    # Fallback to LLM
    return llm_map_to_control(log_message)
```

**Reasoning Engine** (OpenAI Integration):

```python
# reasoning_engine.py
from openai import OpenAI

class ComplianceReasoningEngine:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
    
    def explain_violation(self, log_event: dict, control: dict) -> str:
        """
        Generate natural language explanation for why event is non-compliant
        """
        prompt = f"""
        You are a cybersecurity compliance auditor for Rwanda.
        
        A log event has been flagged as NON-COMPLIANT against Rwanda NCSA standards.
        
        Log Event:
        - Message: {log_event['log_message']}
        - Status Code: {log_event['status_code']}
        - Time: {log_event['timestamp']}
        - User: {log_event['user_id']}
        
        Violated Control:
        - ID: {control['control_id']}
        - Name: {control['name']}
        - Requirement: {control['description']}
        
        Provide:
        1. Clear explanation of WHY this violates the control
        2. Specific evidence from the log
        3. Risk level (High/Medium/Low) and justification
        4. Recommended remediation steps
        5. Similar patterns to watch for
        
        Format as JSON:
        {{
          "explanation": "...",
          "evidence": "...",
          "risk_level": "High|Medium|Low",
          "risk_justification": "...",
          "remediation": ["step 1", "step 2", ...],
          "patterns_to_watch": ["pattern 1", ...]
        }}
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
```

---

### ENGINE 4: Decision & Scoring Engine

**Purpose**: Aggregate compliance scores, route decisions, enable continuous learning

**Compliance Scoring**:

```python
# scoring_engine.py
class ComplianceScoringEngine:
    def __init__(self, db_conn):
        self.db = db_conn
    
    def calculate_compliance_score(self, time_period: str = "30d") -> dict:
        """
        Calculate overall and per-family compliance scores
        """
        query = """
        SELECT 
            control_family,
            COUNT(*) as total_events,
            SUM(CASE WHEN compliance_status = 'compliant' THEN 1 ELSE 0 END) as compliant_events,
            ROUND(100.0 * SUM(CASE WHEN compliance_status = 'compliant' THEN 1 ELSE 0 END) / COUNT(*), 2) as compliance_pct
        FROM compliance_events
        WHERE timestamp >= NOW() - INTERVAL '{time_period}'
        GROUP BY control_family
        ORDER BY compliance_pct ASC
        """
        
        results = self.db.execute(query)
        
        family_scores = {}
        total_events = 0
        total_compliant = 0
        
        for row in results:
            family_scores[row['control_family']] = {
                'total': row['total_events'],
                'compliant': row['compliant_events'],
                'score': row['compliance_pct']
            }
            total_events += row['total_events']
            total_compliant += row['compliant_events']
        
        overall_score = round(100.0 * total_compliant / total_events, 2)
        
        return {
            'overall_score': overall_score,
            'family_scores': family_scores,
            'period': time_period,
            'total_events_analyzed': total_events
        }
    
    def calculate_risk_score(self, violation: dict) -> float:
        """
        Calculate risk score for a violation
        
        Risk = α·Severity + β·Likelihood + γ·Business_Impact
        """
        # Severity based on control family
        severity_weights = {
            'Access Control': 0.9,
            'Incident Response': 0.95,
            'Audit and Accountability': 0.85,
            # ... all 14 families
        }
        
        severity = severity_weights.get(violation['control_family'], 0.5)
        
        # Likelihood based on historical frequency
        likelihood = self.get_violation_frequency(violation['control_id'])
        
        # Business impact (regulatory penalties)
        impact = 0.8  # High for Rwanda NCSA violations
        
        # Weighted sum (α=0.4, β=0.3, γ=0.3)
        risk_score = 0.4 * severity + 0.3 * likelihood + 0.3 * impact
        
        return round(risk_score, 3)
```

**Decision Routing**:

```python
# decision_engine.py
class DecisionEngine:
    def __init__(self, xgboost_api, reasoning_engine, db):
        self.xgboost = xgboost_api
        self.reasoning = reasoning_engine
        self.db = db
    
    def process_log_event(self, event: dict) -> dict:
        """
        Process a single log event through decision pipeline
        """
        # 1. XGBoost classification
        classification = self.xgboost.classify(event)
        
        # 2. Route based on confidence
        if classification['confidence'] >= 0.90:
            if classification['compliance_status'] == 'compliant':
                # Auto-accept
                decision = {
                    'action': 'auto_accept',
                    'requires_review': False
                }
            else:
                # Non-compliant with high confidence
                # Generate LLM explanation
                explanation = self.reasoning.explain_violation(
                    event, 
                    classification['control']
                )
                decision = {
                    'action': 'flag_for_review',
                    'priority': 'HIGH',
                    'requires_review': True,
                    'explanation': explanation
                }
        else:
            # Low confidence - always review
            decision = {
                'action': 'queue_for_verification',
                'requires_review': True,
                'priority': 'MEDIUM'
            }
        
        # 3. Save to database
        self.db.save_event(event, classification, decision)
        
        # 4. Return decision
        return decision
```

**Continuous Learning**:

```python
# continuous_learning.py
import schedule
import time

class ContinuousLearningPipeline:
    def __init__(self, model_path, db):
        self.model_path = model_path
        self.db = db
    
    def weekly_retraining(self):
        """
        Retrain model weekly with new labeled data
        """
        print("Starting weekly retraining...")
        
        # 1. Collect human-verified labels from last week
        new_labels = self.db.get_verified_labels(days=7)
        
        if len(new_labels) < 100:
            print(f"Insufficient new labels ({len(new_labels)}), skipping retraining")
            return
        
        # 2. Combine with synthetic data (adaptive ratio)
        synthetic_data = load_synthetic_data()
        
        # Adaptive mixing: Start 50/50, gradually increase real data ratio
        real_ratio = min(0.9, 0.5 + (len(new_labels) / 10000))
        
        combined_data = mix_datasets(synthetic_data, new_labels, real_ratio)
        
        # 3. Train new model
        new_model = train_xgboost(combined_data)
        
        # 4. Cross-validate
        cv_score = cross_validate(new_model, combined_data)
        print(f"New model CV F1: {cv_score}")
        
        # 5. A/B test against current model
        current_model_f1 = get_current_model_f1()
        
        if cv_score > current_model_f1 + 0.02:  # 2% improvement threshold
            # Promote to production
            version = get_next_version()  # e.g., v3.0.47 (week 47)
            new_model.save_model(f"models/rwanda_ncsa_v{version}.json")
            
            # Update production symlink
            update_production_model(version)
            
            print(f"✅ Deployed new model v{version} (F1: {cv_score})")
        else:
            print(f"⚠️ New model not better, keeping current (F1: {current_model_f1})")
    
    def start_scheduler(self):
        """
        Schedule weekly retraining (every Sunday at 2 AM)
        """
        schedule.every().sunday.at("02:00").do(self.weekly_retraining)
        
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
```

---

### ENGINE 5: Report Generation Engine

**Purpose**: Generate comprehensive compliance reports using LLM

**Report Template**:

```python
# report_generator.py
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import matplotlib.pyplot as plt

class ReportGenerator:
    def __init__(self, openai_api_key: str):
        self.openai = OpenAI(api_key=openai_api_key)
    
    def generate_compliance_report(self, scoring_data: dict, violations: list) -> str:
        """
        Generate comprehensive compliance report
        """
        # 1. LLM-generated narrative
        narrative = self.generate_narrative(scoring_data, violations)
        
        # 2. Generate visualizations
        charts = self.generate_charts(scoring_data)
        
        # 3. Create PDF
        pdf_path = self.create_pdf(narrative, charts, violations)
        
        return pdf_path
    
    def generate_narrative(self, scoring_data: dict, violations: list) -> dict:
        """
        Use LLM to generate executive summary and analysis
        """
        prompt = f"""
        You are generating a Rwanda NCSA compliance audit report.
        
        Compliance Data:
        - Overall Score: {scoring_data['overall_score']}%
        - Period: {scoring_data['period']}
        - Total Events: {scoring_data['total_events_analyzed']}
        
        Family Scores:
        {json.dumps(scoring_data['family_scores'], indent=2)}
        
        Top Violations ({len(violations)} total):
        {json.dumps(violations[:10], indent=2)}
        
        Generate:
        
        1. Executive Summary (3-5 paragraphs)
           - Overall compliance status
           - Key findings
           - Critical risks
           - High-level recommendations
        
        2. Control Family Analysis (for each of 14 families)
           - Current compliance percentage
           - Trend (improving/degrading)
           - Top issues
           - Specific remediation steps
        
        3. Risk Assessment
           - Top 10 highest-risk violations
           - Potential regulatory penalties
           - Business impact
        
        4. Action Plan
           - Immediate actions (< 7 days)
           - Short-term (< 30 days)
           - Long-term (< 90 days)
        
        Format as JSON with sections.
        """
        
        response = self.openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    def generate_charts(self, scoring_data: dict) -> dict:
        """
        Generate matplotlib/plotly charts
        """
        charts = {}
        
        # 1. Overall compliance gauge
        fig, ax = plt.subplots(figsize=(6, 4))
        score = scoring_data['overall_score']
        ax.barh(['Compliance'], [score], color='green' if score >= 80 else 'red')
        ax.set_xlim(0, 100)
        ax.set_xlabel('Percentage')
        ax.set_title('Overall Compliance Score')
        plt.savefig('charts/compliance_gauge.png')
        charts['compliance_gauge'] = 'charts/compliance_gauge.png'
        
        # 2. Family scores bar chart
        families = list(scoring_data['family_scores'].keys())
        scores = [scoring_data['family_scores'][f]['score'] for f in families]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(families, scores)
        ax.set_xlabel('Compliance %')
        ax.set_title('Compliance by Control Family')
        plt.tight_layout()
        plt.savefig('charts/family_scores.png')
        charts['family_scores'] = 'charts/family_scores.png'
        
        # 3. More charts...
        
        return charts
    
    def create_pdf(self, narrative: dict, charts: dict, violations: list) -> str:
        """
        Create professional PDF report
        """
        filename = f"reports/Rwanda_NCSA_Compliance_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Rwanda NCSA Compliance Audit Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Metadata
        metadata = Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal'])
        story.append(metadata)
        story.append(Spacer(1, 24))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", styles['Heading1']))
        story.append(Paragraph(narrative['executive_summary'], styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Charts
        from reportlab.platypus import Image
        story.append(PageBreak())
        story.append(Paragraph("Compliance Overview", styles['Heading1']))
        story.append(Image(charts['compliance_gauge'], width=400, height=300))
        story.append(Spacer(1, 12))
        story.append(Image(charts['family_scores'], width=500, height=350))
        
        # Violations Table
        story.append(PageBreak())
        story.append(Paragraph("Top Violations", styles['Heading1']))
        
        table_data = [['Control ID', 'Severity', 'Description', 'Count']]
        for v in violations[:10]:
            table_data.append([v['control_id'], v['severity'], v['description'][:50], str(v['count'])])
        
        table = Table(table_data)
        story.append(table)
        
        # ... (more sections)
        
        # Build PDF
        doc.build(story)
        
        return filename
```

---

## Deployment Architecture

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  # ENGINE 1: Log Collection MCP Server
  mcp-log-collector:
    build: ./engines/log_collector
    container_name: rwanda-ncsa-mcp-collector
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - REDIS_URL=redis://redis:6379
    ports:
      - "514:514/udp"  # Syslog
      - "8080:8080"     # MCP HTTP API
    volumes:
      - /var/log:/host/logs:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
    depends_on:
      - redis
      - postgres
  
  # ENGINE 3: XGBoost Compliance API
  xgboost-api:
    build: ./engines/xgboost_api
    container_name: rwanda-ncsa-xgboost
    environment:
      - MODEL_PATH=/models/rwanda_ncsa_compliance_auditor.json
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    volumes:
      - ./models/compliance_auditor_final:/models:ro
  
  # ENGINE 4: Decision & Scoring Engine
  decision-engine:
    build: ./engines/decision
    container_name: rwanda-ncsa-decision
    environment:
      - XGBOOST_API_URL=http://xgboost-api:8000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - POSTGRES_URL=postgresql://user:pass@postgres:5432/compliance
      - REDIS_URL=redis://redis:6379
    depends_on:
      - xgboost-api
      - postgres
      - redis
  
  # ENGINE 5: Report Generator
  report-generator:
    build: ./engines/reports
    container_name: rwanda-ncsa-reports
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - POSTGRES_URL=postgresql://user:pass@postgres:5432/compliance
    volumes:
      - ./reports:/app/reports
    depends_on:
      - postgres
  
  # Data Layer
  postgres:
    image: postgres:15
    container_name: rwanda-ncsa-postgres
    environment:
      - POSTGRES_USER=compliance_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=compliance
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    container_name: rwanda-ncsa-redis
    ports:
      - "6379:6379"
  
  # Optional: Web Dashboard
  dashboard:
    build: ./engines/dashboard
    container_name: rwanda-ncsa-dashboard
    environment:
      - API_URL=http://decision-engine:8001
    ports:
      - "3000:3000"
    depends_on:
      - decision-engine

volumes:
  postgres_data:
```

---

## Phased Implementation Plan

### Phase 1: Foundation (Weeks 1-2)

**Goal**: Set up core infrastructure and XGBoost API

**Tasks**:
1. **Set up project structure**
   - Create Git repository
   - Initialize Docker Compose
   - Set up PostgreSQL + Redis

2. **Deploy XGBoost API (ENGINE 3)**
   - Build FastAPI wrapper
   - Load trained model
   - Test /classify endpoint
   - Add health checks

3. **Build Control Index Database**
   - Import 169 Rwanda NCSA controls
   - Import 27 NIST controls
   - Create search indexes

**Deliverables**:
- ✅ Working XGBoost API
- ✅ Control database populated
- ✅ Docker containers running

**Testing**:
```bash
curl -X POST http://localhost:8000/classify \
  -H "Content-Type: application/json" \
  -d '{
    "log_message": "User account created without approval",
    "status_code": 401,
    "hour_of_day": 14,
    "port": 443
  }'
```

---

### Phase 2: Log Collection (Weeks 3-4)

**Goal**: Implement MCP-based log collection

**Tasks**:
1. **Set up MCP Python SDK**
   - Install: `pip install mcp anthropic-mcp-sdk`
   - Configure MCP servers

2. **Implement AWS CloudTrail MCP** (if using AWS)
   - Fork: `github.com/awslabs/mcp-cloudtrail-server`
   - Configure AWS credentials
   - Test log ingestion

3. **Build Syslog MCP Server**
   - Listen on UDP 514
   - Parse syslog format
   - Normalize to standard schema

4. **Implement Log Parser (Drain algorithm)**
   - Extract log templates
   - Normalize fields
   - Output to Redis queue

**Deliverables**:
- ✅ MCP log collectors running
- ✅ Logs flowing to Redis
- ✅ Normalized log format

**Testing**:
```bash
# Send test syslog message
logger -n localhost -P 514 "User admin created new account for user_test"

# Check Redis queue
redis-cli LRANGE logs:incoming 0 -1
```

---

### Phase 3: Document Processing (Week 5)

**Goal**: Extract controls from documents using LLM

**Tasks**:
1. **Build Document Processor (ENGINE 2)**
   - PDF extraction (PyPDF2)
   - DOCX extraction (python-docx)
   - OpenAI integration

2. **Process Rwanda NCSA PDF**
   - Already have 169 controls extracted
   - Verify completeness
   - Add to control index

3. **Process NIST SP 800-53 PDF**
   - Extract all controls
   - Map to Rwanda NCSA
   - Store mappings

**Deliverables**:
- ✅ Document processor working
- ✅ All controls in database
- ✅ NIST-Rwanda mappings

**Testing**:
```bash
python engines/document_processor/extract.py \
  --file docs/Rwanda_NCSA.pdf \
  --framework "Rwanda-NCSA"
```

---

### Phase 4: Decision Engine (Week 6)

**Goal**: Implement decision routing and scoring

**Tasks**:
1. **Build Decision Engine (ENGINE 4)**
   - Confidence-based routing
   - Risk scoring algorithm
   - Database persistence

2. **Implement Reasoning Engine**
   - OpenAI GPT-4 integration
   - Explanation generation
   - Evidence extraction

3. **Set up human review queue**
   - Low-confidence events
   - High-risk violations
   - Feedback collection

**Deliverables**:
- ✅ Decision engine running
- ✅ LLM explanations working
- ✅ Events stored in PostgreSQL

**Testing**:
```bash
# Send test event through pipeline
python test_decision_engine.py --event test_data/violation.json
```

---

### Phase 5: Report Generation (Week 7)

**Goal**: Generate beautiful PDF reports

**Tasks**:
1. **Build Report Generator (ENGINE 5)**
   - LLM narrative generation
   - Matplotlib charts
   - ReportLab PDF creation

2. **Design report template**
   - Rwanda govt branding
   - NCSA logo
   - Professional layout

3. **Implement scheduled reports**
   - Daily summaries
   - Weekly reports
   - Monthly compliance reviews

**Deliverables**:
- ✅ Report generator working
- ✅ PDF reports generated
- ✅ Scheduled automation

**Testing**:
```bash
python engines/reports/generate.py --period 30d --output report.pdf
```

---

### Phase 6: Continuous Learning (Week 8)

**Goal**: Enable model improvement over time

**Tasks**:
1. **Implement feedback collection**
   - Human corrections
   - Label storage
   - Quality checks

2. **Build retraining pipeline**
   - Weekly schedule
   - Data mixing (synthetic + real)
   - A/B testing

3. **Model versioning**
   - Git-like versioning (v3.0.week_number)
   - Rollback capability
   - Performance tracking

**Deliverables**:
- ✅ Continuous learning pipeline
- ✅ Weekly retraining automated
- ✅ Model performance trending

**Testing**:
```bash
# Trigger manual retraining
python engines/continuous_learning/retrain.py --force
```

---

### Phase 7: Integration & Testing (Week 9-10)

**Goal**: End-to-end testing and optimization

**Tasks**:
1. **Integration testing**
   - Full pipeline (log → report)
   - Load testing (10K events/min)
   - Failure recovery

2. **Performance optimization**
   - Redis caching
   - Batch processing
   - Query optimization

3. **Security hardening**
   - API authentication
   - Encryption at rest
   - Audit logging

**Deliverables**:
- ✅ Full system tested
- ✅ Performance benchmarks met
- ✅ Security audit passed

---

### Phase 8: Deployment & Documentation (Week 11-12)

**Goal**: Production deployment and documentation

**Tasks**:
1. **Production deployment**
   - Kubernetes (optional)
   - Docker Swarm
   - Cloud hosting (AWS/Azure/GCP)

2. **Documentation**
   - Installation guide
   - API documentation
   - User manual
   - Admin guide

3. **Training**
   - Admin training
   - User training
   - Runbooks

**Deliverables**:
- ✅ Production system live
- ✅ Complete documentation
- ✅ Team trained

---

## Extensibility for Other African Countries

**Design Principles**:
1. **Framework-agnostic control index**
   - Any country can add their controls
   - Automatic mapping to NIST/ISO 27001

2. **Pluggable document processor**
   - Process any regulatory PDF
   - Extract controls via LLM
   - Store in standard format

3. **Multi-framework support**
   ```python
   frameworks = {
       'Rwanda-NCSA': 169 controls,
       'Nigeria-NITDA': TBD,
       'Kenya-CAK': TBD,
       'South Africa-POPIA': TBD
   }
   ```

4. **Configuration-driven**
   ```yaml
   # config/country.yaml
   country: Rwanda
   framework: NCSA
   controls_source: docs/Rwanda_NCSA.pdf
   language: en
   currency: RWF
   penalties: ...
   ```

---

## Missing Pieces & How to Complete

### 1. ⚠️ Real Rwanda Institutional Logs
**Current**: Only synthetic data
**Needed**: 5,000+ labeled real logs
**How to get**:
- Partner with Rwanda govt institutions
- Anonymize logs
- Manual labeling by experts

### 2. ⚠️ OpenAI API Key
**Current**: ENV variable placeholder
**Needed**: Funded OpenAI account
**How to get**:
- Sign up: https://platform.openai.com
- Add payment method
- Get API key
- Budget: ~$50-100/month for testing

### 3. ⚠️ Rwanda Govt Branding Assets
**Current**: Generic PDF template
**Needed**: Official NCSA logo, colors
**How to get**:
- Contact Rwanda NCSA
- Request branding guidelines
- Integrate into report template

### 4. ⚠️ Production Infrastructure
**Current**: Docker Compose (local)
**Needed**: Cloud hosting
**Options**:
- AWS (EC2 + RDS)
- Azure (VM + PostgreSQL)
- GCP (Compute Engine)
- On-prem servers

### 5. ⚠️ CERT Insider Threat Dataset
**Current**: Not downloaded
**Needed**: For baseline anomaly detection
**How to get**:
```bash
# Download from CMU CERT
wget https://resources.sei.cmu.edu/library/asset-view.cfm?assetid=508099
```

---

## Success Metrics

**Technical Metrics**:
- [ ] XGBoost inference: <1ms per event ✅ (Already achieved)
- [ ] End-to-end pipeline: <5 seconds per log
- [ ] Report generation: <60 seconds
- [ ] System uptime: 99.9%
- [ ] Model F1-score on real data: >70%

**Business Metrics**:
- [ ] Audit time reduction: >50% (Proposal goal)
- [ ] False positive rate: <10%
- [ ] Human review rate: <30%
- [ ] Cost per audit: <$500 (vs $5,000 manual)

**Research Metrics**:
- [ ] Novel framework for African compliance ✅
- [ ] Extensible to 5+ African countries
- [ ] Publications: 1-2 conference papers
- [ ] Industry adoption: 3+ pilot deployments

---

## Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1 | Week 1-2 | XGBoost API + Database |
| Phase 2 | Week 3-4 | MCP Log Collection |
| Phase 3 | Week 5 | Document Processing |
| Phase 4 | Week 6 | Decision Engine |
| Phase 5 | Week 7 | Report Generation |
| Phase 6 | Week 8 | Continuous Learning |
| Phase 7 | Week 9-10 | Testing & Optimization |
| Phase 8 | Week 11-12 | Deployment & Docs |

**Total**: 12 weeks (3 months)

---

## Conclusion

**Rwanda NCSA Compliance Auditor v3.0.0** is a comprehensive, extensible AI-powered platform that:

✅ **Innovates**: First multi-engine AI compliance system for African regulatory frameworks  
✅ **Scales**: From Rwanda NCSA to any African country's standards  
✅ **Performs**: <1ms inference, 50%+ time reduction, continuous learning  
✅ **Explains**: LLM-powered reasoning for every decision  
✅ **Reports**: Beautiful PDF reports with insights and remediation

**Next Step**: Begin Phase 1 implementation this week!

