"""
Compliance Scoring Service
Aggregates compliance scores by control family
"""

from typing import Dict, List
from collections import defaultdict
import asyncio


class ComplianceScorer:
    """Manages compliance scoring aggregation"""

    def __init__(self):
        # In-memory storage (in production, use PostgreSQL)
        self.family_stats = defaultdict(lambda: {"compliant": 0, "total": 0})
        self.overall_stats = {"compliant": 0, "total": 0}

        # Rwanda NCSA Control Families
        self.control_families = [
            "Access Control",
            "Audit and Accountability",
            "Configuration Management",
            "Identification and Authentication",
            "Incident Response",
            "Maintenance",
            "Media Protection",
            "Physical and Environmental Protection",
            "Personnel Security",
            "Risk Assessment",
            "System and Communications Protection",
            "System and Information Integrity"
        ]

        # Initialize families
        for family in self.control_families:
            self.family_stats[family] = {"compliant": 0, "total": 0}

    async def update_scores(self, prediction: str):
        """
        Update compliance scores based on new prediction

        Args:
            prediction: 'compliant' or 'non_compliant'
        """
        # Update overall stats
        self.overall_stats['total'] += 1
        if prediction == 'compliant':
            self.overall_stats['compliant'] += 1

        # Map to random family for demo (in production, use actual control mapping)
        import random
        family = random.choice(self.control_families)

        # Update family stats
        self.family_stats[family]['total'] += 1
        if prediction == 'compliant':
            self.family_stats[family]['compliant'] += 1

    async def get_family_scores(self) -> List[Dict]:
        """
        Get compliance scores for all control families

        Returns:
            List of family scores with compliance percentages
        """
        scores = []

        for family, stats in self.family_stats.items():
            total = stats['total']
            compliant = stats['compliant']

            if total > 0:
                percentage = (compliant / total) * 100
            else:
                percentage = 0.0

            # Determine risk level
            if percentage >= 90:
                risk_level = "low"
            elif percentage >= 70:
                risk_level = "medium"
            else:
                risk_level = "high"

            scores.append({
                "family": family,
                "compliant_events": compliant,
                "total_events": total,
                "compliance_percentage": round(percentage, 2),
                "risk_level": risk_level
            })

        # Sort by compliance percentage (lowest first - highest risk)
        scores.sort(key=lambda x: x['compliance_percentage'])

        return scores

    async def get_overall_score(self) -> Dict:
        """
        Get overall compliance percentage

        Returns:
            Overall compliance statistics
        """
        total = self.overall_stats['total']
        compliant = self.overall_stats['compliant']

        if total > 0:
            percentage = (compliant / total) * 100
        else:
            percentage = 0.0

        return {
            "percentage": round(percentage, 2),
            "total": total,
            "compliant": compliant,
            "non_compliant": total - compliant
        }

    async def get_family_score(self, family: str) -> Dict:
        """Get score for a specific control family"""
        stats = self.family_stats.get(family, {"compliant": 0, "total": 0})
        total = stats['total']
        compliant = stats['compliant']

        if total > 0:
            percentage = (compliant / total) * 100
        else:
            percentage = 0.0

        return {
            "family": family,
            "percentage": round(percentage, 2),
            "compliant": compliant,
            "total": total
        }
