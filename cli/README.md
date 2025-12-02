# Rwanda NCSA Compliance Auditor CLI

Beautiful command-line interface for the Rwanda NCSA Compliance Auditor platform.

## Installation

```bash
# Install dependencies
pip install -r cli/requirements.txt

# Install globally (optional)
pip install -e .

# Or run directly
python rwanda_ncsa.py --help
```

## Quick Start

```bash
# Show help
python rwanda_ncsa.py --help

# Check system status
python rwanda_ncsa.py status

# Start interactive mode
python rwanda_ncsa.py interactive

# Start all engines
python rwanda_ncsa.py start --all

# Login to platform
python rwanda_ncsa.py auth login
```

## Commands

### Authentication

```bash
# Login
rwanda-ncsa auth login -u admin -p password

# Show current user
rwanda-ncsa auth whoami

# Logout
rwanda-ncsa auth logout

# Connect to machine for auditing
rwanda-ncsa auth connect -h 192.168.1.100 -u auditor -m ssh_key

# Create audit user (with confirmation)
rwanda-ncsa auth create-audit-user -h target-server -a root
```

### Compliance Audit

```bash
# Start audit
rwanda-ncsa audit start -h localhost -f rwanda-ncsa

# View findings
rwanda-ncsa audit findings -s critical

# List controls
rwanda-ncsa audit controls

# Check audit status
rwanda-ncsa audit status -a AUD001
```

### Log Analysis

```bash
# Classify a single log
rwanda-ncsa logs analyze "User login failed for admin from 192.168.1.50"

# Collect logs from target
rwanda-ncsa logs collect -h localhost -t auth

# Batch analyze log file
rwanda-ncsa logs batch-analyze -f /var/log/auth.log

# List available log sources
rwanda-ncsa logs sources -h target-server
```

### Classification

```bash
# Classify single log message
rwanda-ncsa classify single "SSH login successful for user admin"

# Batch classify from file
rwanda-ncsa classify batch -f logs.txt -o results.json

# Show model info
rwanda-ncsa classify model-info

# Get control information
rwanda-ncsa classify control-info -c RWNCSA-AU-002
```

### Reports

```bash
# Generate report
rwanda-ncsa report generate -a AUD001 -f pdf -t detailed

# List reports
rwanda-ncsa report list

# Email report
rwanda-ncsa report email -f report.pdf -t admin@example.com

# View summary
rwanda-ncsa report summary -a AUD001
```

### Documents

```bash
# Process policy document
rwanda-ncsa docs process /path/to/policy.pdf -e

# Batch process directory
rwanda-ncsa docs batch-process ./policies/ -r

# Analyze gaps
rwanda-ncsa docs analyze-gaps /path/to/policy.pdf

# List templates
rwanda-ncsa docs templates
```

### Configuration

```bash
# Show configuration
rwanda-ncsa config show

# Set value
rwanda-ncsa config set base_url http://localhost

# Initialize interactively
rwanda-ncsa config init

# Show engine config
rwanda-ncsa config engines
```

### Daemon Mode

```bash
# Start all engines as daemon
rwanda-ncsa daemon start --all --detach

# Stop daemon
rwanda-ncsa daemon stop --all

# View daemon status
rwanda-ncsa daemon status

# View logs
rwanda-ncsa daemon logs -f

# Enable auto-start
rwanda-ncsa daemon autostart --enable
```

### Engine Control

```bash
# Start all engines
rwanda-ncsa start --all

# Start specific engine
rwanda-ncsa start -e xgboost_classifier

# Stop all engines
rwanda-ncsa stop --all

# Check status
rwanda-ncsa status
```

## Interactive Mode

For a full interactive experience:

```bash
rwanda-ncsa interactive
```

This provides:
- Tab completion
- Command history
- Real-time feedback
- Rich formatted output

## Configuration File

Configuration is stored in `~/.rwanda-ncsa/config.json`:

```json
{
  "base_url": "http://localhost",
  "token": "...",
  "default_framework": "all",
  "default_output_format": "pdf"
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `RWANDA_NCSA_TOKEN` | Authentication token |
| `RWANDA_NCSA_HOME` | Project root directory |
| `ENGINE1_PORT` - `ENGINE7_PORT` | Engine ports |

## Output Themes

The CLI uses Rich for beautiful terminal output:
- Color-coded status indicators
- Formatted tables
- Progress spinners
- Syntax highlighting

## Examples

### Full Audit Workflow

```bash
# 1. Login
rwanda-ncsa auth login -u admin

# 2. Connect to target
rwanda-ncsa auth connect -h 192.168.1.100 -u auditor -m local

# 3. Create audit user (if needed)
rwanda-ncsa auth create-audit-user -h 192.168.1.100 -a root

# 4. Start audit
rwanda-ncsa audit start -h 192.168.1.100

# 5. View findings
rwanda-ncsa audit findings

# 6. Generate report
rwanda-ncsa report generate -a AUD001 -f pdf
```

### Document Analysis

```bash
# Process policy documents
rwanda-ncsa docs batch-process ./policies/ -r

# Analyze gaps
rwanda-ncsa docs analyze-gaps ./policies/security_policy.pdf

# Generate gap report
rwanda-ncsa report generate --template gap-analysis
```

## Support

For help:
```bash
rwanda-ncsa --help
rwanda-ncsa <command> --help
```
