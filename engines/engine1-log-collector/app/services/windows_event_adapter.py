"""
Windows Event Log Adapter with LLM Enhancement
Parses Windows Event Logs (XML format) with semantic understanding
"""

from typing import Dict, Optional, Any
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from .llm_log_analyzer import LLMLogAnalyzer


class WindowsEventAdapter:
    """Parse Windows Event Logs with LLM semantic enhancement"""

    def __init__(self, llm_analyzer: Optional[LLMLogAnalyzer] = None):
        self.llm_analyzer = llm_analyzer

        # Common Windows security event IDs
        self.event_types = {
            # Authentication events
            4624: "Successful logon",
            4625: "Failed logon",
            4634: "Logoff",
            4647: "User-initiated logoff",
            4648: "Logon using explicit credentials",

            # Account management
            4720: "User account created",
            4722: "User account enabled",
            4723: "User changed password",
            4724: "Password reset attempt",
            4725: "User account disabled",
            4726: "User account deleted",

            # Privilege use
            4672: "Special privileges assigned to new logon",
            4673: "Privileged service called",

            # Process events
            4688: "Process created",
            4689: "Process terminated",

            # Object access
            4663: "Attempt to access object",
            4660: "Object deleted",

            # Policy changes
            4719: "System audit policy changed",

            # System events
            4616: "System time changed",
            4697: "Service installed",
            4698: "Scheduled task created"
        }

    def parse(self, raw_event: str) -> Dict[str, Any]:
        """
        Parse Windows Event Log (XML or text format)

        Args:
            raw_event: Raw Windows Event Log entry

        Returns:
            Parsed event data
        """
        # Try XML parsing first
        if raw_event.strip().startswith('<'):
            return self._parse_xml(raw_event)
        else:
            # Try text format parsing
            return self._parse_text(raw_event)

    async def parse_with_llm(self, raw_event: str) -> Dict[str, Any]:
        """
        Parse Windows Event and enhance with LLM semantic analysis

        Args:
            raw_event: Raw Windows Event Log entry

        Returns:
            Parsed event with LLM enrichment
        """
        # Traditional parsing for structure
        parsed = self.parse(raw_event)

        # LLM enrichment for meaning
        if self.llm_analyzer:
            # Build context for LLM
            event_description = self._build_description(parsed)

            llm_result = await self.llm_analyzer.analyze_log(
                log_message=event_description,
                parsed_data=parsed,
                source='windows_event'
            )

            # Merge LLM results
            parsed['llm_analysis'] = llm_result
            parsed['event_type'] = llm_result.get('event_type', 'unknown')
            parsed['mapped_controls'] = llm_result.get('mapped_controls', [])
            parsed['compliance_status'] = llm_result.get('compliance_status', 'unknown')
            parsed['severity_llm'] = llm_result.get('severity', 'low')
            parsed['confidence'] = llm_result.get('confidence', 0.5)
            parsed['llm_interpretation'] = llm_result.get('llm_interpretation', '')

        return parsed

    def _parse_xml(self, xml_str: str) -> Dict[str, Any]:
        """Parse Windows Event XML format"""
        try:
            root = ET.fromstring(xml_str)

            # Define namespaces
            ns = {'Event': 'http://schemas.microsoft.com/win/2004/08/events/event'}

            # Extract System section
            system = root.find('Event:System', ns)
            event_id_elem = system.find('Event:EventID', ns) if system else None
            event_id = int(event_id_elem.text) if event_id_elem is not None else 0

            # Extract basic fields
            computer = system.find('Event:Computer', ns).text if system and system.find('Event:Computer', ns) is not None else 'unknown'
            time_created = system.find('Event:TimeCreated', ns)
            timestamp = time_created.get('SystemTime') if time_created is not None else datetime.now().isoformat()

            # Extract EventData
            event_data = {}
            event_data_elem = root.find('Event:EventData', ns)
            if event_data_elem is not None:
                for data in event_data_elem.findall('Event:Data', ns):
                    name = data.get('Name')
                    value = data.text
                    if name:
                        event_data[name] = value

            # Build parsed result
            parsed = {
                'format': 'Windows Event XML',
                'event_id': event_id,
                'event_description': self.event_types.get(event_id, f'Event ID {event_id}'),
                'timestamp': timestamp,
                'computer': computer,
                'event_data': event_data,
                'user': event_data.get('TargetUserName') or event_data.get('SubjectUserName'),
                'domain': event_data.get('TargetDomainName') or event_data.get('SubjectDomainName'),
                'logon_type': event_data.get('LogonType'),
                'workstation': event_data.get('WorkstationName'),
                'ip_address': event_data.get('IpAddress'),
                'status_code': self._map_event_to_status(event_id),
                'severity': self._determine_severity(event_id),
                'raw': xml_str
            }

            return parsed

        except Exception as e:
            print(f"⚠️ XML parsing error: {str(e)}")
            return self._parse_generic(xml_str)

    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse Windows Event text format"""
        lines = text.split('\n')

        parsed = {
            'format': 'Windows Event Text',
            'message': text,
            'severity': 'info',
            'raw': text
        }

        # Try to extract key fields
        for line in lines:
            if 'Event ID:' in line or 'EventID:' in line:
                match = re.search(r'Event\s*ID[:\s]+(\d+)', line, re.IGNORECASE)
                if match:
                    event_id = int(match.group(1))
                    parsed['event_id'] = event_id
                    parsed['event_description'] = self.event_types.get(event_id, f'Event ID {event_id}')
                    parsed['status_code'] = self._map_event_to_status(event_id)
                    parsed['severity'] = self._determine_severity(event_id)

            elif 'Computer:' in line or 'Source:' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    parsed['computer'] = parts[1].strip()

            elif 'User:' in line or 'Account:' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    parsed['user'] = parts[1].strip()

        return parsed

    def _parse_generic(self, text: str) -> Dict[str, Any]:
        """Generic fallback parsing"""
        return {
            'format': 'Windows Event Generic',
            'message': text,
            'timestamp': datetime.now().isoformat(),
            'severity': 'info',
            'raw': text
        }

    def _map_event_to_status(self, event_id: int) -> int:
        """Map Windows Event ID to HTTP-like status code"""
        # Successful events → 200
        if event_id in [4624, 4634, 4647, 4720, 4722, 4723]:
            return 200

        # Failed authentication → 401
        elif event_id in [4625, 4724]:
            return 401

        # Unauthorized access → 403
        elif event_id in [4673]:
            return 403

        # System errors → 500
        elif event_id in [4697, 4698, 4719]:
            return 500

        # Default
        else:
            return 200

    def _determine_severity(self, event_id: int) -> str:
        """Determine severity based on event ID"""
        # Critical security events
        if event_id in [4625, 4724, 4719, 4697, 4698]:
            return 'high'

        # Privilege events
        elif event_id in [4672, 4673]:
            return 'medium'

        # Normal events
        else:
            return 'low'

    def _build_description(self, parsed: Dict) -> str:
        """Build human-readable description for LLM"""
        event_id = parsed.get('event_id', 0)
        event_desc = parsed.get('event_description', 'Unknown event')
        user = parsed.get('user', 'unknown')
        computer = parsed.get('computer', 'unknown')

        return f"Windows Event {event_id}: {event_desc} - User: {user}, Computer: {computer}"
