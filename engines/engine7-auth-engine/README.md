# ENGINE 7: Authentication & Authorization Engine

Secure authentication engine for the Rwanda NCSA Compliance Auditor platform.

## Features

### Platform Authentication (JWT)
- User registration and login
- Role-based access control (admin, auditor, viewer)
- Session management
- Token refresh

### Machine Authentication
- SSH key authentication
- SSH password authentication
- Local system authentication
- WinRM for Windows (planned)

### Secure Audit User Creation
- Read-only permissions only
- Restricted shell (rbash)
- Command whitelist enforcement
- Directory access control
- User consent confirmation

## Security Principles

1. **Least Privilege**: Audit users have minimal required permissions
2. **User Consent**: Explicit confirmation required before creating audit users
3. **Command Whitelist**: Only approved commands can be executed
4. **Audit Logging**: All actions are logged
5. **Session Timeouts**: Automatic session expiration

## Allowed Commands (Audit User)

### Log Reading
- `cat`, `head`, `tail`, `less`, `grep`, `awk`

### System Information
- `journalctl`, `last`, `lastlog`, `who`, `w`, `uptime`

### Process/Network
- `ps`, `netstat`, `ss`, `lsof`

### User Information
- `id`, `getent`, `groups`

### Service Status
- `systemctl status`, `service --status-all`

### Filesystem (Read-only)
- `ls`, `stat`, `file`, `df`, `du`

## Prohibited Commands

- File modification: `rm`, `mv`, `cp`, `chmod`, `chown`
- Privilege escalation: `sudo`, `su`, `passwd`
- Network tools: `wget`, `curl`, `nc`, `netcat`
- Scripting: `python`, `perl`, `ruby`, `bash`, `sh`
- System control: `kill`, `reboot`, `shutdown`
- Firewall: `iptables`, `firewall-cmd`

## API Endpoints

### Platform Auth
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login
- `POST /auth/logout` - Logout
- `GET /auth/me` - Current user info

### Machine Auth
- `POST /auth/machine/connect` - Connect to target machine
- `GET /auth/machine/permissions` - View audit permissions
- `POST /auth/machine/create-audit-user` - Preview audit user creation
- `POST /auth/machine/create-audit-user/confirm` - Confirm and create
- `DELETE /auth/machine/disconnect/{session_id}` - Disconnect
- `GET /auth/machine/sessions` - List active sessions

## Quick Start

### Docker

```bash
# Build
docker build -t rwanda-ncsa/auth-engine .

# Run
docker run -p 8007:8007 \
  -e AUTH_SECRET_KEY=your-secret-key \
  rwanda-ncsa/auth-engine
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run
python -m uvicorn app.main:app --host 0.0.0.0 --port 8007 --reload
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| AUTH_SECRET_KEY | JWT signing key | Random |
| AUTH_ALGORITHM | JWT algorithm | HS256 |
| AUTH_ACCESS_TOKEN_EXPIRE_MINUTES | Token expiry | 30 |
| AUTH_PORT | Service port | 8007 |
| AUDIT_USERNAME | Default audit user | rwanda_ncsa_auditor |

## Usage Example

### 1. Login to Platform

```bash
curl -X POST http://localhost:8007/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### 2. Connect to Target Machine

```bash
curl -X POST http://localhost:8007/auth/machine/connect \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "localhost",
    "port": 22,
    "username": "auditor",
    "auth_method": "local",
    "os_type": "linux"
  }'
```

### 3. Create Audit User (with confirmation)

```bash
# Preview
curl -X POST http://localhost:8007/auth/machine/create-audit-user \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "target-server",
    "admin_username": "root",
    "audit_username": "rwanda_ncsa_auditor"
  }'

# Confirm
curl -X POST "http://localhost:8007/auth/machine/create-audit-user/confirm?confirmation=I_CONFIRM_AUDIT_USER_CREATION" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

## Integration with Other Engines

ENGINE 7 provides authentication for:
- **ENGINE 1** (Log Collector): Machine authentication for remote log collection
- **ENGINE 2** (Document Processor): Platform authentication
- **ENGINE 3** (XGBoost Classifier): Platform authentication
- **ENGINE 4** (Decision Engine): Platform authentication
- **ENGINE 5** (Web UI): Platform authentication (SSO)
- **ENGINE 6** (Report Generator): Platform authentication

## License

Rwanda NCSA Compliance Auditor - Internal Use
