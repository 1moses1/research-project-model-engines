#!/usr/bin/env python3
"""
Test Script for 47 Rwanda NCSA Controls
Tests all parsers and decision logic with real macOS data
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Add engines/shared to path
sys.path.insert(0, str(Path(__file__).parent / 'engines' / 'shared'))

from evidence_parsers import RwandaNCSAEvidenceParser
from rwanda_decision_engine import RwandaNCSADecisionEngine


def main():
    """Test all 47 controls with real macOS data"""

    print("=" * 80)
    print(" TESTING 47 RWANDA NCSA CONTROLS")
    print("=" * 80)
    print(f"Test ID: TEST-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    print()

    # Load control definitions
    controls_file = Path(__file__).parent / 'engines' / 'shared' / 'rwanda_ncsa_controls.json'
    with open(controls_file) as f:
        controls_data = json.load(f)

    controls = controls_data['controls']
    print(f"✓ Loaded {len(controls)} control definitions\n")

    # Initialize parsers and decision engine
    parsers = RwandaNCSAEvidenceParser()
    decision_engine = RwandaNCSADecisionEngine()

    print("✓ Initialized parsers and decision engine\n")

    # Test results
    results = {
        "total_controls": len(controls),
        "tested": 0,
        "parser_success": 0,
        "parser_failed": 0,
        "decision_success": 0,
        "decision_failed": 0,
        "controls": []
    }

    print("-" * 80)
    print("PHASE 1: TESTING PARSERS")
    print("-" * 80)

    # Test each control
    for control_id, control_spec in sorted(controls.items()):
        results["tested"] += 1
        control_name = control_spec['name']

        print(f"\n[{results['tested']}/{len(controls)}] Testing {control_id}: {control_name}")

        # Get audit command
        macos_impl = control_spec.get('macos_implementation', {})
        audit_cmd = macos_impl.get('audit_command', '')

        if not audit_cmd:
            print(f"  ⚠ No audit command defined - skipping")
            results["controls"].append({
                "control_id": control_id,
                "name": control_name,
                "parser_status": "SKIPPED",
                "decision_status": "SKIPPED",
                "reason": "No audit command"
            })
            continue

        print(f"  Command: {audit_cmd}")

        # Execute command
        try:
            # Expand shell variables and tilde for proper subprocess execution
            import os
            import shlex

            # Expand environment variables and tilde
            expanded_cmd = os.path.expandvars(audit_cmd)
            expanded_cmd = os.path.expanduser(expanded_cmd)

            # Use shlex for proper shell-aware splitting
            cmd_parts = shlex.split(expanded_cmd)

            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=60  # Increased from 10 to 60 for slow commands like softwareupdate
            )

            output = result.stdout if result.stdout else result.stderr
            print(f"  Output: {len(output)} bytes (exit code: {result.returncode})")

        except Exception as e:
            print(f"  ✗ Command failed: {str(e)[:50]}")
            results["parser_failed"] += 1
            results["controls"].append({
                "control_id": control_id,
                "name": control_name,
                "parser_status": "COMMAND_FAILED",
                "decision_status": "NOT_TESTED",
                "error": str(e)
            })
            continue

        # Test parser
        try:
            parsed = parsers.parse_evidence(audit_cmd, output, control_id)

            if parsed.get('parsing_successful'):
                print(f"  ✓ Parser: {parsed['evidence_summary']}")
                print(f"    Compliance: {parsed['compliance_status']}")
                print(f"    Score: {parsed['compliance_score']:.1f}%")

                if parsed.get('gaps'):
                    print(f"    Gaps: {len(parsed['gaps'])}")
                    for gap in parsed['gaps'][:2]:  # Show first 2 gaps
                        print(f"      - {gap.get('requirement', 'N/A')}")

                results["parser_success"] += 1
                parser_status = "SUCCESS"

                # Test decision engine
                try:
                    decisions = decision_engine.make_decisions([parsed])
                    decision = decisions[0] if decisions else None

                    if decision:
                        print(f"  ✓ Decision: {decision.get('final_decision', 'N/A')}")
                        print(f"    Confidence: {decision.get('confidence', 0):.2f}")
                        print(f"    Method: {decision.get('decision_method', 'N/A')}")

                        results["decision_success"] += 1
                        decision_status = "SUCCESS"
                    else:
                        print(f"  ✗ Decision: No decision returned")
                        results["decision_failed"] += 1
                        decision_status = "FAILED"

                except Exception as e:
                    print(f"  ✗ Decision failed: {str(e)[:50]}")
                    results["decision_failed"] += 1
                    decision_status = "ERROR"

            else:
                print(f"  ✗ Parser failed")
                results["parser_failed"] += 1
                parser_status = "FAILED"
                decision_status = "NOT_TESTED"

        except Exception as e:
            print(f"  ✗ Parser error: {str(e)[:50]}")
            results["parser_failed"] += 1
            parser_status = "ERROR"
            decision_status = "NOT_TESTED"

        results["controls"].append({
            "control_id": control_id,
            "name": control_name,
            "parser_status": parser_status,
            "decision_status": decision_status,
            "compliance": parsed.get('compliance_status') if 'parsed' in locals() else None,
            "confidence": decision.get('confidence') if 'decision' in locals() else None
        })

    # Print summary
    print("\n" + "=" * 80)
    print(" TEST SUMMARY")
    print("=" * 80)
    print(f"\nTotal Controls: {results['total_controls']}")
    print(f"Tested: {results['tested']}")
    print()
    print("PARSER RESULTS:")
    print(f"  ✓ Success: {results['parser_success']}/{results['tested']} ({results['parser_success']/results['tested']*100:.1f}%)")
    print(f"  ✗ Failed:  {results['parser_failed']}/{results['tested']} ({results['parser_failed']/results['tested']*100:.1f}%)")
    print()
    print("DECISION ENGINE RESULTS:")
    if results['parser_success'] > 0:
        print(f"  ✓ Success: {results['decision_success']}/{results['parser_success']} ({results['decision_success']/results['parser_success']*100:.1f}%)")
        print(f"  ✗ Failed:  {results['decision_failed']}/{results['parser_success']} ({results['decision_failed']/results['parser_success']*100:.1f}%)")
    else:
        print(f"  ✓ Success: 0/0 (N/A - no parsers succeeded)")
        print(f"  ✗ Failed:  0/0 (N/A - no parsers succeeded)")
    print()

    # Overall completeness
    parser_rate = results['parser_success'] / results['tested'] * 100
    decision_rate = results['decision_success'] / results['parser_success'] * 100 if results['parser_success'] > 0 else 0
    overall_rate = results['decision_success'] / results['tested'] * 100

    print("OVERALL COMPLETENESS:")
    print(f"  Parser Implementation:  {parser_rate:.1f}%")
    print(f"  Decision Logic:         {decision_rate:.1f}%")
    print(f"  End-to-End Functional:  {overall_rate:.1f}%")
    print()

    # Save results
    output_file = Path('test_results_47_controls.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"Results saved to: {output_file}")
    print()

    # Validation status
    if overall_rate >= 95:
        print("✅ VALIDATION PASSED - All 47 controls fully functional!")
    elif overall_rate >= 80:
        print("⚠️  VALIDATION PARTIAL - Most controls working, some fixes needed")
    else:
        print("❌ VALIDATION FAILED - Significant issues found")

    return results


if __name__ == "__main__":
    results = main()
