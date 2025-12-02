# ENGINE 7: Authentication & Authorization Engine - Architecture

## Overview

ENGINE 7 provides secure authentication for:
1. **Machine Authentication**: Connecting to target systems for audit log collection
2. **Platform Authentication**: Users accessing the Rwanda NCSA Compliance Auditor

## Security Principles

### 1. Principle of Least Privilege
- Read-only access for audit operations
- Whitelist-only commands (no arbitrary execution)
- Explicit directory permissions
- Time-limited sessions

### 2. User Consent & Transparency
- Prompt user before creating audit user
- Show exact permissions being requested
- Display allowed directories and commands
- Require explicit confirmation

### 3. Credential Security
- Encrypted credential storage
- Session tokens with expiry
- No plaintext passwords
- Secure environment variable handling

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Rwanda NCSA Compliance Auditor                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │     CLI      │    │     UI       │    │   Daemon     │                  │
│  │  Interface   │    │  Interface   │    │   (k8s)      │                  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                  │
│         │                   │                   │                           │
│         └───────────────────┼───────────────────┘                           │
│                             │                                               │
│                    ┌────────▼────────┐                                      │
│                    │   ENGINE 7:     │                                      │
│                    │   Auth Engine   │                                      │
│                    └────────┬────────┘                                      │
│                             │                                               │
│         ┌───────────────────┼───────────────────┐                           │
│         │                   │                   │                           │
│  ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐                     │
│  │ Machine     │    │ Platform    │    │ Session     │                     │
│  │ Auth        │    │ User Auth   │    │ Manager     │                     │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘                     │
│         │                   │                   │                           │
│         ▼                   ▼                   ▼                           │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │              Secure Credential Store                 │                   │
│  │  - Encrypted storage (AES-256)                      │                   │
│  │  - Session tokens (JWT)                             │                   │
│  │  - OS keychain integration                          │                   │
│  └─────────────────────────────────────────────────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘

                                    │
                                    │ Authenticated Connection
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Target System                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    rwanda_ncsa_auditor (Read-Only User)              │   │
│  │                                                                       │   │
│  │  Allowed Directories:              Allowed Commands:                  │   │
│  │  - /var/log/                       - cat, head, tail, less           │   │
│  │  - /var/log/audit/                 - grep, awk (read-only)           │   │
│  │  - /etc/ (read-only)               - journalctl (read)               │   │
│  │  - /home/*/.bash_history           - last, lastlog, who              │   │
│  │  - /var/log/syslog                 - ps, netstat, ss                 │   │
│  │  - /var/log/auth.log               - systemctl status                │   │
│  │                                    - getent, id                       │   │
│  │  PROHIBITED:                       - NO: rm, mv, chmod, chown        │   │
│  │  - /root/                          - NO: sudo, su                    │   │
│  │  - Private keys                    - NO: wget, curl (data exfil)     │   │
│  │  - /etc/shadow                     - NO: shell spawning              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Machine Authentication Module

**Purpose**: Securely connect to target systems for audit

**Supported Methods**:
- SSH Key-based authentication (recommended)
- SSH Password authentication (with warnings)
- Local system access (current user)
- WinRM for Windows systems

**User Creation Flow**:
```
1. User initiates audit connection
2. System prompts: "Create audit user 'rwanda_ncsa_auditor'?"
3. Display exact permissions and directories
4. User confirms (explicit consent)
5. Create user with read-only permissions
6. Store credentials securely
7. Begin audit session
```

### 2. Platform Authentication Module

**Purpose**: Authenticate users to the compliance platform

**Features**:
- Username/password authentication
- API key authentication
- OAuth2/OIDC integration (future)
- Role-based access control (RBAC)

**Roles**:
- `admin`: Full system access
- `auditor`: Run audits, view reports
- `viewer`: View-only access

### 3. Session Manager

**Purpose**: Manage authentication sessions

**Features**:
- JWT token generation
- Session timeout (configurable)
- Token refresh
- Session revocation
- Audit logging

### 4. Credential Store

**Purpose**: Secure storage of credentials

**Storage Options**:
- OS Keychain (macOS Keychain, Windows Credential Manager)
- Encrypted file storage (AES-256)
- Environment variables (for containers)
- HashiCorp Vault integration (production)

## Audit Command Whitelist

### Linux/macOS Commands

```python
AUDIT_COMMANDS_LINUX = {
    # Log Reading
    "cat": {"allowed_paths": ["/var/log/*", "/etc/*"]},
    "head": {"allowed_paths": ["/var/log/*"]},
    "tail": {"allowed_paths": ["/var/log/*"]},
    "less": {"allowed_paths": ["/var/log/*"]},
    "grep": {"allowed_paths": ["/var/log/*", "/etc/*"]},

    # System Info
    "journalctl": {"flags": ["--no-pager", "-r", "-n"]},
    "last": {},
    "lastlog": {},
    "who": {},
    "w": {},
    "uptime": {},

    # Process/Network
    "ps": {"flags": ["aux", "-ef"]},
    "netstat": {"flags": ["-tuln", "-an"]},
    "ss": {"flags": ["-tuln"]},

    # User Info
    "id": {},
    "getent": {"args": ["passwd", "group"]},
    "groups": {},

    # Service Status
    "systemctl": {"subcommands": ["status", "is-active", "list-units"]},
    "service": {"subcommands": ["status"]},

    # File System (read-only)
    "ls": {"flags": ["-la", "-lah"]},
    "stat": {},
    "file": {},
    "df": {},
    "du": {"flags": ["-sh"]},
}

PROHIBITED_COMMANDS = [
    "rm", "mv", "cp", "chmod", "chown", "chgrp",
    "sudo", "su", "passwd", "useradd", "userdel",
    "wget", "curl", "nc", "netcat", "nmap",
    "python", "perl", "ruby", "bash", "sh", "zsh",
    "vi", "vim", "nano", "emacs",
    "kill", "pkill", "killall",
    "reboot", "shutdown", "init",
    "iptables", "firewall-cmd",
]
```

### Windows Commands

```python
AUDIT_COMMANDS_WINDOWS = {
    # Event Logs
    "Get-EventLog": {"parameters": ["-LogName"]},
    "Get-WinEvent": {"parameters": ["-FilterHashtable"]},

    # System Info
    "Get-Process": {},
    "Get-Service": {},
    "Get-NetTCPConnection": {},
    "Get-LocalUser": {},
    "Get-LocalGroup": {},

    # Security
    "Get-Acl": {},
    "auditpol": {"subcommands": ["/get"]},
}
```

## Audit Directories by OS

### Linux

```yaml
audit_directories:
  system_logs:
    - /var/log/syslog
    - /var/log/messages
    - /var/log/dmesg

  auth_logs:
    - /var/log/auth.log
    - /var/log/secure
    - /var/log/faillog

  audit_logs:
    - /var/log/audit/audit.log
    - /var/log/audit/

  application_logs:
    - /var/log/apache2/
    - /var/log/nginx/
    - /var/log/mysql/

  config_files:
    - /etc/passwd (read-only)
    - /etc/group (read-only)
    - /etc/ssh/sshd_config
    - /etc/sudoers (if permitted)
```

### macOS

```yaml
audit_directories:
  system_logs:
    - /var/log/system.log
    - /var/log/install.log

  security_logs:
    - /var/log/secure.log
    - /private/var/log/asl/
```

### Windows

```yaml
audit_directories:
  event_logs:
    - Security
    - System
    - Application

  config:
    - C:\Windows\System32\config\
```

## Security Controls

### 1. Command Validation Pipeline

```
User Request
     │
     ▼
┌────────────┐
│ Parse Cmd  │ ──▶ Tokenize command
└─────┬──────┘
      │
      ▼
┌────────────┐
│ Whitelist  │ ──▶ Is command in whitelist?
│  Check     │     NO → REJECT
└─────┬──────┘
      │ YES
      ▼
┌────────────┐
│ Flag       │ ──▶ Are flags allowed?
│ Validation │     DANGEROUS → REJECT
└─────┬──────┘
      │ SAFE
      ▼
┌────────────┐
│ Path       │ ──▶ Is target path allowed?
│ Validation │     OUTSIDE SCOPE → REJECT
└─────┬──────┘
      │ ALLOWED
      ▼
┌────────────┐
│ Injection  │ ──▶ Shell injection check
│  Check     │     DETECTED → REJECT
└─────┬──────┘
      │ CLEAN
      ▼
┌────────────┐
│ Execute    │ ──▶ Run with timeout
│ (Sandboxed)│     Log execution
└────────────┘
```

### 2. Session Security

```python
SESSION_CONFIG = {
    "token_type": "JWT",
    "algorithm": "HS256",
    "access_token_expire_minutes": 30,
    "refresh_token_expire_days": 7,
    "max_concurrent_sessions": 3,
    "require_mfa": False,  # Future
}
```

### 3. Audit Logging

All actions are logged:
- Authentication attempts (success/failure)
- Commands executed
- Files accessed
- Anomalies detected
- Session events

## API Endpoints

### Machine Authentication

```
POST /auth/machine/connect
POST /auth/machine/create-user
POST /auth/machine/verify-permissions
DELETE /auth/machine/disconnect
GET /auth/machine/status
```

### Platform Authentication

```
POST /auth/login
POST /auth/logout
POST /auth/refresh
GET /auth/me
POST /auth/api-key/generate
DELETE /auth/api-key/revoke
```

### Session Management

```
GET /sessions
DELETE /sessions/{session_id}
GET /sessions/active
```

## Environment Variables

```bash
# Platform Auth
AUTH_SECRET_KEY=your-256-bit-secret-key
AUTH_ALGORITHM=HS256
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Credential Storage
CREDENTIAL_STORE_TYPE=keychain  # keychain, encrypted_file, vault
CREDENTIAL_ENCRYPTION_KEY=your-encryption-key

# Machine Auth Defaults
DEFAULT_AUDIT_USERNAME=rwanda_ncsa_auditor
SSH_KEY_PATH=/app/keys/
SSH_KNOWN_HOSTS=/app/known_hosts

# Security
COMMAND_TIMEOUT_SECONDS=30
MAX_OUTPUT_SIZE_BYTES=10485760  # 10MB
ENABLE_AUDIT_LOGGING=true
```

## Implementation Priority

1. **Phase 1**: Platform authentication (JWT)
2. **Phase 2**: Machine authentication (SSH)
3. **Phase 3**: Command whitelist enforcement
4. **Phase 4**: Audit user creation
5. **Phase 5**: Credential store integration
6. **Phase 6**: Windows support
