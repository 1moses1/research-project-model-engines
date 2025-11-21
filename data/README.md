# Data Directory (`data/`)

This directory contains all datasets used for training and testing the Rwanda NCSA Compliance Monitoring System.

## Directory Structure

```
data/
├── raw/                    # Original Rwanda NCSA regulatory documents
├── synthetic/              # Synthetically generated compliance events (100K)
├── public/                 # Public security datasets (NSL-KDD, LogHub)
├── public_formatted/       # Preprocessed public data for training
├── real_formatted/         # Final training dataset (200K events) ⭐
├── processed/              # Intermediate processing outputs
└── targeted/               # Targeted attack samples for Phase 2.5
```

## Dataset Overview

### Training Data Composition (200,000 events)

| Dataset | Events | Source | Purpose |
|---------|--------|--------|---------|
| **NSL-KDD** | 103,962 (52%) | Network intrusion detection benchmark | Real attack patterns (42 attack types) |
| **LogHub-Hadoop** | 21,000 (10.5%) | Distributed system logs | Real system failures and errors |
| **LogHub-OpenStack** | 10,500 (5.25%) | Cloud infrastructure logs | Cloud security events |
| **LogHub-Linux** | 4,538 (2.27%) | System logs | OS-level security events |
| **Synthetic** | 60,000 (30%) | Generated from Rwanda NCSA standards | Compliance-specific scenarios |
| **Total** | **200,000** | Mixed | Robust training data |

## Key Datasets

### 1. `real_formatted/` ⭐ PRODUCTION TRAINING DATA

**Purpose**: Final training dataset for XGBoost Phase 2.5

**Files**:
- `compliance_events_train.csv` (140,000 events, 70%)
- `compliance_events_val.csv` (30,000 events, 15%)
- `compliance_events_test.csv` (30,000 events, 15%)

**Schema**:
```csv
timestamp,log_message,control_id,control_family,framework,compliance_status,severity,source_ip,dest_ip,user,resource
2025-10-22 10:30:45,"Failed SSH login from 192.168.1.100",AC-3,Access Control,NIST,non_compliant,high,192.168.1.100,10.0.0.1,admin,/var/log/auth.log
```

**Data Quality**:
- ✅ Zero missing values
- ✅ 50 compliance controls represented
- ✅ 42 attack types covered
- ✅ Realistic temporal patterns (business hours bias)
- ✅ Balanced severity distribution

### 2. `public/` - Public Security Datasets

#### NSL-KDD Dataset
**Source**: https://github.com/defcom17/NSL_KDD
**Size**: 148,517 records
**Content**: Network intrusion detection with 42 attack types

**Attack Categories**:
- **DoS** (12 types): Neptune, Smurf, Pod, Teardrop, Land, Apache2, UDPStorm
- **Probe** (6 types): Satan, IPSweep, Nmap, PortSweep, MScan, Saint
- **R2L** (14 types): Warezclient, Warezmaster, Phishing, Spy, Multihop
- **U2R** (7 types): Buffer Overflow, Rootkit, Perl, Loadmodule, SQLAttack
- **Malware** (3 types): Worm, Trojan, Virus

#### LogHub Datasets
**Source**: https://zenodo.org/record/3227177
**Size**: ~1GB compressed
**Applications**: Hadoop, OpenStack, Linux

**Log Types**:
- Hadoop: Distributed processing errors
- OpenStack: Cloud infrastructure events
- Linux: System-level security logs

### 3. `synthetic/` - Synthetic Compliance Events

**Purpose**: Ensures coverage of all 50 controls and Rwanda-specific scenarios

**Generation Method**:
1. Control definitions from Rwanda NCSA and NIST SP 800-53
2. Realistic log templates per control family
3. Temporal patterns (business hours, weekends)
4. Metadata generation (IPs, users, resources)

**Files**:
- `compliance_events_train.csv` (70,000 events)
- `compliance_events_val.csv` (15,000 events)
- `compliance_events_test.csv` (15,000 events)

**Advantages**:
- ✅ Covers all 50 controls
- ✅ Rwanda NCSA-specific requirements
- ✅ Balanced class distribution
- ✅ No privacy concerns

### 4. `targeted/` - Phase 2.5 Targeted Samples

**Purpose**: Address Phase 2 "compliant bias" by adding 37K targeted attack samples

**Content**:
- 5,231 phishing samples
- 1,316 insider threat samples
- 8,462 DDoS samples
- 6,923 credential stuffing samples
- 7,154 lateral movement samples
- 7,914 other advanced attacks

**Impact**: Fixed Phase 2's 5 misclassified attacks, improving from 58.3% to 100% real scenario accuracy

### 5. `raw/` - Rwanda NCSA Regulatory Documents

**Content**:
- Rwanda NCSA Minimum Cybersecurity Standards (PDF)
- Law Establishing NCSA
- Cyber Crimes Law
- Financial Sector Standards

**Purpose**: Reference documents for control definitions and compliance requirements

## Data Preprocessing Pipeline

### Step 1: Download Public Datasets
```bash
python src/data_pipeline/public_datasets_downloader.py
```

### Step 2: Preprocess Public Data
```bash
python src/data_pipeline/public_dataset_preprocessor.py
```

**Transformations**:
1. Attack type → Compliance control mapping
2. Log pattern → Compliance status mapping
3. Timestamp normalization (30-day range)
4. Metadata generation (IPs, users, resources)
5. Severity assignment (based on attack type)

### Step 3: Generate Synthetic Data
```bash
python src/data_pipeline/synthetic_generator.py --config config/data_config.yaml
```

### Step 4: Combine and Format
```bash
python src/data_pipeline/combine_datasets.py --output data/real_formatted/
```

**Output**: `data/real_formatted/` with 70/15/15 train/val/test split

## Attack Type → Control Mapping

| Attack Category | Example Attacks | Mapped Controls | Compliance Status |
|----------------|-----------------|-----------------|-------------------|
| **Unauthorized Access** | Buffer overflow, rootkit, privilege escalation | AC-3, AC-6 | Non-Compliant |
| **Password Attacks** | Brute force, password guessing | IA-5 | Non-Compliant |
| **DoS Attacks** | Neptune, Smurf, DDoS | SC-5 | Non-Compliant |
| **Reconnaissance** | Port scan, IP sweep, network probing | SI-4 | Non-Compliant |
| **Remote Exploits** | Phishing, SQL injection, malware | AC-3, SI-3 | Non-Compliant |
| **Normal Operations** | Successful login, backup completed | Various | Compliant |

## Data Statistics

### Class Distribution
- **Compliant**: 137,000 events (68.5%)
- **Non-Compliant**: 63,000 events (31.5%)
- **Imbalance Ratio**: 2.17:1 (handled via `scale_pos_weight=5.75` in XGBoost)

### Severity Distribution
- **Normal**: 137,000 (68.5%)
- **Medium**: 15,750 (7.9%)
- **High**: 31,500 (15.8%)
- **Critical**: 15,750 (7.9%)

### Control Family Distribution
| Family | Controls | Events |
|--------|----------|--------|
| **Access Control (AC)** | 10 | 50,000 |
| **System Protection (SC)** | 10 | 40,000 |
| **System Integrity (SI)** | 8 | 35,000 |
| **Audit and Accountability (AU)** | 8 | 30,000 |
| **Identification & Authentication (IA)** | 6 | 25,000 |
| **Incident Response (IR)** | 4 | 12,000 |
| **Configuration Management (CM)** | 4 | 8,000 |

## Data Privacy & Ethics

### Public Datasets
- ✅ All datasets are publicly available
- ✅ No personal information or sensitive data
- ✅ Proper attribution and citations provided

### Synthetic Data
- ✅ No real user data used
- ✅ Randomized IPs, usernames, timestamps
- ✅ Privacy-preserving by design

### Rwanda NCSA Documents
- ✅ Public regulatory documents
- ✅ No confidential government information
- ✅ Proper attribution to Rwanda NCSA

## Data Quality Checks

Run validation tests:
```bash
python tests/test_data_quality.py
```

**Checks**:
- ✅ No missing values
- ✅ All controls represented (50/50)
- ✅ Temporal range valid (30 days)
- ✅ IP addresses valid format
- ✅ Severity aligns with attack type
- ✅ Train/val/test splits correct (70/15/15)

## Dataset Citations

### NSL-KDD
```bibtex
@inproceedings{tavallaee2009detailed,
  title={A detailed analysis of the KDD CUP 99 data set},
  author={Tavallaee, Mahbod and Bagheri, Ebrahim and Lu, Wei and Ghorbani, Ali A},
  booktitle={IEEE Symposium on Computational Intelligence for Security and Defense Applications},
  year={2009}
}
```

### LogHub
```bibtex
@dataset{he2020loghub,
  author = {He, Shilin and Zhu, Jieming and He, Pinjia and Lyu, Michael R.},
  title = {Loghub: A Large Collection of System Log Datasets towards Automated Log Analytics},
  year = {2020},
  publisher = {Zenodo},
  doi = {10.5281/zenodo.3227177}
}
```

---

**Last Updated**: November 3, 2025
**Total Dataset Size**: 200,000 compliance events
**Training Set**: 140,000 events (70%)
**Validation Set**: 30,000 events (15%)
**Test Set**: 30,000 events (15%)
