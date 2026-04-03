#!/usr/bin/env python3
"""
Expanded LLM Zero-Shot Evaluation — Rwanda NCSA Compliance Auditor
Phase A+B: n=50 per log type across 4 structurally distinct log types
  1. SSH Authentication logs       (n=50)
  2. macOS System/Service logs     (n=50)
  3. HTTP/API Access logs          (n=50)
  4. Windows Security Event logs   (n=50)  ← NEW (Phase B)

Also runs local Ollama eval if available (Phase C).
Ground truth: rule-based classifiers, manually cross-validated.
"""

import json
import os
import time
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────
# Load .env
# ─────────────────────────────────────────────────────────────────
env_file = Path(__file__).parent.parent / '.env'
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())

from openai import OpenAI
openai_client = OpenAI(
    api_key=os.environ['OPENAI_API_KEY'],
    organization=os.environ.get('OPENAI_ORG_ID')
)

# ─────────────────────────────────────────────────────────────────
# TYPE 1: SSH Authentication Logs (n=50)
# Ground truth: "Failed"/"Invalid"/"refused"/"disconnect"/"exceeded" → non_compliant
#               "Accepted" → compliant
# ─────────────────────────────────────────────────────────────────
SSH_LOGS = [
    # ── compliant (20) ──────────────────────────────────────────
    ("Mar 20 15:27:01 sshd[1201]: Accepted publickey for moiseiradukunda from 127.0.0.1 port 52000 ssh2", "compliant"),
    ("Mar 20 15:27:05 sshd[1202]: Accepted password for deploy from 10.0.1.5 port 44211 ssh2", "compliant"),
    ("Mar 20 09:56:00 sshd[890]: Accepted publickey for moiseiradukunda from ::1 port 51022 ssh2: RSA SHA256:abcdef", "compliant"),
    ("Accepted password for backup from 192.168.1.10 port 60100 ssh2", "compliant"),
    ("Accepted publickey for ubuntu from 10.0.0.1 port 22 ssh2: ED25519 SHA256:xyz", "compliant"),
    ("Accepted publickey for ci-runner from 10.10.0.5 port 55000 ssh2", "compliant"),
    ("Accepted password for webadmin from 10.0.0.2 port 42100 ssh2", "compliant"),
    ("Accepted publickey for jenkins from 192.168.10.5 port 49200 ssh2: RSA SHA256:q1w2", "compliant"),
    ("Accepted password for analyst from 10.0.0.50 port 51234 ssh2", "compliant"),
    ("Accepted publickey for devops from 10.20.0.100 port 43211 ssh2: ECDSA SHA256:r3t4", "compliant"),
    ("Accepted password for sysadmin from 192.168.1.50 port 52100 ssh2", "compliant"),
    ("Accepted publickey for monitor from 10.0.2.5 port 44300 ssh2: RSA SHA256:u5v6", "compliant"),
    ("Accepted password for postgres from 127.0.0.1 port 53000 ssh2", "compliant"),
    ("Accepted publickey for admin from 10.0.0.10 port 55100 ssh2: ED25519 SHA256:w7x8", "compliant"),
    ("Accepted password for operator from 192.168.2.10 port 51050 ssh2", "compliant"),
    ("Accepted publickey for auditor from 10.5.0.1 port 44500 ssh2: RSA SHA256:y9z0", "compliant"),
    ("Accepted password for readonly from 10.0.1.20 port 50200 ssh2", "compliant"),
    ("Accepted publickey for automation from 172.16.0.5 port 46000 ssh2: ECDSA SHA256:a1b2", "compliant"),
    ("Accepted password for compliance from 10.0.0.80 port 52500 ssh2", "compliant"),
    ("Accepted publickey for reporter from 192.168.1.100 port 43100 ssh2: RSA SHA256:c3d4", "compliant"),
    # ── non_compliant (30) ──────────────────────────────────────
    ("Nov 25 03:14:07 sshd[2193]: Failed password for invalid user admin from 192.168.1.105 port 4444 ssh2", "non_compliant"),
    ("Nov 25 03:14:09 sshd[2194]: Failed password for invalid user root from 192.168.1.105 port 4445 ssh2", "non_compliant"),
    ("Nov 25 03:14:12 sshd[2195]: Failed password for invalid user oracle from 10.0.0.15 port 22344 ssh2", "non_compliant"),
    ("Nov 25 04:01:33 sshd[3310]: Connection closed by 203.0.113.15 port 39211 [preauth]", "non_compliant"),
    ("Nov 25 04:01:45 sshd[3311]: Failed password for root from 203.0.113.15 port 39212 ssh2", "non_compliant"),
    ("Nov 25 04:02:01 sshd[3312]: error: maximum authentication attempts exceeded for invalid user admin from 203.0.113.15 port 39213 ssh2 [preauth]", "non_compliant"),
    ("Nov 25 05:10:22 sshd[4001]: Received disconnect from 45.33.32.156 port 22 [preauth]", "non_compliant"),
    ("Invalid user ftp from 203.0.113.77 port 21", "non_compliant"),
    ("Failed password for nobody from 198.51.100.5 port 1024 ssh2", "non_compliant"),
    ("Connection closed by invalid user vagrant 10.20.0.1 port 2222 [preauth]", "non_compliant"),
    ("Failed password for invalid user oracle from 45.33.32.156 port 9999 ssh2", "non_compliant"),
    ("Did not receive identification string from 45.33.32.156 port 22", "non_compliant"),
    ("Failed password for invalid user pi from 10.0.0.99 port 22 ssh2", "non_compliant"),
    ("Disconnecting invalid user admin 192.168.1.200 port 2222: Too many authentication failures", "non_compliant"),
    ("Failed password for invalid user postgres from 172.16.0.1 port 5432 ssh2", "non_compliant"),
    ("error: maximum authentication attempts exceeded for root from 198.51.100.5 port 22 ssh2 [preauth]", "non_compliant"),
    ("Failed password for invalid user test from 45.33.32.156 port 1234 ssh2", "non_compliant"),
    ("Invalid user ubuntu from 203.0.113.20 port 22", "non_compliant"),
    ("Failed password for invalid user deploy from 10.0.0.200 port 4422 ssh2", "non_compliant"),
    ("Connection closed by authenticating user root 192.168.1.1 port 4321 [preauth]", "non_compliant"),
    ("Failed password for invalid user guest from 172.16.0.50 port 6543 ssh2", "non_compliant"),
    ("Received disconnect from 198.51.100.100 port 22: Bye Bye [preauth]", "non_compliant"),
    ("Failed password for invalid user hadoop from 10.0.10.10 port 8022 ssh2", "non_compliant"),
    ("Invalid user jenkins from 45.33.32.100 port 22", "non_compliant"),
    ("Failed password for root from 198.51.100.25 port 4433 ssh2", "non_compliant"),
    ("error: kex_exchange_identification: Connection closed by remote host 203.0.113.50 port 22", "non_compliant"),
    ("Failed password for invalid user mysql from 172.16.0.100 port 3306 ssh2", "non_compliant"),
    ("Disconnecting authenticating user admin 203.0.113.40 port 22: Too many authentication failures [preauth]", "non_compliant"),
    ("Failed password for invalid user ftpuser from 198.51.100.60 port 21 ssh2", "non_compliant"),
    ("Invalid user admin from 45.33.32.200 port 22 [preauth]", "non_compliant"),
]

# ─────────────────────────────────────────────────────────────────
# TYPE 2: macOS System/Service Logs (n=50)
# Ground truth: security control absent/failed/misconfigured → non_compliant
#               security control active/enforced → compliant
# ─────────────────────────────────────────────────────────────────
MACOS_LOGS = [
    # ── compliant (25) ──────────────────────────────────────────
    ("launchctl: com.microsoft.wdav.tray PID=1841 Status=0 (Microsoft Defender ATP running)", "compliant"),
    ("launchctl: com.jamf.management.agent PID=1854 Status=0 (JAMF MDM agent active)", "compliant"),
    ("spctl --status: assessments enabled (Gatekeeper active, only signed software allowed)", "compliant"),
    ("fdesetup status: FileVault is On (disk encryption active on /dev/disk3s1)", "compliant"),
    ("sw_vers: ProductVersion: 26.3.1 BuildVersion: 25D2128 (OS current, no critical patches pending)", "compliant"),
    ("pfctl -s all: Firewall enabled. Block policy: drop. 47 rules active.", "compliant"),
    ("launchctl: com.apple.auditd PID=1199 Status=0 (audit daemon active, logging to /var/audit)", "compliant"),
    ("ntpq -p: remote=time.apple.com refid=GPS offset=-0.003 (NTP synchronized)", "compliant"),
    ("dscl . -read /Groups/admin GroupMembership: admin root moiseiradukunda (least-privilege enforced)", "compliant"),
    ("csrutil status: System Integrity Protection status: enabled.", "compliant"),
    ("launchctl: com.apple.screensaver PID=1300 Status=0 (screen lock active after 5 min idle)", "compliant"),
    ("security find-certificate -a: 12 trusted CA certificates found (certificate store healthy)", "compliant"),
    ("sshd -T | grep passwordauthentication: passwordauthentication no (key-only SSH enforced)", "compliant"),
    ("launchctl: com.apple.TimeMachine PID=2201 Status=0 (backup agent active, last backup 2h ago)", "compliant"),
    ("softwareupdate -l: No new software available (all patches applied)", "compliant"),
    ("launchctl: com.crowdstrike.falcond PID=1920 Status=0 (CrowdStrike Falcon EDR active)", "compliant"),
    ("log show --last 1h | grep 'com.apple.security': 0 policy violations detected", "compliant"),
    ("diskutil apfs list: APFS Volume encrypted YES (FileVault active on all volumes)", "compliant"),
    ("launchctl: com.apple.ntp PID=891 Status=0 (NTP daemon synchronized)", "compliant"),
    ("pwpolicy -getaccountpolicies: minLength=14 maxFailedLogins=5 (NCSA password policy met)", "compliant"),
    ("launchctl: com.apple.RemoteDesktop PID=None Status=3 (ARD disabled, not running)", "compliant"),
    ("syslog -k Facility authpriv -k Sender sshd: 0 unauthorized access events last 24h", "compliant"),
    ("launchctl: com.apple.mDNSResponder PID=1002 Status=0 (Bonjour active, local only)", "compliant"),
    ("xattr -l /Applications/Firefox.app: com.apple.quarantine cleared after notarization check", "compliant"),
    ("launchctl: com.apple.security.policyengine PID=1100 Status=0 (GKE policy engine active)", "compliant"),
    # ── non_compliant (25) ──────────────────────────────────────
    ("launchctl: com.apple.auditd PID=None Status=-9 (audit daemon crashed, not restarting)", "non_compliant"),
    ("launchctl: com.apple.screensharing PID=1201 Status=0 (screen sharing enabled - unreviewed)", "non_compliant"),
    ("csrutil status: System Integrity Protection status: disabled.", "non_compliant"),
    ("launchctl: com.apple.ftpd PID=5501 Status=0 (FTP daemon running - insecure protocol)", "non_compliant"),
    ("fdesetup status: FileVault is Off (no disk encryption - NCSA SC-28 violation)", "non_compliant"),
    ("spctl --status: assessments disabled (Gatekeeper OFF - unsigned apps allowed)", "non_compliant"),
    ("pfctl -s all: No ALTQ support in kernel. Firewall disabled.", "non_compliant"),
    ("pwpolicy -getaccountpolicies: minLength=6 maxFailedLogins=unlimited (policy below NCSA minimum)", "non_compliant"),
    ("softwareupdate -l: 3 critical security updates available (CVE-2026-1234, CVE-2026-5678, CVE-2026-9012)", "non_compliant"),
    ("launchctl: com.apple.tftpd PID=3301 Status=0 (TFTP daemon running - insecure protocol)", "non_compliant"),
    ("sshd -T | grep passwordauthentication: passwordauthentication yes (password auth enabled)", "non_compliant"),
    ("dscl . -read /Users/testuser: AuthenticationAuthority ;ShadowHash; (local account no MFA)", "non_compliant"),
    ("log show --last 1h | grep 'com.apple.security': 7 policy violations in last hour", "non_compliant"),
    ("launchctl: com.microsoft.wdav.tray PID=None Status=3 (Microsoft Defender not running)", "non_compliant"),
    ("ntpq -p: No association ID (NTP not synchronized - time integrity at risk)", "non_compliant"),
    ("launchctl: com.apple.telnetd PID=7701 Status=0 (Telnet daemon running - plaintext protocol)", "non_compliant"),
    ("csrutil authenticated-root status: disabled (kernel extensions unrestricted)", "non_compliant"),
    ("diskutil apfs list: APFS Volume encrypted NO (unencrypted volume found)", "non_compliant"),
    ("launchctl: com.apple.RemoteDesktop.agent PID=1901 Status=0 (ARD enabled without policy review)", "non_compliant"),
    ("spctl --assess --type exec /Applications/Unknown.app: rejected (unsigned app blocked by Gatekeeper - attempted execution logged)", "non_compliant"),
    ("security authorizationdb read system.privilege.admin: allow (admin rights overly permissive)", "non_compliant"),
    ("launchctl: com.apple.smbd PID=4401 Status=0 (SMB file sharing enabled - review required)", "non_compliant"),
    ("log show --last 24h | grep 'rootless violation': 3 SIP violations detected", "non_compliant"),
    ("launchctl: com.apple.nfsd PID=6601 Status=0 (NFS daemon running - unauthenticated shares risk)", "non_compliant"),
    ("sw_vers: ProductVersion: 13.0 BuildVersion: 22A380 (EOL OS - no security patches available)", "non_compliant"),
]

# ─────────────────────────────────────────────────────────────────
# TYPE 3: HTTP/API Access Logs (n=50)
# Ground truth: unauthorized access, attack patterns, policy violations → non_compliant
#               authorized API usage → compliant
# ─────────────────────────────────────────────────────────────────
API_LOGS = [
    # ── compliant (20) ──────────────────────────────────────────
    ('192.168.1.200 - - [20/Mar/2026:20:51:01 +0000] "GET /api/v1/health HTTP/1.1" 200 45 "-" "curl/7.79.1"', "compliant"),
    ('10.0.0.5 - admin - [20/Mar/2026:20:51:10 +0000] "GET /api/v1/controls HTTP/1.1" 200 4512 "-" "compliance-client/1.0"', "compliant"),
    ('10.0.0.5 - admin - [20/Mar/2026:20:51:20 +0000] "POST /api/v1/audit/start HTTP/1.1" 200 128 "-" "compliance-client/1.0"', "compliant"),
    ('10.0.0.5 - analyst - [20/Mar/2026:20:52:30 +0000] "GET /api/v1/reports/latest HTTP/1.1" 200 19841 "-" "Mozilla/5.0"', "compliant"),
    ('10.0.0.5 - admin - [20/Mar/2026:20:53:15 +0000] "DELETE /api/v1/audit/AUDIT-001 HTTP/1.1" 200 24 "-" "compliance-client/1.0"', "compliant"),
    ('192.168.1.50 - viewer - [20/Mar/2026:09:00:00 +0000] "GET /api/v1/dashboard HTTP/1.1" 200 3200 "-" "Mozilla/5.0"', "compliant"),
    ('10.0.1.10 - api_user - [20/Mar/2026:10:15:00 +0000] "POST /api/v1/evidence HTTP/1.1" 201 512 "-" "audit-agent/2.0"', "compliant"),
    ('192.168.1.30 - analyst - [20/Mar/2026:11:30:00 +0000] "GET /api/v1/controls/AC-7 HTTP/1.1" 200 1024 "-" "compliance-client/1.0"', "compliant"),
    ('10.0.0.20 - admin - [20/Mar/2026:12:00:00 +0000] "PUT /api/v1/settings/notifications HTTP/1.1" 200 64 "-" "admin-portal/1.5"', "compliant"),
    ('192.168.2.10 - reporter - [20/Mar/2026:13:45:00 +0000] "GET /api/v1/export/pdf HTTP/1.1" 200 45000 "-" "Mozilla/5.0"', "compliant"),
    ('10.0.0.5 - admin - [20/Mar/2026:14:00:00 +0000] "POST /api/v1/audit/schedule HTTP/1.1" 202 128 "-" "compliance-client/1.0"', "compliant"),
    ('192.168.1.100 - analyst - [20/Mar/2026:15:00:00 +0000] "GET /api/v1/findings HTTP/1.1" 200 8192 "-" "Mozilla/5.0"', "compliant"),
    ('10.0.2.5 - monitor - [20/Mar/2026:16:00:00 +0000] "GET /api/v1/metrics HTTP/1.1" 200 256 "-" "prometheus/2.40"', "compliant"),
    ('192.168.1.75 - admin - [20/Mar/2026:17:30:00 +0000] "POST /api/v1/users HTTP/1.1" 201 128 "-" "admin-portal/1.5"', "compliant"),
    ('10.0.0.5 - analyst - [20/Mar/2026:18:00:00 +0000] "GET /api/v1/controls?family=AC HTTP/1.1" 200 12288 "-" "compliance-client/1.0"', "compliant"),
    ('192.168.1.200 - - [20/Mar/2026:18:30:00 +0000] "GET /api/v1/version HTTP/1.1" 200 32 "-" "healthcheck/1.0"', "compliant"),
    ('10.0.0.5 - admin - [20/Mar/2026:19:00:00 +0000] "PATCH /api/v1/controls/IA-5/threshold HTTP/1.1" 200 48 "-" "compliance-client/1.0"', "compliant"),
    ('192.168.1.50 - viewer - [20/Mar/2026:19:30:00 +0000] "GET /api/v1/audit/history HTTP/1.1" 200 4096 "-" "Mozilla/5.0"', "compliant"),
    ('10.0.0.5 - admin - [20/Mar/2026:20:00:00 +0000] "POST /api/v1/notify HTTP/1.1" 200 64 "-" "compliance-client/1.0"', "compliant"),
    ('192.168.2.20 - auditor - [20/Mar/2026:20:30:00 +0000] "GET /api/v1/evidence/AC-7 HTTP/1.1" 200 2048 "-" "audit-client/3.0"', "compliant"),
    # ── non_compliant (30) ──────────────────────────────────────
    ('203.0.113.42 - - [20/Mar/2026:20:51:05 +0000] "POST /auth/login HTTP/1.1" 401 89 "-" "python-requests/2.28"', "non_compliant"),
    ('203.0.113.42 - - [20/Mar/2026:20:51:11 +0000] "POST /auth/login HTTP/1.1" 401 89 "-" "python-requests/2.28"', "non_compliant"),
    ('203.0.113.42 - - [20/Mar/2026:20:51:12 +0000] "POST /auth/login HTTP/1.1" 401 89 "-" "python-requests/2.28"', "non_compliant"),
    ('45.33.32.156 - - [20/Mar/2026:20:52:00 +0000] "GET /admin/config HTTP/1.1" 403 52 "-" "sqlmap/1.7"', "non_compliant"),
    ('172.16.0.99 - - [20/Mar/2026:20:53:00 +0000] "GET /../../../etc/passwd HTTP/1.1" 400 0 "-" "curl/7.68"', "non_compliant"),
    ('45.33.32.100 - - [20/Mar/2026:21:00:00 +0000] "GET /api/v1/controls HTTP/1.1" 403 52 "-" "nikto/2.1.6"', "non_compliant"),
    ('198.51.100.5 - - [20/Mar/2026:21:05:00 +0000] "POST /api/v1/users HTTP/1.1" 401 89 "-" "python-requests/2.28"', "non_compliant"),
    ('203.0.113.50 - - [20/Mar/2026:21:10:00 +0000] "GET /api/v1/admin/users HTTP/1.1" 403 0 "-" "curl/7.79"', "non_compliant"),
    ('172.16.0.200 - - [20/Mar/2026:21:15:00 +0000] "GET /etc/shadow HTTP/1.1" 404 0 "-" "curl/7.68"', "non_compliant"),
    ('45.33.32.200 - - [20/Mar/2026:21:20:00 +0000] "POST /auth/login HTTP/1.1" 429 0 "-" "python-requests/2.28"', "non_compliant"),
    ('198.51.100.25 - - [20/Mar/2026:21:25:00 +0000] "GET /api/v1/../../.env HTTP/1.1" 400 0 "-" "Nmap Scripting Engine"', "non_compliant"),
    ('203.0.113.75 - - [20/Mar/2026:21:30:00 +0000] "POST /api/v1/audit/start HTTP/1.1" 401 89 "-" "burpsuite/2022"', "non_compliant"),
    ('45.33.32.150 - - [20/Mar/2026:21:35:00 +0000] "GET /api/v1/users/1 HTTP/1.1" 403 52 "-" "sqlmap/1.7"', "non_compliant"),
    ('172.16.0.150 - - [20/Mar/2026:21:40:00 +0000] "PUT /api/v1/users/admin HTTP/1.1" 403 0 "-" "curl/7.79"', "non_compliant"),
    ('198.51.100.50 - - [20/Mar/2026:21:45:00 +0000] "GET /wp-admin/admin-ajax.php HTTP/1.1" 404 0 "-" "Mozilla/5.0"', "non_compliant"),
    ('45.33.32.50 - - [20/Mar/2026:21:50:00 +0000] "POST /api/v1/auth HTTP/1.1" 500 200 "-" "python-requests/2.28"', "non_compliant"),
    ('203.0.113.90 - - [20/Mar/2026:21:55:00 +0000] "GET /api/v1/controls?page=1 UNION SELECT * FROM users-- HTTP/1.1" 400 0 "-" "sqlmap/1.7"', "non_compliant"),
    ('172.16.0.250 - - [20/Mar/2026:22:00:00 +0000] "GET /actuator/env HTTP/1.1" 404 0 "-" "curl/7.68"', "non_compliant"),
    ('198.51.100.75 - - [20/Mar/2026:22:05:00 +0000] "POST /auth/login HTTP/1.1" 401 89 "-" "hydra/9.3"', "non_compliant"),
    ('45.33.32.75 - - [20/Mar/2026:22:10:00 +0000] "GET /api/v1/reports HTTP/1.1" 403 52 "-" "dirbuster/1.0-RC1"', "non_compliant"),
    ('203.0.113.25 - - [20/Mar/2026:22:15:00 +0000] "GET /.git/config HTTP/1.1" 404 0 "-" "curl/7.79"', "non_compliant"),
    ('172.16.0.100 - - [20/Mar/2026:22:20:00 +0000] "POST /api/v1/evidence HTTP/1.1" 401 89 "-" "python-requests/2.28"', "non_compliant"),
    ('198.51.100.100 - - [20/Mar/2026:22:25:00 +0000] "GET /api/v1/users?id=1 OR 1=1-- HTTP/1.1" 400 0 "-" "sqlmap/1.7"', "non_compliant"),
    ('45.33.32.25 - - [20/Mar/2026:22:30:00 +0000] "POST /api/v1/upload HTTP/1.1" 403 0 "-" "curl/7.68"', "non_compliant"),
    ('203.0.113.60 - - [20/Mar/2026:22:35:00 +0000] "GET /server-status HTTP/1.1" 403 52 "-" "Nmap/7.92"', "non_compliant"),
    ('172.16.0.75 - - [20/Mar/2026:22:40:00 +0000] "DELETE /api/v1/controls HTTP/1.1" 403 0 "-" "curl/7.79"', "non_compliant"),
    ('198.51.100.125 - - [20/Mar/2026:22:45:00 +0000] "GET /api/v1/auth/bypass?debug=true HTTP/1.1" 400 0 "-" "curl/7.68"', "non_compliant"),
    ('45.33.32.125 - - [20/Mar/2026:22:50:00 +0000] "POST /auth/login HTTP/1.1" 401 89 "-" "medusa/2.2"', "non_compliant"),
    ('203.0.113.35 - - [20/Mar/2026:22:55:00 +0000] "GET /api/v1/settings/../../../etc/hosts HTTP/1.1" 400 0 "-" "curl/7.68"', "non_compliant"),
    ('172.16.0.125 - - [20/Mar/2026:23:00:00 +0000] "POST /api/v1/audit/start HTTP/1.1" 403 52 "-" "intruder/1.0"', "non_compliant"),
]

# ─────────────────────────────────────────────────────────────────
# TYPE 4: Windows Security Event Logs (n=50) ← NEW Phase B
# Ground truth based on Windows Event ID semantics:
#   4624 (successful logon)          → compliant
#   4625 (failed logon)              → non_compliant
#   4648 (explicit credentials)      → non_compliant (lateral movement risk)
#   4672 (special privilege logon)   → non_compliant (requires review)
#   4688 (new process — suspicious)  → non_compliant
#   4698/4702 (sched task created)   → non_compliant
#   4720 (user account created)      → non_compliant (needs review)
#   4732 (added to admin group)      → non_compliant
#   4768 (Kerberos TGT request OK)   → compliant
#   4769 (Kerberos service ticket)   → compliant
#   4776 (NTLM auth — policy check)  → non_compliant (NTLM deprecated)
#   7045 (service installed)         → non_compliant
# ─────────────────────────────────────────────────────────────────
WINDOWS_LOGS = [
    # ── compliant (20) ──────────────────────────────────────────
    ("EventID=4624 Account=DOMAIN\\moiseiradukunda LogonType=3 (Network) SourceIP=192.168.1.50 WorkStation=CORP-PC01 Status=Success", "compliant"),
    ("EventID=4624 Account=DOMAIN\\analyst1 LogonType=2 (Interactive) WorkStation=CORP-WS05 Status=Success", "compliant"),
    ("EventID=4768 AccountName=svcbackup SuppliedRealmName=NCSA.LOCAL ClientAddress=192.168.1.10 Status=0x0 (Success)", "compliant"),
    ("EventID=4769 AccountName=admin@NCSA.LOCAL ServiceName=krbtgt TicketOptions=0x40810010 Status=0x0", "compliant"),
    ("EventID=4624 Account=DOMAIN\\sysadmin LogonType=10 (RemoteInteractive) SourceIP=10.0.0.5 Status=Success", "compliant"),
    ("EventID=4768 AccountName=admin@NCSA.LOCAL ClientAddress=10.0.0.5 TicketEncType=0x12 (AES256) Status=0x0", "compliant"),
    ("EventID=4624 Account=DOMAIN\\reporter LogonType=3 SourceIP=192.168.2.10 WorkStation=AUDIT-PC Status=Success", "compliant"),
    ("EventID=4769 AccountName=moiseiradukunda@NCSA.LOCAL ServiceName=cifs/fileserver Status=0x0 (Success)", "compliant"),
    ("EventID=4624 Account=DOMAIN\\operator LogonType=2 WorkStation=OPS-PC01 Status=Success", "compliant"),
    ("EventID=4768 AccountName=compliance@NCSA.LOCAL ClientAddress=10.5.0.1 Status=0x0 (Success)", "compliant"),
    ("EventID=4624 Account=DOMAIN\\auditor LogonType=3 SourceIP=10.5.0.1 WorkStation=AUDIT-STATION Status=Success", "compliant"),
    ("EventID=4769 AccountName=svcmonitor@NCSA.LOCAL ServiceName=http/webserver TicketEncType=0x12 Status=0x0", "compliant"),
    ("EventID=4624 Account=DOMAIN\\helpdesk LogonType=10 SourceIP=192.168.1.100 Status=Success", "compliant"),
    ("EventID=4768 AccountName=devops@NCSA.LOCAL ClientAddress=172.16.0.10 TicketEncType=0x11 (AES128) Status=0x0", "compliant"),
    ("EventID=4624 Account=DOMAIN\\readonly LogonType=3 SourceIP=192.168.3.50 WorkStation=READ-ONLY Status=Success", "compliant"),
    ("EventID=4769 AccountName=analyst1@NCSA.LOCAL ServiceName=mssql/dbserver01 Status=0x0 (Success)", "compliant"),
    ("EventID=4624 Account=DOMAIN\\monitor LogonType=5 (Service) WorkStation=MONITOR-SVC Status=Success", "compliant"),
    ("EventID=4768 AccountName=backup@NCSA.LOCAL ClientAddress=10.1.0.5 TicketEncType=0x12 Status=0x0", "compliant"),
    ("EventID=4624 Account=DOMAIN\\cirunner LogonType=3 SourceIP=172.16.0.20 WorkStation=CI-AGENT Status=Success", "compliant"),
    ("EventID=4624 Account=DOMAIN\\dbadmin LogonType=4 (Batch) WorkStation=DB-SERVER Status=Success", "compliant"),
    # ── non_compliant (30) ──────────────────────────────────────
    ("EventID=4625 Account=Administrator FailureReason=Unknown username or bad password SourceIP=203.0.113.42 LogonType=3 Status=0xC000006D", "non_compliant"),
    ("EventID=4625 Account=DOMAIN\\admin FailureReason=Bad password SourceIP=45.33.32.156 LogonType=3 Status=0xC000006A", "non_compliant"),
    ("EventID=4625 Account=root FailureReason=Unknown username SourceIP=198.51.100.5 LogonType=3 Status=0xC0000064", "non_compliant"),
    ("EventID=4625 Account=DOMAIN\\svctest FailureReason=Bad password SourceIP=172.16.0.99 LogonType=3 Status=0xC000006A SubStatus=0xC0000064", "non_compliant"),
    ("EventID=4648 SubjectAccount=DOMAIN\\user1 TargetAccount=Administrator TargetServer=DC01 Process=mimikatz.exe (explicit credential use — lateral movement indicator)", "non_compliant"),
    ("EventID=4688 NewProcessName=C:\\Windows\\Temp\\svc.exe Creator=DOMAIN\\webuser CommandLine=powershell.exe -enc JAB (base64 encoded PowerShell)", "non_compliant"),
    ("EventID=4688 NewProcessName=C:\\Users\\Public\\update.exe Creator=DOMAIN\\employee1 CommandLine=cmd /c whoami && net user (command injection indicator)", "non_compliant"),
    ("EventID=4698 TaskName=\\Microsoft\\Windows\\UpdateSvc Author=DOMAIN\\anonymous Action=C:\\Temp\\backdoor.exe (scheduled task with suspicious executable)", "non_compliant"),
    ("EventID=4720 TargetUsername=backdooruser PrivilegeList=SeDebugPrivilege Creator=DOMAIN\\compromised (new privileged account created)", "non_compliant"),
    ("EventID=4732 MemberName=DOMAIN\\newuser GroupName=Administrators SourceIP=203.0.113.42 (user added to admin group from external IP)", "non_compliant"),
    ("EventID=4776 PackageName=NTLM SubjectAccount=DOMAIN\\svclegacy Status=0xC0000064 (NTLM authentication — deprecated protocol in use)", "non_compliant"),
    ("EventID=7045 ServiceName=nc.exe ImagePath=C:\\Windows\\System32\\nc.exe -lvp 4444 ServiceType=Kernel Driver (netcat installed as service)", "non_compliant"),
    ("EventID=4625 Account=Administrator FailureReason=Bad password SourceIP=198.51.100.25 LogonType=10 (18 attempts in 2 minutes)", "non_compliant"),
    ("EventID=4648 SubjectAccount=DOMAIN\\svc1 TargetAccount=DOMAIN\\admin TargetServer=FILESERVER Process=wmic.exe (WMI lateral movement)", "non_compliant"),
    ("EventID=4688 NewProcessName=C:\\Windows\\System32\\rundll32.exe Creator=DOMAIN\\user2 CommandLine=rundll32.exe javascript:... (fileless execution)", "non_compliant"),
    ("EventID=4625 Account=sysadmin FailureReason=Bad password SourceIP=45.33.32.200 LogonType=3 Status=0xC000006A (brute force pattern)", "non_compliant"),
    ("EventID=4720 TargetUsername=tempuser123 PrivilegeList=SeLoadDriverPrivilege Creator=SYSTEM (unexpected system-level account creation)", "non_compliant"),
    ("EventID=4698 TaskName=\\Updater Author=NT AUTHORITY\\SYSTEM Action=C:\\Windows\\Temp\\update32.dll,Execute (persistence via scheduled task)", "non_compliant"),
    ("EventID=7045 ServiceName=svchost32 ImagePath=%SystemRoot%\\svchost32.exe -k netsvcs ServiceType=Win32 OwnProcess (typosquatting service)", "non_compliant"),
    ("EventID=4776 PackageName=NTLM SubjectAccount=DOMAIN\\webacc Status=0xC000006A (NTLM fallback after Kerberos failure — policy violation)", "non_compliant"),
    ("EventID=4625 Account=Administrator FailureReason=Bad password SourceIP=172.16.0.200 LogonType=3 Status=0xC000006A (5th failure in 10 min)", "non_compliant"),
    ("EventID=4688 NewProcessName=C:\\Temp\\payload.exe Creator=DOMAIN\\finance CommandLine=payload.exe --inject --pid=lsass.exe (LSASS injection attempt)", "non_compliant"),
    ("EventID=4648 SubjectAccount=DOMAIN\\contractor TargetAccount=DOMAIN\\domainadmin Process=psexec.exe TargetServer=DC01 (privilege escalation attempt)", "non_compliant"),
    ("EventID=4732 MemberName=DOMAIN\\intern GroupName=Administrators Creator=DOMAIN\\compromised (unauthorized privilege escalation)", "non_compliant"),
    ("EventID=4625 Account=sa FailureReason=Unknown username SourceIP=203.0.113.60 LogonType=3 Status=0xC0000064 (SQL SA brute force)", "non_compliant"),
    ("EventID=4698 TaskName=\\Windows\\Telemetry\\payload Author=DOMAIN\\user3 Action=C:\\ProgramData\\backdoor.vbs,WScript (VBS persistence)", "non_compliant"),
    ("EventID=4688 NewProcessName=C:\\Windows\\System32\\cmd.exe Creator=DOMAIN\\webservice CommandLine=cmd /c net user hacker P@ss /add (account creation via web shell)", "non_compliant"),
    ("EventID=7045 ServiceName=wuauserv32 ImagePath=C:\\Users\\Public\\wuauserv32.exe StartType=Auto (masquerading as Windows Update)", "non_compliant"),
    ("EventID=4625 Account=Administrator FailureReason=Bad password SourceIP=198.51.100.75 LogonType=3 Status=0xC000006A (credential stuffing pattern: 200 attempts)", "non_compliant"),
    ("EventID=4776 PackageName=NTLM TargetAccount=DOMAIN\\krbtgt Status=0x0 (NTLM used for krbtgt — Golden Ticket risk)", "non_compliant"),
]

# ─────────────────────────────────────────────────────────────────
# CLASSIFICATION PROMPT
# ─────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a cybersecurity compliance analyst evaluating log entries against Rwanda's
National Cyber Security Authority (NCSA) Minimum Cybersecurity Standards (aligned with NIST SP 800-53).

Your task: classify each log entry as one of:
- compliant: The event indicates normal, authorized, secure operation consistent with NCSA policies
- non_compliant: The event indicates a security violation, policy breach, unauthorized access,
  disabled security control, attack pattern, or anomalous activity
- partial: Mixed signals requiring human investigation

Respond with ONLY a JSON object:
{"status": "compliant|non_compliant|partial", "confidence": 0.0-1.0,
 "ncsa_control": "e.g. AC-7 or IA-2", "reason": "one sentence explanation"}"""

def classify_openai(log_text: str, model: str = "gpt-4o-mini") -> dict:
    try:
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Log entry: {log_text}"}
            ],
            temperature=0,
            max_tokens=150,
            response_format={"type": "json_object"}
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        return {"status": "error", "confidence": 0.0, "reason": str(e)}

def classify_ollama(log_text: str, model: str = "llama3.1:8b") -> dict:
    """Classify via local Ollama instance."""
    try:
        import urllib.request
        payload = json.dumps({
            "model": model,
            "prompt": f"{SYSTEM_PROMPT}\n\nLog entry: {log_text}\n\nRespond with ONLY valid JSON:",
            "stream": False,
            "options": {"temperature": 0, "num_predict": 150}
        }).encode()
        req = urllib.request.Request(
            "http://localhost:11434/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = json.loads(resp.read())["response"].strip()
            # Extract JSON from response
            start = raw.find('{')
            end = raw.rfind('}') + 1
            if start >= 0 and end > start:
                return json.loads(raw[start:end])
            return {"status": "error", "confidence": 0.0, "reason": "no JSON in response"}
    except Exception as e:
        return {"status": "error", "confidence": 0.0, "reason": str(e)}

def check_ollama_available() -> tuple[bool, str]:
    """Check if Ollama is running and which models are available."""
    try:
        import urllib.request
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as resp:
            data = json.loads(resp.read())
            models = [m["name"] for m in data.get("models", [])]
            for preferred in ["llama3.1:8b", "llama3:8b", "mistral:7b", "llama2:7b"]:
                if preferred in models:
                    return True, preferred
            if models:
                return True, models[0]
            return False, "no models pulled"
    except Exception as e:
        return False, str(e)

def evaluate_log_type(name: str, samples: list, classifier_fn, model_label: str) -> dict:
    print(f"\n{'='*65}")
    print(f"  [{model_label}] Evaluating: {name} ({len(samples)} samples)")
    print(f"{'='*65}")

    correct, total, results = 0, 0, []
    for i, (log_text, ground_truth) in enumerate(samples):
        result = classifier_fn(log_text)
        predicted = result.get("status", "error")
        confidence = result.get("confidence", 0.0)
        is_correct = (predicted == ground_truth)
        if is_correct:
            correct += 1
        total += 1
        icon = "✓" if is_correct else "✗"
        print(f"  [{i+1:2d}] {icon} GT={ground_truth:15s} PRED={predicted:15s} conf={confidence:.2f}  {log_text[:55]}...")
        results.append({
            "log": log_text[:120], "ground_truth": ground_truth,
            "predicted": predicted, "confidence": confidence,
            "correct": is_correct, "ncsa_control": result.get("ncsa_control", ""),
            "reason": result.get("reason", "")
        })
        time.sleep(0.15)  # rate limiting

    accuracy = correct / total * 100
    avg_conf = sum(r["confidence"] for r in results) / len(results) * 100
    print(f"\n  ACCURACY: {correct}/{total} = {accuracy:.1f}% | AVG CONF: {avg_conf:.1f}%")
    return {
        "log_type": name, "n_samples": total, "correct": correct,
        "accuracy": round(accuracy, 1), "avg_confidence": round(avg_conf, 1),
        "results": results
    }

def run_evaluation(classifier_fn, model_label: str) -> dict:
    all_results = []
    log_types = [
        ("SSH Authentication Logs", SSH_LOGS),
        ("macOS System/Service Logs", MACOS_LOGS),
        ("HTTP/API Access Logs", API_LOGS),
        ("Windows Security Event Logs", WINDOWS_LOGS),
    ]
    for name, samples in log_types:
        r = evaluate_log_type(name, samples, classifier_fn, model_label)
        all_results.append(r)

    total_correct = sum(r["correct"] for r in all_results)
    total_n = sum(r["n_samples"] for r in all_results)
    overall = total_correct / total_n * 100

    print(f"\n{'='*65}")
    print(f"  [{model_label}] SUMMARY")
    print(f"{'='*65}")
    print(f"  {'Log Type':<35} {'N':>5} {'Correct':>8} {'Accuracy':>10} {'Avg Conf':>10}")
    print(f"  {'-'*35} {'-'*5} {'-'*8} {'-'*10} {'-'*10}")
    for r in all_results:
        print(f"  {r['log_type']:<35} {r['n_samples']:>5} {r['correct']:>8} {r['accuracy']:>9.1f}% {r['avg_confidence']:>9.1f}%")
    print(f"  {'OVERALL':<35} {total_n:>5} {total_correct:>8} {overall:>9.1f}%")

    return {
        "model": model_label, "evaluation_date": datetime.now().isoformat(),
        "framework": "Rwanda NCSA", "evaluation_type": "zero_shot",
        "results_by_type": all_results, "overall_accuracy": round(overall, 1),
        "total_samples": total_n, "total_correct": total_correct
    }

def main():
    print("\n" + "="*70)
    print("  EXPANDED LLM ZERO-SHOT EVALUATION — Rwanda NCSA Compliance Auditor")
    print("  Phase A+B: n=50 per type | 4 log types | 200 total samples")
    print("  Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("="*70)

    results_dir = Path(__file__).parent.parent / "results" / "audit"
    results_dir.mkdir(parents=True, exist_ok=True)

    all_model_results = {}

    # ── Phase A+B: GPT-4o-mini evaluation ─────────────────────
    print("\n[Phase A+B] Running GPT-4o-mini evaluation (200 samples)...")
    gpt_results = run_evaluation(
        lambda log: classify_openai(log, "gpt-4o-mini"),
        "GPT-4o-mini"
    )
    all_model_results["gpt-4o-mini"] = gpt_results

    # Save Phase A+B results (also updates multi_log_llm_eval.json for compatibility)
    out_path = results_dir / "expanded_llm_eval.json"
    out_path.write_text(json.dumps(gpt_results, indent=2))
    print(f"\n  [Saved] {out_path}")

    # Also update the original file so phase2 router script can consume it
    compat_path = results_dir / "multi_log_llm_eval.json"
    compat_path.write_text(json.dumps(gpt_results, indent=2))
    print(f"  [Updated] {compat_path} (compatibility for phase2 router)")

    # ── Phase C: Ollama local LLM evaluation ──────────────────
    ollama_available, ollama_model = check_ollama_available()
    if ollama_available:
        print(f"\n[Phase C] Ollama detected — model: {ollama_model}")
        print("Running local LLM evaluation (200 samples)...")
        ollama_results = run_evaluation(
            lambda log: classify_ollama(log, ollama_model),
            f"Ollama/{ollama_model}"
        )
        all_model_results[f"ollama_{ollama_model}"] = ollama_results
        ollama_path = results_dir / "ollama_llm_eval.json"
        ollama_path.write_text(json.dumps(ollama_results, indent=2))
        print(f"  [Saved] {ollama_path}")
    else:
        print(f"\n[Phase C] Ollama not available ({ollama_model}) — skipping local LLM eval")
        print("  Install Ollama and run: ollama pull llama3.1:8b  to enable this.")

    # ── Combined comparison summary ────────────────────────────
    combined_output = {
        "evaluation_date": datetime.now().isoformat(),
        "framework": "Rwanda NCSA",
        "n_per_type": 50,
        "total_samples": 200,
        "log_types": ["SSH Authentication", "macOS System/Service",
                      "HTTP/API Access", "Windows Security Events"],
        "models_evaluated": list(all_model_results.keys()),
        "results": all_model_results
    }
    combined_path = results_dir / "expanded_llm_eval_combined.json"
    combined_path.write_text(json.dumps(combined_output, indent=2))
    print(f"\n  [Saved] {combined_path}")

    # ── Final comparison table ─────────────────────────────────
    print("\n" + "="*70)
    print("  FINAL COMPARISON — All Models vs All Log Types")
    print("="*70)
    log_type_names = ["SSH Authentication Logs", "macOS System/Service Logs",
                      "HTTP/API Access Logs", "Windows Security Event Logs"]
    header = f"  {'Log Type':<38}"
    for m in all_model_results:
        header += f" {m:>14}"
    print(header)
    print("  " + "-" * (38 + 15 * len(all_model_results)))
    for lt in log_type_names:
        row = f"  {lt:<38}"
        for m, res in all_model_results.items():
            match = next((r for r in res["results_by_type"] if r["log_type"] == lt), None)
            acc = f"{match['accuracy']:.1f}%" if match else "N/A"
            row += f" {acc:>14}"
        print(row)
    overall_row = f"  {'OVERALL':<38}"
    for m, res in all_model_results.items():
        overall_row += f" {res['overall_accuracy']:>13.1f}%"
    print(overall_row)
    print("="*70)
    print("\n  All results saved. Run scripts/phase2_adaptive_router_eval.py next.")

if __name__ == "__main__":
    main()
