"""
Class Balancing for Imbalanced Compliance Datasets.

This module provides techniques for handling class imbalance in compliance data:
1. SMOTE (Synthetic Minority Over-sampling Technique)
2. Random oversampling
3. Random undersampling
4. Cost-sensitive learning weights
5. Combined approaches

Features:
- Multiple balancing strategies
- Configurable target ratios
- Support for multi-class problems
- Integration with scikit-learn and imbalanced-learn
- Cost calculation for cost-sensitive learning

References:
- Chawla et al. (2002). SMOTE: Synthetic Minority Over-sampling Technique.
  Journal of Artificial Intelligence Research.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
from collections import Counter
from sklearn.utils.class_weight import compute_class_weight

from ..utils.config_loader import ConfigLoader
from ..utils.logger import setup_logger


class SMOTEBalancer:
    """
    SMOTE implementation for oversampling minority class.

    SMOTE creates synthetic samples by interpolating between existing
    minority class samples and their k-nearest neighbors.

    Note: For full SMOTE implementation, requires imbalanced-learn library.
    This is a simplified version for demonstration.
    """

    def __init__(self, k_neighbors: int = 5, random_state: int = 42):
        """
        Initialize SMOTE balancer.

        Args:
            k_neighbors: Number of nearest neighbors for interpolation
            random_state: Random seed for reproducibility
        """
        self.k_neighbors = k_neighbors
        self.random_state = random_state
        self.logger = setup_logger("smote_balancer", "logs/class_balancing.log")

    def oversample(
        self,
        X: np.ndarray,
        y: np.ndarray,
        target_ratio: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Oversample minority class using SMOTE.

        For simplified implementation, uses random oversampling.
        For production, use imblearn.over_sampling.SMOTE.

        Args:
            X: Feature matrix
            y: Target labels
            target_ratio: Target ratio of minority/majority

        Returns:
            Tuple of (balanced_X, balanced_y)
        """
        try:
            from imblearn.over_sampling import SMOTE

            self.logger.info("Using imbalanced-learn SMOTE implementation")

            smote = SMOTE(
                sampling_strategy=target_ratio,
                k_neighbors=self.k_neighbors,
                random_state=self.random_state
            )

            X_balanced, y_balanced = smote.fit_resample(X, y)

            self.logger.info(f"SMOTE complete: {len(y)} → {len(y_balanced)} samples")

            return X_balanced, y_balanced

        except ImportError:
            self.logger.warning("imbalanced-learn not installed, using random oversampling")
            return self._random_oversample(X, y, target_ratio)

    def _random_oversample(
        self,
        X: np.ndarray,
        y: np.ndarray,
        target_ratio: float
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Fallback: Random oversampling of minority class.

        Args:
            X: Feature matrix
            y: Target labels
            target_ratio: Target ratio of minority/majority

        Returns:
            Tuple of (balanced_X, balanced_y)
        """
        # Count class distribution
        unique_classes, class_counts = np.unique(y, return_counts=True)

        if len(unique_classes) != 2:
            self.logger.warning("Random oversampling works best for binary classification")

        # Identify minority and majority classes
        minority_class = unique_classes[np.argmin(class_counts)]
        majority_class = unique_classes[np.argmax(class_counts)]

        minority_count = np.min(class_counts)
        majority_count = np.max(class_counts)

        # Calculate target minority count
        target_minority_count = int(majority_count * target_ratio)

        # Number of samples to generate
        n_samples_to_generate = max(0, target_minority_count - minority_count)

        self.logger.info(f"Generating {n_samples_to_generate} synthetic minority samples")

        # Get minority class indices
        minority_indices = np.where(y == minority_class)[0]

        # Randomly duplicate minority samples
        np.random.seed(self.random_state)
        duplicate_indices = np.random.choice(
            minority_indices,
            size=n_samples_to_generate,
            replace=True
        )

        # Combine original and duplicated samples
        X_balanced = np.vstack([X, X[duplicate_indices]])
        y_balanced = np.hstack([y, y[duplicate_indices]])

        # Shuffle
        shuffle_indices = np.random.permutation(len(y_balanced))
        X_balanced = X_balanced[shuffle_indices]
        y_balanced = y_balanced[shuffle_indices]

        return X_balanced, y_balanced


class RandomUndersampler:
    """Random undersampling of majority class."""

    def __init__(self, random_state: int = 42):
        """
        Initialize random undersampler.

        Args:
            random_state: Random seed
        """
        self.random_state = random_state
        self.logger = setup_logger("undersampler", "logs/class_balancing.log")

    def undersample(
        self,
        X: np.ndarray,
        y: np.ndarray,
        target_ratio: float = 1.0
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Undersample majority class.

        Args:
            X: Feature matrix
            y: Target labels
            target_ratio: Target ratio of minority/majority

        Returns:
            Tuple of (balanced_X, balanced_y)
        """
        # Count class distribution
        unique_classes, class_counts = np.unique(y, return_counts=True)

        minority_class = unique_classes[np.argmin(class_counts)]
        majority_class = unique_classes[np.argmax(class_counts)]

        minority_count = np.min(class_counts)
        majority_count = np.max(class_counts)

        # Calculate target majority count
        target_majority_count = int(minority_count / target_ratio)

        # Get indices
        minority_indices = np.where(y == minority_class)[0]
        majority_indices = np.where(y == majority_class)[0]

        # Randomly sample from majority class
        np.random.seed(self.random_state)
        sampled_majority_indices = np.random.choice(
            majority_indices,
            size=min(target_majority_count, len(majority_indices)),
            replace=False
        )

        # Combine minority and sampled majority
        selected_indices = np.hstack([minority_indices, sampled_majority_indices])

        X_balanced = X[selected_indices]
        y_balanced = y[selected_indices]

        # Shuffle
        shuffle_indices = np.random.permutation(len(y_balanced))
        X_balanced = X_balanced[shuffle_indices]
        y_balanced = y_balanced[shuffle_indices]

        self.logger.info(f"Undersampling complete: {len(y)} → {len(y_balanced)} samples")

        return X_balanced, y_balanced


class ClassBalancing:
    """
    Main class balancing pipeline.

    Provides multiple strategies for handling class imbalance:
    - SMOTE oversampling
    - Random oversampling
    - Random undersampling
    - Combined over/under sampling
    - Cost-sensitive learning weights
    """

    def __init__(
        self,
        method: str = "smote",
        target_ratio: float = 0.5,
        k_neighbors: int = 5,
        output_dir: str = "data/balanced"
    ):
        """
        Initialize class balancing pipeline.

        Args:
            method: Balancing method (smote, oversample, undersample, combined, cost_sensitive)
            target_ratio: Target ratio of minority/majority
            k_neighbors: K neighbors for SMOTE
            output_dir: Output directory
        """
        self.method = method
        self.target_ratio = target_ratio
        self.k_neighbors = k_neighbors
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize balancers
        self.smote_balancer = SMOTEBalancer(k_neighbors=k_neighbors)
        self.undersampler = RandomUndersampler()

        # Logger
        self.logger = setup_logger("class_balancing", "logs/class_balancing.log")

        self.logger.info(f"Initialized class balancing: method={method}, "
                        f"target_ratio={target_ratio}")

    def balance_dataset(
        self,
        df: pd.DataFrame,
        feature_columns: List[str],
        target_column: str = "compliance_status"
    ) -> pd.DataFrame:
        """
        Balance dataset using specified method.

        Args:
            df: Input DataFrame
            feature_columns: List of feature column names
            target_column: Target column name

        Returns:
            Balanced DataFrame
        """
        self.logger.info(f"Balancing dataset: {len(df)} samples")

        # Extract features and target
        X = df[feature_columns].values
        y = df[target_column].values

        # Check class distribution
        unique_classes, class_counts = np.unique(y, return_counts=True)
        self.logger.info(f"Original distribution: {dict(zip(unique_classes, class_counts))}")

        # Apply balancing method
        if self.method == "smote":
            X_balanced, y_balanced = self.smote_balancer.oversample(
                X, y, self.target_ratio
            )

        elif self.method == "oversample":
            X_balanced, y_balanced = self.smote_balancer._random_oversample(
                X, y, self.target_ratio
            )

        elif self.method == "undersample":
            X_balanced, y_balanced = self.undersampler.undersample(
                X, y, self.target_ratio
            )

        elif self.method == "combined":
            # First oversample, then undersample
            X_temp, y_temp = self.smote_balancer.oversample(X, y, 0.7)
            X_balanced, y_balanced = self.undersampler.undersample(
                X_temp, y_temp, 0.8
            )

        elif self.method == "cost_sensitive":
            # No resampling, return original with class weights
            self.logger.info("Using cost-sensitive learning (no resampling)")
            X_balanced, y_balanced = X, y

        else:
            self.logger.warning(f"Unknown method: {self.method}, returning original")
            X_balanced, y_balanced = X, y

        # Check balanced distribution
        unique_balanced, balanced_counts = np.unique(y_balanced, return_counts=True)
        self.logger.info(f"Balanced distribution: {dict(zip(unique_balanced, balanced_counts))}")

        # Reconstruct DataFrame
        # For simplicity, duplicate rows for oversampling
        if len(y_balanced) > len(y):
            # Oversampling occurred
            n_duplicates = len(y_balanced) - len(y)

            # Create balanced df by duplicating minority samples
            balanced_df = df.copy()

            minority_class = unique_classes[np.argmin(class_counts)]
            minority_samples = df[df[target_column] == minority_class]

            # Randomly sample with replacement
            duplicated_samples = minority_samples.sample(
                n=n_duplicates,
                replace=True,
                random_state=42
            )

            balanced_df = pd.concat([balanced_df, duplicated_samples], ignore_index=True)

            # Shuffle
            balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

        elif len(y_balanced) < len(y):
            # Undersampling occurred
            majority_class = unique_classes[np.argmax(class_counts)]

            # Keep all minority samples
            minority_samples = df[df[target_column] != majority_class]

            # Sample from majority
            n_majority_to_keep = len(y_balanced) - len(minority_samples)
            majority_samples = df[df[target_column] == majority_class].sample(
                n=n_majority_to_keep,
                random_state=42
            )

            balanced_df = pd.concat([minority_samples, majority_samples], ignore_index=True)

            # Shuffle
            balanced_df = balanced_df.sample(frac=1, random_state=42).reset_index(drop=True)

        else:
            # No change
            balanced_df = df.copy()

        self.logger.info(f"Balancing complete: {len(df)} → {len(balanced_df)} samples")

        return balanced_df

    def compute_class_weights(
        self,
        y: np.ndarray,
        classes: Optional[np.ndarray] = None
    ) -> Dict[Any, float]:
        """
        Compute class weights for cost-sensitive learning.

        Weights are inversely proportional to class frequencies:
        weight(class) = n_samples / (n_classes * n_samples_in_class)

        Args:
            y: Target labels
            classes: Optional array of class labels

        Returns:
            Dictionary mapping class -> weight
        """
        if classes is None:
            classes = np.unique(y)

        # Compute weights
        weights = compute_class_weight(
            class_weight='balanced',
            classes=classes,
            y=y
        )

        class_weights = dict(zip(classes, weights))

        self.logger.info(f"Class weights: {class_weights}")

        return class_weights

    def save_balanced_dataset(
        self,
        df: pd.DataFrame,
        filename: str = "balanced_dataset.csv"
    ) -> Path:
        """
        Save balanced dataset.

        Args:
            df: Balanced DataFrame
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename

        df.to_csv(output_path, index=False)

        self.logger.info(f"Balanced dataset saved to {output_path}")

        return output_path

    def get_statistics(
        self,
        df_original: pd.DataFrame,
        df_balanced: pd.DataFrame,
        target_column: str
    ) -> Dict[str, Any]:
        """
        Get balancing statistics.

        Args:
            df_original: Original DataFrame
            df_balanced: Balanced DataFrame
            target_column: Target column name

        Returns:
            Dictionary of statistics
        """
        original_counts = df_original[target_column].value_counts().to_dict()
        balanced_counts = df_balanced[target_column].value_counts().to_dict()

        stats = {
            "original_size": len(df_original),
            "balanced_size": len(df_balanced),
            "size_change": len(df_balanced) - len(df_original),
            "size_change_percent": ((len(df_balanced) / len(df_original)) - 1) * 100,
            "original_distribution": original_counts,
            "balanced_distribution": balanced_counts,
            "method": self.method,
            "target_ratio": self.target_ratio
        }

        return stats


def main():
    """
    Main function to demonstrate class balancing.

    Workflow:
    1. Load configuration
    2. Load training dataset
    3. Balance classes using configured method
    4. Save balanced dataset
    5. Print statistics
    """
    print("\n" + "="*60)
    print("CLASS BALANCING PIPELINE")
    print("="*60 + "\n")

    # Load configuration
    config_loader = ConfigLoader()
    data_config = config_loader.load_data_config()

    balancing_config = data_config.get('class_balancing', {})

    # Initialize balancer
    balancer = ClassBalancing(
        method=balancing_config.get('method', 'smote'),
        target_ratio=balancing_config.get('target_ratio', 0.5),
        k_neighbors=balancing_config.get('k_neighbors', 5)
    )

    print("✅ Class balancing initialized")
    print(f"   Method: {balancer.method}")
    print(f"   Target ratio: {balancer.target_ratio}")
    print()

    # Check if training dataset exists
    train_file = Path("data/synthetic/compliance_events_train.csv")

    if not train_file.exists():
        print("⚠️  Training dataset not found!")
        print(f"   Expected: {train_file}")
        print("\n📝 Please generate the synthetic dataset first:")
        print("   python src/data_pipeline/synthetic_generator.py")
        print()
        return

    # Load training dataset
    print(f"📂 Loading training dataset: {train_file}")
    df = pd.read_csv(train_file)
    print(f"✅ Loaded {len(df)} events")
    print()

    # Show original distribution
    print("📊 Original class distribution:")
    print(df['compliance_status'].value_counts())
    print()

    # For SMOTE, we need numeric features
    # Use simple numeric features for demonstration
    feature_columns = ['hour_of_day', 'status_code', 'port']

    # Check if columns exist
    missing_cols = [col for col in feature_columns if col not in df.columns]

    if missing_cols:
        print(f"⚠️  Missing columns: {missing_cols}")
        print("   Using alternative approach...")

        # Create dummy numeric features
        df['feature_1'] = df['compliance_status'].map({'compliant': 1, 'non_compliant': 0})
        df['feature_2'] = df.index % 100
        df['feature_3'] = np.random.randint(0, 10, size=len(df))

        feature_columns = ['feature_1', 'feature_2', 'feature_3']

    # Balance dataset
    print(f"⚖️  Balancing dataset using {balancer.method}...")
    balanced_df = balancer.balance_dataset(
        df,
        feature_columns=feature_columns,
        target_column='compliance_status'
    )

    # Save balanced dataset
    print("\n💾 Saving balanced dataset...")
    output_path = balancer.save_balanced_dataset(
        balanced_df,
        filename="compliance_events_train_balanced.csv"
    )

    print(f"✅ Balanced dataset saved: {output_path}")
    print()

    # Statistics
    print("="*60)
    print("BALANCING STATISTICS")
    print("="*60)

    stats = balancer.get_statistics(df, balanced_df, 'compliance_status')

    print(f"Original dataset size: {stats['original_size']:,}")
    print(f"Balanced dataset size: {stats['balanced_size']:,}")
    print(f"Change: {stats['size_change']:+,} samples ({stats['size_change_percent']:+.1f}%)")
    print()

    print("Original distribution:")
    for label, count in stats['original_distribution'].items():
        print(f"  {label}: {count:,} ({count/stats['original_size']*100:.1f}%)")

    print("\nBalanced distribution:")
    for label, count in stats['balanced_distribution'].items():
        print(f"  {label}: {count:,} ({count/stats['balanced_size']*100:.1f}%)")

    print()

    # Compute class weights for cost-sensitive learning
    print("="*60)
    print("CLASS WEIGHTS (for cost-sensitive learning)")
    print("="*60)

    y = df['compliance_status'].values
    class_weights = balancer.compute_class_weights(y)

    for label, weight in class_weights.items():
        print(f"  {label}: {weight:.4f}")

    print("\n" + "="*60)
    print("✅ CLASS BALANCING COMPLETE!")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
