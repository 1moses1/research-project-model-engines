"""
Generate Full Training Dataset with All 196 Validated Controls

This script regenerates the training dataset with complete coverage
of all 196 government-validated controls (169 Rwanda NCSA + 27 NIST).

Previous dataset: 50 controls, 70K events (25.5% coverage)
New dataset: 196 controls, 100K events (100% coverage)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src"))

from data_pipeline.synthetic_generator import SyntheticEventGenerator
from utils.logger import setup_logger
import time

def main():
    logger = setup_logger("full_training_generation", "logs/training_generation.log")

    print("=" * 80)
    print("GENERATING FULL TRAINING DATASET - 196 CONTROLS")
    print("=" * 80)
    print()

    # Initialize generator with validated taxonomy
    print("📥 Loading validated control taxonomy...")
    generator = SyntheticEventGenerator(
        control_taxonomy_path="data/processed/control_taxonomy_validated.json",
        output_dir="data/synthetic"
    )

    print(f"✅ Loaded {len(generator.all_controls)} validated controls")
    print(f"   Rwanda NCSA: {len(generator.rwanda_controls)} controls")
    print(f"   NIST SP 800-53: {len(generator.nist_controls)} controls")
    print()

    # Generate 100K events
    print("🔄 Generating 100,000 compliance events...")
    print("   This will take approximately 2-3 minutes...")
    print()

    start_time = time.time()

    # Generate full dataset
    df = generator.generate_dataset(num_events=100_000)

    # Split into train/val/test
    train_df, val_df, test_df = generator.split_dataset(
        df,
        train_ratio=0.70,
        val_ratio=0.15,
        test_ratio=0.15
    )

    # Save datasets
    train_df.to_csv('data/synthetic/compliance_events_train.csv', index=False)
    val_df.to_csv('data/synthetic/compliance_events_val.csv', index=False)
    test_df.to_csv('data/synthetic/compliance_events_test.csv', index=False)

    # Generate statistics
    import json
    stats = {
        'total_events': int(len(df)),
        'train_events': int(len(train_df)),
        'val_events': int(len(val_df)),
        'test_events': int(len(test_df)),
        'unique_controls': int(df['control_id'].nunique()),
        'compliant_events': int((df['compliance_status'] == 'compliant').sum()),
        'non_compliant_events': int((df['compliance_status'] == 'non_compliant').sum()),
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    with open('data/synthetic/dataset_statistics.json', 'w') as f:
        json.dump(stats, f, indent=2)

    elapsed = time.time() - start_time

    print()
    print("=" * 80)
    print("GENERATION COMPLETE")
    print("=" * 80)
    print()
    print(f"⏱️  Time elapsed: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
    print()
    print("📊 Dataset Statistics:")
    print(f"   Total events: {stats['total_events']:,}")
    print(f"   Training: {stats['train_events']:,} (70%)")
    print(f"   Validation: {stats['val_events']:,} (15%)")
    print(f"   Test: {stats['test_events']:,} (15%)")
    print()
    print(f"   Unique controls: {stats.get('unique_controls', len(generator.all_controls))}")
    print(f"   Expected: 196 controls")
    print(f"   Coverage: {stats.get('unique_controls', len(generator.all_controls))/196*100:.1f}%")
    print()
    print(f"   Compliant events: {stats.get('compliant_events', 'N/A'):,}")
    print(f"   Non-compliant events: {stats.get('non_compliant_events', 'N/A'):,}")
    print()
    print("📁 Output files:")
    print(f"   ✅ data/synthetic/compliance_events_train.csv")
    print(f"   ✅ data/synthetic/compliance_events_val.csv")
    print(f"   ✅ data/synthetic/compliance_events_test.csv")
    print(f"   ✅ data/synthetic/dataset_statistics.json")
    print()
    print("🎯 Next step: Retrain XGBoost model with new dataset")
    print("   Command: python train_all_models.py")
    print()
    print("=" * 80)
    print("✅ SUCCESS - Ready for model training!")
    print("=" * 80)


if __name__ == "__main__":
    main()
