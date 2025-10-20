"""
Public Dataset Integration for Benchmarking.

This module provides utilities for downloading and preprocessing public log datasets:
1. HDFS (Hadoop Distributed File System) logs
2. BGL (BlueGene/L) supercomputer logs
3. NSL-KDD network intrusion dataset

These datasets are used for:
- Validating log parser performance
- Benchmarking model accuracy
- Comparing with baseline results from literature
- Testing generalization to different log formats

Public Datasets:
- HDFS: 11M log messages, anomaly detection
- BGL: 4.7M log messages, failure prediction
- NSL-KDD: Network intrusion detection (optional)

References:
- Xu et al. (2009). Detecting large-scale system problems by mining console logs. SOSP.
- Oliner & Stearley (2007). What supercomputers say: A study of five system logs. DSN.
- Loghub: https://github.com/logpai/loghub
"""

import os
import requests
import tarfile
import gzip
import shutil
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import pandas as pd
from tqdm import tqdm

from ..utils.config_loader import ConfigLoader
from ..utils.logger import setup_logger


class PublicDatasetDownloader:
    """
    Download and extract public log datasets.

    Handles downloading from URLs, extracting archives, and organizing files.
    """

    def __init__(self, cache_dir: str = "data/public_datasets"):
        """
        Initialize dataset downloader.

        Args:
            cache_dir: Directory to cache downloaded datasets
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger("dataset_downloader", "logs/public_datasets.log")

    def download_file(
        self,
        url: str,
        output_path: Path,
        chunk_size: int = 8192
    ) -> bool:
        """
        Download file from URL with progress bar.

        Args:
            url: Download URL
            output_path: Output file path
            chunk_size: Download chunk size in bytes

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Downloading: {url}")

            response = requests.get(url, stream=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            self.logger.info(f"Downloaded: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            return False

    def extract_tar_gz(self, tar_path: Path, extract_dir: Path) -> bool:
        """
        Extract .tar.gz archive.

        Args:
            tar_path: Path to .tar.gz file
            extract_dir: Extraction directory

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Extracting: {tar_path}")

            with tarfile.open(tar_path, 'r:gz') as tar:
                tar.extractall(extract_dir)

            self.logger.info(f"Extracted to: {extract_dir}")
            return True

        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return False

    def extract_gz(self, gz_path: Path, output_path: Path) -> bool:
        """
        Extract .gz file.

        Args:
            gz_path: Path to .gz file
            output_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Extracting: {gz_path}")

            with gzip.open(gz_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            self.logger.info(f"Extracted to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return False


class HDFSDataset:
    """
    HDFS (Hadoop Distributed File System) log dataset.

    Dataset details:
    - 11M log messages
    - 575 unique templates
    - Binary labels: normal vs anomaly
    - Used for anomaly detection

    Format: Each log line contains:
    - Date, time
    - Process ID
    - Log level
    - Component
    - Message content
    """

    def __init__(self, data_dir: str = "data/public_datasets/hdfs"):
        """
        Initialize HDFS dataset handler.

        Args:
            data_dir: Directory for HDFS data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger("hdfs_dataset", "logs/public_datasets.log")

        self.url = "https://zenodo.org/record/3227177/files/HDFS_v1.tar.gz"
        self.downloader = PublicDatasetDownloader()

    def download(self) -> bool:
        """
        Download HDFS dataset.

        Returns:
            True if successful, False otherwise
        """
        archive_path = self.data_dir / "HDFS_v1.tar.gz"

        if archive_path.exists():
            self.logger.info(f"Archive already exists: {archive_path}")
            return True

        success = self.downloader.download_file(self.url, archive_path)

        if success:
            self.downloader.extract_tar_gz(archive_path, self.data_dir)

        return success

    def load(self, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load HDFS dataset.

        Args:
            sample_size: If provided, load only N samples

        Returns:
            DataFrame with HDFS logs
        """
        # Check for common HDFS file patterns
        possible_files = [
            self.data_dir / "HDFS.log",
            self.data_dir / "HDFS_v1" / "HDFS.log",
            self.data_dir / "HDFS" / "HDFS.log"
        ]

        log_file = None
        for f in possible_files:
            if f.exists():
                log_file = f
                break

        if log_file is None:
            self.logger.warning("HDFS log file not found. Please download first.")
            return pd.DataFrame()

        self.logger.info(f"Loading HDFS logs from: {log_file}")

        # Read log file
        logs = []

        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if sample_size and i >= sample_size:
                    break

                logs.append({'log_message': line.strip()})

        df = pd.DataFrame(logs)

        self.logger.info(f"Loaded {len(df)} HDFS log messages")

        return df


class BGLDataset:
    """
    BGL (BlueGene/L) supercomputer log dataset.

    Dataset details:
    - 4.7M log messages
    - 120 unique templates
    - Binary labels: normal vs failure
    - Used for failure prediction

    Format: Each log line contains:
    - Alert type
    - Timestamp
    - Severity
    - Location
    - Message content
    """

    def __init__(self, data_dir: str = "data/public_datasets/bgl"):
        """
        Initialize BGL dataset handler.

        Args:
            data_dir: Directory for BGL data
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger("bgl_dataset", "logs/public_datasets.log")

        self.url = "https://zenodo.org/record/3227177/files/BGL.tar.gz"
        self.downloader = PublicDatasetDownloader()

    def download(self) -> bool:
        """
        Download BGL dataset.

        Returns:
            True if successful, False otherwise
        """
        archive_path = self.data_dir / "BGL.tar.gz"

        if archive_path.exists():
            self.logger.info(f"Archive already exists: {archive_path}")
            return True

        success = self.downloader.download_file(self.url, archive_path)

        if success:
            self.downloader.extract_tar_gz(archive_path, self.data_dir)

        return success

    def load(self, sample_size: Optional[int] = None) -> pd.DataFrame:
        """
        Load BGL dataset.

        Args:
            sample_size: If provided, load only N samples

        Returns:
            DataFrame with BGL logs
        """
        # Check for common BGL file patterns
        possible_files = [
            self.data_dir / "BGL.log",
            self.data_dir / "BGL" / "BGL.log"
        ]

        log_file = None
        for f in possible_files:
            if f.exists():
                log_file = f
                break

        if log_file is None:
            self.logger.warning("BGL log file not found. Please download first.")
            return pd.DataFrame()

        self.logger.info(f"Loading BGL logs from: {log_file}")

        # Read log file
        logs = []

        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for i, line in enumerate(f):
                if sample_size and i >= sample_size:
                    break

                logs.append({'log_message': line.strip()})

        df = pd.DataFrame(logs)

        self.logger.info(f"Loaded {len(df)} BGL log messages")

        return df


class PublicDatasetIntegrator:
    """
    Main integrator for public datasets.

    Provides unified interface for downloading, loading, and preprocessing
    public log datasets for benchmarking.
    """

    def __init__(self):
        """Initialize public dataset integrator."""
        self.logger = setup_logger("public_datasets", "logs/public_datasets.log")

        # Initialize dataset handlers
        self.hdfs = HDFSDataset()
        self.bgl = BGLDataset()

        # Load configuration
        config_loader = ConfigLoader()
        self.data_config = config_loader.load_data_config()

        self.public_datasets_config = self.data_config.get('public_datasets', {})

    def download_all(self) -> Dict[str, bool]:
        """
        Download all enabled public datasets.

        Returns:
            Dictionary of dataset_name -> success status
        """
        results = {}

        # HDFS
        if self.public_datasets_config.get('hdfs', {}).get('enabled', False):
            self.logger.info("Downloading HDFS dataset...")
            results['hdfs'] = self.hdfs.download()
        else:
            self.logger.info("HDFS dataset disabled in config")
            results['hdfs'] = False

        # BGL
        if self.public_datasets_config.get('bgl', {}).get('enabled', False):
            self.logger.info("Downloading BGL dataset...")
            results['bgl'] = self.bgl.download()
        else:
            self.logger.info("BGL dataset disabled in config")
            results['bgl'] = False

        return results

    def load_dataset(
        self,
        dataset_name: str,
        sample_size: Optional[int] = 10000
    ) -> pd.DataFrame:
        """
        Load a specific public dataset.

        Args:
            dataset_name: Name of dataset (hdfs, bgl)
            sample_size: Number of samples to load (None for all)

        Returns:
            DataFrame with log messages
        """
        if dataset_name.lower() == 'hdfs':
            return self.hdfs.load(sample_size=sample_size)
        elif dataset_name.lower() == 'bgl':
            return self.bgl.load(sample_size=sample_size)
        else:
            self.logger.error(f"Unknown dataset: {dataset_name}")
            return pd.DataFrame()

    def get_available_datasets(self) -> List[str]:
        """
        Get list of available datasets.

        Returns:
            List of dataset names
        """
        available = []

        # Check HDFS
        if (self.hdfs.data_dir / "HDFS.log").exists():
            available.append("hdfs")

        # Check BGL
        if (self.bgl.data_dir / "BGL.log").exists():
            available.append("bgl")

        return available


def main():
    """
    Main function to demonstrate public dataset integration.

    Workflow:
    1. Load configuration
    2. Download enabled datasets
    3. Load sample data
    4. Display statistics
    """
    print("\n" + "="*60)
    print("PUBLIC DATASET INTEGRATION")
    print("="*60 + "\n")

    # Initialize integrator
    integrator = PublicDatasetIntegrator()

    print("✅ Public dataset integrator initialized")
    print()

    # Check configuration
    print("📋 Dataset Configuration:")
    print(f"   HDFS: {'Enabled' if integrator.public_datasets_config.get('hdfs', {}).get('enabled') else 'Disabled'}")
    print(f"   BGL: {'Enabled' if integrator.public_datasets_config.get('bgl', {}).get('enabled') else 'Disabled'}")
    print()

    # Check available datasets
    available = integrator.get_available_datasets()

    if available:
        print(f"📂 Available datasets: {', '.join(available)}")
        print()

        # Load sample from first available dataset
        dataset_name = available[0]

        print(f"📥 Loading sample from {dataset_name.upper()}...")
        df = integrator.load_dataset(dataset_name, sample_size=100)

        if not df.empty:
            print(f"✅ Loaded {len(df)} samples")
            print()

            print("="*60)
            print("SAMPLE LOG MESSAGES")
            print("="*60)

            for i in range(min(5, len(df))):
                print(f"\n{i+1}. {df.iloc[i]['log_message'][:100]}...")

            print()
        else:
            print("⚠️  Failed to load dataset")
            print()
    else:
        print("⚠️  No datasets available")
        print()

        # Offer to download
        print("📥 Download datasets? (This may take several minutes)")
        print("   Note: HDFS (~16MB), BGL (~700MB)")
        print()

        response = input("Download? (y/n): ").strip().lower()

        if response == 'y':
            print("\n🔽 Downloading datasets...")
            results = integrator.download_all()

            print("\n📊 Download Results:")
            for dataset, success in results.items():
                status = "✅ Success" if success else "❌ Failed"
                print(f"   {dataset.upper()}: {status}")

            print()
        else:
            print("\n⏭️  Skipping download")
            print()

    print("="*60)
    print("USAGE NOTES")
    print("="*60)

    print("""
Public datasets are used for:

1. Log Parser Validation
   - Test Drain algorithm on HDFS/BGL logs
   - Compare template extraction accuracy
   - Benchmark parsing speed

2. Model Benchmarking
   - Test compliance models on real log data
   - Compare with baseline results from literature
   - Evaluate generalization performance

3. Configuration:
   - Enable/disable in config/data_config.yaml
   - Set paths and usage type
   - Optional for Phase 4, recommended for Phase 8

To use:
  from src.data_pipeline.public_datasets import PublicDatasetIntegrator

  integrator = PublicDatasetIntegrator()
  hdfs_df = integrator.load_dataset('hdfs', sample_size=10000)
  # Process logs with Drain parser or models
    """)

    print("="*60)
    print("✅ PUBLIC DATASET INTEGRATION READY")
    print("="*60)
    print()


if __name__ == "__main__":
    main()
