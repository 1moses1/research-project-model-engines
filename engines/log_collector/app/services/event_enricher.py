"""
Event Enricher Service
Enriches normalized events with additional context
"""

from typing import Dict, Optional
import re


class EventEnricher:
    """Enriches log events with additional context"""

    def __init__(self):
        # GeoIP database would go here in production
        self.ip_geolocation = {
            # Mock data for demo
            "192.168.1.": {"country": "Local Network", "city": "Internal"},
            "10.0.": {"country": "Local Network", "city": "Internal"},
            "172.16.": {"country": "Local Network", "city": "Internal"},
        }

        # User risk profiles
        self.user_risk_profiles = {}

        # Known malicious IPs (would be loaded from threat intelligence feed)
        self.threat_ips = set()

    def enrich(self, event: Dict) -> Dict:
        """
        Enrich event with additional context

        Args:
            event: Normalized event

        Returns:
            Enriched event
        """
        enriched = event.copy()

        # Add geolocation if IP available
        if event.get("ip_address"):
            geo_data = self._get_geolocation(event["ip_address"])
            if geo_data:
                enriched["metadata"]["geo_location"] = geo_data

            # Check threat intelligence
            if self._is_threat_ip(event["ip_address"]):
                enriched["metadata"]["threat_detected"] = True
                enriched["metadata"]["threat_type"] = "malicious_ip"

        # Enrich user data
        if event.get("user"):
            user_context = self._get_user_context(event["user"])
            if user_context:
                enriched["metadata"]["user_context"] = user_context

        # Classify event type
        event_type = self._classify_event_type(event)
        enriched["metadata"]["event_type"] = event_type

        # Add risk score
        risk_score = self._calculate_risk_score(event)
        enriched["metadata"]["risk_score"] = risk_score

        # Detect anomalies
        is_anomaly, anomaly_reason = self._detect_anomaly(event)
        if is_anomaly:
            enriched["metadata"]["anomaly_detected"] = True
            enriched["metadata"]["anomaly_reason"] = anomaly_reason

        # Add compliance context
        compliance_context = self._get_compliance_context(event)
        if compliance_context:
            enriched["metadata"]["compliance_context"] = compliance_context

        return enriched

    def _get_geolocation(self, ip_address: str) -> Optional[Dict]:
        """Get geolocation data for IP address"""
        # Check if private IP
        if self._is_private_ip(ip_address):
            return {"country": "Private Network", "city": "Internal", "is_private": True}

        # Mock geolocation lookup
        for prefix, location in self.ip_geolocation.items():
            if ip_address.startswith(prefix):
                return location

        # Default for unknown
        return {"country": "Unknown", "city": "Unknown", "is_private": False}

    def _is_private_ip(self, ip_address: str) -> bool:
        """Check if IP is private/internal"""
        private_ranges = [
            r"^10\.",
            r"^172\.(?:1[6-9]|2\d|3[01])\.",
            r"^192\.168\.",
            r"^127\.",
            r"^169\.254\.",
        ]

        for pattern in private_ranges:
            if re.match(pattern, ip_address):
                return True

        return False

    def _is_threat_ip(self, ip_address: str) -> bool:
        """Check if IP is in threat intelligence database"""
        return ip_address in self.threat_ips

    def _get_user_context(self, username: str) -> Dict:
        """Get user context and risk profile"""
        # In production, this would query user database
        return {
            "username": username,
            "risk_level": "normal",
            "privileged": username.startswith("admin") or username.startswith("root"),
            "department": "unknown",
        }

    def _classify_event_type(self, event: Dict) -> str:
        """Classify event type based on action and content"""
        action = (event.get("action") or "").lower()
        message = (event.get("log_message") or "").lower()
        resource = (event.get("resource") or "").lower()

        # Authentication events
        if any(keyword in message for keyword in ["login", "logout", "auth", "password", "credential"]):
            if "failed" in message or "denied" in message:
                return "authentication_failure"
            elif "success" in message:
                return "authentication_success"
            else:
                return "authentication"

        # Access control events
        if any(keyword in message for keyword in ["access", "permission", "denied", "forbidden"]):
            return "access_control"

        # File/data access
        if any(keyword in message for keyword in ["file", "read", "write", "download", "upload"]):
            return "data_access"

        # Network events
        if any(keyword in message for keyword in ["connection", "network", "firewall", "port"]):
            return "network"

        # Configuration changes
        if any(keyword in message for keyword in ["config", "setting", "modify", "change", "update"]):
            return "configuration_change"

        # System events
        if any(keyword in message for keyword in ["start", "stop", "restart", "shutdown", "boot"]):
            return "system_event"

        return "generic"

    def _calculate_risk_score(self, event: Dict) -> float:
        """
        Calculate risk score for event (0.0 - 1.0)

        Factors:
        - Failed authentication attempts
        - Privileged user actions
        - External IP addresses
        - Non-business hours
        - Error/failure status codes
        """
        risk_score = 0.0

        # Check for failure indicators
        message = (event.get("log_message") or "").lower()
        if any(keyword in message for keyword in ["failed", "error", "denied", "unauthorized"]):
            risk_score += 0.3

        # Check status code
        status_code = event.get("status_code")
        if status_code:
            if status_code >= 400:
                risk_score += 0.2
            if status_code >= 500:
                risk_score += 0.1

        # Check for privileged user
        user = event.get("user")
        if user and (user.startswith("admin") or user.startswith("root")):
            risk_score += 0.2

        # Check for external IP
        ip = event.get("ip_address")
        if ip and not self._is_private_ip(ip):
            risk_score += 0.2

        # Check severity
        severity = event.get("severity")
        if severity in ["CRITICAL", "ERROR"]:
            risk_score += 0.3
        elif severity == "WARNING":
            risk_score += 0.1

        # Cap at 1.0
        return min(risk_score, 1.0)

    def _detect_anomaly(self, event: Dict) -> tuple[bool, Optional[str]]:
        """
        Detect anomalies in event

        Returns:
            (is_anomaly, reason)
        """
        message = (event.get("log_message") or "").lower()

        # Multiple failed login attempts
        if "failed" in message and "login" in message:
            return (True, "failed_authentication")

        # Suspicious privilege escalation
        if "sudo" in message or "privilege" in message:
            return (True, "privilege_escalation")

        # Unusual file access
        if any(keyword in message for keyword in ["/etc/shadow", "/etc/passwd", "credential"]):
            return (True, "sensitive_file_access")

        # Port scanning
        if "port" in message and "scan" in message:
            return (True, "port_scan")

        # SQL injection attempts
        if any(keyword in message for keyword in ["union select", "or 1=1", "drop table"]):
            return (True, "sql_injection_attempt")

        return (False, None)

    def _get_compliance_context(self, event: Dict) -> Optional[Dict]:
        """Get compliance context for event"""
        event_type = event.get("metadata", {}).get("event_type")

        # Map event types to compliance controls
        compliance_mapping = {
            "authentication": ["AC-2", "IA-2", "IA-3"],
            "authentication_failure": ["AC-7", "AU-2", "SI-4"],
            "access_control": ["AC-3", "AC-6", "AU-2"],
            "data_access": ["AC-4", "AU-9", "SC-28"],
            "configuration_change": ["CM-2", "CM-3", "AU-2"],
            "network": ["SC-7", "SC-8", "SI-4"],
        }

        controls = compliance_mapping.get(event_type, [])

        if controls:
            return {
                "applicable_controls": controls,
                "requires_audit": True,
                "retention_required": True,
            }

        return None
