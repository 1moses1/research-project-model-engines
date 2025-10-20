"""
BERT-based Compliance Classifier.

This module implements a fine-tuned BERT model for binary classification
of compliance events (compliant vs non-compliant).

Model: bert-base-uncased (110M parameters)
Strategy: Fine-tuning with frozen initial layers
Target: >93% accuracy

Features:
- Pre-trained BERT tokenizer and model
- Configurable layer freezing
- Training with early stopping
- Validation monitoring
- Model checkpointing
- Inference optimization

Architecture:
- Input: Log message text
- BERT encoder (12 layers, 768 hidden, 12 attention heads)
- Dropout layer (0.1)
- Linear classification head (768 → 2 classes)
- Output: Compliant / Non-compliant prediction

References:
- Devlin et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers
  for Language Understanding. NAACL.
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    BertTokenizer,
    BertForSequenceClassification,
    AdamW,
    get_linear_schedule_with_warmup
)
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
from tqdm import tqdm
import json

import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import setup_logger
from utils.config_loader import ConfigLoader


class ComplianceDataset(Dataset):
    """
    PyTorch Dataset for compliance events.

    Tokenizes log messages and prepares them for BERT.
    """

    def __init__(
        self,
        texts: List[str],
        labels: List[str],
        tokenizer: BertTokenizer,
        max_length: int = 128
    ):
        """
        Initialize dataset.

        Args:
            texts: List of log messages
            labels: List of compliance labels
            tokenizer: BERT tokenizer
            max_length: Maximum sequence length
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length

        # Convert string labels to integers
        self.label_map = {'compliant': 0, 'non_compliant': 1}
        self.labels_int = [self.label_map[label] for label in labels]

    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.texts)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a single item.

        Args:
            idx: Sample index

        Returns:
            Dictionary with input_ids, attention_mask, and label
        """
        text = self.texts[idx]
        label = self.labels_int[idx]

        # Tokenize
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )

        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(label, dtype=torch.long)
        }


class BERTClassifier:
    """
    BERT-based compliance classifier.

    Wraps HuggingFace BERT for compliance classification with
    training, evaluation, and inference capabilities.
    """

    def __init__(
        self,
        model_name: str = 'bert-base-uncased',
        num_labels: int = 2,
        max_length: int = 128,
        freeze_layers: int = 10,
        device: str = None
    ):
        """
        Initialize BERT classifier.

        Args:
            model_name: Pre-trained BERT model name
            num_labels: Number of output classes
            max_length: Maximum sequence length
            freeze_layers: Number of BERT layers to freeze (0-12)
            device: Device to use (cuda/cpu, auto-detected if None)
        """
        self.model_name = model_name
        self.num_labels = num_labels
        self.max_length = max_length
        self.freeze_layers = freeze_layers

        # Device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        # Logger
        self.logger = setup_logger("bert_classifier", "logs/bert_classifier.log")

        # Load tokenizer
        self.logger.info(f"Loading tokenizer: {model_name}")
        self.tokenizer = BertTokenizer.from_pretrained(model_name)

        # Load model
        self.logger.info(f"Loading model: {model_name}")
        self.model = BertForSequenceClassification.from_pretrained(
            model_name,
            num_labels=num_labels
        )

        # Freeze layers
        if freeze_layers > 0:
            self._freeze_layers(freeze_layers)

        # Move to device
        self.model.to(self.device)

        self.logger.info(f"BERT classifier initialized on {self.device}")
        self.logger.info(f"  Model: {model_name}")
        self.logger.info(f"  Frozen layers: {freeze_layers}/12")
        self.logger.info(f"  Max length: {max_length}")

    def _freeze_layers(self, n_layers: int):
        """
        Freeze initial BERT layers.

        Args:
            n_layers: Number of layers to freeze (0-12)
        """
        if n_layers == 0:
            return

        # Freeze embeddings
        for param in self.model.bert.embeddings.parameters():
            param.requires_grad = False

        # Freeze encoder layers
        for i in range(n_layers):
            for param in self.model.bert.encoder.layer[i].parameters():
                param.requires_grad = False

        self.logger.info(f"Froze embeddings + first {n_layers} encoder layers")

    def prepare_data(
        self,
        train_texts: List[str],
        train_labels: List[str],
        val_texts: List[str],
        val_labels: List[str],
        batch_size: int = 16
    ) -> Tuple[DataLoader, DataLoader]:
        """
        Prepare data loaders.

        Args:
            train_texts: Training log messages
            train_labels: Training labels
            val_texts: Validation log messages
            val_labels: Validation labels
            batch_size: Batch size

        Returns:
            Tuple of (train_loader, val_loader)
        """
        self.logger.info(f"Preparing data loaders...")

        # Create datasets
        train_dataset = ComplianceDataset(
            train_texts, train_labels, self.tokenizer, self.max_length
        )

        val_dataset = ComplianceDataset(
            val_texts, val_labels, self.tokenizer, self.max_length
        )

        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0  # Set to 0 for compatibility
        )

        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=0
        )

        self.logger.info(f"Train: {len(train_dataset)} samples, {len(train_loader)} batches")
        self.logger.info(f"Val: {len(val_dataset)} samples, {len(val_loader)} batches")

        return train_loader, val_loader

    def train_epoch(
        self,
        train_loader: DataLoader,
        optimizer,
        scheduler
    ) -> float:
        """
        Train for one epoch.

        Args:
            train_loader: Training data loader
            optimizer: Optimizer
            scheduler: Learning rate scheduler

        Returns:
            Average training loss
        """
        self.model.train()

        total_loss = 0
        progress_bar = tqdm(train_loader, desc="Training")

        for batch in progress_bar:
            # Move to device
            input_ids = batch['input_ids'].to(self.device)
            attention_mask = batch['attention_mask'].to(self.device)
            labels = batch['label'].to(self.device)

            # Forward pass
            outputs = self.model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                labels=labels
            )

            loss = outputs.loss

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            scheduler.step()

            # Track loss
            total_loss += loss.item()

            # Update progress bar
            progress_bar.set_postfix({'loss': loss.item()})

        avg_loss = total_loss / len(train_loader)

        return avg_loss

    def evaluate(self, val_loader: DataLoader) -> Tuple[float, float]:
        """
        Evaluate model on validation set.

        Args:
            val_loader: Validation data loader

        Returns:
            Tuple of (average_loss, accuracy)
        """
        self.model.eval()

        total_loss = 0
        correct_predictions = 0
        total_predictions = 0

        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                labels = batch['label'].to(self.device)

                # Forward pass
                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )

                loss = outputs.loss
                logits = outputs.logits

                # Predictions
                preds = torch.argmax(logits, dim=1)

                # Accuracy
                correct_predictions += (preds == labels).sum().item()
                total_predictions += labels.size(0)

                # Loss
                total_loss += loss.item()

        avg_loss = total_loss / len(val_loader)
        accuracy = correct_predictions / total_predictions

        return avg_loss, accuracy

    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 5,
        learning_rate: float = 2e-5,
        warmup_steps: int = 0,
        save_dir: str = "models/checkpoints/bert"
    ) -> Dict[str, List[float]]:
        """
        Train BERT classifier.

        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of epochs
            learning_rate: Learning rate
            warmup_steps: Warmup steps for scheduler
            save_dir: Directory to save checkpoints

        Returns:
            Training history dictionary
        """
        self.logger.info(f"Starting training: {epochs} epochs, lr={learning_rate}")

        # Optimizer
        optimizer = AdamW(self.model.parameters(), lr=learning_rate)

        # Scheduler
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=total_steps
        )

        # Training history
        history = {
            'train_loss': [],
            'val_loss': [],
            'val_accuracy': []
        }

        # Best model tracking
        best_accuracy = 0.0
        save_path = Path(save_dir)
        save_path.mkdir(parents=True, exist_ok=True)

        # Training loop
        for epoch in range(epochs):
            self.logger.info(f"\nEpoch {epoch + 1}/{epochs}")

            # Train
            train_loss = self.train_epoch(train_loader, optimizer, scheduler)

            # Validate
            val_loss, val_accuracy = self.evaluate(val_loader)

            # Log metrics
            self.logger.info(f"  Train Loss: {train_loss:.4f}")
            self.logger.info(f"  Val Loss: {val_loss:.4f}")
            self.logger.info(f"  Val Accuracy: {val_accuracy:.4f} ({val_accuracy*100:.2f}%)")

            # Save history
            history['train_loss'].append(train_loss)
            history['val_loss'].append(val_loss)
            history['val_accuracy'].append(val_accuracy)

            # Save best model
            if val_accuracy > best_accuracy:
                best_accuracy = val_accuracy
                best_model_path = save_path / "best_model.pt"
                torch.save(self.model.state_dict(), best_model_path)
                self.logger.info(f"  ✅ New best model saved: {val_accuracy:.4f}")

        self.logger.info(f"\nTraining complete!")
        self.logger.info(f"Best validation accuracy: {best_accuracy:.4f} ({best_accuracy*100:.2f}%)")

        # Check if target met
        if best_accuracy >= 0.93:
            self.logger.info(f"🎉 Target accuracy (>93%) ACHIEVED!")
        else:
            self.logger.warning(f"⚠️  Target accuracy (>93%) not met. Best: {best_accuracy*100:.2f}%")

        return history

    def predict(
        self,
        texts: List[str],
        batch_size: int = 32
    ) -> Tuple[List[str], np.ndarray]:
        """
        Make predictions on new data.

        Args:
            texts: List of log messages
            batch_size: Batch size for inference

        Returns:
            Tuple of (predicted_labels, predicted_probabilities)
        """
        self.model.eval()

        all_preds = []
        all_probs = []

        # Create dummy labels for dataset
        dummy_labels = ['compliant'] * len(texts)

        dataset = ComplianceDataset(
            texts, dummy_labels, self.tokenizer, self.max_length
        )

        loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        with torch.no_grad():
            for batch in tqdm(loader, desc="Predicting"):
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)

                outputs = self.model(
                    input_ids=input_ids,
                    attention_mask=attention_mask
                )

                logits = outputs.logits
                probs = torch.softmax(logits, dim=1)

                preds = torch.argmax(logits, dim=1)

                all_preds.extend(preds.cpu().numpy())
                all_probs.extend(probs[:, 1].cpu().numpy())  # Probability of non_compliant

        # Convert predictions to labels
        label_map_inv = {0: 'compliant', 1: 'non_compliant'}
        pred_labels = [label_map_inv[pred] for pred in all_preds]

        return pred_labels, np.array(all_probs)

    def save_model(self, save_path: str):
        """
        Save model and tokenizer.

        Args:
            save_path: Directory to save model
        """
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)

        # Save model
        self.model.save_pretrained(save_path)

        # Save tokenizer
        self.tokenizer.save_pretrained(save_path)

        self.logger.info(f"Model saved to {save_path}")

    def load_model(self, load_path: str):
        """
        Load model and tokenizer.

        Args:
            load_path: Directory containing saved model
        """
        load_path = Path(load_path)

        # Load model
        self.model = BertForSequenceClassification.from_pretrained(load_path)
        self.model.to(self.device)

        # Load tokenizer
        self.tokenizer = BertTokenizer.from_pretrained(load_path)

        self.logger.info(f"Model loaded from {load_path}")


def main():
    """
    Main function to demonstrate BERT classifier.

    Loads synthetic data and trains BERT for compliance classification.
    """
    print("\n" + "="*60)
    print("BERT COMPLIANCE CLASSIFIER")
    print("="*60 + "\n")

    # Check for synthetic data
    train_file = Path("data/synthetic/compliance_events_train.csv")

    if not train_file.exists():
        print("⚠️  Training dataset not found!")
        print(f"   Expected: {train_file}")
        print("\n📝 Please generate the synthetic dataset first:")
        print("   python src/data_pipeline/synthetic_generator.py")
        print()
        return

    # Load data
    print(f"📂 Loading datasets...")
    train_df = pd.read_csv(train_file)
    val_df = pd.read_csv("data/synthetic/compliance_events_val.csv")
    test_df = pd.read_csv("data/synthetic/compliance_events_test.csv")

    print(f"✅ Train: {len(train_df)} samples")
    print(f"✅ Val: {len(val_df)} samples")
    print(f"✅ Test: {len(test_df)} samples")
    print()

    # Sample for quick demo (use full dataset in production)
    SAMPLE_SIZE = 1000  # Use 1000 for demo, remove for full training

    train_df = train_df.head(SAMPLE_SIZE)
    val_df = val_df.head(int(SAMPLE_SIZE * 0.15 / 0.70))
    test_df = test_df.head(int(SAMPLE_SIZE * 0.15 / 0.70))

    print(f"🔬 Using sample: {len(train_df)}/{len(val_df)}/{len(test_df)} for demo")
    print()

    # Initialize BERT classifier
    print("🤖 Initializing BERT classifier...")
    classifier = BERTClassifier(
        model_name='bert-base-uncased',
        max_length=128,
        freeze_layers=10
    )

    print("✅ BERT initialized")
    print()

    # Prepare data
    print("📊 Preparing data loaders...")
    train_loader, val_loader = classifier.prepare_data(
        train_texts=train_df['log_message'].tolist(),
        train_labels=train_df['compliance_status'].tolist(),
        val_texts=val_df['log_message'].tolist(),
        val_labels=val_df['compliance_status'].tolist(),
        batch_size=16
    )

    print("✅ Data loaders ready")
    print()

    # Train (2 epochs for demo)
    print("🏋️  Training BERT...")
    print("   Note: Using 2 epochs for demo (use 5 in production)")
    print()

    history = classifier.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=2,  # Use 5 in production
        learning_rate=2e-5
    )

    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)

    print(f"\nFinal validation accuracy: {history['val_accuracy'][-1]:.4f} ({history['val_accuracy'][-1]*100:.2f}%)")

    print("\n💡 For full training:")
    print("   - Remove SAMPLE_SIZE limit")
    print("   - Use epochs=5")
    print("   - Train on full 70K dataset")
    print("   - Expected accuracy: >93%")

    print("\n" + "="*60)
    print()


if __name__ == "__main__":
    main()
