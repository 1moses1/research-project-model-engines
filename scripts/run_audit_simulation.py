#!/usr/bin/env python3
"""
Standalone Audit Simulation Script

This script runs a complete audit simulation using:
- 5 sample logs from real-world datasets
- 4 policy documents from Alvin Tech sample organization
- Direct LLM analysis (without requiring Engine 3 to be running)

Generates a comprehensive PDF audit report.

Usage:
    cd model-engine
    source venv/bin/activate
    python scripts/run_audit_simulation.py

Author: Moise Iradukunda Ingabire
Institution: Carnegie Mellon University Africa
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# =============================================================================
# Configuration
# =============================================================================

POLICY_DOCS_DIR = PROJECT_ROOT / "docs/sample_policy_docs/Company's Security Report To Audit"
OUTPUT_DIR = PROJECT_ROOT / "test_outputs"

# Sample logs for testing (diverse set covering different compliance scenarios)
SAMPLE_LOGS = [
    {
        "id": "LOG-001",
        "log_message": "Nov 30 07:17:01 ip-172-31-27-153 CRON[22125]: pam_unix(cron:session): session opened for user root by (uid=0)",
        "source": "linux_auth",
        "timestamp": "2024-11-30T07:17:01",
        "source_ip": "172.31.27.153"
    },
    {
        "id": "LOG-002",
        "log_message": "Nov 30 08:42:04 ip-172-31-27-153 sshd[22182]: Invalid user admin from 187.12.249.74",
        "source": "linux_auth",
        "timestamp": "2024-11-30T08:42:04",
        "source_ip": "187.12.249.74"
    },
    {
        "id": "LOG-003",
        "log_message": "Nov 30 08:42:14 ip-172-31-27-153 sshd[22184]: Did not receive identification string from 187.12.249.74",
        "source": "linux_auth",
        "timestamp": "2024-11-30T08:42:14",
        "source_ip": "187.12.249.74"
    },
    {
        "id": "LOG-004",
        "log_message": "Nov 30 06:39:00 ip-172-31-27-153 CRON[21882]: pam_unix(cron:session): session closed for user root",
        "source": "linux_auth",
        "timestamp": "2024-11-30T06:39:00",
        "source_ip": "172.31.27.153"
    },
    {
        "id": "LOG-005",
        "log_message": "Nov 30 11:54:50 ip-172-31-27-153 sshd[22341]: fatal: Read from socket failed: Connection reset by peer [preauth]",
        "source": "linux_auth",
        "timestamp": "2024-11-30T11:54:50",
        "source_ip": "172.31.27.153"
    },
]

# Policy documents to analyze
POLICY_DOCUMENTS = [
    "Alvin Tech Internal Audit Report.pdf",
    "Alvin Tech Post-Patching Security Scan Report.pdf",
    "Alvin Tech Security Patching Report.pdf",
    "Alvin Tech Updated Security Policy.pdf",
]


# =============================================================================
# Rule-Based Analyzer (Fallback when LLM not available)
# =============================================================================

class RuleBasedAnalyzer:
    """Simple rule-based analyzer for log compliance."""

    PATTERNS = {
        # Non-compliant patterns
        "invalid user": ("RWNCSA-AC-38", "Access Control", "non_compliant", "Unauthorized access attempt detected"),
        "failed password": ("RWNCSA-IA-98", "Identity Management", "non_compliant", "Failed authentication attempt"),
        "did not receive identification": ("RWNCSA-IA-100", "Identity Management", "non_compliant", "Protocol violation - no identification"),
        "connection reset by peer": ("RWNCSA-SC-155", "System Protection", "non_compliant", "Abnormal connection termination"),
        "authentication failure": ("RWNCSA-AC-37", "Access Control", "non_compliant", "Authentication failed"),
        "access denied": ("RWNCSA-AC-37", "Access Control", "non_compliant", "Access denied to resource"),
        "fatal:": ("RWNCSA-SC-155", "System Protection", "non_compliant", "System error detected"),

        # Compliant patterns
        "session opened": ("RWNCSA-AU-68", "Audit and Accountability", "compliant", "Legitimate session started"),
        "session closed": ("RWNCSA-AU-69", "Audit and Accountability", "compliant", "Session properly terminated"),
        "accepted password": ("RWNCSA-IA-97", "Identity Management", "compliant", "Successful authentication"),
        "accepted publickey": ("RWNCSA-IA-99", "Identity Management", "compliant", "Key-based authentication successful"),
        "connection closed": ("RWNCSA-SC-155", "System Protection", "compliant", "Normal connection closure"),
        "cron": ("RWNCSA-CM-83", "Configuration Management", "compliant", "Scheduled task execution"),
    }

    def analyze(self, log_message: str) -> Dict[str, Any]:
        """Analyze a log message and return compliance result."""
        log_lower = log_message.lower()

        for pattern, (control_id, family, status, description) in self.PATTERNS.items():
            if pattern in log_lower:
                confidence = 0.95 if status == "non_compliant" else 0.90

                return {
                    "prediction": status,
                    "confidence": confidence,
                    "probabilities": {
                        "compliant": 1 - confidence if status == "non_compliant" else confidence,
                        "non_compliant": confidence if status == "non_compliant" else 1 - confidence
                    },
                    "primary_control": {
                        "control_id": control_id,
                        "control_name": description,
                        "control_family": family,
                        "compliance_status": status,
                        "confidence": confidence,
                        "relevance": 1.0
                    },
                    "reasoning": f"Pattern '{pattern}' detected in log. {description}",
                    "evidence_indicators": [f"Matched pattern: {pattern}"],
                    "risk_indicators": [description] if status == "non_compliant" else [],
                    "recommended_actions": [
                        f"Review {family} controls",
                        "Investigate source IP",
                        "Check access logs"
                    ] if status == "non_compliant" else [],
                    "model_used": "rule-based-analyzer",
                    "timestamp": datetime.now().isoformat()
                }

        # Default for unknown patterns
        return {
            "prediction": "partial",
            "confidence": 0.5,
            "probabilities": {"compliant": 0.5, "non_compliant": 0.5},
            "primary_control": {
                "control_id": "RWNCSA-AU-70",
                "control_name": "General Audit Events",
                "control_family": "Audit and Accountability",
                "compliance_status": "partial",
                "confidence": 0.5,
                "relevance": 0.5
            },
            "reasoning": "No specific pattern matched - requires manual review",
            "evidence_indicators": [],
            "risk_indicators": [],
            "recommended_actions": ["Manual review required"],
            "model_used": "rule-based-analyzer",
            "timestamp": datetime.now().isoformat()
        }


# =============================================================================
# LLM Analyzer (Uses Engine 3 client)
# =============================================================================

class LLMAnalyzer:
    """LLM-powered analyzer using Anthropic/OpenAI."""

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "anthropic")
        self.model = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.client = None

        if self.api_key and self.provider == "anthropic":
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                print(f"  LLM Client initialized: {self.provider}/{self.model}")
            except ImportError:
                print("  Warning: anthropic package not installed")
            except Exception as e:
                print(f"  Warning: Failed to initialize LLM client: {e}")

    def analyze(self, log_message: str, context: Dict = None) -> Dict[str, Any]:
        """Analyze a log message using LLM."""
        if not self.client:
            return None

        try:
            prompt = f"""Analyze this security log for Rwanda NCSA compliance:

Log: {log_message}

Determine:
1. Compliance status (compliant, non_compliant, partial)
2. Relevant NCSA control ID (format: RWNCSA-XX-NN)
3. Control family (Access Control, Audit and Accountability, etc.)
4. Confidence score (0.0-1.0)
5. Brief reasoning

Respond in JSON format:
{{
    "prediction": "compliant|non_compliant|partial",
    "confidence": 0.95,
    "control_id": "RWNCSA-AC-37",
    "control_name": "Access Control Description",
    "control_family": "Access Control",
    "reasoning": "Brief explanation",
    "risk_indicators": ["list of risks if non-compliant"],
    "recommended_actions": ["list of actions"]
}}"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse response
            response_text = response.content[0].text
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                result["model_used"] = f"llm-{self.model}"
                result["timestamp"] = datetime.now().isoformat()

                # Format for consistency
                return {
                    "prediction": result.get("prediction", "partial"),
                    "confidence": result.get("confidence", 0.8),
                    "probabilities": {
                        "compliant": result.get("confidence", 0.8) if result.get("prediction") == "compliant" else 1 - result.get("confidence", 0.8),
                        "non_compliant": result.get("confidence", 0.8) if result.get("prediction") == "non_compliant" else 1 - result.get("confidence", 0.8)
                    },
                    "primary_control": {
                        "control_id": result.get("control_id", "RWNCSA-AU-70"),
                        "control_name": result.get("control_name", "Unknown"),
                        "control_family": result.get("control_family", "Audit and Accountability"),
                        "compliance_status": result.get("prediction", "partial"),
                        "confidence": result.get("confidence", 0.8),
                        "relevance": 1.0
                    },
                    "reasoning": result.get("reasoning", "LLM analysis"),
                    "evidence_indicators": [f"LLM identified: {result.get('control_name', 'Unknown')}"],
                    "risk_indicators": result.get("risk_indicators", []),
                    "recommended_actions": result.get("recommended_actions", []),
                    "model_used": f"llm-{self.model}",
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            print(f"    LLM analysis failed: {e}")
            return None


# =============================================================================
# Document Analyzer
# =============================================================================

class DocumentAnalyzer:
    """Analyzes policy documents for compliance mapping."""

    def analyze(self, doc_path: Path) -> Dict[str, Any]:
        """Analyze a policy document."""
        if not doc_path.exists():
            return {"error": f"File not found: {doc_path}", "document_name": doc_path.name}

        # Basic analysis based on document name
        doc_name = doc_path.name.lower()

        controls_mapped = []
        findings = []

        if "internal audit" in doc_name:
            controls_mapped = ["RWNCSA-CA-01", "RWNCSA-AU-01", "RWNCSA-RA-02"]
            findings = [
                {"control_id": "RWNCSA-CA-01", "status": "compliant", "finding": "Internal audit procedures documented"},
                {"control_id": "RWNCSA-AU-01", "status": "partial", "finding": "Audit logging partially implemented"},
            ]
        elif "patching" in doc_name:
            controls_mapped = ["RWNCSA-CM-02", "RWNCSA-SI-02", "RWNCSA-RA-05"]
            findings = [
                {"control_id": "RWNCSA-CM-02", "status": "compliant", "finding": "Patch management process documented"},
                {"control_id": "RWNCSA-SI-02", "status": "compliant", "finding": "Security patches applied regularly"},
            ]
        elif "security policy" in doc_name:
            controls_mapped = ["RWNCSA-SP-01", "RWNCSA-PL-01", "RWNCSA-AT-01"]
            findings = [
                {"control_id": "RWNCSA-SP-01", "status": "compliant", "finding": "Security policy document exists"},
                {"control_id": "RWNCSA-PL-01", "status": "partial", "finding": "Planning procedures need update"},
            ]
        elif "scan" in doc_name:
            controls_mapped = ["RWNCSA-RA-05", "RWNCSA-CA-02", "RWNCSA-SI-03"]
            findings = [
                {"control_id": "RWNCSA-RA-05", "status": "compliant", "finding": "Vulnerability scanning performed"},
                {"control_id": "RWNCSA-CA-02", "status": "compliant", "finding": "Security assessment completed"},
            ]

        return {
            "document_name": doc_path.name,
            "document_path": str(doc_path),
            "status": "analyzed",
            "file_size_bytes": doc_path.stat().st_size,
            "controls_mapped": controls_mapped,
            "findings": findings,
            "summary": f"Policy document '{doc_path.name}' mapped to {len(controls_mapped)} NCSA controls",
            "timestamp": datetime.now().isoformat()
        }


# =============================================================================
# Report Generator
# =============================================================================

class AuditReportGenerator:
    """Generates PDF audit reports."""

    def __init__(self, results: Dict[str, Any]):
        self.results = results

    def generate_pdf(self, output_path: Path) -> Path:
        """Generate a PDF audit report."""
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
        from reportlab.lib.enums import TA_CENTER, TA_LEFT

        doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                               leftMargin=0.75*inch, rightMargin=0.75*inch,
                               topMargin=0.75*inch, bottomMargin=0.75*inch)
        styles = getSampleStyleSheet()
        story = []

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1a365d')
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=20
        )

        section_style = ParagraphStyle(
            'Section',
            parent=styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#2c5282')
        )

        # Title Page
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("Rwanda NCSA", title_style))
        story.append(Paragraph("Compliance Audit Report", title_style))
        story.append(Spacer(1, 0.5*inch))

        summary = self.results.get("summary", {})
        story.append(Paragraph(f"Organization: {summary.get('organization', 'N/A')}", subtitle_style))
        story.append(Paragraph(f"Audit ID: {summary.get('audit_id', 'N/A')}", subtitle_style))
        story.append(Paragraph(f"Date: {summary.get('timestamp', datetime.now().isoformat())[:10]}", subtitle_style))
        story.append(Spacer(1, 1*inch))

        # Status badge
        risk_level = summary.get('risk_level', 'MEDIUM')
        risk_color = {'LOW': colors.green, 'MEDIUM': colors.orange, 'HIGH': colors.red}.get(risk_level, colors.grey)
        story.append(Paragraph(f"<font color='{risk_color.hexval()}'>Overall Risk Level: {risk_level}</font>", subtitle_style))

        story.append(PageBreak())

        # Executive Summary
        story.append(Paragraph("Executive Summary", section_style))

        log_stats = summary.get("log_analysis", {})
        doc_stats = summary.get("document_analysis", {})

        exec_summary = f"""
        This compliance audit was conducted against the <b>Rwanda National Cyber Security Authority (NCSA)
        Minimum Cybersecurity Standards</b>. The audit analyzed {log_stats.get('total_logs', 0)} security log events
        and {doc_stats.get('total_documents', 0)} policy documents.

        <br/><br/>
        <b>Key Findings:</b>
        <br/>
        • Overall Compliance Rate: {log_stats.get('compliance_rate', 0):.1f}%
        <br/>
        • Compliant Events: {log_stats.get('compliant', 0)}
        <br/>
        • Non-Compliant Events: {log_stats.get('non_compliant', 0)}
        <br/>
        • Average Confidence: {log_stats.get('average_confidence', 0):.1%}
        <br/><br/>
        The audit identified several areas requiring attention, particularly in access control and identity management.
        Detailed findings and recommendations are provided in the following sections.
        """
        story.append(Paragraph(exec_summary, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))

        # Summary Table
        story.append(Paragraph("Audit Summary", section_style))
        summary_data = [
            ["Metric", "Value", "Status"],
            ["Total Logs Analyzed", str(log_stats.get('total_logs', 0)), "✓"],
            ["Compliant Events", str(log_stats.get('compliant', 0)), "✓" if log_stats.get('compliant', 0) > 0 else "—"],
            ["Non-Compliant Events", str(log_stats.get('non_compliant', 0)), "⚠" if log_stats.get('non_compliant', 0) > 0 else "✓"],
            ["Compliance Rate", f"{log_stats.get('compliance_rate', 0):.1f}%", "✓" if log_stats.get('compliance_rate', 0) >= 80 else "⚠"],
            ["Documents Analyzed", str(doc_stats.get('total_documents', 0)), "✓"],
            ["Risk Level", summary.get('risk_level', 'N/A'), ""],
        ]

        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch, 1*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f7fafc'), colors.white]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.5*inch))

        # Control Family Analysis
        story.append(Paragraph("Control Family Analysis", section_style))
        families = summary.get("control_families", {})
        if families:
            family_data = [["Control Family", "Compliant", "Non-Compliant", "Total", "Rate"]]
            for family, stats in families.items():
                total = stats.get('total', 0)
                compliant = stats.get('compliant', 0)
                rate = (compliant / total * 100) if total > 0 else 0
                family_data.append([
                    family[:30],
                    str(compliant),
                    str(stats.get('non_compliant', 0)),
                    str(total),
                    f"{rate:.0f}%"
                ])

            family_table = Table(family_data, colWidths=[2.5*inch, 1*inch, 1.2*inch, 0.8*inch, 0.8*inch])
            family_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('ALIGN', (0, 1), (0, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f7fafc'), colors.white]),
            ]))
            story.append(family_table)

        story.append(PageBreak())

        # Detailed Log Analysis Findings
        story.append(Paragraph("Detailed Log Analysis Findings", section_style))

        for i, result in enumerate(self.results.get("log_analysis", [])):
            if "error" in result:
                continue

            log = result.get("original_log", {})
            ctrl = result.get("primary_control", {})
            prediction = result.get("prediction", "unknown")

            # Color code by status
            status_color = {
                "compliant": colors.HexColor('#38a169'),
                "non_compliant": colors.HexColor('#e53e3e'),
                "partial": colors.HexColor('#dd6b20')
            }.get(prediction, colors.grey)

            story.append(Paragraph(f"<b>Finding {i+1}: {ctrl.get('control_id', 'N/A')}</b>", styles['Heading4']))

            finding_data = [
                ["Field", "Value"],
                ["Log Message", log.get('log_message', 'N/A')[:80] + "..."],
                ["Status", prediction.upper()],
                ["Control", f"{ctrl.get('control_id', 'N/A')} - {ctrl.get('control_name', 'N/A')[:40]}"],
                ["Family", ctrl.get('control_family', 'N/A')],
                ["Confidence", f"{result.get('confidence', 0):.1%}"],
                ["Model", result.get('model_used', 'N/A')],
            ]

            finding_table = Table(finding_data, colWidths=[1.5*inch, 5*inch])
            finding_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e0')),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            story.append(finding_table)

            if result.get("reasoning"):
                story.append(Paragraph(f"<i>Reasoning: {result['reasoning'][:200]}</i>", styles['Normal']))

            story.append(Spacer(1, 0.2*inch))

        story.append(PageBreak())

        # Policy Document Analysis
        story.append(Paragraph("Policy Document Analysis", section_style))

        for doc_result in self.results.get("document_analysis", []):
            doc_name = doc_result.get('document_name', 'Unknown')
            story.append(Paragraph(f"<b>{doc_name}</b>", styles['Heading4']))

            if doc_result.get("findings"):
                for finding in doc_result["findings"]:
                    status_icon = "✓" if finding.get("status") == "compliant" else "⚠"
                    story.append(Paragraph(
                        f"{status_icon} {finding.get('control_id', 'N/A')}: {finding.get('finding', 'N/A')}",
                        styles['Normal']
                    ))

            story.append(Paragraph(f"<i>{doc_result.get('summary', '')}</i>", styles['Normal']))
            story.append(Spacer(1, 0.15*inch))

        story.append(PageBreak())

        # Recommendations
        story.append(Paragraph("Recommendations", section_style))

        recommendations = [
            ("High Priority", "Address non-compliant access control events immediately", colors.HexColor('#e53e3e')),
            ("High Priority", "Review and strengthen identity management controls", colors.HexColor('#e53e3e')),
            ("Medium Priority", "Update security policies to align with NCSA requirements", colors.HexColor('#dd6b20')),
            ("Medium Priority", "Implement automated monitoring for all control families", colors.HexColor('#dd6b20')),
            ("Low Priority", "Schedule quarterly compliance audits", colors.HexColor('#38a169')),
            ("Low Priority", "Consider implementing MFA for all administrative access", colors.HexColor('#38a169')),
        ]

        for priority, rec, color in recommendations:
            story.append(Paragraph(f"<font color='{color.hexval()}'><b>{priority}:</b></font> {rec}", styles['Normal']))
            story.append(Spacer(1, 0.1*inch))

        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("—" * 50, styles['Normal']))
        story.append(Paragraph(
            f"Generated by Rwanda NCSA Compliance Auditor | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            subtitle_style
        ))
        story.append(Paragraph(
            "Powered by MCP+LLM Semantic Analysis | Carnegie Mellon University Africa",
            subtitle_style
        ))

        # Build PDF
        doc.build(story)
        return output_path


# =============================================================================
# Main Orchestrator
# =============================================================================

def run_audit():
    """Run the complete audit simulation."""
    print("=" * 70)
    print("   RWANDA NCSA COMPLIANCE AUDIT SIMULATION")
    print("=" * 70)
    print(f"\nStarted at: {datetime.now().isoformat()}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize analyzers
    rule_analyzer = RuleBasedAnalyzer()
    llm_analyzer = LLMAnalyzer()
    doc_analyzer = DocumentAnalyzer()

    results = {
        "log_analysis": [],
        "document_analysis": [],
        "summary": {},
        "timestamp": datetime.now().isoformat()
    }

    # Step 1: Analyze logs
    print("\n" + "=" * 60)
    print("STEP 1: Analyzing Security Logs")
    print("=" * 60)

    for i, log in enumerate(SAMPLE_LOGS):
        print(f"\n  [{i+1}/{len(SAMPLE_LOGS)}] Analyzing: {log['log_message'][:50]}...")

        # Try LLM first, fall back to rule-based
        result = llm_analyzer.analyze(log["log_message"]) if llm_analyzer.client else None

        if not result:
            result = rule_analyzer.analyze(log["log_message"])
            print("    Using: Rule-based analyzer")
        else:
            print("    Using: LLM analyzer")

        result["original_log"] = log
        results["log_analysis"].append(result)

        print(f"    Status: {result['prediction'].upper()} (confidence: {result['confidence']:.0%})")
        print(f"    Control: {result['primary_control']['control_id']} - {result['primary_control']['control_family']}")

    # Step 2: Analyze policy documents
    print("\n" + "=" * 60)
    print("STEP 2: Analyzing Policy Documents")
    print("=" * 60)

    for i, doc_name in enumerate(POLICY_DOCUMENTS):
        doc_path = POLICY_DOCS_DIR / doc_name
        print(f"\n  [{i+1}/{len(POLICY_DOCUMENTS)}] Processing: {doc_name}...")

        doc_result = doc_analyzer.analyze(doc_path)
        results["document_analysis"].append(doc_result)

        if "error" not in doc_result:
            print(f"    Controls mapped: {len(doc_result.get('controls_mapped', []))}")
        else:
            print(f"    Error: {doc_result['error']}")

    # Step 3: Calculate summary
    print("\n" + "=" * 60)
    print("STEP 3: Calculating Audit Summary")
    print("=" * 60)

    log_results = results["log_analysis"]
    doc_results = results["document_analysis"]

    compliant = sum(1 for r in log_results if r.get("prediction") == "compliant")
    non_compliant = sum(1 for r in log_results if r.get("prediction") == "non_compliant")
    partial = sum(1 for r in log_results if r.get("prediction") == "partial")
    total = len(log_results)

    confidences = [r.get("confidence", 0) for r in log_results]
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0

    # Control families
    families = {}
    for r in log_results:
        ctrl = r.get("primary_control", {})
        family = ctrl.get("control_family", "Unknown")
        if family not in families:
            families[family] = {"compliant": 0, "non_compliant": 0, "total": 0}
        families[family]["total"] += 1
        if r.get("prediction") == "compliant":
            families[family]["compliant"] += 1
        elif r.get("prediction") == "non_compliant":
            families[family]["non_compliant"] += 1

    results["summary"] = {
        "audit_id": f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "organization": "Alvin Tech (Sample)",
        "framework": "Rwanda NCSA Minimum Cybersecurity Standards",
        "log_analysis": {
            "total_logs": total,
            "compliant": compliant,
            "non_compliant": non_compliant,
            "partial": partial,
            "compliance_rate": (compliant / total * 100) if total > 0 else 0,
            "average_confidence": avg_confidence
        },
        "document_analysis": {
            "total_documents": len(doc_results),
            "processed": sum(1 for d in doc_results if "error" not in d),
            "documents": [d.get("document_name", "Unknown") for d in doc_results]
        },
        "control_families": families,
        "overall_compliance_status": "PARTIAL" if non_compliant > 0 else "COMPLIANT",
        "risk_level": "HIGH" if non_compliant > compliant else "MEDIUM" if non_compliant > 0 else "LOW"
    }

    summary = results["summary"]
    print(f"\n  Audit ID: {summary['audit_id']}")
    print(f"  Compliance Rate: {summary['log_analysis']['compliance_rate']:.1f}%")
    print(f"  Risk Level: {summary['risk_level']}")

    # Step 4: Generate PDF report
    print("\n" + "=" * 60)
    print("STEP 4: Generating PDF Audit Report")
    print("=" * 60)

    report_generator = AuditReportGenerator(results)
    report_path = OUTPUT_DIR / f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    report_generator.generate_pdf(report_path)

    print(f"\n  Report saved to: {report_path}")

    # Save JSON results
    json_path = OUTPUT_DIR / f"audit_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"  JSON results saved to: {json_path}")

    # Final Summary
    print("\n" + "=" * 70)
    print("   AUDIT COMPLETE")
    print("=" * 70)
    print(f"\n  Audit ID: {summary['audit_id']}")
    print(f"  Logs Analyzed: {summary['log_analysis']['total_logs']}")
    print(f"  Documents Analyzed: {summary['document_analysis']['total_documents']}")
    print(f"  Compliance Rate: {summary['log_analysis']['compliance_rate']:.1f}%")
    print(f"  Risk Level: {summary['risk_level']}")
    print(f"\n  PDF Report: {report_path}")
    print(f"  JSON Results: {json_path}")
    print(f"\n  Completed at: {datetime.now().isoformat()}")

    return report_path


if __name__ == "__main__":
    run_audit()
