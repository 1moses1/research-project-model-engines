#!/usr/bin/env python3
"""
Task A — Hybrid System Combined Evaluation
Addresses: R2-C4 ("components tested in isolation") and the missing combined-system table.

Evaluates ALL three system configurations on the SAME 180 real-world labeled logs:
  1. XGBoost v2 alone       (in-vocab: SSH/PAM; OOV: Windows/HTTP → expect failure)
  2. GPT-4o-mini alone      (all log types via OpenAI API)
  3. Hybrid combined        (XGBoost for in-vocab logs, GPT-4o-mini for OOV)

Routing rule (hybrid):
  - Count non-zero TF-IDF features for each log.
  - If count > 0 → XGBoost (log is in-vocabulary, SSH/PAM format recognized)
  - If count = 0 → route to GPT-4o-mini (log is OOV, Windows/HTTP format)

Dataset: identical to Phase 4 cross-dataset evaluation
  SSH    n=100  (linux_auth.log + Elastic AWS EC2 auth.log + LogPai PAM)
  Windows n=60  (Mordor APT3 PurpleSharp AD Playbook I, EventID-labeled)
  HTTP   n=20   (Elastic Apache access log, 2xx=compliant, 4xx/5xx=non-compliant)
  Total  n=180

Outputs:
  reports/hybrid_system_eval.json
  reports/hybrid_system_eval_summary.csv
"""

import csv
import json
import math
import os
import pickle
import random
import re
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
REPORTS_DIR = ROOT / "reports"
MODEL_DIR = ROOT / "models" / "xgboost_v2"
MORDOR_FILE = ROOT / "datasets/real_world/windows_events/datasets/atomic/windows/lateral_movement/host/purplesharp_ad_playbook_I_2020-10-22042947.json"
LINUX_AUTH = ROOT / "datasets/real_world/linux_auth.log"

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# Load .env for OPENAI_API_KEY
env_file = ROOT / ".env"
if env_file.exists():
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


# ──────────────────────────────────────────────────────────────────────────────
# SIMPLETFIDF (must match train_xgboost_v2.py for pickle compatibility)
# ──────────────────────────────────────────────────────────────────────────────

class SimpleTfidf:
    def __init__(self, max_features=50, ngram_range=(1, 2), min_df=2):
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.vocab_: dict = {}
        self.idf_: dict = {}

    @staticmethod
    def _tokenize(text: str, ngram_range) -> list[str]:
        tokens = [t for t in text.lower().split() if len(t) > 1 and not t.isdigit()]
        result = list(tokens)
        if ngram_range[1] >= 2:
            for i in range(len(tokens) - 1):
                result.append(f"{tokens[i]} {tokens[i+1]}")
        return result

    def fit(self, texts: list[str]):
        df_counter: Counter = Counter()
        n = len(texts)
        for text in texts:
            for t in set(self._tokenize(text, self.ngram_range)):
                df_counter[t] += 1
        valid = sorted([(t, d) for t, d in df_counter.items() if d >= self.min_df], key=lambda x: -x[1])
        top = valid[:self.max_features]
        self.vocab_ = {t: i for i, (t, _) in enumerate(top)}
        self.idf_ = {t: math.log((n + 1) / (d + 1)) + 1 for t, d in top}
        return self

    def transform(self, texts: list[str]) -> list[list[float]]:
        rows = []
        for text in texts:
            vec = [0.0] * len(self.vocab_)
            tf = Counter(self._tokenize(text, self.ngram_range))
            total = sum(tf.values()) or 1
            for term, cnt in tf.items():
                if term in self.vocab_:
                    vec[self.vocab_[term]] = cnt / total * self.idf_[term]
            rows.append(vec)
        return rows

    def get_feature_names(self) -> list[str]:
        return [t for t, _ in sorted(self.vocab_.items(), key=lambda x: x[1])]


# ──────────────────────────────────────────────────────────────────────────────
# MODEL LOADING
# ──────────────────────────────────────────────────────────────────────────────

def load_model():
    with open(MODEL_DIR / "xgboost_v2.pkl", "rb") as f:
        model = pickle.load(f)
    with open(MODEL_DIR / "tfidf_vectorizer.pkl", "rb") as f:
        tfidf = pickle.load(f)
    with open(MODEL_DIR / "family_encoder.pkl", "rb") as f:
        family_enc = pickle.load(f)
    return model, tfidf, family_enc


NUMERIC_FEATURES = ["port", "hour_of_day", "day_of_week", "is_business_hours"]


def featurize(logs: list[str], families: list[str],
              tfidf, family_enc: dict,
              numeric_rows: list[dict] | None = None) -> list[list[float]]:
    import numpy as np
    n_families = len(family_enc)
    mat = tfidf.transform(logs)
    result = []
    for i, (_, fam) in enumerate(zip(logs, families)):
        vec = list(mat[i])
        nums = numeric_rows[i] if numeric_rows else {}
        for f in NUMERIC_FEATURES:
            vec.append(float(nums.get(f, 0)))
        fv = [0.0] * n_families
        idx = family_enc.get(fam, -1)
        if idx >= 0:
            fv[idx] = 1.0
        vec.extend(fv)
        result.append(vec)
    return result


def count_active_tfidf(log: str, tfidf) -> int:
    vec = tfidf.transform([log])[0]
    return sum(1 for v in vec if v > 0)


# ──────────────────────────────────────────────────────────────────────────────
# LLM BACKEND
# ──────────────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a cybersecurity compliance analyst evaluating log entries against Rwanda's \
National Cyber Security Authority (NCSA) Minimum Cybersecurity Standards, which are grounded in \
NIST SP 800-53 Rev. 5.

Your task: classify each log entry as one of:
- compliant: The event indicates normal, authorized, secure operation consistent with security policy
- non_compliant: The event indicates a security violation, policy breach, unauthorized access, \
disabled security control, failed authentication, or anomalous activity
- uncertain: Insufficient information to determine compliance status

Respond with ONLY a JSON object containing exactly these fields:
{"status": "compliant|non_compliant|uncertain", "confidence": 0.0-1.0, \
"ncsa_control": "e.g. AC-7 or AC-2", "reason": "one sentence max 20 words"}

Do not include any text outside the JSON object."""


def parse_llm_response(raw: str) -> dict:
    raw = raw.strip()
    raw = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except json.JSONDecodeError:
                pass
    return {"status": "parse_error", "confidence": 0.0, "ncsa_control": "", "reason": raw[:100]}


def call_llm(log_text: str) -> dict:
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Log entry:\n{log_text}"},
            ],
            temperature=0,
            max_tokens=120,
            response_format={"type": "json_object"},
        )
        return parse_llm_response(response.choices[0].message.content)
    except Exception as e:
        return {"status": "api_error", "confidence": 0.0, "ncsa_control": "", "reason": str(e)[:80]}


# ──────────────────────────────────────────────────────────────────────────────
# DATASET LOADERS (identical to cross_dataset_eval_v1.py)
# ──────────────────────────────────────────────────────────────────────────────

REAL_SSH_ACCEPTED = [
    "Mar 27 13:08:09 ip-10-77-20-248 sshd[1361]: Accepted publickey for ubuntu from 85.245.107.41 port 54259 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
    "Mar 27 13:44:20 ip-10-77-20-248 sshd[2818]: Accepted publickey for ubuntu from 85.245.107.41 port 54866 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
    "Mar 27 15:48:29 ip-10-77-20-248 sshd[2998]: Accepted publickey for ubuntu from 85.245.107.41 port 57684 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
    "Mar 27 17:08:36 ip-10-77-20-248 sshd[14516]: Accepted publickey for ubuntu from 85.245.107.41 port 58981 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
    "Mar 28 10:23:57 ip-10-77-20-248 sshd[22597]: Accepted publickey for ubuntu from 85.245.107.41 port 53514 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
    "Mar 28 11:02:16 ip-10-77-20-248 sshd[22710]: Accepted publickey for ubuntu from 85.245.107.41 port 54168 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
    "Mar 28 12:01:35 ip-10-77-20-248 sshd[23132]: Accepted publickey for ubuntu from 85.245.107.41 port 54982 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
    "Mar 28 12:01:46 ip-10-77-20-248 sshd[23219]: Accepted publickey for ubuntu from 85.245.107.41 port 54983 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
    "Mar 28 12:03:14 ip-10-77-20-248 sshd[23289]: Accepted publickey for ubuntu from 85.245.107.41 port 54988 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
    "Mar 28 12:03:17 ip-10-77-20-248 sshd[23338]: Accepted publickey for ubuntu from 85.245.107.41 port 54989 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
    "Mar 28 14:09:55 ip-10-77-20-248 sshd[29069]: Accepted publickey for ubuntu from 85.245.107.41 port 55779 ssh2: RSA SHA256:Kl8kPGZrTiz7g4FO1hyqHdsSBBb5Fge6NWOobN03XJg",
]

REAL_PAM_SESSIONS = [
    "Jun 15 04:06:18 combo su(pam_unix)[21416]: session opened for user cyrus by (uid=0)",
    "Jun 15 04:12:42 combo su(pam_unix)[22644]: session opened for user news by (uid=0)",
    "Jun 16 04:10:22 combo su(pam_unix)[25178]: session opened for user cyrus by (uid=0)",
    "Jun 17 04:03:33 combo su(pam_unix)[27953]: session opened for user cyrus by (uid=0)",
    "Jun 17 04:09:43 combo su(pam_unix)[29190]: session opened for user news by (uid=0)",
    "Jun 17 20:29:26 combo sshd(pam_unix)[30631]: session opened for user test by (uid=509)",
    "Jun 18 04:07:05 combo su(pam_unix)[31791]: session opened for user cyrus by (uid=0)",
    "Jun 19 04:08:55 combo su(pam_unix)[2192]: session opened for user cyrus by (uid=0)",
    "Jun 20 04:02:54 combo su(pam_unix)[9187]: session opened for user cyrus by (uid=0)",
    "Jun 21 04:06:57 combo su(pam_unix)[12098]: session opened for user cyrus by (uid=0)",
    "Jun 22 04:05:58 combo su(pam_unix)[16663]: session opened for user cyrus by (uid=0)",
    "Jun 23 04:05:28 combo su(pam_unix)[19534]: session opened for user cyrus by (uid=0)",
    "Jun 24 04:05:34 combo su(pam_unix)[26938]: session opened for user cyrus by (uid=0)",
    "Jun 25 04:04:25 combo su(pam_unix)[29690]: session opened for user cyrus by (uid=0)",
    "Mar 27 13:17:01 ip-10-77-20-248 CRON[2623]: pam_unix(cron:session): session opened for user root",
    "Mar 27 16:17:01 ip-10-77-20-248 CRON[3550]: pam_unix(cron:session): session opened for user root",
    "Mar 28 11:17:01 ip-10-77-20-248 CRON[23035]: pam_unix(cron:session): session opened for user root",
    "Mar 27 13:08:09 ip-10-77-20-248 sshd[1361]: pam_unix(sshd:session): session opened for user ubuntu by (uid=0)",
    "Mar 28 10:23:57 ip-10-77-20-248 sshd[22597]: pam_unix(sshd:session): session opened for user ubuntu by (uid=0)",
    "Mar 28 12:01:35 ip-10-77-20-248 sshd[23132]: pam_unix(sshd:session): session opened for user ubuntu by (uid=0)",
]

WINDOWS_EVENT_DESCRIPTIONS = {
    4624: "An account was successfully logged on.",
    4625: "An account failed to log on. This may indicate brute-force or credential stuffing.",
    4634: "An account was logged off.",
    4648: "A logon was attempted using explicit credentials (pass-the-hash or lateral movement indicator).",
    4688: "A new process has been created.",
    4771: "Kerberos pre-authentication failed. Repeated failures indicate password spray or brute-force.",
    4776: "The domain controller attempted to validate the credentials for an account.",
    5145: "A network share object was checked to see whether the client can be granted access. Possible lateral movement.",
    5156: "The Windows Filtering Platform permitted a network connection.",
    4672: "Special privileges assigned to new logon (SeDebugPrivilege, SeTcbPrivilege, etc.).",
    4673: "A privileged service was called. Sensitive privilege use detected.",
    4769: "A Kerberos service ticket was requested. Unusual service names may indicate lateral movement.",
}
LOGON_TYPES = {
    "2": "Interactive (local keyboard/screen)",
    "3": "Network (SMB, RPC, named pipe)",
    "4": "Batch (scheduled task)",
    "5": "Service account logon",
    "7": "Unlock (workstation unlock)",
    "8": "NetworkCleartext (plaintext credentials over network)",
    "9": "NewCredentials (RunAs with different credentials)",
    "10": "RemoteInteractive (RDP/Terminal Services)",
    "11": "CachedInteractive (cached domain credentials)",
}

HTTP_COMPLIANT = [
    '10.105.21.199 - badeyek [08/Sep/2006:04:22:00 +0000] "GET http://www.goonernews.com/ HTTP/1.1" 200 10182',
    '10.105.21.199 - badeyek [08/Sep/2006:04:22:02 +0000] "GET http://www.google-analytics.com/urchin.js HTTP/1.1" 200 5626',
    '10.105.21.199 - badeyek [08/Sep/2006:04:22:05 +0000] "GET http://as.casalemedia.com/s? HTTP/1.1" 200 1013',
    '10.105.33.214 - adeolaegbedokun [08/Sep/2006:04:22:23 +0000] "POST http://shttp.msg.yahoo.com/notify/ HTTP/1.1" 200 484',
    '10.105.47.218 - nazsoau [08/Sep/2006:04:22:24 +0000] "GET http://hi5.com/ HTTP/1.1" 200 29359',
    '10.105.33.214 - adeolaegbedokun [08/Sep/2006:04:22:33 +0000] "GET http://insider.msg.yahoo.com/? HTTP/1.1" 200 24095',
    '10.105.33.214 - adeolaegbedokun [08/Sep/2006:04:22:33 +0000] "GET http://radio.launch.yahoo.com/radio/play/playmessenger.asp HTTP/1.1" 200 22964',
    '10.105.33.214 - adeolaegbedokun [08/Sep/2006:04:22:35 +0000] "GET http://address.yahoo.com/yab/us? HTTP/1.1" 200 699',
    '10.105.33.214 - adeolaegbedokun [08/Sep/2006:04:22:42 +0000] "GET http://us.i1.yimg.com/us.yimg.com/i/us/toolbar50x50.gif HTTP/1.1" 200 2263',
    '10.105.21.199 - badeyek [08/Sep/2006:04:22:43 +0000] "GET http://newsrss.bbc.co.uk/rss/newsonline_world_edition/front_page/rss.xml HTTP/1.1" 200 17396',
    '10.105.33.214 - adeolaegbedokun [08/Sep/2006:04:22:44 +0000] "GET http://us.news1.yimg.com/us.yimg.com/p/ap/20060906/thumb.71d29ded334347c48ac88433d033c9a9.pakistan_bin_laden_nyol440.jpg HTTP/1.1" 200 10593',
    '10.105.33.214 - adeolaegbedokun [08/Sep/2006:04:22:48 +0000] "GET http://radio.music.yahoo.com/radio/player/ymsgr/initstationfeed.asp? HTTP/1.1" 200 515',
    '10.105.21.199 - badeyek [08/Sep/2006:04:22:07 +0000] "GET http://4.adbrite.com/mb/text_group.php? HTTP/1.1" 200 1577',
    '10.105.21.199 - badeyek [08/Sep/2006:04:22:15 +0000] "GET http://dd.connextra.com/servlet/controller? HTTP/1.1" 200 30904',
]

HTTP_NONCOMPLIANT = [
    '10.105.47.218 - - [08/Sep/2006:04:22:17 +0000] "GET http://hi5.com/ HTTP/1.1" 407 1661',
    '10.105.33.214 - - [08/Sep/2006:04:22:23 +0000] "GET http://update.messenger.yahoo.com/msgrcli7.html HTTP/1.1" 407 1752',
    '10.105.37.58 - - [08/Sep/2006:04:22:26 +0000] "GET http://rms.adobe.com/read/0600/win_/ENU/read0600win_ENUadbe0000.xml HTTP/1.1" 407 1812',
    '10.105.37.17 - - [08/Sep/2006:04:22:38 +0000] "CONNECT us.mcafee.com:443 HTTP/1.1" 407 1667',
    '10.105.37.17 - - [08/Sep/2006:04:22:38 +0000] "POST http://us.mcafee.com/apps/agent/submgr/appinstru.asp HTTP/1.1" 407 1767',
    '10.105.37.65 - - [08/Sep/2006:04:22:49 +0000] "GET http://natrocket.kmip.net:5288/iesocks? HTTP/1.1" 407 1728',
    '10.105.37.180 - - [08/Sep/2006:04:23:01 +0000] "GET http://www.google.com/supported_domains HTTP/1.1" 407 1728',
    '10.105.37.180 - - [08/Sep/2006:04:23:02 +0000] "CONNECT login.live.com:443 HTTP/1.1" 407 1670',
    '10.105.37.180 - - [08/Sep/2006:04:23:31 +0000] "POST http://www.ceruleanstudios.com/cgi-bin/autosync/autosync HTTP/1.1" 401 1764',
    '10.105.37.180 - - [08/Sep/2006:04:23:32 +0000] "CONNECT update.microsoft.com:443 HTTP/1.1" 407 1688',
    '10.105.37.180 - - [08/Sep/2006:04:23:32 +0000] "POST http://stats.update.microsoft.com/ReportingWebService/ReportingWebService.asmx HTTP/1.1" 407 1850',
    '10.105.33.214 - adeolaegbedokun [08/Sep/2006:04:23:36 +0000] "GET http://pgq.yahoo.com/feed/pg4? HTTP/1.1" 500 1392',
    '10.105.37.180 - - [08/Sep/2006:04:23:36 +0000] "GET http://nds2.nokia.com/files/support/global/phones/guides/pcsuitecheck.xml HTTP/1.1" 407 1830',
    '10.105.23.141 - - [08/Sep/2006:04:23:37 +0000] "GET http://switchboard.real.com/player/? HTTP/1.1" 401 1709',
]


def _enrich_windows(ev: dict) -> str:
    """Rich enrichment matching Phase 2 expanded_llm_eval_v2.py methodology."""
    eid = int(ev.get("EventID", 0))
    desc = WINDOWS_EVENT_DESCRIPTIONS.get(eid, f"Windows Security Event {eid}.")
    computer = ev.get("Computer", ev.get("HostName", "WORKSTATION"))
    ts = ev.get("EventTime", ev.get("@timestamp", ""))[:19]
    channel = ev.get("Channel", "Security")

    parts = [f"[Windows {channel}] EventID {eid}: {desc}",
             f"Computer={computer} Time={ts}"]

    subj = ev.get("SubjectUserName", "")
    if subj and subj not in ("-", ""):
        parts.append(f"Subject={subj}")

    tgt = ev.get("TargetUserName", "")
    if tgt and tgt not in ("-", ""):
        parts.append(f"Target={tgt}")

    logon_type = str(ev.get("LogonType", ""))
    if logon_type and logon_type != "0":
        lt_desc = LOGON_TYPES.get(logon_type, f"type {logon_type}")
        parts.append(f"LogonType={logon_type} ({lt_desc})")

    ip = ev.get("IpAddress", ev.get("SourceAddress", ""))
    if ip and ip not in ("-", "::1", "::"):
        parts.append(f"SourceIP={ip}")

    proc = ev.get("ProcessName", ev.get("NewProcessName", ""))
    if proc and proc != "-":
        parts.append(f"Process={Path(str(proc)).name}")

    dst_addr = ev.get("DestAddress", "")
    dst_port = ev.get("DestPort", "")
    if dst_addr and dst_addr not in ("-", "::"):
        port_desc = {
            "389": "LDAP", "636": "LDAPS", "445": "SMB", "3389": "RDP",
            "88": "Kerberos", "135": "RPC", "443": "HTTPS", "80": "HTTP",
        }.get(str(dst_port), str(dst_port))
        parts.append(f"Dst={dst_addr}:{port_desc}")

    failure = ev.get("FailureReason", ev.get("Status", ""))
    if failure and failure not in ("-", "0x0"):
        parts.append(f"Status={failure}")

    return "  ".join(parts)


def load_all_datasets() -> list[dict]:
    """Load SSH n=100, Windows n=60, HTTP n=20 (identical to Phase 4)."""
    samples: list[dict] = []
    random.seed(RANDOM_SEED)

    # ── SSH (n=100: 50 compliant, 50 non-compliant) ──
    nc_patterns = ["Failed", "Invalid", "disconnect", "preauth", "error", "Connection closed"]
    nc_lines = []
    if LINUX_AUTH.exists():
        with open(LINUX_AUTH, errors="replace") as f:
            for line in f:
                line = line.strip()
                if line and any(p in line for p in nc_patterns):
                    nc_lines.append(line)
        random.shuffle(nc_lines)
        for line in nc_lines[:50]:
            port_m = re.search(r"port (\d+)", line)
            samples.append({
                "log_message": line,
                "true_label": "non_compliant",
                "control_family": "Access Control",
                "log_type": "ssh",
                "port": int(port_m.group(1)) if port_m else 22,
                "hour_of_day": 3, "day_of_week": 1, "is_business_hours": 0,
            })

    compliant_pool = []
    for log in REAL_SSH_ACCEPTED:
        port_m = re.search(r"port (\d+)", log)
        compliant_pool.append({
            "log_message": log, "true_label": "compliant",
            "control_family": "Access Control", "log_type": "ssh",
            "port": int(port_m.group(1)) if port_m else 22,
            "hour_of_day": 10, "day_of_week": 2, "is_business_hours": 1,
        })
    for i, log in enumerate(REAL_PAM_SESSIONS):
        compliant_pool.append({
            "log_message": log, "true_label": "compliant",
            "control_family": "Audit and Accountability" if "cron" in log.lower() else "Access Control",
            "log_type": "ssh",
            "port": 22, "hour_of_day": 4 + (i % 10), "day_of_week": i % 7,
            "is_business_hours": 1 if (4 + i % 10) >= 9 else 0,
        })
    for i in range(50):
        samples.append(dict(compliant_pool[i % len(compliant_pool)]))

    # ── Windows (n=60: 50 compliant, 10 non-compliant from Mordor) ──
    if MORDOR_FILE.exists():
        compliant_ids = {4624, 5156, 4634, 4776}
        noncompliant_ids = {4625, 4648, 4771, 5145}
        family_map = {
            4624: "Access Control", 5156: "System and Communications Protection",
            4634: "Audit and Accountability", 4776: "Identity Management and Authentication",
            4625: "Access Control", 4648: "Access Control",
            4771: "Identity Management and Authentication", 5145: "System and Communications Protection",
        }
        comp_w, noncomp_w = [], []
        with open(MORDOR_FILE) as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    ev = json.loads(line.strip())
                except json.JSONDecodeError:
                    continue
                eid_raw = ev.get("EventID") or ev.get("event_id")
                try:
                    eid = int(str(eid_raw))
                except (TypeError, ValueError):
                    continue
                enriched = _enrich_windows(ev)
                entry = {
                    "log_message": enriched,
                    "control_family": family_map.get(eid, "Access Control"),
                    "log_type": "windows",
                    "port": ev.get("DestPort", 445) or 445,
                    "hour_of_day": 10, "day_of_week": 2, "is_business_hours": 1,
                }
                if eid in compliant_ids and len(comp_w) < 50:
                    comp_w.append({**entry, "true_label": "compliant"})
                elif eid in noncompliant_ids and len(noncomp_w) < 10:
                    noncomp_w.append({**entry, "true_label": "non_compliant"})
                if len(comp_w) >= 50 and len(noncomp_w) >= 10:
                    break
        samples.extend(comp_w + noncomp_w)

    # ── HTTP (n=20: 10 compliant, 10 non-compliant) ──
    for log in HTTP_COMPLIANT:
        samples.append({
            "log_message": log, "true_label": "compliant",
            "control_family": "System and Communications Protection", "log_type": "http",
            "port": 80, "hour_of_day": 10, "day_of_week": 2, "is_business_hours": 1,
        })
    for log in HTTP_NONCOMPLIANT:
        samples.append({
            "log_message": log, "true_label": "non_compliant",
            "control_family": "System and Communications Protection", "log_type": "http",
            "port": 80, "hour_of_day": 3, "day_of_week": 1, "is_business_hours": 0,
        })

    random.shuffle(samples)
    return samples


# ──────────────────────────────────────────────────────────────────────────────
# METRICS
# ──────────────────────────────────────────────────────────────────────────────

def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    margin = (z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return (round(max(0, centre - margin) * 100, 1), round(min(1, centre + margin) * 100, 1))


def compute_metrics(preds: list[str], true_labels: list[str]) -> dict:
    tp = sum(1 for p, t in zip(preds, true_labels) if p == "non_compliant" and t == "non_compliant")
    tn = sum(1 for p, t in zip(preds, true_labels) if p == "compliant" and t == "compliant")
    fp = sum(1 for p, t in zip(preds, true_labels) if p == "non_compliant" and t == "compliant")
    fn = sum(1 for p, t in zip(preds, true_labels) if p == "compliant" and t == "non_compliant")
    n = len(preds)
    n_pos = tp + fn
    n_neg = fp + tn
    accuracy = (tp + tn) / n if n > 0 else 0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    fpr = fp / n_neg if n_neg > 0 else 0
    f1_ci = wilson_ci(tp, n_pos) if n_pos > 0 else (0.0, 100.0)
    acc_ci = wilson_ci(tp + tn, n)
    return {
        "n": n, "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "accuracy_pct": round(accuracy * 100, 1),
        "precision_pct": round(precision * 100, 1),
        "recall_pct": round(recall * 100, 1),
        "f1_pct": round(f1 * 100, 1),
        "fpr_pct": round(fpr * 100, 1),
        "f1_ci_95": list(f1_ci),
        "acc_ci_95": list(acc_ci),
    }


# ──────────────────────────────────────────────────────────────────────────────
# PREDICTION FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def predict_xgboost(samples: list[dict], model, tfidf, family_enc) -> list[str]:
    import numpy as np
    logs = [s["log_message"] for s in samples]
    families = [s["control_family"] for s in samples]
    numeric = [{"port": s.get("port", 22), "hour_of_day": s.get("hour_of_day", 10),
                "day_of_week": s.get("day_of_week", 2),
                "is_business_hours": s.get("is_business_hours", 1)}
               for s in samples]
    X = np.array(featurize(logs, families, tfidf, family_enc, numeric))
    preds = model.predict(X)
    return ["non_compliant" if p == 1 else "compliant" for p in preds]


def predict_llm(samples: list[dict], delay: float = 0.3) -> list[str]:
    preds = []
    n = len(samples)
    for i, s in enumerate(samples):
        result = call_llm(s["log_message"])
        status = result.get("status", "uncertain")
        if status not in ("compliant", "non_compliant"):
            status = "non_compliant"
        preds.append(status)
        if (i + 1) % 20 == 0:
            print(f"    LLM progress: {i+1}/{n}", flush=True)
        time.sleep(delay)
    return preds


def predict_hybrid(samples: list[dict], model, tfidf, family_enc,
                   xgb_preds: list[str], llm_preds: list[str]) -> list[str]:
    """
    Routing rule: if TF-IDF active features > 0 → use XGBoost prediction
                  else → use GPT-4o-mini prediction
    Both component predictions are pre-computed; hybrid just selects based on route.
    """
    hybrid_preds = []
    routes = []
    for i, s in enumerate(samples):
        n_active = count_active_tfidf(s["log_message"], tfidf)
        if n_active > 0:
            hybrid_preds.append(xgb_preds[i])
            routes.append("xgboost")
        else:
            hybrid_preds.append(llm_preds[i])
            routes.append("gpt-4o-mini")
    return hybrid_preds, routes


# ──────────────────────────────────────────────────────────────────────────────
# PER-TYPE BREAKDOWN
# ──────────────────────────────────────────────────────────────────────────────

def evaluate_by_type(samples: list[dict], preds: list[str]) -> dict:
    types = ["ssh", "windows", "http"]
    result = {}
    for lt in types:
        idx = [i for i, s in enumerate(samples) if s["log_type"] == lt]
        if not idx:
            continue
        sub_preds = [preds[i] for i in idx]
        sub_labels = [samples[i]["true_label"] for i in idx]
        result[lt] = compute_metrics(sub_preds, sub_labels)
        result[lt]["n"] = len(idx)
    return result


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    import sys
    print("=== Hybrid System Combined Evaluation ===", flush=True)
    print(f"Loading datasets...", flush=True)

    samples = load_all_datasets()
    ssh_n = sum(1 for s in samples if s["log_type"] == "ssh")
    win_n = sum(1 for s in samples if s["log_type"] == "windows")
    http_n = sum(1 for s in samples if s["log_type"] == "http")
    print(f"  Total: {len(samples)} samples  (SSH={ssh_n}, Windows={win_n}, HTTP={http_n})", flush=True)

    print("Loading XGBoost model...", flush=True)
    model, tfidf, family_enc = load_model()

    # ── Step 1: XGBoost predictions ──
    print("\n[1/3] XGBoost v2 predictions...", flush=True)
    xgb_preds = predict_xgboost(samples, model, tfidf, family_enc)

    # ── Step 2: LLM predictions ──
    print("\n[2/3] GPT-4o-mini predictions (180 API calls)...", flush=True)
    llm_preds = predict_llm(samples, delay=0.3)

    # ── Step 3: Hybrid predictions ──
    print("\n[3/3] Hybrid routing (TF-IDF active > 0 → XGBoost, else → GPT-4o-mini)...", flush=True)
    hybrid_preds, routes = predict_hybrid(samples, model, tfidf, family_enc, xgb_preds, llm_preds)
    n_routed_xgb = routes.count("xgboost")
    n_routed_llm = routes.count("gpt-4o-mini")
    print(f"  Routed to XGBoost: {n_routed_xgb}  |  Routed to GPT-4o-mini: {n_routed_llm}", flush=True)

    # ── Aggregate metrics ──
    true_labels = [s["true_label"] for s in samples]
    xgb_overall = compute_metrics(xgb_preds, true_labels)
    llm_overall = compute_metrics(llm_preds, true_labels)
    hyb_overall = compute_metrics(hybrid_preds, true_labels)

    xgb_by_type = evaluate_by_type(samples, xgb_preds)
    llm_by_type = evaluate_by_type(samples, llm_preds)
    hyb_by_type = evaluate_by_type(samples, hybrid_preds)

    # ── Console summary table ──
    print("\n" + "=" * 80, flush=True)
    print("COMBINED EVALUATION RESULTS", flush=True)
    print("=" * 80, flush=True)
    header = f"{'System':<22} {'Acc%':>6} {'F1%':>6} {'FPR%':>6} {'F1 CI 95%':>18}"
    print(header)
    print("-" * 60)
    for label, m in [("XGBoost v2 alone", xgb_overall),
                     ("GPT-4o-mini alone", llm_overall),
                     ("Hybrid combined", hyb_overall)]:
        ci = f"[{m['f1_ci_95'][0]}, {m['f1_ci_95'][1]}]"
        print(f"{label:<22} {m['accuracy_pct']:>6.1f} {m['f1_pct']:>6.1f} {m['fpr_pct']:>6.1f} {ci:>18}")
    print()
    print("Per-type breakdown:", flush=True)
    print(f"{'Type':<12} {'System':<20} {'n':>4} {'Acc%':>6} {'F1%':>6} {'FPR%':>6}")
    print("-" * 60)
    for lt in ["ssh", "windows", "http"]:
        for label, bt in [("XGBoost", xgb_by_type),
                          ("GPT-4o-mini", llm_by_type),
                          ("Hybrid", hyb_by_type)]:
            m = bt.get(lt, {})
            if m:
                print(f"{lt:<12} {label:<20} {m['n']:>4} {m['accuracy_pct']:>6.1f} "
                      f"{m['f1_pct']:>6.1f} {m['fpr_pct']:>6.1f}")
        print()

    # ── Save JSON ──
    output = {
        "generated_at": datetime.utcnow().isoformat(),
        "model_xgboost": "XGBoost v2 (models/xgboost_v2/)",
        "model_llm": "gpt-4o-mini",
        "routing_rule": "TF-IDF active features > 0 → XGBoost; = 0 → GPT-4o-mini",
        "n_total": len(samples),
        "n_ssh": ssh_n, "n_windows": win_n, "n_http": http_n,
        "n_routed_xgboost": n_routed_xgb,
        "n_routed_llm": n_routed_llm,
        "overall": {
            "xgboost_alone": xgb_overall,
            "llm_alone": llm_overall,
            "hybrid_combined": hyb_overall,
        },
        "by_log_type": {
            "xgboost_alone": xgb_by_type,
            "llm_alone": llm_by_type,
            "hybrid_combined": hyb_by_type,
        },
        "per_sample": [
            {
                "log_type": s["log_type"],
                "true_label": s["true_label"],
                "xgb_pred": xgb_preds[i],
                "llm_pred": llm_preds[i],
                "hybrid_pred": hybrid_preds[i],
                "hybrid_route": routes[i],
            }
            for i, s in enumerate(samples)
        ],
    }
    out_json = REPORTS_DIR / "hybrid_system_eval.json"
    with open(out_json, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nSaved: {out_json}", flush=True)

    # ── Save CSV summary ──
    out_csv = REPORTS_DIR / "hybrid_system_eval_summary.csv"
    rows = []
    for system, overall, by_type in [
        ("XGBoost v2 alone", xgb_overall, xgb_by_type),
        ("GPT-4o-mini alone", llm_overall, llm_by_type),
        ("Hybrid combined", hyb_overall, hyb_by_type),
    ]:
        rows.append({
            "system": system, "log_type": "overall",
            "n": overall["n"],
            "accuracy_pct": overall["accuracy_pct"],
            "f1_pct": overall["f1_pct"],
            "fpr_pct": overall["fpr_pct"],
            "f1_ci_95_lo": overall["f1_ci_95"][0],
            "f1_ci_95_hi": overall["f1_ci_95"][1],
        })
        for lt, m in by_type.items():
            rows.append({
                "system": system, "log_type": lt,
                "n": m["n"],
                "accuracy_pct": m["accuracy_pct"],
                "f1_pct": m["f1_pct"],
                "fpr_pct": m["fpr_pct"],
                "f1_ci_95_lo": m["f1_ci_95"][0],
                "f1_ci_95_hi": m["f1_ci_95"][1],
            })
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["system", "log_type", "n",
                                          "accuracy_pct", "f1_pct", "fpr_pct",
                                          "f1_ci_95_lo", "f1_ci_95_hi"])
        w.writeheader()
        w.writerows(rows)
    print(f"Saved: {out_csv}", flush=True)
    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
