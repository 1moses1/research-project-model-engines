# ENGINE 5: Report Generation Engine

**Rwanda NCSA Compliance Auditor v3.0.0**

LLM-powered PDF report generation engine that creates professional compliance reports, scorecards, executive summaries, and gap analyses.

## Features

### Report Types
- **Full Compliance Report**: Comprehensive assessment with detailed findings
- **Executive Summary**: High-level overview for leadership
- **Compliance Scorecard**: Visual metrics and grades
- **Gap Analysis**: Detailed remediation roadmap

### LLM Integration
- **OpenAI GPT-4**: Intelligent narrative generation
- **Mock Mode**: Realistic report generation without API key
- **Professional Formatting**: Executive-level quality

### PDF Generation
- **ReportLab Integration**: Professional PDF documents
- **Charts & Visualizations**: Matplotlib-powered graphics
- **Custom Styling**: Branded templates
- **Multi-page Layout**: Cover page, TOC, sections, footer

### Visualizations
- **Compliance Pie Charts**: Status distribution
- **Control Family Bar Charts**: Scores by family
- **Risk Distribution Charts**: Risk severity breakdown
- **Compliance Gauges**: Overall score meters

## Architecture

```
Report Request → LLM Generator → Content Sections
                      ↓
              Chart Generator → Matplotlib Charts
                      ↓
              PDF Generator → ReportLab PDF
                      ↓
             File Storage → Download API
```

## API Endpoints

### Report Generation

#### `POST /generate/report`
Generate compliance report

**Request:**
```json
{
  "report_type": "full",
  "compliance_data": {
    "company_name": "Acme Corp",
    "assessment_date": "2025-01-15",
    "framework": "Rwanda-NCSA",
    "total_controls": 169,
    "compliant_controls": 135,
    "non_compliant_controls": 25,
    "pending_controls": 9,
    "family_scores": [
      {
        "family": "Access Control",
        "compliance_percentage": 85.5,
        "total_controls": 15,
        "compliant_controls": 13
      }
    ],
    "risk_summary": {
      "critical": 3,
      "high": 8,
      "medium": 15,
      "low": 12
    }
  },
  "include_charts": true,
  "include_recommendations": true
}
```

**Response:**
```json
{
  "success": true,
  "report_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "report_type": "full",
  "company_name": "Acme Corp",
  "file_path": "/reports/a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "file_size": 524288,
  "generation_time": 5.32,
  "llm_enabled": true,
  "pages": 12
}
```

**Report Types:**
- `full` - Comprehensive compliance report
- `executive` - Executive summary
- `scorecard` - Compliance scorecard
- `gap_analysis` - Gap analysis and remediation roadmap

#### `GET /reports/{report_id}`
Download generated report

**Response:** PDF file download

#### `GET /reports`
List all generated reports

**Response:**
```json
{
  "total": 10,
  "reports": [
    {
      "report_id": "a1b2c3d4",
      "report_type": "full",
      "filename": "a1b2c3d4_full_report.pdf",
      "file_size": 524288,
      "created_at": "2025-01-15T10:30:00",
      "download_url": "/reports/a1b2c3d4"
    }
  ]
}
```

#### `DELETE /reports/{report_id}`
Delete a report

**Response:**
```json
{
  "success": true,
  "message": "Report deleted: a1b2c3d4",
  "files_deleted": 1
}
```

### System Information

#### `GET /health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "Report Generation Engine",
  "version": "1.0.0",
  "llm_enabled": true,
  "reports_directory": "/app/reports",
  "timestamp": "2025-01-15T10:30:00"
}
```

#### `GET /stats`
Get statistics

**Response:**
```json
{
  "service": "Report Generation Engine",
  "llm_enabled": true,
  "report_types": ["full", "executive", "scorecard", "gap_analysis"],
  "reports_generated": {
    "full": 15,
    "executive": 25,
    "scorecard": 30,
    "gap_analysis": 10,
    "total": 80
  },
  "total_storage_bytes": 41943040,
  "total_storage_mb": 40.0,
  "reports_directory": "/app/reports"
}
```

## Installation

### Prerequisites
- Python 3.11+
- OpenAI API key (optional, for LLM generation)
- Docker & Docker Compose (for containerized deployment)

### Local Development

```bash
# Navigate to ENGINE 5 directory
cd engines/report_generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-api-key-here"

# Run the server
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d report-generator

# View logs
docker-compose logs -f report-generator

# Stop service
docker-compose down
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4 | None (uses mock mode) |
| `PORT` | Server port | 8003 |

### Report Cleanup

Reports are automatically cleaned up after 24 hours to manage storage. This can be configured in the background tasks.

## Report Sections

### Full Compliance Report

1. **Cover Page**: Company name, date, confidential notice
2. **Table of Contents**: Section navigation
3. **Introduction**: Purpose, scope, methodology
4. **Executive Summary**: High-level overview
5. **Compliance Analysis**: Detailed breakdown by control family
6. **Risk Assessment**: Risk categorization and impact
7. **Detailed Findings**: Critical, major, and minor issues
8. **Compliance Gaps**: Gap identification and analysis
9. **Recommendations**: Strategic and tactical improvements
10. **Next Steps**: Implementation roadmap
11. **Visualizations**: Charts and graphs
12. **Footer**: Document information, disclaimer

### Executive Summary

1. **Executive Summary**: 2-3 paragraph overview
2. **Compliance Overview**: Key metrics
3. **Risk Assessment**: High-priority risks
4. **Key Findings**: Top 3-5 critical findings
5. **Recommendations**: Top 5 strategic recommendations
6. **Visualizations**: Key charts

### Compliance Scorecard

1. **Header**: Company, date, framework
2. **Overall Score**: Grade and compliance rate
3. **Control Family Scores**: Visual scorecard
4. **Compliance Metrics**: Effectiveness, maturity
5. **Risk Summary**: Risk distribution
6. **Top Priorities**: Improvement areas
7. **Compliance Breakdown**: Status breakdown
8. **Recommendations Summary**: Action items

### Gap Analysis Report

1. **Gap Analysis Overview**: Summary of identified gaps
2. **Critical Gaps**: High-severity gaps
3. **Moderate Gaps**: Medium-priority gaps
4. **Minor Gaps**: Low-priority gaps
5. **Root Cause Analysis**: Systemic issues
6. **Remediation Roadmap**: Phased implementation plan
7. **Resource Requirements**: Personnel, technology, budget

## LLM Processing

### OpenAI Mode (Production)

When `OPENAI_API_KEY` is provided:
- Uses GPT-4 for narrative generation
- Context-aware content
- Professional tone and structure
- Custom prompts per report type
- Temperature: 0.4 (balanced creativity/consistency)
- Max tokens: 3000 per section

**Example Prompt (Executive Summary):**
```
Generate an executive summary compliance report for {company_name}.

Framework: Rwanda-NCSA
Total Controls: 169
Compliant: 135 (79.9%)
Non-Compliant: 25 (14.8%)

Generate a professional executive summary with:
1. EXECUTIVE SUMMARY (2-3 paragraphs)
2. COMPLIANCE OVERVIEW
3. RISK ASSESSMENT
4. KEY FINDINGS
5. RECOMMENDATIONS
```

### Mock Mode (Testing)

When no API key is provided:
- Generates realistic mock content
- Based on compliance data patterns
- Professional formatting maintained
- Suitable for testing and demos

## Chart Generation

### Available Charts

1. **Compliance Pie Chart**
   - Compliant vs Non-Compliant vs Pending
   - Color-coded (green, red, orange)
   - Percentage labels

2. **Control Family Bar Chart**
   - Horizontal bars per family
   - Color-coded by performance
   - Target/minimum reference lines

3. **Risk Distribution Chart**
   - Vertical bars by severity
   - Critical, High, Medium, Low
   - Count labels

4. **Compliance Gauge**
   - Polar chart showing overall %
   - Color-coded arc
   - Large percentage display

### Chart Configuration

- **Size**: 8x6 inches (standard), 12x8 (bar charts)
- **DPI**: 150 (high quality)
- **Format**: PNG (base64 encoded)
- **Backend**: Matplotlib 'Agg' (non-interactive)

## PDF Styling

### Layout

- **Page Size**: US Letter (8.5" x 11")
- **Margins**: 1 inch (72 points)
- **Font**: Helvetica family
- **Line Spacing**: 12 points after paragraphs

### Custom Styles

- **Title**: 24pt, bold, centered, dark blue
- **Heading**: 16pt, bold, dark gray
- **Subheading**: 12pt, bold, light gray
- **Body**: 10pt, justified, black

### Color Scheme

- **Primary**: #2c3e50 (dark blue)
- **Secondary**: #34495e (slate)
- **Accent**: #7f8c8d (gray)
- **Success**: #2ecc71 (green)
- **Warning**: #f39c12 (orange)
- **Danger**: #e74c3c (red)

## Testing

### Manual Testing

```bash
# Generate full report
curl -X POST "http://localhost:8003/generate/report" \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "full",
    "compliance_data": {
      "company_name": "Test Corp",
      "total_controls": 100,
      "compliant_controls": 75,
      "non_compliant_controls": 25
    }
  }'

# Download report
curl "http://localhost:8003/reports/{report_id}" -o report.pdf

# List reports
curl "http://localhost:8003/reports"

# Get stats
curl "http://localhost:8003/stats"

# Health check
curl "http://localhost:8003/health"
```

### Performance Benchmarks

| Operation | Avg Time | Max Size |
|-----------|----------|----------|
| LLM content generation | 3-8s | 3000 tokens |
| Chart generation | 1-3s | 5 charts |
| PDF assembly | 1-2s | 20 pages |
| **Total (full report)** | **5-13s** | **2-5MB** |

## Integration with Other Engines

### ENGINE 4: Decision Engine
```python
# Call ENGINE 5 to generate compliance report
import httpx

async with httpx.AsyncClient() as client:
    # Get compliance data from ENGINE 4
    family_scores = await scoring_service.get_family_scores()
    risk_summary = await risk_service.get_risk_summary()

    # Request report generation
    response = await client.post(
        "http://report-generator:8003/generate/report",
        json={
            "report_type": "executive",
            "compliance_data": {
                "company_name": "Acme Corp",
                "family_scores": family_scores,
                "risk_summary": risk_summary
            }
        }
    )

    report_info = response.json()
    report_id = report_info["report_id"]
```

### ENGINE 6: Web UI
```typescript
// Generate and download report from frontend
const generateReport = async () => {
  const response = await fetch('http://localhost:8003/generate/report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      report_type: 'scorecard',
      compliance_data: complianceData
    })
  });

  const result = await response.json();

  // Download the generated report
  const downloadUrl = `http://localhost:8003/reports/${result.report_id}`;
  window.open(downloadUrl, '_blank');
};
```

## Troubleshooting

### Common Issues

**1. OpenAI API Errors**
```
⚠️ OpenAI API error: Rate limit exceeded
⚠️ Falling back to mock generation
```
Solution: Check API key, rate limits, or use mock mode

**2. Chart Generation Errors**
```
⚠️ Matplotlib not available - charts will be skipped
```
Solution: Install matplotlib: `pip install matplotlib`

**3. PDF Generation Errors**
```
⚠️ ReportLab not available - using text-based fallback
```
Solution: Install ReportLab: `pip install reportlab`

**4. Storage Issues**
```
Reports directory full
```
Solution: Run cleanup task or increase storage limits

## Directory Structure

```
engines/report_generator/
├── app/
│   ├── main.py                          # FastAPI application (400+ lines)
│   ├── __init__.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_report_generator.py      # GPT-4 integration (450+ lines)
│   │   ├── pdf_generator.py             # ReportLab PDF gen (330+ lines)
│   │   ├── scorecard_generator.py       # Scorecard builder (300+ lines)
│   │   └── chart_generator.py           # Matplotlib charts (350+ lines)
│   └── templates/                       # Future: HTML templates
├── requirements.txt                     # Python dependencies
├── Dockerfile                           # Container configuration
└── README.md                            # This file
```

## Future Enhancements

- [ ] HTML report generation
- [ ] Multi-language support (FR, KIN)
- [ ] Custom branding/logos
- [ ] Email delivery integration
- [ ] Report templates library
- [ ] Trend analysis (historical comparisons)
- [ ] Interactive dashboards
- [ ] Automated report scheduling
- [ ] Digital signatures
- [ ] Export to Word/Excel

## Contributors

**Rwanda NCSA Compliance Auditor Team**
- ENGINE 5: Report Generation Engine

## License

Internal use only - Rwanda NCSA Compliance Auditor v3.0.0

---

**ENGINE 5 Status:** ✅ COMPLETE
**Port:** 8003
**Dependencies:** OpenAI (optional), ReportLab, Matplotlib
**Integration:** ENGINE 4 (Decision), ENGINE 6 (Web UI)
