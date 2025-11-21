"""
Public Datasets Downloader for Compliance Monitoring

Downloads and preprocesses:
1. CICIDS 2017 - Network intrusion detection
2. NSL-KDD / UNSW-NB15 - Network attacks
3. CERT Insider Threat - User activity logs
4. LogHub - System logs for parsing

Author: Moise Iradukunda (CMU)
Date: October 2025
"""

import os
import requests
import zipfile
import tarfile
import gzip
import shutil
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging
from urllib.parse import urlparse
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import setup_logger


class PublicDatasetsDownloader:
    """Download and preprocess public security datasets."""

    # Dataset URLs
    DATASETS = {
        'CICIDS2017': {
            'name': 'CICIDS 2017',
            'urls': [
                'https://www.unb.ca/cic/datasets/ids-2017.html',  # Official page
                # Note: CICIDS 2017 requires manual download from UNB
            ],
            'description': 'Network intrusion detection dataset with benign and attack traffic',
            'format': 'CSV',
            'size': '~6GB',
            'manual': True
        },
        'NSL-KDD': {
            'name': 'NSL-KDD',
            'urls': [
                'https://github.com/defcom17/NSL_KDD/raw/master/KDDTrain+.txt',
                'https://github.com/defcom17/NSL_KDD/raw/master/KDDTest+.txt',
            ],
            'description': 'Improved KDD Cup 99 dataset for intrusion detection',
            'format': 'TXT',
            'size': '~10MB',
            'manual': False
        },
        'UNSW-NB15': {
            'name': 'UNSW-NB15',
            'urls': [
                'https://cloudstor.aarnet.edu.au/plus/s/2DhnLGDdEECo4ys/download',  # Training set
            ],
            'description': 'Modern network intrusion dataset with 9 attack categories',
            'format': 'CSV',
            'size': '~2GB',
            'manual': True  # Requires UNSW portal access
        },
        'CERT': {
            'name': 'CERT Insider Threat',
            'urls': [
                'https://kilthub.cmu.edu/articles/dataset/Insider_Threat_Test_Dataset/12841247',
            ],
            'description': 'User activity logs with insider threat scenarios',
            'format': 'CSV',
            'size': '~500MB',
            'manual': True  # Requires CMU CERT registration
        },
        'LogHub': {
            'name': 'LogHub',
            'urls': [
                'https://zenodo.org/record/3227177/files/Hadoop.tar.gz',
                'https://zenodo.org/record/3227177/files/HDFS.tar.gz',
                'https://zenodo.org/record/3227177/files/Linux.tar.gz',
                'https://zenodo.org/record/3227177/files/OpenStack.tar.gz',
            ],
            'description': 'System logs from distributed applications',
            'format': 'LOG',
            'size': '~1GB',
            'manual': False
        }
    }

    # NSL-KDD column names
    NSL_KDD_COLUMNS = [
        'duration', 'protocol_type', 'service', 'flag', 'src_bytes', 'dst_bytes',
        'land', 'wrong_fragment', 'urgent', 'hot', 'num_failed_logins',
        'logged_in', 'num_compromised', 'root_shell', 'su_attempted', 'num_root',
        'num_file_creations', 'num_shells', 'num_access_files', 'num_outbound_cmds',
        'is_host_login', 'is_guest_login', 'count', 'srv_count', 'serror_rate',
        'srv_serror_rate', 'rerror_rate', 'srv_rerror_rate', 'same_srv_rate',
        'diff_srv_rate', 'srv_diff_host_rate', 'dst_host_count', 'dst_host_srv_count',
        'dst_host_same_srv_rate', 'dst_host_diff_srv_rate', 'dst_host_same_src_port_rate',
        'dst_host_srv_diff_host_rate', 'dst_host_serror_rate', 'dst_host_srv_serror_rate',
        'dst_host_rerror_rate', 'dst_host_srv_rerror_rate', 'label', 'difficulty'
    ]

    def __init__(self, output_dir: str = "data/public"):
        """
        Initialize downloader.

        Args:
            output_dir: Directory to save downloaded datasets
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger("public_datasets", "logs/public_datasets.log")
        self.logger.info("Public Datasets Downloader initialized")

    def download_file(self, url: str, output_path: Path, chunk_size: int = 8192) -> bool:
        """
        Download a file with progress bar.

        Args:
            url: URL to download from
            output_path: Path to save file
            chunk_size: Download chunk size

        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Downloading from {url}")

            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            with open(output_path, 'wb') as f:
                with tqdm(total=total_size, unit='B', unit_scale=True, desc=output_path.name) as pbar:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)
                            pbar.update(len(chunk))

            self.logger.info(f"Downloaded successfully: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            return False

    def extract_archive(self, archive_path: Path, extract_to: Path) -> bool:
        """
        Extract archive file (zip, tar.gz, gz).

        Args:
            archive_path: Path to archive
            extract_to: Directory to extract to

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Extracting {archive_path}")

            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)

            elif archive_path.suffix == '.gz':
                if archive_path.stem.endswith('.tar'):
                    # tar.gz file
                    with tarfile.open(archive_path, 'r:gz') as tar_ref:
                        tar_ref.extractall(extract_to)
                else:
                    # .gz file
                    output_path = extract_to / archive_path.stem
                    with gzip.open(archive_path, 'rb') as f_in:
                        with open(output_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)

            elif '.tar' in archive_path.suffixes:
                with tarfile.open(archive_path, 'r') as tar_ref:
                    tar_ref.extractall(extract_to)

            self.logger.info(f"Extracted to {extract_to}")
            return True

        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return False

    def download_nsl_kdd(self) -> bool:
        """Download NSL-KDD dataset."""
        self.logger.info("Downloading NSL-KDD dataset")

        dataset_dir = self.output_dir / "NSL-KDD"
        dataset_dir.mkdir(exist_ok=True)

        urls = self.DATASETS['NSL-KDD']['urls']

        for url in urls:
            filename = url.split('/')[-1]
            output_path = dataset_dir / filename

            if output_path.exists():
                self.logger.info(f"Already exists: {output_path}")
                continue

            success = self.download_file(url, output_path)
            if not success:
                return False

        # Convert to CSV with proper column names
        self._convert_nsl_kdd_to_csv(dataset_dir)

        return True

    def _convert_nsl_kdd_to_csv(self, dataset_dir: Path):
        """Convert NSL-KDD .txt files to CSV with column names."""
        for txt_file in dataset_dir.glob("*.txt"):
            csv_file = txt_file.with_suffix('.csv')

            if csv_file.exists():
                continue

            self.logger.info(f"Converting {txt_file} to CSV")

            try:
                # Read raw data
                df = pd.read_csv(txt_file, header=None, names=self.NSL_KDD_COLUMNS)

                # Save as CSV
                df.to_csv(csv_file, index=False)
                self.logger.info(f"Saved: {csv_file}")

            except Exception as e:
                self.logger.error(f"Conversion failed: {e}")

    def download_loghub(self) -> bool:
        """Download LogHub datasets."""
        self.logger.info("Downloading LogHub datasets")

        dataset_dir = self.output_dir / "LogHub"
        dataset_dir.mkdir(exist_ok=True)

        urls = self.DATASETS['LogHub']['urls']

        for url in urls:
            filename = url.split('/')[-1]
            archive_path = dataset_dir / filename
            extract_dir = dataset_dir / filename.replace('.tar.gz', '')

            if extract_dir.exists():
                self.logger.info(f"Already extracted: {extract_dir}")
                continue

            # Download
            success = self.download_file(url, archive_path)
            if not success:
                continue

            # Extract
            self.extract_archive(archive_path, extract_dir)

            # Clean up archive
            archive_path.unlink()

        return True

    def print_manual_instructions(self):
        """Print instructions for manually downloadable datasets."""
        print("\n" + "=" * 80)
        print("MANUAL DOWNLOAD REQUIRED FOR SOME DATASETS")
        print("=" * 80)

        for dataset_name, info in self.DATASETS.items():
            if info['manual']:
                print(f"\n📦 {info['name']}")
                print(f"   Description: {info['description']}")
                print(f"   Size: {info['size']}")
                print(f"   Format: {info['format']}")
                print(f"   Download from: {info['urls'][0]}")
                print(f"   Save to: {self.output_dir / dataset_name}/")
                print()

        print("=" * 80)
        print("\n✅ Automated downloads will begin now...")
        print()

    def download_all_automatic(self):
        """Download all datasets that don't require manual download."""
        self.logger.info("Starting automatic downloads")

        # Print manual instructions first
        self.print_manual_instructions()

        # Download NSL-KDD
        print("\n📥 Downloading NSL-KDD...")
        success = self.download_nsl_kdd()
        if success:
            print("✅ NSL-KDD downloaded successfully")
        else:
            print("❌ NSL-KDD download failed")

        # Download LogHub
        print("\n📥 Downloading LogHub...")
        success = self.download_loghub()
        if success:
            print("✅ LogHub downloaded successfully")
        else:
            print("❌ LogHub download failed")

        print("\n" + "=" * 80)
        print("DOWNLOAD SUMMARY")
        print("=" * 80)
        print("\n✅ Automatic downloads complete!")
        print(f"📁 Downloaded to: {self.output_dir}")
        print("\n⚠️  Remember to manually download:")
        print("   • CICIDS 2017 (from UNB CIC)")
        print("   • UNSW-NB15 (from UNSW)")
        print("   • CERT Insider Threat (from CMU CERT)")
        print("\n" + "=" * 80)

    def create_dataset_info(self):
        """Create README with dataset information."""
        readme_path = self.output_dir / "README.md"

        content = """# Public Security Datasets

Downloaded datasets for Rwanda NCSA compliance monitoring model training.

## Datasets

### 1. CICIDS 2017
- **Description**: Network intrusion detection with benign and attack traffic
- **Size**: ~6GB
- **Format**: CSV
- **Use**: Train baseline classifiers (Random Forest, SVM, LSTM)
- **Source**: UNB Canadian Institute for Cybersecurity

### 2. NSL-KDD
- **Description**: Improved KDD Cup 99 for intrusion detection
- **Size**: ~10MB
- **Format**: CSV (converted from TXT)
- **Use**: Cross-dataset generalization testing
- **Source**: GitHub defcom17/NSL_KDD

### 3. UNSW-NB15
- **Description**: Modern network intrusion with 9 attack categories
- **Size**: ~2GB
- **Format**: CSV
- **Use**: Augment training data, test generalization
- **Source**: UNSW Canberra

### 4. CERT Insider Threat
- **Description**: User activity logs with insider threat scenarios
- **Size**: ~500MB
- **Format**: CSV
- **Use**: Generate realistic user behavior patterns
- **Source**: CMU CERT Division

### 5. LogHub
- **Description**: System logs from distributed applications
- **Size**: ~1GB
- **Format**: LOG files
- **Applications**: Hadoop, HDFS, Linux, OpenStack
- **Use**: Train log parsing and template extraction
- **Source**: Zenodo LogHub repository

## Directory Structure

```
data/public/
├── NSL-KDD/
│   ├── KDDTrain+.csv
│   └── KDDTest+.csv
├── LogHub/
│   ├── Hadoop/
│   ├── HDFS/
│   ├── Linux/
│   └── OpenStack/
├── CICIDS2017/  (manual download)
├── UNSW-NB15/   (manual download)
└── CERT/        (manual download)
```

## Usage

```python
from src.data_pipeline.public_datasets_downloader import PublicDatasetsDownloader

# Download datasets
downloader = PublicDatasetsDownloader()
downloader.download_all_automatic()

# Manual downloads required for:
# - CICIDS 2017
# - UNSW-NB15
# - CERT Insider Threat
```

## Citations

[16] UNB CIC. "CICIDS 2017 Dataset." https://www.unb.ca/cic/datasets/ids-2017.html

[17] UNSW. "UNSW-NB15 Dataset." https://research.unsw.edu.au/projects/unsw-nb15-dataset

[18] CMU CERT. "Insider Threat Test Dataset." https://kilthub.cmu.edu/

[19] LogHub. "Log Datasets for System Log Analytics." https://zenodo.org/record/3227177

---

Generated by Public Datasets Downloader
Rwanda NCSA Compliance Monitoring Project
"""

        readme_path.write_text(content)
        self.logger.info(f"Created README: {readme_path}")


def main():
    """Main entry point."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║   Public Security Datasets Downloader                        ║
║   Rwanda NCSA Compliance Monitoring Project                  ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Initialize downloader
    downloader = PublicDatasetsDownloader()

    # Download all automatic datasets
    downloader.download_all_automatic()

    # Create dataset info
    downloader.create_dataset_info()

    print("\n✅ Setup complete!")
    print(f"📁 Datasets location: {downloader.output_dir}")
    print("\n💡 Next steps:")
    print("   1. Manually download CICIDS 2017, UNSW-NB15, CERT")
    print("   2. Run preprocessing pipeline")
    print("   3. Train models with public datasets")


if __name__ == "__main__":
    main()
