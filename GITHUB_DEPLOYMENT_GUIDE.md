# GitHub Deployment Guide

This guide explains whether and how the Rwanda NCSA Compliance Model repository can be pushed to GitHub.

## Quick Answer

**Can this repo be pushed to GitHub?** ✅ **YES, with significant modifications**

**Current repo size:** 10 GB (too large for standard GitHub)
**Recommended approach:** Use Git LFS + exclude large files

---

## Repository Size Analysis

### Current Size Breakdown

| Component | Size | GitHub Compatible? | Recommendation |
|-----------|------|-------------------|----------------|
| **venv/** | 3.1 GB | ❌ No | EXCLUDE - Never commit virtual environments |
| **data/public/** | 2.5 GB | ❌ No | EXCLUDE or Git LFS - Public datasets |
| **data/security_feeds/** | 2.6 GB | ❌ No | EXCLUDE or Git LFS - Security feeds |
| **Source code + docs** | ~300 MB | ✅ Yes | INCLUDE |
| **Trained models** | ~500 MB | ⚠️ Maybe | Git LFS recommended |
| **data/real_formatted/** | ~800 MB | ⚠️ Maybe | Git LFS or external hosting |
| **logs/** | ~200 MB | ❌ No | EXCLUDE - Generate locally |

**Total:** 10 GB → **Reduced to ~1 GB** after exclusions (or ~300 MB without large datasets)

---

## Files That MUST NOT Be Pushed (Security Risk)

### 🔴 CRITICAL - NEVER COMMIT

The following files contain sensitive credentials and MUST be excluded:

```
.model_signing_key                     # Cryptographic signing key
config/credentials/*.json              # API keys for all users
certs/server.key                       # TLS private key
certs/server.crt                       # TLS certificate
```

**Why?** These files contain:
- **API keys** (admin, analysts: `BiN9m96bcnvJDUCSLLNclckGJAC_Hip7isd3zmmyexs`, etc.)
- **Cryptographic signing key** (used for model integrity verification)
- **TLS certificates** (used for HTTPS API)

**If accidentally committed**, you MUST:
1. Rotate ALL API keys immediately
2. Generate new signing key
3. Remove from Git history using `git filter-branch` or BFG Repo-Cleaner
4. Force push to overwrite history

---

## Recommended GitHub Deployment Strategy

### Option 1: Lightweight Repo (Recommended for Public)

**Size:** ~300 MB
**Best for:** Open-source sharing, collaboration, code review

**What to include:**
- ✅ Source code (`src/`)
- ✅ Documentation (`*.md`)
- ✅ Configuration templates (without credentials)
- ✅ Test scripts
- ✅ Small sample datasets (10K events)
- ✅ Model metadata (JSON files)

**What to exclude:**
- ❌ `venv/` (3.1 GB)
- ❌ `data/public/` (2.5 GB)
- ❌ `data/security_feeds/` (2.6 GB)
- ❌ `results/models/*.pkl` (500 MB models)
- ❌ `logs/` (200 MB)
- ❌ Credentials and keys

**How users get full data:**
```bash
# Clone repo
git clone https://github.com/your-username/rwanda-ncsa-compliance-model.git

# Download public datasets separately
python scripts/download_datasets.py

# Train models from scratch
python train_xgboost_phase2_5.py
```

---

### Option 2: Git LFS (Recommended for Private Repos)

**Size:** ~1 GB (with LFS pointers)
**Best for:** Private repositories, full reproducibility

**Git Large File Storage (LFS)** stores large files externally while keeping pointers in Git.

#### Setup Git LFS

```bash
# Install Git LFS
brew install git-lfs  # macOS
# or: sudo apt install git-lfs  # Linux

# Initialize LFS in repo
cd model-engine/
git lfs install

# Track large files
git lfs track "results/models/*.pkl"
git lfs track "results/models/*.pt"
git lfs track "data/real_formatted/*.csv"
git lfs track "*.parquet"

# Verify LFS tracking
cat .gitattributes
```

#### What to track with LFS

```bash
# Models (500 MB)
git lfs track "results/models/xgboost_phase2_5/*.pkl"

# Training data (800 MB)
git lfs track "data/real_formatted/*.csv"
git lfs track "data/real_formatted/*.parquet"

# Large model files
git lfs track "*.h5"
git lfs track "*.pt"
```

#### Still exclude from LFS

- ❌ `venv/` (recreate with `pip install -r requirements.txt`)
- ❌ `data/public/` (download from original sources)
- ❌ `data/security_feeds/` (download from threat feeds)
- ❌ Credentials

**GitHub LFS limits (Free tier):**
- Storage: 1 GB
- Bandwidth: 1 GB/month

**GitHub LFS costs (if exceeded):**
- $5/month per 50 GB storage + 50 GB bandwidth

---

### Option 3: External Data Hosting

**Size:** ~300 MB (GitHub) + external storage
**Best for:** Large public datasets, cost optimization

**Host large files externally:**
- **Hugging Face Datasets** (free, unlimited) - ML datasets
- **Zenodo** (free, 50 GB per dataset) - Academic research
- **AWS S3** (paid, ~$0.023/GB/month) - Private data
- **Google Drive** (free, 15 GB) - Small teams

**Example: Download script**

```python
# scripts/download_datasets.py
import requests

DATASETS = {
    'nsl_kdd': 'https://zenodo.org/record/.../nsl_kdd.csv',
    'loghub': 'https://zenodo.org/record/.../loghub.csv',
    'models': 'https://huggingface.co/your-username/rwanda-ncsa/model.pkl'
}

def download_file(url, destination):
    response = requests.get(url, stream=True)
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

# Download all datasets
download_file(DATASETS['nsl_kdd'], 'data/public/nsl_kdd.csv')
download_file(DATASETS['loghub'], 'data/public/loghub.csv')
download_file(DATASETS['models'], 'results/models/xgboost_phase2_5.pkl')
```

**README instructions:**
```markdown
## Dataset Download

Large datasets are hosted externally to keep the repository lightweight.

python scripts/download_datasets.py
```

---

## Step-by-Step GitHub Deployment

### 1. Prepare Repository

```bash
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"

# Ensure .gitignore is updated
cat .gitignore  # Verify sensitive files are excluded

# Initialize git (if not already)
git init

# Add all files (respecting .gitignore)
git add .

# Check what will be committed
git status
```

### 2. Verify Sensitive Files Are Excluded

```bash
# Check for credentials (should return nothing)
git ls-files | grep -E "credentials|\.key|\.pem|\.crt"

# If any sensitive files are staged, remove them
git reset HEAD config/credentials/
git reset HEAD .model_signing_key
git reset HEAD certs/server.key
git reset HEAD certs/server.crt
```

### 3. Create Initial Commit

```bash
# Create first commit
git commit -m "Initial commit: Rwanda NCSA Compliance Model v2.5

Production-ready compliance monitoring system:
- 99.49% accuracy (24,477 test events)
- XGBoost Phase 2.5 model
- 50 compliance controls (NIST SP 800-53 + Rwanda NCSA)
- 200K training events (70% public, 30% synthetic)
- 9 security layers
- REST API with JWT authentication
- Comprehensive documentation

Sensitive credentials excluded for security.
Large datasets excluded - download separately via scripts/download_datasets.py.

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
"
```

### 4. Create GitHub Repository

**Option A: Via GitHub CLI**
```bash
# Install GitHub CLI
brew install gh  # macOS

# Authenticate
gh auth login

# Create private repo
gh repo create rwanda-ncsa-compliance-model --private --source=. --remote=origin

# Or create public repo
gh repo create rwanda-ncsa-compliance-model --public --source=. --remote=origin

# Push
git push -u origin main
```

**Option B: Via GitHub Web UI**
1. Go to https://github.com/new
2. Name: `rwanda-ncsa-compliance-model`
3. Visibility: **Private** (recommended - contains research data)
4. Don't initialize with README (we already have one)
5. Click "Create repository"

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/rwanda-ncsa-compliance-model.git

# Push
git branch -M main
git push -u origin main
```

### 5. Verify Deployment

```bash
# Check remote
git remote -v

# Verify no sensitive files were pushed
git log --name-only | grep -E "credentials|\.key"

# If sensitive files found, IMMEDIATELY rotate keys and clean history
```

---

## Post-Deployment Checklist

### Security Verification

- [ ] No credentials in repository (`git log --all --name-only | grep credentials`)
- [ ] No API keys in files (`grep -r "BiN9m96b" .` should return nothing)
- [ ] No signing keys (`ls -la .model_signing_key` not in repo)
- [ ] No TLS certificates (`git ls-files | grep "\.key\|\.crt"` returns nothing)
- [ ] `.gitignore` properly configured

### Documentation

- [ ] README.md explains how to download datasets
- [ ] INSTALLATION.md includes environment setup
- [ ] GITHUB_DEPLOYMENT_GUIDE.md (this file) in repo
- [ ] LICENSE file added (if open-sourcing)
- [ ] CITATION.cff for academic citation

### Repository Settings

- [ ] Repository visibility set correctly (Private for sensitive data)
- [ ] Branch protection enabled on `main`
- [ ] Require pull request reviews before merging
- [ ] GitHub Actions for CI/CD (optional)
- [ ] Issues and Discussions enabled

---

## GitHub Repository Size Limits

| Item | Limit | Notes |
|------|-------|-------|
| **Repository size** | 5 GB recommended | Soft limit, warnings at 1 GB |
| **File size** | 100 MB | Hard limit per file |
| **Push size** | 2 GB | Per push |
| **Git LFS storage** | 1 GB free | $5/50GB after that |

**Current situation:**
- ❌ 10 GB repo → Exceeds GitHub limits
- ✅ 300 MB (without large data) → Within limits
- ✅ 1 GB (with Git LFS) → Within LFS free tier

---

## Alternative Hosting Options

### For Public Open-Source

| Platform | Max Size | Cost | Best For |
|----------|----------|------|----------|
| **GitHub** | 5 GB | Free | Code + small datasets |
| **GitLab** | 10 GB | Free | Larger repos |
| **Hugging Face** | Unlimited | Free | ML models + datasets |
| **Zenodo** | 50 GB/dataset | Free | Academic research |

### For Private Research

| Platform | Max Size | Cost | Best For |
|----------|----------|------|----------|
| **GitHub Private** | 5 GB | Free | Small teams |
| **GitLab Private** | 10 GB | Free | Larger teams |
| **AWS CodeCommit** | 5 GB | $1/user/mo | Enterprise |
| **Bitbucket** | Unlimited | $3/user/mo | Private orgs |

---

## Recommended Workflow

### For Carnegie Mellon Research

**Recommendation:** GitHub Private + External Datasets

1. **GitHub Private Repo:** Source code + documentation (300 MB)
2. **Hugging Face:** Trained models (500 MB) - https://huggingface.co/YOUR_CMU_USERNAME
3. **Zenodo:** Public datasets (NSL-KDD, LogHub) - 2.5 GB - Academic DOI
4. **CMU Storage:** Security feeds (2.6 GB) - Internal only

**Benefits:**
- ✅ Version control for code
- ✅ No GitHub size limits exceeded
- ✅ Academic citation via Zenodo DOI
- ✅ ML community access via Hugging Face
- ✅ Sensitive data stays on CMU servers

---

## Commands Summary

### Quick Deployment (Lightweight)

```bash
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"

# Verify .gitignore
cat .gitignore

# Initialize and commit
git init
git add .
git commit -m "Initial commit: Rwanda NCSA Compliance Model v2.5"

# Create GitHub repo
gh repo create rwanda-ncsa-compliance-model --private --source=. --remote=origin

# Push
git push -u origin main
```

### Quick Deployment (With Git LFS)

```bash
cd "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine"

# Setup Git LFS
git lfs install
git lfs track "results/models/*.pkl"
git lfs track "data/real_formatted/*.csv"

# Commit
git add .gitattributes
git add .
git commit -m "Initial commit with Git LFS"

# Create repo and push
gh repo create rwanda-ncsa-compliance-model --private --source=. --remote=origin
git push -u origin main
```

---

## Support

**Questions about deployment?**
- GitHub Docs: https://docs.github.com/en/repositories/working-with-files/managing-large-files
- Git LFS Docs: https://git-lfs.github.com/
- CMU IT Support: https://www.cmu.edu/computing/

**Security concerns?**
- Review: MODEL_SECURITY_HARDENING.md
- Contact: CMU Information Security Office

---

**Last Updated:** November 4, 2025
**Repository Version:** 2.5.0
**Deployment Status:** Ready for GitHub (with modifications)
