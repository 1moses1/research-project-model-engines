#!/usr/bin/env python3
"""
Analyze why the enhanced model is performing worse than baseline
"""

import pandas as pd
import numpy as np
from pathlib import Path

print("="*100)
print("DATA QUALITY ANALYSIS - Enhanced vs Original")
print("="*100)
print()

# Load original synthetic data
print("1. ORIGINAL SYNTHETIC DATA (Baseline: 75% accuracy):")
print("-"*100)
try:
    orig_train = pd.read_csv("data/combined_compliance/compliance_events_train.csv")
    orig_test = pd.read_csv("data/combined_compliance/compliance_events_test.csv")

    print(f"Training: {len(orig_train):,} events")
    print(f"Test: {len(orig_test):,} events")
    print()

    print("Label Distribution (Training):")
    compliant_orig = (orig_train['compliance_status'] == 'compliant').sum()
    non_compliant_orig = (orig_train['compliance_status'] == 'non_compliant').sum()
    print(f"  Compliant: {compliant_orig:,} ({compliant_orig/len(orig_train)*100:.1f}%)")
    print(f"  Non-compliant: {non_compliant_orig:,} ({non_compliant_orig/len(orig_train)*100:.1f}%)")
    print()

    print("Framework Distribution:")
    for framework, count in orig_train['framework'].value_counts().items():
        print(f"  {framework}: {count:,} ({count/len(orig_train)*100:.1f}%)")
    print()

except Exception as e:
    print(f"Error: {e}")
    print()

# Load enhanced data
print("2. ENHANCED DATA (Current: 58.3% accuracy):")
print("-"*100)
try:
    enh_train = pd.read_csv("data/advanced_processed/enhanced_train.csv")
    enh_test = pd.read_csv("data/advanced_processed/enhanced_test.csv")

    print(f"Training: {len(enh_train):,} events")
    print(f"Test: {len(enh_test):,} events")
    print()

    print("Label Distribution (Training):")
    compliant_enh = (enh_train['compliance_status'] == 'compliant').sum()
    non_compliant_enh = (enh_train['compliance_status'] == 'non_compliant').sum()
    print(f"  Compliant: {compliant_enh:,} ({compliant_enh/len(enh_train)*100:.1f}%)")
    print(f"  Non-compliant: {non_compliant_enh:,} ({non_compliant_enh/len(enh_train)*100:.1f}%)")
    print(f"  Ratio: {compliant_enh/non_compliant_enh:.2f}:1")
    print()

    print("Framework Distribution:")
    for framework, count in enh_train['framework'].value_counts().items():
        print(f"  {framework}: {count:,} ({count/len(enh_train)*100:.1f}%)")
    print()

    print("Log Message Samples from Real Data:")
    print("-"*50)
    # NSL-KDD samples
    nsl_samples = enh_train[enh_train['framework'] == 'NIST-800-53'].head(3)
    for idx, row in nsl_samples.iterrows():
        print(f"{row['compliance_status']}: {row['log_message'][:100]}...")
    print()

except Exception as e:
    print(f"Error: {e}")
    print()

# Analysis
print("="*100)
print("ROOT CAUSE ANALYSIS:")
print("="*100)
print()

if compliant_enh/len(enh_train) > 0.80:
    print("❌ PROBLEM IDENTIFIED: SEVERE CLASS IMBALANCE")
    print()
    print(f"The enhanced dataset has {compliant_enh/len(enh_train)*100:.1f}% compliant events,")
    print("which is too high. The model learns to predict 'compliant' most of the time.")
    print()
    print("This happened because:")
    print("1. NSL-KDD dataset includes many 'normal' (compliant) traffic samples")
    print("2. We sampled 50K from NSL-KDD, most of which are 'normal'")
    print("3. The synthetic data (25% non-compliant) got diluted")
    print()
    print("SOLUTION:")
    print("- Re-process NSL-KDD to focus on attack traffic only")
    print("- Balance the dataset: 50% compliant, 50% non-compliant")
    print("- Use SMOTE or oversampling for minority class")
    print()

print("="*100)
