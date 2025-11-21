#!/usr/bin/env python3
"""
Integrate Targeted Datasets with Existing Training Data

Combines:
1. Original 88K samples (synthetic + NSL-KDD + MITRE + CISA)
2. 15K phishing emails
3. 8K insider threat scenarios
4. 7K DDoS attacks
5. 7K credential stuffing attacks

Total: ~125K training samples with better attack coverage
"""

import pandas as pd
import logging
from pathlib import Path
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_original_datasets():
    """Load original temporal-enhanced datasets"""

    logger.info("Loading original datasets...")

    train_df = pd.read_csv("data/temporal_enhanced/train_temporal_enhanced.csv")
    val_df = pd.read_csv("data/temporal_enhanced/val_temporal_enhanced.csv")
    test_df = pd.read_csv("data/temporal_enhanced/test_temporal_enhanced.csv")

    logger.info(f"  Original train: {len(train_df):,}")
    logger.info(f"  Original val:   {len(val_df):,}")
    logger.info(f"  Original test:  {len(test_df):,}")

    return train_df, val_df, test_df


def load_targeted_datasets():
    """Load all targeted attack datasets"""

    logger.info("\nLoading targeted datasets...")

    targeted_data = {}

    # Phishing
    phishing_train = pd.read_csv("data/targeted/phishing/phishing_train.csv")
    phishing_val = pd.read_csv("data/targeted/phishing/phishing_val.csv")
    phishing_test = pd.read_csv("data/targeted/phishing/phishing_test.csv")

    targeted_data['phishing'] = {
        'train': phishing_train,
        'val': phishing_val,
        'test': phishing_test
    }
    logger.info(f"  Phishing - Train: {len(phishing_train):,}, Val: {len(phishing_val):,}, Test: {len(phishing_test):,}")

    # Insider Threat
    insider_train = pd.read_csv("data/targeted/insider_threat/insider_threat_train.csv")
    insider_val = pd.read_csv("data/targeted/insider_threat/insider_threat_val.csv")
    insider_test = pd.read_csv("data/targeted/insider_threat/insider_threat_test.csv")

    targeted_data['insider_threat'] = {
        'train': insider_train,
        'val': insider_val,
        'test': insider_test
    }
    logger.info(f"  Insider Threat - Train: {len(insider_train):,}, Val: {len(insider_val):,}, Test: {len(insider_test):,}")

    # DDoS
    ddos_train = pd.read_csv("data/targeted/ddos/ddos_train.csv")
    ddos_val = pd.read_csv("data/targeted/ddos/ddos_val.csv")
    ddos_test = pd.read_csv("data/targeted/ddos/ddos_test.csv")

    targeted_data['ddos'] = {
        'train': ddos_train,
        'val': ddos_val,
        'test': ddos_test
    }
    logger.info(f"  DDoS - Train: {len(ddos_train):,}, Val: {len(ddos_val):,}, Test: {len(ddos_test):,}")

    # Credential Stuffing
    cred_train = pd.read_csv("data/targeted/credential_stuffing/credential_train.csv")
    cred_val = pd.read_csv("data/targeted/credential_stuffing/credential_val.csv")
    cred_test = pd.read_csv("data/targeted/credential_stuffing/credential_test.csv")

    targeted_data['credential_stuffing'] = {
        'train': cred_train,
        'val': cred_val,
        'test': cred_test
    }
    logger.info(f"  Credential Stuffing - Train: {len(cred_train):,}, Val: {len(cred_val):,}, Test: {len(cred_test):,}")

    return targeted_data


def align_columns(original_df, targeted_df):
    """Align columns between original and targeted datasets"""

    # Get common columns
    common_cols = set(original_df.columns) & set(targeted_df.columns)

    # Get columns only in original
    original_only = set(original_df.columns) - set(targeted_df.columns)

    # Get columns only in targeted
    targeted_only = set(targeted_df.columns) - set(original_df.columns)

    logger.debug(f"  Common columns: {len(common_cols)}")
    logger.debug(f"  Original only: {original_only}")
    logger.debug(f"  Targeted only: {targeted_only}")

    # Add missing columns to targeted data with default values
    for col in original_only:
        if col in ['hour', 'minute', 'day_of_week', 'day_of_month', 'month']:
            # Extract from timestamp
            if 'timestamp' in targeted_df.columns:
                targeted_df['timestamp'] = pd.to_datetime(targeted_df['timestamp'], errors='coerce')
                if col == 'day_of_week':
                    targeted_df[col] = targeted_df['timestamp'].dt.dayofweek
                elif col == 'day_of_month':
                    targeted_df[col] = targeted_df['timestamp'].dt.day
                else:
                    targeted_df[col] = getattr(targeted_df['timestamp'].dt, col)
        else:
            # Set to 0 or empty string
            targeted_df[col] = 0 if targeted_df.dtypes.get(col, float) in [float, int] else ''

    # Ensure same column order as original
    targeted_df = targeted_df[original_df.columns]

    return targeted_df


def integrate_datasets():
    """Integrate all datasets"""

    logger.info("\n" + "="*80)
    logger.info("INTEGRATING TARGETED DATASETS WITH ORIGINAL DATA")
    logger.info("="*80 + "\n")

    # Load original
    orig_train, orig_val, orig_test = load_original_datasets()

    # Load targeted
    targeted_data = load_targeted_datasets()

    # Combine train sets
    logger.info("\nCombining training sets...")

    train_sets = [orig_train]
    for name, data in targeted_data.items():
        aligned = align_columns(orig_train, data['train'])
        train_sets.append(aligned)
        logger.info(f"  Added {name}: {len(aligned):,} samples")

    combined_train = pd.concat(train_sets, ignore_index=True)
    combined_train = combined_train.sample(frac=1, random_state=42).reset_index(drop=True)

    logger.info(f"\n✅ Combined train: {len(combined_train):,} samples")

    # Combine validation sets
    logger.info("\nCombining validation sets...")

    val_sets = [orig_val]
    for name, data in targeted_data.items():
        aligned = align_columns(orig_val, data['val'])
        val_sets.append(aligned)
        logger.info(f"  Added {name}: {len(aligned):,} samples")

    combined_val = pd.concat(val_sets, ignore_index=True)
    combined_val = combined_val.sample(frac=1, random_state=42).reset_index(drop=True)

    logger.info(f"\n✅ Combined val: {len(combined_val):,} samples")

    # Combine test sets
    logger.info("\nCombining test sets...")

    test_sets = [orig_test]
    for name, data in targeted_data.items():
        aligned = align_columns(orig_test, data['test'])
        test_sets.append(aligned)
        logger.info(f"  Added {name}: {len(aligned):,} samples")

    combined_test = pd.concat(test_sets, ignore_index=True)
    combined_test = combined_test.sample(frac=1, random_state=42).reset_index(drop=True)

    logger.info(f"\n✅ Combined test: {len(combined_test):,} samples")

    # Save combined datasets
    output_dir = Path("data/integrated_targeted")
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"\nSaving integrated datasets to {output_dir}...")

    combined_train.to_csv(output_dir / "train_integrated.csv", index=False)
    combined_val.to_csv(output_dir / "val_integrated.csv", index=False)
    combined_test.to_csv(output_dir / "test_integrated.csv", index=False)

    logger.info("✅ Saved all integrated datasets")

    # Statistics
    logger.info("\n" + "="*80)
    logger.info("INTEGRATED DATASET STATISTICS")
    logger.info("="*80)

    logger.info(f"\nTotal samples:")
    logger.info(f"  Train: {len(orig_train):,} → {len(combined_train):,} (+{len(combined_train) - len(orig_train):,})")
    logger.info(f"  Val:   {len(orig_val):,} → {len(combined_val):,} (+{len(combined_val) - len(orig_val):,})")
    logger.info(f"  Test:  {len(orig_test):,} → {len(combined_test):,} (+{len(combined_test) - len(orig_test):,})")

    logger.info(f"\nCompliance distribution (train):")
    train_compliance = combined_train['compliance_status'].value_counts()
    for status, count in train_compliance.items():
        logger.info(f"  {status}: {count:,} ({count/len(combined_train)*100:.1f}%)")

    if 'framework' in combined_train.columns:
        logger.info(f"\nFramework distribution (train):")
        framework_dist = combined_train['framework'].value_counts().head(10)
        for framework, count in framework_dist.items():
            logger.info(f"  {framework}: {count:,}")

    if 'anomaly_type' in combined_train.columns:
        logger.info(f"\nAnomaly type distribution (train):")
        anomaly_dist = combined_train['anomaly_type'].value_counts().head(10)
        for anomaly, count in anomaly_dist.items():
            logger.info(f"  {anomaly}: {count:,}")

    # Save statistics
    stats = {
        'integration_date': datetime.now().isoformat(),
        'original_samples': {
            'train': len(orig_train),
            'val': len(orig_val),
            'test': len(orig_test)
        },
        'integrated_samples': {
            'train': len(combined_train),
            'val': len(combined_val),
            'test': len(combined_test)
        },
        'targeted_additions': {
            name: {
                'train': len(data['train']),
                'val': len(data['val']),
                'test': len(data['test'])
            }
            for name, data in targeted_data.items()
        },
        'compliance_distribution': train_compliance.to_dict(),
        'total_increase': {
            'train': len(combined_train) - len(orig_train),
            'val': len(combined_val) - len(orig_val),
            'test': len(combined_test) - len(orig_test)
        }
    }

    with open(output_dir / 'integration_statistics.json', 'w') as f:
        json.dump(stats, f, indent=2)

    logger.info(f"\n✅ Statistics saved to {output_dir}/integration_statistics.json")

    logger.info("\n" + "="*80)
    logger.info("DATASET INTEGRATION COMPLETE")
    logger.info("="*80)
    logger.info("\nNext steps:")
    logger.info("1. Generate BERT embeddings: python src/models/bert_feature_extractor.py --data-dir data/integrated_targeted")
    logger.info("2. Retrain Phase 2 model: python train_phase2_integrated.py")
    logger.info("3. Test on 12 scenarios: python test_phase2_integrated.py")
    logger.info("="*80)

    return combined_train, combined_val, combined_test


def main():
    """Main integration script"""
    train_df, val_df, test_df = integrate_datasets()

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Integrated datasets created:")
    print(f"  Train: {len(train_df):,} samples")
    print(f"  Val:   {len(val_df):,} samples")
    print(f"  Test:  {len(test_df):,} samples")
    print(f"\nLocation: data/integrated_targeted/")
    print("\nTargeted attacks added:")
    print("  ✅ Phishing emails (15K)")
    print("  ✅ Insider threats (8K)")
    print("  ✅ DDoS attacks (7K)")
    print("  ✅ Credential stuffing (7K)")
    print("\nReady for Phase 2.5 training with improved attack coverage!")
    print("="*80)


if __name__ == '__main__':
    main()
