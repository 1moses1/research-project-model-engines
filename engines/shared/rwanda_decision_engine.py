"""
Rwanda NCSA Control-Specific Decision Engine
Replaces generic majority vote with intelligent control requirements
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class RwandaNCSADecisionEngine:
    """
    Intelligent decision engine with control-specific logic
    Each Rwanda NCSA control has unique requirements and thresholds
    """

    def __init__(self, controls_file: Optional[str] = None):
        """Initialize with Rwanda NCSA control specifications"""
        if controls_file is None:
            controls_file = Path(__file__).parent / "rwanda_ncsa_controls.json"

        with open(controls_file, 'r') as f:
            self.controls_db = json.load(f)['controls']

    def make_decisions(self, evidence_list: List[Dict], classifications: List[Dict] = None) -> List[Dict]:
        """
        Make compliance decisions based on evidence and classifications

        Args:
            evidence_list: List of parsed evidence with compliance_status
            classifications: Optional ML classifications (XGBoost results)

        Returns:
            List of control decisions with gaps and remediation
        """
        # Group evidence by control_id
        evidence_by_control = {}
        for evidence in evidence_list:
            control_id = evidence.get('control_id')
            if control_id and control_id != 'UNKNOWN':
                if control_id not in evidence_by_control:
                    evidence_by_control[control_id] = []
                evidence_by_control[control_id].append(evidence)

        # Make decisions for each control
        decisions = []
        for control_id, control_evidence in evidence_by_control.items():
            decision = self._decide_control(control_id, control_evidence, classifications)
            decisions.append(decision)

        return decisions

    def _decide_control(self, control_id: str, evidence_list: List[Dict],
                       classifications: List[Dict] = None) -> Dict:
        """
        Make decision for a specific control using control-specific logic

        Different controls have different requirements:
        - SI-007: Requires BOTH SIP AND Gatekeeper (not majority)
        - IA-005: Requires ALL password requirements met
        - AU-004: Single threshold check (disk < 90%)
        - Others: Evidence-based assessment
        """
        control = self.controls_db.get(control_id, {})
        control_name = control.get('name', control_id)
        severity = control.get('severity', 'UNKNOWN')

        # Control-specific decision logic
        if control_id == "RWNCSA-SI-007":
            return self._decide_si_007_system_integrity(control_id, evidence_list, control)
        elif control_id == "RWNCSA-IA-005":
            return self._decide_ia_005_password_policy(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AU-004":
            return self._decide_au_004_disk_storage(control_id, evidence_list, control)
        elif control_id in ["RWNCSA-AC-001", "RWNCSA-AC-002", "RWNCSA-AC-010"]:
            return self._decide_access_control(control_id, evidence_list, control)
        elif control_id in ["RWNCSA-AU-002"]:
            return self._decide_audit_logging(control_id, evidence_list, control)
        elif control_id in ["RWNCSA-CM-002"]:
            return self._decide_configuration_mgmt(control_id, evidence_list, control)
        elif control_id == "RWNCSA-SI-003":
            return self._decide_si_003_process_monitoring(control_id, evidence_list, control)

        # Phase 1 Controls (21 new)
        elif control_id == "RWNCSA-AC-003":
            return self._decide_ac_003_admin_access(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-004":
            return self._decide_ac_004_ssh_config(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-005":
            return self._decide_ac_005_file_permissions(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-006":
            return self._decide_ac_006_sudo_config(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-007":
            return self._decide_ac_007_screen_lock(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-008":
            return self._decide_ac_008_remote_desktop(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AU-001":
            return self._decide_au_001_audit_system(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AU-003":
            return self._decide_au_003_time_sync(control_id, evidence_list, control)
        elif control_id == "RWNCSA-CO-001":
            return self._decide_co_001_software_inventory(control_id, evidence_list, control)
        elif control_id == "RWNCSA-CO-003":
            return self._decide_co_003_patch_status(control_id, evidence_list, control)
        elif control_id == "RWNCSA-CO-004":
            return self._decide_co_004_configuration_profiles(control_id, evidence_list, control)
        elif control_id == "RWNCSA-ID-002":
            return self._decide_id_002_biometric(control_id, evidence_list, control)
        elif control_id == "RWNCSA-SY-001":
            return self._decide_sy_001_firewall(control_id, evidence_list, control)
        elif control_id == "RWNCSA-SY-002":
            return self._decide_sy_002_filevault(control_id, evidence_list, control)
        elif control_id == "RWNCSA-SY-003":
            return self._decide_sy_003_bluetooth(control_id, evidence_list, control)
        elif control_id == "RWNCSA-SY-004":
            return self._decide_sy_004_network_config(control_id, evidence_list, control)
        elif control_id == "RWNCSA-SY-005":
            return self._decide_sy_005_antimalware(control_id, evidence_list, control)
        elif control_id == "RWNCSA-SY-006":
            return self._decide_sy_006_file_sharing(control_id, evidence_list, control)
        elif control_id == "RWNCSA-SY-007":
            return self._decide_sy_007_wifi(control_id, evidence_list, control)
        elif control_id == "RWNCSA-SY-008":
            return self._decide_sy_008_vpn(control_id, evidence_list, control)
        elif control_id == "RWNCSA-SY-009":
            return self._decide_sy_009_dns(control_id, evidence_list, control)

        # Week 1 Access Control (17 new)
        elif control_id == "RWNCSA-AC-009":
            return self._decide_ac_009_mfa(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-011":
            return self._decide_ac_011_lockout(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-012":
            return self._decide_ac_012_guest(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-013":
            return self._decide_ac_013_autologin(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-014":
            return self._decide_ac_014_fast_user_switching(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-015":
            return self._decide_ac_015_password_reset(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-016":
            return self._decide_ac_016_inactive_accounts(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-017":
            return self._decide_ac_017_root_status(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-018":
            return self._decide_ac_018_home_permissions(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-019":
            return self._decide_ac_019_shared_folders(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-020":
            return self._decide_ac_020_login_banner(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-021":
            return self._decide_ac_021_grace_time(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-022":
            return self._decide_ac_022_system_prefs(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-023":
            return self._decide_ac_023_keychain(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-024":
            return self._decide_ac_024_terminal(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-025":
            return self._decide_ac_025_ssh_keys(control_id, evidence_list, control)
        elif control_id == "RWNCSA-AC-026":
            return self._decide_ac_026_pf_rules(control_id, evidence_list, control)
        else:
            return self._decide_generic(control_id, evidence_list, control)

    def _decide_si_007_system_integrity(self, control_id: str, evidence_list: List[Dict],
                                       control: Dict) -> Dict:
        """
        CRITICAL CONTROL: System Integrity Protection
        Requires BOTH SIP AND Gatekeeper enabled (not majority vote)
        """
        sip_enabled = False
        gatekeeper_enabled = False
        all_gaps = []

        for evidence in evidence_list:
            actual_state = evidence.get('actual_state', {})

            # Check SIP status
            if 'sip_enabled' in actual_state:
                sip_enabled = actual_state['sip_enabled']

            # Check Gatekeeper status
            if 'gatekeeper_enabled' in actual_state:
                gatekeeper_enabled = actual_state['gatekeeper_enabled']

            # Collect gaps
            gaps = evidence.get('gaps', [])
            all_gaps.extend(gaps)

        # BOTH must be enabled for compliance
        is_compliant = sip_enabled and gatekeeper_enabled

        # Calculate score based on what's enabled
        if is_compliant:
            compliance_score = 100.0
        elif sip_enabled or gatekeeper_enabled:
            compliance_score = 50.0  # Partial credit
        else:
            compliance_score = 0.0

        return {
            "control_id": control_id,
            "control_name": control.get('name'),
            "control_family": control.get('family'),
            "final_decision": "compliant" if is_compliant else "non_compliant",
            "compliance_score": compliance_score,
            "confidence": 0.99,  # High confidence - these are binary checks
            "evidence_count": len(evidence_list),
            "decision_method": "control_specific_requirements",
            "requirements_met": {
                "sip_enabled": sip_enabled,
                "gatekeeper_enabled": gatekeeper_enabled,
                "all_required_met": is_compliant
            },
            "gaps": all_gaps,
            "severity": control.get('severity'),
            "risk_assessment": control.get('risk_assessment', {}),
            "remediation_steps": control.get('remediation', {}).get('steps', []),
            "timestamp": datetime.now().isoformat()
        }

    def _decide_ia_005_password_policy(self, control_id: str, evidence_list: List[Dict],
                                      control: Dict) -> Dict:
        """
        CRITICAL CONTROL: Password Policy
        Requires ALL password requirements met (length, complexity, age, lockout)
        """
        requirements = control.get('requirements', {})
        all_gaps = []
        policy_config = {}

        for evidence in evidence_list:
            actual_state = evidence.get('actual_state', {})
            policy_config.update(actual_state)
            all_gaps.extend(evidence.get('gaps', []))

        # Check each requirement
        requirements_met = {
            "min_length": (policy_config.get('min_length', 0) >= requirements.get('minimum_length', 12)),
            "complexity": policy_config.get('complexity_required', False),
            "max_age": (policy_config.get('max_age_days') is not None and
                       policy_config.get('max_age_days', 999) <= requirements.get('maximum_age_days', 90)),
            "lockout": policy_config.get('lockout_threshold') is not None
        }

        # ALL must be true for compliance
        is_compliant = all(requirements_met.values())

        # Calculate score based on requirements met
        compliance_score = (sum(requirements_met.values()) / len(requirements_met)) * 100

        return {
            "control_id": control_id,
            "control_name": control.get('name'),
            "control_family": control.get('family'),
            "final_decision": "compliant" if is_compliant else "non_compliant",
            "compliance_score": compliance_score,
            "confidence": 0.95,
            "evidence_count": len(evidence_list),
            "decision_method": "all_requirements_must_pass",
            "requirements_met": requirements_met,
            "policy_configuration": policy_config,
            "gaps": all_gaps,
            "severity": control.get('severity'),
            "risk_assessment": control.get('risk_assessment', {}),
            "remediation_steps": control.get('remediation', {}).get('steps', []),
            "timestamp": datetime.now().isoformat()
        }

    def _decide_au_004_disk_storage(self, control_id: str, evidence_list: List[Dict],
                                   control: Dict) -> Dict:
        """
        Audit Storage Capacity - Single threshold check
        Disk usage must be below 90%
        """
        root_usage = None
        all_gaps = []

        for evidence in evidence_list:
            actual_state = evidence.get('actual_state', {})
            root_usage = actual_state.get('root_partition_usage_percent')
            all_gaps.extend(evidence.get('gaps', []))

        # Threshold check
        threshold = 90
        is_compliant = root_usage is not None and root_usage < threshold

        # Score based on how close to threshold
        if root_usage is None:
            compliance_score = 0.0
        elif root_usage < 70:
            compliance_score = 100.0  # Excellent
        elif root_usage < 80:
            compliance_score = 90.0   # Good
        elif root_usage < 90:
            compliance_score = 70.0   # Acceptable
        elif root_usage < 95:
            compliance_score = 40.0   # Warning
        else:
            compliance_score = 0.0    # Critical

        return {
            "control_id": control_id,
            "control_name": control.get('name'),
            "control_family": control.get('family'),
            "final_decision": "compliant" if is_compliant else "non_compliant",
            "compliance_score": compliance_score,
            "confidence": 0.98,
            "evidence_count": len(evidence_list),
            "decision_method": "threshold_check",
            "actual_value": root_usage,
            "threshold": threshold,
            "within_threshold": is_compliant,
            "gaps": all_gaps,
            "severity": control.get('severity'),
            "risk_assessment": control.get('risk_assessment', {}),
            "remediation_steps": control.get('remediation', {}).get('steps', []),
            "timestamp": datetime.now().isoformat()
        }

    def _decide_access_control(self, control_id: str, evidence_list: List[Dict],
                               control: Dict) -> Dict:
        """
        Access Control family - Evidence-based assessment
        AC-001: Login history must exist with timestamps
        AC-002: User accounts must be inventoried
        AC-010: Active sessions must be monitored
        """
        all_gaps = []
        compliance_statuses = []

        for evidence in evidence_list:
            status = evidence.get('compliance_status', 'UNKNOWN')
            compliance_statuses.append(status)
            all_gaps.extend(evidence.get('gaps', []))

        # Majority vote for Access Control
        compliant_count = compliance_statuses.count('COMPLIANT')
        total_count = len(compliance_statuses)

        is_compliant = compliant_count > (total_count / 2)
        compliance_score = (compliant_count / total_count * 100) if total_count > 0 else 0.0

        return {
            "control_id": control_id,
            "control_name": control.get('name'),
            "control_family": control.get('family'),
            "final_decision": "compliant" if is_compliant else "non_compliant",
            "compliance_score": compliance_score,
            "confidence": 0.85,
            "evidence_count": len(evidence_list),
            "decision_method": "majority_vote",
            "compliant_evidence": compliant_count,
            "total_evidence": total_count,
            "gaps": all_gaps,
            "severity": control.get('severity'),
            "risk_assessment": control.get('risk_assessment', {}),
            "remediation_steps": control.get('remediation', {}).get('steps', []),
            "timestamp": datetime.now().isoformat()
        }

    def _decide_audit_logging(self, control_id: str, evidence_list: List[Dict],
                             control: Dict) -> Dict:
        """
        Audit & Accountability - Logging must be operational
        AU-002: System logs must exist with timestamps
        """
        all_gaps = []
        log_entries_found = 0

        for evidence in evidence_list:
            actual_state = evidence.get('actual_state', {})
            log_entries_found += actual_state.get('log_entries_found', 0)
            all_gaps.extend(evidence.get('gaps', []))

        # Logging is compliant if log entries exist
        is_compliant = log_entries_found > 0

        # Score based on log volume (more logs = better)
        if log_entries_found == 0:
            compliance_score = 0.0
        elif log_entries_found < 10:
            compliance_score = 60.0  # Minimal logging
        elif log_entries_found < 50:
            compliance_score = 85.0  # Moderate logging
        else:
            compliance_score = 100.0  # Good logging

        return {
            "control_id": control_id,
            "control_name": control.get('name'),
            "control_family": control.get('family'),
            "final_decision": "compliant" if is_compliant else "non_compliant",
            "compliance_score": compliance_score,
            "confidence": 0.95,
            "evidence_count": len(evidence_list),
            "decision_method": "log_availability_check",
            "log_entries_found": log_entries_found,
            "gaps": all_gaps,
            "severity": control.get('severity'),
            "risk_assessment": control.get('risk_assessment', {}),
            "remediation_steps": control.get('remediation', {}).get('steps', []),
            "timestamp": datetime.now().isoformat()
        }

    def _decide_configuration_mgmt(self, control_id: str, evidence_list: List[Dict],
                                   control: Dict) -> Dict:
        """
        Configuration Management - System baseline must be documented
        CM-002: Version and hardware info must be available
        """
        all_gaps = []
        system_info_available = False

        for evidence in evidence_list:
            actual_state = evidence.get('actual_state', {})
            if 'os_version' in actual_state or 'model' in actual_state:
                system_info_available = True
            all_gaps.extend(evidence.get('gaps', []))

        is_compliant = system_info_available
        compliance_score = 100.0 if is_compliant else 0.0

        return {
            "control_id": control_id,
            "control_name": control.get('name'),
            "control_family": control.get('family'),
            "final_decision": "compliant" if is_compliant else "non_compliant",
            "compliance_score": compliance_score,
            "confidence": 0.90,
            "evidence_count": len(evidence_list),
            "decision_method": "information_availability_check",
            "gaps": all_gaps,
            "severity": control.get('severity'),
            "risk_assessment": control.get('risk_assessment', {}),
            "remediation_steps": control.get('remediation', {}).get('steps', []),
            "timestamp": datetime.now().isoformat()
        }

    def _decide_si_003_process_monitoring(self, control_id: str, evidence_list: List[Dict],
                                         control: Dict) -> Dict:
        """
        System Integrity - Process monitoring
        SI-003: Process list must be accessible
        """
        all_gaps = []
        total_processes = 0

        for evidence in evidence_list:
            actual_state = evidence.get('actual_state', {})
            total_processes = max(total_processes, actual_state.get('total_processes', 0))
            all_gaps.extend(evidence.get('gaps', []))

        is_compliant = total_processes > 0
        compliance_score = 100.0 if is_compliant else 0.0

        return {
            "control_id": control_id,
            "control_name": control.get('name'),
            "control_family": control.get('family'),
            "final_decision": "compliant" if is_compliant else "non_compliant",
            "compliance_score": compliance_score,
            "confidence": 0.85,
            "evidence_count": len(evidence_list),
            "decision_method": "process_enumeration_check",
            "total_processes": total_processes,
            "gaps": all_gaps,
            "severity": control.get('severity'),
            "risk_assessment": control.get('risk_assessment', {}),
            "remediation_steps": control.get('remediation', {}).get('steps', []),
            "timestamp": datetime.now().isoformat()
        }

    def _decide_generic(self, control_id: str, evidence_list: List[Dict],
                       control: Dict) -> Dict:
        """
        Generic decision logic for controls without specific requirements
        Uses majority vote from evidence compliance status
        """
        all_gaps = []
        compliance_statuses = []

        for evidence in evidence_list:
            status = evidence.get('compliance_status', 'UNKNOWN')
            compliance_statuses.append(status)
            all_gaps.extend(evidence.get('gaps', []))

        compliant_count = compliance_statuses.count('COMPLIANT')
        total_count = len(compliance_statuses)

        is_compliant = compliant_count > (total_count / 2) if total_count > 0 else False
        compliance_score = (compliant_count / total_count * 100) if total_count > 0 else 0.0

        return {
            "control_id": control_id,
            "control_name": control.get('name', control_id),
            "control_family": control.get('family', 'Unknown'),
            "final_decision": "compliant" if is_compliant else "non_compliant",
            "compliance_score": compliance_score,
            "confidence": 0.70,  # Lower confidence for generic logic
            "evidence_count": len(evidence_list),
            "decision_method": "generic_majority_vote",
            "compliant_evidence": compliant_count,
            "total_evidence": total_count,
            "gaps": all_gaps,
            "severity": control.get('severity', 'UNKNOWN'),
            "risk_assessment": control.get('risk_assessment', {}),
            "remediation_steps": control.get('remediation', {}).get('steps', []),
            "timestamp": datetime.now().isoformat()
        }

    def generate_executive_summary(self, decisions: List[Dict]) -> Dict:
        """
        Generate executive summary from decisions
        Includes overall score, critical gaps, risk prioritization
        """
        total_controls = len(decisions)
        compliant_controls = sum(1 for d in decisions if d['final_decision'] == 'compliant')
        non_compliant_controls = total_controls - compliant_controls

        # Calculate overall score
        if total_controls > 0:
            overall_score = sum(d['compliance_score'] for d in decisions) / total_controls
        else:
            overall_score = 0.0

        # Identify critical gaps
        critical_gaps = []
        high_gaps = []
        for decision in decisions:
            if decision['final_decision'] == 'non_compliant':
                severity = decision.get('severity', 'UNKNOWN')
                if severity == 'CRITICAL':
                    critical_gaps.append({
                        "control_id": decision['control_id'],
                        "control_name": decision['control_name'],
                        "gaps": decision.get('gaps', []),
                        "remediation": decision.get('remediation_steps', [])
                    })
                elif severity == 'HIGH':
                    high_gaps.append({
                        "control_id": decision['control_id'],
                        "control_name": decision['control_name'],
                        "gaps": decision.get('gaps', []),
                        "remediation": decision.get('remediation_steps', [])
                    })

        return {
            "overall_score": overall_score,
            "total_controls": total_controls,
            "compliant_controls": compliant_controls,
            "non_compliant_controls": non_compliant_controls,
            "compliance_rate": (compliant_controls / total_controls * 100) if total_controls > 0 else 0,
            "critical_gaps": critical_gaps,
            "high_priority_gaps": high_gaps,
            "risk_summary": {
                "critical_risks": len(critical_gaps),
                "high_risks": len(high_gaps),
                "total_gaps": sum(len(d.get('gaps', [])) for d in decisions)
            },
            "generated_at": datetime.now().isoformat()
        }


    # ===================================================================
    # PHASE 1 DECISION FUNCTIONS (21 controls)
    # ===================================================================

    def _decide_binary_control(self, control_id: str, evidence_list: List[Dict], control: Dict, 
                                feature_key: str, expected_value: bool = True) -> Dict:
        """Generic binary decision (enabled/disabled)"""
        actual_value = False
        for ev in evidence_list:
            if feature_key in ev.get('actual_state', {}):
                actual_value = ev['actual_state'][feature_key]
                break
        
        is_compliant = (actual_value == expected_value)
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {
            "control_id": control_id,
            "control_name": control['name'],
            "final_decision": "compliant" if is_compliant else "non_compliant",
            "compliance_score": 100.0 if is_compliant else 0.0,
            "confidence": 0.98,
            "decision_method": "binary_check",
            "gaps": gaps,
            "severity": control['severity'],
            "remediation_priority": "CRITICAL" if control['severity'] == "CRITICAL" else "HIGH" if not is_compliant else "LOW"
        }

    def _decide_ac_003_admin_access(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Admin access control - requires 1-3 admins"""
        admin_count = 0
        for ev in evidence_list:
            admin_count = ev.get('actual_state', {}).get('count', 0)
        
        is_compliant = 1 <= admin_count <= 3
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 50.0, "confidence": 0.95, "decision_method": "threshold_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "HIGH" if not is_compliant else "LOW"}

    def _decide_ac_004_ssh_config(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """SSH config - requires root disabled AND password auth disabled"""
        root_disabled = False
        password_disabled = False
        for ev in evidence_list:
            state = ev.get('actual_state', {})
            root_disabled = state.get('permit_root_login', False)
            password_disabled = state.get('password_auth_disabled', False)
        
        is_compliant = root_disabled and password_disabled
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 25.0, "confidence": 0.99, "decision_method": "config_requirements", "gaps": gaps, "severity": "CRITICAL", "remediation_priority": "CRITICAL" if not is_compliant else "LOW"}

    def _decide_ac_005_file_permissions(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """File permissions - no world-writable files"""
        return self._decide_binary_control(control_id, evidence_list, control, 'insecure_count', False)

    def _decide_ac_006_sudo_config(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Sudo config - NOPASSWD should not be present"""
        return self._decide_binary_control(control_id, evidence_list, control, 'nopasswd_present', False)

    def _decide_ac_007_screen_lock(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Screen lock - timeout <= 300 seconds"""
        timeout = None
        for ev in evidence_list:
            timeout = ev.get('actual_state', {}).get('timeout_seconds')
        
        is_compliant = timeout is not None and timeout <= 300
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 50.0, "confidence": 0.90, "decision_method": "threshold_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "MEDIUM" if not is_compliant else "LOW"}

    def _decide_ac_008_remote_desktop(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Remote desktop - should be disabled"""
        return self._decide_binary_control(control_id, evidence_list, control, 'screensharing_enabled', False)

    def _decide_au_001_audit_system(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Audit system - must be running"""
        return self._decide_binary_control(control_id, evidence_list, control, 'audit_running', True)

    def _decide_au_003_time_sync(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Time sync - must be enabled"""
        return self._decide_binary_control(control_id, evidence_list, control, 'ntp_enabled', True)

    def _decide_co_001_software_inventory(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Software inventory - must be available"""
        app_count = 0
        for ev in evidence_list:
            app_count = ev.get('actual_state', {}).get('app_count', 0)
        
        is_compliant = app_count > 0
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 0.0, "confidence": 0.85, "decision_method": "inventory_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "MEDIUM" if not is_compliant else "LOW"}

    def _decide_co_003_patch_status(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Patch status - no critical patches pending"""
        critical_pending = False
        for ev in evidence_list:
            critical_pending = ev.get('actual_state', {}).get('critical_pending', False)
        
        is_compliant = not critical_pending
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 0.0, "confidence": 0.99, "decision_method": "critical_check", "gaps": gaps, "severity": "CRITICAL", "remediation_priority": "CRITICAL" if not is_compliant else "LOW"}

    def _decide_co_004_configuration_profiles(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Config profiles - should be documented"""
        return self._standard_decision(control_id, evidence_list, control, 0.85)

    def _decide_id_002_biometric(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Biometric - should be enabled if available"""
        return self._standard_decision(control_id, evidence_list, control, 0.90)

    def _decide_sy_001_firewall(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Firewall - MUST be enabled (CRITICAL)"""
        return self._decide_binary_control(control_id, evidence_list, control, 'firewall_enabled', True)

    def _decide_sy_002_filevault(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """FileVault - MUST be enabled (CRITICAL)"""
        return self._decide_binary_control(control_id, evidence_list, control, 'filevault_enabled', True)

    def _decide_sy_003_bluetooth(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Bluetooth - should be disabled when not needed"""
        return self._decide_binary_control(control_id, evidence_list, control, 'bluetooth_enabled', False)

    def _decide_sy_004_network_config(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Network config - should be present"""
        return self._standard_decision(control_id, evidence_list, control, 0.90)

    def _decide_sy_005_antimalware(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Anti-malware - XProtect should be present"""
        return self._decide_binary_control(control_id, evidence_list, control, 'xprotect_enabled', True)

    def _decide_sy_006_file_sharing(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """File sharing - should be disabled unless required"""
        return self._decide_binary_control(control_id, evidence_list, control, 'sharing_enabled', False)

    def _decide_sy_007_wifi(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Wi-Fi - no open/WEP networks"""
        open_count = 0
        for ev in evidence_list:
            open_count = ev.get('actual_state', {}).get('open_networks', 0)
        
        is_compliant = open_count == 0
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 0.0, "confidence": 0.95, "decision_method": "security_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "HIGH" if not is_compliant else "LOW"}

    def _decide_sy_008_vpn(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """VPN - should be configured"""
        return self._decide_binary_control(control_id, evidence_list, control, 'vpn_configured', True)

    def _decide_sy_009_dns(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """DNS - trusted servers configured"""
        dns_count = 0
        for ev in evidence_list:
            dns_count = ev.get('actual_state', {}).get('count', 0)
        
        is_compliant = dns_count > 0
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 0.0, "confidence": 0.88, "decision_method": "config_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "MEDIUM" if not is_compliant else "LOW"}

    # ===================================================================
    # WEEK 1 ACCESS CONTROL DECISION FUNCTIONS (17 controls)
    # ===================================================================

    def _decide_ac_009_mfa(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """MFA - certificates should be configured"""
        cert_count = 0
        for ev in evidence_list:
            cert_count = ev.get('actual_state', {}).get('certificates', 0)
        
        is_compliant = cert_count > 0
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 0.0, "confidence": 0.90, "decision_method": "mfa_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "HIGH" if not is_compliant else "LOW"}

    def _decide_ac_011_lockout(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Account lockout - max attempts <= 5"""
        max_attempts = None
        for ev in evidence_list:
            max_attempts = ev.get('actual_state', {}).get('max_attempts')
        
        is_compliant = max_attempts is not None and max_attempts <= 5
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 0.0, "confidence": 0.95, "decision_method": "threshold_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "MEDIUM" if not is_compliant else "LOW"}

    def _decide_ac_012_guest(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Guest account - must be disabled"""
        return self._decide_binary_control(control_id, evidence_list, control, 'guest_disabled', True)

    def _decide_ac_013_autologin(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Auto-login - must be disabled"""
        return self._decide_binary_control(control_id, evidence_list, control, 'auto_login_disabled', True)

    def _decide_ac_014_fast_user_switching(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Fast user switching - configuration documented"""
        return self._standard_decision(control_id, evidence_list, control, 0.80)

    def _decide_ac_015_password_reset(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Password reset policy - should be configured"""
        return self._standard_decision(control_id, evidence_list, control, 0.85)

    def _decide_ac_016_inactive_accounts(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Inactive accounts - should be tracked"""
        return self._standard_decision(control_id, evidence_list, control, 0.85)

    def _decide_ac_017_root_status(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Root account - MUST be disabled (CRITICAL)"""
        return self._decide_binary_control(control_id, evidence_list, control, 'root_disabled', True)

    def _decide_ac_018_home_permissions(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Home directory permissions - no insecure directories"""
        insecure_count = 0
        for ev in evidence_list:
            insecure_count = ev.get('actual_state', {}).get('insecure_count', 0)
        
        is_compliant = insecure_count == 0
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 50.0, "confidence": 0.95, "decision_method": "permission_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "HIGH" if not is_compliant else "LOW"}

    def _decide_ac_019_shared_folders(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Shared folders - should be documented"""
        return self._standard_decision(control_id, evidence_list, control, 0.85)

    def _decide_ac_020_login_banner(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Login banner - should have warning"""
        banner_exists = False
        has_warning = False
        for ev in evidence_list:
            state = ev.get('actual_state', {})
            banner_exists = state.get('banner_exists', False)
            has_warning = state.get('has_warning', False)
        
        is_compliant = banner_exists and has_warning
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 0.0, "confidence": 0.85, "decision_method": "content_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "LOW" if not is_compliant else "LOW"}

    def _decide_ac_021_grace_time(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Grace time - must be 0"""
        grace_time = None
        for ev in evidence_list:
            grace_time = ev.get('actual_state', {}).get('grace_time')
        
        is_compliant = grace_time == 0
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 50.0, "confidence": 0.92, "decision_method": "threshold_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "MEDIUM" if not is_compliant else "LOW"}

    def _decide_ac_022_system_prefs(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """System preferences - must require admin"""
        return self._decide_binary_control(control_id, evidence_list, control, 'requires_admin', True)

    def _decide_ac_023_keychain(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Keychain - should be configured"""
        return self._decide_binary_control(control_id, evidence_list, control, 'has_keychains', True)

    def _decide_ac_024_terminal(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Terminal access - should be controlled"""
        return self._standard_decision(control_id, evidence_list, control, 0.85)

    def _decide_ac_025_ssh_keys(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """SSH keys - must have secure permissions"""
        has_keys = False
        insecure_count = 0
        for ev in evidence_list:
            state = ev.get('actual_state', {})
            has_keys = state.get('has_keys', False)
            insecure_count = state.get('insecure_count', 0)
        
        is_compliant = has_keys and insecure_count == 0
        gaps = []
        for ev in evidence_list:
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": 100.0 if is_compliant else 50.0, "confidence": 0.95, "decision_method": "permission_check", "gaps": gaps, "severity": control['severity'], "remediation_priority": "HIGH" if not is_compliant else "LOW"}

    def _decide_ac_026_pf_rules(self, control_id: str, evidence_list: List[Dict], control: Dict) -> Dict:
        """Packet filter rules - should be configured"""
        return self._decide_binary_control(control_id, evidence_list, control, 'has_rules', True)

    def _standard_decision(self, control_id: str, evidence_list: List[Dict], control: Dict, confidence: float) -> Dict:
        """Standard decision based on evidence compliance_status"""
        is_compliant = False
        compliance_score = 0.0
        gaps = []
        
        for ev in evidence_list:
            if ev.get('compliance_status') == 'COMPLIANT':
                is_compliant = True
            compliance_score = max(compliance_score, ev.get('compliance_score', 0.0))
            gaps.extend(ev.get('gaps', []))
        
        return {"control_id": control_id, "control_name": control['name'], "final_decision": "compliant" if is_compliant else "non_compliant", "compliance_score": compliance_score, "confidence": confidence, "decision_method": "evidence_based", "gaps": gaps, "severity": control['severity'], "remediation_priority": "HIGH" if not is_compliant and control['severity'] in ["CRITICAL", "HIGH"] else "MEDIUM" if not is_compliant else "LOW"}

