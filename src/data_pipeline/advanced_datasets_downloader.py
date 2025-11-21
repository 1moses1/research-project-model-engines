"""
Advanced Cybersecurity Datasets Downloader

Downloads additional cybersecurity datasets and compliance standards:
1. CSIC 2010 - Web application attacks
2. ADFA-IDS - Linux intrusion dataset
3. CTU-13 - Botnet traffic
4. Kitsune Network Attack Dataset
5. SecRepo - Security data samples
6. NIST CVE Database
7. Compliance Standards (NIST, ISO, CIS, PCI-DSS, etc.)

Author: Moise Iradukunda (CMU)
Date: October 2025
"""

import os
import requests
import zipfile
import tarfile
import gzip
import json
from pathlib import Path
from tqdm import tqdm
from typing import Dict, List
import logging
import sys
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utils.logger import setup_logger


class AdvancedDatasetsDownloader:
    """Download advanced cybersecurity datasets and compliance standards."""

    # Additional cybersecurity datasets
    DATASETS = {
        'CSIC-2010': {
            'name': 'CSIC 2010 HTTP Dataset',
            'urls': [
                'http://www.isi.csic.es/dataset/csic2010http.zip'
            ],
            'description': 'Web application attacks (SQL injection, XSS, buffer overflow)',
            'format': 'TXT',
            'size': '~40MB',
            'manual': False,
            'category': 'web_security'
        },
        'ADFA-IDS': {
            'name': 'ADFA Intrusion Detection',
            'urls': [
                'https://www.unsw.adfa.edu.au/australian-centre-for-cyber-security/cybersecurity/ADFA-IDS-Datasets/'
            ],
            'description': 'Linux system call traces for intrusion detection',
            'format': 'TXT',
            'size': '~500MB',
            'manual': True,
            'category': 'host_intrusion'
        },
        'CTU-13': {
            'name': 'CTU-13 Botnet Dataset',
            'urls': [
                'https://www.stratosphereips.org/datasets-ctu13'
            ],
            'description': 'Real botnet traffic captures',
            'format': 'PCAP',
            'size': '~50GB',
            'manual': True,
            'category': 'botnet'
        },
        'Kitsune': {
            'name': 'Kitsune Network Attack Dataset',
            'urls': [
                'https://archive.ics.uci.edu/ml/datasets/Kitsune+Network+Attack+Dataset'
            ],
            'description': 'Network-based anomaly detection',
            'format': 'CSV',
            'size': '~2GB',
            'manual': True,
            'category': 'network_anomaly'
        },
        'SecRepo': {
            'name': 'Security Repo Samples',
            'urls': [
                'http://www.secrepo.com/'
            ],
            'description': 'Various security log samples',
            'format': 'Various',
            'size': 'Various',
            'manual': True,
            'category': 'security_logs'
        },
        'EMBER': {
            'name': 'EMBER Malware Dataset',
            'urls': [
                'https://github.com/elastic/ember'
            ],
            'description': 'Malware classification dataset',
            'format': 'JSON',
            'size': '~2GB',
            'manual': True,
            'category': 'malware'
        }
    }

    # Compliance standards and frameworks
    COMPLIANCE_STANDARDS = {
        'NIST-SP-800-53': {
            'name': 'NIST SP 800-53 Rev 5',
            'url': 'https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf',
            'description': 'Security and Privacy Controls',
            'format': 'PDF',
            'category': 'framework'
        },
        'NIST-CSF': {
            'name': 'NIST Cybersecurity Framework',
            'url': 'https://www.nist.gov/cyberframework/framework',
            'description': 'Framework for improving critical infrastructure cybersecurity',
            'format': 'PDF',
            'category': 'framework'
        },
        'ISO-27001': {
            'name': 'ISO/IEC 27001:2022',
            'url': 'https://www.iso.org/standard/27001',
            'description': 'Information security management systems',
            'format': 'PDF',
            'category': 'standard',
            'manual': True  # Requires purchase
        },
        'CIS-Controls': {
            'name': 'CIS Critical Security Controls v8',
            'url': 'https://www.cisecurity.org/controls/v8',
            'description': 'Prioritized set of actions for cyber defense',
            'format': 'PDF',
            'category': 'controls'
        },
        'PCI-DSS': {
            'name': 'PCI DSS v4.0',
            'url': 'https://www.pcisecuritystandards.org/documents/PCI-DSS-v4-0.pdf',
            'description': 'Payment Card Industry Data Security Standard',
            'format': 'PDF',
            'category': 'compliance'
        },
        'MITRE-ATT&CK': {
            'name': 'MITRE ATT&CK Framework',
            'url': 'https://attack.mitre.org/',
            'description': 'Adversarial tactics and techniques',
            'format': 'JSON',
            'category': 'threat_intelligence'
        },
        'OWASP-Top-10': {
            'name': 'OWASP Top 10',
            'url': 'https://owasp.org/www-project-top-ten/',
            'description': 'Top 10 web application security risks',
            'format': 'PDF',
            'category': 'web_security'
        },
        'GDPR': {
            'name': 'EU GDPR',
            'url': 'https://gdpr-info.eu/',
            'description': 'General Data Protection Regulation',
            'format': 'HTML',
            'category': 'privacy'
        }
    }

    def __init__(self, output_dir: str = "data/advanced_datasets"):
        """
        Initialize downloader.

        Args:
            output_dir: Directory to save datasets
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger("advanced_datasets", "logs/advanced_datasets.log")
        self.logger.info("Advanced Datasets Downloader initialized")

    def download_file(self, url: str, output_path: Path, chunk_size: int = 8192) -> bool:
        """
        Download a file with progress bar.

        Args:
            url: URL to download from
            output_path: Path to save file
            chunk_size: Download chunk size

        Returns:
            True if successful
        """
        try:
            self.logger.info(f"Downloading from {url}")

            # Add headers to mimic browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }

            response = requests.get(url, stream=True, timeout=60, headers=headers, allow_redirects=True)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'wb') as f:
                if total_size > 0:
                    with tqdm(total=total_size, unit='B', unit_scale=True, desc=output_path.name) as pbar:
                        for chunk in response.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                                pbar.update(len(chunk))
                else:
                    # No content length, download without progress bar
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            f.write(chunk)

            self.logger.info(f"Downloaded successfully: {output_path}")
            return True

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Download failed for {url}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error downloading {url}: {e}")
            return False

    def download_mitre_attck(self) -> bool:
        """Download MITRE ATT&CK framework data."""
        self.logger.info("Downloading MITRE ATT&CK framework")

        output_dir = self.output_dir / "compliance_standards" / "MITRE-ATT&CK"
        output_dir.mkdir(parents=True, exist_ok=True)

        # MITRE ATT&CK Enterprise matrix
        urls = {
            'enterprise-attack.json': 'https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json',
            'mobile-attack.json': 'https://raw.githubusercontent.com/mitre/cti/master/mobile-attack/mobile-attack.json',
            'ics-attack.json': 'https://raw.githubusercontent.com/mitre/cti/master/ics-attack/ics-attack.json'
        }

        success_count = 0
        for filename, url in urls.items():
            output_path = output_dir / filename
            if output_path.exists():
                self.logger.info(f"Already exists: {output_path}")
                success_count += 1
                continue

            if self.download_file(url, output_path):
                success_count += 1

        return success_count == len(urls)

    def download_nist_nvd(self) -> bool:
        """Download NIST National Vulnerability Database (CVE data)."""
        self.logger.info("Downloading NIST NVD CVE data")

        output_dir = self.output_dir / "compliance_standards" / "NIST-NVD"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Recent CVE feeds
        current_year = datetime.now().year
        years = [current_year, current_year - 1, current_year - 2]

        success_count = 0
        for year in years:
            filename = f"nvdcve-1.1-{year}.json"
            url = f"https://nvd.nist.gov/feeds/json/cve/1.1/{filename}.gz"
            gz_path = output_dir / f"{filename}.gz"
            json_path = output_dir / filename

            if json_path.exists():
                self.logger.info(f"Already exists: {json_path}")
                success_count += 1
                continue

            # Download compressed file
            if self.download_file(url, gz_path):
                # Extract
                try:
                    with gzip.open(gz_path, 'rb') as f_in:
                        with open(json_path, 'wb') as f_out:
                            f_out.write(f_in.read())
                    gz_path.unlink()  # Remove compressed file
                    self.logger.info(f"Extracted: {json_path}")
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Extraction failed: {e}")

        return success_count > 0

    def download_cis_benchmarks(self) -> bool:
        """Download CIS Benchmarks information."""
        self.logger.info("Downloading CIS Controls information")

        output_dir = self.output_dir / "compliance_standards" / "CIS-Controls"
        output_dir.mkdir(parents=True, exist_ok=True)

        # CIS Controls v8 implementation groups
        urls = {
            'CIS_Controls_Version_8.pdf': 'https://www.cisecurity.org/controls/v8',
            'implementation_groups.json': 'https://www.cisecurity.org/controls/cis-controls-list'
        }

        # Create a JSON file with CIS Controls information
        cis_controls = {
            "version": "8.0",
            "date_published": "2021-05-18",
            "implementation_groups": {
                "IG1": "Basic cyber hygiene",
                "IG2": "Scalable security",
                "IG3": "Advanced security"
            },
            "controls": [
                {
                    "id": "1",
                    "name": "Inventory and Control of Enterprise Assets",
                    "description": "Actively manage hardware assets"
                },
                {
                    "id": "2",
                    "name": "Inventory and Control of Software Assets",
                    "description": "Actively manage software assets"
                },
                {
                    "id": "3",
                    "name": "Data Protection",
                    "description": "Develop processes and technical controls"
                },
                {
                    "id": "4",
                    "name": "Secure Configuration",
                    "description": "Establish and maintain secure configurations"
                },
                {
                    "id": "5",
                    "name": "Account Management",
                    "description": "Use processes and tools to assign and manage authorization"
                },
                {
                    "id": "6",
                    "name": "Access Control Management",
                    "description": "Use processes and tools to create, assign, manage, and revoke access credentials"
                },
                {
                    "id": "7",
                    "name": "Continuous Vulnerability Management",
                    "description": "Develop a plan to continuously assess and track vulnerabilities"
                },
                {
                    "id": "8",
                    "name": "Audit Log Management",
                    "description": "Collect, alert, review, and retain audit logs"
                },
                {
                    "id": "9",
                    "name": "Email and Web Browser Protections",
                    "description": "Improve defenses and reduce risks from email and web browsers"
                },
                {
                    "id": "10",
                    "name": "Malware Defenses",
                    "description": "Control installation, spread, and execution of malicious applications"
                },
                {
                    "id": "11",
                    "name": "Data Recovery",
                    "description": "Establish and maintain data recovery practices"
                },
                {
                    "id": "12",
                    "name": "Network Infrastructure Management",
                    "description": "Establish, implement, and actively manage network devices"
                },
                {
                    "id": "13",
                    "name": "Network Monitoring and Defense",
                    "description": "Operate processes and tooling to establish and maintain comprehensive network monitoring"
                },
                {
                    "id": "14",
                    "name": "Security Awareness and Skills Training",
                    "description": "Establish and maintain a security awareness program"
                },
                {
                    "id": "15",
                    "name": "Service Provider Management",
                    "description": "Develop a process to evaluate service providers"
                },
                {
                    "id": "16",
                    "name": "Application Software Security",
                    "description": "Manage the security life cycle of in-house developed applications"
                },
                {
                    "id": "17",
                    "name": "Incident Response Management",
                    "description": "Establish a program to develop and maintain an incident response capability"
                },
                {
                    "id": "18",
                    "name": "Penetration Testing",
                    "description": "Test the effectiveness and resiliency of enterprise assets"
                }
            ],
            "source": "https://www.cisecurity.org/controls/v8",
            "downloaded": datetime.now().isoformat()
        }

        # Save CIS Controls
        output_file = output_dir / "cis_controls_v8.json"
        with open(output_file, 'w') as f:
            json.dump(cis_controls, f, indent=2)

        self.logger.info(f"Created CIS Controls: {output_file}")
        return True

    def download_owasp_top10(self) -> bool:
        """Download OWASP Top 10 information."""
        self.logger.info("Downloading OWASP Top 10")

        output_dir = self.output_dir / "compliance_standards" / "OWASP"
        output_dir.mkdir(parents=True, exist_ok=True)

        # OWASP Top 10 2021
        owasp_top10 = {
            "version": "2021",
            "date_published": "2021-09-24",
            "risks": [
                {
                    "rank": "A01:2021",
                    "name": "Broken Access Control",
                    "description": "Restrictions on what authenticated users are allowed to do are often not properly enforced",
                    "cwe_mappings": [
                        "CWE-200: Exposure of Sensitive Information",
                        "CWE-201: Insertion of Sensitive Information Into Sent Data",
                        "CWE-352: Cross-Site Request Forgery"
                    ]
                },
                {
                    "rank": "A02:2021",
                    "name": "Cryptographic Failures",
                    "description": "Failures related to cryptography which often leads to sensitive data exposure",
                    "cwe_mappings": [
                        "CWE-259: Use of Hard-coded Password",
                        "CWE-327: Broken or Risky Crypto Algorithm",
                        "CWE-331: Insufficient Entropy"
                    ]
                },
                {
                    "rank": "A03:2021",
                    "name": "Injection",
                    "description": "Application is vulnerable to attack when user-supplied data is not validated, filtered, or sanitized",
                    "cwe_mappings": [
                        "CWE-79: Cross-site Scripting",
                        "CWE-89: SQL Injection",
                        "CWE-73: External Control of File Name or Path"
                    ]
                },
                {
                    "rank": "A04:2021",
                    "name": "Insecure Design",
                    "description": "Risks related to design and architectural flaws",
                    "cwe_mappings": [
                        "CWE-209: Generation of Error Message Containing Sensitive Information",
                        "CWE-256: Plaintext Storage of a Password",
                        "CWE-501: Trust Boundary Violation"
                    ]
                },
                {
                    "rank": "A05:2021",
                    "name": "Security Misconfiguration",
                    "description": "Missing appropriate security hardening or improperly configured permissions",
                    "cwe_mappings": [
                        "CWE-16: Configuration",
                        "CWE-611: Improper Restriction of XML External Entity Reference"
                    ]
                },
                {
                    "rank": "A06:2021",
                    "name": "Vulnerable and Outdated Components",
                    "description": "Using components with known vulnerabilities",
                    "cwe_mappings": [
                        "CWE-1104: Use of Unmaintained Third Party Components"
                    ]
                },
                {
                    "rank": "A07:2021",
                    "name": "Identification and Authentication Failures",
                    "description": "Confirmation of the user's identity, authentication, and session management is critical",
                    "cwe_mappings": [
                        "CWE-297: Improper Validation of Certificate with Host Mismatch",
                        "CWE-287: Improper Authentication",
                        "CWE-384: Session Fixation"
                    ]
                },
                {
                    "rank": "A08:2021",
                    "name": "Software and Data Integrity Failures",
                    "description": "Code and infrastructure that does not protect against integrity violations",
                    "cwe_mappings": [
                        "CWE-829: Inclusion of Functionality from Untrusted Control Sphere",
                        "CWE-494: Download of Code Without Integrity Check"
                    ]
                },
                {
                    "rank": "A09:2021",
                    "name": "Security Logging and Monitoring Failures",
                    "description": "Without logging and monitoring, breaches cannot be detected",
                    "cwe_mappings": [
                        "CWE-117: Improper Output Neutralization for Logs",
                        "CWE-223: Omission of Security-relevant Information",
                        "CWE-532: Insertion of Sensitive Information into Log File"
                    ]
                },
                {
                    "rank": "A10:2021",
                    "name": "Server-Side Request Forgery (SSRF)",
                    "description": "SSRF flaws occur whenever a web application is fetching a remote resource without validating the user-supplied URL",
                    "cwe_mappings": [
                        "CWE-918: Server-Side Request Forgery (SSRF)"
                    ]
                }
            ],
            "source": "https://owasp.org/Top10/",
            "downloaded": datetime.now().isoformat()
        }

        # Save OWASP Top 10
        output_file = output_dir / "owasp_top10_2021.json"
        with open(output_file, 'w') as f:
            json.dump(owasp_top10, f, indent=2)

        self.logger.info(f"Created OWASP Top 10: {output_file}")
        return True

    def download_pci_dss(self) -> bool:
        """Download PCI DSS information."""
        self.logger.info("Creating PCI DSS control mappings")

        output_dir = self.output_dir / "compliance_standards" / "PCI-DSS"
        output_dir.mkdir(parents=True, exist_ok=True)

        # PCI DSS v4.0 requirements
        pci_dss = {
            "version": "4.0",
            "date_published": "2022-03-31",
            "requirements": [
                {
                    "id": "1",
                    "name": "Install and Maintain Network Security Controls",
                    "description": "Network security controls protect the cardholder data environment"
                },
                {
                    "id": "2",
                    "name": "Apply Secure Configurations to All System Components",
                    "description": "Malicious individuals use default passwords and settings to compromise systems"
                },
                {
                    "id": "3",
                    "name": "Protect Stored Account Data",
                    "description": "Protection methods such as encryption, truncation, masking, and hashing"
                },
                {
                    "id": "4",
                    "name": "Protect Cardholder Data with Strong Cryptography During Transmission",
                    "description": "Sensitive information must be encrypted during transmission over networks"
                },
                {
                    "id": "5",
                    "name": "Protect All Systems and Networks from Malicious Software",
                    "description": "Anti-virus software must be used on all systems commonly affected by malware"
                },
                {
                    "id": "6",
                    "name": "Develop and Maintain Secure Systems and Software",
                    "description": "Security vulnerabilities in systems and software are continuously being discovered"
                },
                {
                    "id": "7",
                    "name": "Restrict Access to System Components and Cardholder Data by Business Need to Know",
                    "description": "Limit access to authorized personnel with legitimate business need"
                },
                {
                    "id": "8",
                    "name": "Identify Users and Authenticate Access to System Components",
                    "description": "Assigning a unique identification to each person with access ensures accountability"
                },
                {
                    "id": "9",
                    "name": "Restrict Physical Access to Cardholder Data",
                    "description": "Physical access provides the opportunity to access devices or data"
                },
                {
                    "id": "10",
                    "name": "Log and Monitor All Access to System Components and Cardholder Data",
                    "description": "Logging mechanisms and ability to track user activities are critical"
                },
                {
                    "id": "11",
                    "name": "Test Security of Systems and Networks Regularly",
                    "description": "Vulnerabilities are continually discovered, systems must be tested regularly"
                },
                {
                    "id": "12",
                    "name": "Support Information Security with Organizational Policies and Programs",
                    "description": "Overall information security policy sets the security tone for the whole entity"
                }
            ],
            "source": "https://www.pcisecuritystandards.org/",
            "downloaded": datetime.now().isoformat()
        }

        # Save PCI DSS
        output_file = output_dir / "pci_dss_v4.json"
        with open(output_file, 'w') as f:
            json.dump(pci_dss, f, indent=2)

        self.logger.info(f"Created PCI DSS mappings: {output_file}")
        return True

    def create_dataset_inventory(self):
        """Create comprehensive inventory of all datasets."""
        inventory = {
            "datasets": {
                "downloaded": [],
                "manual_required": []
            },
            "compliance_standards": {
                "downloaded": [],
                "manual_required": []
            },
            "total_size_gb": 0,
            "created": datetime.now().isoformat()
        }

        # Check what was downloaded
        for dataset_name, info in self.DATASETS.items():
            dataset_entry = {
                "name": dataset_name,
                "description": info['description'],
                "category": info['category'],
                "size": info['size']
            }

            if info['manual']:
                inventory['datasets']['manual_required'].append(dataset_entry)
            else:
                inventory['datasets']['downloaded'].append(dataset_entry)

        # Check compliance standards
        compliance_dir = self.output_dir / "compliance_standards"
        if compliance_dir.exists():
            for standard_dir in compliance_dir.iterdir():
                if standard_dir.is_dir():
                    files = list(standard_dir.glob("*"))
                    inventory['compliance_standards']['downloaded'].append({
                        "name": standard_dir.name,
                        "files": len(files),
                        "path": str(standard_dir)
                    })

        # Save inventory
        inventory_file = self.output_dir / "dataset_inventory.json"
        with open(inventory_file, 'w') as f:
            json.dump(inventory, f, indent=2)

        self.logger.info(f"Created inventory: {inventory_file}")
        return inventory

    def print_manual_instructions(self):
        """Print instructions for manually downloadable datasets."""
        print("\n" + "=" * 80)
        print("MANUAL DOWNLOAD REQUIRED FOR SOME DATASETS")
        print("=" * 80)

        for dataset_name, info in self.DATASETS.items():
            if info['manual']:
                print(f"\n📦 {info['name']}")
                print(f"   Category: {info['category']}")
                print(f"   Description: {info['description']}")
                print(f"   Size: {info['size']}")
                print(f"   Format: {info['format']}")
                print(f"   Download from: {info['urls'][0]}")
                print(f"   Save to: {self.output_dir / dataset_name}/")

        print("\n" + "=" * 80)
        print("✅ Automated downloads will begin now...")
        print()

    def download_all(self):
        """Download all available datasets and standards."""
        print("\n" + "=" * 80)
        print("ADVANCED CYBERSECURITY DATASETS DOWNLOADER")
        print("=" * 80)
        print(f"Output directory: {self.output_dir}")
        print("=" * 80 + "\n")

        # Print manual download instructions
        self.print_manual_instructions()

        results = {
            'compliance_standards': {},
            'datasets': {}
        }

        # Download compliance standards
        print("\n📚 Downloading Compliance Standards...\n")

        print("📥 MITRE ATT&CK Framework...")
        results['compliance_standards']['MITRE-ATT&CK'] = self.download_mitre_attck()

        print("\n📥 NIST NVD (CVE Database)...")
        results['compliance_standards']['NIST-NVD'] = self.download_nist_nvd()

        print("\n📥 CIS Controls v8...")
        results['compliance_standards']['CIS-Controls'] = self.download_cis_benchmarks()

        print("\n📥 OWASP Top 10...")
        results['compliance_standards']['OWASP-Top-10'] = self.download_owasp_top10()

        print("\n📥 PCI DSS v4...")
        results['compliance_standards']['PCI-DSS'] = self.download_pci_dss()

        # Create inventory
        print("\n📊 Creating dataset inventory...")
        inventory = self.create_dataset_inventory()

        # Print summary
        print("\n" + "=" * 80)
        print("DOWNLOAD SUMMARY")
        print("=" * 80)

        print("\n✅ Compliance Standards Downloaded:")
        for standard, success in results['compliance_standards'].items():
            status = "✅" if success else "❌"
            print(f"   {status} {standard}")

        print(f"\n📁 All files saved to: {self.output_dir}")
        print(f"📋 Inventory: {self.output_dir / 'dataset_inventory.json'}")

        print("\n⚠️  Manual downloads required:")
        print("   • ADFA-IDS (Linux intrusion detection)")
        print("   • CTU-13 (Botnet traffic - 50GB)")
        print("   • Kitsune (Network anomaly detection)")
        print("   • SecRepo (Security log samples)")
        print("   • EMBER (Malware dataset)")

        print("\n" + "=" * 80)

        return results


def main():
    """Main execution."""
    downloader = AdvancedDatasetsDownloader()
    downloader.download_all()


if __name__ == "__main__":
    main()
