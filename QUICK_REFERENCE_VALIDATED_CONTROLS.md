# Quick Reference: Using Validated Rwanda NCSA Controls

## At a Glance

✅ **Use This**: `control_taxonomy_validated.json`
❌ **Never Use**: `control_taxonomy.json` (backed up as `.backup`)

---

## Quick Commands

### Validate Controls Before Training
```bash
python scripts/validate_control_taxonomy.py
```

### Regenerate Training Data
```bash
python src/data_pipeline/synthetic_generator.py --num-events 100000
```

### Train Models
```bash
python train_all_models.py
```

---

## Control Count

| Framework | Count | Role |
|-----------|-------|------|
| Rwanda NCSA | 169 requirements | PRIMARY |
| NIST SP 800-53 | 27 controls | SECONDARY |
| **Total** | **196** | - |

---

## Official Rwanda NCSA Families (14)

1. Security Policy and Procedures (16)
2. Access Control (26)
3. Awareness and Training (7)
4. Audit and Accountability (26)
5. Configuration Management (14)
6. Identity Management and Authentication (13)
7. Incident Response (6)
8. Maintenance (7)
9. Media Protection (9)
10. Personnel Security (11)
11. Physical and Environmental Protection (10)
12. Risk Assessment (3)
13. Security Assessment (4)
14. System and Communications Protection (17)

---

## Requirement ID Format

✅ **Correct**: `5-2`, `7-1`, `14-3` (Chapter-Number)
❌ **Wrong**: `RW-AC-001`, `RW-VM-003` (Fictional)

---

## In Your Code

### Python
```python
# Load validated taxonomy
with open('data/processed/control_taxonomy_validated.json') as f:
    taxonomy = json.load(f)

# Verify it's validated
assert taxonomy['metadata']['validated'] == True

# Use Rwanda requirements (PRIMARY)
rwanda_reqs = taxonomy['rwanda']  # 169 requirements

# Use NIST controls (SECONDARY)
nist_controls = taxonomy['nist']  # 27 controls
```

### Synthetic Data Generation
```python
from src.data_pipeline.synthetic_generator import SyntheticEventGenerator

# Automatically uses validated taxonomy
generator = SyntheticEventGenerator()  # Uses control_taxonomy_validated.json

# Generate events
events = generator.generate_events(num_events=100000)
```

---

## Validation Checks

Run this BEFORE every training session:
```bash
python scripts/validate_control_taxonomy.py
```

Expected output:
```
✅ ALL VALIDATION CHECKS PASSED
✅ Rwanda requirements count: 169
✅ All 14 official Rwanda NCSA families present
✅ No fictional 'RW-*' control IDs found
```

---

## Common Mistakes to Avoid

❌ **Don't**: Use `control_taxonomy.json`
✅ **Do**: Use `control_taxonomy_validated.json`

❌ **Don't**: Create controls with IDs like `RW-XX-001`
✅ **Do**: Use official requirement IDs like `5-2`, `7-1`

❌ **Don't**: Skip validation before training
✅ **Do**: Always run validation script first

❌ **Don't**: Treat NIST and Rwanda as equal
✅ **Do**: Rwanda PRIMARY, NIST SECONDARY

---

## File Locations

```
data/processed/
├── control_taxonomy_validated.json          ← USE THIS
├── control_taxonomy_OLD_INCORRECT.json.backup  ← Backup only
└── ...

scripts/
└── validate_control_taxonomy.py             ← Run before training

src/data_pipeline/
├── control_mapper_validated.py              ← New validated mapper
└── synthetic_generator.py                   ← Updated to use validated

docs/regulatory_frameworks/
└── Minimum_Cybersecurity_Standards_for_Public_Institutions.pdf  ← Source
```

---

## Decision Tree: Which File to Use?

```
Q: Are you training a model?
│
├─ Yes → Use control_taxonomy_validated.json
│        Run validation script first!
│
└─ No → Are you validating controls?
         │
         ├─ Yes → Run scripts/validate_control_taxonomy.py
         │
         └─ No → Are you adding new controls?
                  │
                  ├─ Yes → Extract from official PDF
                  │        Update control_mapper_validated.py
                  │        Run validation script
                  │
                  └─ No → Review RWANDA_NCSA_CONTROL_FIX_SUMMARY.md
```

---

## Emergency: If You Accidentally Use Old Controls

1. **Stop training immediately**
2. **Run validation**: `python scripts/validate_control_taxonomy.py`
3. **Check error output** for guidance
4. **Delete generated data** from incorrect taxonomy
5. **Regenerate data** with validated controls
6. **Restart training** with clean data

---

## Questions?

1. Read: `RWANDA_NCSA_CONTROL_FIX_SUMMARY.md`
2. Read: `CONTROL_TAXONOMY_VALIDATION_REPORT.md`
3. Read: `RWANDA_NCSA_CONTROL_ANALYSIS.md`
4. Check: Official PDF in `docs/regulatory_frameworks/`

---

**Remember**: Rwanda NCSA is PRIMARY, NIST is SECONDARY!
