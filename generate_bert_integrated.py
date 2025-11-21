#!/usr/bin/env python3
"""
Generate BERT Embeddings for Integrated Dataset
Now with 114K training samples
"""

from src.models.bert_feature_extractor import BERTFeatureExtractor
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("="*80)
    logger.info("GENERATING BERT EMBEDDINGS FOR INTEGRATED DATASET")
    logger.info("="*80)

    # Load datasets
    logger.info("\nLoading integrated datasets...")
    train_df = pd.read_csv('data/integrated_targeted/train_integrated.csv')
    val_df = pd.read_csv('data/integrated_targeted/val_integrated.csv')
    test_df = pd.read_csv('data/integrated_targeted/test_integrated.csv')

    logger.info(f'  Train: {len(train_df):,} samples')
    logger.info(f'  Val:   {len(val_df):,} samples')
    logger.info(f'  Test:  {len(test_df):,} samples')
    logger.info(f'  Total: {len(train_df) + len(val_df) + len(test_df):,} samples')

    # Initialize BERT
    logger.info("\nInitializing BERT feature extractor...")
    bert = BERTFeatureExtractor()

    # Extract embeddings
    logger.info("\n" + "-"*80)
    logger.info("Extracting train embeddings (114K samples - may take 5-10 min)...")
    logger.info("-"*80)
    train_embeddings = bert.extract_embeddings(train_df['log_message'].tolist(), batch_size=64)
    logger.info(f"  Train shape: {train_embeddings.shape}")

    logger.info("\n" + "-"*80)
    logger.info("Extracting val embeddings...")
    logger.info("-"*80)
    val_embeddings = bert.extract_embeddings(val_df['log_message'].tolist(), batch_size=64)
    logger.info(f"  Val shape: {val_embeddings.shape}")

    logger.info("\n" + "-"*80)
    logger.info("Extracting test embeddings...")
    logger.info("-"*80)
    test_embeddings = bert.extract_embeddings(test_df['log_message'].tolist(), batch_size=64)
    logger.info(f"  Test shape: {test_embeddings.shape}")

    # Save
    output_dir = Path('data/bert_embeddings_integrated')
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"\nSaving embeddings to {output_dir}...")
    np.save(output_dir / 'train_bert_embeddings.npy', train_embeddings)
    np.save(output_dir / 'val_bert_embeddings.npy', val_embeddings)
    np.save(output_dir / 'test_bert_embeddings.npy', test_embeddings)

    logger.info("="*80)
    logger.info("✅ BERT EMBEDDING GENERATION COMPLETE")
    logger.info("="*80)
    logger.info(f"Saved:")
    logger.info(f"  - train_bert_embeddings.npy ({train_embeddings.shape})")
    logger.info(f"  - val_bert_embeddings.npy ({val_embeddings.shape})")
    logger.info(f"  - test_bert_embeddings.npy ({test_embeddings.shape})")
    logger.info("\nNext: python train_phase2_integrated.py")
    logger.info("="*80)

if __name__ == '__main__':
    main()
