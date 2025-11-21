#!/usr/bin/env python3
"""
SIEM/SOAR Integration Adapter
Converts unstructured inputs into formats compatible with security systems:
- Splunk, ELK Stack, QRadar, ArcSight (SIEM)
- Cortex XSOAR, Phantom, Demisto (SOAR)
- CEF, LEEF, Syslog formats
"""

import json
import socket
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SIEMFormatter:
    """Format security events for SIEM ingestion"""

    @staticmethod
    def to_cef(event: Dict) -> str:
        """
        Convert to Common Event Format (CEF)
        Used by: ArcSight, Splunk, QRadar

        Format: CEF:Version|Device Vendor|Device Product|Device Version|Signature ID|Name|Severity|Extension
        """
        # Extract fields
        severity_map = {'low': 3, 'medium': 6, 'critical': 10}
        severity = severity_map.get(event.get('severity', 'low'), 5)

        compliance_status = event.get('compliance_status', 'unknown')
        control_id = event.get('control_id', 'UNKNOWN')

        # Build CEF header
        cef_header = [
            "CEF:0",  # Version
            "Rwanda NCSA",  # Device Vendor
            "ML Compliance Engine",  # Device Product
            "1.0",  # Device Version
            control_id,  # Signature ID
            f"Compliance Violation - {compliance_status}",  # Name
            str(severity)  # Severity
        ]

        # Build CEF extension
        extensions = []

        # Add standard fields
        if 'timestamp' in event or 'processed_timestamp' in event:
            timestamp = event.get('processed_timestamp', event.get('timestamp', ''))
            extensions.append(f"rt={timestamp}")

        if 'entities' in event:
            entities = event['entities']
            if 'ip_address' in entities and entities['ip_address']:
                extensions.append(f"src={entities['ip_address'][0]}")
            if 'user_id' in entities and entities['user_id']:
                extensions.append(f"suser={entities['user_id'][0]}")
            if 'ports' in entities and entities['ports']:
                extensions.append(f"dpt={entities['ports'][0]}")

        # Add custom fields
        extensions.append(f"cs1Label=Confidence Score")
        extensions.append(f"cs1={event.get('confidence_score', 0):.2%}")

        extensions.append(f"cs2Label=Control Family")
        extensions.append(f"cs2={event.get('control_family', 'Unknown')}")

        extensions.append(f"cs3Label=Framework")
        extensions.append(f"cs3={event.get('framework', 'NIST-800-53')}")

        if 'mitre_tactics' in event:
            tactics = ','.join(event['mitre_tactics'][:3])
            extensions.append(f"cs4Label=MITRE Tactics")
            extensions.append(f"cs4={tactics}")

        # Add message
        msg = event.get('log_message', event.get('raw_text', ''))[:200]
        extensions.append(f"msg={msg}")

        # Combine
        cef_string = '|'.join(cef_header) + '|' + ' '.join(extensions)

        return cef_string

    @staticmethod
    def to_leef(event: Dict) -> str:
        """
        Convert to Log Event Extended Format (LEEF)
        Used by: IBM QRadar

        Format: LEEF:Version|Vendor|Product|Version|EventID|key=value
        """
        # Build LEEF header
        control_id = event.get('control_id', 'UNKNOWN')

        leef_header = [
            "LEEF:2.0",  # Version
            "Rwanda NCSA",  # Vendor
            "ML Compliance Engine",  # Product
            "1.0",  # Version
            control_id  # Event ID
        ]

        # Build key-value pairs
        kv_pairs = []

        kv_pairs.append(f"devTime={event.get('processed_timestamp', datetime.now().isoformat())}")
        kv_pairs.append(f"cat={event.get('compliance_status', 'unknown')}")
        kv_pairs.append(f"sev={event.get('severity', 'low')}")
        kv_pairs.append(f"confidence={event.get('confidence_score', 0):.2%}")
        kv_pairs.append(f"controlFamily={event.get('control_family', 'Unknown')}")
        kv_pairs.append(f"framework={event.get('framework', 'NIST-800-53')}")

        # Add entities
        if 'entities' in event:
            entities = event['entities']
            if 'ip_address' in entities and entities['ip_address']:
                kv_pairs.append(f"src={entities['ip_address'][0]}")
            if 'user_id' in entities and entities['user_id']:
                kv_pairs.append(f"usrName={entities['user_id'][0]}")

        # Add message
        msg = event.get('log_message', event.get('raw_text', ''))[:200]
        kv_pairs.append(f"msg={msg}")

        # Combine
        leef_string = '|'.join(leef_header) + '|' + '\t'.join(kv_pairs)

        return leef_string

    @staticmethod
    def to_json(event: Dict) -> str:
        """
        Convert to JSON format
        Used by: ELK Stack, Splunk, modern SIEMs
        """
        # Create structured JSON
        structured_event = {
            'timestamp': event.get('processed_timestamp', datetime.now().isoformat()),
            'event_type': 'compliance_check',
            'compliance': {
                'status': event.get('compliance_status', 'unknown'),
                'confidence': event.get('confidence_score', 0),
                'severity': event.get('severity', 'low')
            },
            'control': {
                'id': event.get('control_id', 'UNKNOWN'),
                'family': event.get('control_family', 'Unknown'),
                'framework': event.get('framework', 'NIST-800-53')
            },
            'threat_intel': {
                'mitre_tactics': event.get('mitre_tactics', []),
                'mitre_techniques': event.get('mitre_techniques', [])
            },
            'entities': event.get('entities', {}),
            'message': event.get('log_message', event.get('raw_text', '')),
            'metadata': event.get('metadata', {}),
            'source': event.get('source_type', 'unknown')
        }

        # Add RAG context if available
        if 'rag_context' in event:
            structured_event['rag_context'] = event['rag_context']

        return json.dumps(structured_event)

    @staticmethod
    def to_syslog(event: Dict, facility: int = 16, severity_level: int = 5) -> str:
        """
        Convert to Syslog format (RFC 5424)
        Used by: Universal syslog receivers

        Format: <Priority>Version Timestamp Hostname App-Name ProcID MsgID SD Message
        """
        # Calculate priority
        severity_map = {'low': 6, 'medium': 4, 'critical': 2}
        severity = severity_map.get(event.get('severity', 'low'), 5)
        priority = (facility * 8) + severity

        # Build structured data
        control_id = event.get('control_id', 'UNKNOWN')
        compliance_status = event.get('compliance_status', 'unknown')
        confidence = event.get('confidence_score', 0)

        structured_data = (
            f"[compliance@32473 "
            f"controlId=\"{control_id}\" "
            f"status=\"{compliance_status}\" "
            f"confidence=\"{confidence:.2%}\" "
            f"framework=\"{event.get('framework', 'NIST-800-53')}\"]"
        )

        # Build syslog message
        timestamp = event.get('processed_timestamp', datetime.now().isoformat())
        hostname = socket.gethostname()
        app_name = "compliance-engine"
        proc_id = "-"
        msg_id = control_id

        message = event.get('log_message', event.get('raw_text', ''))[:200]

        syslog_msg = (
            f"<{priority}>1 {timestamp} {hostname} {app_name} "
            f"{proc_id} {msg_id} {structured_data} {message}"
        )

        return syslog_msg


class SOARAdapter:
    """Adapter for SOAR platforms (Cortex XSOAR, Phantom, Demisto)"""

    @staticmethod
    def to_xsoar_incident(event: Dict) -> Dict:
        """
        Convert to Cortex XSOAR incident format
        """
        severity_map = {'low': 1, 'medium': 2, 'critical': 4}

        incident = {
            'name': f"Compliance Violation - {event.get('control_id', 'UNKNOWN')}",
            'type': 'Compliance Violation',
            'severity': severity_map.get(event.get('severity', 'low'), 1),
            'occurred': event.get('processed_timestamp', datetime.now().isoformat()),
            'details': event.get('log_message', event.get('raw_text', '')),
            'customFields': {
                'compliancestatus': event.get('compliance_status', 'unknown'),
                'confidencescore': event.get('confidence_score', 0),
                'controlid': event.get('control_id', 'UNKNOWN'),
                'controlfamily': event.get('control_family', 'Unknown'),
                'framework': event.get('framework', 'NIST-800-53'),
                'mitretactics': ','.join(event.get('mitre_tactics', [])),
                'mitretechniques': ','.join(event.get('mitre_techniques', []))
            },
            'labels': [
                {'type': 'Control', 'value': event.get('control_id', 'UNKNOWN')},
                {'type': 'Severity', 'value': event.get('severity', 'low')},
                {'type': 'Framework', 'value': event.get('framework', 'NIST-800-53')}
            ]
        }

        # Add entities as labels
        if 'entities' in event:
            entities = event['entities']
            if 'ip_address' in entities and entities['ip_address']:
                for ip in entities['ip_address'][:3]:
                    incident['labels'].append({'type': 'IP', 'value': ip})
            if 'user_id' in entities and entities['user_id']:
                for user in entities['user_id'][:3]:
                    incident['labels'].append({'type': 'User', 'value': user})

        return incident

    @staticmethod
    def to_phantom_container(event: Dict) -> Dict:
        """
        Convert to Splunk Phantom/SOAR container format
        """
        severity_map = {'low': 'low', 'medium': 'medium', 'critical': 'high'}

        container = {
            'name': f"Compliance Violation - {event.get('control_id', 'UNKNOWN')}",
            'description': event.get('log_message', event.get('raw_text', ''))[:500],
            'severity': severity_map.get(event.get('severity', 'low'), 'low'),
            'status': 'new',
            'label': 'compliance',
            'custom_fields': {
                'compliance_status': event.get('compliance_status', 'unknown'),
                'confidence_score': event.get('confidence_score', 0),
                'control_id': event.get('control_id', 'UNKNOWN'),
                'control_family': event.get('control_family', 'Unknown'),
                'framework': event.get('framework', 'NIST-800-53')
            },
            'artifacts': []
        }

        # Add artifacts (entities)
        if 'entities' in event:
            entities = event['entities']

            if 'ip_address' in entities and entities['ip_address']:
                for ip in entities['ip_address']:
                    container['artifacts'].append({
                        'cef': {'sourceAddress': ip},
                        'name': 'IP Address',
                        'label': 'artifact'
                    })

            if 'user_id' in entities and entities['user_id']:
                for user in entities['user_id']:
                    container['artifacts'].append({
                        'cef': {'userName': user},
                        'name': 'User Account',
                        'label': 'artifact'
                    })

            if 'file_path' in entities and entities['file_path']:
                for path in entities['file_path']:
                    container['artifacts'].append({
                        'cef': {'filePath': path},
                        'name': 'File Path',
                        'label': 'artifact'
                    })

        return container


class SecuritySystemIntegration:
    """
    Complete integration system for security platforms
    Routes events to appropriate systems in correct format
    """

    def __init__(self):
        self.siem_formatter = SIEMFormatter()
        self.soar_adapter = SOARAdapter()

    def format_for_system(self, event: Dict, target_system: str) -> str:
        """
        Format event for specific security system

        Args:
            event: Structured event from NLP processor
            target_system: Target system name

        Returns:
            Formatted event string
        """
        formatters = {
            'splunk': self.siem_formatter.to_json,
            'elk': self.siem_formatter.to_json,
            'elasticsearch': self.siem_formatter.to_json,
            'qradar': self.siem_formatter.to_leef,
            'arcsight': self.siem_formatter.to_cef,
            'cef': self.siem_formatter.to_cef,
            'leef': self.siem_formatter.to_leef,
            'syslog': self.siem_formatter.to_syslog,
            'json': self.siem_formatter.to_json
        }

        formatter = formatters.get(target_system.lower(), self.siem_formatter.to_json)
        return formatter(event)

    def create_soar_incident(self, event: Dict, platform: str = 'xsoar') -> Dict:
        """
        Create SOAR incident/container

        Args:
            event: Structured event
            platform: SOAR platform (xsoar, phantom, demisto)

        Returns:
            SOAR incident/container dict
        """
        if platform.lower() in ['xsoar', 'demisto']:
            return self.soar_adapter.to_xsoar_incident(event)
        elif platform.lower() in ['phantom', 'splunk-soar']:
            return self.soar_adapter.to_phantom_container(event)
        else:
            # Default to XSOAR format
            return self.soar_adapter.to_xsoar_incident(event)

    def send_to_syslog(self, event: Dict, host: str = 'localhost', port: int = 514):
        """Send event to syslog server (UDP)"""
        try:
            syslog_msg = self.siem_formatter.to_syslog(event)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(syslog_msg.encode('utf-8'), (host, port))
            sock.close()
            logger.info(f"Sent event to syslog {host}:{port}")
        except Exception as e:
            logger.error(f"Failed to send syslog: {e}")

    def batch_format(self, events: List[Dict], target_system: str) -> List[str]:
        """Format multiple events"""
        return [self.format_for_system(event, target_system) for event in events]


def main():
    """Test SIEM/SOAR integration"""
    print("\n" + "="*100)
    print("SIEM/SOAR INTEGRATION TEST")
    print("="*100 + "\n")

    # Sample event
    sample_event = {
        'raw_text': 'Unauthorized access attempt from IP 192.168.1.100 to database server - Connection denied',
        'processed_timestamp': datetime.now().isoformat(),
        'compliance_status': 'non_compliant',
        'confidence_score': 0.92,
        'severity': 'critical',
        'control_id': 'AC-3',
        'control_family': 'Access Control',
        'framework': 'NIST-800-53',
        'mitre_tactics': ['initial-access', 'credential-access'],
        'mitre_techniques': ['T1110'],
        'entities': {
            'ip_address': ['192.168.1.100'],
            'user_id': ['admin']
        },
        'log_message': 'Unauthorized access attempt detected',
        'metadata': {}
    }

    integrator = SecuritySystemIntegration()

    # Test SIEM formats
    print("SIEM FORMATS:\n")

    print("1. CEF (ArcSight):")
    print(integrator.format_for_system(sample_event, 'cef'))
    print()

    print("2. LEEF (QRadar):")
    print(integrator.format_for_system(sample_event, 'leef'))
    print()

    print("3. JSON (ELK/Splunk):")
    print(json.dumps(json.loads(integrator.format_for_system(sample_event, 'json')), indent=2))
    print()

    print("4. Syslog (RFC 5424):")
    print(integrator.format_for_system(sample_event, 'syslog'))
    print()

    # Test SOAR formats
    print("\n" + "="*100)
    print("SOAR FORMATS:\n")

    print("1. Cortex XSOAR Incident:")
    xsoar_incident = integrator.create_soar_incident(sample_event, 'xsoar')
    print(json.dumps(xsoar_incident, indent=2))
    print()

    print("2. Splunk Phantom Container:")
    phantom_container = integrator.create_soar_incident(sample_event, 'phantom')
    print(json.dumps(phantom_container, indent=2))

    print("\n" + "="*100)


if __name__ == '__main__':
    main()
