"""
Risk Assessment Service
Calculates risk scores for compliance violations
"""

from typing import Dict
import math


class RiskAssessor:
    """Calculates risk scores for events"""

    def __init__(self):
        # Risk scoring weights
        self.alpha = 0.4  # Severity weight
        self.beta = 0.3   # Likelihood weight
        self.gamma = 0.3  # Business impact weight

    async def calculate_risk(
        self,
        prediction: str,
        confidence: float,
        status_code: int
    ) -> Dict:
        """
        Calculate risk score using formula:
        Risk = α·Severity + β·Likelihood + γ·Business_Impact

        Args:
            prediction: 'compliant' or 'non_compliant'
            confidence: Prediction confidence (0-1)
            status_code: HTTP status code

        Returns:
            Risk assessment with score and level
        """
        # If compliant, risk is low
        if prediction == 'compliant':
            return {
                "score": 0.0,
                "level": "low",
                "severity": "none",
                "likelihood": 0.0,
                "business_impact": 0.0
            }

        # Calculate severity based on status code
        severity = self._calculate_severity(status_code)

        # Calculate likelihood based on confidence
        # Higher confidence in non-compliance = higher likelihood
        likelihood = confidence

        # Calculate business impact (simplified)
        business_impact = self._calculate_business_impact(status_code)

        # Overall risk score (0-10 scale)
        risk_score = (
            self.alpha * severity +
            self.beta * likelihood +
            self.gamma * business_impact
        ) * 10

        # Determine risk level
        if risk_score >= 7.0:
            risk_level = "critical"
            severity_label = "high"
        elif risk_score >= 5.0:
            risk_level = "high"
            severity_label = "medium"
        elif risk_score >= 3.0:
            risk_level = "medium"
            severity_label = "low"
        else:
            risk_level = "low"
            severity_label = "minimal"

        return {
            "score": round(risk_score, 2),
            "level": risk_level,
            "severity": severity_label,
            "likelihood": round(likelihood, 2),
            "business_impact": round(business_impact, 2)
        }

    def _calculate_severity(self, status_code: int) -> float:
        """
        Calculate severity based on HTTP status code

        Args:
            status_code: HTTP status code

        Returns:
            Severity score (0-1)
        """
        severity_map = {
            # 2xx - Success (low severity if flagged)
            200: 0.2,
            201: 0.2,

            # 3xx - Redirection (low-medium severity)
            301: 0.3,
            302: 0.3,

            # 4xx - Client errors (medium-high severity)
            400: 0.5,
            401: 0.7,  # Unauthorized - high severity
            403: 0.8,  # Forbidden - high severity
            404: 0.4,

            # 5xx - Server errors (high severity)
            500: 0.9,
            502: 0.8,
            503: 0.7
        }

        return severity_map.get(status_code, 0.5)  # Default medium

    def _calculate_business_impact(self, status_code: int) -> float:
        """
        Calculate business impact

        In production, this would consider:
        - Regulatory penalty potential
        - Data sensitivity
        - System criticality

        Args:
            status_code: HTTP status code

        Returns:
            Business impact score (0-1)
        """
        # Simplified: Higher status codes = higher impact
        if status_code >= 500:
            return 0.9  # Server errors = high business impact
        elif status_code in [401, 403]:
            return 0.8  # Security violations = high impact
        elif status_code >= 400:
            return 0.5  # Client errors = medium impact
        else:
            return 0.3  # Other = low impact
