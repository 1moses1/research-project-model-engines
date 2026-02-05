"""
LLM Client for Compliance Analysis.

Provides a unified interface to Claude (Anthropic) and GPT (OpenAI)
for semantic compliance analysis of log entries.
"""

import os
import json
import time
import hashlib
from typing import Optional, Dict, Any, List, Literal
from datetime import datetime
from functools import lru_cache

# LLM providers
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from ..models.ncsa_controls import find_relevant_controls, get_control


# =============================================================================
# Prompt Templates
# =============================================================================

COMPLIANCE_ANALYSIS_PROMPT = """You are a cybersecurity compliance auditor specializing in Rwanda's National Cyber Security Authority (NCSA) Minimum Cybersecurity Standards. Your task is to analyze log entries and determine whether the SECURITY EVENT described in the log indicates a compliance violation.

## CRITICAL: What You Are Evaluating

You are NOT evaluating whether the logging system is working correctly.
You ARE evaluating whether the EVENT DESCRIBED in the log represents:
- **compliant**: A normal, authorized, secure operation (e.g., successful authorized login, normal session, scheduled task)
- **non_compliant**: A security violation, attack attempt, unauthorized access, or policy breach (e.g., failed login, invalid user, authentication failure, intrusion attempt)
- **partial**: Mixed indicators or requires further investigation

## Classification Rules

**Mark as NON_COMPLIANT if the log indicates:**
- Failed authentication attempts (failed password, invalid credentials)
- Invalid or unknown user access attempts
- Unauthorized access attempts
- Missing identification or authentication
- Intrusion detection alerts or break-in attempts
- Suspicious activities (port scans, brute force patterns)
- Security policy violations
- Malware or threat detection

**Mark as COMPLIANT if the log indicates:**
- Successful authorized authentication (accepted password, accepted publickey)
- Normal session open/close by authorized users
- Routine scheduled tasks (cron jobs)
- Normal connection termination
- Successful security operations

## Log Entry to Analyze
```
{log_message}
```

## Context Information
- Timestamp: {timestamp}
- Source IP: {source_ip}
- Destination IP: {destination_ip}
- Port: {port}
- Hour of Day: {hour_of_day}
- Business Hours: {is_business_hours}
- User ID: {user_id}
- Action: {action}

## Relevant NCSA Controls
{relevant_controls_json}

## Your Analysis Task

1. **Event Classification**: Is the EVENT in this log a security violation or normal operation?
2. **Primary Control**: Which NCSA control does this event relate to?
3. **Compliance Status**: Based on the EVENT (not the logging), is this compliant or non_compliant?
4. **Evidence**: What specific words/patterns in the log support your determination?
5. **Risk Assessment**: What security risk does this event indicate?
6. **Remediation**: If non_compliant, what action should be taken?

## Response Format
Respond with a valid JSON object in exactly this format:
{{
    "primary_control": {{
        "control_id": "RWNCSA-XX-YY",
        "control_name": "Name of the control",
        "control_family": "Control Family Name",
        "compliance_status": "compliant|non_compliant|partial",
        "confidence": 0.95,
        "relevance": 0.9
    }},
    "secondary_controls": [
        {{
            "control_id": "RWNCSA-XX-YY",
            "control_name": "Name",
            "control_family": "Family",
            "compliance_status": "compliant|non_compliant|partial",
            "confidence": 0.8,
            "relevance": 0.7
        }}
    ],
    "reasoning": "Detailed explanation focusing on what the EVENT indicates, not whether logging works...",
    "evidence_indicators": [
        "Specific evidence from the log",
        "Another piece of evidence"
    ],
    "risk_indicators": [
        "Identified security risk if any"
    ],
    "recommended_actions": [
        "Specific remediation action"
    ]
}}

## Examples

Log: "Failed password for invalid user admin from 192.168.1.100"
→ NON_COMPLIANT (the EVENT is a failed authentication attempt, indicating unauthorized access attempt)

Log: "Accepted publickey for deploy from 10.0.0.10 port 22"
→ COMPLIANT (the EVENT is a successful authorized authentication)

Log: "POSSIBLE BREAK-IN ATTEMPT!"
→ NON_COMPLIANT (the EVENT indicates a potential intrusion)

Important:
- Focus on what the EVENT indicates, not whether the log was captured correctly
- Use ONLY the controls provided in the "Relevant NCSA Controls" section
- Be precise with control IDs (format: RWNCSA-XX-YY)
- "Failed", "Invalid", "denied", "failure", "attack", "intrusion" → typically NON_COMPLIANT
- "Accepted", "success", "opened", "closed" (normal) → typically COMPLIANT"""


BATCH_ANALYSIS_PROMPT = """You are analyzing multiple log entries for compliance with Rwanda NCSA standards.
Analyze each log and return results as a JSON array.

## Logs to Analyze
{logs_json}

## Available NCSA Controls
{controls_json}

Return a JSON array with one result object per log, in the same order as input."""


# =============================================================================
# Response Cache
# =============================================================================

class ResponseCache:
    """Simple in-memory cache for LLM responses."""

    def __init__(self, max_size: int = 10000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def _hash_key(self, log_message: str, context: Dict) -> str:
        """Generate cache key from log and context."""
        content = f"{log_message}:{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def get(self, log_message: str, context: Dict) -> Optional[Dict]:
        """Get cached response if available."""
        key = self._hash_key(log_message, context)
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.misses += 1
        return None

    def set(self, log_message: str, context: Dict, response: Dict):
        """Cache a response."""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        key = self._hash_key(log_message, context)
        self.cache[key] = response

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self.hits + self.misses
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / total if total > 0 else 0
        }


# =============================================================================
# LLM Client
# =============================================================================

class ComplianceLLMClient:
    """
    Multi-provider LLM client for compliance analysis.

    Supports:
    - Anthropic Claude (claude-sonnet-4-20250514, claude-opus-4-20250514)
    - OpenAI GPT (gpt-4-turbo, gpt-4o)

    Features:
    - Response caching
    - Automatic fallback between providers
    - Structured JSON output parsing
    - Cost tracking
    """

    def __init__(
        self,
        provider: Literal["anthropic", "openai"] = "anthropic",
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        enable_cache: bool = True,
        cache_size: int = 10000
    ):
        self.provider = provider
        self.enable_cache = enable_cache
        self.cache = ResponseCache(max_size=cache_size) if enable_cache else None

        # Track costs and usage
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_requests = 0

        # Initialize provider
        if provider == "anthropic":
            if not ANTHROPIC_AVAILABLE:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
            self.client = anthropic.Anthropic(
                api_key=api_key or os.getenv("ANTHROPIC_API_KEY")
            )
            self.model = model or "claude-sonnet-4-20250514"
        elif provider == "openai":
            if not OPENAI_AVAILABLE:
                raise ImportError("openai package not installed. Run: pip install openai")
            self.client = OpenAI(
                api_key=api_key or os.getenv("OPENAI_API_KEY")
            )
            self.model = model or "gpt-4-turbo"
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _format_prompt(
        self,
        log_message: str,
        context: Dict[str, Any],
        relevant_controls: List[Dict]
    ) -> str:
        """Format the analysis prompt with log and context."""
        return COMPLIANCE_ANALYSIS_PROMPT.format(
            log_message=log_message,
            timestamp=context.get("timestamp", "Unknown"),
            source_ip=context.get("source_ip", "Unknown"),
            destination_ip=context.get("destination_ip", "Unknown"),
            port=context.get("port", "Unknown"),
            hour_of_day=context.get("hour_of_day", "Unknown"),
            is_business_hours=context.get("is_business_hours", "Unknown"),
            user_id=context.get("user_id", "Unknown"),
            action=context.get("action", "Unknown"),
            relevant_controls_json=json.dumps(relevant_controls, indent=2)
        )

    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        # Try to extract JSON from response
        try:
            # Handle markdown code blocks
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            return json.loads(response_text)
        except json.JSONDecodeError:
            # Return a default structure if parsing fails
            return {
                "primary_control": {
                    "control_id": "RWNCSA-AU-70",
                    "control_name": "General Audit Events",
                    "control_family": "Audit and Accountability",
                    "compliance_status": "unknown",
                    "confidence": 0.5,
                    "relevance": 0.5
                },
                "secondary_controls": [],
                "reasoning": f"Failed to parse LLM response: {response_text[:200]}",
                "evidence_indicators": [],
                "risk_indicators": [],
                "recommended_actions": ["Review log manually"]
            }

    async def analyze_log(
        self,
        log_message: str,
        context: Optional[Dict[str, Any]] = None,
        include_reasoning: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze a single log entry for compliance.

        Args:
            log_message: The raw log message to analyze
            context: Additional context (timestamp, IP, port, etc.)
            include_reasoning: Whether to include detailed reasoning

        Returns:
            Dict with compliance analysis results
        """
        context = context or {}
        start_time = time.time()

        # Check cache
        if self.enable_cache:
            cached = self.cache.get(log_message, context)
            if cached:
                cached["cached"] = True
                cached["latency_ms"] = (time.time() - start_time) * 1000
                return cached

        # Find relevant controls using keyword matching
        relevant_controls = find_relevant_controls(log_message, top_k=5)

        # If no controls found, use default audit control
        if not relevant_controls:
            relevant_controls = [get_control("RWNCSA-AU-70")]

        # Format prompt
        prompt = self._format_prompt(log_message, context, relevant_controls)

        # Call LLM
        try:
            if self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = response.content[0].text
                self.total_input_tokens += response.usage.input_tokens
                self.total_output_tokens += response.usage.output_tokens
            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"},
                    max_tokens=1024
                )
                response_text = response.choices[0].message.content
                self.total_input_tokens += response.usage.prompt_tokens
                self.total_output_tokens += response.usage.completion_tokens

            self.total_requests += 1

        except Exception as e:
            # Return error response
            latency_ms = (time.time() - start_time) * 1000
            return {
                "primary_control": {
                    "control_id": "RWNCSA-AU-70",
                    "control_name": "General Audit Events",
                    "control_family": "Audit and Accountability",
                    "compliance_status": "unknown",
                    "confidence": 0.0,
                    "relevance": 0.0
                },
                "secondary_controls": [],
                "reasoning": f"LLM API error: {str(e)}",
                "evidence_indicators": [],
                "risk_indicators": [],
                "recommended_actions": ["Retry analysis"],
                "model_used": self.model,
                "latency_ms": latency_ms,
                "cached": False,
                "error": str(e)
            }

        # Parse response
        result = self._parse_response(response_text)

        # Add metadata
        latency_ms = (time.time() - start_time) * 1000
        result["model_used"] = self.model
        result["latency_ms"] = latency_ms
        result["cached"] = False
        result["timestamp"] = datetime.utcnow().isoformat()

        # Compute prediction for backward compatibility
        primary_status = result.get("primary_control", {}).get("compliance_status", "unknown")
        result["prediction"] = primary_status if primary_status != "unknown" else "non_compliant"
        result["confidence"] = result.get("primary_control", {}).get("confidence", 0.5)
        result["probabilities"] = {
            "compliant": result["confidence"] if result["prediction"] == "compliant" else 1 - result["confidence"],
            "non_compliant": result["confidence"] if result["prediction"] == "non_compliant" else 1 - result["confidence"]
        }

        # Cache result
        if self.enable_cache:
            self.cache.set(log_message, context, result)

        return result

    async def analyze_batch(
        self,
        logs: List[Dict[str, Any]],
        include_reasoning: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple logs.

        Currently processes sequentially. Future optimization:
        batch into single prompt or parallel requests.
        """
        results = []
        for log_entry in logs:
            log_message = log_entry.get("log_message", "")
            context = {k: v for k, v in log_entry.items() if k != "log_message"}

            result = await self.analyze_log(
                log_message=log_message,
                context=context,
                include_reasoning=include_reasoning
            )
            results.append(result)

        return results

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        cache_stats = self.cache.stats() if self.cache else {}
        return {
            "provider": self.provider,
            "model": self.model,
            "total_requests": self.total_requests,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "estimated_cost_usd": self._estimate_cost(),
            "cache": cache_stats
        }

    def _estimate_cost(self) -> float:
        """Estimate API cost based on token usage."""
        # Approximate pricing (as of 2024)
        if self.provider == "anthropic":
            if "opus" in self.model:
                input_rate = 0.015 / 1000
                output_rate = 0.075 / 1000
            elif "sonnet" in self.model:
                input_rate = 0.003 / 1000
                output_rate = 0.015 / 1000
            else:  # haiku
                input_rate = 0.00025 / 1000
                output_rate = 0.00125 / 1000
        else:  # openai
            if "gpt-4" in self.model:
                input_rate = 0.01 / 1000
                output_rate = 0.03 / 1000
            else:
                input_rate = 0.0005 / 1000
                output_rate = 0.0015 / 1000

        return (self.total_input_tokens * input_rate +
                self.total_output_tokens * output_rate)


# =============================================================================
# Synchronous wrapper for non-async contexts
# =============================================================================

class SyncComplianceLLMClient(ComplianceLLMClient):
    """Synchronous version of the LLM client."""

    def analyze_log_sync(
        self,
        log_message: str,
        context: Optional[Dict[str, Any]] = None,
        include_reasoning: bool = True
    ) -> Dict[str, Any]:
        """Synchronous log analysis."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self.analyze_log(log_message, context, include_reasoning)
        )

    def analyze_batch_sync(
        self,
        logs: List[Dict[str, Any]],
        include_reasoning: bool = True
    ) -> List[Dict[str, Any]]:
        """Synchronous batch analysis."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self.analyze_batch(logs, include_reasoning)
        )
