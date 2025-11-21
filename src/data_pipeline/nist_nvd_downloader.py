#!/usr/bin/env python3
"""
NIST NVD API 2.0 Downloader
Downloads CVE data from NIST National Vulnerability Database using the new API 2.0
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('nist_nvd_api')


class NISTNVDDownloader:
    """Download CVE data from NIST NVD API 2.0"""

    BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

    def __init__(self, output_dir: str = "data/advanced_datasets/compliance_standards/NIST-NVD"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Security Research Project)',
            'Accept': 'application/json'
        })

    def get_recent_cves(self, days: int = 120, results_per_page: int = 2000) -> List[Dict]:
        """
        Download recent CVEs from the last N days

        Args:
            days: Number of days to look back
            results_per_page: Results per API call (max 2000)

        Returns:
            List of CVE records
        """
        all_cves = []

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Format dates for API (ISO 8601)
        start_date_str = start_date.strftime('%Y-%m-%dT00:00:00.000')
        end_date_str = end_date.strftime('%Y-%m-%dT23:59:59.999')

        logger.info(f"Fetching CVEs from {start_date_str} to {end_date_str}")

        start_index = 0
        total_results = None

        while True:
            params = {
                'pubStartDate': start_date_str,
                'pubEndDate': end_date_str,
                'resultsPerPage': results_per_page,
                'startIndex': start_index
            }

            try:
                logger.info(f"Fetching CVEs starting at index {start_index}...")
                response = self.session.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                # Get total results on first call
                if total_results is None:
                    total_results = data.get('totalResults', 0)
                    logger.info(f"Total CVEs to download: {total_results}")

                # Extract CVEs from response
                vulnerabilities = data.get('vulnerabilities', [])

                if not vulnerabilities:
                    break

                all_cves.extend(vulnerabilities)
                logger.info(f"Downloaded {len(all_cves)}/{total_results} CVEs")

                # Check if we're done
                if len(all_cves) >= total_results:
                    break

                start_index += results_per_page

                # Rate limiting: NIST allows 5 requests per 30 seconds without API key
                time.sleep(6)

            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching CVEs: {e}")
                break

        return all_cves

    def get_high_severity_cves(self, limit: int = 1000) -> List[Dict]:
        """
        Download high and critical severity CVEs

        Args:
            limit: Maximum number of CVEs to download

        Returns:
            List of CVE records
        """
        all_cves = []

        # CVSS v3 severity thresholds: CRITICAL >= 9.0, HIGH >= 7.0
        for severity_min in [9.0, 7.0]:
            logger.info(f"Fetching CVEs with CVSS >= {severity_min}")

            params = {
                'cvssV3Severity': 'CRITICAL' if severity_min >= 9.0 else 'HIGH',
                'resultsPerPage': min(limit, 2000),
                'startIndex': 0
            }

            try:
                response = self.session.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                vulnerabilities = data.get('vulnerabilities', [])

                all_cves.extend(vulnerabilities)
                logger.info(f"Downloaded {len(vulnerabilities)} {params['cvssV3Severity']} severity CVEs")

                # Rate limiting
                time.sleep(6)

                if len(all_cves) >= limit:
                    break

            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching high severity CVEs: {e}")

        return all_cves[:limit]

    def download_cve_data(self, mode: str = 'recent', days: int = 120, limit: int = 5000) -> bool:
        """
        Download CVE data from NIST NVD

        Args:
            mode: 'recent' for recent CVEs, 'high_severity' for critical/high CVEs
            days: For 'recent' mode, number of days to look back
            limit: Maximum CVEs to download

        Returns:
            True if successful
        """
        try:
            logger.info(f"Starting NIST NVD download (mode: {mode})")

            if mode == 'recent':
                cves = self.get_recent_cves(days=days)
            elif mode == 'high_severity':
                cves = self.get_high_severity_cves(limit=limit)
            else:
                logger.error(f"Unknown mode: {mode}")
                return False

            if not cves:
                logger.warning("No CVEs downloaded")
                return False

            # Save to JSON file
            output_file = self.output_dir / f'nvd_cves_{mode}_{datetime.now().strftime("%Y%m%d")}.json'

            output_data = {
                'metadata': {
                    'download_date': datetime.now().isoformat(),
                    'mode': mode,
                    'total_cves': len(cves),
                    'source': 'NIST NVD API 2.0',
                    'api_url': self.BASE_URL
                },
                'vulnerabilities': cves
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Saved {len(cves)} CVEs to {output_file}")
            logger.info(f"File size: {output_file.stat().st_size / (1024*1024):.2f} MB")

            # Create summary
            self._create_summary(cves, output_file)

            return True

        except Exception as e:
            logger.error(f"Error downloading NIST NVD data: {e}")
            return False

    def _create_summary(self, cves: List[Dict], output_file: Path):
        """Create a summary of downloaded CVEs"""
        summary = {
            'total_cves': len(cves),
            'severity_distribution': {},
            'top_vendors': {},
            'top_cwe': {},
            'recent_cves': []
        }

        # Analyze CVEs
        for vuln in cves:
            cve = vuln.get('cve', {})
            cve_id = cve.get('id', 'Unknown')

            # Get severity
            metrics = cve.get('metrics', {})
            cvss_v3 = metrics.get('cvssMetricV31', [])
            if cvss_v3:
                severity = cvss_v3[0].get('cvssData', {}).get('baseSeverity', 'UNKNOWN')
                summary['severity_distribution'][severity] = summary['severity_distribution'].get(severity, 0) + 1

            # Get CWE
            weaknesses = cve.get('weaknesses', [])
            for weakness in weaknesses:
                for desc in weakness.get('description', []):
                    cwe_id = desc.get('value', '')
                    if cwe_id.startswith('CWE-'):
                        summary['top_cwe'][cwe_id] = summary['top_cwe'].get(cwe_id, 0) + 1

            # Add to recent list (first 10)
            if len(summary['recent_cves']) < 10:
                description = ''
                descriptions = cve.get('descriptions', [])
                if descriptions:
                    description = descriptions[0].get('value', '')[:200]

                summary['recent_cves'].append({
                    'id': cve_id,
                    'description': description,
                    'published': cve.get('published', ''),
                })

        # Sort and limit top items
        summary['top_cwe'] = dict(sorted(summary['top_cwe'].items(), key=lambda x: x[1], reverse=True)[:10])

        # Save summary
        summary_file = output_file.parent / f'{output_file.stem}_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)

        logger.info(f"✅ Created summary: {summary_file}")
        logger.info(f"Severity distribution: {summary['severity_distribution']}")


def main():
    """Main entry point"""
    downloader = NISTNVDDownloader()

    print("\n" + "="*80)
    print("NIST NVD API 2.0 DOWNLOADER")
    print("="*80)
    print()

    # Download recent CVEs (last 120 days)
    print("📥 Downloading recent CVEs (last 120 days)...")
    success1 = downloader.download_cve_data(mode='recent', days=120)

    print()

    # Download high severity CVEs
    print("📥 Downloading high/critical severity CVEs...")
    success2 = downloader.download_cve_data(mode='high_severity', limit=1000)

    print()
    print("="*80)
    if success1 or success2:
        print("✅ NIST NVD download completed successfully")
        print(f"📁 Files saved to: data/advanced_datasets/compliance_standards/NIST-NVD/")
    else:
        print("❌ NIST NVD download failed")
    print("="*80)


if __name__ == '__main__':
    main()
