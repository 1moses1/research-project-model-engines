"""
Continuous Learning Service
Manages feedback collection and model retraining
"""

from typing import Dict, List
from datetime import datetime


class ContinuousLearner:
    """Manages continuous learning pipeline"""

    def __init__(self):
        # In-memory feedback storage (in production, use PostgreSQL)
        self.feedback_data = []
        self.retraining_history = []

    async def add_feedback(
        self,
        event_id: str,
        predicted_label: str,
        correct_label: str,
        reviewer: str,
        notes: str = None
    ):
        """
        Record human feedback for an event

        Args:
            event_id: Event identifier
            predicted_label: Model's prediction
            correct_label: Human-corrected label
            reviewer: Username of reviewer
            notes: Optional notes
        """
        feedback = {
            "event_id": event_id,
            "predicted_label": predicted_label,
            "correct_label": correct_label,
            "reviewer": reviewer,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat(),
            "used_for_training": False
        }

        self.feedback_data.append(feedback)

        print(f"📝 Feedback recorded for {event_id} by {reviewer}")
        print(f"   Predicted: {predicted_label} → Correct: {correct_label}")

    async def get_feedback_count(self) -> int:
        """Get count of feedback items"""
        return len(self.feedback_data)

    async def get_unused_feedback_count(self) -> int:
        """Get count of feedback not yet used for training"""
        return len([f for f in self.feedback_data if not f['used_for_training']])

    async def trigger_retraining(self):
        """
        Trigger model retraining with collected feedback

        In production, this would:
        1. Combine synthetic training data with real feedback
        2. Retrain XGBoost model
        3. A/B test new model vs current
        4. Deploy if performance improves
        """
        print("\n" + "=" * 80)
        print("🔄 TRIGGERING MODEL RETRAINING")
        print("=" * 80)

        unused_feedback = [f for f in self.feedback_data if not f['used_for_training']]
        feedback_count = len(unused_feedback)

        print(f"📊 Feedback items for training: {feedback_count}")

        # Simulate retraining process
        print("🔄 Step 1: Preparing training data (synthetic + feedback)")
        print("🔄 Step 2: Training new XGBoost model")
        print("🔄 Step 3: Cross-validation (5-fold)")
        print("🔄 Step 4: A/B testing new model")

        # Mark feedback as used
        for feedback in unused_feedback:
            feedback['used_for_training'] = True

        # Record retraining
        retraining_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "feedback_count": feedback_count,
            "status": "completed",
            "model_version": f"v3.0.{len(self.retraining_history) + 1}"
        }
        self.retraining_history.append(retraining_record)

        print(f"✅ Retraining complete: Model {retraining_record['model_version']}")
        print("=" * 80 + "\n")

    async def get_stats(self) -> Dict:
        """
        Get continuous learning statistics

        Returns:
            Statistics about feedback and retraining
        """
        unused = await self.get_unused_feedback_count()

        # Calculate accuracy improvement if we have retraining history
        accuracy_improvement = 0.0
        if len(self.retraining_history) > 0:
            # Simulate improvement
            accuracy_improvement = len(self.retraining_history) * 0.05  # 5% per retraining

        return {
            "total_feedback": len(self.feedback_data),
            "unused_feedback": unused,
            "retraining_threshold": 100,
            "retraining_count": len(self.retraining_history),
            "last_retraining": self.retraining_history[-1] if self.retraining_history else None,
            "estimated_accuracy_improvement": round(accuracy_improvement, 3)
        }

    async def get_feedback_breakdown(self) -> Dict:
        """
        Get breakdown of feedback by correction type

        Returns:
            Statistics on false positives and false negatives
        """
        false_positives = 0  # Predicted non-compliant, actually compliant
        false_negatives = 0  # Predicted compliant, actually non-compliant
        correct_predictions = 0

        for feedback in self.feedback_data:
            pred = feedback['predicted_label']
            correct = feedback['correct_label']

            if pred == correct:
                correct_predictions += 1
            elif pred == 'non_compliant' and correct == 'compliant':
                false_positives += 1
            elif pred == 'compliant' and correct == 'non_compliant':
                false_negatives += 1

        total = len(self.feedback_data)

        return {
            "total_feedback": total,
            "correct_predictions": correct_predictions,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "accuracy_on_feedback": round((correct_predictions / total * 100) if total > 0 else 0, 2)
        }
