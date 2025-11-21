# ENGINE 1: LLM-Powered Log Parser with MCP Server Architecture

**Date**: November 21, 2025
**Status**: 🚧 **DESIGN PHASE**
**Goal**: Transform ENGINE 1 into an intelligent, context-aware log collection and parsing system

---

## 🎯 Executive Summary

ENGINE 1 will be upgraded from a simple log collector to an **intelligent log understanding system** that combines:
1. **LLM-powered semantic parsing** (like ENGINE 2's document processing)
2. **MCP server capabilities** (read-only command execution for log collection)
3. **Multi-format log support** (syslog, JSON, Windows Events, custom formats)
4. **Automatic control mapping** (maps log events to 196 Rwanda NCSA/NIST controls)
5. **Context-aware enrichment** (understands what logs mean, not just pattern matching)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      ENGINE 1: INTELLIGENT LOG PARSER            │
│                        (LLM + MCP + Multi-Format)                │
└─────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
        ┌───────────────────────┐   ┌──────────────────────┐
        │   MCP SERVER LAYER    │   │   LLM SERVICE LAYER  │
        │  (Log Collection)     │   │  (Semantic Parsing)  │
        └───────────────────────┘   └──────────────────────┘
                    │                           │
        ┌───────────┴────────┐      ┌──────────┴─────────┐
        ▼                    ▼      ▼                    ▼
  ┌─────────┐        ┌─────────┐  ┌──────┐      ┌────────────┐
  │ Command │        │  File   │  │ GPT  │      │ Semantic   │
  │ Exec    │        │ Read    │  │ -4   │      │ Matcher    │
  └─────────┘        └─────────┘  └──────┘      └────────────┘
        │                    │          │                │
        └────────┬───────────┘          └────────┬───────┘
                 ▼                               ▼
        ┌────────────────────┐          ┌───────────────┐
        │  LOG ADAPTER LAYER │          │  ENRICHMENT   │
        │  (Format Parser)   │          │   SERVICE     │
        └────────────────────┘          └───────────────┘
                 │                               │
      ┌──────────┼──────────┐                   │
      ▼          ▼          ▼                   │
 ┌────────┐ ┌─────────┐ ┌────────┐            │
 │ Syslog │ │ Windows │ │  JSON  │            │
 │ Parser │ │ Events  │ │ Parser │            │
 └────────┘ └─────────┘ └────────┘            │
      │          │          │                   │
      └──────────┴──────────┴───────────────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │  NORMALIZED OUTPUT   │
                  │  (for ENGINE 3)      │
                  └──────────────────────┘
```

---

## 🧠 LLM-Powered Features

### 1. **Semantic Log Understanding**
Instead of rigid regex patterns, LLM understands context:

**Before (Regex-based)**:
```python
if re.match(r"Failed login.*", log):
    event_type = "authentication_failure"
```

**After (LLM-powered)**:
```python
llm_result = llm.analyze_log(
    log="User jdoe authentication attempt rejected due to expired credentials",
    controls=rwanda_controls
)
# Returns:
# {
#   "event_type": "authentication_failure",
#   "severity": "medium",
#   "mapped_controls": ["RWNCSA-AC-17", "RWNCSA-IA-74"],
#   "compliance_status": "non_compliant",
#   "reason": "Credential management violation",
#   "confidence": 0.89
# }
```

### 2. **Automatic Control Mapping**
LLM maps log events to relevant Rwanda NCSA/NIST controls:

**Example Log**:
```
Nov 21 14:30:22 server sshd[1234]: Failed password for admin from 192.168.1.100 port 22 ssh2
```

**LLM Analysis**:
```json
{
  "timestamp": "2025-11-21T14:30:22Z",
  "source": "sshd",
  "event": "authentication_failure",
  "user": "admin",
  "source_ip": "192.168.1.100",
  "port": 22,
  "protocol": "ssh2",
  "mapped_controls": [
    {
      "control_id": "RWNCSA-AC-17",
      "control_name": "Account Management",
      "relevance": 0.95,
      "reason": "Failed authentication attempt"
    },
    {
      "control_id": "RWNCSA-IA-74",
      "control_name": "Identifier Management",
      "relevance": 0.87,
      "reason": "User authentication event"
    }
  ],
  "compliance_status": "non_compliant",
  "severity": "high",
  "indicators": [
    "off_hours_access_attempt",
    "repeated_failure_pattern"
  ]
}
```

### 3. **Context-Aware Anomaly Detection**
LLM understands what's "normal" vs "suspicious":

```python
# LLM recognizes patterns across logs
llm.detect_anomalies([
    "14:30 admin login from 192.168.1.100",
    "14:31 admin login from 10.0.0.50",      # Suspicious: different IP
    "14:32 admin login from 203.45.67.89"   # Suspicious: foreign IP
])
# Returns: "Credential stuffing attack - admin account compromised"
```

---

## 🔌 MCP Server Capabilities

### What is MCP?
**Model Context Protocol (MCP)** enables:
- Read-only command execution
- Secure log collection from remote sources
- Standardized tool interface for LLMs
- Pipe/streaming log data

### MCP Tools for ENGINE 1

#### Tool 1: `execute_command`
```python
# Read logs from remote systems (read-only)
{
  "tool": "execute_command",
  "command": "journalctl -u sshd --since '1 hour ago'",
  "readonly": true,
  "timeout": 30
}
```

#### Tool 2: `read_log_file`
```python
# Read log files with automatic rotation handling
{
  "tool": "read_log_file",
  "path": "/var/log/auth.log",
  "lines": 1000,
  "follow": true  # Tail mode
}
```

#### Tool 3: `query_windows_events`
```python
# Collect Windows Event Logs
{
  "tool": "query_windows_events",
  "log_name": "Security",
  "event_ids": [4624, 4625, 4648],  # Logon events
  "time_range": "last_hour"
}
```

#### Tool 4: `stream_syslog`
```python
# Real-time syslog collection
{
  "tool": "stream_syslog",
  "host": "192.168.1.100",
  "port": 514,
  "protocol": "tcp"
}
```

---

## 📋 Log Format Adapters

### 1. **Syslog Adapter** (RFC 5424 & RFC 3164)
```python
class SyslogAdapter:
    """Parse syslog messages using LLM for semantic understanding"""

    def parse(self, raw_log: str) -> dict:
        # Traditional parsing for structure
        structured = self._parse_syslog_format(raw_log)

        # LLM enrichment for meaning
        llm_analysis = self.llm.analyze_syslog(
            message=structured['message'],
            facility=structured['facility'],
            severity=structured['severity'],
            controls=self.controls
        )

        return {**structured, **llm_analysis}
```

**Example**:
```
Input:  <34>Nov 21 14:30:22 server sshd[1234]: Failed password for admin
Output: {
  "timestamp": "2025-11-21T14:30:22Z",
  "hostname": "server",
  "process": "sshd",
  "pid": 1234,
  "severity": "critical",
  "event_type": "authentication_failure",
  "mapped_controls": ["RWNCSA-AC-17"],
  "compliance_status": "non_compliant"
}
```

### 2. **Windows Event Log Adapter**
```python
class WindowsEventAdapter:
    """Parse Windows XML events using LLM for interpretation"""

    def parse(self, event_xml: str) -> dict:
        # Parse XML structure
        event = self._parse_event_xml(event_xml)

        # LLM interprets event meaning
        llm_analysis = self.llm.analyze_windows_event(
            event_id=event['event_id'],
            description=event['description'],
            data=event['event_data'],
            controls=self.controls
        )

        return {**event, **llm_analysis}
```

**Example**:
```xml
Input: <Event ID="4625">Account failed to log on</Event>

Output: {
  "event_id": 4625,
  "timestamp": "2025-11-21T14:30:22Z",
  "computer": "WORKSTATION01",
  "user": "DOMAIN\\admin",
  "failure_reason": "Unknown user name or bad password",
  "event_type": "authentication_failure",
  "mapped_controls": ["RWNCSA-AC-17", "RWNCSA-IA-74"],
  "compliance_status": "non_compliant",
  "severity": "high",
  "llm_interpretation": "Brute force attack detected"
}
```

### 3. **JSON Log Adapter**
```python
class JSONLogAdapter:
    """Parse JSON logs with LLM semantic enhancement"""

    def parse(self, json_log: str) -> dict:
        # Parse JSON
        log = json.loads(json_log)

        # LLM adds semantic layer
        llm_analysis = self.llm.analyze_json_log(
            log_data=log,
            controls=self.controls
        )

        return {**log, **llm_analysis}
```

### 4. **Custom Format Adapter** (LLM-only)
```python
class LLMUniversalAdapter:
    """Handle any log format using pure LLM understanding"""

    def parse(self, raw_log: str) -> dict:
        # Let LLM figure out the format and meaning
        return self.llm.parse_unknown_log(
            log=raw_log,
            controls=self.controls,
            examples=self.few_shot_examples
        )
```

---

## 🔄 Processing Pipeline

```python
# ENGINE 1 Processing Flow

1. LOG COLLECTION (MCP Layer)
   ├─ Execute read-only commands
   ├─ Stream from syslog servers
   ├─ Query Windows Event Logs
   └─ Read log files

2. FORMAT DETECTION (Auto)
   ├─ Detect syslog pattern
   ├─ Detect Windows XML
   ├─ Detect JSON structure
   └─ Fallback to LLM universal parser

3. LLM SEMANTIC ANALYSIS
   ├─ Understand log context
   ├─ Extract entities (users, IPs, actions)
   ├─ Map to Rwanda NCSA/NIST controls
   ├─ Assess compliance status
   └─ Determine severity

4. ENRICHMENT
   ├─ Add temporal features (hour, day, business hours)
   ├─ Add geolocation (IP → country)
   ├─ Add threat intelligence
   └─ Calculate confidence scores

5. NORMALIZATION
   ├─ Convert to ENGINE 3 format
   ├─ Add metadata
   └─ Output structured event

6. OUTPUT TO ENGINE 3
   └─ Send for ML classification
```

---

## 🎯 Output Format (for ENGINE 3)

```json
{
  "timestamp": "2025-11-21T14:30:22Z",
  "log_message": "Failed password for admin from 192.168.1.100 port 22 ssh2",
  "status_code": 401,
  "port": 22,
  "enrichment": {
    "source": "syslog",
    "original_format": "RFC3164",
    "llm_analyzed": true,
    "controls_mapped": ["RWNCSA-AC-17", "RWNCSA-IA-74"],
    "compliance_status": "non_compliant",
    "severity": "high",
    "confidence": 0.89,
    "event_type": "authentication_failure",
    "entities": {
      "user": "admin",
      "source_ip": "192.168.1.100",
      "country": "Unknown"
    },
    "indicators": [
      "off_hours_access_attempt",
      "high_privilege_account"
    ]
  }
}
```

---

## 🛠️ Implementation Plan

### Phase 1: LLM Service Integration
- [ ] Add LLM client (OpenAI/Anthropic API)
- [ ] Implement control mapper with LLM
- [ ] Create semantic log analyzer
- [ ] Build few-shot prompting system

### Phase 2: MCP Server Setup
- [ ] Implement MCP protocol
- [ ] Add read-only command executor
- [ ] Create secure sandboxing
- [ ] Build log streaming service

### Phase 3: Log Adapters
- [ ] Syslog adapter (RFC 5424 + LLM)
- [ ] Windows Event adapter (XML + LLM)
- [ ] JSON adapter (structured + LLM)
- [ ] Universal LLM adapter (fallback)

### Phase 4: Integration
- [ ] Connect to ENGINE 3 API
- [ ] Add buffering/batching
- [ ] Implement error handling
- [ ] Build monitoring dashboard

---

## 📊 Expected Performance

| Metric | Target | Notes |
|--------|--------|-------|
| **Log Processing Speed** | 100-500 logs/sec | With LLM caching |
| **LLM Latency** | 50-200ms per log | Batched requests |
| **Control Mapping Accuracy** | >90% | LLM semantic understanding |
| **Format Detection** | 100% | Auto-detect + LLM fallback |
| **MCP Command Execution** | <100ms | Read-only, sandboxed |

---

## 🔒 Security Considerations

### Read-Only MCP
- **No write operations** allowed
- **Sandboxed execution** environment
- **Command whitelist** (only safe read commands)
- **Timeout enforcement** (max 30s per command)

### LLM Safety
- **No sensitive data in prompts** (sanitize logs first)
- **Rate limiting** (prevent API abuse)
- **Caching** (reduce costs)
- **Fallback to regex** (when LLM unavailable)

---

## 💰 Cost Estimates

### LLM API Usage
- **Model**: GPT-4-turbo or Claude Sonnet
- **Cost per log**: ~$0.0001 - $0.001
- **Monthly cost (1M logs)**: $100 - $1000
- **Optimization**: Batch requests, caching, local models

### Alternatives
- **Local LLM**: Llama 3.1 (70B) for on-premise
- **Hybrid**: LLM for complex logs, regex for simple patterns
- **Caching**: 80% hit rate → 80% cost reduction

---

## 🚀 Benefits Over Current System

| Feature | Current ENGINE 1 | New LLM-Powered ENGINE 1 |
|---------|------------------|--------------------------|
| **Log Understanding** | Regex patterns | Semantic LLM analysis |
| **Format Support** | Fixed parsers | Universal (LLM adapts) |
| **Control Mapping** | Manual rules | Automatic (LLM infers) |
| **Anomaly Detection** | Threshold-based | Context-aware (LLM) |
| **Windows Events** | Not supported | Full support + LLM |
| **Custom Formats** | Requires coding | LLM auto-adapts |
| **MCP Server** | Not available | Full read-only access |
| **Accuracy** | ~70% | >90% (semantic) |

---

**Next**: Implement Phase 1 (LLM Service Integration)

**Status**: ✅ Design Complete | 🚧 Implementation Starting
