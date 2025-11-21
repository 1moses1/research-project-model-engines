# ENGINE 2: Document Processing Engine

**Rwanda NCSA Compliance Auditor v3.0.0**

LLM-powered document processing engine that extracts compliance controls from policy documents and maps them to the Rwanda NCSA framework.

## Features

### Document Processing
- **Multi-format Support**: PDF, DOCX, Excel, TXT, Markdown
- **Text Extraction**: Robust extraction from various document types
- **Table Support**: Extracts data from tables in Word and Excel documents
- **Large File Handling**: Processes documents up to 10MB

### LLM Control Extraction
- **OpenAI GPT-4 Integration**: Intelligent control extraction using LLM
- **Mock Mode Fallback**: Works without API key for testing
- **Structured Output**: Extracts control ID, name, description, family, requirements
- **Confidence Scoring**: Each extracted control includes confidence score

### Control Mapping
- **Rwanda NCSA Mapping**: Maps extracted controls to Rwanda NCSA taxonomy
- **Fuzzy Matching**: Uses similarity algorithms for control matching
- **Multi-framework Support**: Supports NIST and Rwanda NCSA controls
- **Search & Validation**: Search controls by keyword, validate control IDs

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Document Upload (API)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────▼──────────┐
          │  File Type Router   │
          └─────────┬───────────┘
                    │
        ┌───────────┴───────────┬────────────┬──────────┐
        │                       │            │          │
   ┌────▼────┐           ┌─────▼─────┐ ┌───▼───┐ ┌───▼───┐
   │   PDF   │           │   DOCX    │ │ Excel │ │  TXT  │
   │Extractor│           │ Extractor │ │Extract│ │ Read  │
   └────┬────┘           └─────┬─────┘ └───┬───┘ └───┬───┘
        │                      │            │         │
        └──────────────────────┴────────────┴─────────┘
                               │
                    ┌──────────▼──────────┐
                    │   LLM Processor     │
                    │  (OpenAI GPT-4)     │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Control Mapper     │
                    │ (Rwanda NCSA Match) │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   JSON Response     │
                    │  (Mapped Controls)  │
                    └─────────────────────┘
```

## API Endpoints

### Document Processing

#### `POST /process/document`
Upload and process a document to extract compliance controls

**Request:**
```bash
curl -X POST "http://localhost:8002/process/document" \
  -F "file=@policy_document.pdf" \
  -F "company_name=Acme Corp" \
  -F "framework=Rwanda-NCSA"
```

**Response:**
```json
{
  "success": true,
  "filename": "policy_document.pdf",
  "company_name": "Acme Corp",
  "framework": "Rwanda-NCSA",
  "processing_time": 2.34,
  "extracted_text_length": 15234,
  "controls_extracted": 12,
  "controls_mapped": 10,
  "llm_enabled": true,
  "controls": [
    {
      "extracted": {
        "control_id": "AC-1",
        "control_name": "Access Control Policy",
        "description": "...",
        "family": "Access Control",
        "requirements": ["..."],
        "confidence": 0.92
      },
      "matched": {
        "control_id": "NCSA-AC-01",
        "control_name": "Access Control Policy and Procedures",
        "description": "...",
        "family": "Access Control"
      },
      "match_score": 0.87,
      "match_method": "fuzzy_match"
    }
  ]
}
```

### Control Search

#### `GET /controls/search`
Search for controls by keyword

**Request:**
```bash
curl "http://localhost:8002/controls/search?query=encryption&limit=10"
```

**Response:**
```json
{
  "query": "encryption",
  "results_count": 5,
  "results": [
    {
      "control": {
        "control_id": "NCSA-SC-13",
        "control_name": "Cryptographic Protection",
        "description": "...",
        "family": "System and Communications Protection"
      },
      "relevance": 0.89,
      "matched_field": "description"
    }
  ]
}
```

#### `GET /controls/{control_id}`
Get specific control by ID

**Request:**
```bash
curl "http://localhost:8002/controls/NCSA-AC-01"
```

**Response:**
```json
{
  "control_id": "NCSA-AC-01",
  "control_name": "Access Control Policy and Procedures",
  "description": "The organization develops, documents, and disseminates access control policies...",
  "family": "Access Control",
  "requirements": ["...", "..."],
  "log_indicators": ["login", "logout", "access denied"]
}
```

### System Information

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "Document Processing Engine",
  "version": "1.0.0"
}
```

#### `GET /stats`
Get processing statistics

**Response:**
```json
{
  "total_controls": 169,
  "rwanda_ncsa_controls": 21,
  "nist_controls": 29,
  "control_families": 12,
  "llm_enabled": true,
  "supported_formats": ["pdf", "docx", "xlsx", "txt", "md"]
}
```

## Installation

### Prerequisites
- Python 3.11+
- OpenAI API key (optional, for LLM extraction)
- Docker & Docker Compose (for containerized deployment)

### Local Development

```bash
# Navigate to ENGINE 2 directory
cd engines/document_processor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"
export CONTROL_TAXONOMY_PATH="../../data/processed/control_taxonomy_validated.json"

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d document-processor

# View logs
docker-compose logs -f document-processor

# Stop service
docker-compose down
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | None (uses mock mode) |
| `CONTROL_TAXONOMY_PATH` | Path to control taxonomy JSON | `data/processed/control_taxonomy_validated.json` |
| `MAX_FILE_SIZE` | Maximum upload file size (bytes) | 10485760 (10MB) |
| `PORT` | Server port | 8002 |

### Supported File Formats

| Format | Extension | Max Size | Tables | Images |
|--------|-----------|----------|--------|--------|
| PDF | `.pdf` | 10MB | ✓ | Text only |
| Word | `.docx` | 10MB | ✓ | Text only |
| Excel | `.xlsx` | 10MB | ✓ | N/A |
| Text | `.txt` | 10MB | - | - |
| Markdown | `.md` | 10MB | - | - |

## LLM Processing

### OpenAI Mode (Production)

When `OPENAI_API_KEY` is provided:
- Uses GPT-4 for intelligent control extraction
- Analyzes document context and semantics
- Extracts structured control information
- Provides high-accuracy confidence scores

**Prompt Engineering:**
```python
You are a compliance auditor analyzing policy documents for {company_name}.
Extract compliance controls and requirements from the following document text.
Framework: {framework}

For each control you identify:
1. Assign a control ID (e.g., AC-1, AU-2, etc.)
2. Provide a clear control name
3. Write a detailed description
4. Identify the control family
5. List specific requirements/obligations
```

### Mock Mode (Testing)

When no API key is provided:
- Generates realistic mock controls
- Based on document text length: `num_controls = min(max(words // 200, 3), 20)`
- Creates 3-20 controls depending on document size
- Assigns random control families
- Confidence scores: 0.75-0.95

## Control Mapping Algorithm

### Matching Strategy

1. **Exact ID Match** (Score: 1.0)
   - Direct control ID match
   - Case-insensitive comparison

2. **Fuzzy Text Match** (Score: 0.0-1.0)
   - Name similarity: 70% weight
   - Description similarity: 30% weight
   - Uses SequenceMatcher algorithm

3. **Family Bonus** (+0.1)
   - Adds 0.1 to score if control families match

4. **Threshold Filtering**
   - Default threshold: 0.6
   - Only matches above threshold are returned

### Example Matching

```python
# Input: Extracted control from document
{
  "control_id": "AC-1",
  "control_name": "Access Control Policy",
  "description": "Develop and maintain access control policies",
  "family": "Access Control"
}

# Output: Matched to Rwanda NCSA
{
  "matched": {
    "control_id": "NCSA-AC-01",
    "control_name": "Access Control Policy and Procedures"
  },
  "match_score": 0.87,
  "match_method": "fuzzy_match"
}
```

## Testing

### Manual Testing

```bash
# Test PDF processing
curl -X POST "http://localhost:8002/process/document" \
  -F "file=@test_policy.pdf"

# Test control search
curl "http://localhost:8002/controls/search?query=firewall"

# Test specific control
curl "http://localhost:8002/controls/NCSA-AC-01"

# Health check
curl "http://localhost:8002/health"
```

### Performance Benchmarks

| Operation | Avg Time | Max Size |
|-----------|----------|----------|
| PDF extraction | 1-3s | 10MB |
| DOCX extraction | 0.5-2s | 10MB |
| Excel extraction | 0.5-2s | 10MB |
| LLM processing | 2-5s | 4000 chars |
| Control mapping | <100ms | 20 controls |

## Integration with Other Engines

### ENGINE 4: Decision Engine
```python
# ENGINE 4 can call ENGINE 2 to enrich control database
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://document-processor:8002/process/document",
        files={"file": document_content}
    )
    extracted_controls = response.json()["controls"]
```

### ENGINE 6: Web UI
```typescript
// Upload document from frontend
const formData = new FormData();
formData.append('file', file);
formData.append('company_name', 'Acme Corp');

const response = await fetch('http://localhost:8002/process/document', {
  method: 'POST',
  body: formData
});

const result = await response.json();
```

## Troubleshooting

### Common Issues

**1. OpenAI API Errors**
```
⚠️ OpenAI API error: Rate limit exceeded
⚠️ Falling back to mock extraction
```
Solution: Check API key, rate limits, or use mock mode

**2. File Upload Errors**
```
HTTPException: File size exceeds 10MB limit
```
Solution: Reduce file size or increase MAX_FILE_SIZE

**3. Control Mapping Issues**
```
🔍 Matched 0 / 12 controls
```
Solution: Check taxonomy file path, lower threshold, verify control IDs

**4. PDF Extraction Errors**
```
⚠️ PDF extraction error: File is encrypted
```
Solution: Decrypt PDF, use unprotected version

## Directory Structure

```
engines/document_processor/
├── app/
│   ├── main.py                 # FastAPI application (350+ lines)
│   ├── extractors/
│   │   ├── __init__.py
│   │   ├── pdf_extractor.py    # PDF text extraction
│   │   ├── docx_extractor.py   # Word document parsing
│   │   └── excel_extractor.py  # Excel spreadsheet reading
│   └── services/
│       ├── __init__.py
│       ├── llm_processor.py    # OpenAI GPT-4 integration
│       └── control_mapper.py   # Control matching algorithm
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Container configuration
└── README.md                   # This file
```

## Future Enhancements

- [ ] OCR support for scanned PDFs
- [ ] Image analysis for diagrams and flowcharts
- [ ] Multi-language document support
- [ ] Batch document processing
- [ ] Document versioning and diff analysis
- [ ] Custom control framework support
- [ ] Semantic search with embeddings
- [ ] Control extraction from source code

## Contributors

**Rwanda NCSA Compliance Auditor Team**
- ENGINE 2: Document Processing Engine

## License

Internal use only - Rwanda NCSA Compliance Auditor v3.0.0

---

**ENGINE 2 Status:** ✅ COMPLETE
**Port:** 8002
**Dependencies:** OpenAI (optional), PyPDF2, python-docx, openpyxl
**Integration:** ENGINE 4 (Decision), ENGINE 6 (Web UI)
