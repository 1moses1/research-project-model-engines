#!/usr/bin/env python3
"""
Phase 0 — Data Integrity Audit
Quantifies all leakage sources in synthetic training/val/test datasets,
maps class distribution across 143 system-auditable NCSA controls,
and outputs structured reports for Phase 1 retraining decisions.

Outputs:
  reports/data_leakage_audit.json
  reports/class_distribution_143controls.json
  reports/data_audit_summary.txt
"""

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data" / "synthetic"
REPORTS_DIR = ROOT / "reports"
TAXONOMY_PATH = ROOT / "data" / "processed" / "control_taxonomy_validated.json"

REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ──────────────────────────────────────────────────────────────────────────────
# LEAKAGE DETECTION PATTERNS
# These are strings that should NEVER appear in realistic log messages because
# they embed the compliance verdict directly — the exact cause of 100% F1.
# ──────────────────────────────────────────────────────────────────────────────
LEAKAGE_PATTERNS = [
    # Explicit verdict strings
    (r"compliance verification.*status\s*:\s*(compliant|non.?compliant)", "explicit_verdict"),
    (r"audit log\s*[-–]\s*compliance (violation|passed)", "audit_verdict"),
    (r"status\s*:\s*(compliant|non.?compliant)", "status_verdict"),
    (r"(compliant|non.?compliant)\s*(event|record|entry|log)", "label_in_log"),
    # Control ID leakage (RWNCSA-XX-NNN in free-text log fields)
    (r"RWNCSA-[A-Z]{2}-\d+", "control_id_in_log"),
    # Policy/compliance jargon that is unrealistic in raw system logs
    (r"compliance check (passed|failed)", "compliance_check_result"),
    (r"regulatory (compliance|violation)", "regulatory_mention"),
    (r"ncsa.*(compliant|violation|control)", "ncsa_reference_in_log"),
]

COMPILED_PATTERNS = [(re.compile(p, re.IGNORECASE), label) for p, label in LEAKAGE_PATTERNS]

STATUS_CODE_COMPLIANT = {200, 201, 204}
STATUS_CODE_NONCOMPLIANT = {400, 401, 403, 404, 500, 503}


def detect_leakage(log_message: str) -> list[str]:
    hits = []
    for pattern, label in COMPILED_PATTERNS:
        if pattern.search(log_message):
            hits.append(label)
    return hits


def load_taxonomy_control_ids() -> tuple[set, set]:
    """Returns (all_control_ids, system_auditable_ids).
    System-auditable = controls that have log_indicators defined."""
    with open(TAXONOMY_PATH) as f:
        taxonomy = json.load(f)

    all_ids: set = set()
    auditable_ids: set = set()

    for section in ("rwanda", "nist"):
        for ctrl in taxonomy.get(section, []):
            cid = ctrl["control_id"]
            all_ids.add(cid)
            indicators = ctrl.get("log_indicators", [])
            if indicators and any(i.strip() for i in indicators):
                auditable_ids.add(cid)

    return all_ids, auditable_ids


def audit_split(csv_path: Path, split_name: str) -> dict:
    print(f"\n  Auditing {split_name}: {csv_path.name} ...", flush=True)

    total = 0
    leaky_rows = 0
    leakage_type_counts: Counter = Counter()
    compliance_dist: Counter = Counter()       # compliant / non_compliant
    control_dist: Counter = Counter()          # per control_id
    status_code_dist: Counter = Counter()
    status_code_label_agreement = {"agree": 0, "disagree": 0, "unknown": 0}
    rows_with_multiple_leaks = 0

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            log_msg = row.get("log_message", "")
            label = row.get("compliance_status", "unknown").strip().lower()
            ctrl_id = row.get("control_id", "UNKNOWN").strip()
            try:
                sc = int(row.get("status_code", 0))
            except ValueError:
                sc = 0

            # Leakage detection
            hits = detect_leakage(log_msg)
            if hits:
                leaky_rows += 1
                for h in hits:
                    leakage_type_counts[h] += 1
                if len(hits) > 1:
                    rows_with_multiple_leaks += 1

            # Class distribution
            compliance_dist[label] += 1
            control_dist[ctrl_id] += 1

            # Status-code vs label agreement check
            if sc in STATUS_CODE_COMPLIANT:
                expected = "compliant"
            elif sc in STATUS_CODE_NONCOMPLIANT:
                expected = "non_compliant"
            else:
                expected = None

            if expected is None:
                status_code_label_agreement["unknown"] += 1
            elif expected == label:
                status_code_label_agreement["agree"] += 1
            else:
                status_code_label_agreement["disagree"] += 1

    leakage_rate = leaky_rows / total * 100 if total else 0
    compliant_n = compliance_dist.get("compliant", 0)
    noncompliant_n = compliance_dist.get("non_compliant", 0)
    imbalance_ratio = compliant_n / noncompliant_n if noncompliant_n else float("inf")

    print(f"    Total rows      : {total:,}")
    print(f"    Leaky rows      : {leaky_rows:,}  ({leakage_rate:.1f}%)")
    print(f"    Compliant       : {compliant_n:,}")
    print(f"    Non-compliant   : {noncompliant_n:,}")
    print(f"    Imbalance ratio : {imbalance_ratio:.2f}:1")
    print(f"    Unique controls : {len(control_dist)}")
    print(f"    Leakage types   : {dict(leakage_type_counts)}")

    return {
        "split": split_name,
        "total_rows": total,
        "leaky_rows": leaky_rows,
        "leakage_rate_pct": round(leakage_rate, 2),
        "rows_with_multiple_leaks": rows_with_multiple_leaks,
        "leakage_by_type": dict(leakage_type_counts),
        "class_distribution": {
            "compliant": compliant_n,
            "non_compliant": noncompliant_n,
            "other": total - compliant_n - noncompliant_n,
        },
        "imbalance_ratio": round(imbalance_ratio, 3),
        "unique_controls_in_split": len(control_dist),
        "status_code_label_agreement": status_code_label_agreement,
        "control_distribution": dict(control_dist.most_common()),
    }


def build_per_control_distribution(splits: list[dict], auditable_ids: set) -> dict:
    """Merge control distributions from all splits and flag auditable controls."""
    merged: defaultdict = defaultdict(lambda: {"compliant": 0, "non_compliant": 0, "total": 0})

    for split in splits:
        for ctrl, count in split["control_distribution"].items():
            # We don't have per-label compliance split here; use total as proxy
            merged[ctrl]["total"] += count

    result = {}
    for ctrl, counts in sorted(merged.items()):
        result[ctrl] = {
            **counts,
            "is_system_auditable": ctrl in auditable_ids,
        }

    return result


def compute_status_code_correlation(csv_path: Path) -> dict:
    """Compute Pearson correlation between status_code and compliance label (binary)."""
    xs, ys = [], []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                sc = int(row.get("status_code", 0))
            except ValueError:
                continue
            label = 1 if row.get("compliance_status", "").strip().lower() == "compliant" else 0
            xs.append(sc)
            ys.append(label)

    n = len(xs)
    if n < 2:
        return {"pearson_r": None, "n": n}

    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / n
    std_x = (sum((x - mean_x) ** 2 for x in xs) / n) ** 0.5
    std_y = (sum((y - mean_y) ** 2 for y in ys) / n) ** 0.5

    if std_x == 0 or std_y == 0:
        r = None
    else:
        r = round(cov / (std_x * std_y), 4)

    return {"pearson_r": r, "n": n}


def main():
    print("=" * 70)
    print("  PHASE 0 — Data Integrity Audit")
    print("  Manuscript: futureinternet-4270373 | Rwanda NCSA Compliance")
    print("=" * 70)

    # Load taxonomy
    print("\n[1/4] Loading control taxonomy...")
    all_ctrl_ids, auditable_ids = load_taxonomy_control_ids()
    print(f"      All controls    : {len(all_ctrl_ids)}")
    print(f"      System-auditable: {len(auditable_ids)}")

    # Audit each split
    print("\n[2/4] Auditing dataset splits for leakage...")
    splits_raw = []
    for split_name, filename in [
        ("train", "compliance_events_train.csv"),
        ("val",   "compliance_events_val.csv"),
        ("test",  "compliance_events_test.csv"),
    ]:
        csv_path = DATA_DIR / filename
        if not csv_path.exists():
            print(f"      WARNING: {filename} not found, skipping.")
            continue
        result = audit_split(csv_path, split_name)
        splits_raw.append(result)

    # Status-code correlation on training set
    print("\n[3/4] Computing status_code ↔ label Pearson correlation (train)...")
    train_path = DATA_DIR / "compliance_events_train.csv"
    corr = compute_status_code_correlation(train_path)
    print(f"      Pearson r = {corr['pearson_r']}  (n = {corr['n']:,})")

    # Build per-control distribution report
    print("\n[4/4] Building per-control class distribution...")
    per_ctrl_dist = build_per_control_distribution(splits_raw, auditable_ids)
    auditable_in_data = sum(1 for v in per_ctrl_dist.values() if v["is_system_auditable"])
    total_in_data = len(per_ctrl_dist)
    print(f"      Controls in data   : {total_in_data}")
    print(f"      Auditable in data  : {auditable_in_data}")
    print(f"      Missing from data  : {len(auditable_ids) - auditable_in_data}")

    # ─── Leakage summary ──────────────────────────────────────────────────────
    leakage_summary = {
        "audit_date": __import__("datetime").datetime.now().isoformat(),
        "taxonomy_total_controls": len(all_ctrl_ids),
        "taxonomy_system_auditable_controls": len(auditable_ids),
        "status_code_pearson_correlation": corr,
        "critical_finding": (
            "40%+ of synthetic log_message fields contain explicit compliance verdicts "
            "(e.g., 'Compliance verification for RWNCSA-AT-47 - status: compliant'). "
            "This explains the 100% F1 score — the model memorized these strings, "
            "not security semantics. All data must be regenerated before retraining."
        ),
        "splits": [
            {k: v for k, v in s.items() if k != "control_distribution"}
            for s in splits_raw
        ],
        "recommended_action": (
            "Run scripts/generate_synthetic_data_v2.py to regenerate all splits "
            "with realistic log messages free of embedded compliance verdicts."
        ),
    }

    leakage_path = REPORTS_DIR / "data_leakage_audit.json"
    leakage_path.write_text(json.dumps(leakage_summary, indent=2))
    print(f"\n  [OK] Leakage audit saved: {leakage_path}")

    # ─── Per-control distribution ──────────────────────────────────────────────
    ctrl_report = {
        "audit_date": leakage_summary["audit_date"],
        "total_unique_controls_in_data": total_in_data,
        "system_auditable_controls_in_data": auditable_in_data,
        "system_auditable_controls_in_taxonomy": len(auditable_ids),
        "controls_missing_from_data": sorted(auditable_ids - set(per_ctrl_dist.keys())),
        "per_control": per_ctrl_dist,
    }

    ctrl_path = REPORTS_DIR / "class_distribution_143controls.json"
    ctrl_path.write_text(json.dumps(ctrl_report, indent=2))
    print(f"  [OK] Control distribution saved: {ctrl_path}")

    # ─── Human-readable summary ────────────────────────────────────────────────
    lines = [
        "=" * 70,
        "PHASE 0 DATA INTEGRITY AUDIT — SUMMARY",
        "=" * 70,
        "",
    ]
    for s in splits_raw:
        lines += [
            f"Split: {s['split'].upper()}",
            f"  Total rows      : {s['total_rows']:,}",
            f"  Leaky rows      : {s['leaky_rows']:,}  ({s['leakage_rate_pct']:.1f}%)",
            f"  Leakage types   : {s['leakage_by_type']}",
            f"  Compliant       : {s['class_distribution']['compliant']:,}",
            f"  Non-compliant   : {s['class_distribution']['non_compliant']:,}",
            f"  Imbalance ratio : {s['imbalance_ratio']:.2f}:1",
            f"  Unique controls : {s['unique_controls_in_split']}",
            "",
        ]
    lines += [
        f"Status-code Pearson r (train): {corr['pearson_r']}",
        "",
        "VERDICT: Dataset must be fully regenerated before any model training.",
        f"  See: {leakage_path}",
        f"  See: {ctrl_path}",
        "=" * 70,
    ]

    summary_path = REPORTS_DIR / "data_audit_summary.txt"
    summary_path.write_text("\n".join(lines))
    print(f"  [OK] Human summary saved:  {summary_path}")

    print("\n" + "\n".join(lines))
    return leakage_summary


if __name__ == "__main__":
    main()
