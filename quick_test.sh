#!/bin/bash

# Quick test script for data pipeline validation
# Run this after installing dependencies

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   AI-Driven Compliance Auditing - Quick Pipeline Test         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "   Please run: source venv/bin/activate"
    echo ""
    exit 1
fi

echo "✅ Virtual environment: activated"
echo ""

# Test 1: Config Loader
echo "─────────────────────────────────────────────────────────────────"
echo "Test 1: Configuration Loader"
echo "─────────────────────────────────────────────────────────────────"
python -c "
from src.utils.config_loader import ConfigLoader
loader = ConfigLoader()
print('✅ Config loader works!')
print(f'   NIST controls: {len(loader.get_nist_controls())}')
print(f'   Rwanda controls: {len(loader.get_rwanda_controls())}')
" || exit 1
echo ""

# Test 2: Logger
echo "─────────────────────────────────────────────────────────────────"
echo "Test 2: Logger"
echo "─────────────────────────────────────────────────────────────────"
python -c "
from src.utils.logger import setup_logger
logger = setup_logger('quick_test')
logger.info('✅ Logger works!')
" || exit 1
echo ""

# Test 3: Control Mapper
echo "─────────────────────────────────────────────────────────────────"
echo "Test 3: Control Mapper (Generating Taxonomy...)"
echo "─────────────────────────────────────────────────────────────────"
python -c "
from src.data_pipeline.control_mapper import ControlMapper
mapper = ControlMapper()
output_path = mapper.save_control_taxonomy()
print(f'✅ Taxonomy saved: {output_path}')
" || exit 1
echo ""

# Test 4: Synthetic Generator (Small)
echo "─────────────────────────────────────────────────────────────────"
echo "Test 4: Synthetic Generator (1,000 events)"
echo "─────────────────────────────────────────────────────────────────"
python -c "
from src.data_pipeline.synthetic_generator import SyntheticEventGenerator
import warnings
warnings.filterwarnings('ignore')

generator = SyntheticEventGenerator()
df = generator.generate_dataset(num_events=1000)

print(f'✅ Generated {len(df)} events')
print(f'   Columns: {len(df.columns)}')
print(f'   Compliant: {(df[\"compliance_status\"] == \"compliant\").sum()}')
print(f'   Non-compliant: {(df[\"compliance_status\"] == \"non_compliant\").sum()}')

# Test split
train_df, val_df, test_df = generator.split_dataset(df)
print(f'✅ Split complete: {len(train_df)}/{len(val_df)}/{len(test_df)}')
" || exit 1
echo ""

# Summary
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      ✅ ALL TESTS PASSED!                       ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Pipeline Status: READY"
echo ""
echo "Next Steps:"
echo "  1. Generate full dataset: python src/data_pipeline/synthetic_generator.py"
echo "  2. Run comprehensive tests: python test_pipeline.py"
echo "  3. Proceed to baseline models (Phase 5)"
echo ""
