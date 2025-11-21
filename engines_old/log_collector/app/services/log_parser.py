"""
Log Parser Service
Parses raw log messages from various sources with LLM enhancement
"""

from typing import Dict, Optional
import re
from datetime import datetime
from .llm_log_analyzer import LLMLogAnalyzer
from .syslog_adapter import SyslogAdapter
from .windows_event_adapter import WindowsEventAdapter


class LogParser:
    """Parses log messages from different sources with LLM enhancement"""

    def __init__(self, llm_analyzer: Optional[LLMLogAnalyzer] = None):
        # LLM analyzer for semantic understanding
        self.llm_analyzer = llm_analyzer

        # Format-specific adapters
        self.syslog_adapter = SyslogAdapter(llm_analyzer=llm_analyzer)
        self.windows_adapter = WindowsEventAdapter(llm_analyzer=llm_analyzer)

        # Common log patterns
        self.patterns = {
            "syslog": re.compile(
                r"(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+"
                r"(?P<host>\S+)\s+"
                r"(?P<process>\S+?):\s+"
                r"(?P<message>.*)"
            ),
            "apache": re.compile(
                r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
                r"(?P<user>\S+)\s+"
                r"(?P<auth_user>\S+)\s+"
                r"\[(?P<timestamp>[^\]]+)\]\s+"
                r'\"(?P<method>\w+)\s+(?P<path>\S+)\s+(?P<protocol>[^\"]+)\"\s+'
                r"(?P<status>\d+)\s+"
                r"(?P<size>\d+)"
            ),
            "nginx": re.compile(
                r"(?P<ip>\d+\.\d+\.\d+\.\d+)\s+"
                r"-\s+"
                r"(?P<user>\S+)\s+"
                r"\[(?P<timestamp>[^\]]+)\]\s+"
                r'\"(?P<request>[^\"]+)\"\s+'
                r"(?P<status>\d+)\s+"
                r"(?P<size>\d+)\s+"
                r'\"(?P<referrer>[^\"]*)\"\s+'
                r'\"(?P<user_agent>[^\"]+)\"'
            ),
            "json": re.compile(r"\{.*\}"),
            "key_value": re.compile(r"(\w+)=([^\s]+)"),
        }

    def parse(self, raw_message: str, source: str = "generic") -> Dict:
        """
        Parse raw log message

        Args:
            raw_message: Raw log message string
            source: Log source type

        Returns:
            Dictionary of parsed fields
        """
        # Try specific parsers based on source
        if source in ["system_logs", "syslog"]:
            return self._parse_syslog(raw_message)
        elif source in ["web_logs", "apache", "nginx"]:
            return self._parse_web_log(raw_message)
        elif source == "json":
            return self._parse_json(raw_message)
        else:
            return self._parse_generic(raw_message)

    def _parse_syslog(self, message: str) -> Dict:
        """Parse syslog format messages"""
        match = self.patterns["syslog"].match(message)

        if match:
            return {
                "timestamp": match.group("timestamp"),
                "host": match.group("host"),
                "process": match.group("process"),
                "message": match.group("message"),
                "user": self._extract_user(match.group("message")),
                "action": self._extract_action(match.group("message")),
                "ip_address": self._extract_ip(match.group("message")),
            }
        else:
            return self._parse_generic(message)

    def _parse_web_log(self, message: str) -> Dict:
        """Parse web server (Apache/Nginx) logs"""
        # Try Apache format
        match = self.patterns["apache"].match(message)

        if match:
            return {
                "ip_address": match.group("ip"),
                "user": match.group("user") if match.group("user") != "-" else None,
                "timestamp": match.group("timestamp"),
                "method": match.group("method"),
                "path": match.group("path"),
                "protocol": match.group("protocol"),
                "status_code": int(match.group("status")),
                "size": int(match.group("size")),
                "message": f"{match.group('method')} {match.group('path')} {match.group('status')}",
                "action": match.group("method"),
                "resource": match.group("path"),
            }

        # Try Nginx format
        match = self.patterns["nginx"].match(message)

        if match:
            request_parts = match.group("request").split()
            method = request_parts[0] if request_parts else "UNKNOWN"
            path = request_parts[1] if len(request_parts) > 1 else "/"

            return {
                "ip_address": match.group("ip"),
                "user": match.group("user") if match.group("user") != "-" else None,
                "timestamp": match.group("timestamp"),
                "method": method,
                "path": path,
                "status_code": int(match.group("status")),
                "size": int(match.group("size")),
                "user_agent": match.group("user_agent"),
                "message": f"{method} {path} {match.group('status')}",
                "action": method,
                "resource": path,
            }

        return self._parse_generic(message)

    def _parse_json(self, message: str) -> Dict:
        """Parse JSON log messages"""
        try:
            import json
            data = json.loads(message)

            # Normalize JSON structure
            return {
                "timestamp": data.get("timestamp") or data.get("time"),
                "message": data.get("message") or data.get("msg"),
                "user": data.get("user") or data.get("username"),
                "ip_address": data.get("ip") or data.get("client_ip"),
                "action": data.get("action") or data.get("event"),
                "resource": data.get("resource") or data.get("target"),
                "status_code": data.get("status") or data.get("code"),
                "severity": data.get("severity") or data.get("level"),
                **data  # Include all other fields
            }
        except:
            return self._parse_generic(message)

    def _parse_generic(self, message: str) -> Dict:
        """Parse generic log messages"""
        parsed = {
            "message": message,
            "user": self._extract_user(message),
            "ip_address": self._extract_ip(message),
            "action": self._extract_action(message),
            "resource": self._extract_resource(message),
        }

        # Try to extract key=value pairs
        kv_matches = self.patterns["key_value"].findall(message)
        if kv_matches:
            for key, value in kv_matches:
                parsed[key.lower()] = value

        return parsed

    def _extract_user(self, message: str) -> Optional[str]:
        """Extract username from message"""
        # Common patterns
        patterns = [
            r"user[=:]?\s*(\w+)",
            r"username[=:]?\s*(\w+)",
            r"account[=:]?\s*(\w+)",
            r"for\s+(\w+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)

        return None

    def _extract_ip(self, message: str) -> Optional[str]:
        """Extract IP address from message"""
        pattern = r"\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b"
        match = re.search(pattern, message)
        if match:
            return match.group(0)
        return None

    def _extract_action(self, message: str) -> Optional[str]:
        """Extract action/event type from message"""
        # Common action keywords
        actions = [
            "login", "logout", "access", "denied", "failed", "success",
            "create", "delete", "update", "modify", "change",
            "start", "stop", "restart", "connect", "disconnect",
            "upload", "download", "GET", "POST", "PUT", "DELETE"
        ]

        message_lower = message.lower()
        for action in actions:
            if action.lower() in message_lower:
                return action.upper()

        return None

    def _extract_resource(self, message: str) -> Optional[str]:
        """Extract resource/file/path from message"""
        # Common patterns
        patterns = [
            r"file[=:]?\s*([^\s]+)",
            r"path[=:]?\s*([^\s]+)",
            r"resource[=:]?\s*([^\s]+)",
            r"/[\w/\.]+",  # Unix-style paths
            r"[A-Z]:\\[\w\\]+",  # Windows paths
        ]

        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1) if match.lastindex else match.group(0)

        return None

    def extract_status_code(self, message: str) -> Optional[int]:
        """Extract HTTP status code from message"""
        pattern = r"\b([1-5]\d{2})\b"
        match = re.search(pattern, message)
        if match:
            return int(match.group(1))
        return None

    async def parse_with_llm(self, raw_message: str, source: str = "generic") -> Dict:
        """
        Parse log with LLM enhancement

        Args:
            raw_message: Raw log message
            source: Log source type

        Returns:
            Parsed log with LLM semantic enrichment
        """
        # Use specialized adapters for better parsing
        if source in ["system_logs", "syslog"] and raw_message.startswith('<'):
            # Syslog format
            return await self.syslog_adapter.parse_with_llm(raw_message)
        elif source in ["windows_events", "windows"] or '<Event' in raw_message:
            # Windows Event format
            return await self.windows_adapter.parse_with_llm(raw_message)
        else:
            # Generic parsing + LLM enrichment
            parsed = self.parse(raw_message, source)

            if self.llm_analyzer:
                llm_result = await self.llm_analyzer.analyze_log(
                    log_message=raw_message,
                    parsed_data=parsed,
                    source=source
                )

                # Merge LLM results
                parsed['llm_analysis'] = llm_result
                parsed['event_type'] = llm_result.get('event_type', 'unknown')
                parsed['mapped_controls'] = llm_result.get('mapped_controls', [])
                parsed['compliance_status'] = llm_result.get('compliance_status', 'unknown')
                parsed['severity_llm'] = llm_result.get('severity', 'low')
                parsed['confidence'] = llm_result.get('confidence', 0.5)

            return parsed
