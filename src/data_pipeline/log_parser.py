"""
Log Parser using Drain Algorithm for template extraction.

This module implements the Drain algorithm for parsing unstructured log messages
into structured templates. Drain is a fast online log parsing method that extracts
log templates from raw log messages.

Features:
- Online parsing (processes logs one by one)
- Fixed-depth parse tree structure
- Similarity-based clustering
- Support for wildcard tokens
- Template extraction and storage
- Integration with compliance event pipeline

References:
- He, P., et al. (2017). Drain: An online log parsing approach with fixed depth tree.
  IEEE International Conference on Web Services (ICWS).
"""

import re
import json
import hashlib
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
from collections import defaultdict
import pandas as pd
import numpy as np

from ..utils.config_loader import ConfigLoader
from ..utils.logger import setup_logger


class LogCluster:
    """
    Represents a cluster of similar log messages with a common template.

    Attributes:
        cluster_id: Unique identifier for the cluster
        log_template: The extracted template with wildcards
        log_ids: List of event IDs belonging to this cluster
        size: Number of logs in this cluster
    """

    def __init__(self, log_template: List[str], cluster_id: int):
        """
        Initialize a log cluster.

        Args:
            log_template: List of tokens representing the template
            cluster_id: Unique cluster identifier
        """
        self.cluster_id = cluster_id
        self.log_template = log_template
        self.log_ids: List[str] = []
        self.size = 0

    def add_log_id(self, log_id: str):
        """Add a log event ID to this cluster."""
        self.log_ids.append(log_id)
        self.size += 1

    def get_template_str(self) -> str:
        """Get template as string with wildcards."""
        return ' '.join(self.log_template)


class Node:
    """
    Node in the fixed-depth parse tree.

    Attributes:
        token: Token value at this node (or digit/length indicator)
        depth: Depth of this node in the tree
        children: Child nodes
        cluster_ids: IDs of log clusters at leaf nodes
    """

    def __init__(self, token: str = "", depth: int = 0):
        """
        Initialize a tree node.

        Args:
            token: Token value or special marker
            depth: Depth in the parse tree
        """
        self.token = token
        self.depth = depth
        self.children: Dict[str, 'Node'] = {}
        self.cluster_ids: List[int] = []


class DrainParser:
    """
    Drain algorithm implementation for log template extraction.

    The Drain algorithm uses a fixed-depth parse tree to group similar log messages
    and extract templates with wildcards for variable parts.

    Workflow:
    1. Preprocess log message (tokenize, remove special chars)
    2. Search parse tree by log length and initial tokens
    3. Find best matching cluster using similarity
    4. Update cluster or create new one
    5. Extract template with wildcards
    """

    def __init__(
        self,
        depth: int = 4,
        similarity_threshold: float = 0.5,
        max_children: int = 100,
        max_clusters: int = 1000,
        output_dir: str = "data/processed"
    ):
        """
        Initialize Drain parser.

        Args:
            depth: Depth of the parse tree (typically 4)
            similarity_threshold: Minimum similarity for clustering (0-1)
            max_children: Maximum children per internal node
            max_clusters: Maximum number of clusters
            output_dir: Directory for output files
        """
        self.depth = depth - 2  # Root and length layers are implicit
        self.similarity_threshold = similarity_threshold
        self.max_children = max_children
        self.max_clusters = max_clusters
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize parse tree
        self.root_node = Node()
        self.log_clusters: Dict[int, LogCluster] = {}
        self.cluster_counter = 0

        # Statistics
        self.parsed_count = 0
        self.template_count = 0

        # Logger
        self.logger = setup_logger("drain_parser", "logs/drain_parser.log")

        self.logger.info(f"Initialized Drain parser: depth={depth}, "
                        f"similarity={similarity_threshold}, "
                        f"max_clusters={max_clusters}")

    def preprocess(self, log_message: str) -> List[str]:
        """
        Preprocess log message into tokens.

        Steps:
        1. Remove special characters (except space, hyphen, underscore)
        2. Split into tokens
        3. Filter empty tokens

        Args:
            log_message: Raw log message

        Returns:
            List of tokens
        """
        # Remove timestamps (common pattern: YYYY-MM-DD HH:MM:SS)
        log_message = re.sub(r'\d{4}-\d{2}-\d{2}[\sT]\d{2}:\d{2}:\d{2}', '<TIMESTAMP>', log_message)

        # Remove IP addresses (IPv4 pattern)
        log_message = re.sub(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '<IP>', log_message)

        # Remove numbers (but keep words with numbers like "user001")
        log_message = re.sub(r'\b\d+\b', '<NUM>', log_message)

        # Remove special characters but keep alphanumeric, space, hyphen, underscore
        log_message = re.sub(r'[^\w\s\-]', ' ', log_message)

        # Split into tokens
        tokens = log_message.split()

        # Filter empty tokens
        tokens = [t for t in tokens if t]

        return tokens

    def has_numbers(self, token: str) -> bool:
        """Check if token contains any digits."""
        return bool(re.search(r'\d', token))

    def tree_search(self, tokens: List[str]) -> Node:
        """
        Search parse tree to find the leaf node for the log.

        Navigation:
        1. Layer 1 (root): Start at root
        2. Layer 2 (length): Navigate by token count
        3. Layers 3+: Navigate by first tokens (or <*> for wildcards)

        Args:
            tokens: Preprocessed log tokens

        Returns:
            Leaf node containing cluster IDs
        """
        # Layer 1: Root node
        current_node = self.root_node

        # Layer 2: Length node
        log_length = len(tokens)
        length_str = str(log_length)

        if length_str not in current_node.children:
            current_node.children[length_str] = Node(length_str, 1)

        current_node = current_node.children[length_str]

        # Layers 3+: Navigate by tokens
        for idx in range(min(self.depth, len(tokens))):
            token = tokens[idx]

            # Check if token contains digits - use wildcard path
            if self.has_numbers(token):
                token_key = "<*>"
            else:
                token_key = token

            # If too many children, use wildcard
            if token_key not in current_node.children:
                if len(current_node.children) >= self.max_children:
                    token_key = "<*>"

                if token_key not in current_node.children:
                    current_node.children[token_key] = Node(token_key, current_node.depth + 1)

            current_node = current_node.children[token_key]

        return current_node

    def calculate_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """
        Calculate similarity between two token sequences.

        Similarity = (number of matching tokens) / (total tokens)
        Wildcards <*> match any token.

        Args:
            tokens1: First token sequence (log message)
            tokens2: Second token sequence (template)

        Returns:
            Similarity score (0-1)
        """
        if len(tokens1) != len(tokens2):
            return 0.0

        matching_tokens = 0

        for t1, t2 in zip(tokens1, tokens2):
            if t1 == t2 or t2 == "<*>":
                matching_tokens += 1

        similarity = matching_tokens / len(tokens1) if len(tokens1) > 0 else 0.0

        return similarity

    def find_best_cluster(self, leaf_node: Node, tokens: List[str]) -> Optional[LogCluster]:
        """
        Find the best matching cluster at a leaf node.

        Args:
            leaf_node: Leaf node from tree search
            tokens: Preprocessed log tokens

        Returns:
            Best matching cluster, or None if no match above threshold
        """
        best_cluster = None
        max_similarity = 0.0

        for cluster_id in leaf_node.cluster_ids:
            cluster = self.log_clusters[cluster_id]
            similarity = self.calculate_similarity(tokens, cluster.log_template)

            if similarity > max_similarity:
                max_similarity = similarity
                best_cluster = cluster

        # Return cluster only if similarity is above threshold
        if max_similarity >= self.similarity_threshold:
            return best_cluster
        else:
            return None

    def create_template(self, tokens1: List[str], tokens2: List[str]) -> List[str]:
        """
        Create a template by merging two token sequences.

        Matching tokens are kept, differing tokens become wildcards <*>.

        Args:
            tokens1: First token sequence
            tokens2: Second token sequence

        Returns:
            Template with wildcards
        """
        if len(tokens1) != len(tokens2):
            raise ValueError("Token sequences must have same length")

        template = []

        for t1, t2 in zip(tokens1, tokens2):
            if t1 == t2:
                template.append(t1)
            else:
                template.append("<*>")

        return template

    def add_cluster(self, leaf_node: Node, tokens: List[str]) -> LogCluster:
        """
        Create a new cluster at a leaf node.

        Args:
            leaf_node: Leaf node from tree search
            tokens: Log tokens for the new cluster

        Returns:
            Newly created cluster
        """
        new_cluster = LogCluster(tokens, self.cluster_counter)
        self.log_clusters[self.cluster_counter] = new_cluster
        leaf_node.cluster_ids.append(self.cluster_counter)

        self.cluster_counter += 1
        self.template_count += 1

        return new_cluster

    def parse_log(self, log_id: str, log_message: str) -> Tuple[str, List[str]]:
        """
        Parse a single log message.

        Workflow:
        1. Preprocess log message
        2. Search parse tree
        3. Find best matching cluster
        4. Update cluster or create new one
        5. Return template

        Args:
            log_id: Unique log event ID
            log_message: Raw log message

        Returns:
            Tuple of (template_string, template_tokens)
        """
        # Preprocess
        tokens = self.preprocess(log_message)

        if not tokens:
            return "<EMPTY>", ["<EMPTY>"]

        # Tree search
        leaf_node = self.tree_search(tokens)

        # Find best matching cluster
        matched_cluster = self.find_best_cluster(leaf_node, tokens)

        if matched_cluster:
            # Update existing cluster
            matched_cluster.add_log_id(log_id)

            # Refine template
            new_template = self.create_template(matched_cluster.log_template, tokens)
            matched_cluster.log_template = new_template
        else:
            # Create new cluster
            if self.cluster_counter >= self.max_clusters:
                # Reuse oldest cluster (simple strategy)
                self.logger.warning(f"Max clusters ({self.max_clusters}) reached")
                matched_cluster = self.log_clusters[0]
                matched_cluster.add_log_id(log_id)
            else:
                matched_cluster = self.add_cluster(leaf_node, tokens)
                matched_cluster.add_log_id(log_id)

        self.parsed_count += 1

        if self.parsed_count % 10000 == 0:
            self.logger.info(f"Parsed {self.parsed_count} logs, "
                           f"{self.template_count} templates")

        template_str = matched_cluster.get_template_str()

        return template_str, matched_cluster.log_template

    def parse_dataset(
        self,
        df: pd.DataFrame,
        log_column: str = "log_message",
        id_column: str = "event_id"
    ) -> pd.DataFrame:
        """
        Parse an entire dataset of log messages.

        Args:
            df: DataFrame containing log messages
            log_column: Column name for log messages
            id_column: Column name for event IDs

        Returns:
            DataFrame with added columns: log_template, template_tokens
        """
        self.logger.info(f"Parsing {len(df)} log messages...")

        templates = []
        template_tokens_list = []

        for idx, row in df.iterrows():
            log_id = row[id_column]
            log_message = row[log_column]

            template_str, template_tokens = self.parse_log(log_id, log_message)

            templates.append(template_str)
            template_tokens_list.append(template_tokens)

        # Add columns
        df['log_template'] = templates
        df['template_tokens'] = template_tokens_list

        self.logger.info(f"Parsing complete: {self.parsed_count} logs, "
                        f"{self.template_count} unique templates")

        return df

    def get_templates(self) -> Dict[int, Dict[str, Any]]:
        """
        Get all extracted templates.

        Returns:
            Dictionary of cluster_id -> template info
        """
        templates = {}

        for cluster_id, cluster in self.log_clusters.items():
            templates[cluster_id] = {
                "cluster_id": cluster_id,
                "template": cluster.get_template_str(),
                "template_tokens": cluster.log_template,
                "log_count": cluster.size,
                "log_ids": cluster.log_ids[:10]  # Sample of log IDs
            }

        return templates

    def save_templates(self, filename: str = "log_templates.json") -> Path:
        """
        Save extracted templates to JSON file.

        Args:
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename

        templates = self.get_templates()

        # Create summary
        output_data = {
            "metadata": {
                "total_logs_parsed": self.parsed_count,
                "unique_templates": self.template_count,
                "depth": self.depth + 2,
                "similarity_threshold": self.similarity_threshold,
                "max_clusters": self.max_clusters
            },
            "templates": templates
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        self.logger.info(f"Templates saved to {output_path}")

        return output_path

    def save_parsed_dataset(
        self,
        df: pd.DataFrame,
        filename: str = "parsed_logs.csv"
    ) -> Path:
        """
        Save parsed dataset with templates.

        Args:
            df: Parsed DataFrame
            filename: Output filename

        Returns:
            Path to saved file
        """
        output_path = self.output_dir / filename

        # Drop template_tokens column (list type, not CSV-friendly)
        df_to_save = df.drop(columns=['template_tokens'], errors='ignore')

        df_to_save.to_csv(output_path, index=False)

        self.logger.info(f"Parsed dataset saved to {output_path}")

        return output_path

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get parsing statistics.

        Returns:
            Dictionary of statistics
        """
        cluster_sizes = [cluster.size for cluster in self.log_clusters.values()]

        stats = {
            "total_logs_parsed": self.parsed_count,
            "unique_templates": self.template_count,
            "average_cluster_size": np.mean(cluster_sizes) if cluster_sizes else 0,
            "median_cluster_size": np.median(cluster_sizes) if cluster_sizes else 0,
            "max_cluster_size": max(cluster_sizes) if cluster_sizes else 0,
            "min_cluster_size": min(cluster_sizes) if cluster_sizes else 0,
            "compression_ratio": self.parsed_count / self.template_count if self.template_count > 0 else 0
        }

        return stats


def main():
    """
    Main function to demonstrate log parser usage.

    Workflow:
    1. Load configuration
    2. Load synthetic dataset
    3. Parse log messages
    4. Save parsed dataset and templates
    5. Print statistics
    """
    print("\n" + "="*60)
    print("LOG PARSER - DRAIN ALGORITHM")
    print("="*60 + "\n")

    # Load configuration
    config_loader = ConfigLoader()
    data_config = config_loader.load_data_config()

    parser_config = data_config.get('log_parser', {})

    # Initialize parser
    parser = DrainParser(
        depth=parser_config.get('depth', 4),
        similarity_threshold=parser_config.get('similarity_threshold', 0.5),
        max_children=parser_config.get('max_children', 100),
        max_clusters=parser_config.get('max_clusters', 1000)
    )

    print("✅ Drain parser initialized")
    print(f"   Depth: {parser_config.get('depth', 4)}")
    print(f"   Similarity threshold: {parser_config.get('similarity_threshold', 0.5)}")
    print(f"   Max clusters: {parser_config.get('max_clusters', 1000)}")
    print()

    # Check if synthetic dataset exists
    synthetic_dir = Path("data/synthetic")
    train_file = synthetic_dir / "compliance_events_train.csv"

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

    # Parse logs (use sample for testing)
    sample_size = min(10000, len(df))
    df_sample = df.head(sample_size).copy()

    print(f"🔍 Parsing {sample_size} log messages...")
    print()

    parsed_df = parser.parse_dataset(df_sample)

    # Save results
    print("\n💾 Saving results...")
    templates_path = parser.save_templates()
    parsed_path = parser.save_parsed_dataset(parsed_df)

    print(f"✅ Templates saved: {templates_path}")
    print(f"✅ Parsed logs saved: {parsed_path}")
    print()

    # Statistics
    print("="*60)
    print("PARSING STATISTICS")
    print("="*60)

    stats = parser.get_statistics()

    print(f"Total logs parsed: {stats['total_logs_parsed']:,}")
    print(f"Unique templates: {stats['unique_templates']:,}")
    print(f"Compression ratio: {stats['compression_ratio']:.2f}x")
    print(f"Average cluster size: {stats['average_cluster_size']:.1f}")
    print(f"Median cluster size: {stats['median_cluster_size']:.0f}")
    print(f"Max cluster size: {stats['max_cluster_size']:,}")
    print(f"Min cluster size: {stats['min_cluster_size']:,}")
    print()

    # Show sample templates
    print("="*60)
    print("SAMPLE TEMPLATES (Top 10 by frequency)")
    print("="*60)

    templates = parser.get_templates()
    sorted_templates = sorted(
        templates.values(),
        key=lambda x: x['log_count'],
        reverse=True
    )

    for i, template_info in enumerate(sorted_templates[:10], 1):
        print(f"\n{i}. Template ID: {template_info['cluster_id']}")
        print(f"   Count: {template_info['log_count']}")
        print(f"   Template: {template_info['template']}")

    print("\n" + "="*60)
    print("✅ LOG PARSING COMPLETE!")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
