#!/usr/bin/env python3
"""
Retrain XGBoost Model with Compliance-Enriched Data
Combines original synthetic data with MITRE ATT&CK, OWASP, CIS, PCI DSS data
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from models.xgboost_classifier import XGBoostClassifier
from utils.logger import setup_logger

logger = setup_logger('retrain_xgboost')


def load_original_datasets() -> pd.DataFrame:
    """Load original synthetic datasets"""
    logger.info("Loading original synthetic datasets...")

    datasets = []
    data_dir = Path("data/synthetic")

    # Load train, val, test sets
    for split in ['train', 'val', 'test']:
        file_path = data_dir / f"compliance_events_{split}.csv"
        if file_path.exists():
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} events from {split} set")
            datasets.append(df)
        else:
            logger.warning(f"File not found: {file_path}")

    if not datasets:
        logger.error("No original datasets found")
        return pd.DataFrame()

    combined = pd.concat(datasets, ignore_index=True)
    logger.info(f"Total original events: {len(combined)}")

    return combined


def load_compliance_enriched_dataset() -> pd.DataFrame:
    """Load compliance-enriched dataset"""
    logger.info("Loading compliance-enriched dataset...")

    file_path = Path("data/compliance_enriched/compliance_enriched_dataset.csv")

    if not file_path.exists():
        logger.error(f"Compliance dataset not found: {file_path}")
        return pd.DataFrame()

    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} compliance-enriched events")

    return df


def align_datasets(original_df: pd.DataFrame, enriched_df: pd.DataFrame) -> pd.DataFrame:
    """
    Align enriched dataset to match original dataset schema

    Args:
        original_df: Original synthetic dataset
        enriched_df: Compliance-enriched dataset

    Returns:
        Aligned enriched dataset
    """
    logger.info("Aligning dataset schemas...")

    # Get required columns from original dataset
    required_columns = original_df.columns.tolist()

    # Parse timestamps and add temporal features
    if 'timestamp' in enriched_df.columns:
        enriched_df['timestamp'] = pd.to_datetime(enriched_df['timestamp'])
        enriched_df['hour_of_day'] = enriched_df['timestamp'].dt.hour
        enriched_df['day_of_week'] = enriched_df['timestamp'].dt.dayofweek
        enriched_df['is_business_hours'] = (
            (enriched_df['hour_of_day'] >= 8) &
            (enriched_df['hour_of_day'] <= 17) &
            (enriched_df['day_of_week'] < 5)
        ).astype(int)

    # Ensure enriched dataset has all required columns
    for col in required_columns:
        if col not in enriched_df.columns:
            # Add missing columns with default values
            if col == 'severity':
                enriched_df[col] = enriched_df.get('anomaly_type', 'normal')
            elif col == 'hour_of_day':
                enriched_df[col] = 12  # Default to noon
            elif col == 'day_of_week':
                enriched_df[col] = 2  # Default to Wednesday
            elif col == 'is_business_hours':
                enriched_df[col] = 1  # Default to business hours
            elif col == 'port':
                enriched_df[col] = 443  # Default to HTTPS
            elif col == 'control_family':
                # Map control_id to control_family
                control_family_map = {
                    'AC-3': 'Access Control', 'AC-6': 'Access Control',
                    'AU-2': 'Audit and Accountability', 'AU-6': 'Audit and Accountability',
                    'CM-3': 'Configuration Management', 'CM-6': 'Configuration Management',
                    'CM-7': 'Configuration Management', 'CM-8': 'Configuration Management',
                    'IA-2': 'Identification and Authentication', 'IA-5': 'Identification and Authentication',
                    'IR-4': 'Incident Response',
                    'PE-3': 'Physical and Environmental Protection',
                    'PL-1': 'Planning',
                    'RA-5': 'Risk Assessment',
                    'SA-11': 'System and Services Acquisition', 'SA-15': 'System and Services Acquisition',
                    'SC-7': 'System and Communications Protection', 'SC-13': 'System and Communications Protection',
                    'SC-28': 'System and Communications Protection',
                    'SI-2': 'System and Information Integrity', 'SI-3': 'System and Information Integrity',
                    'SI-4': 'System and Information Integrity', 'SI-10': 'System and Information Integrity',
                    'CA-7': 'Assessment, Authorization, and Monitoring'
                }
                enriched_df[col] = enriched_df['control_id'].map(control_family_map).fillna('System and Information Integrity')
            elif col == 'framework':
                # Determine framework from source
                enriched_df[col] = enriched_df['source'].apply(lambda x:
                    'MITRE ATT&CK' if 'mitre' in x.lower() else
                    'OWASP' if 'owasp' in x.lower() else
                    'CIS' if 'cis' in x.lower() else
                    'PCI DSS' if 'pci' in x.lower() else
                    'NIST NVD' if 'nvd' in x.lower() else
                    'NIST SP 800-53'
                )
            elif col == 'anomaly_label':
                # Map anomaly_type to anomaly_label
                enriched_df[col] = enriched_df.get('anomaly_type', 'normal')
            elif col in ['timestamp', 'log_message', 'source', 'event_type', 'control_id',
                         'user', 'ip_address', 'resource', 'status_code',
                         'compliance_status', 'anomaly_type', 'description']:
                # These columns should already exist
                if col not in enriched_df.columns:
                    enriched_df[col] = 'unknown'
            else:
                # Generic default
                enriched_df[col] = ''

    # Fill any remaining NaN values
    for col in required_columns:
        if enriched_df[col].dtype == 'object':
            enriched_df[col] = enriched_df[col].fillna('unknown')
        else:
            enriched_df[col] = enriched_df[col].fillna(0)

    # Select only required columns in the same order
    enriched_df = enriched_df[required_columns]

    logger.info("Schema alignment complete")
    logger.info(f"Aligned {len(enriched_df)} enriched events")

    return enriched_df


def combine_datasets(original_df: pd.DataFrame, enriched_df: pd.DataFrame,
                     enrichment_ratio: float = 0.3) -> pd.DataFrame:
    """
    Combine original and enriched datasets

    Args:
        original_df: Original synthetic dataset
        enriched_df: Compliance-enriched dataset
        enrichment_ratio: Ratio of enriched data to add (0.3 = 30% enriched, 70% original)

    Returns:
        Combined dataset
    """
    logger.info(f"Combining datasets with enrichment ratio: {enrichment_ratio}")

    # Calculate target sizes
    total_original = len(original_df)
    target_enriched = int(total_original * enrichment_ratio)

    # Sample enriched dataset if it's larger than needed
    if len(enriched_df) > target_enriched:
        enriched_sample = enriched_df.sample(n=target_enriched, random_state=42)
        logger.info(f"Sampled {target_enriched} events from enriched dataset")
    else:
        enriched_sample = enriched_df
        logger.info(f"Using all {len(enriched_df)} enriched events")

    # Combine datasets
    combined = pd.concat([original_df, enriched_sample], ignore_index=True)

    # Shuffle
    combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)

    logger.info(f"Combined dataset size: {len(combined)} events")
    logger.info(f"  - Original: {len(original_df)} ({len(original_df)/len(combined)*100:.1f}%)")
    logger.info(f"  - Enriched: {len(enriched_sample)} ({len(enriched_sample)/len(combined)*100:.1f}%)")

    return combined


def split_dataset(df: pd.DataFrame, train_ratio: float = 0.7,
                  val_ratio: float = 0.15) -> tuple:
    """
    Split dataset into train/val/test sets

    Args:
        df: Combined dataset
        train_ratio: Training set ratio
        val_ratio: Validation set ratio

    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    logger.info(f"Splitting dataset (train={train_ratio}, val={val_ratio}, test={1-train_ratio-val_ratio})")

    # Calculate split indices
    n = len(df)
    train_idx = int(n * train_ratio)
    val_idx = int(n * (train_ratio + val_ratio))

    # Split
    train_df = df[:train_idx].copy()
    val_df = df[train_idx:val_idx].copy()
    test_df = df[val_idx:].copy()

    logger.info(f"Train set: {len(train_df)} events")
    logger.info(f"Val set: {len(val_df)} events")
    logger.info(f"Test set: {len(test_df)} events")

    return train_df, val_df, test_df


def save_combined_datasets(train_df: pd.DataFrame, val_df: pd.DataFrame,
                           test_df: pd.DataFrame, output_dir: Path):
    """Save combined datasets"""
    logger.info(f"Saving combined datasets to {output_dir}...")

    output_dir.mkdir(parents=True, exist_ok=True)

    # Save datasets
    train_df.to_csv(output_dir / "compliance_events_train.csv", index=False)
    val_df.to_csv(output_dir / "compliance_events_val.csv", index=False)
    test_df.to_csv(output_dir / "compliance_events_test.csv", index=False)

    logger.info("✅ Datasets saved successfully")


def train_xgboost_model(train_data_path: Path, output_dir: Path) -> dict:
    """
    Train XGBoost model with compliance-enriched data

    Args:
        train_data_path: Path to training data directory
        output_dir: Output directory for model and results

    Returns:
        Training metrics
    """
    logger.info("Training XGBoost model with compliance-enriched data...")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize classifier
    classifier = XGBoostClassifier()

    # Load training and validation data
    train_file = train_data_path / "compliance_events_train.csv"
    val_file = train_data_path / "compliance_events_val.csv"

    if not train_file.exists():
        logger.error(f"Training file not found: {train_file}")
        return {}

    if not val_file.exists():
        logger.error(f"Validation file not found: {val_file}")
        return {}

    logger.info(f"Loading training data from {train_file}")
    train_df = pd.read_csv(train_file)

    logger.info(f"Loading validation data from {val_file}")
    val_df = pd.read_csv(val_file)

    # Prepare features and labels
    logger.info("Preparing features...")

    # Fit feature engineer on training data
    classifier.feature_engineer.fit(train_df)

    # Transform training data
    X_train = classifier.feature_engineer.transform(train_df)
    y_train = train_df['compliance_status'].map({'compliant': 0, 'non_compliant': 1}).values

    # Transform validation data
    X_val = classifier.feature_engineer.transform(val_df)
    y_val = val_df['compliance_status'].map({'compliant': 0, 'non_compliant': 1}).values

    logger.info(f"Training set: {X_train.shape}")
    logger.info(f"Validation set: {X_val.shape}")

    # Train model
    logger.info("Starting model training...")
    history = classifier.train(X_train, y_train, X_val, y_val, early_stopping_rounds=50)

    # Save model
    model_path = output_dir / "xgboost_model_compliance_enriched"
    classifier.save_model(str(model_path))
    logger.info(f"✅ Model saved to {model_path}")

    # Evaluate on validation set
    logger.info("Evaluating on validation set...")
    predictions, probabilities = classifier.predict(val_df)

    # Calculate metrics
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

    y_pred = [1 if p == 'non_compliant' else 0 for p in predictions]

    # Confusion matrix
    cm = confusion_matrix(y_val, y_pred)
    tn, fp, fn, tp = cm.ravel()

    metrics = {
        'accuracy': float(accuracy_score(y_val, y_pred)),
        'precision': float(precision_score(y_val, y_pred, zero_division=0)),
        'recall': float(recall_score(y_val, y_pred, zero_division=0)),
        'f1_score': float(f1_score(y_val, y_pred, zero_division=0)),
        'avg_confidence': float(np.mean(probabilities)),
        'true_positives': int(tp),
        'false_positives': int(fp),
        'true_negatives': int(tn),
        'false_negatives': int(fn)
    }

    logger.info("Validation Metrics:")
    logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
    logger.info(f"  Precision: {metrics['precision']:.4f}")
    logger.info(f"  Recall: {metrics['recall']:.4f}")
    logger.info(f"  F1 Score: {metrics['f1_score']:.4f}")
    logger.info(f"  False Negatives: {metrics['false_negatives']}")
    logger.info(f"  False Positives: {metrics['false_positives']}")

    # Save metrics
    metrics_file = output_dir / "compliance_enriched_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"✅ Metrics saved to {metrics_file}")

    return metrics


def main():
    """Main entry point"""
    print("\n" + "="*80)
    print("XGBOOST RETRAINING WITH COMPLIANCE-ENRICHED DATA")
    print("="*80)
    print()

    # Create output directories
    combined_data_dir = Path("data/combined_compliance")
    model_output_dir = Path("results/models/xgboost_compliance_enriched")

    # Step 1: Load datasets
    print("Step 1: Loading datasets...")
    original_df = load_original_datasets()
    enriched_df = load_compliance_enriched_dataset()

    if original_df.empty:
        logger.error("Failed to load original dataset")
        return

    if enriched_df.empty:
        logger.warning("No enriched dataset available, using only original data")
        combined_df = original_df
    else:
        # Step 2: Align schemas
        print("\nStep 2: Aligning dataset schemas...")
        enriched_df = align_datasets(original_df, enriched_df)

        # Step 3: Combine datasets
        print("\nStep 3: Combining datasets...")
        combined_df = combine_datasets(original_df, enriched_df, enrichment_ratio=0.3)

    # Step 4: Split dataset
    print("\nStep 4: Splitting into train/val/test sets...")
    train_df, val_df, test_df = split_dataset(combined_df)

    # Step 5: Save combined datasets
    print("\nStep 5: Saving combined datasets...")
    save_combined_datasets(train_df, val_df, test_df, combined_data_dir)

    # Step 6: Train model
    print("\nStep 6: Training XGBoost model...")
    metrics = train_xgboost_model(combined_data_dir, model_output_dir)

    # Summary
    print("\n" + "="*80)
    print("TRAINING COMPLETE")
    print("="*80)
    print(f"Combined dataset: {len(combined_df)} events")
    print(f"Training set: {len(train_df)} events")
    print(f"Validation set: {len(val_df)} events")
    print(f"Test set: {len(test_df)} events")
    print()

    if metrics:
        print("Validation Performance:")
        print(f"  Accuracy: {metrics['accuracy']:.2%}")
        print(f"  Precision: {metrics['precision']:.2%}")
        print(f"  Recall: {metrics['recall']:.2%}")
        print(f"  F1 Score: {metrics['f1_score']:.2%}")
        print()

    print(f"Model saved to: {model_output_dir}")
    print(f"Combined datasets saved to: {combined_data_dir}")
    print("="*80)


if __name__ == '__main__':
    main()
