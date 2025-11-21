#!/usr/bin/env python3
"""
Demo: Model Explainability
Show how the model makes decisions
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from explain_predictions_cli import ModelExplainer


def main():
    print("\n" + "="*90)
    print(" "*30 + "EXPLAINABILITY DEMO")
    print("="*90)
    print()
    print("This demo shows HOW the model makes predictions")
    print("and WHICH features influence its decisions.")
    print()

    # Initialize explainer
    explainer = ModelExplainer()

    # Load test data
    test_df = pd.read_csv("data/combined_compliance/compliance_events_test.csv")

    # Example 1: Compliant event
    print("\n" + "="*90)
    print("EXAMPLE 1: COMPLIANT EVENT")
    print("="*90)

    compliant_events = test_df[test_df['compliance_status'] == 'compliant']
    sample1 = compliant_events.sample(n=1, random_state=42)

    explainer.explain_single_event(sample1)

    input("\n[Press Enter to see next example...]")

    # Example 2: Non-compliant event
    print("\n" + "="*90)
    print("EXAMPLE 2: NON-COMPLIANT EVENT (ATTACK)")
    print("="*90)

    non_compliant_events = test_df[test_df['compliance_status'] == 'non_compliant']
    sample2 = non_compliant_events.sample(n=1, random_state=42)

    explainer.explain_single_event(sample2)

    input("\n[Press Enter to see batch analysis...]")

    # Example 3: Batch analysis
    print("\n" + "="*90)
    print("EXAMPLE 3: BATCH ANALYSIS")
    print("="*90)

    sample3 = test_df.sample(n=20, random_state=42)
    explainer.batch_explain(sample3, top_n=5)

    print("\n" + "="*90)
    print("DEMO COMPLETE")
    print("="*90)
    print()
    print("To run full interactive mode:")
    print("  python explain_predictions_cli.py --interactive")
    print()
    print("="*90)


if __name__ == '__main__':
    main()
