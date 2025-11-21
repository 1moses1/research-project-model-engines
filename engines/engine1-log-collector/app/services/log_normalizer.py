"""
Log Normalizer Service
Normalizes parsed logs into standard format for ENGINE 3
"""

from typing import Dict, Any, Optional
from datetime import datetime


class LogNormalizer:
    """Normalizes log events to standard format"""

    def __init__(self):
        self.severity_mapping = {
            "EMERGENCY": "CRITICAL",
            "ALERT": "CRITICAL",
            "CRITICAL": "CRITICAL",
            "ERROR": "ERROR",
            "WARNING": "WARNING",
            "WARN": "WARNING",
            "NOTICE": "INFO",
            "INFO": "INFO",
            "INFORMATIONAL": "INFO",
            "DEBUG": "DEBUG",
        }

    def normalize(
        self,
        event_id: str,
        timestamp: str,
        source: str,
        parsed_data: Dict,
        raw_message: str,
        severity: str = "INFO",
        metadata: Dict[str, Any] = None
    ) -> Dict:
        """
        Normalize log event to standard format

        Args:
            event_id: Unique event identifier
            timestamp: Event timestamp
            source: Log source
            parsed_data: Parsed log data
            raw_message: Original raw log message
            severity: Log severity level
            metadata: Additional metadata

        Returns:
            Normalized event dictionary
        """
        # Normalize timestamp
        normalized_timestamp = self._normalize_timestamp(
            parsed_data.get("timestamp") or timestamp
        )

        # Normalize severity
        normalized_severity = self._normalize_severity(
            parsed_data.get("severity") or severity
        )

        # Extract core fields
        user = self._extract_user(parsed_data)
        ip_address = self._extract_ip(parsed_data)
        resource = self._extract_resource(parsed_data)
        action = self._extract_action(parsed_data)
        status_code = self._extract_status_code(parsed_data)

        # Build log message for classification
        log_message = self._build_log_message(parsed_data, raw_message)

        # Build normalized event
        normalized_event = {
            "event_id": event_id,
            "timestamp": normalized_timestamp,
            "source": source,
            "log_message": log_message,
            "user": user,
            "ip_address": ip_address,
            "resource": resource,
            "action": action,
            "status_code": status_code,
            "severity": normalized_severity,
            "raw_message": raw_message,
            "metadata": metadata or {}
        }

        # Add additional fields from parsed data
        for key, value in parsed_data.items():
            if key not in normalized_event and value is not None:
                normalized_event["metadata"][key] = value

        return normalized_event

    def _normalize_timestamp(self, timestamp_str: str) -> str:
        """Normalize timestamp to ISO format"""
        try:
            # If already ISO format
            if "T" in timestamp_str:
                dt = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                return dt.isoformat()

            # Try common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%d/%b/%Y:%H:%M:%S %z",
                "%b %d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    # If no year, use current year
                    if dt.year == 1900:
                        dt = dt.replace(year=datetime.now().year)
                    return dt.isoformat()
                except:
                    continue

            # Fallback to current time
            return datetime.now().isoformat()

        except:
            return datetime.now().isoformat()

    def _normalize_severity(self, severity: str) -> str:
        """Normalize severity level"""
        severity_upper = severity.upper()
        return self.severity_mapping.get(severity_upper, "INFO")

    def _extract_user(self, parsed_data: Dict) -> Optional[str]:
        """Extract user from parsed data"""
        user = parsed_data.get("user") or parsed_data.get("username") or parsed_data.get("account")

        if user and user != "-":
            return user

        return None

    def _extract_ip(self, parsed_data: Dict) -> Optional[str]:
        """Extract IP address from parsed data"""
        ip = (
            parsed_data.get("ip_address")
            or parsed_data.get("ip")
            or parsed_data.get("client_ip")
            or parsed_data.get("source_ip")
        )

        if ip and ip != "-":
            return ip

        return None

    def _extract_resource(self, parsed_data: Dict) -> Optional[str]:
        """Extract resource from parsed data"""
        resource = (
            parsed_data.get("resource")
            or parsed_data.get("path")
            or parsed_data.get("file")
            or parsed_data.get("target")
        )

        if resource and resource != "-":
            return resource

        return None

    def _extract_action(self, parsed_data: Dict) -> Optional[str]:
        """Extract action from parsed data"""
        action = (
            parsed_data.get("action")
            or parsed_data.get("event")
            or parsed_data.get("method")
            or parsed_data.get("operation")
        )

        if action and action != "-":
            return action.upper()

        return None

    def _extract_status_code(self, parsed_data: Dict) -> Optional[int]:
        """Extract status code from parsed data"""
        status = parsed_data.get("status_code") or parsed_data.get("status") or parsed_data.get("code")

        if status:
            try:
                return int(status)
            except:
                # Map common status strings to codes
                status_mapping = {
                    "success": 200,
                    "ok": 200,
                    "failed": 400,
                    "error": 500,
                    "denied": 403,
                    "unauthorized": 401,
                    "forbidden": 403,
                    "not_found": 404,
                }
                return status_mapping.get(str(status).lower())

        return None

    def _build_log_message(self, parsed_data: Dict, raw_message: str) -> str:
        """
        Build standardized log message for classification

        Format: [TIMESTAMP] [SOURCE] [ACTION] [USER] [RESOURCE] [STATUS]
        """
        message = parsed_data.get("message", raw_message)

        # If we have structured data, build a formatted message
        components = []

        if parsed_data.get("action"):
            components.append(f"Action: {parsed_data['action']}")

        if parsed_data.get("user"):
            components.append(f"User: {parsed_data['user']}")

        if parsed_data.get("ip_address"):
            components.append(f"IP: {parsed_data['ip_address']}")

        if parsed_data.get("resource"):
            components.append(f"Resource: {parsed_data['resource']}")

        if parsed_data.get("status_code"):
            components.append(f"Status: {parsed_data['status_code']}")

        if components:
            formatted_message = " | ".join(components)
            return f"{formatted_message} | {message}"
        else:
            return message

    def validate_event(self, event: Dict) -> bool:
        """
        Validate normalized event has required fields

        Args:
            event: Normalized event

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["event_id", "timestamp", "source", "log_message"]

        for field in required_fields:
            if field not in event or not event[field]:
                return False

        return True
