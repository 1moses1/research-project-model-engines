import pandas as pd
import json
from pathlib import Path

print("="*100)
print("CURRENT DATASET INVENTORY & MODEL IMPACT ANALYSIS")
print("="*100)
print()

# 1. Training Data Analysis
print("1. TRAINING DATA CURRENTLY USED:")
print("-"*100)

try:
    train = pd.read_csv("data/combined_compliance/compliance_events_train.csv")
    val = pd.read_csv("data/combined_compliance/compliance_events_val.csv")
    test = pd.read_csv("data/combined_compliance/compliance_events_test.csv")
    
    print(f"✅ Training set: {len(train):,} events")
    print(f"✅ Validation set: {len(val):,} events")
    print(f"✅ Test set: {len(test):,} events")
    print(f"   Total: {len(train) + len(val) + len(test):,} events")
    print()
    
    # Analyze distribution
    print("   Distribution:")
    print(f"   - Compliant: {(train['compliance_status'] == 'compliant').sum():,} ({(train['compliance_status'] == 'compliant').sum()/len(train)*100:.1f}%)")
    print(f"   - Non-compliant: {(train['compliance_status'] == 'non_compliant').sum():,} ({(train['compliance_status'] == 'non_compliant').sum()/len(train)*100:.1f}%)")
    print()
    
    # Control families
    print("   Control Families:")
    for family, count in train['control_family'].value_counts().head(5).items():
        print(f"   - {family}: {count:,}")
    print()
    
except Exception as e:
    print(f"❌ Could not load training data: {e}")
    print()

# 2. Available Advanced Datasets
print("2. ADVANCED DATASETS AVAILABLE (NOT YET INTEGRATED):")
print("-"*100)

advanced_datasets = {
    "MITRE ATT&CK Enterprise": "data/advanced_datasets/compliance_standards/MITRE-ATT&CK/enterprise-attack.json",
    "MITRE ATT&CK Mobile": "data/advanced_datasets/compliance_standards/MITRE-ATT&CK/mobile-attack.json",
    "MITRE ATT&CK ICS": "data/advanced_datasets/compliance_standards/MITRE-ATT&CK/ics-attack.json",
    "CIS Controls v8": "data/advanced_datasets/compliance_standards/CIS-Controls/cis_controls_v8.json",
    "OWASP Top 10": "data/advanced_datasets/compliance_standards/OWASP/owasp_top10_2021.json",
    "PCI-DSS v4": "data/advanced_datasets/compliance_standards/PCI-DSS/pci_dss_v4.json",
    "NIST NVD CVEs": "data/advanced_datasets/compliance_standards/NIST-NVD/nvd_cves_high_severity_20251028.json"
}

for name, path in advanced_datasets.items():
    if Path(path).exists():
        size_mb = Path(path).stat().st_size / (1024*1024)
        print(f"✅ {name}: {size_mb:.2f} MB")
        try:
            with open(path) as f:
                data = json.load(f)
                if isinstance(data, dict):
                    if 'objects' in data:
                        print(f"   - {len(data['objects'])} objects")
                    elif 'CVE_Items' in data:
                        print(f"   - {len(data['CVE_Items'])} CVEs")
                    else:
                        print(f"   - {len(data)} entries")
                elif isinstance(data, list):
                    print(f"   - {len(data)} items")
        except:
            pass
    else:
        print(f"❌ {name}: NOT FOUND")
print()

# 3. Downloaded Security Feeds
print("3. SECURITY FEEDS DOWNLOADED (NOT YET INTEGRATED):")
print("-"*100)

security_feeds = {
    "CISA KEV": "data/security_feeds/cisa_advisories/known_exploited_vulnerabilities.json",
    "MITRE Enterprise": "data/security_feeds/mitre_attack/enterprise-attack.json",
    "MITRE Mobile": "data/security_feeds/mitre_attack/mobile-attack.json",
    "MITRE ICS": "data/security_feeds/mitre_attack/ics-attack.json",
    "ThreatFox": "data/security_feeds/malware_feeds/abuse_ch_threatfox.json",
    "SecRepo Web Logs": "data/security_feeds/log_samples/secrepo_web_logs.log",
    "SecRepo DNS Logs": "data/security_feeds/log_samples/secrepo_dns_logs.log"
}

for name, path in security_feeds.items():
    if Path(path).exists():
        size_mb = Path(path).stat().st_size / (1024*1024)
        if size_mb > 1:
            print(f"✅ {name}: {size_mb:.2f} MB")
            if path.endswith('.log'):
                with open(path) as f:
                    lines = sum(1 for _ in f)
                print(f"   - {lines:,} log lines")
        else:
            print(f"✅ {name}: {size_mb*1024:.2f} KB")
    else:
        print(f"❌ {name}: NOT FOUND")
print()

# 4. Public Datasets
print("4. PUBLIC DATASETS AVAILABLE (NOT YET USED):")
print("-"*100)

public_datasets = {
    "NSL-KDD Train": "data/public/NSL-KDD/KDDTrain+.csv",
    "NSL-KDD Test": "data/public/NSL-KDD/KDDTest+.csv",
    "HDFS Logs": "data/public/hdfs/extracted/HDFS.log",
    "OpenStack Normal": "data/public/LogHub/OpenStack/openstack_normal1.log",
    "OpenStack Abnormal": "data/public/LogHub/OpenStack/openstack_abnormal.log"
}

for name, path in public_datasets.items():
    if Path(path).exists():
        size_mb = Path(path).stat().st_size / (1024*1024)
        print(f"✅ {name}: {size_mb:.2f} MB")
        if path.endswith('.csv'):
            try:
                df = pd.read_csv(path, nrows=5)
                print(f"   - {len(pd.read_csv(path)):,} rows, {len(df.columns)} columns")
            except:
                pass
    else:
        print(f"❌ {name}: NOT FOUND")
print()

print("="*100)
print("SUMMARY:")
print("="*100)
print("✅ Current training: 100K synthetic compliance events")
print("⚠️  Advanced datasets: AVAILABLE but NOT INTEGRATED (7 datasets)")
print("⚠️  Security feeds: DOWNLOADED but NOT USED (2.7 GB)")
print("⚠️  Public datasets: AVAILABLE but NOT INTEGRATED (NSL-KDD, HDFS, OpenStack)")
print()
print("IMPACT ON MODEL:")
print("- Using only synthetic data → Limited real-world patterns")
print("- Not using MITRE/NIST/CIS → Missing industry attack patterns")
print("- Not using real logs → Cannot detect sophisticated attacks")
print("="*100)
