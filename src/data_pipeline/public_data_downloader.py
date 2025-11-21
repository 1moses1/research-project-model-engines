"""
Public Cybersecurity Log Dataset Downloader

This script downloads and prepares public cybersecurity log datasets
for training compliance auditing models. Uses real-world logs but applies
Rwanda NCSA and NIST control mappings for compliance classification.

Supported Datasets:
1. Loghub HDFS - Hadoop Distributed File System logs (11M+ logs)
2. Loghub BGL - BlueGene/L supercomputer logs (4.7M logs)
3. LANL Cyber Security - Los Alamos authentication/network logs (1.6B events)
4. Apache HTTP Logs - Web server intrusion detection logs
5. Windows Event Logs - Security audit logs

Author: Moise Iradukunda (CMU)
Date: October 2025
"""

import os
import sys
import logging
import requests
import tarfile
import gzip
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_downloader.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PublicDatasetDownloader:
    """Download and prepare public cybersecurity log datasets"""

    def __init__(self, data_dir: str = "data/public"):
        """
        Initialize downloader

        Args:
            data_dir: Base directory for storing downloaded datasets
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Dataset URLs and metadata
        self.datasets = {
            'hdfs': {
                'name': 'HDFS Logs (Loghub)',
                'url': 'https://zenodo.org/record/3227177/files/HDFS_1.tar.gz',
                'size': '~43MB compressed',
                'total_logs': '11,175,629',
                'labeled': True,
                'description': 'Hadoop Distributed File System logs with anomaly labels'
            },
            'bgl': {
                'name': 'BGL Supercomputer Logs (Loghub)',
                'url': 'https://zenodo.org/record/3227177/files/BGL.tar.gz',
                'size': '~708MB compressed',
                'total_logs': '4,747,963',
                'labeled': True,
                'description': 'BlueGene/L supercomputer logs with alert labels'
            },
            'apache': {
                'name': 'Apache HTTP Logs (Intrusion Detection)',
                'url': 'https://github.com/ocatak/apache-http-logs/raw/master/apache_access_log.csv',
                'size': '~5MB',
                'total_logs': '~40,000',
                'labeled': True,
                'description': 'Apache access logs labeled for XSS/SQLI attacks'
            },
            'thunderbird': {
                'name': 'Thunderbird Logs (Loghub)',
                'url': 'https://zenodo.org/record/3227177/files/Thunderbird.tar.gz',
                'size': '~183MB compressed',
                'total_logs': '211,212,192',
                'labeled': True,
                'description': 'Thunderbird supercomputer logs with anomaly labels'
            },
            'linux_auth': {
                'name': 'Linux Auth Logs (SecRepo)',
                'url': 'http://www.secrepo.com/auth.log/auth.log.gz',
                'size': '~5MB compressed',
                'total_logs': '~86,000',
                'labeled': False,
                'description': 'Linux authentication logs (mostly failed SSH attempts)'
            }
        }

        logger.info(f"Initialized PublicDatasetDownloader")
        logger.info(f"Data directory: {self.data_dir}")

    def list_datasets(self):
        """Print available datasets"""
        logger.info("\n" + "="*80)
        logger.info("AVAILABLE PUBLIC CYBERSECURITY LOG DATASETS")
        logger.info("="*80)

        for key, info in self.datasets.items():
            logger.info(f"\n{key.upper()}:")
            logger.info(f"  Name: {info['name']}")
            logger.info(f"  Size: {info['size']}")
            logger.info(f"  Total Logs: {info['total_logs']}")
            logger.info(f"  Labeled: {info['labeled']}")
            logger.info(f"  Description: {info['description']}")
            logger.info(f"  URL: {info['url']}")

        logger.info("\n" + "="*80)

    def download_file(self, url: str, output_path: Path, chunk_size: int = 8192) -> bool:
        """
        Download file with progress bar

        Args:
            url: Download URL
            output_path: Path to save file
            chunk_size: Download chunk size in bytes

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Downloading from: {url}")
            logger.info(f"Saving to: {output_path}")

            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Stream download with progress bar
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            # Get total file size
            total_size = int(response.headers.get('content-length', 0))

            # Download with progress bar
            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=output_path.name) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            logger.info(f"✅ Downloaded successfully: {output_path.name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to download {url}: {e}")
            return False

    def extract_tar_gz(self, archive_path: Path, extract_dir: Path) -> bool:
        """
        Extract .tar.gz archive

        Args:
            archive_path: Path to archive file
            extract_dir: Directory to extract to

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Extracting {archive_path.name}...")
            extract_dir.mkdir(parents=True, exist_ok=True)

            with tarfile.open(archive_path, 'r:gz') as tar:
                tar.extractall(path=extract_dir)

            logger.info(f"✅ Extracted to: {extract_dir}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to extract {archive_path}: {e}")
            return False

    def extract_gz(self, archive_path: Path, output_path: Path) -> bool:
        """
        Extract .gz file

        Args:
            archive_path: Path to .gz file
            output_path: Path for extracted file

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Extracting {archive_path.name}...")

            with gzip.open(archive_path, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            logger.info(f"✅ Extracted to: {output_path}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to extract {archive_path}: {e}")
            return False

    def download_hdfs(self) -> bool:
        """Download and extract HDFS logs"""
        dataset_dir = self.data_dir / "hdfs"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Download
        archive_path = dataset_dir / "HDFS_1.tar.gz"
        if not archive_path.exists():
            if not self.download_file(self.datasets['hdfs']['url'], archive_path):
                return False
        else:
            logger.info(f"Archive already exists: {archive_path}")

        # Extract
        extract_dir = dataset_dir / "extracted"
        if not (extract_dir / "HDFS").exists():
            if not self.extract_tar_gz(archive_path, extract_dir):
                return False
        else:
            logger.info(f"Already extracted: {extract_dir}")

        logger.info(f"✅ HDFS dataset ready at: {dataset_dir}")
        return True

    def download_bgl(self) -> bool:
        """Download and extract BGL logs"""
        dataset_dir = self.data_dir / "bgl"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Download
        archive_path = dataset_dir / "BGL.tar.gz"
        if not archive_path.exists():
            if not self.download_file(self.datasets['bgl']['url'], archive_path):
                return False
        else:
            logger.info(f"Archive already exists: {archive_path}")

        # Extract
        extract_dir = dataset_dir / "extracted"
        if not (extract_dir / "BGL").exists():
            if not self.extract_tar_gz(archive_path, extract_dir):
                return False
        else:
            logger.info(f"Already extracted: {extract_dir}")

        logger.info(f"✅ BGL dataset ready at: {dataset_dir}")
        return True

    def download_apache(self) -> bool:
        """Download Apache HTTP logs"""
        dataset_dir = self.data_dir / "apache"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Download CSV directly
        csv_path = dataset_dir / "apache_access_log.csv"
        if not csv_path.exists():
            if not self.download_file(self.datasets['apache']['url'], csv_path):
                return False
        else:
            logger.info(f"File already exists: {csv_path}")

        logger.info(f"✅ Apache dataset ready at: {dataset_dir}")
        return True

    def download_thunderbird(self) -> bool:
        """Download and extract Thunderbird logs"""
        dataset_dir = self.data_dir / "thunderbird"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Download
        archive_path = dataset_dir / "Thunderbird.tar.gz"
        if not archive_path.exists():
            if not self.download_file(self.datasets['thunderbird']['url'], archive_path):
                return False
        else:
            logger.info(f"Archive already exists: {archive_path}")

        # Extract
        extract_dir = dataset_dir / "extracted"
        if not (extract_dir / "Thunderbird").exists():
            if not self.extract_tar_gz(archive_path, extract_dir):
                return False
        else:
            logger.info(f"Already extracted: {extract_dir}")

        logger.info(f"✅ Thunderbird dataset ready at: {dataset_dir}")
        return True

    def download_linux_auth(self) -> bool:
        """Download and extract Linux auth logs"""
        dataset_dir = self.data_dir / "linux_auth"
        dataset_dir.mkdir(parents=True, exist_ok=True)

        # Download
        archive_path = dataset_dir / "auth.log.gz"
        if not archive_path.exists():
            if not self.download_file(self.datasets['linux_auth']['url'], archive_path):
                return False
        else:
            logger.info(f"Archive already exists: {archive_path}")

        # Extract
        output_path = dataset_dir / "auth.log"
        if not output_path.exists():
            if not self.extract_gz(archive_path, output_path):
                return False
        else:
            logger.info(f"Already extracted: {output_path}")

        logger.info(f"✅ Linux auth dataset ready at: {dataset_dir}")
        return True

    def download_all(self, datasets: Optional[List[str]] = None):
        """
        Download all specified datasets

        Args:
            datasets: List of dataset keys to download (None = all)
        """
        if datasets is None:
            datasets = ['hdfs', 'bgl', 'apache']  # Default: most relevant for compliance

        logger.info("\n" + "="*80)
        logger.info("DOWNLOADING PUBLIC DATASETS")
        logger.info("="*80)
        logger.info(f"Datasets to download: {', '.join(datasets)}")
        logger.info(f"Target directory: {self.data_dir}")
        logger.info("="*80 + "\n")

        results = {}

        for dataset in datasets:
            logger.info(f"\n{'='*80}")
            logger.info(f"DOWNLOADING: {dataset.upper()}")
            logger.info(f"{'='*80}")

            if dataset == 'hdfs':
                results[dataset] = self.download_hdfs()
            elif dataset == 'bgl':
                results[dataset] = self.download_bgl()
            elif dataset == 'apache':
                results[dataset] = self.download_apache()
            elif dataset == 'thunderbird':
                results[dataset] = self.download_thunderbird()
            elif dataset == 'linux_auth':
                results[dataset] = self.download_linux_auth()
            else:
                logger.warning(f"Unknown dataset: {dataset}")
                results[dataset] = False

        # Summary
        logger.info("\n" + "="*80)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("="*80)

        for dataset, success in results.items():
            status = "✅ SUCCESS" if success else "❌ FAILED"
            logger.info(f"{dataset.upper()}: {status}")

        total = len(results)
        successful = sum(results.values())
        logger.info(f"\nTotal: {successful}/{total} datasets downloaded successfully")
        logger.info("="*80 + "\n")

        return results


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Download public cybersecurity log datasets')
    parser.add_argument(
        '--datasets',
        nargs='+',
        choices=['hdfs', 'bgl', 'apache', 'thunderbird', 'linux_auth', 'all'],
        default=['hdfs', 'bgl', 'apache'],
        help='Datasets to download (default: hdfs bgl apache)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data/public',
        help='Directory to store downloaded datasets (default: data/public)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available datasets and exit'
    )

    args = parser.parse_args()

    # Initialize downloader
    downloader = PublicDatasetDownloader(data_dir=args.data_dir)

    # List datasets if requested
    if args.list:
        downloader.list_datasets()
        return

    # Handle 'all' option
    if 'all' in args.datasets:
        datasets = ['hdfs', 'bgl', 'apache', 'thunderbird', 'linux_auth']
    else:
        datasets = args.datasets

    # Download datasets
    results = downloader.download_all(datasets=datasets)

    # Exit code based on results
    if all(results.values()):
        logger.info("✅ All downloads completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Some downloads failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
