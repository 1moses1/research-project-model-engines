#!/bin/bash

echo "=========================================="
echo "CLEANING UP OUT-OF-SCOPE DATASETS"
echo "=========================================="

# Create archive directory for backup
mkdir -p archive/out_of_scope_datasets
timestamp=$(date +%Y%m%d_%H%M%S)

echo ""
echo "📦 Archiving out-of-scope datasets..."

# Archive attack-focused datasets
datasets_to_archive=(
    "data/targeted"
    "data/integrated_targeted"
    "data/advanced_datasets"
    "data/advanced_processed"
    "data/bert_embeddings"
    "data/bert_embeddings_integrated"
    "data/combined_compliance"
    "data/compliance_enriched"
    "data/temporal_enhanced"
    "data/security_feeds"
)

for dataset in "${datasets_to_archive[@]}"; do
    if [ -d "$dataset" ]; then
        echo "  Moving: $dataset → archive/out_of_scope_datasets/"
        mv "$dataset" "archive/out_of_scope_datasets/"
    fi
done

echo ""
echo "✅ Archived out-of-scope datasets"

echo ""
echo "📊 Remaining datasets (COMPLIANCE-FOCUSED):"
echo ""
ls -lh data/

echo ""
echo "=========================================="
echo "CLEANUP COMPLETE"
echo "=========================================="
echo ""
echo "✅ KEPT (Compliance Auditing - Proposal Aligned):"
echo "   • data/validated_synthetic/     - Rwanda NCSA compliance events (70K)"
echo "   • data/public/                  - LogHub logs (BGL, HDFS, Apache)"
echo "   • data/real/                    - Processed LogHub compliance format"
echo "   • data/real_formatted/          - Formatted compliance events"
echo "   • data/public_formatted/        - Public dataset compliance format"
echo "   • data/synthetic/               - Original synthetic (old controls)"
echo "   • data/processed/               - Control taxonomies"
echo ""
echo "🗄️  ARCHIVED (Out of Scope):"
echo "   • data/targeted/                - Attack datasets (phishing, DDoS, etc.)"
echo "   • data/integrated_targeted/     - Mixed attack/compliance data"
echo "   • data/advanced_*               - Advanced features (not in proposal)"
echo "   • data/bert_embeddings*/        - Old BERT embeddings"
echo "   • data/temporal_enhanced/       - Temporal features (not in proposal)"
echo "   • data/security_feeds/          - Threat intel feeds"
echo ""
echo "Location: archive/out_of_scope_datasets/"
echo ""
