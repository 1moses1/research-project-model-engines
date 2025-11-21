#!/usr/bin/env python3
"""
Comprehensive Security Dataset Download Pipeline
Downloads large datasets in background: MITRE ATT&CK, NIST NVD, threat intel feeds
"""

import requests
import json
import gzip
import csv
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityDatasetDownloader:
    """Download and process large security datasets"""

    def __init__(self, data_dir: str = "data/security_feeds"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.data_dir / "mitre_attack").mkdir(exist_ok=True)
        (self.data_dir / "nist_nvd").mkdir(exist_ok=True)
        (self.data_dir / "threat_intel").mkdir(exist_ok=True)
        (self.data_dir / "cisa_advisories").mkdir(exist_ok=True)
        (self.data_dir / "malware_feeds").mkdir(exist_ok=True)
        (self.data_dir / "log_samples").mkdir(exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Security Research Bot)',
            'Accept': 'application/json'
        })

    def download_mitre_attack(self) -> Dict:
        """Download MITRE ATT&CK framework (Enterprise, Mobile, ICS)"""
        logger.info("Downloading MITRE ATT&CK datasets...")

        datasets = {
            'enterprise': 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json',
            'mobile': 'https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json',
            'ics': 'https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json'
        }

        results = {}
        for name, url in datasets.items():
            try:
                logger.info(f"  Downloading MITRE ATT&CK {name}...")
                response = self.session.get(url, timeout=120)
                response.raise_for_status()

                output_file = self.data_dir / "mitre_attack" / f"{name}-attack.json"
                with open(output_file, 'w') as f:
                    json.dump(response.json(), f, indent=2)

                # Extract techniques
                data = response.json()
                techniques = self._extract_attack_techniques(data)

                techniques_file = self.data_dir / "mitre_attack" / f"{name}-techniques.json"
                with open(techniques_file, 'w') as f:
                    json.dump(techniques, f, indent=2)

                results[name] = {
                    'status': 'success',
                    'file': str(output_file),
                    'techniques_count': len(techniques),
                    'size_mb': output_file.stat().st_size / (1024 * 1024)
                }
                logger.info(f"    ✓ {name}: {len(techniques)} techniques, {results[name]['size_mb']:.2f} MB")

            except Exception as e:
                logger.error(f"    ✗ Failed to download {name}: {e}")
                results[name] = {'status': 'error', 'error': str(e)}

        return results

    def _extract_attack_techniques(self, attack_data: Dict) -> List[Dict]:
        """Extract techniques from MITRE ATT&CK STIX format"""
        techniques = []

        for obj in attack_data.get('objects', []):
            if obj.get('type') == 'attack-pattern':
                technique = {
                    'id': obj.get('external_references', [{}])[0].get('external_id', ''),
                    'name': obj.get('name', ''),
                    'description': obj.get('description', ''),
                    'tactics': [phase['phase_name'] for phase in obj.get('kill_chain_phases', [])],
                    'platforms': obj.get('x_mitre_platforms', []),
                    'data_sources': obj.get('x_mitre_data_sources', [])
                }
                techniques.append(technique)

        return techniques

    def download_nist_nvd(self, years: int = 5) -> Dict:
        """Download NIST National Vulnerability Database (last N years)"""
        logger.info(f"Downloading NIST NVD (last {years} years)...")

        base_url = "https://nvd.nist.gov/feeds/json/cve/1.1/nvdcve-1.1-{year}.json.gz"
        current_year = datetime.now().year
        results = {}

        for year in range(current_year - years, current_year + 1):
            try:
                url = base_url.format(year=year)
                logger.info(f"  Downloading CVE data for {year}...")

                response = self.session.get(url, timeout=300, stream=True)
                response.raise_for_status()

                # Download compressed file
                gz_file = self.data_dir / "nist_nvd" / f"nvdcve-{year}.json.gz"
                with open(gz_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Decompress
                json_file = self.data_dir / "nist_nvd" / f"nvdcve-{year}.json"
                with gzip.open(gz_file, 'rb') as f_in:
                    with open(json_file, 'wb') as f_out:
                        f_out.write(f_in.read())

                # Extract CVEs
                with open(json_file, 'r') as f:
                    cve_data = json.load(f)

                cve_count = len(cve_data.get('CVE_Items', []))
                results[year] = {
                    'status': 'success',
                    'cve_count': cve_count,
                    'file': str(json_file),
                    'size_mb': json_file.stat().st_size / (1024 * 1024)
                }

                # Remove compressed file to save space
                gz_file.unlink()

                logger.info(f"    ✓ {year}: {cve_count} CVEs, {results[year]['size_mb']:.2f} MB")

                # Rate limiting
                time.sleep(6)  # NIST API limit: 10 requests per 60 seconds

            except Exception as e:
                logger.error(f"    ✗ Failed to download {year}: {e}")
                results[year] = {'status': 'error', 'error': str(e)}

        return results

    def download_cisa_advisories(self) -> Dict:
        """Download CISA Known Exploited Vulnerabilities (KEV)"""
        logger.info("Downloading CISA KEV catalog...")

        url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"

        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            output_file = self.data_dir / "cisa_advisories" / "known_exploited_vulnerabilities.json"
            with open(output_file, 'w') as f:
                json.dump(response.json(), f, indent=2)

            kev_data = response.json()
            vuln_count = len(kev_data.get('vulnerabilities', []))

            logger.info(f"  ✓ Downloaded {vuln_count} actively exploited vulnerabilities")

            return {
                'status': 'success',
                'vulnerability_count': vuln_count,
                'file': str(output_file)
            }

        except Exception as e:
            logger.error(f"  ✗ Failed to download CISA KEV: {e}")
            return {'status': 'error', 'error': str(e)}

    def download_malware_feeds(self) -> Dict:
        """Download malware indicators and threat intelligence"""
        logger.info("Downloading malware threat feeds...")

        feeds = {
            'abuse_ch_urlhaus': 'https://urlhaus.abuse.ch/downloads/csv_recent/',
            'abuse_ch_threatfox': 'https://threatfox.abuse.ch/export/json/recent/',
            'malware_bazaar_recent': 'https://bazaar.abuse.ch/export/json/recent/'
        }

        results = {}

        for name, url in feeds.items():
            try:
                logger.info(f"  Downloading {name}...")
                response = self.session.get(url, timeout=60)
                response.raise_for_status()

                if 'csv' in name:
                    output_file = self.data_dir / "malware_feeds" / f"{name}.csv"
                    with open(output_file, 'wb') as f:
                        f.write(response.content)
                else:
                    output_file = self.data_dir / "malware_feeds" / f"{name}.json"
                    with open(output_file, 'w') as f:
                        json.dump(response.json(), f, indent=2)

                results[name] = {
                    'status': 'success',
                    'file': str(output_file),
                    'size_kb': output_file.stat().st_size / 1024
                }

                logger.info(f"    ✓ {name}: {results[name]['size_kb']:.2f} KB")

                time.sleep(2)  # Rate limiting

            except Exception as e:
                logger.error(f"    ✗ Failed to download {name}: {e}")
                results[name] = {'status': 'error', 'error': str(e)}

        return results

    def download_sample_logs(self) -> Dict:
        """Download sample security log datasets from public repositories"""
        logger.info("Downloading sample security log datasets...")

        # Public security log datasets
        datasets = {
            'secrepo_web_logs': 'http://www.secrepo.com/maccdc2012/conn.log.gz',
            'secrepo_dns_logs': 'http://www.secrepo.com/maccdc2012/dns.log.gz',
        }

        results = {}

        for name, url in datasets.items():
            try:
                logger.info(f"  Downloading {name}...")
                response = self.session.get(url, timeout=300, stream=True)

                if response.status_code == 404:
                    logger.warning(f"    ⚠ {name} not available (404)")
                    results[name] = {'status': 'not_available'}
                    continue

                response.raise_for_status()

                # Download compressed
                gz_file = self.data_dir / "log_samples" / f"{name}.gz"
                with open(gz_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                # Decompress
                log_file = self.data_dir / "log_samples" / f"{name}.log"
                with gzip.open(gz_file, 'rb') as f_in:
                    with open(log_file, 'wb') as f_out:
                        f_out.write(f_in.read())

                gz_file.unlink()  # Remove compressed file

                # Count lines
                with open(log_file, 'r') as f:
                    line_count = sum(1 for _ in f)

                results[name] = {
                    'status': 'success',
                    'file': str(log_file),
                    'lines': line_count,
                    'size_mb': log_file.stat().st_size / (1024 * 1024)
                }

                logger.info(f"    ✓ {name}: {line_count} lines, {results[name]['size_mb']:.2f} MB")

            except Exception as e:
                logger.error(f"    ✗ Failed to download {name}: {e}")
                results[name] = {'status': 'error', 'error': str(e)}

        return results

    def download_all(self, parallel: bool = False) -> Dict:
        """Download all datasets"""
        logger.info("\n" + "="*80)
        logger.info("STARTING COMPREHENSIVE DATASET DOWNLOAD")
        logger.info("="*80 + "\n")

        start_time = time.time()
        all_results = {}

        if parallel:
            # Download in parallel using ThreadPoolExecutor
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(self.download_mitre_attack): 'mitre_attack',
                    executor.submit(self.download_cisa_advisories): 'cisa_kev',
                    executor.submit(self.download_malware_feeds): 'malware_feeds',
                    executor.submit(self.download_sample_logs): 'sample_logs'
                }

                for future in as_completed(futures):
                    dataset_name = futures[future]
                    try:
                        all_results[dataset_name] = future.result()
                    except Exception as e:
                        logger.error(f"Error downloading {dataset_name}: {e}")
                        all_results[dataset_name] = {'status': 'error', 'error': str(e)}

            # Download NVD sequentially (rate-limited API)
            all_results['nist_nvd'] = self.download_nist_nvd(years=3)
        else:
            # Sequential download
            all_results['mitre_attack'] = self.download_mitre_attack()
            all_results['nist_nvd'] = self.download_nist_nvd(years=3)
            all_results['cisa_kev'] = self.download_cisa_advisories()
            all_results['malware_feeds'] = self.download_malware_feeds()
            all_results['sample_logs'] = self.download_sample_logs()

        elapsed = time.time() - start_time

        # Save summary
        summary = {
            'download_timestamp': datetime.now().isoformat(),
            'elapsed_seconds': elapsed,
            'datasets': all_results
        }

        summary_file = self.data_dir / "download_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        logger.info("\n" + "="*80)
        logger.info("DOWNLOAD COMPLETE")
        logger.info("="*80)
        logger.info(f"Total time: {elapsed/60:.1f} minutes")
        logger.info(f"Summary saved to: {summary_file}")
        logger.info("="*80 + "\n")

        return summary


def main():
    """Main download orchestrator"""
    downloader = SecurityDatasetDownloader()

    # Download all datasets in parallel
    results = downloader.download_all(parallel=True)

    # Print summary
    print("\n" + "="*80)
    print("DATASET DOWNLOAD SUMMARY")
    print("="*80)

    for dataset, result in results['datasets'].items():
        print(f"\n{dataset.upper()}:")
        if isinstance(result, dict):
            for key, value in result.items():
                if key != 'status':
                    print(f"  {key}: {value}")

    print("\n" + "="*80)


if __name__ == '__main__':
    main()
