"""
LLM Processing Service
Uses OpenAI GPT-4 to extract compliance controls from documents
"""

from typing import Dict, List, Optional
import json
import random
import os
from pathlib import Path


class LLMProcessor:
    """Processes documents with LLM to extract controls"""

    def __init__(self, api_key: Optional[str] = None, control_taxonomy_path: Optional[str] = None):
        self.api_key = api_key
        self.enabled = bool(api_key)

        # Load Rwanda NCSA controls for baseline
        self.rwanda_controls = self._load_rwanda_controls(control_taxonomy_path)
        print(f"✅ Loaded {len(self.rwanda_controls)} Rwanda NCSA controls for LLM context")

        if self.enabled:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=api_key)
                print("✅ OpenAI client initialized")
            except ImportError:
                print("⚠️  OpenAI package not installed - using mock mode")
                self.enabled = False
                self.client = None
        else:
            print("⚠️  No API key provided - using mock mode")
            self.client = None

    def _load_rwanda_controls(self, taxonomy_path: Optional[str] = None) -> List[Dict]:
        """Load Rwanda NCSA controls from taxonomy"""
        try:
            if taxonomy_path is None:
                taxonomy_path = os.getenv(
                    'CONTROL_TAXONOMY_PATH',
                    '/app/data/control_taxonomy_validated.json'
                )

            with open(taxonomy_path, 'r') as f:
                taxonomy_data = json.load(f)

            # Extract Rwanda controls
            rwanda_controls = taxonomy_data.get('rwanda', [])

            # Format for LLM prompt (simplified)
            simplified_controls = []
            for ctrl in rwanda_controls[:50]:  # Use top 50 most common controls
                simplified_controls.append({
                    'control_id': ctrl['control_id'],
                    'name': ctrl['name'],
                    'family': ctrl['family'],
                    'description': ctrl.get('description', '')[:200]  # Truncate long descriptions
                })

            return simplified_controls

        except Exception as e:
            print(f"⚠️ Could not load Rwanda controls: {str(e)}")
            return []

    def is_enabled(self) -> bool:
        """Check if LLM is enabled"""
        return self.enabled

    async def extract_controls(
        self,
        text: str,
        framework: str = "Rwanda-NCSA",
        company_name: str = "Demo Company"
    ) -> Dict:
        """
        Extract compliance controls from text using LLM

        Args:
            text: Document text
            framework: Compliance framework (Rwanda-NCSA, NIST, etc.)
            company_name: Company name

        Returns:
            Dictionary with extracted controls
        """
        if self.enabled and self.client:
            return await self._extract_with_openai(text, framework, company_name)
        else:
            return self._extract_mock(text, framework, company_name)

    async def _extract_with_openai(
        self,
        text: str,
        framework: str,
        company_name: str
    ) -> Dict:
        """Extract controls using OpenAI GPT-4"""
        try:
            # Truncate text if too long (max 8000 chars)
            truncated_text = text[:8000] if len(text) > 8000 else text

            # Prepare Rwanda NCSA controls list for prompt
            controls_context = json.dumps(self.rwanda_controls[:30], indent=2)  # Use top 30 for token limit

            prompt = f"""You are a compliance auditor analyzing policy documents for {company_name} against Rwanda NCSA Cybersecurity Minimum Standards.

CRITICAL INSTRUCTIONS:
1. You MUST map findings to the Rwanda NCSA controls provided below
2. Use ONLY the control_id format from the Rwanda NCSA list (e.g., "4-1", "5-2", "6-3")
3. DO NOT create generic control IDs like "AC-1" or "PM-1"
4. Match document findings to the most relevant Rwanda NCSA control from the list

RWANDA NCSA CONTROLS BASELINE:
{controls_context}

TASK:
Analyze the document and identify security findings, gaps, or requirements. For each finding:
1. MAP it to the most relevant Rwanda NCSA control from the list above
2. Use the exact control_id from the list (e.g., "4-1" not "AC-1")
3. Extract specific requirements/findings from the document
4. Assess compliance status
5. Provide confidence score (0.0-1.0)

If a finding doesn't match any Rwanda NCSA control well, choose the closest match and note lower confidence.

Return ONLY valid JSON with this structure:
{{
  "controls": [
    {{
      "control_id": "4-1",
      "control_name": "Security Policy and Procedures - Requirement 4-1",
      "description": "Specific finding from document...",
      "family": "Security Policy and Procedures",
      "requirements": ["Specific requirement 1", "Specific requirement 2"],
      "evidence": "Quote or reference from document",
      "compliance_status": "non_compliant",
      "confidence": 0.85
    }}
  ]
}}

DOCUMENT TEXT:
{truncated_text}

Extract controls mapped to Rwanda NCSA (JSON only):"""

            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a Rwanda NCSA compliance auditor. You MUST map findings to Rwanda NCSA control IDs. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Lower temperature for more consistent control mapping
                max_tokens=3000  # More tokens for detailed analysis
            )

            content = response.choices[0].message.content

            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract JSON from markdown code blocks
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
            print(f"⚠️ OpenAI API error: {str(e)}")
            print("⚠️ Falling back to mock extraction")
            return self._extract_mock(text, framework, company_name)

    def _extract_mock(
        self,
        text: str,
        framework: str,
        company_name: str
    ) -> Dict:
        """
        Mock control extraction (when OpenAI not available)
        Simulates realistic control extraction based on text length
        """
        # Calculate number of controls based on text length
        words = len(text.split())
        num_controls = min(max(words // 200, 3), 20)  # 3-20 controls

        control_families = [
            "Access Control",
            "Audit and Accountability",
            "Configuration Management",
            "Identification and Authentication",
            "Incident Response",
            "System and Information Integrity"
        ]

        mock_controls = []

        for i in range(num_controls):
            family = random.choice(control_families)
            family_prefix = family.split()[0][:2].upper()

            control = {
                "control_id": f"{family_prefix}-{i+1}",
                "control_name": f"{family} Policy and Procedures",
                "description": f"The organization develops, documents, and disseminates {family.lower()} policies and procedures.",
                "family": family,
                "requirements": [
                    f"Develop {family.lower()} policy",
                    f"Document {family.lower()} procedures",
                    f"Review and update {family.lower()} controls annually"
                ],
                "confidence": round(random.uniform(0.75, 0.95), 2)
            }

            mock_controls.append(control)

        print(f"🔄 Mock extraction: {len(mock_controls)} controls")

        return {"controls": mock_controls}
