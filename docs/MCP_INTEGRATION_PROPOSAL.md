# MCP Integration Proposal for Rwanda NCSA Compliance Auditor

## Executive Summary

This document proposes replacing the custom XGBoost classifier (Engine 3) with an MCP-based LLM integration that leverages Claude, GPT-4, or similar models for semantic compliance analysis. This shift addresses fundamental limitations in the current keyword-based approach while maintaining the microservices architecture.

---

## Current vs Proposed Architecture

### Current Architecture (7 Engines)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CURRENT ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐  │
│  │   Engine 1   │    │   Engine 2   │    │      Engine 3        │  │
│  │Log Collector │───▶│Doc Processor │    │  XGBoost Classifier  │  │
│  │  + LLM Hint  │    │              │    │  (TF-IDF + Keywords) │  │
│  └──────────────┘    └──────────────┘    └──────────────────────┘  │
│         │                   │                       │               │
│         └───────────────────┼───────────────────────┘               │
│                             ▼                                       │
│                    ┌──────────────────┐                             │
│                    │    Engine 4      │                             │
│                    │ Decision Engine  │                             │
│                    │  (Rule-Based)    │                             │
│                    └──────────────────┘                             │
│                             │                                       │
│         ┌───────────────────┼───────────────────┐                   │
│         ▼                   ▼                   ▼                   │
│  ┌──────────────┐  ┌──────────────┐    ┌──────────────┐            │
│  │   Engine 5   │  │   Engine 6   │    │   Engine 7   │            │
│  │    Web UI    │  │Report Generator│  │  Auth Engine │            │
│  └──────────────┘  └──────────────┘    └──────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

LIMITATIONS:
- XGBoost learns keyword patterns, not semantic meaning
- 7.98% accuracy on unseen log patterns
- Requires retraining for each deployment context
- No reasoning/explanation capability
```

### Proposed Architecture (MCP-Integrated)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MCP-INTEGRATED ARCHITECTURE                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐                              │
│  │   Engine 1   │    │   Engine 2   │                              │
│  │Log Collector │    │Doc Processor │                              │
│  │  (Unchanged) │    │  (Unchanged) │                              │
│  └──────────────┘    └──────────────┘                              │
│         │                   │                                       │
│         └─────────┬─────────┘                                       │
│                   ▼                                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    MCP SERVER LAYER                          │   │
│  │  ┌─────────────────────────────────────────────────────────┐│   │
│  │  │              Engine 3 (REDESIGNED)                      ││   │
│  │  │           MCP Compliance Analyzer                       ││   │
│  │  │                                                         ││   │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ ││   │
│  │  │  │MCP Server:  │  │MCP Server:  │  │  MCP Server:    │ ││   │
│  │  │  │Log Context  │  │NCSA Rules   │  │  Evidence DB    │ ││   │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────┘ ││   │
│  │  │           │              │                │             ││   │
│  │  │           └──────────────┼────────────────┘             ││   │
│  │  │                          ▼                              ││   │
│  │  │              ┌─────────────────────┐                    ││   │
│  │  │              │    LLM API Layer    │                    ││   │
│  │  │              │ (Claude/GPT-4/etc)  │                    ││   │
│  │  │              │                     │                    ││   │
│  │  │              │ - Semantic Analysis │                    ││   │
│  │  │              │ - Control Mapping   │                    ││   │
│  │  │              │ - Reasoning/Explain │                    ││   │
│  │  │              └─────────────────────┘                    ││   │
│  │  │                          │                              ││   │
│  │  │                          ▼                              ││   │
│  │  │              ┌─────────────────────┐                    ││   │
│  │  │              │   Output Parser     │                    ││   │
│  │  │              │ (Structured JSON)   │                    ││   │
│  │  │              └─────────────────────┘                    ││   │
│  │  └─────────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                   │                                                 │
│                   ▼                                                 │
│          ┌──────────────────┐                                       │
│          │    Engine 4      │                                       │
│          │ Decision Engine  │                                       │
│          │  (Rule-Based)    │   ◄── Unchanged: Final decisions      │
│          └──────────────────┘                                       │
│                   │                                                 │
│   ┌───────────────┼───────────────┐                                │
│   ▼               ▼               ▼                                │
│ Engine 5      Engine 6       Engine 7                              │
│ (Unchanged)   (Unchanged)    (Unchanged)                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Analysis: What Changes vs What Remains

### REMOVED Components

| Component | Why Remove |
|-----------|------------|
| XGBoost Model (.json) | Replaced by LLM semantic understanding |
| TF-IDF Vectorizer | LLM has native text understanding |
| Label Encoders | LLM outputs structured responses directly |
| Training Pipeline | No model training needed |
| Fine-tuning Scripts | Prompt engineering replaces fine-tuning |
| Model Metrics Tracking | LLM performance is consistent |

### RETAINED Components

| Component | Why Keep |
|-----------|----------|
| Engine 1: Log Collector | Still need to collect/parse logs |
| Engine 2: Doc Processor | Still need to process policy documents |
| Engine 4: Decision Engine | Business rules for final compliance decisions |
| Engine 5: Web UI | User interface unchanged |
| Engine 6: Report Generator | Report generation unchanged |
| Engine 7: Auth Engine | Authentication unchanged |
| Evidence Parsers | Rule-based parsing still useful for structured data |
| Database/Storage | Still need to persist audit results |

### MODIFIED Components

| Component | Modification |
|-----------|-------------|
| Engine 3 | Complete redesign as MCP Server + LLM API client |
| API Contracts | Add reasoning/explanation fields to responses |
| Cost Model | Per-API-call pricing vs infrastructure costs |

---

## MCP Server Design for Engine 3

### MCP Server 1: Log Context Server

Provides LLM with access to log data and metadata.

```python
# mcp_servers/log_context_server.py

from mcp.server import Server
from mcp.types import Tool, Resource

server = Server("log-context")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="get_log_batch",
            description="Retrieve batch of logs for compliance analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "batch_size": {"type": "integer", "default": 100},
                    "time_range": {"type": "string"},
                    "source_filter": {"type": "string"}
                }
            }
        ),
        Tool(
            name="get_log_context",
            description="Get surrounding context for a specific log entry",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_id": {"type": "string"},
                    "context_window": {"type": "integer", "default": 10}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "get_log_batch":
        return await fetch_logs_from_engine1(arguments)
    elif name == "get_log_context":
        return await get_log_context(arguments)
```

### MCP Server 2: NCSA Rules Server

Provides LLM with access to Rwanda NCSA control definitions.

```python
# mcp_servers/ncsa_rules_server.py

from mcp.server import Server
from mcp.types import Resource

server = Server("ncsa-rules")

NCSA_CONTROLS = {
    "RWNCSA-AC-37": {
        "name": "Access Control - 4-17",
        "family": "Access Control",
        "description": "Failed authentication attempts must be logged and monitored",
        "evidence_patterns": [
            "Failed password",
            "authentication failure",
            "Invalid user",
            "Access denied"
        ],
        "compliant_indicators": [
            "Alert generated for failed attempts",
            "Account lockout after threshold"
        ],
        "non_compliant_indicators": [
            "No logging of failed attempts",
            "Unlimited retry allowed"
        ]
    },
    # ... 196 controls
}

@server.list_resources()
async def list_resources():
    return [
        Resource(
            uri=f"ncsa://controls/{ctrl_id}",
            name=ctrl["name"],
            description=ctrl["description"]
        )
        for ctrl_id, ctrl in NCSA_CONTROLS.items()
    ]

@server.read_resource()
async def read_resource(uri: str):
    control_id = uri.split("/")[-1]
    return json.dumps(NCSA_CONTROLS.get(control_id, {}))
```

### MCP Server 3: Evidence Database Server

Provides LLM with access to historical compliance evidence.

```python
# mcp_servers/evidence_db_server.py

from mcp.server import Server
from mcp.types import Tool

server = Server("evidence-db")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="query_similar_evidence",
            description="Find similar compliance evidence from historical audits",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_pattern": {"type": "string"},
                    "control_family": {"type": "string"},
                    "limit": {"type": "integer", "default": 5}
                }
            }
        ),
        Tool(
            name="store_evidence",
            description="Store new compliance evidence for future reference",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_message": {"type": "string"},
                    "control_id": {"type": "string"},
                    "compliance_status": {"type": "string"},
                    "reasoning": {"type": "string"}
                }
            }
        )
    ]
```

---

## LLM Integration Layer

### Compliance Analysis Prompt Template

```python
COMPLIANCE_ANALYSIS_PROMPT = """
You are a cybersecurity compliance auditor specializing in Rwanda's NCSA
Minimum Cybersecurity Standards. Analyze the following log entry and
determine its compliance implications.

## Log Entry
{log_message}

## Context
- Timestamp: {timestamp}
- Source IP: {source_ip}
- Destination: {destination}
- Port: {port}
- Hour of Day: {hour_of_day}
- Business Hours: {is_business_hours}

## Available NCSA Controls
{relevant_controls}

## Your Task
1. Identify which NCSA control(s) this log relates to
2. Determine compliance status (compliant/non_compliant/partial)
3. Provide confidence score (0.0-1.0)
4. Explain your reasoning

## Response Format (JSON)
{
    "primary_control": {
        "control_id": "RWNCSA-XX-YY",
        "control_name": "...",
        "compliance_status": "compliant|non_compliant|partial",
        "confidence": 0.95,
        "reasoning": "..."
    },
    "secondary_controls": [...],
    "risk_indicators": [...],
    "recommended_actions": [...]
}
"""
```

### API Integration Class

```python
# engines/engine3-mcp-analyzer/app/llm_client.py

import anthropic
from openai import OpenAI
from typing import Literal

class ComplianceLLMClient:
    """Multi-provider LLM client for compliance analysis."""

    def __init__(
        self,
        provider: Literal["anthropic", "openai"] = "anthropic",
        model: str = None
    ):
        self.provider = provider

        if provider == "anthropic":
            self.client = anthropic.Anthropic()
            self.model = model or "claude-sonnet-4-20250514"
        else:
            self.client = OpenAI()
            self.model = model or "gpt-4-turbo"

    async def analyze_log(
        self,
        log_message: str,
        context: dict,
        ncsa_controls: list
    ) -> dict:
        """Analyze a log entry for compliance."""

        prompt = COMPLIANCE_ANALYSIS_PROMPT.format(
            log_message=log_message,
            timestamp=context.get("timestamp"),
            source_ip=context.get("source_ip"),
            destination=context.get("destination"),
            port=context.get("port"),
            hour_of_day=context.get("hour_of_day"),
            is_business_hours=context.get("is_business_hours"),
            relevant_controls=json.dumps(ncsa_controls, indent=2)
        )

        if self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return self._parse_response(response.content[0].text)
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)

    async def analyze_batch(
        self,
        logs: list[dict],
        ncsa_controls: list
    ) -> list[dict]:
        """Batch analyze multiple logs efficiently."""
        # Use batching for cost efficiency
        results = []
        for log in logs:
            result = await self.analyze_log(
                log["log_message"],
                log,
                ncsa_controls
            )
            results.append(result)
        return results
```

---

## Cost Analysis

### Current Architecture Costs

| Item | Monthly Cost |
|------|-------------|
| Kubernetes cluster (3 nodes) | $150 |
| Model training compute | $50 |
| Storage | $20 |
| **Total** | **$220/month** |

### MCP + LLM Architecture Costs

| Item | Monthly Cost | Notes |
|------|-------------|-------|
| Kubernetes cluster (2 nodes) | $100 | Reduced compute needs |
| Claude API (100K logs/month) | $30-50 | ~$0.003/1K input tokens |
| Storage | $20 | |
| **Total** | **$150-170/month** | **~25% savings** |

### Cost Optimization Strategies

1. **Caching**: Cache LLM responses for identical/similar logs
2. **Batching**: Analyze multiple logs in single API call
3. **Tiered Analysis**:
   - Rule-based for obvious cases (90% of logs)
   - LLM only for ambiguous cases (10% of logs)
4. **Model Selection**: Use cheaper models for simple logs, premium for complex

---

## Migration Plan

### Phase 1: MCP Infrastructure (Week 1-2)

1. Set up MCP server framework
2. Implement Log Context Server
3. Implement NCSA Rules Server
4. Test MCP communication

### Phase 2: LLM Integration (Week 3-4)

1. Implement LLM client (Anthropic/OpenAI)
2. Design prompt templates
3. Implement response parsing
4. Add caching layer

### Phase 3: Engine 3 Redesign (Week 5-6)

1. Create new FastAPI service with MCP
2. Maintain API compatibility with Engine 4
3. Add explanation/reasoning endpoints
4. Implement batch processing

### Phase 4: Testing & Validation (Week 7-8)

1. Test on synthetic data
2. Test on SecRepo logs
3. Compare with XGBoost baseline
4. Performance/latency testing

### Phase 5: Deployment (Week 9-10)

1. Deploy to staging
2. A/B testing with production traffic
3. Monitor costs and accuracy
4. Full rollout

---

## API Contract Changes

### Current Engine 3 Response

```json
{
    "prediction": "non_compliant",
    "confidence": 0.87,
    "probabilities": {
        "compliant": 0.13,
        "non_compliant": 0.87
    }
}
```

### New MCP-Enhanced Response

```json
{
    "prediction": "non_compliant",
    "confidence": 0.92,
    "primary_control": {
        "control_id": "RWNCSA-AC-37",
        "control_name": "Access Control - Failed Authentication Monitoring",
        "compliance_status": "non_compliant"
    },
    "reasoning": "The log shows 'Failed password for invalid user admin' which indicates an unauthorized access attempt. Under RWNCSA-AC-37, failed authentication must trigger alerts. No evidence of alert generation in surrounding context.",
    "evidence_indicators": [
        "Failed password attempt detected",
        "Invalid username 'admin' attempted",
        "Source IP 192.168.1.100 not in whitelist"
    ],
    "recommended_actions": [
        "Enable failed login alerting",
        "Implement IP-based rate limiting",
        "Review account lockout policy"
    ],
    "secondary_controls": [
        {
            "control_id": "RWNCSA-IA-98",
            "relevance": 0.75
        }
    ],
    "model_used": "claude-sonnet-4-20250514",
    "latency_ms": 450
}
```

---

## Advantages of MCP + LLM Approach

| Advantage | Description |
|-----------|-------------|
| **Semantic Understanding** | LLM understands meaning, not just keywords |
| **Zero-Shot Generalization** | Works on any log format without retraining |
| **Explainability** | Provides reasoning for every decision |
| **Continuous Improvement** | LLM updates don't require your intervention |
| **Multi-Control Mapping** | Can identify multiple relevant controls per log |
| **Context Awareness** | Can use surrounding logs for better analysis |
| **No Training Data Needed** | Eliminates synthetic data limitations |
| **Reduced Maintenance** | No model retraining, artifact management |

## Disadvantages & Mitigations

| Disadvantage | Mitigation |
|--------------|------------|
| API Latency (300-500ms) | Batch processing, async, caching |
| API Costs | Tiered analysis, caching, model selection |
| Rate Limits | Multiple providers, request queuing |
| Internet Dependency | Local fallback model (Ollama) |
| Prompt Injection Risk | Input sanitization, output validation |

---

## Recommended LLM Models

| Use Case | Recommended Model | Cost/1K tokens |
|----------|------------------|----------------|
| High accuracy, complex logs | Claude Opus 4 | $0.015 |
| Balanced cost/accuracy | Claude Sonnet 4 | $0.003 |
| Budget, simple logs | Claude Haiku | $0.00025 |
| Alternative provider | GPT-4 Turbo | $0.01 |
| Local/offline | Llama 3 (Ollama) | Free |

---

## Conclusion

Replacing XGBoost with MCP + LLM integration offers:

1. **Better accuracy** on real-world logs (semantic vs keyword matching)
2. **Zero retraining** for new deployment contexts
3. **Explainable decisions** with reasoning
4. **Lower total cost** (~25% reduction)
5. **Simpler architecture** (no ML pipeline)

The 7-engine architecture remains largely intact, with only Engine 3 being redesigned. This is a low-risk, high-reward modernization that leverages state-of-the-art LLM capabilities while maintaining your existing infrastructure investments.
