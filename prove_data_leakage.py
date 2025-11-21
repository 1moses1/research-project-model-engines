#!/usr/bin/env python3
"""
Prove Data Leakage - Simple and Definitive Test
Flip status codes and see if model predictions flip too
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.xgboost_classifier import XGBoostClassifier


def main():
    print("\n" + "="*80)
    print("DATA LEAKAGE PROOF TEST")
    print("="*80)
    print()

    # Load model
    classifier = XGBoostClassifier()
    model_path = Path("results/models/xgboost_compliance_enriched/xgboost_model_compliance_enriched")
    classifier.load_model(str(model_path))
    print("✅ Model loaded\n")

    # Load test data
    test_df = pd.read_csv("data/combined_compliance/compliance_events_test.csv")
    sample = test_df.sample(n=100, random_state=42)
    print(f"📊 Testing on {len(sample)} samples\n")

    #-------------------------------------------
    # TEST 1: Original predictions
    #-------------------------------------------
    print("TEST 1: Original Data")
    print("-" * 80)

    preds_original, probs_original = classifier.predict(sample)

    compliant_count = sum(1 for p in preds_original if p == 'compliant')
    non_compliant_count = len(preds_original) - compliant_count

    print(f"Predictions:")
    print(f"  Compliant: {compliant_count}")
    print(f"  Non-Compliant: {non_compliant_count}")
    print()

    #-------------------------------------------
    # TEST 2: Flip status codes (200→403, 403→200)
    #-------------------------------------------
    print("TEST 2: Flipped Status Codes")
    print("-" * 80)
    print("Action: Changing all status codes 200→403, 403→200")
    print("        (keeping everything else EXACTLY the same)\n")

    modified = sample.copy()

    # Flip status codes
    def flip_status(code):
        if code in [200, 201, 204]:
            return 403  # Success → Forbidden
        elif code in [400, 401, 403, 404, 500, 503]:
            return 200  # Error → Success
        return code

    modified['status_code'] = modified['status_code'].apply(flip_status)

    preds_modified, probs_modified = classifier.predict(modified)

    compliant_count_mod = sum(1 for p in preds_modified if p == 'compliant')
    non_compliant_count_mod = len(preds_modified) - compliant_count_mod

    print(f"Predictions AFTER flipping status codes:")
    print(f"  Compliant: {compliant_count_mod}")
    print(f"  Non-Compliant: {non_compliant_count_mod}")
    print()

    #-------------------------------------------
    # ANALYSIS
    #-------------------------------------------
    print("="*80)
    print("ANALYSIS")
    print("="*80)
    print()

    # Count how many predictions flipped
    flipped = sum(1 for orig, mod in zip(preds_original, preds_modified) if orig != mod)
    flip_rate = flipped / len(preds_original) * 100

    print(f"Predictions that changed: {flipped}/{len(preds_original)} ({flip_rate:.1f}%)")
    print()

    # Detailed comparison
    print("Prediction Changes:")
    changes = {
        'compliant_to_noncompliant': 0,
        'noncompliant_to_compliant': 0,
        'no_change': 0
    }

    for i, (orig, mod) in enumerate(zip(preds_original, preds_modified)):
        if orig == 'compliant' and mod == 'non_compliant':
            changes['compliant_to_noncompliant'] += 1
        elif orig == 'non_compliant' and mod == 'compliant':
            changes['noncompliant_to_compliant'] += 1
        else:
            changes['no_change'] += 1

    print(f"  Compliant → Non-Compliant: {changes['compliant_to_noncompliant']}")
    print(f"  Non-Compliant → Compliant: {changes['noncompliant_to_compliant']}")
    print(f"  No Change: {changes['no_change']}")
    print()

    #-------------------------------------------
    # VERDICT
    #-------------------------------------------
    print("="*80)
    print("VERDICT")
    print("="*80)
    print()

    if flip_rate > 70:
        print("🚨 CRITICAL DATA LEAKAGE CONFIRMED!")
        print()
        print(f"{flip_rate:.1f}% of predictions flipped when only status codes changed!")
        print()
        print("This proves the model is relying heavily on status codes,")
        print("not learning actual security patterns from log messages.")
        print()
        print("The 100% accuracy was FAKE - due to data leakage.")
        print()
        verdict = "CRITICAL_LEAKAGE"

    elif flip_rate > 30:
        print("⚠️  SIGNIFICANT DATA LEAKAGE DETECTED")
        print()
        print(f"{flip_rate:.1f}% of predictions changed with status code flip.")
        print()
        print("Status codes have too much influence on predictions.")
        print("Model is not learning robust security patterns.")
        print()
        verdict = "MODERATE_LEAKAGE"

    elif flip_rate > 10:
        print("⚠️  MINOR DATA LEAKAGE")
        print()
        print(f"{flip_rate:.1f}% of predictions changed.")
        print()
        print("Status codes have some influence, but not critical.")
        print("Model is using other features too.")
        print()
        verdict = "MINOR_LEAKAGE"

    else:
        print("✅ NO SIGNIFICANT DATA LEAKAGE")
        print()
        print(f"Only {flip_rate:.1f}% of predictions changed.")
        print()
        print("Model is robust to status code changes.")
        print("Likely learning from log message content.")
        print()
        verdict = "NO_LEAKAGE"

    #-------------------------------------------
    # RECOMMENDATION
    #-------------------------------------------
    print("="*80)
    print("RECOMMENDATION")
    print("="*80)
    print()

    if verdict in ['CRITICAL_LEAKAGE', 'MODERATE_LEAKAGE']:
        print("❌ DO NOT DEPLOY THIS MODEL TO PRODUCTION")
        print()
        print("Required Actions:")
        print("1. Remove status_code from features")
        print("2. Retrain model without data leakage")
        print("3. Test again on truly novel scenarios")
        print("4. Expect accuracy to drop to 85-95% (more realistic)")
        print()
    else:
        print("✅ Model can be deployed with caution")
        print()
        print("Recommended Actions:")
        print("1. Continue monitoring in production")
        print("2. Test on more adversarial scenarios")
        print("3. Implement explainability interface")
        print()

    print("="*80)

    # Save results
    results = {
        'flip_rate': float(flip_rate),
        'total_samples': len(preds_original),
        'predictions_changed': int(flipped),
        'verdict': verdict,
        'changes': changes
    }

    import json
    output_file = Path("results/models/xgboost_compliance_enriched/data_leakage_proof.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print()


if __name__ == '__main__':
    main()
