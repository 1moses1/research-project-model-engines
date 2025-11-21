"""
Fast XGBoost Retraining with Validated Rwanda NCSA Controls

This script:
1. Validates control taxonomy
2. Generates synthetic training data with validated controls
3. Retrains XGBoost model
4. Evaluates performance
5. Saves model and metrics

Focus: XGBoost only (fast and efficient)
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import subprocess
from datetime import datetime

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(step, message):
    """Print colored step message."""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}[STEP {step}] {message}{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

def validate_controls():
    """Validate control taxonomy before proceeding."""
    print_step(1, "Validating Control Taxonomy")

    result = subprocess.run(
        ["python", "scripts/validate_control_taxonomy.py"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"{Colors.RED}❌ Control validation FAILED!{Colors.END}")
        print(result.stdout)
        print(result.stderr)
        sys.exit(1)

    print(f"{Colors.GREEN}✅ Control taxonomy validated successfully!{Colors.END}")
    return True

def generate_training_data_fast():
    """Generate training data quickly (smaller dataset for speed)."""
    print_step(2, "Generating Training Data with Validated Controls")

    from src.data_pipeline.synthetic_generator import SyntheticEventGenerator

    # Use smaller dataset for faster training
    num_train = 50000  # 50K for speed (vs 100K)
    num_val = 10000    # 10K validation
    num_test = 10000   # 10K test

    print(f"Generating {num_train + num_val + num_test} total events...")
    print(f"  - Training: {num_train}")
    print(f"  - Validation: {num_val}")
    print(f"  - Test: {num_test}")

    # Initialize generator with VALIDATED taxonomy
    generator = SyntheticEventGenerator(
        control_taxonomy_path="data/processed/control_taxonomy_validated.json",
        output_dir="data/validated_synthetic"
    )

    # Generate datasets
    print("\nGenerating complete dataset...")
    total_events = num_train + num_val + num_test

    # Generate single dataset and split
    all_events = generator.generate_dataset(num_events=total_events)

    # Split into train/val/test
    print("Splitting into train/val/test...")
    train_events = all_events.iloc[:num_train]
    val_events = all_events.iloc[num_train:num_train+num_val]
    test_events = all_events.iloc[num_train+num_val:]

    # Save datasets
    output_dir = Path("data/validated_synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)

    train_path = output_dir / "train_validated.csv"
    val_path = output_dir / "val_validated.csv"
    test_path = output_dir / "test_validated.csv"

    print("\nSaving datasets...")
    train_events.to_csv(train_path, index=False)
    val_events.to_csv(val_path, index=False)
    test_events.to_csv(test_path, index=False)

    print(f"{Colors.GREEN}✅ Training data generated successfully!{Colors.END}")
    print(f"  - Train: {train_path} ({len(train_events):,} events)")
    print(f"  - Val: {val_path} ({len(val_events):,} events)")
    print(f"  - Test: {test_path} ({len(test_events):,} events)")

    return train_path, val_path, test_path

def train_xgboost(train_path, val_path):
    """Train XGBoost model with validated data."""
    print_step(3, "Training XGBoost Model")

    import xgboost as xgb
    from sklearn.preprocessing import LabelEncoder
    from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

    # Load data
    print("Loading training data...")
    train_df = pd.read_csv(train_path)
    val_df = pd.read_csv(val_path)

    # Feature engineering
    print("Engineering features...")

    # Get all numeric columns from the data (auto-detect)
    numeric_cols = train_df.select_dtypes(include=[np.number]).columns.tolist()

    # Exclude target variables and IDs
    exclude_cols = ['event_id', 'compliance_status', 'anomaly_label']
    available_features = [col for col in numeric_cols if col not in exclude_cols]

    # If no numeric features, use basic ones
    if not available_features:
        available_features = ['hour_of_day', 'is_business_hours']

    print(f"Using {len(available_features)} features: {available_features}")

    X_train = train_df[available_features].fillna(0)
    X_val = val_df[available_features].fillna(0)

    # Convert all columns to numeric (XGBoost requirement)
    X_train = X_train.apply(pd.to_numeric, errors='coerce').fillna(0)
    X_val = X_val.apply(pd.to_numeric, errors='coerce').fillna(0)

    # Encode labels
    le = LabelEncoder()
    y_train = le.fit_transform(train_df['compliance_status'])
    y_val = le.transform(val_df['compliance_status'])

    print(f"\nTraining XGBoost on {len(X_train):,} samples...")
    print(f"Features: {len(available_features)}")
    print(f"Classes: {list(le.classes_)}")

    # Train XGBoost (balanced speed and performance)
    model = xgb.XGBClassifier(
        n_estimators=200,       # Increased for better performance
        max_depth=8,            # Deeper trees
        learning_rate=0.05,     # Lower learning rate for stability
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=3,     # Handle imbalanced data (75%/25%)
        objective='binary:logistic',
        random_state=42,
        n_jobs=-1,              # Use all cores
        tree_method='hist'       # Faster training
    )

    print("\nTraining in progress...")
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )

    # Evaluate
    y_pred = model.predict(X_val)
    accuracy = accuracy_score(y_val, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_val, y_pred, average='binary')

    print(f"\n{Colors.GREEN}✅ XGBoost training complete!{Colors.END}")
    print(f"\nValidation Performance:")
    print(f"  - Accuracy: {accuracy:.4f}")
    print(f"  - Precision: {precision:.4f}")
    print(f"  - Recall: {recall:.4f}")
    print(f"  - F1-Score: {f1:.4f}")

    # Save model
    model_dir = Path("models/validated")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "xgboost_validated.json"
    model.save_model(model_path)

    # Save label encoder
    import pickle
    le_path = model_dir / "label_encoder.pkl"
    with open(le_path, 'wb') as f:
        pickle.dump(le, f)

    # Save feature list
    feature_path = model_dir / "features.json"
    with open(feature_path, 'w') as f:
        json.dump({'features': available_features}, f, indent=2)

    print(f"\n{Colors.GREEN}✅ Model saved to: {model_path}{Colors.END}")

    return model, le, available_features, {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1': f1
    }

def evaluate_on_test(model, le, features, test_path):
    """Evaluate model on test set."""
    print_step(4, "Evaluating on Test Set")

    from sklearn.metrics import classification_report, confusion_matrix
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Load test data
    test_df = pd.read_csv(test_path)

    X_test = test_df[features].fillna(0)

    # Convert all columns to numeric
    X_test = X_test.apply(pd.to_numeric, errors='coerce').fillna(0)

    y_test = le.transform(test_df['compliance_status'])

    # Predict
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Metrics
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=le.classes_, yticklabels=le.classes_)
    plt.title('XGBoost Confusion Matrix (Validated Controls)')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')

    output_dir = Path("results/validated")
    output_dir.mkdir(parents=True, exist_ok=True)

    cm_path = output_dir / "xgboost_confusion_matrix.png"
    plt.savefig(cm_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"\n{Colors.GREEN}✅ Confusion matrix saved to: {cm_path}{Colors.END}")

    # Save metrics
    from sklearn.metrics import accuracy_score, precision_recall_fscore_support

    accuracy = accuracy_score(y_test, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_test, y_pred, average='binary')

    metrics = {
        'model': 'XGBoost',
        'framework': 'Rwanda NCSA (PRIMARY) + NIST (SECONDARY)',
        'validated': True,
        'validation_date': datetime.now().strftime('%Y-%m-%d'),
        'test_metrics': {
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1': float(f1)
        },
        'training_samples': len(pd.read_csv(test_path.parent / "train_validated.csv")),
        'test_samples': len(test_df)
    }

    metrics_path = output_dir / "xgboost_validated_metrics.json"
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)

    print(f"{Colors.GREEN}✅ Metrics saved to: {metrics_path}{Colors.END}")

    return metrics

def main():
    """Main execution function."""
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BLUE}XGBoost Retraining with Validated Rwanda NCSA Controls{Colors.END}")
    print(f"{Colors.BLUE}{'='*80}{Colors.END}\n")

    start_time = datetime.now()

    try:
        # Step 1: Validate controls
        validate_controls()

        # Step 2: Generate training data
        train_path, val_path, test_path = generate_training_data_fast()

        # Step 3: Train XGBoost
        model, le, features, val_metrics = train_xgboost(train_path, val_path)

        # Step 4: Evaluate on test set
        test_metrics = evaluate_on_test(model, le, features, test_path)

        # Final summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n{Colors.GREEN}{'='*80}{Colors.END}")
        print(f"{Colors.GREEN}✅ XGBOOST RETRAINING COMPLETE!{Colors.END}")
        print(f"{Colors.GREEN}{'='*80}{Colors.END}\n")

        print("Summary:")
        print(f"  - Duration: {duration:.1f} seconds")
        print(f"  - Model: XGBoost (validated controls)")
        print(f"  - Framework: Rwanda NCSA (PRIMARY) + NIST (SECONDARY)")
        print(f"  - Test Accuracy: {test_metrics['test_metrics']['accuracy']:.4f}")
        print(f"  - Test F1-Score: {test_metrics['test_metrics']['f1']:.4f}")
        print(f"\nModel saved to: models/validated/xgboost_validated.json")
        print(f"Metrics saved to: results/validated/xgboost_validated_metrics.json")

        print(f"\n{Colors.GREEN}Next steps:{Colors.END}")
        print("  1. Review metrics: results/validated/xgboost_validated_metrics.json")
        print("  2. Update K8s deployment with new model")
        print("  3. Test with: python test_k8s_compliance.py")

    except Exception as e:
        print(f"\n{Colors.RED}{'='*80}{Colors.END}")
        print(f"{Colors.RED}❌ ERROR: {str(e)}{Colors.END}")
        print(f"{Colors.RED}{'='*80}{Colors.END}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
