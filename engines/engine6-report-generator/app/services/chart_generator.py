"""
Chart Generator Service
Generates charts and visualizations for compliance reports
"""

from typing import Dict, List
import io
import base64


class ChartGenerator:
    """Generates charts for compliance reports"""

    def __init__(self):
        self.matplotlib_available = False
        self._check_matplotlib()

    def _check_matplotlib(self):
        """Check if matplotlib is available"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            self.matplotlib_available = True
            print("✅ Matplotlib available for chart generation")
        except ImportError:
            print("⚠️  Matplotlib not available - charts will be skipped")

    def generate_charts(
        self,
        compliance_data: Dict,
        report_type: str
    ) -> List[Dict]:
        """
        Generate charts for the report

        Args:
            compliance_data: Compliance metrics and data
            report_type: Type of report (full, executive, scorecard, gap_analysis)

        Returns:
            List of chart dictionaries with image data
        """
        if not self.matplotlib_available:
            return []

        charts = []

        try:
            # Generate different charts based on report type
            if report_type in ["full", "executive"]:
                charts.append(self._generate_compliance_pie_chart(compliance_data))
                charts.append(self._generate_family_bar_chart(compliance_data))
                charts.append(self._generate_risk_distribution(compliance_data))

            elif report_type == "scorecard":
                charts.append(self._generate_compliance_gauge(compliance_data))
                charts.append(self._generate_family_bar_chart(compliance_data))

            elif report_type == "gap_analysis":
                charts.append(self._generate_gap_severity_chart(compliance_data))
                charts.append(self._generate_family_bar_chart(compliance_data))

            print(f"📊 Generated {len(charts)} charts for {report_type} report")

        except Exception as e:
            print(f"⚠️ Chart generation error: {str(e)}")

        return charts

    def _generate_compliance_pie_chart(self, compliance_data: Dict) -> Dict:
        """Generate compliance overview pie chart"""
        try:
            import matplotlib.pyplot as plt

            compliant = compliance_data.get('compliant_controls', 0)
            non_compliant = compliance_data.get('non_compliant_controls', 0)
            pending = compliance_data.get('pending_controls', 0)

            # Create pie chart
            fig, ax = plt.subplots(figsize=(8, 6))

            sizes = [compliant, non_compliant, pending]
            labels = ['Compliant', 'Non-Compliant', 'Pending']
            colors = ['#2ecc71', '#e74c3c', '#f39c12']
            explode = (0.1, 0, 0)  # Explode compliant slice

            ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='%1.1f%%', shadow=True, startangle=90)
            ax.axis('equal')
            plt.title('Compliance Status Overview', fontsize=14, fontweight='bold')

            # Convert to base64
            img_data = self._fig_to_base64(fig)
            plt.close(fig)

            return {
                "type": "pie",
                "title": "Compliance Status Overview",
                "data": img_data,
                "description": "Distribution of control compliance status"
            }

        except Exception as e:
            print(f"⚠️ Pie chart error: {str(e)}")
            return {}

    def _generate_family_bar_chart(self, compliance_data: Dict) -> Dict:
        """Generate control family scores bar chart"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            family_scores = compliance_data.get('family_scores', [])

            if not family_scores:
                # Generate mock data
                family_scores = self._generate_mock_family_scores(compliance_data)

            # Extract data
            families = [f.get('family', '')[:20] for f in family_scores]  # Truncate long names
            scores = [f.get('compliance_percentage', 0) for f in family_scores]

            # Create bar chart
            fig, ax = plt.subplots(figsize=(12, 8))

            y_pos = np.arange(len(families))
            colors = ['#2ecc71' if s >= 90 else '#f39c12' if s >= 70 else '#e74c3c' for s in scores]

            bars = ax.barh(y_pos, scores, color=colors, alpha=0.8)

            # Add value labels on bars
            for i, (bar, score) in enumerate(zip(bars, scores)):
                ax.text(score + 2, i, f'{score:.1f}%', va='center', fontsize=9)

            ax.set_yticks(y_pos)
            ax.set_yticklabels(families, fontsize=10)
            ax.set_xlabel('Compliance Percentage', fontsize=11, fontweight='bold')
            ax.set_title('Compliance Score by Control Family', fontsize=14, fontweight='bold')
            ax.set_xlim(0, 105)

            # Add grid
            ax.grid(axis='x', linestyle='--', alpha=0.3)

            # Add reference lines
            ax.axvline(x=90, color='green', linestyle='--', alpha=0.5, label='Target (90%)')
            ax.axvline(x=70, color='orange', linestyle='--', alpha=0.5, label='Minimum (70%)')
            ax.legend(loc='lower right', fontsize=9)

            plt.tight_layout()

            # Convert to base64
            img_data = self._fig_to_base64(fig)
            plt.close(fig)

            return {
                "type": "bar",
                "title": "Control Family Compliance Scores",
                "data": img_data,
                "description": "Compliance percentage for each control family"
            }

        except Exception as e:
            print(f"⚠️ Bar chart error: {str(e)}")
            return {}

    def _generate_risk_distribution(self, compliance_data: Dict) -> Dict:
        """Generate risk distribution chart"""
        try:
            import matplotlib.pyplot as plt

            risk_data = compliance_data.get('risk_summary', {})

            critical = risk_data.get('critical', 3)
            high = risk_data.get('high', 8)
            medium = risk_data.get('medium', 15)
            low = risk_data.get('low', 12)

            # Create bar chart
            fig, ax = plt.subplots(figsize=(8, 6))

            risk_levels = ['Critical', 'High', 'Medium', 'Low']
            counts = [critical, high, medium, low]
            colors = ['#c0392b', '#e74c3c', '#f39c12', '#2ecc71']

            bars = ax.bar(risk_levels, counts, color=colors, alpha=0.8)

            # Add value labels
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(count)}', ha='center', va='bottom', fontsize=12, fontweight='bold')

            ax.set_ylabel('Number of Risks', fontsize=11, fontweight='bold')
            ax.set_title('Risk Distribution', fontsize=14, fontweight='bold')
            ax.grid(axis='y', linestyle='--', alpha=0.3)

            plt.tight_layout()

            # Convert to base64
            img_data = self._fig_to_base64(fig)
            plt.close(fig)

            return {
                "type": "bar",
                "title": "Risk Distribution",
                "data": img_data,
                "description": "Distribution of identified risks by severity"
            }

        except Exception as e:
            print(f"⚠️ Risk chart error: {str(e)}")
            return {}

    def _generate_compliance_gauge(self, compliance_data: Dict) -> Dict:
        """Generate compliance rate gauge/meter"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np

            total = compliance_data.get('total_controls', 0)
            compliant = compliance_data.get('compliant_controls', 0)
            compliance_rate = (compliant / total * 100) if total > 0 else 0

            # Create gauge chart
            fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={'projection': 'polar'})

            # Set up gauge
            theta = np.linspace(0, np.pi, 100)

            # Background arc (0-100%)
            ax.plot(theta, [1]*len(theta), color='lightgray', linewidth=20, alpha=0.3)

            # Compliance arc
            compliance_theta = np.linspace(0, np.pi * (compliance_rate / 100), 100)
            color = '#2ecc71' if compliance_rate >= 90 else '#f39c12' if compliance_rate >= 70 else '#e74c3c'
            ax.plot(compliance_theta, [1]*len(compliance_theta), color=color, linewidth=20)

            # Configure chart
            ax.set_ylim(0, 1.5)
            ax.set_yticks([])
            ax.set_xticks(np.linspace(0, np.pi, 5))
            ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
            ax.spines['polar'].set_visible(False)

            # Add compliance rate text
            ax.text(np.pi/2, 0.5, f'{compliance_rate:.1f}%',
                   ha='center', va='center', fontsize=36, fontweight='bold', color=color)
            ax.text(np.pi/2, 0.2, 'Compliance Rate',
                   ha='center', va='center', fontsize=12, color='gray')

            plt.title('Overall Compliance Score', fontsize=14, fontweight='bold', pad=20)

            # Convert to base64
            img_data = self._fig_to_base64(fig)
            plt.close(fig)

            return {
                "type": "gauge",
                "title": "Overall Compliance Score",
                "data": img_data,
                "description": f"Current compliance rate: {compliance_rate:.1f}%"
            }

        except Exception as e:
            print(f"⚠️ Gauge chart error: {str(e)}")
            return {}

    def _generate_gap_severity_chart(self, compliance_data: Dict) -> Dict:
        """Generate gap severity distribution chart"""
        try:
            import matplotlib.pyplot as plt

            # Calculate gap distribution
            non_compliant = compliance_data.get('non_compliant_controls', 0)

            # Estimate distribution (could be provided in compliance_data)
            critical = int(non_compliant * 0.15)
            high = int(non_compliant * 0.30)
            medium = int(non_compliant * 0.35)
            low = non_compliant - critical - high - medium

            # Create pie chart
            fig, ax = plt.subplots(figsize=(8, 6))

            sizes = [critical, high, medium, low]
            labels = ['Critical', 'High', 'Medium', 'Low']
            colors = ['#c0392b', '#e74c3c', '#f39c12', '#2ecc71']
            explode = (0.1, 0.05, 0, 0)

            ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                   autopct='%1.1f%%', shadow=True, startangle=90)
            ax.axis('equal')
            plt.title('Gap Severity Distribution', fontsize=14, fontweight='bold')

            # Convert to base64
            img_data = self._fig_to_base64(fig)
            plt.close(fig)

            return {
                "type": "pie",
                "title": "Gap Severity Distribution",
                "data": img_data,
                "description": "Distribution of compliance gaps by severity level"
            }

        except Exception as e:
            print(f"⚠️ Gap chart error: {str(e)}")
            return {}

    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string"""
        try:
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            buffer.close()
            return img_base64
        except Exception as e:
            print(f"⚠️ Figure to base64 error: {str(e)}")
            return ""

    def _generate_mock_family_scores(self, compliance_data: Dict) -> List[Dict]:
        """Generate mock family scores for testing"""
        families = [
            "Access Control",
            "Audit and Accountability",
            "Configuration Management",
            "Identification and Authentication",
            "Incident Response",
            "Maintenance",
            "Media Protection",
            "Physical Protection",
            "Risk Assessment",
            "System Protection",
            "System Integrity",
            "Security Training"
        ]

        overall_rate = (compliance_data.get('compliant_controls', 0) /
                       compliance_data.get('total_controls', 1) * 100)

        variations = [5, -3, 8, -5, 3, -2, 7, -4, 2, -6, 4, -1]

        family_scores = []
        for idx, family in enumerate(families):
            score = max(0, min(100, overall_rate + variations[idx]))
            family_scores.append({
                "family": family,
                "compliance_percentage": round(score, 1)
            })

        return family_scores
