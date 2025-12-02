"""
LLM Report Generator Service
Uses OpenAI GPT-4 to generate compliance report narratives
"""

from typing import Dict, List, Optional
import json
import random


class LLMReportGenerator:
    """Generates report content using LLM"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.enabled = bool(api_key)

        if self.enabled:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=api_key)
                print("✅ OpenAI client initialized for report generation")
            except ImportError:
                print("⚠️  OpenAI package not installed - using mock mode")
                self.enabled = False
                self.client = None
        else:
            print("⚠️  No API key provided - using mock mode")
            self.client = None

    def is_enabled(self) -> bool:
        """Check if LLM is enabled"""
        return self.enabled

    async def generate_executive_summary(
        self,
        compliance_data: Dict,
        include_recommendations: bool = True
    ) -> Dict:
        """
        Generate executive summary report

        Args:
            compliance_data: Compliance metrics and data
            include_recommendations: Include AI recommendations

        Returns:
            Dictionary with report sections
        """
        if self.enabled and self.client:
            return await self._generate_with_openai(
                compliance_data=compliance_data,
                report_type="executive",
                include_recommendations=include_recommendations
            )
        else:
            return self._generate_mock_executive(compliance_data, include_recommendations)

    async def generate_full_report(
        self,
        compliance_data: Dict,
        include_recommendations: bool = True
    ) -> Dict:
        """
        Generate full compliance report

        Args:
            compliance_data: Compliance metrics and data
            include_recommendations: Include AI recommendations

        Returns:
            Dictionary with report sections
        """
        if self.enabled and self.client:
            return await self._generate_with_openai(
                compliance_data=compliance_data,
                report_type="full",
                include_recommendations=include_recommendations
            )
        else:
            return self._generate_mock_full(compliance_data, include_recommendations)

    async def generate_gap_analysis(
        self,
        compliance_data: Dict
    ) -> Dict:
        """
        Generate compliance gap analysis report

        Args:
            compliance_data: Compliance metrics and data

        Returns:
            Dictionary with gap analysis sections
        """
        if self.enabled and self.client:
            return await self._generate_with_openai(
                compliance_data=compliance_data,
                report_type="gap_analysis",
                include_recommendations=True
            )
        else:
            return self._generate_mock_gap_analysis(compliance_data)

    async def _generate_with_openai(
        self,
        compliance_data: Dict,
        report_type: str,
        include_recommendations: bool
    ) -> Dict:
        """Generate report content using OpenAI GPT-4"""
        try:
            company_name = compliance_data.get('company_name', 'Unknown Company')
            framework = compliance_data.get('framework', 'Rwanda-NCSA')
            total_controls = compliance_data.get('total_controls', 0)
            compliant = compliance_data.get('compliant_controls', 0)
            non_compliant = compliance_data.get('non_compliant_controls', 0)

            compliance_rate = (compliant / total_controls * 100) if total_controls > 0 else 0

            # Build comprehensive prompt based on report type
            if report_type == "executive":
                prompt = self._build_executive_prompt(compliance_data, include_recommendations)
            elif report_type == "gap_analysis":
                prompt = self._build_gap_analysis_prompt(compliance_data)
            else:  # full report
                prompt = self._build_full_report_prompt(compliance_data, include_recommendations)

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity compliance expert specializing in Rwanda NCSA standards. Generate professional, detailed compliance reports."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.4,
                max_tokens=3000
            )

            content = response.choices[0].message.content

            # Parse the response into structured sections
            return self._parse_llm_response(content, report_type)

        except Exception as e:
            print(f"⚠️ OpenAI API error: {str(e)}")
            print("⚠️ Falling back to mock generation")

            if report_type == "executive":
                return self._generate_mock_executive(compliance_data, include_recommendations)
            elif report_type == "gap_analysis":
                return self._generate_mock_gap_analysis(compliance_data)
            else:
                return self._generate_mock_full(compliance_data, include_recommendations)

    def _build_executive_prompt(self, compliance_data: Dict, include_recommendations: bool) -> str:
        """Build prompt for executive summary"""
        company_name = compliance_data.get('company_name', 'Unknown Company')
        framework = compliance_data.get('framework', 'Rwanda-NCSA')
        total_controls = compliance_data.get('total_controls', 0)
        compliant = compliance_data.get('compliant_controls', 0)
        non_compliant = compliance_data.get('non_compliant_controls', 0)
        compliance_rate = (compliant / total_controls * 100) if total_controls > 0 else 0

        prompt = f"""Generate an executive summary compliance report for {company_name}.

Framework: {framework}
Total Controls: {total_controls}
Compliant: {compliant}
Non-Compliant: {non_compliant}
Compliance Rate: {compliance_rate:.1f}%

Generate a professional executive summary with the following sections:

1. EXECUTIVE SUMMARY (2-3 paragraphs)
   - Overall compliance status
   - Key findings
   - Critical areas of concern

2. COMPLIANCE OVERVIEW
   - Summary of compliance metrics
   - Trends and patterns

3. RISK ASSESSMENT
   - High-priority risks
   - Medium and low risks
   - Business impact

4. KEY FINDINGS
   - Top 3-5 most critical findings
   - Each finding with severity and impact"""

        if include_recommendations:
            prompt += """

5. RECOMMENDATIONS
   - Top 5 strategic recommendations
   - Priority and timeline for each
   - Expected impact"""

        prompt += """

Format the response with clear section headers (use "###" for sections).
Be concise, professional, and focused on executive-level insights.
"""

        return prompt

    def _build_full_report_prompt(self, compliance_data: Dict, include_recommendations: bool) -> str:
        """Build prompt for full compliance report"""
        company_name = compliance_data.get('company_name', 'Unknown Company')
        framework = compliance_data.get('framework', 'Rwanda-NCSA')
        total_controls = compliance_data.get('total_controls', 0)
        compliant = compliance_data.get('compliant_controls', 0)

        prompt = f"""Generate a comprehensive compliance report for {company_name}.

Framework: {framework}
Total Controls: {total_controls}
Compliant: {compliant}

Generate a detailed compliance report with these sections:

1. INTRODUCTION
   - Purpose of assessment
   - Scope and methodology
   - Assessment period

2. EXECUTIVE SUMMARY
   - High-level overview
   - Key findings

3. COMPLIANCE ANALYSIS
   - Detailed analysis by control family
   - Strengths and weaknesses

4. RISK ASSESSMENT
   - Risk categories and levels
   - Potential business impact

5. DETAILED FINDINGS
   - Critical issues
   - Major concerns
   - Minor observations

6. COMPLIANCE GAPS
   - Identified gaps
   - Impact analysis"""

        if include_recommendations:
            prompt += """

7. RECOMMENDATIONS
   - Strategic recommendations
   - Tactical improvements
   - Implementation roadmap

8. NEXT STEPS
   - Immediate actions
   - Short-term goals
   - Long-term strategy"""

        prompt += """

Format with clear section headers (use "###").
Be thorough and professional."""

        return prompt

    def _build_gap_analysis_prompt(self, compliance_data: Dict) -> str:
        """Build prompt for gap analysis"""
        company_name = compliance_data.get('company_name', 'Unknown Company')
        non_compliant = compliance_data.get('non_compliant_controls', 0)

        prompt = f"""Generate a compliance gap analysis report for {company_name}.

Non-Compliant Controls: {non_compliant}

Analyze the compliance gaps with these sections:

1. GAP ANALYSIS OVERVIEW
   - Summary of identified gaps
   - Gap severity distribution

2. CRITICAL GAPS
   - High-severity gaps requiring immediate attention
   - Business impact for each

3. MODERATE GAPS
   - Medium-priority gaps
   - Recommended timelines

4. MINOR GAPS
   - Low-priority gaps
   - Long-term improvements

5. ROOT CAUSE ANALYSIS
   - Common patterns in gaps
   - Systemic issues identified

6. REMEDIATION ROADMAP
   - Phase 1: Immediate actions (0-30 days)
   - Phase 2: Short-term fixes (1-3 months)
   - Phase 3: Long-term improvements (3-12 months)

7. RESOURCE REQUIREMENTS
   - Personnel needs
   - Technology requirements
   - Budget estimates

Format with clear section headers (use "###")."""

        return prompt

    def _parse_llm_response(self, content: str, report_type: str) -> Dict:
        """Parse LLM response into structured sections"""
        sections = {}
        current_section = "introduction"
        current_content = []

        for line in content.split('\n'):
            line = line.strip()

            # Check if line is a section header
            if line.startswith('###'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()

                # Start new section
                current_section = line.replace('###', '').strip().lower().replace(' ', '_')
                current_content = []
            else:
                if line:
                    current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()

        return {
            "report_type": report_type,
            "sections": sections,
            "full_text": content
        }

    def _generate_mock_executive(self, compliance_data: Dict, include_recommendations: bool) -> Dict:
        """Generate mock executive summary"""
        company_name = compliance_data.get('company_name', 'Unknown Company')
        total_controls = compliance_data.get('total_controls', 0)
        compliant = compliance_data.get('compliant_controls', 0)
        non_compliant = compliance_data.get('non_compliant_controls', 0)
        compliance_rate = (compliant / total_controls * 100) if total_controls > 0 else 0

        sections = {
            "executive_summary": f"""
{company_name} has undergone a comprehensive cybersecurity compliance assessment against the Rwanda National Cyber Security Authority (NCSA) Cybersecurity Minimum Standards. The assessment evaluated {total_controls} security controls across 12 control families.

Overall Compliance Rate: {compliance_rate:.1f}%

The organization demonstrates {'strong' if compliance_rate >= 80 else 'moderate' if compliance_rate >= 60 else 'limited'} compliance with Rwanda NCSA requirements, with {compliant} controls fully implemented and {non_compliant} controls requiring remediation.
""",

            "compliance_overview": f"""
Assessment Period: {compliance_data.get('assessment_date', 'Current')}
Framework: Rwanda NCSA Cybersecurity Minimum Standards
Total Controls Evaluated: {total_controls}
Compliant Controls: {compliant} ({compliance_rate:.1f}%)
Non-Compliant Controls: {non_compliant} ({100-compliance_rate:.1f}%)

The compliance assessment reveals that the organization has implemented foundational security controls but requires additional effort to achieve full compliance with Rwanda NCSA standards.
""",

            "risk_assessment": """
HIGH PRIORITY RISKS:
- Access Control: Inadequate role-based access controls increase unauthorized access risk
- Audit & Accountability: Insufficient logging may impede incident detection and response
- System Integrity: Lack of file integrity monitoring exposes systems to tampering

MEDIUM PRIORITY RISKS:
- Configuration Management: Inconsistent baseline configurations across systems
- Incident Response: Limited incident response procedures and testing

LOW PRIORITY RISKS:
- Documentation: Some security policies require updates to reflect current practices
""",

            "key_findings": """
1. ACCESS CONTROL GAPS (HIGH)
   Finding: 30% of systems lack proper role-based access controls
   Impact: Increased risk of unauthorized access and data breaches

2. AUDIT LOGGING DEFICIENCIES (HIGH)
   Finding: Centralized logging not implemented for all critical systems
   Impact: Delayed detection of security incidents and compliance violations

3. INCIDENT RESPONSE MATURITY (MEDIUM)
   Finding: Incident response plan exists but lacks regular testing
   Impact: Potential delays in responding to security incidents

4. CONFIGURATION MANAGEMENT (MEDIUM)
   Finding: Security baselines not consistently applied
   Impact: System hardening gaps and increased attack surface

5. SECURITY AWARENESS (LOW)
   Finding: Annual security training completion rate is 85%
   Impact: Minor risk of social engineering vulnerabilities
"""
        }

        if include_recommendations:
            sections["recommendations"] = """
1. IMPLEMENT RBAC SYSTEM (PRIORITY: HIGH, TIMELINE: 30 DAYS)
   Deploy role-based access control across all critical systems
   Expected Impact: 40% reduction in unauthorized access risk

2. CENTRALIZE AUDIT LOGGING (PRIORITY: HIGH, TIMELINE: 60 DAYS)
   Implement SIEM solution for centralized log management
   Expected Impact: Real-time threat detection and compliance monitoring

3. ENHANCE INCIDENT RESPONSE (PRIORITY: MEDIUM, TIMELINE: 90 DAYS)
   Conduct quarterly incident response exercises
   Expected Impact: 50% improvement in mean time to respond

4. STANDARDIZE CONFIGURATIONS (PRIORITY: MEDIUM, TIMELINE: 120 DAYS)
   Apply CIS benchmarks to all server and network infrastructure
   Expected Impact: Reduced attack surface by 30%

5. INCREASE SECURITY AWARENESS (PRIORITY: LOW, TIMELINE: 180 DAYS)
   Implement quarterly security awareness campaigns
   Expected Impact: Achieve 98% training completion rate
"""

        return {
            "report_type": "executive",
            "sections": sections,
            "full_text": "\n\n".join(sections.values())
        }

    def _generate_mock_full(self, compliance_data: Dict, include_recommendations: bool) -> Dict:
        """Generate mock full report"""
        executive_content = self._generate_mock_executive(compliance_data, include_recommendations)

        # Add additional sections for full report
        sections = executive_content["sections"].copy()

        sections["introduction"] = f"""
This comprehensive compliance assessment report presents the findings of a thorough evaluation of {compliance_data.get('company_name', 'Unknown Company')}'s cybersecurity posture against the Rwanda National Cyber Security Authority (NCSA) Cybersecurity Minimum Standards.

ASSESSMENT SCOPE:
The assessment covered all 12 control families defined in the Rwanda NCSA framework, evaluating technical controls, policies, procedures, and operational practices.

METHODOLOGY:
The assessment employed a combination of automated scanning, manual review of security configurations, documentation analysis, and interviews with key personnel.

ASSESSMENT PERIOD:
{compliance_data.get('assessment_date', 'Current Assessment Period')}
"""

        sections["compliance_analysis"] = """
CONTROL FAMILY BREAKDOWN:

Access Control (AC): 75% compliant
- Strengths: Password policies, account management
- Weaknesses: Role-based access, privileged account monitoring

Audit and Accountability (AU): 65% compliant
- Strengths: Basic logging enabled
- Weaknesses: Centralized logging, log retention, SIEM

Configuration Management (CM): 80% compliant
- Strengths: Change control process
- Weaknesses: Baseline configurations, automated compliance checking

Identification and Authentication (IA): 90% compliant
- Strengths: Multi-factor authentication, strong password requirements
- Weaknesses: Periodic re-authentication for privileged users

Incident Response (IR): 70% compliant
- Strengths: Incident response plan documented
- Weaknesses: Regular testing, automation, playbooks

System and Information Integrity (SI): 75% compliant
- Strengths: Antivirus deployment, patch management
- Weaknesses: File integrity monitoring, vulnerability scanning frequency
"""

        return {
            "report_type": "full",
            "sections": sections,
            "full_text": "\n\n".join(sections.values())
        }

    def _generate_mock_gap_analysis(self, compliance_data: Dict) -> Dict:
        """Generate mock gap analysis"""
        sections = {
            "gap_analysis_overview": f"""
Compliance gap analysis for {compliance_data.get('company_name', 'Unknown Company')} identified {compliance_data.get('non_compliant_controls', 0)} non-compliant controls requiring remediation.

GAP SEVERITY DISTRIBUTION:
- Critical: 8 gaps (immediate action required)
- High: 15 gaps (30-day timeline)
- Medium: 22 gaps (90-day timeline)
- Low: 12 gaps (180-day timeline)
""",

            "critical_gaps": """
1. CENTRALIZED LOGGING AND MONITORING (AU-2, AU-3, AU-6)
   Gap: No centralized SIEM solution deployed
   Business Impact: Unable to detect sophisticated attacks or insider threats
   Remediation: Deploy SIEM platform within 30 days

2. PRIVILEGED ACCESS MANAGEMENT (AC-2, AC-6)
   Gap: No privileged access management (PAM) solution
   Business Impact: Elevated risk of credential theft and unauthorized admin access
   Remediation: Implement PAM solution within 45 days

3. VULNERABILITY MANAGEMENT (RA-5, SI-2)
   Gap: Vulnerability scanning performed quarterly (should be continuous)
   Business Impact: Extended exposure window to known vulnerabilities
   Remediation: Deploy continuous vulnerability scanning within 30 days
""",

            "moderate_gaps": """
1. SECURITY AWARENESS TRAINING (AT-2)
   Gap: Annual training only, no phishing simulations
   Recommended Timeline: 60 days

2. INCIDENT RESPONSE TESTING (IR-3)
   Gap: Incident response plan not tested regularly
   Recommended Timeline: 90 days

3. CONFIGURATION BASELINES (CM-2)
   Gap: Security baselines not documented for all system types
   Recommended Timeline: 90 days
""",

            "root_cause_analysis": """
Analysis of compliance gaps reveals several systemic issues:

1. RESOURCE CONSTRAINTS
   Many gaps stem from insufficient security staffing and budget allocation

2. TOOLING GAPS
   Lack of enterprise security tools (SIEM, PAM, vulnerability scanner)

3. PROCESS MATURITY
   Security processes exist but lack formalization and regular review

4. AWARENESS AND TRAINING
   Limited security awareness across the organization
""",

            "remediation_roadmap": """
PHASE 1: IMMEDIATE ACTIONS (0-30 DAYS)
- Deploy centralized logging and SIEM
- Implement continuous vulnerability scanning
- Enable file integrity monitoring on critical systems
- Estimated Cost: $50,000 - $100,000

PHASE 2: SHORT-TERM FIXES (1-3 MONTHS)
- Implement privileged access management
- Establish security configuration baselines
- Conduct first incident response exercise
- Launch security awareness campaign
- Estimated Cost: $75,000 - $150,000

PHASE 3: LONG-TERM IMPROVEMENTS (3-12 MONTHS)
- Automate compliance checking
- Implement security orchestration
- Achieve full compliance with Rwanda NCSA
- Establish continuous improvement program
- Estimated Cost: $100,000 - $200,000
"""
        }

        return {
            "report_type": "gap_analysis",
            "sections": sections,
            "full_text": "\n\n".join(sections.values())
        }
