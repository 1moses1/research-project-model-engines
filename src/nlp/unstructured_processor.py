#!/usr/bin/env python3
"""
Unstructured Input Processor - NLP Engine
Converts ANY unstructured security data into structured format for XGBoost + RAG
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import pandas as pd
import numpy as np

# NLP libraries
import spacy
from collections import Counter

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnstructuredSecurityProcessor:
    """
    Process unstructured security inputs and convert to structured format
    Handles: raw logs, alerts, reports, emails, threat intel, any text
    """

    def __init__(self, ncsa_standards_path: str = "data/rwanda_ncsa"):
        """Initialize with Rwanda NCSA standards for RAG"""
        self.ncsa_path = Path(ncsa_standards_path)

        # Load spaCy model for NLP
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("Downloading spaCy model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")

        # Load NCSA standards for RAG
        self.ncsa_standards = self._load_ncsa_standards()

        # Security keyword dictionaries
        self.security_indicators = self._build_security_indicators()

        # Pattern extractors
        self.patterns = self._compile_patterns()

    def _load_ncsa_standards(self) -> Dict:
        """Load Rwanda NCSA minimum cybersecurity standards"""
        standards = {}

        try:
            # Load all NCSA documents
            for file_path in self.ncsa_path.glob("*.txt"):
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    standards[file_path.stem] = content

            logger.info(f"Loaded {len(standards)} NCSA standard documents")

        except Exception as e:
            logger.warning(f"Could not load NCSA standards: {e}")
            # Create fallback standards
            standards = self._create_fallback_standards()

        return standards

    def _create_fallback_standards(self) -> Dict:
        """Create fallback NCSA standards structure"""
        return {
            'access_control': 'Access control policies and procedures',
            'incident_response': 'Incident detection, response and recovery',
            'data_protection': 'Data encryption, backup and privacy',
            'network_security': 'Network monitoring, segmentation and protection',
            'audit_logging': 'Security event logging and monitoring'
        }

    def _build_security_indicators(self) -> Dict[str, List[str]]:
        """Build comprehensive security indicator dictionaries"""
        return {
            'attack_keywords': [
                'unauthorized', 'denied', 'blocked', 'failed', 'suspicious',
                'malicious', 'exploit', 'intrusion', 'breach', 'compromise',
                'vulnerability', 'threat', 'attack', 'malware', 'ransomware',
                'phishing', 'injection', 'overflow', 'escalation', 'backdoor',
                'trojan', 'worm', 'virus', 'rootkit', 'botnet', 'ddos',
                'brute force', 'zero-day', 'apt', 'lateral movement'
            ],
            'compliant_keywords': [
                'successful', 'completed', 'authorized', 'verified', 'validated',
                'approved', 'allowed', 'granted', 'authenticated', 'encrypted',
                'secured', 'compliant', 'passed', 'accepted', 'normal'
            ],
            'severity_high': [
                'critical', 'emergency', 'severe', 'catastrophic', 'breach',
                'compromise', 'ransomware', 'data exfiltration', 'zero-day'
            ],
            'severity_medium': [
                'warning', 'suspicious', 'unusual', 'unexpected', 'anomalous',
                'potential', 'possible', 'attempted'
            ],
            'severity_low': [
                'info', 'informational', 'notice', 'debug', 'verbose'
            ],
            'mitre_tactics': [
                'reconnaissance', 'resource development', 'initial access',
                'execution', 'persistence', 'privilege escalation',
                'defense evasion', 'credential access', 'discovery',
                'lateral movement', 'collection', 'command and control',
                'exfiltration', 'impact'
            ]
        }

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for entity extraction"""
        return {
            'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
            'ipv6': re.compile(r'\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b'),
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'url': re.compile(r'https?://[^\s]+'),
            'domain': re.compile(r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b'),
            'cve': re.compile(r'CVE-\d{4}-\d{4,7}'),
            'md5': re.compile(r'\b[a-f0-9]{32}\b'),
            'sha1': re.compile(r'\b[a-f0-9]{40}\b'),
            'sha256': re.compile(r'\b[a-f0-9]{64}\b'),
            'port': re.compile(r'\b(?:port|PORT)\s*:?\s*(\d{1,5})\b'),
            'user_id': re.compile(r'\b(?:user|username|userid|uid)\s*:?\s*([a-zA-Z0-9_-]+)\b', re.IGNORECASE),
            'process': re.compile(r'\b(?:process|proc)\s*:?\s*([a-zA-Z0-9_.-]+)\b', re.IGNORECASE),
            'file_path': re.compile(r'(?:/[a-zA-Z0-9_.-]+)+|(?:[A-Z]:\\[a-zA-Z0-9_.-\\]+)'),
            'timestamp': re.compile(r'\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}'),
        }

    def process(self, raw_input: str, source_type: str = 'unknown') -> Dict[str, Any]:
        """
        Main processing function - converts unstructured text to structured format

        Args:
            raw_input: Any unstructured security text (log, alert, report, etc.)
            source_type: Type of source (log, alert, email, report, threat_intel)

        Returns:
            Structured dictionary ready for XGBoost + RAG
        """
        logger.info(f"Processing {source_type} input ({len(raw_input)} chars)...")

        # Extract entities
        entities = self._extract_entities(raw_input)

        # Analyze sentiment and intent
        sentiment = self._analyze_sentiment(raw_input)

        # Classify compliance status
        compliance = self._classify_compliance(raw_input, entities)

        # Map to MITRE ATT&CK
        mitre_mapping = self._map_to_mitre(raw_input)

        # Map to NCSA standards
        ncsa_mapping = self._map_to_ncsa(raw_input)

        # Extract temporal features
        temporal = self._extract_temporal_features(raw_input)

        # Determine control family
        control_info = self._determine_control(entities, sentiment, mitre_mapping)

        # Build structured output
        structured = {
            # Original data
            'raw_text': raw_input,
            'source_type': source_type,
            'processed_timestamp': datetime.now().isoformat(),

            # Entities
            'entities': entities,

            # Classification
            'compliance_status': compliance['status'],
            'confidence_score': compliance['confidence'],
            'severity': compliance['severity'],

            # Mappings
            'control_id': control_info['control_id'],
            'control_family': control_info['control_family'],
            'framework': control_info['framework'],
            'mitre_tactics': mitre_mapping['tactics'],
            'mitre_techniques': mitre_mapping['techniques'],
            'ncsa_standards': ncsa_mapping['standards'],

            # Features for XGBoost
            'log_message': self._clean_for_model(raw_input),
            'hour_of_day': temporal['hour'],
            'day_of_week': temporal['day_of_week'],
            'is_business_hours': temporal['is_business_hours'],
            'port': entities.get('ports', [0])[0] if entities.get('ports') else 0,

            # Metadata
            'metadata': {
                'entity_count': sum(len(v) if isinstance(v, list) else 1 for v in entities.values()),
                'text_length': len(raw_input),
                'sentiment_score': sentiment['score'],
                'security_keywords': sentiment['security_keywords']
            }
        }

        logger.info(f"  ✓ Structured: {compliance['status']} ({compliance['confidence']:.1%} confidence)")

        return structured

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract security-relevant entities using regex and NLP"""
        entities = {}

        # Regex-based extraction
        for entity_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                entities[entity_type] = list(set(matches))  # Deduplicate

        # spaCy NER
        doc = self.nlp(text[:100000])  # Limit text length
        spacy_entities = {}

        for ent in doc.ents:
            if ent.label_ not in spacy_entities:
                spacy_entities[ent.label_] = []
            spacy_entities[ent.label_].append(ent.text)

        entities['named_entities'] = spacy_entities

        return entities

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze security sentiment (attack vs normal)"""
        text_lower = text.lower()

        # Count security indicators
        attack_count = sum(1 for keyword in self.security_indicators['attack_keywords']
                          if keyword in text_lower)
        compliant_count = sum(1 for keyword in self.security_indicators['compliant_keywords']
                             if keyword in text_lower)

        # Security sentiment score (-1 = attack, +1 = normal)
        if attack_count + compliant_count == 0:
            score = 0
        else:
            score = (compliant_count - attack_count) / (attack_count + compliant_count)

        # Extract matched keywords
        matched_keywords = []
        for keyword in self.security_indicators['attack_keywords']:
            if keyword in text_lower:
                matched_keywords.append(keyword)

        return {
            'score': score,
            'attack_indicators': attack_count,
            'compliant_indicators': compliant_count,
            'security_keywords': matched_keywords[:10]  # Top 10
        }

    def _classify_compliance(self, text: str, entities: Dict) -> Dict[str, Any]:
        """Classify compliance status and severity"""
        sentiment = self._analyze_sentiment(text)
        text_lower = text.lower()

        # Determine compliance status
        if sentiment['score'] < -0.3:
            status = 'non_compliant'
            confidence = min(0.95, 0.7 + abs(sentiment['score']) * 0.3)
        elif sentiment['score'] > 0.3:
            status = 'compliant'
            confidence = min(0.95, 0.7 + sentiment['score'] * 0.3)
        else:
            # Ambiguous - use additional heuristics
            if any(keyword in text_lower for keyword in ['denied', 'blocked', 'failed']):
                status = 'non_compliant'
                confidence = 0.65
            else:
                status = 'compliant'
                confidence = 0.60

        # Determine severity
        severity = 'low'
        for keyword in self.security_indicators['severity_high']:
            if keyword in text_lower:
                severity = 'critical'
                break

        if severity != 'critical':
            for keyword in self.security_indicators['severity_medium']:
                if keyword in text_lower:
                    severity = 'medium'
                    break

        return {
            'status': status,
            'confidence': confidence,
            'severity': severity
        }

    def _map_to_mitre(self, text: str) -> Dict[str, List[str]]:
        """Map text to MITRE ATT&CK tactics and techniques"""
        text_lower = text.lower()

        # Identify tactics
        tactics = []
        for tactic in self.security_indicators['mitre_tactics']:
            if tactic.lower() in text_lower:
                tactics.append(tactic)

        # Heuristic technique mapping
        techniques = []

        if 'scan' in text_lower or 'reconnaissance' in text_lower:
            techniques.append('T1046')  # Network Service Scanning

        if 'phishing' in text_lower or 'email' in text_lower:
            techniques.append('T1566')  # Phishing

        if 'brute' in text_lower or 'password' in text_lower:
            techniques.append('T1110')  # Brute Force

        if 'lateral' in text_lower or 'movement' in text_lower:
            techniques.append('T1021')  # Remote Services

        if 'exfiltration' in text_lower or 'data transfer' in text_lower:
            techniques.append('T1041')  # Exfiltration Over C2

        return {
            'tactics': tactics if tactics else ['unknown'],
            'techniques': techniques if techniques else []
        }

    def _map_to_ncsa(self, text: str) -> Dict[str, List[str]]:
        """Map to Rwanda NCSA minimum cybersecurity standards"""
        text_lower = text.lower()
        matched_standards = []

        # Match against NCSA standards
        for standard_name, standard_content in self.ncsa_standards.items():
            # Simple keyword matching (can be enhanced with embeddings)
            standard_keywords = standard_content.lower().split()[:50]
            text_words = text_lower.split()

            overlap = len(set(standard_keywords) & set(text_words))
            if overlap > 3:  # Threshold for relevance
                matched_standards.append(standard_name)

        # Fallback heuristics
        if not matched_standards:
            if any(word in text_lower for word in ['access', 'login', 'authentication']):
                matched_standards.append('access_control')
            elif any(word in text_lower for word in ['incident', 'alert', 'breach']):
                matched_standards.append('incident_response')
            elif any(word in text_lower for word in ['encryption', 'data', 'privacy']):
                matched_standards.append('data_protection')

        return {
            'standards': matched_standards if matched_standards else ['general']
        }

    def _extract_temporal_features(self, text: str) -> Dict[str, int]:
        """Extract temporal features from text or use current time"""
        # Try to find timestamp in text
        timestamp_match = self.patterns['timestamp'].search(text)

        if timestamp_match:
            try:
                dt = datetime.fromisoformat(timestamp_match.group())
            except:
                dt = datetime.now()
        else:
            dt = datetime.now()

        return {
            'hour': dt.hour,
            'day_of_week': dt.weekday(),
            'is_business_hours': 1 if 8 <= dt.hour <= 17 and dt.weekday() < 5 else 0
        }

    def _determine_control(self, entities: Dict, sentiment: Dict, mitre: Dict) -> Dict[str, str]:
        """Determine NIST control based on entities and context"""

        # Default
        control_id = 'SI-4'  # System Monitoring
        control_family = 'System and Information Integrity'
        framework = 'NIST-800-53'

        # Heuristic mapping
        if entities.get('user_id'):
            control_id = 'AC-3'
            control_family = 'Access Control'
        elif entities.get('email'):
            control_id = 'SI-8'
            control_family = 'System and Information Integrity'
        elif entities.get('file_path'):
            control_id = 'AU-6'
            control_family = 'Audit and Accountability'
        elif 'credential access' in mitre.get('tactics', []):
            control_id = 'IA-2'
            control_family = 'Identification and Authentication'

        return {
            'control_id': control_id,
            'control_family': control_family,
            'framework': framework
        }

    def _clean_for_model(self, text: str) -> str:
        """Clean text for XGBoost model"""
        # Remove extra whitespace
        text = ' '.join(text.split())

        # Truncate if too long
        if len(text) > 1000:
            text = text[:1000]

        return text

    def process_batch(self, inputs: List[str], source_types: Optional[List[str]] = None) -> pd.DataFrame:
        """Process multiple unstructured inputs into DataFrame for XGBoost"""

        if source_types is None:
            source_types = ['unknown'] * len(inputs)

        results = []
        for text, source_type in zip(inputs, source_types):
            try:
                structured = self.process(text, source_type)
                results.append(structured)
            except Exception as e:
                logger.error(f"Error processing input: {e}")

        # Convert to DataFrame
        df = pd.DataFrame(results)

        logger.info(f"Processed {len(results)} inputs into structured DataFrame")

        return df


def main():
    """Test the unstructured processor"""
    processor = UnstructuredSecurityProcessor()

    # Test cases
    test_inputs = [
        "2025-01-15T14:30:45 - Unauthorized access attempt from IP 192.168.1.100 to database server - Connection denied by firewall",
        "User john.doe@company.com successfully logged in via VPN from 10.0.0.50 at 2025-01-15 09:00:00",
        "CRITICAL: Ransomware detected on host WORKSTATION-042 - File encryption in progress - Process: evil.exe (SHA256: abc123...)",
        "Phishing email blocked - Sender: attacker@malicious.com - Subject: 'Urgent: Update your password' - Malware attachment detected",
        "System backup completed successfully - 500GB transferred to S3 bucket backup-prod-2025 - Encryption verified"
    ]

    print("\n" + "="*100)
    print("UNSTRUCTURED INPUT PROCESSING TEST")
    print("="*100 + "\n")

    for i, input_text in enumerate(test_inputs, 1):
        print(f"\nTest {i}:")
        print(f"Input: {input_text[:80]}...")

        result = processor.process(input_text)

        print(f"  Status: {result['compliance_status'].upper()}")
        print(f"  Confidence: {result['confidence_score']:.1%}")
        print(f"  Severity: {result['severity']}")
        print(f"  Control: {result['control_id']} ({result['control_family']})")
        print(f"  MITRE Tactics: {', '.join(result['mitre_tactics'])}")
        print(f"  Entities: {len(result['metadata']['entity_count'])} extracted")


if __name__ == '__main__':
    main()
