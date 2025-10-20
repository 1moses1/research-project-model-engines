"""
Data Augmentation Pipeline for Compliance Log Messages.

This module provides techniques for augmenting compliance event data to:
1. Increase dataset size and diversity
2. Balance class distributions
3. Improve model generalization
4. Handle rare event types

Augmentation Methods:
- Synonym replacement: Replace words with synonyms
- Back-translation: Translate to another language and back
- Template variation: Vary log templates while preserving semantics
- Random insertion: Insert relevant words
- Random swap: Swap positions of words
- Random deletion: Delete words randomly

Features:
- Preserves control IDs and compliance labels
- Maintains semantic meaning
- Configurable augmentation factor
- Support for multiple augmentation strategies
"""

import random
import re
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import pandas as pd
import numpy as np
from collections import defaultdict

from ..utils.config_loader import ConfigLoader
from ..utils.logger import setup_logger


class SynonymReplacer:
    """
    Replace words with synonyms to create variations.

    Uses a predefined dictionary of common log terms and their synonyms.
    """

    def __init__(self):
        """Initialize synonym dictionary."""
        self.synonyms = {
            # Actions
            "created": ["generated", "established", "initiated", "added"],
            "deleted": ["removed", "terminated", "erased", "destroyed"],
            "modified": ["changed", "updated", "altered", "edited"],
            "accessed": ["retrieved", "viewed", "opened", "read"],
            "failed": ["unsuccessful", "rejected", "denied", "error"],
            "successful": ["completed", "approved", "authorized", "accepted"],
            "attempted": ["tried", "initiated", "started", "begun"],
            "blocked": ["prevented", "stopped", "denied", "rejected"],

            # Objects
            "user": ["account", "identity", "credential", "person"],
            "account": ["user", "profile", "identity"],
            "file": ["document", "resource", "data", "asset"],
            "system": ["server", "host", "machine", "platform"],
            "access": ["entry", "permission", "authorization", "login"],
            "password": ["credential", "passphrase", "authentication"],
            "permission": ["privilege", "authorization", "access", "right"],

            # Security terms
            "unauthorized": ["unapproved", "illegal", "forbidden", "invalid"],
            "malicious": ["harmful", "dangerous", "suspicious", "threatening"],
            "violation": ["breach", "infraction", "non-compliance", "failure"],
            "compliance": ["adherence", "conformity", "accordance"],
            "vulnerability": ["weakness", "flaw", "exposure", "risk"],
            "attack": ["intrusion", "breach", "assault", "exploit"],

            # Status
            "detected": ["identified", "discovered", "found", "located"],
            "logged": ["recorded", "captured", "registered", "documented"],
            "verified": ["confirmed", "validated", "authenticated", "checked"],
            "escalated": ["elevated", "promoted", "upgraded", "raised"],
        }

    def replace(self, text: str, probability: float = 0.3) -> str:
        """
        Replace words with synonyms.

        Args:
            text: Input text
            probability: Probability of replacing each eligible word

        Returns:
            Augmented text
        """
        words = text.split()
        augmented_words = []

        for word in words:
            # Check if word (lowercased) is in synonym dictionary
            word_lower = word.lower()

            if word_lower in self.synonyms and random.random() < probability:
                # Replace with random synonym
                synonym = random.choice(self.synonyms[word_lower])

                # Preserve capitalization
                if word[0].isupper():
                    synonym = synonym.capitalize()

                augmented_words.append(synonym)
            else:
                augmented_words.append(word)

        return ' '.join(augmented_words)


class TemplateVariation:
    """
    Vary log templates while preserving semantics.

    Generates variations of log message templates by:
    - Reordering clauses
    - Adding/removing filler words
    - Paraphrasing common patterns
    """

    def __init__(self):
        """Initialize template variation patterns."""
        self.patterns = {
            # User account patterns
            r"User (account|profile) (\w+) (created|added|generated)": [
                r"Created user \2 account",
                r"Account \2 has been \3",
                r"New user account \2 \3",
            ],

            # Access patterns
            r"(Successful|Failed) (login|access) (for|by|from) (\w+)": [
                r"\2 \1 for user \4",
                r"User \4 \2 \1",
                r"\4 \2 attempt \1",
            ],

            # File patterns
            r"File (\S+) (accessed|modified|deleted) by (\w+)": [
                r"User \3 \2 file \1",
                r"\3 performed \2 operation on \1",
                r"File operation: \2 \1 by \3",
            ],

            # Permission patterns
            r"(Permission|Privilege) (granted|revoked|denied) (for|to) (\w+)": [
                r"\1 \2 for user \4",
                r"User \4 \1 \2",
                r"\4 \1 change: \2",
            ],
        }

    def vary(self, text: str) -> str:
        """
        Generate template variation.

        Args:
            text: Input log message

        Returns:
            Varied log message
        """
        # Try to match and vary known patterns
        for pattern, variations in self.patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                # Choose random variation
                variation = random.choice(variations)
                augmented = re.sub(pattern, variation, text, flags=re.IGNORECASE)
                return augmented

        # If no pattern matched, return original
        return text


class RandomInsertion:
    """Insert relevant words into log messages."""

    def __init__(self):
        """Initialize word lists for insertion."""
        self.filler_words = [
            "successfully", "properly", "correctly", "securely",
            "immediately", "recently", "automatically", "manually"
        ]

        self.time_indicators = [
            "at this time", "just now", "recently", "currently"
        ]

    def insert(self, text: str, n_insertions: int = 1) -> str:
        """
        Insert random words.

        Args:
            text: Input text
            n_insertions: Number of words to insert

        Returns:
            Augmented text
        """
        words = text.split()

        if len(words) < 3:
            return text

        for _ in range(n_insertions):
            # Choose random position (not first or last)
            position = random.randint(1, len(words) - 1)

            # Choose random word to insert
            insert_word = random.choice(self.filler_words + self.time_indicators)

            words.insert(position, insert_word)

        return ' '.join(words)


class RandomSwap:
    """Swap positions of words in log messages."""

    def swap(self, text: str, n_swaps: int = 2) -> str:
        """
        Swap word positions.

        Args:
            text: Input text
            n_swaps: Number of swaps to perform

        Returns:
            Augmented text
        """
        words = text.split()

        if len(words) < 4:
            return text

        for _ in range(n_swaps):
            # Choose two random positions (not first word - usually subject)
            idx1 = random.randint(1, len(words) - 1)
            idx2 = random.randint(1, len(words) - 1)

            # Swap
            words[idx1], words[idx2] = words[idx2], words[idx1]

        return ' '.join(words)


class RandomDeletion:
    """Delete words randomly from log messages."""

    def delete(self, text: str, probability: float = 0.1) -> str:
        """
        Delete words randomly.

        Args:
            text: Input text
            probability: Probability of deleting each word

        Returns:
            Augmented text
        """
        words = text.split()

        if len(words) < 3:
            return text

        # Keep first word (usually subject)
        augmented_words = [words[0]]

        # Randomly delete other words
        for word in words[1:]:
            if random.random() > probability:
                augmented_words.append(word)

        # Ensure at least 2 words remain
        if len(augmented_words) < 2:
            return text

        return ' '.join(augmented_words)


class DataAugmentation:
    """
    Main data augmentation pipeline.

    Combines multiple augmentation techniques to generate diverse variations
    of compliance event data while preserving labels and control IDs.
    """

    def __init__(
        self,
        methods: List[str] = None,
        augmentation_factor: float = 1.5,
        output_dir: str = "data/augmented"
    ):
        """
        Initialize data augmentation pipeline.

        Args:
            methods: List of augmentation methods to use
            augmentation_factor: Factor to multiply dataset size
            output_dir: Directory for augmented data
        """
        self.methods = methods or [
            "synonym_replacement",
            "template_variation",
            "random_insertion"
        ]
        self.augmentation_factor = augmentation_factor
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize augmenters
        self.synonym_replacer = SynonymReplacer()
        self.template_variation = TemplateVariation()
        self.random_insertion = RandomInsertion()
        self.random_swap = RandomSwap()
        self.random_deletion = RandomDeletion()

        # Logger
        self.logger = setup_logger("data_augmentation", "logs/data_augmentation.log")

        self.logger.info(f"Initialized data augmentation: methods={methods}, "
                        f"factor={augmentation_factor}")

    def augment_text(self, text: str, method: str) -> str:
        """
        Augment a single text using specified method.

        Args:
            text: Input text
            method: Augmentation method name

        Returns:
            Augmented text
        """
        if method == "synonym_replacement":
            return self.synonym_replacer.replace(text, probability=0.3)

        elif method == "template_variation":
            return self.template_variation.vary(text)

        elif method == "random_insertion":
            return self.random_insertion.insert(text, n_insertions=1)

        elif method == "random_swap":
            return self.random_swap.swap(text, n_swaps=2)

        elif method == "random_deletion":
            return self.random_deletion.delete(text, probability=0.1)

        else:
            self.logger.warning(f"Unknown augmentation method: {method}")
            return text

    def augment_event(self, event: Dict[str, Any], method: str) -> Dict[str, Any]:
        """
        Augment a single compliance event.

        Only augments log_message, preserves all labels and metadata.

        Args:
            event: Event dictionary
            method: Augmentation method

        Returns:
            Augmented event
        """
        augmented_event = event.copy()

        # Augment log message
        if 'log_message' in augmented_event:
            original_message = augmented_event['log_message']
            augmented_message = self.augment_text(original_message, method)
            augmented_event['log_message'] = augmented_message

        # Generate new event ID
        if 'event_id' in augmented_event:
            original_id = augmented_event['event_id']
            augmented_event['event_id'] = f"{original_id}-aug-{method[:3]}"

        return augmented_event

    def augment_dataset(
        self,
        df: pd.DataFrame,
        target_column: str = "compliance_status",
        augment_minority_only: bool = True
    ) -> pd.DataFrame:
        """
        Augment entire dataset.

        Args:
            df: Input DataFrame
            target_column: Column to check for minority class
            augment_minority_only: If True, only augment minority class

        Returns:
            Augmented DataFrame
        """
        self.logger.info(f"Augmenting dataset: {len(df)} events")

        # Calculate class distribution
        if target_column in df.columns:
            class_counts = df[target_column].value_counts()
            self.logger.info(f"Class distribution before augmentation:\n{class_counts}")

            if augment_minority_only:
                # Identify minority class
                minority_class = class_counts.idxmin()
                self.logger.info(f"Augmenting minority class: {minority_class}")

                # Filter minority class samples
                minority_df = df[df[target_column] == minority_class].copy()
                majority_df = df[df[target_column] != minority_class].copy()

                # Calculate number of augmentations needed
                target_minority_size = int(len(majority_df) * 0.7)  # Balance to 70% of majority
                n_augmentations = max(0, target_minority_size - len(minority_df))

                self.logger.info(f"Generating {n_augmentations} augmented samples")

                # Generate augmented samples
                augmented_samples = []

                for _ in range(n_augmentations):
                    # Sample random event from minority class
                    sample_event = minority_df.sample(n=1).iloc[0].to_dict()

                    # Choose random augmentation method
                    method = random.choice(self.methods)

                    # Augment event
                    augmented_event = self.augment_event(sample_event, method)

                    augmented_samples.append(augmented_event)

                # Create augmented DataFrame
                if augmented_samples:
                    augmented_df = pd.DataFrame(augmented_samples)

                    # Combine original and augmented
                    result_df = pd.concat([majority_df, minority_df, augmented_df], ignore_index=True)

                    # Shuffle
                    result_df = result_df.sample(frac=1, random_state=42).reset_index(drop=True)
                else:
                    result_df = df.copy()

            else:
                # Augment entire dataset uniformly
                n_augmentations = int(len(df) * (self.augmentation_factor - 1))
                self.logger.info(f"Generating {n_augmentations} augmented samples")

                augmented_samples = []

                for _ in range(n_augmentations):
                    # Sample random event
                    sample_event = df.sample(n=1).iloc[0].to_dict()

                    # Choose random method
                    method = random.choice(self.methods)

                    # Augment
                    augmented_event = self.augment_event(sample_event, method)

                    augmented_samples.append(augmented_event)

                # Combine
                if augmented_samples:
                    augmented_df = pd.DataFrame(augmented_samples)
                    result_df = pd.concat([df, augmented_df], ignore_index=True)

                    # Shuffle
                    result_df = result_df.sample(frac=1, random_state=42).reset_index(drop=True)
                else:
                    result_df = df.copy()

        else:
            # No target column, augment uniformly
            result_df = df.copy()

        # Log final distribution
        if target_column in result_df.columns:
            final_counts = result_df[target_column].value_counts()
            self.logger.info(f"Class distribution after augmentation:\n{final_counts}")

        self.logger.info(f"Augmentation complete: {len(df)} → {len(result_df)} events")

        return result_df

    def save_augmented_dataset(
        self,
        df: pd.DataFrame,
        filename: str = "augmented_dataset.csv"
    ) -> Path:
        """
        Save augmented dataset.

        Args:
            df: Augmented DataFrame
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename

        df.to_csv(output_path, index=False)

        self.logger.info(f"Augmented dataset saved to {output_path}")

        return output_path


def main():
    """
    Main function to demonstrate data augmentation.

    Workflow:
    1. Load configuration
    2. Load training dataset
    3. Augment minority class
    4. Save augmented dataset
    5. Print statistics
    """
    print("\n" + "="*60)
    print("DATA AUGMENTATION PIPELINE")
    print("="*60 + "\n")

    # Load configuration
    config_loader = ConfigLoader()
    data_config = config_loader.load_data_config()

    augmentation_config = data_config.get('augmentation', {})

    if not augmentation_config.get('enabled', True):
        print("⚠️  Data augmentation is disabled in config")
        return

    # Initialize augmentation
    augmenter = DataAugmentation(
        methods=augmentation_config.get('methods', [
            "synonym_replacement",
            "template_variation",
            "random_insertion"
        ]),
        augmentation_factor=augmentation_config.get('augmentation_factor', 1.5)
    )

    print("✅ Data augmentation initialized")
    print(f"   Methods: {augmenter.methods}")
    print(f"   Augmentation factor: {augmenter.augmentation_factor}")
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

    # Augment dataset (minority class only)
    print("🔄 Augmenting minority class...")
    augmented_df = augmenter.augment_dataset(
        df,
        target_column='compliance_status',
        augment_minority_only=True
    )

    # Save augmented dataset
    print("\n💾 Saving augmented dataset...")
    output_path = augmenter.save_augmented_dataset(
        augmented_df,
        filename="compliance_events_train_augmented.csv"
    )

    print(f"✅ Augmented dataset saved: {output_path}")
    print()

    # Statistics
    print("="*60)
    print("AUGMENTATION STATISTICS")
    print("="*60)

    print(f"Original dataset size: {len(df):,}")
    print(f"Augmented dataset size: {len(augmented_df):,}")
    print(f"Increase: +{len(augmented_df) - len(df):,} events ({((len(augmented_df) / len(df)) - 1) * 100:.1f}%)")
    print()

    print("Final class distribution:")
    print(augmented_df['compliance_status'].value_counts())
    print()

    # Show sample augmented messages
    print("="*60)
    print("SAMPLE AUGMENTED MESSAGES")
    print("="*60)

    # Find augmented samples
    augmented_samples = augmented_df[augmented_df['event_id'].str.contains('-aug-', na=False)]

    if len(augmented_samples) > 0:
        for i in range(min(5, len(augmented_samples))):
            sample = augmented_samples.iloc[i]
            print(f"\n{i+1}. Original ID: {sample['event_id'].split('-aug-')[0]}")
            print(f"   Augmented message: {sample['log_message']}")
    else:
        print("\nNo augmented samples found (augmentation may have been skipped)")

    print("\n" + "="*60)
    print("✅ DATA AUGMENTATION COMPLETE!")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
