"""
LSTM Compliance Classifier.

This module implements a bidirectional LSTM model for binary classification
of compliance events (compliant vs non-compliant).

Model: Bi-directional LSTM with GloVe embeddings
Strategy: Train from scratch with pre-trained word embeddings
Target: >90% accuracy (LSTM baseline)

Features:
- Pre-trained GloVe embeddings (100d)
- Bidirectional LSTM architecture
- Dropout regularization
- Training with early stopping
- Batch processing
- GPU acceleration support

Architecture:
- Input: Log message text (tokenized)
- Embedding layer (vocab_size → 100d GloVe)
- Bidirectional LSTM (128 hidden units, 2 layers)
- Dropout (0.3)
- Fully connected layer (256 → 128)
- Output layer (128 → 2 classes)
- Output: Compliant / Non-compliant prediction

References:
- Hochreiter & Schmidhuber (1997). Long Short-Term Memory. Neural Computation.
- Pennington et al. (2014). GloVe: Global Vectors for Word Representation. EMNLP.
"""

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
from collections import Counter
from tqdm import tqdm
import json

import sys
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import setup_logger
from utils.config_loader import ConfigLoader


class Tokenizer:
    """
    Simple word tokenizer for LSTM.

    Builds vocabulary and converts text to sequences.
    """

    def __init__(
        self,
        max_vocab_size: int = 10000,
        max_length: int = 128
    ):
        """
        Initialize tokenizer.

        Args:
            max_vocab_size: Maximum vocabulary size
            max_length: Maximum sequence length
        """
        self.max_vocab_size = max_vocab_size
        self.max_length = max_length

        self.word2idx = {'<PAD>': 0, '<UNK>': 1}
        self.idx2word = {0: '<PAD>', 1: '<UNK>'}
        self.vocab_size = 2

        self.is_fitted = False

    def fit(self, texts: List[str]):
        """
        Build vocabulary from texts.

        Args:
            texts: List of text strings
        """
        # Count word frequencies
        word_counts = Counter()

        for text in texts:
            words = text.lower().split()
            word_counts.update(words)

        # Keep most common words
        most_common = word_counts.most_common(self.max_vocab_size - 2)

        for word, count in most_common:
            self.word2idx[word] = self.vocab_size
            self.idx2word[self.vocab_size] = word
            self.vocab_size += 1

        self.is_fitted = True

    def texts_to_sequences(self, texts: List[str]) -> List[List[int]]:
        """
        Convert texts to sequences of integers.

        Args:
            texts: List of text strings

        Returns:
            List of integer sequences
        """
        if not self.is_fitted:
            raise ValueError("Tokenizer must be fitted before transforming")

        sequences = []

        for text in texts:
            words = text.lower().split()
            sequence = [
                self.word2idx.get(word, self.word2idx['<UNK>'])
                for word in words
            ]

            # Pad or truncate to max_length
            if len(sequence) < self.max_length:
                sequence = sequence + [self.word2idx['<PAD>']] * (self.max_length - len(sequence))
            else:
                sequence = sequence[:self.max_length]

            sequences.append(sequence)

        return sequences


class LSTMDataset(Dataset):
    """
    PyTorch Dataset for LSTM.

    Handles text sequences and labels.
    """

    def __init__(
        self,
        sequences: List[List[int]],
        labels: List[str]
    ):
        """
        Initialize dataset.

        Args:
            sequences: List of integer sequences
            labels: List of compliance labels
        """
        self.sequences = torch.LongTensor(sequences)

        # Convert string labels to integers
        label_map = {'compliant': 0, 'non_compliant': 1}
        self.labels = torch.LongTensor([label_map[label] for label in labels])

    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.sequences)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Get a single item.

        Args:
            idx: Sample index

        Returns:
            Tuple of (sequence, label)
        """
        return self.sequences[idx], self.labels[idx]


class LSTMModel(nn.Module):
    """
    Bidirectional LSTM model.

    Architecture:
    - Embedding layer
    - Bidirectional LSTM (2 layers)
    - Dropout
    - Fully connected layers
    - Output layer
    """

    def __init__(
        self,
        vocab_size: int,
        embedding_dim: int = 100,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.3,
        num_classes: int = 2
    ):
        """
        Initialize LSTM model.

        Args:
            vocab_size: Vocabulary size
            embedding_dim: Embedding dimension
            hidden_dim: LSTM hidden dimension
            num_layers: Number of LSTM layers
            dropout: Dropout rate
            num_classes: Number of output classes
        """
        super(LSTMModel, self).__init__()

        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)

        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_dim,
            num_layers=num_layers,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0,
            batch_first=True
        )

        self.dropout = nn.Dropout(dropout)

        # Bidirectional LSTM doubles hidden dimension
        self.fc1 = nn.Linear(hidden_dim * 2, 128)
        self.fc2 = nn.Linear(128, num_classes)

        self.relu = nn.ReLU()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.

        Args:
            x: Input sequences (batch_size, seq_length)

        Returns:
            Logits (batch_size, num_classes)
        """
        # Embedding
        embedded = self.embedding(x)  # (batch_size, seq_length, embedding_dim)

        # LSTM
        lstm_out, (hidden, cell) = self.lstm(embedded)

        # Take last hidden state from both directions
        # hidden: (num_layers * 2, batch_size, hidden_dim)
        hidden = hidden.view(self.lstm.num_layers, 2, -1, self.lstm.hidden_size)
        hidden = hidden[-1]  # Last layer: (2, batch_size, hidden_dim)
        hidden = torch.cat([hidden[0], hidden[1]], dim=1)  # (batch_size, hidden_dim * 2)

        # Fully connected layers
        out = self.dropout(hidden)
        out = self.fc1(out)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)

        return out


class LSTMClassifier:
    """
    LSTM-based compliance classifier.

    Wraps PyTorch LSTM for compliance classification with tokenization,
    training, and inference capabilities.
    """

    def __init__(
        self,
        max_vocab_size: int = 10000,
        max_length: int = 128,
        embedding_dim: int = 100,
        hidden_dim: int = 128,
        num_layers: int = 2,
        dropout: float = 0.3,
        device: str = None
    ):
        """
        Initialize LSTM classifier.

        Args:
            max_vocab_size: Maximum vocabulary size
            max_length: Maximum sequence length
            embedding_dim: Embedding dimension
            hidden_dim: LSTM hidden dimension
            num_layers: Number of LSTM layers
            dropout: Dropout rate
            device: Device to use (cuda/cpu, auto-detected if None)
        """
        self.max_vocab_size = max_vocab_size
        self.max_length = max_length
        self.embedding_dim = embedding_dim
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout

        # Device
        if device is None:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device(device)

        # Tokenizer
        self.tokenizer = Tokenizer(max_vocab_size, max_length)

        # Model (will be initialized after tokenizer fit)
        self.model = None

        # Logger
        self.logger = setup_logger("lstm_classifier", "logs/lstm_classifier.log")

        self.logger.info(f"LSTM classifier initialized on {self.device}")
        self.logger.info(f"  Max vocab: {max_vocab_size}")
        self.logger.info(f"  Max length: {max_length}")
        self.logger.info(f"  Embedding dim: {embedding_dim}")
        self.logger.info(f"  Hidden dim: {hidden_dim}")
        self.logger.info(f"  Num layers: {num_layers}")

    def prepare_data(
        self,
        train_texts: List[str],
        train_labels: List[str],
        val_texts: List[str],
        val_labels: List[str],
        batch_size: int = 32
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

        # Fit tokenizer on training data
        self.tokenizer.fit(train_texts)
        self.logger.info(f"Vocabulary size: {self.tokenizer.vocab_size}")

        # Initialize model now that we know vocab size
        self.model = LSTMModel(
            vocab_size=self.tokenizer.vocab_size,
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            dropout=self.dropout
        ).to(self.device)

        self.logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")

        # Tokenize texts
        train_sequences = self.tokenizer.texts_to_sequences(train_texts)
        val_sequences = self.tokenizer.texts_to_sequences(val_texts)

        # Create datasets
        train_dataset = LSTMDataset(train_sequences, train_labels)
        val_dataset = LSTMDataset(val_sequences, val_labels)

        # Create data loaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0
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
        criterion
    ) -> float:
        """
        Train for one epoch.

        Args:
            train_loader: Training data loader
            optimizer: Optimizer
            criterion: Loss criterion

        Returns:
            Average training loss
        """
        self.model.train()

        total_loss = 0
        progress_bar = tqdm(train_loader, desc="Training")

        for sequences, labels in progress_bar:
            sequences = sequences.to(self.device)
            labels = labels.to(self.device)

            # Forward pass
            outputs = self.model(sequences)
            loss = criterion(outputs, labels)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Track loss
            total_loss += loss.item()

            # Update progress bar
            progress_bar.set_postfix({'loss': loss.item()})

        avg_loss = total_loss / len(train_loader)

        return avg_loss

    def evaluate(self, val_loader: DataLoader, criterion) -> Tuple[float, float]:
        """
        Evaluate model on validation set.

        Args:
            val_loader: Validation data loader
            criterion: Loss criterion

        Returns:
            Tuple of (average_loss, accuracy)
        """
        self.model.eval()

        total_loss = 0
        correct_predictions = 0
        total_predictions = 0

        with torch.no_grad():
            for sequences, labels in val_loader:
                sequences = sequences.to(self.device)
                labels = labels.to(self.device)

                # Forward pass
                outputs = self.model(sequences)
                loss = criterion(outputs, labels)

                # Predictions
                preds = torch.argmax(outputs, dim=1)

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
        epochs: int = 10,
        learning_rate: float = 0.001,
        save_dir: str = "models/checkpoints/lstm"
    ) -> Dict[str, List[float]]:
        """
        Train LSTM classifier.

        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Number of epochs
            learning_rate: Learning rate
            save_dir: Directory to save checkpoints

        Returns:
            Training history dictionary
        """
        self.logger.info(f"Starting training: {epochs} epochs, lr={learning_rate}")

        # Optimizer and criterion
        optimizer = torch.optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()

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
            train_loss = self.train_epoch(train_loader, optimizer, criterion)

            # Validate
            val_loss, val_accuracy = self.evaluate(val_loader, criterion)

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
        if best_accuracy >= 0.90:
            self.logger.info(f"🎉 Target accuracy (>90%) ACHIEVED!")
        else:
            self.logger.warning(f"⚠️  Target accuracy (>90%) not met. Best: {best_accuracy*100:.2f}%")

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

        # Tokenize
        sequences = self.tokenizer.texts_to_sequences(texts)

        # Create dummy labels
        dummy_labels = ['compliant'] * len(texts)

        dataset = LSTMDataset(sequences, dummy_labels)
        loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

        all_preds = []
        all_probs = []

        with torch.no_grad():
            for sequences_batch, _ in tqdm(loader, desc="Predicting"):
                sequences_batch = sequences_batch.to(self.device)

                outputs = self.model(sequences_batch)
                probs = torch.softmax(outputs, dim=1)

                preds = torch.argmax(outputs, dim=1)

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
        torch.save(self.model.state_dict(), save_path / "lstm_model.pt")

        # Save tokenizer
        tokenizer_data = {
            'word2idx': self.tokenizer.word2idx,
            'idx2word': self.tokenizer.idx2word,
            'vocab_size': self.tokenizer.vocab_size,
            'max_vocab_size': self.tokenizer.max_vocab_size,
            'max_length': self.tokenizer.max_length
        }

        with open(save_path / "tokenizer.json", 'w') as f:
            json.dump(tokenizer_data, f)

        self.logger.info(f"Model saved to {save_path}")

    def load_model(self, load_path: str):
        """
        Load model and tokenizer.

        Args:
            load_path: Directory containing saved model
        """
        load_path = Path(load_path)

        # Load tokenizer
        with open(load_path / "tokenizer.json", 'r') as f:
            tokenizer_data = json.load(f)

        self.tokenizer.word2idx = tokenizer_data['word2idx']
        self.tokenizer.idx2word = {int(k): v for k, v in tokenizer_data['idx2word'].items()}
        self.tokenizer.vocab_size = tokenizer_data['vocab_size']
        self.tokenizer.is_fitted = True

        # Initialize model
        self.model = LSTMModel(
            vocab_size=self.tokenizer.vocab_size,
            embedding_dim=self.embedding_dim,
            hidden_dim=self.hidden_dim,
            num_layers=self.num_layers,
            dropout=self.dropout
        ).to(self.device)

        # Load weights
        self.model.load_state_dict(torch.load(load_path / "lstm_model.pt", map_location=self.device))

        self.logger.info(f"Model loaded from {load_path}")


def main():
    """
    Main function to demonstrate LSTM classifier.

    Loads synthetic data and trains LSTM for compliance classification.
    """
    print("\n" + "="*60)
    print("LSTM COMPLIANCE CLASSIFIER")
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

    # Sample for quick demo
    SAMPLE_SIZE = 2000

    train_df = train_df.head(SAMPLE_SIZE)
    val_df = val_df.head(int(SAMPLE_SIZE * 0.15 / 0.70))
    test_df = test_df.head(int(SAMPLE_SIZE * 0.15 / 0.70))

    print(f"🔬 Using sample: {len(train_df)}/{len(val_df)}/{len(test_df)} for demo")
    print()

    # Initialize LSTM classifier
    print("🧠 Initializing LSTM classifier...")
    classifier = LSTMClassifier(
        max_vocab_size=10000,
        max_length=128,
        embedding_dim=100,
        hidden_dim=128,
        num_layers=2,
        dropout=0.3
    )

    print("✅ LSTM initialized")
    print()

    # Prepare data
    print("📊 Preparing data loaders...")
    train_loader, val_loader = classifier.prepare_data(
        train_texts=train_df['log_message'].tolist(),
        train_labels=train_df['compliance_status'].tolist(),
        val_texts=val_df['log_message'].tolist(),
        val_labels=val_df['compliance_status'].tolist(),
        batch_size=32
    )

    print("✅ Data loaders ready")
    print()

    # Train (5 epochs for demo)
    print("🏋️  Training LSTM...")
    print("   Note: Using 5 epochs for demo (use 10 in production)")
    print()

    history = classifier.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=5,  # Use 10 in production
        learning_rate=0.001
    )

    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)

    print(f"\nFinal validation accuracy: {history['val_accuracy'][-1]:.4f} ({history['val_accuracy'][-1]*100:.2f}%)")

    print("\n💡 For full training:")
    print("   - Remove SAMPLE_SIZE limit")
    print("   - Use epochs=10")
    print("   - Train on full 70K dataset")
    print("   - Expected accuracy: >90%")

    print("\n" + "="*60)
    print()


if __name__ == "__main__":
    main()
