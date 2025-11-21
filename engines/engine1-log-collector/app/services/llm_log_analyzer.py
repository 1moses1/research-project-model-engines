"""
LLM Log Analyzer Service
Uses OpenAI GPT-4 to semantically understand and analyze log events for compliance
Similar to ENGINE 2's LLM processor but specialized for log analysis
"""

from typing import Dict, List, Optional, Any
import json
import os
from pathlib import Path


class LLMLogAnalyzer:
    """Analyzes log events using LLM for semantic understanding and control mapping"""

    def __init__(self, api_key: Optional[str] = None, control_taxonomy_path: Optional[str] = None):
        self.api_key = api_key
        self.enabled = bool(api_key)

        # Load Rwanda NCSA controls for baseline
        self.rwanda_controls = self._load_rwanda_controls(control_taxonomy_path)
        print(f"✅ Loaded {len(self.rwanda_controls)} Rwanda NCSA controls for LLM log analysis")

        if self.enabled:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=api_key)
                print("✅ OpenAI client initialized for log analysis")
            except ImportError:
                print("⚠️  OpenAI package not installed - using regex-only mode")
                self.enabled = False
                self.client = None
        else:
            print("⚠️  No API key provided - using regex-only mode for logs")
            self.client = None

    def _load_rwanda_controls(self, taxonomy_path: Optional[str] = None) -> List[Dict]:
        """Load Rwanda NCSA controls from taxonomy"""
        try:
            if taxonomy_path is None:
                taxonomy_path = os.getenv(
                    'CONTROL_TAXONOMY_PATH',
                    '/app/data/control_taxonomy_validated.json'
                )

            # Try alternate paths
            if not os.path.exists(taxonomy_path):
                # Try relative path from log_collector
                alt_path = '/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine/data/processed/control_taxonomy_validated.json'
                if os.path.exists(alt_path):
                    taxonomy_path = alt_path

            with open(taxonomy_path, 'r') as f:
                taxonomy_data = json.load(f)

            # Extract Rwanda controls
            rwanda_controls = taxonomy_data.get('rwanda', [])

            # Format for LLM prompt (simplified for log analysis)
            simplified_controls = []
            for ctrl in rwanda_controls:
                simplified_controls.append({
                    'control_id': ctrl['control_id'],
                    'name': ctrl['name'],
                    'family': ctrl['family'],
                    'description': ctrl.get('description', '')[:150],  # Shorter for log context
                    'log_indicators': ctrl.get('log_indicators', [])[:3]  # First 3 indicators
                })

            return simplified_controls

        except Exception as e:
            print(f"⚠️ Could not load Rwanda controls: {str(e)}")
            return []

    def is_enabled(self) -> bool:
        """Check if LLM is enabled"""
        return self.enabled

    async def analyze_log(
        self,
        log_message: str,
        parsed_data: Dict[str, Any],
        source: str = "generic"
    ) -> Dict:
        """
        Analyze a log event using LLM for semantic understanding

        Args:
            log_message: Raw log message
            parsed_data: Pre-parsed data from regex parser
            source: Log source type

        Returns:
            Dictionary with LLM analysis results including:
            - mapped_controls: List of relevant Rwanda NCSA controls
            - event_type: Classified event type
            - compliance_status: compliant or non_compliant
            - severity: critical, high, medium, low
            - indicators: List of compliance indicators
            - confidence: Confidence score (0.0-1.0)
        """
        if self.enabled and self.client:
            return await self._analyze_with_llm(log_message, parsed_data, source)
        else:
            return self._analyze_regex_only(log_message, parsed_data, source)

    async def _analyze_with_llm(
        self,
        log_message: str,
        parsed_data: Dict[str, Any],
        source: str
    ) -> Dict:
        """Analyze log using OpenAI GPT-4 for semantic understanding"""
        try:
            # Prepare control context (use top 50 for token efficiency)
            controls_sample = self.rwanda_controls[:50]
            controls_context = json.dumps([{
                'id': c['control_id'],
                'name': c['name'],
                'family': c['family'],
                'indicators': c.get('log_indicators', [])
            } for c in controls_sample], indent=2)

            # Build context from parsed data
            context = f"""
Source: {source}
User: {parsed_data.get('user', 'N/A')}
IP: {parsed_data.get('ip_address', 'N/A')}
Action: {parsed_data.get('action', 'N/A')}
Resource: {parsed_data.get('resource', 'N/A')}
Status Code: {parsed_data.get('status_code', 'N/A')}
"""

            prompt = f"""You are a cybersecurity compliance auditor analyzing log events for Rwanda NCSA compliance.

TASK: Analyze this log event and map it to relevant Rwanda NCSA controls.

RWANDA NCSA CONTROLS (First 50):
{controls_context}

LOG EVENT:
Message: {log_message}
{context}

ANALYSIS REQUIRED:
1. Identify the event type (e.g., authentication_failure, access_granted, policy_violation, etc.)
2. Map to 1-3 most relevant Rwanda NCSA controls from the list
3. Determine compliance status:
   - "compliant": Normal authorized activity
   - "non_compliant": Policy violation, unauthorized access, security incident
4. Assign severity: critical, high, medium, low
5. List 1-3 specific compliance indicators
6. Provide confidence score (0.0-1.0)

EXAMPLES:
- "Failed login attempt" → authentication_failure, non_compliant, maps to AC-* controls
- "User admin logged in successfully" → authentication_success, compliant (if business hours)
- "Permission denied" → authorization_failure, non_compliant, high severity
- "File deleted" → data_modification, depends on authorization

Return ONLY valid JSON:
{{
  "event_type": "authentication_failure",
  "mapped_controls": [
    {{
      "control_id": "RWNCSA-AC-17",
      "relevance": 0.95,
      "reason": "Failed authentication attempt"
    }}
  ],
  "compliance_status": "non_compliant",
  "severity": "high",
  "indicators": ["off_hours_access_attempt", "high_privilege_account"],
  "confidence": 0.89,
  "llm_interpretation": "Brief explanation of the event"
}}

Analyze the log event (JSON only):"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Rwanda NCSA compliance auditor analyzing log events. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Very low for consistent analysis
                max_tokens=800  # Shorter responses for logs
            )

            content = response.choices[0].message.content

            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                    result = json.loads(json_str)
                    return result
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                    result = json.loads(json_str)
                    return result
                else:
                    raise

        except Exception as e:
            print(f"⚠️ LLM analysis error: {str(e)}")
            print("⚠️ Falling back to regex-only analysis")
            return self._analyze_regex_only(log_message, parsed_data, source)

    def _analyze_regex_only(
        self,
        log_message: str,
        parsed_data: Dict[str, Any],
        source: str
    ) -> Dict:
        """
        Fallback analysis using regex patterns only (no LLM)
        Provides basic control mapping based on keywords
        """
        log_lower = log_message.lower()

        # Determine event type
        event_type = "unknown"
        if any(word in log_lower for word in ["fail", "denied", "reject", "error"]):
            event_type = "failure_event"
        elif any(word in log_lower for word in ["success", "accept", "grant", "allow"]):
            event_type = "success_event"
        elif any(word in log_lower for word in ["login", "logon", "auth"]):
            event_type = "authentication_event"
        elif any(word in log_lower for word in ["access", "permission", "authoriz"]):
            event_type = "authorization_event"
        elif any(word in log_lower for word in ["delete", "remove", "drop", "modify"]):
            event_type = "data_modification"
        elif any(word in log_lower for word in ["upload", "download", "transfer"]):
            event_type = "data_transfer"

        # Determine compliance status (basic heuristic)
        status_code = parsed_data.get('status_code')
        compliance_status = "compliant"
        severity = "low"

        if status_code:
            if status_code >= 400:
                compliance_status = "non_compliant"
                if status_code >= 500:
                    severity = "high"
                elif status_code == 401 or status_code == 403:
                    severity = "medium"
        elif any(word in log_lower for word in ["fail", "error", "denied", "reject"]):
            compliance_status = "non_compliant"
            severity = "medium"

        # Map to controls (basic keyword matching)
        mapped_controls = []

        if "auth" in log_lower or "login" in log_lower:
            mapped_controls.append({
                "control_id": "RWNCSA-AC-17",
                "relevance": 0.7,
                "reason": "Authentication-related event"
            })

        if "access" in log_lower or "permission" in log_lower:
            mapped_controls.append({
                "control_id": "RWNCSA-AC-3",
                "relevance": 0.6,
                "reason": "Access control event"
            })

        if "audit" in log_lower or "log" in log_lower:
            mapped_controls.append({
                "control_id": "RWNCSA-AU-2",
                "relevance": 0.5,
                "reason": "Audit logging event"
            })

        # Default control if none matched
        if not mapped_controls:
            mapped_controls.append({
                "control_id": "RWNCSA-SI-4",
                "relevance": 0.4,
                "reason": "General system information event"
            })

        # Build indicators
        indicators = []
        if compliance_status == "non_compliant":
            indicators.append("potential_violation")
        if severity in ["high", "critical"]:
            indicators.append("high_severity_event")
        if parsed_data.get('user') == 'admin' or parsed_data.get('user') == 'root':
            indicators.append("high_privilege_account")

        return {
            "event_type": event_type,
            "mapped_controls": mapped_controls[:3],  # Top 3
            "compliance_status": compliance_status,
            "severity": severity,
            "indicators": indicators,
            "confidence": 0.5,  # Lower confidence for regex-only
            "llm_interpretation": f"Regex-based analysis: {event_type} detected"
        }

    async def analyze_batch(
        self,
        log_events: List[Dict[str, Any]]
    ) -> List[Dict]:
        """
        Analyze multiple log events in batch

        Args:
            log_events: List of dicts with 'log_message', 'parsed_data', 'source'

        Returns:
            List of analysis results
        """
        results = []

        for event in log_events:
            result = await self.analyze_log(
                log_message=event.get('log_message', ''),
                parsed_data=event.get('parsed_data', {}),
                source=event.get('source', 'generic')
            )
            results.append(result)

        return results
