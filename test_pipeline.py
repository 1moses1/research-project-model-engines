"""
Quick test script for data pipeline components.
Run this after installing dependencies to verify everything works.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

def test_config_loader():
    """Test configuration loader."""
    print("\n" + "="*60)
    print("Testing Configuration Loader...")
    print("="*60)

    try:
        from utils.config_loader import ConfigLoader

        loader = ConfigLoader()
        data_config = loader.load_data_config()
        model_config = loader.load_model_config()

        nist_controls = loader.get_nist_controls()
        rwanda_controls = loader.get_rwanda_controls()

        print(f"✅ Data config loaded: {len(data_config)} keys")
        print(f"✅ Model config loaded: {len(model_config)} keys")
        print(f"✅ NIST controls: {len(nist_controls)}")
        print(f"✅ Rwanda controls: {len(rwanda_controls)}")

        return True
    except Exception as e:
        print(f"❌ Config loader failed: {e}")
        return False


def test_logger():
    """Test logger utility."""
    print("\n" + "="*60)
    print("Testing Logger...")
    print("="*60)

    try:
        from utils.logger import setup_logger

        logger = setup_logger("test", "logs/test.log")
        logger.info("Test log message")

        print("✅ Logger works!")
        return True
    except Exception as e:
        print(f"❌ Logger failed: {e}")
        return False


def test_control_mapper():
    """Test control mapper."""
    print("\n" + "="*60)
    print("Testing Control Mapper...")
    print("="*60)

    try:
        from data_pipeline.control_mapper import ControlMapper

        mapper = ControlMapper()
        taxonomy = mapper.create_control_taxonomy()

        print(f"✅ Total controls: {taxonomy['metadata']['total_controls']}")
        print(f"✅ NIST controls: {taxonomy['metadata']['nist_controls']}")
        print(f"✅ Rwanda controls: {taxonomy['metadata']['rwanda_controls']}")
        print(f"✅ Control families: {len(taxonomy['control_families'])}")

        # Save taxonomy
        output_path = mapper.save_control_taxonomy()
        print(f"✅ Taxonomy saved to: {output_path}")

        return True
    except Exception as e:
        print(f"❌ Control mapper failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_synthetic_generator():
    """Test synthetic event generator."""
    print("\n" + "="*60)
    print("Testing Synthetic Event Generator...")
    print("="*60)

    try:
        from data_pipeline.synthetic_generator import SyntheticEventGenerator
        from datetime import datetime

        generator = SyntheticEventGenerator()

        # Generate small test dataset
        print("Generating 1000 test events...")
        df = generator.generate_dataset(num_events=1000)

        print(f"✅ Generated {len(df)} events")
        print(f"✅ Columns: {list(df.columns)}")
        print(f"\nSample event:")
        print(df.iloc[0].to_dict())

        # Test split
        train_df, val_df, test_df = generator.split_dataset(df)
        print(f"\n✅ Split complete:")
        print(f"  Train: {len(train_df)}")
        print(f"  Val: {len(val_df)}")
        print(f"  Test: {len(test_df)}")

        return True
    except Exception as e:
        print(f"❌ Synthetic generator failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print(" COMPLIANCE ML PIPELINE - COMPONENT TESTS")
    print("="*70)

    results = {}

    # Test each component
    results['config_loader'] = test_config_loader()
    results['logger'] = test_logger()
    results['control_mapper'] = test_control_mapper()
    results['synthetic_generator'] = test_synthetic_generator()

    # Summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)

    for component, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {component}")

    all_passed = all(results.values())

    print("\n" + "="*70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
    else:
        print("⚠️  SOME TESTS FAILED - Check errors above")
    print("="*70 + "\n")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
