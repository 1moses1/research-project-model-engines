#!/usr/bin/env python3
"""
Investigate Potential Overfitting in Compliance-Enriched Model
Check for data leakage, memorization, and realistic performance
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json
from collections import Counter
import re

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.xgboost_classifier import XGBoostClassifier
from utils.logger import setup_logger

logger = setup_logger('overfitting_investigation')


def analyze_data_leakage():
    """Check for potential data leakage issues"""
    logger.info("Analyzing potential data leakage...")

    # Load datasets
    train_df = pd.read_csv("data/combined_compliance/compliance_events_train.csv")
    test_df = pd.read_csv("data/combined_compliance/compliance_events_test.csv")

    issues = []

    # Check 1: Log message overlap
    train_logs = set(train_df['log_message'].values)
    test_logs = set(test_df['log_message'].values)
    overlap = train_logs.intersection(test_logs)
    overlap_pct = len(overlap) / len(test_logs) * 100

    logger.info(f"Log message overlap: {len(overlap)}/{len(test_logs)} ({overlap_pct:.2f}%)")

    if overlap_pct > 5:
        issues.append({
            'issue': 'High log message overlap between train and test',
            'severity': 'CRITICAL',
            'overlap_pct': overlap_pct,
            'explanation': 'Model may have memorized exact log messages'
        })

    # Check 2: Distribution similarity (too similar = suspicious)
    train_compliance_dist = train_df['compliance_status'].value_counts(normalize=True)
    test_compliance_dist = test_df['compliance_status'].value_counts(normalize=True)

    logger.info(f"Train compliance distribution: {train_compliance_dist.to_dict()}")
    logger.info(f"Test compliance distribution: {test_compliance_dist.to_dict()}")

    # Check 3: Feature correlation with label
    # Check if any feature is a perfect predictor
    categorical_cols = ['control_id', 'control_family', 'framework', 'source', 'event_type']

    for col in categorical_cols:
        if col in train_df.columns:
            # Check if any value in this column always maps to one class
            grouped = train_df.groupby(col)['compliance_status'].apply(
                lambda x: x.value_counts(normalize=True).max()
            )
            perfect_predictors = grouped[grouped > 0.99]

            if len(perfect_predictors) > 0:
                issues.append({
                    'issue': f'Column {col} has perfect/near-perfect predictors',
                    'severity': 'HIGH',
                    'values': perfect_predictors.to_dict(),
                    'explanation': f'{len(perfect_predictors)} values in {col} predict the label with >99% accuracy'
                })

    # Check 4: Status code patterns
    if 'status_code' in train_df.columns:
        status_compliance = train_df.groupby('status_code')['compliance_status'].apply(
            lambda x: (x == 'compliant').mean()
        )

        logger.info("Status code -> compliance correlation:")
        for status, compliance_rate in status_compliance.items():
            logger.info(f"  Status {status}: {compliance_rate:.2%} compliant")

        # Check if status_code is a perfect predictor
        if any(status_compliance == 1.0) or any(status_compliance == 0.0):
            issues.append({
                'issue': 'Status code is a perfect predictor',
                'severity': 'CRITICAL',
                'explanation': 'Some status codes always map to one class - likely data leakage'
            })

    # Check 5: Temporal patterns
    if 'timestamp' in train_df.columns:
        try:
            train_df['timestamp'] = pd.to_datetime(train_df['timestamp'], format='mixed')
            test_df['timestamp'] = pd.to_datetime(test_df['timestamp'], format='mixed')

            train_date_range = (train_df['timestamp'].min(), train_df['timestamp'].max())
            test_date_range = (test_df['timestamp'].min(), test_df['timestamp'].max())

            logger.info(f"Train date range: {train_date_range}")
            logger.info(f"Test date range: {test_date_range}")

            # Check if dates overlap (temporal leakage)
            if train_date_range[1] >= test_date_range[0]:
                issues.append({
                    'issue': 'Temporal leakage: Train and test date ranges overlap',
                    'severity': 'MEDIUM',
                    'explanation': 'Model may have seen similar temporal patterns'
                })
        except Exception as e:
            logger.warning(f"Could not parse timestamps: {e}")

    return issues


def test_model_on_variations():
    """Test model on slight variations of test data"""
    logger.info("Testing model on data variations...")

    # Load model
    classifier = XGBoostClassifier()
    model_path = Path("results/models/xgboost_compliance_enriched/xgboost_model_compliance_enriched")
    classifier.load_model(str(model_path))

    # Load test data
    test_df = pd.read_csv("data/combined_compliance/compliance_events_test.csv")

    # Sample 100 random test events
    sample_df = test_df.sample(n=min(100, len(test_df)), random_state=42)

    variations = []

    # Variation 1: Slightly modify log messages (typos, case changes)
    modified_df = sample_df.copy()
    modified_df['log_message'] = modified_df['log_message'].apply(
        lambda x: x.replace('detected', 'detectd').replace('blocked', 'blcoked')  # Typos
    )

    preds1, probs1 = classifier.predict(modified_df)
    y_true = modified_df['compliance_status'].values
    accuracy1 = sum(1 for p, t in zip(preds1, y_true) if p == t) / len(y_true)

    variations.append({
        'variation': 'Typos in log messages',
        'accuracy': accuracy1,
        'description': 'Changed "detected" to "detectd", "blocked" to "blcoked"'
    })

    # Variation 2: Change IP addresses
    modified_df = sample_df.copy()
    modified_df['ip_address'] = modified_df['ip_address'].apply(
        lambda x: '10.10.10.10' if isinstance(x, str) else x
    )

    preds2, probs2 = classifier.predict(modified_df)
    accuracy2 = sum(1 for p, t in zip(preds2, y_true) if p == t) / len(y_true)

    variations.append({
        'variation': 'Changed all IPs to 10.10.10.10',
        'accuracy': accuracy2,
        'description': 'All IP addresses set to same value'
    })

    # Variation 3: Change timestamps to future
    modified_df = sample_df.copy()
    if 'timestamp' in modified_df.columns:
        try:
            modified_df['timestamp'] = pd.to_datetime(modified_df['timestamp'], format='mixed')
            modified_df['timestamp'] = modified_df['timestamp'] + pd.Timedelta(days=365)
            modified_df['hour_of_day'] = modified_df['timestamp'].dt.hour
            modified_df['day_of_week'] = modified_df['timestamp'].dt.dayofweek

            preds3, probs3 = classifier.predict(modified_df)
            accuracy3 = sum(1 for p, t in zip(preds3, y_true) if p == t) / len(y_true)

            variations.append({
                'variation': 'Future timestamps (+ 1 year)',
                'accuracy': accuracy3,
                'description': 'All timestamps shifted 1 year into future'
            })
        except Exception as e:
            logger.warning(f"Could not test timestamp variation: {e}")

    # Variation 4: Swap compliant/non-compliant keywords
    modified_df = sample_df.copy()
    modified_df['log_message'] = modified_df['log_message'].apply(
        lambda x: x.replace('denied', 'allowed').replace('blocked', 'permitted')
    )

    preds4, probs4 = classifier.predict(modified_df)
    accuracy4 = sum(1 for p, t in zip(preds4, y_true) if p == t) / len(y_true)

    variations.append({
        'variation': 'Swapped security keywords',
        'accuracy': accuracy4,
        'description': 'Changed "denied" to "allowed", "blocked" to "permitted"'
    })

    return variations


def check_feature_importance():
    """Analyze which features the model relies on most"""
    logger.info("Analyzing feature importance...")

    # Load model
    classifier = XGBoostClassifier()
    model_path = Path("results/models/xgboost_compliance_enriched/xgboost_model_compliance_enriched")
    classifier.load_model(str(model_path))

    # Get feature importance
    importance = classifier.model.feature_importances_

    # Create feature name mapping (this is approximate)
    feature_names = []
    feature_names.extend([f'tfidf_{i}' for i in range(1000)])  # TF-IDF features
    feature_names.extend(['control_id', 'control_family', 'framework',
                          'hour', 'day_of_week', 'is_business_hours',
                          'status_code', 'port', 'anomaly_label'])

    # Sort by importance
    importance_pairs = list(zip(feature_names[:len(importance)], importance))
    importance_pairs.sort(key=lambda x: x[1], reverse=True)

    top_features = importance_pairs[:20]

    suspicious_features = []
    for feat, imp in top_features:
        # Check if any non-TF-IDF feature has very high importance
        if not feat.startswith('tfidf_') and imp > 0.1:
            suspicious_features.append({
                'feature': feat,
                'importance': float(imp),
                'warning': 'High importance for non-text feature may indicate leakage'
            })

    return top_features, suspicious_features


def main():
    """Main investigation"""
    print("\n" + "="*80)
    print("OVERFITTING INVESTIGATION")
    print("="*80)
    print()

    results = {
        'data_leakage_issues': [],
        'variation_tests': [],
        'feature_importance': {},
        'suspicious_features': [],
        'overall_assessment': ''
    }

    # 1. Check data leakage
    print("1. Checking for data leakage...")
    leakage_issues = analyze_data_leakage()
    results['data_leakage_issues'] = leakage_issues

    if leakage_issues:
        print(f"\n⚠️  Found {len(leakage_issues)} potential issues:")
        for issue in leakage_issues:
            print(f"\n[{issue['severity']}] {issue['issue']}")
            print(f"  Explanation: {issue['explanation']}")
    else:
        print("✅ No obvious data leakage detected")

    # 2. Test on variations
    print("\n2. Testing model on data variations...")
    variations = test_model_on_variations()
    results['variation_tests'] = variations

    print("\nPerformance on modified data:")
    for var in variations:
        status = "✅" if var['accuracy'] > 0.9 else "⚠️" if var['accuracy'] > 0.7 else "❌"
        print(f"{status} {var['variation']}: {var['accuracy']:.2%}")
        print(f"   {var['description']}")

    # 3. Feature importance
    print("\n3. Analyzing feature importance...")
    top_features, suspicious = check_feature_importance()
    results['feature_importance'] = {
        'top_20': [(f, float(i)) for f, i in top_features],
        'suspicious': suspicious
    }

    print("\nTop 10 most important features:")
    for i, (feat, imp) in enumerate(top_features[:10], 1):
        print(f"{i:2d}. {feat:30s}: {imp:.4f}")

    if suspicious:
        print(f"\n⚠️  {len(suspicious)} suspicious features with high importance:")
        for s in suspicious:
            print(f"  - {s['feature']}: {s['importance']:.4f}")
            print(f"    {s['warning']}")

    # Overall assessment
    print("\n" + "="*80)
    print("ASSESSMENT")
    print("="*80)

    critical_issues = [i for i in leakage_issues if i['severity'] == 'CRITICAL']
    poor_variations = [v for v in variations if v['accuracy'] < 0.7]

    if critical_issues or poor_variations:
        print("\n⚠️  MODEL MAY BE OVERFITTING")
        print("\nReasons:")
        if critical_issues:
            print(f"  - {len(critical_issues)} critical data leakage issues")
        if poor_variations:
            print(f"  - Poor performance on {len(poor_variations)} variations")
        print("\nThe 100% accuracy is likely NOT realistic for production.")
        results['overall_assessment'] = 'OVERFITTING_LIKELY'
    else:
        print("\n✅ Model appears robust")
        print("The high accuracy may be due to:")
        print("  - High-quality, well-structured training data")
        print("  - Clear patterns in compliance vs non-compliance")
        print("  - Effective feature engineering")
        print("\nHowever, more adversarial testing recommended.")
        results['overall_assessment'] = 'APPEARS_ROBUST_BUT_TEST_MORE'

    # Save results
    output_file = Path("results/models/xgboost_compliance_enriched/overfitting_investigation.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nFull results saved to: {output_file}")
    print("="*80)


if __name__ == '__main__':
    main()
