"""
Audit Command Executor for Rwanda NCSA Compliance.

This service executes macOS audit commands for system-auditable controls
and parses the results using the evidence_parsers module.

Architecture:
- Loads audit commands from rwanda_ncsa_controls_expanded.json
- Executes commands safely with timeout
- Parses output using registered parsers
- Returns structured compliance evidence

Safety:
- Commands are pre-defined (not user-supplied)
- Timeout protection (10 second default)
- Error handling for command failures
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

# Handle imports for both module and CLI usage
try:
    from .evidence_parsers import (
        parse_audit_output,
        evaluate_compliance,
        PARSER_REGISTRY
    )
except ImportError:
    from evidence_parsers import (
        parse_audit_output,
        evaluate_compliance,
        PARSER_REGISTRY
    )


# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
CONTROLS_FILE = PROJECT_ROOT / "engines/shared/rwanda_ncsa_controls_expanded.json"

DEFAULT_TIMEOUT = 10  # seconds


# =============================================================================
# Audit Command Executor
# =============================================================================

class AuditExecutor:
    """
    Executes audit commands for NCSA compliance controls.
    """

    def __init__(self, controls_file: Path = CONTROLS_FILE):
        """Initialize with controls database."""
        self.controls = {}
        self.load_controls(controls_file)

    def load_controls(self, controls_file: Path) -> None:
        """Load controls from JSON file."""
        try:
            with open(controls_file, 'r') as f:
                data = json.load(f)
                self.controls = data.get('controls', {})
                print(f"Loaded {len(self.controls)} controls from {controls_file.name}")
        except FileNotFoundError:
            print(f"Controls file not found: {controls_file}")
            self.controls = {}
        except json.JSONDecodeError as e:
            print(f"Error parsing controls file: {e}")
            self.controls = {}

    def get_control(self, control_id: str) -> Optional[Dict[str, Any]]:
        """Get control definition by ID."""
        return self.controls.get(control_id)

    def get_audit_command(self, control_id: str) -> Optional[str]:
        """Get the audit command for a control."""
        control = self.get_control(control_id)
        if not control:
            return None

        macos_impl = control.get('macos_implementation', {})
        return macos_impl.get('audit_command')

    def get_parser_name(self, control_id: str) -> str:
        """Get the parser name for a control."""
        control = self.get_control(control_id)
        if not control:
            return 'parse_generic_output'

        macos_impl = control.get('macos_implementation', {})
        return macos_impl.get('parser_logic', 'parse_generic_output')

    def execute_command(
        self,
        command: str,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Execute an audit command safely.

        Args:
            command: Shell command to execute
            timeout: Maximum execution time in seconds

        Returns:
            Dict with output, success status, and timing
        """
        start_time = datetime.now()

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

            return {
                "success": result.returncode == 0,
                "output": result.stdout if result.stdout else result.stderr,
                "return_code": result.returncode,
                "elapsed_ms": elapsed_ms,
                "command": command
            }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": f"Command timed out after {timeout} seconds",
                "return_code": -1,
                "elapsed_ms": timeout * 1000,
                "command": command
            }
        except Exception as e:
            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
            return {
                "success": False,
                "output": f"Error executing command: {str(e)}",
                "return_code": -1,
                "elapsed_ms": elapsed_ms,
                "command": command
            }

    def audit_control(
        self,
        control_id: str,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Execute audit for a specific control.

        Args:
            control_id: NCSA control ID (e.g., 'RWNCSA-AC-37')
            timeout: Command timeout in seconds

        Returns:
            Complete audit result with parsed evidence and compliance status
        """
        control = self.get_control(control_id)
        if not control:
            return {
                "control_id": control_id,
                "success": False,
                "error": f"Control {control_id} not found",
                "compliance_status": "unknown"
            }

        # Get audit command
        command = self.get_audit_command(control_id)
        if not command:
            return {
                "control_id": control_id,
                "success": False,
                "error": "No audit command defined for this control",
                "compliance_status": "unknown",
                "audit_type": control.get('audit_type', 'unknown')
            }

        # Execute command
        exec_result = self.execute_command(command, timeout)

        # Parse output
        parser_name = self.get_parser_name(control_id)
        parsed_result = parse_audit_output(exec_result["output"], parser_name)

        # Evaluate compliance
        compliance_eval = evaluate_compliance(parsed_result)

        return {
            "control_id": control_id,
            "control_name": control.get('name', ''),
            "control_family": control.get('family', ''),
            "severity": control.get('severity', 'MEDIUM'),
            "success": exec_result["success"],
            "command_executed": command,
            "command_output": exec_result["output"][:500],  # Truncate for storage
            "parser_used": parser_name,
            "parsed_result": parsed_result,
            "compliance_status": compliance_eval["compliance_status"],
            "confidence": compliance_eval["confidence"],
            "compliance_indicators": compliance_eval["compliance_indicators"],
            "non_compliance_indicators": compliance_eval["non_compliance_indicators"],
            "reasoning": compliance_eval["reasoning"],
            "elapsed_ms": exec_result["elapsed_ms"],
            "timestamp": datetime.now().isoformat()
        }

    def audit_controls_batch(
        self,
        control_ids: List[str],
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Execute audits for multiple controls.

        Args:
            control_ids: List of control IDs to audit
            timeout: Command timeout in seconds

        Returns:
            Batch audit results with summary
        """
        results = []
        compliant_count = 0
        non_compliant_count = 0
        partial_count = 0
        error_count = 0

        total_start = datetime.now()

        for control_id in control_ids:
            result = self.audit_control(control_id, timeout)
            results.append(result)

            status = result.get("compliance_status", "unknown")
            if status == "compliant":
                compliant_count += 1
            elif status == "non_compliant":
                non_compliant_count += 1
            elif status == "partial":
                partial_count += 1
            else:
                error_count += 1

        total_elapsed = (datetime.now() - total_start).total_seconds() * 1000

        return {
            "total_controls": len(control_ids),
            "compliant": compliant_count,
            "non_compliant": non_compliant_count,
            "partial": partial_count,
            "errors": error_count,
            "compliance_rate": (compliant_count / len(control_ids) * 100) if control_ids else 0,
            "total_elapsed_ms": total_elapsed,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }

    def audit_family(
        self,
        family: str,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """
        Execute audits for all controls in a family.

        Args:
            family: Control family name (e.g., 'Access Control')
            timeout: Command timeout in seconds

        Returns:
            Family audit results
        """
        # Find all controls in this family
        control_ids = [
            ctrl_id for ctrl_id, ctrl in self.controls.items()
            if ctrl.get('family') == family
        ]

        if not control_ids:
            return {
                "family": family,
                "error": f"No controls found for family: {family}",
                "total_controls": 0
            }

        results = self.audit_controls_batch(control_ids, timeout)
        results["family"] = family

        return results

    def get_auditable_controls(self) -> List[str]:
        """Get list of all controls that have audit commands."""
        return [
            ctrl_id for ctrl_id, ctrl in self.controls.items()
            if ctrl.get('macos_implementation', {}).get('audit_command')
        ]

    def get_control_families(self) -> List[str]:
        """Get list of unique control families."""
        families = set()
        for ctrl in self.controls.values():
            family = ctrl.get('family')
            if family:
                families.add(family)
        return sorted(families)


# =============================================================================
# Async Executor for Integration with FastAPI
# =============================================================================

class AsyncAuditExecutor(AuditExecutor):
    """
    Async version of AuditExecutor for FastAPI integration.
    """

    async def audit_control_async(
        self,
        control_id: str,
        timeout: int = DEFAULT_TIMEOUT
    ) -> Dict[str, Any]:
        """Async wrapper for audit_control."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.audit_control(control_id, timeout)
        )

    async def audit_controls_batch_async(
        self,
        control_ids: List[str],
        timeout: int = DEFAULT_TIMEOUT,
        max_concurrent: int = 5
    ) -> Dict[str, Any]:
        """
        Async batch audit with concurrency control.

        Args:
            control_ids: List of control IDs
            timeout: Command timeout
            max_concurrent: Max concurrent audits

        Returns:
            Batch results
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def audit_with_semaphore(ctrl_id):
            async with semaphore:
                return await self.audit_control_async(ctrl_id, timeout)

        results = await asyncio.gather(
            *[audit_with_semaphore(ctrl_id) for ctrl_id in control_ids]
        )

        # Calculate summary
        compliant = sum(1 for r in results if r.get("compliance_status") == "compliant")
        non_compliant = sum(1 for r in results if r.get("compliance_status") == "non_compliant")
        partial = sum(1 for r in results if r.get("compliance_status") == "partial")

        return {
            "total_controls": len(control_ids),
            "compliant": compliant,
            "non_compliant": non_compliant,
            "partial": partial,
            "errors": len(control_ids) - compliant - non_compliant - partial,
            "compliance_rate": (compliant / len(control_ids) * 100) if control_ids else 0,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }


# =============================================================================
# Singleton Instance
# =============================================================================

_executor_instance = None


def get_audit_executor() -> AuditExecutor:
    """Get singleton AuditExecutor instance."""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = AuditExecutor()
    return _executor_instance


def get_async_audit_executor() -> AsyncAuditExecutor:
    """Get singleton AsyncAuditExecutor instance."""
    global _executor_instance
    if _executor_instance is None or not isinstance(_executor_instance, AsyncAuditExecutor):
        _executor_instance = AsyncAuditExecutor()
    return _executor_instance


# =============================================================================
# CLI Testing
# =============================================================================

if __name__ == "__main__":
    import sys

    executor = AuditExecutor()

    print("=" * 60)
    print("Rwanda NCSA Audit Command Executor")
    print("=" * 60)

    # Show available controls
    auditable = executor.get_auditable_controls()
    families = executor.get_control_families()

    print(f"\nTotal controls loaded: {len(executor.controls)}")
    print(f"Auditable controls: {len(auditable)}")
    print(f"Control families: {len(families)}")
    print("\nFamilies:", ", ".join(families))

    # Test a specific control if provided
    if len(sys.argv) > 1:
        control_id = sys.argv[1]
        print(f"\n{'='*60}")
        print(f"Auditing: {control_id}")
        print("=" * 60)

        result = executor.audit_control(control_id)
        print(f"\nControl: {result.get('control_name', 'Unknown')}")
        print(f"Family: {result.get('control_family', 'Unknown')}")
        print(f"Command: {result.get('command_executed', 'N/A')}")
        print(f"Parser: {result.get('parser_used', 'N/A')}")
        print(f"\nCompliance Status: {result.get('compliance_status', 'unknown').upper()}")
        print(f"Confidence: {result.get('confidence', 0):.2%}")
        print(f"Elapsed: {result.get('elapsed_ms', 0):.1f}ms")

        print("\nCompliance Indicators:")
        for ind in result.get('compliance_indicators', []):
            print(f"  + {ind}")

        print("\nNon-Compliance Indicators:")
        for ind in result.get('non_compliance_indicators', []):
            print(f"  - {ind}")
    else:
        print("\nUsage: python audit_executor.py <control_id>")
        print("Example: python audit_executor.py RWNCSA-AC-1")

        # Show sample controls
        print("\nSample auditable controls:")
        for ctrl_id in auditable[:5]:
            ctrl = executor.get_control(ctrl_id)
            print(f"  {ctrl_id}: {ctrl.get('name', 'Unknown')[:40]}")
