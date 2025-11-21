#!/usr/bin/env python3
"""
Fix Rwanda NCSA Control Taxonomy - Create Unique Control IDs

ISSUE: The source file has 169 requirements but only 141 unique requirement_ids
because some IDs appear multiple times within the same family with different content.

SOLUTION: Create unique control IDs by combining family index + requirement index
Format: RWNCSA-{family_idx}-{req_idx}

Example:
- Original: "4-1", "4-1" (duplicate in same family)
- Fixed: "RWNCSA-1-1", "RWNCSA-1-2" (unique)
"""

import json
from pathlib import Path
from collections import defaultdict

def create_family_code(family_name: str) -> str:
    """Create a short code from family name"""
    # Map to standard abbreviations
    codes = {
        "Security Policy and Procedures": "SP",
        "Access Control": "AC",
        "Awareness and Training": "AT",
        "Audit and Accountability": "AU",
        "Configuration Management": "CM",
        "Contingency Planning": "CP",
        "Identity Management and Authentication": "IA",
        "Incident Response": "IR",
        "Maintenance": "MA",
        "Media Protection": "MP",
        "Physical and Environmental Protection": "PE",
        "Risk Assessment": "RA",
        "System and Communications Protection": "SC",
        "System and Information Integrity": "SI"
    }
    return codes.get(family_name, "XX")

def fix_taxonomy():
    """Fix the control taxonomy by creating unique IDs"""

    print("=" * 80)
    print("FIXING RWANDA NCSA CONTROL TAXONOMY")
    print("=" * 80)
    print()

    # Load source file
    with open('rwanda_ncsa_validated_controls.json', 'r') as f:
        source = json.load(f)

    # Load existing taxonomy
    taxonomy_path = Path('data/processed/control_taxonomy_validated.json')
    with open(taxonomy_path, 'r') as f:
        taxonomy = json.load(f)

    print(f"📥 Loaded source: {source['metadata']['total_requirements']} requirements")
    print(f"📥 Loaded taxonomy: {len(taxonomy['rwanda'])} Rwanda controls")
    print()

    # Create corrected Rwanda controls with unique IDs
    corrected_rwanda_controls = []
    requirement_counter = 1  # Global counter for unique IDs

    for family_idx, family in enumerate(source.get('control_families', []), 1):
        family_name = family.get('family_name')
        family_code = create_family_code(family_name)

        print(f"Processing family {family_idx}: {family_name} ({family_code})")

        for req_idx, req in enumerate(family.get('requirements', []), 1):
            # Create unique control ID
            # Format: RWNCSA-{FamilyCode}-{GlobalNumber}
            unique_id = f"RWNCSA-{family_code}-{requirement_counter}"

            # Build control object
            control = {
                "control_id": unique_id,
                "original_id": req.get('requirement_id'),  # Keep original for reference
                "framework": "Rwanda-NCSA",
                "name": f"{family_name} - {req.get('requirement_id')}",
                "family": family_name,
                "family_code": family_code,
                "description": req.get('requirement_text', ''),
                "full_text": req.get('requirement_text', ''),
                "chapter": req.get('chapter'),
                "compliance_type": req.get('compliance_type', 'Basic'),
                "nist_mapping": req.get('nist_controls', []),
                "log_indicators": [
                    "policy updated",
                    "compliance check",
                    "audit log"
                ],
                "compliance_criteria": {
                    "must_have": ["documentation"],
                    "frequency": "periodic",
                    "retention": "365 days"
                }
            }

            corrected_rwanda_controls.append(control)
            requirement_counter += 1

        print(f"  ✅ Processed {len(family.get('requirements', []))} requirements")

    print()
    print(f"✅ Created {len(corrected_rwanda_controls)} unique Rwanda NCSA controls")
    print()

    # Update taxonomy
    taxonomy['rwanda'] = corrected_rwanda_controls
    taxonomy['metadata']['last_updated'] = "2025-11-20"
    taxonomy['metadata']['fix_applied'] = "Unique control IDs created to fix duplicates"

    # Save corrected taxonomy
    output_path = Path('data/processed/control_taxonomy_validated_fixed.json')
    with open(output_path, 'w') as f:
        json.dump(taxonomy, f, indent=2)

    print(f"💾 Saved corrected taxonomy to: {output_path}")
    print()

    # Verification
    rwanda_ids = [c['control_id'] for c in corrected_rwanda_controls]
    unique_ids = set(rwanda_ids)

    print("=" * 80)
    print("VERIFICATION")
    print("=" * 80)
    print(f"Total Rwanda controls: {len(corrected_rwanda_controls)}")
    print(f"Unique control IDs: {len(unique_ids)}")
    print(f"Duplicates: {len(rwanda_ids) - len(unique_ids)}")
    print()

    if len(rwanda_ids) == len(unique_ids):
        print("✅ SUCCESS: All control IDs are unique!")
    else:
        print("❌ ERROR: Still have duplicates")

    print()
    print("Sample controls:")
    for i in range(min(3, len(corrected_rwanda_controls))):
        c = corrected_rwanda_controls[i]
        print(f"  {c['control_id']} (was {c['original_id']}): {c['name'][:60]}...")

    return corrected_rwanda_controls

if __name__ == "__main__":
    fix_taxonomy()
