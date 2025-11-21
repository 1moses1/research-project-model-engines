#!/usr/bin/env python3
"""
Temporal Feature Extractor - Phase 2 Enhancement
Adds time-series and sequence-based features

Improves detection of:
1. Lateral movement (rapid connections to multiple servers)
2. Data exfiltration (large transfers at unusual times)
3. Brute force attacks (repeated failed logins)
4. Insider threats (unusual activity patterns)
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TemporalFeatureExtractor:
    """
    Extract temporal and sequential features from log data
    """

    def __init__(self):
        """Initialize temporal feature extractor"""
        pass

    def extract_basic_temporal(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract basic temporal features from timestamp

        Args:
            df: DataFrame with 'timestamp' column

        Returns:
            DataFrame with added temporal features
        """
        df = df.copy()

        # Parse timestamp if it's a string
        if df['timestamp'].dtype == 'object':
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

        # Extract temporal components
        df['hour'] = df['timestamp'].dt.hour
        df['minute'] = df['timestamp'].dt.minute
        df['day_of_week'] = df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
        df['day_of_month'] = df['timestamp'].dt.day
        df['month'] = df['timestamp'].dt.month
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

        # Business hours (9am-5pm, Monday-Friday)
        df['is_business_hours'] = (
            (df['hour'] >= 9) & (df['hour'] < 17) & (df['day_of_week'] < 5)
        ).astype(int)

        # Time of day categories
        df['time_of_day'] = pd.cut(
            df['hour'],
            bins=[0, 6, 12, 18, 24],
            labels=['night', 'morning', 'afternoon', 'evening'],
            include_lowest=True
        ).astype(str)

        # Suspicious time indicators
        df['is_late_night'] = ((df['hour'] >= 22) | (df['hour'] < 6)).astype(int)
        df['is_unusual_time'] = (
            (df['is_weekend'] == 1) | (df['is_late_night'] == 1)
        ).astype(int)

        return df

    def extract_sequence_features(self, df: pd.DataFrame,
                                  user_col: str = 'user',
                                  ip_col: str = 'source_ip',
                                  action_col: str = 'action',
                                  window_minutes: int = 5) -> pd.DataFrame:
        """
        Extract sequence-based features (for detecting lateral movement, brute force)

        Args:
            df: DataFrame sorted by timestamp
            user_col: Column containing user identifier
            ip_col: Column containing IP address
            action_col: Column containing action type
            window_minutes: Time window for counting events

        Returns:
            DataFrame with added sequence features
        """
        df = df.copy()

        # Sort by timestamp
        df = df.sort_values('timestamp')

        # Initialize columns with defaults
        df['events_last_5min'] = 1
        df['failed_attempts_last_5min'] = 0
        df['unique_ips_last_5min'] = 1
        df['unique_users_last_5min'] = 1
        df['rapid_succession'] = 0

        # Time-based grouping
        window = timedelta(minutes=window_minutes)

        # Group by user if column exists
        if user_col in df.columns and df[user_col].notna().any():
            for user in df[user_col].dropna().unique():
                user_mask = df[user_col] == user
                user_df = df[user_mask].copy()

                for idx in user_df.index:
                    current_time = df.loc[idx, 'timestamp']

                    # Get events in window
                    window_mask = (
                        user_mask &
                        (df['timestamp'] >= current_time - window) &
                        (df['timestamp'] <= current_time)
                    )

                    window_events = df[window_mask]

                    # Count events in window
                    df.loc[idx, 'events_last_5min'] = len(window_events)

                    # Count failed attempts
                    if action_col in df.columns:
                        failed_mask = window_events[action_col].str.contains(
                            'fail|deny|block|reject', case=False, na=False
                        )
                        df.loc[idx, 'failed_attempts_last_5min'] = failed_mask.sum()

                    # Unique IPs (lateral movement indicator)
                    if ip_col in df.columns and window_events[ip_col].notna().any():
                        df.loc[idx, 'unique_ips_last_5min'] = window_events[ip_col].nunique()

                    # Rapid succession (events < 1 second apart)
                    if len(window_events) > 1:
                        time_diffs = window_events['timestamp'].diff().dt.total_seconds()
                        rapid_count = (time_diffs < 1).sum()
                        df.loc[idx, 'rapid_succession'] = rapid_count

        return df

    def extract_anomaly_indicators(self, df: pd.DataFrame,
                                   log_col: str = 'log_message') -> pd.DataFrame:
        """
        Extract anomaly indicators from log content

        Args:
            df: DataFrame with log messages
            log_col: Column containing log messages

        Returns:
            DataFrame with anomaly indicators
        """
        df = df.copy()

        # Insider threat indicators
        df['large_transfer'] = df[log_col].str.contains(
            r'(\d+)\s*(gb|tb|mb)', case=False, na=False, regex=True
        ).astype(int)

        df['usb_access'] = df[log_col].str.contains(
            'usb|removable|external', case=False, na=False
        ).astype(int)

        df['sensitive_data'] = df[log_col].str.contains(
            'sensitive|confidential|classified|secret', case=False, na=False
        ).astype(int)

        # Lateral movement indicators
        df['multiple_connections'] = df[log_col].str.contains(
            r'(\d+)\s*(server|host|machine|system)', case=False, na=False, regex=True
        ).astype(int)

        df['smb_rdp_ssh'] = df[log_col].str.contains(
            'smb|rdp|ssh|remote', case=False, na=False
        ).astype(int)

        # Volume-based attack indicators
        df['high_volume'] = df[log_col].str.contains(
            r'(\d{3,})\s*(request|connection|attempt)', case=False, na=False, regex=True
        ).astype(int)

        df['spike_traffic'] = df[log_col].str.contains(
            'spike|surge|flood|storm', case=False, na=False
        ).astype(int)

        # Credential-based indicators
        df['credential_related'] = df[log_col].str.contains(
            'credential|password|login|authentication|stolen', case=False, na=False
        ).astype(int)

        df['multiple_ips'] = df[log_col].str.contains(
            r'(\d{2,})\s*ip', case=False, na=False, regex=True
        ).astype(int)

        # Ransomware indicators
        df['encryption_activity'] = df[log_col].str.contains(
            'encrypt|locked|ransom|.locked|.crypt', case=False, na=False
        ).astype(int)

        df['file_modification'] = df[log_col].str.contains(
            r'(\d{3,})\s*file', case=False, na=False, regex=True
        ).astype(int)

        # Combine into anomaly score
        anomaly_cols = [
            'large_transfer', 'usb_access', 'sensitive_data',
            'multiple_connections', 'smb_rdp_ssh', 'high_volume',
            'spike_traffic', 'credential_related', 'multiple_ips',
            'encryption_activity', 'file_modification'
        ]

        df['anomaly_score'] = df[anomaly_cols].sum(axis=1)

        return df

    def extract_all_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract all temporal features

        Args:
            df: DataFrame with log data

        Returns:
            DataFrame with all temporal features added
        """
        logger.info("Extracting temporal features...")

        # Basic temporal features
        if 'timestamp' in df.columns:
            df = self.extract_basic_temporal(df)
            logger.info("  ✅ Basic temporal features")

            # Sequence features (if we have enough data)
            if len(df) > 100:
                try:
                    df = self.extract_sequence_features(df)
                    logger.info("  ✅ Sequence features")
                except Exception as e:
                    logger.warning(f"  ⚠️  Could not extract sequence features: {e}")

        # Anomaly indicators from log content
        if 'log_message' in df.columns:
            df = self.extract_anomaly_indicators(df)
            logger.info("  ✅ Anomaly indicators")

        return df

    def get_temporal_feature_names(self) -> List[str]:
        """Get list of all temporal feature names"""
        return [
            # Basic temporal
            'hour', 'minute', 'day_of_week', 'day_of_month', 'month',
            'is_weekend', 'is_business_hours', 'is_late_night', 'is_unusual_time',

            # Sequence features
            'events_last_5min', 'failed_attempts_last_5min',
            'unique_ips_last_5min', 'unique_users_last_5min', 'rapid_succession',

            # Anomaly indicators
            'large_transfer', 'usb_access', 'sensitive_data',
            'multiple_connections', 'smb_rdp_ssh', 'high_volume',
            'spike_traffic', 'credential_related', 'multiple_ips',
            'encryption_activity', 'file_modification', 'anomaly_score'
        ]


def add_temporal_features_to_datasets():
    """
    Add temporal features to all datasets
    """
    logger.info("\n" + "="*100)
    logger.info("ADDING TEMPORAL FEATURES TO DATASETS")
    logger.info("="*100 + "\n")

    extractor = TemporalFeatureExtractor()

    datasets = {
        'train': 'data/advanced_processed/enhanced_train.csv',
        'val': 'data/advanced_processed/enhanced_val.csv',
        'test': 'data/advanced_processed/enhanced_test.csv'
    }

    output_dir = Path('data/temporal_enhanced')
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, path in datasets.items():
        logger.info(f"\n{name.upper()} Dataset:")
        logger.info("-" * 50)

        if not Path(path).exists():
            logger.warning(f"File not found: {path}")
            continue

        # Load dataset
        df = pd.read_csv(path)
        logger.info(f"Loaded {len(df):,} events")
        logger.info(f"Columns: {df.columns.tolist()}")

        # Extract temporal features
        df_enhanced = extractor.extract_all_temporal_features(df)

        # Save enhanced dataset
        output_path = output_dir / f'{name}_temporal_enhanced.csv'
        df_enhanced.to_csv(output_path, index=False)

        logger.info(f"✅ Saved to: {output_path}")
        logger.info(f"   New columns: {[c for c in df_enhanced.columns if c not in df.columns]}")

    logger.info("\n" + "="*100)
    logger.info("TEMPORAL FEATURE EXTRACTION COMPLETE")
    logger.info("="*100 + "\n")


if __name__ == '__main__':
    from pathlib import Path
    add_temporal_features_to_datasets()
