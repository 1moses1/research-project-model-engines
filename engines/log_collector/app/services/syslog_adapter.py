"""
Syslog Adapter with LLM Enhancement
Parses syslog messages (RFC 5424 & RFC 3164) with semantic understanding
"""

from typing import Dict, Optional, Any
import re
from datetime import datetime
from .llm_log_analyzer import LLMLogAnalyzer


class SyslogAdapter:
    """Parse syslog messages with LLM semantic enhancement"""

    def __init__(self, llm_analyzer: Optional[LLMLogAnalyzer] = None):
        self.llm_analyzer = llm_analyzer

        # RFC 3164 (BSD syslog) pattern
        self.rfc3164_pattern = re.compile(
            r"<(?P<pri>\d+)>(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+"
            r"(?P<hostname>\S+)\s+"
            r"(?P<tag>\S+?)(?:\[(?P<pid>\d+)\])?:\s+"
            r"(?P<message>.*)"
        )

        # RFC 5424 pattern (more structured)
        self.rfc5424_pattern = re.compile(
            r"<(?P<pri>\d+)>(?P<version>\d+)\s+"
            r"(?P<timestamp>\S+)\s+"
            r"(?P<hostname>\S+)\s+"
            r"(?P<app_name>\S+)\s+"
            r"(?P<procid>\S+)\s+"
            r"(?P<msgid>\S+)\s+"
            r"(?P<structured_data>\S+)\s+"
            r"(?P<message>.*)"
        )

        # Simplified syslog (common in modern systems)
        self.simple_pattern = re.compile(
            r"(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+"
            r"(?P<hostname>\S+)\s+"
            r"(?P<process>\S+?)(?:\[(?P<pid>\d+)\])?:\s+"
            r"(?P<message>.*)"
        )

    def parse(self, raw_log: str) -> Dict[str, Any]:
        """
        Parse syslog message with LLM enhancement

        Args:
            raw_log: Raw syslog message

        Returns:
            Parsed and enriched log data
        """
        # Try RFC 5424 first (most structured)
        parsed = self._try_rfc5424(raw_log)

        if not parsed:
            # Try RFC 3164 (traditional BSD syslog)
            parsed = self._try_rfc3164(raw_log)

        if not parsed:
            # Try simple format
            parsed = self._try_simple(raw_log)

        if not parsed:
            # Fallback: generic parsing
            parsed = self._parse_generic(raw_log)

        return parsed

    async def parse_with_llm(self, raw_log: str) -> Dict[str, Any]:
        """
        Parse syslog and enhance with LLM semantic analysis

        Args:
            raw_log: Raw syslog message

        Returns:
            Parsed log with LLM enrichment
        """
        # Traditional parsing for structure
        parsed = self.parse(raw_log)

        # LLM enrichment for meaning
        if self.llm_analyzer:
            llm_result = await self.llm_analyzer.analyze_log(
                log_message=parsed['message'],
                parsed_data=parsed,
                source='syslog'
            )

            # Merge LLM results
            parsed['llm_analysis'] = llm_result
            parsed['event_type'] = llm_result.get('event_type', 'unknown')
            parsed['mapped_controls'] = llm_result.get('mapped_controls', [])
            parsed['compliance_status'] = llm_result.get('compliance_status', 'unknown')
            parsed['severity_llm'] = llm_result.get('severity', 'low')
            parsed['confidence'] = llm_result.get('confidence', 0.5)

        return parsed

    def _try_rfc5424(self, log: str) -> Optional[Dict]:
        """Try parsing as RFC 5424 syslog"""
        match = self.rfc5424_pattern.match(log)

        if match:
            pri = int(match.group('pri'))
            facility = pri >> 3
            severity = pri & 0x07

            return {
                'format': 'RFC5424',
                'priority': pri,
                'facility': facility,
                'severity': self._map_severity(severity),
                'version': match.group('version'),
                'timestamp': match.group('timestamp'),
                'hostname': match.group('hostname'),
                'app_name': match.group('app_name'),
                'procid': match.group('procid'),
                'msgid': match.group('msgid'),
                'message': match.group('message'),
                'raw': log
            }

        return None

    def _try_rfc3164(self, log: str) -> Optional[Dict]:
        """Try parsing as RFC 3164 (BSD syslog)"""
        match = self.rfc3164_pattern.match(log)

        if match:
            pri = int(match.group('pri'))
            facility = pri >> 3
            severity = pri & 0x07

            return {
                'format': 'RFC3164',
                'priority': pri,
                'facility': facility,
                'severity': self._map_severity(severity),
                'timestamp': match.group('timestamp'),
                'hostname': match.group('hostname'),
                'tag': match.group('tag'),
                'pid': match.group('pid'),
                'message': match.group('message'),
                'raw': log
            }

        return None

    def _try_simple(self, log: str) -> Optional[Dict]:
        """Try parsing simple syslog format (no priority)"""
        match = self.simple_pattern.match(log)

        if match:
            return {
                'format': 'SIMPLE',
                'timestamp': match.group('timestamp'),
                'hostname': match.group('hostname'),
                'process': match.group('process'),
                'pid': match.group('pid'),
                'message': match.group('message'),
                'severity': 'info',  # Default
                'raw': log
            }

        return None

    def _parse_generic(self, log: str) -> Dict:
        """Generic fallback parsing"""
        return {
            'format': 'GENERIC',
            'message': log,
            'timestamp': datetime.now().isoformat(),
            'severity': 'info',
            'raw': log
        }

    def _map_severity(self, severity_code: int) -> str:
        """Map syslog severity code to string"""
        severity_map = {
            0: 'emergency',
            1: 'alert',
            2: 'critical',
            3: 'error',
            4: 'warning',
            5: 'notice',
            6: 'info',
            7: 'debug'
        }
        return severity_map.get(severity_code, 'unknown')

    def extract_user(self, message: str) -> Optional[str]:
        """Extract username from syslog message"""
        patterns = [
            r"user[=:]?\s*(\w+)",
            r"for\s+(\w+)",
            r"by\s+(\w+)",
            r"(\w+)@"
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def extract_ip(self, message: str) -> Optional[str]:
        """Extract IP address from syslog message"""
        ip_pattern = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        match = re.search(ip_pattern, message)
        if match:
            return match.group(0)
        return None
