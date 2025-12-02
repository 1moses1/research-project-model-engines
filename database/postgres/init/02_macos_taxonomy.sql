-- Rwanda NCSA Compliance Auditor - macOS Audit Taxonomy
-- Real commands mapped to NCSA/NIST controls

-- ============================================================================
-- macOS AUDIT COMMANDS TAXONOMY
-- ============================================================================

-- Access Control Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('macos', 'login_history', ARRAY['last', '-10'], 'RWNCSA-AC-001', 'Account Management', 'Access Control',
 'Check login history for unauthorized access attempts',
 '{"look_for": ["reboot", "shutdown", "still logged in"], "warning_patterns": ["root"]}',
 '{"compliant_if": "login_records_exist", "min_entries": 1}'
),

('macos', 'current_users', ARRAY['who'], 'RWNCSA-AC-010', 'Concurrent Session Control', 'Access Control',
 'Monitor active user sessions for unauthorized concurrent access',
 '{"look_for": ["console", "ttys"], "count_sessions": true}',
 '{"compliant_if": "sessions_monitored", "max_concurrent": 5}'
),

('macos', 'user_info', ARRAY['id'], 'RWNCSA-AC-002', 'Access Enforcement', 'Access Control',
 'Verify user privileges and group memberships',
 '{"look_for": ["uid", "gid", "groups"], "warning_patterns": ["wheel", "admin"]}',
 '{"compliant_if": "user_identified", "check_admin": true}'
),

('macos', 'sudo_config', ARRAY['cat', '/etc/sudoers'], 'RWNCSA-AC-006', 'Least Privilege', 'Access Control',
 'Review sudo configuration for privilege escalation controls',
 '{"look_for": ["NOPASSWD", "ALL=(ALL)"], "warning_patterns": ["NOPASSWD"]}',
 '{"compliant_if": "sudo_configured", "no_nopasswd": true}'
),

('macos', 'user_accounts', ARRAY['dscl', '.', '-list', '/Users'], 'RWNCSA-AC-002', 'Access Enforcement', 'Access Control',
 'List all user accounts on the system',
 '{"look_for": ["_"], "count_users": true}',
 '{"compliant_if": "accounts_listed"}'
);

-- Audit and Accountability Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('macos', 'audit_config', ARRAY['sudo', 'cat', '/etc/security/audit_control'], 'RWNCSA-AU-001', 'Audit Policy', 'Audit and Accountability',
 'Check audit configuration and logging policies',
 '{"look_for": ["dir:", "flags:", "minfree:"], "required": ["flags"]}',
 '{"compliant_if": "audit_enabled"}'
),

('macos', 'disk_usage', ARRAY['df', '-h'], 'RWNCSA-AU-004', 'Audit Storage Capacity', 'Audit and Accountability',
 'Verify sufficient storage for audit logs',
 '{"look_for": ["Filesystem", "Size", "Used", "Avail"], "check_percent": true}',
 '{"compliant_if": "storage_available", "min_free_percent": 10}'
),

('macos', 'system_logs', ARRAY['log', 'show', '--predicate', 'eventType == logEvent', '--last', '1h', '--style', 'compact'], 'RWNCSA-AU-002', 'Audit Events', 'Audit and Accountability',
 'Review recent system log events',
 '{"look_for": ["timestamp", "process"], "count_events": true}',
 '{"compliant_if": "logs_available"}'
),

('macos', 'asl_logs', ARRAY['ls', '-la', '/var/log/asl/'], 'RWNCSA-AU-003', 'Audit Log Content', 'Audit and Accountability',
 'Check Apple System Log directory',
 '{"look_for": [".asl"], "check_recent": true}',
 '{"compliant_if": "asl_logs_exist"}'
);

-- System and Information Integrity Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('macos', 'process_list', ARRAY['ps', 'aux'], 'RWNCSA-SI-003', 'Malicious Code Protection', 'System and Information Integrity',
 'Check for security software and suspicious processes',
 '{"look_for": ["MRT", "XProtect", "Malwarebytes", "ClamAV", "Defender"], "warning_patterns": ["crypto", "miner"]}',
 '{"compliant_if": "security_software_running", "required_any": ["MRT", "XProtect"]}'
),

('macos', 'security_assessment', ARRAY['spctl', '--status'], 'RWNCSA-SI-007', 'Software Integrity', 'System and Information Integrity',
 'Check System Integrity Protection and Gatekeeper status',
 '{"look_for": ["assessments enabled", "assessments disabled"]}',
 '{"compliant_if": "value_equals", "expected": "assessments enabled"}'
),

('macos', 'sip_status', ARRAY['csrutil', 'status'], 'RWNCSA-SI-007', 'Software Integrity', 'System and Information Integrity',
 'Check System Integrity Protection status',
 '{"look_for": ["enabled", "disabled"]}',
 '{"compliant_if": "contains", "expected": "enabled"}'
),

('macos', 'xprotect_version', ARRAY['system_profiler', 'SPInstallHistoryDataType'], 'RWNCSA-SI-003', 'Malicious Code Protection', 'System and Information Integrity',
 'Check XProtect and malware definitions version',
 '{"look_for": ["XProtect", "MRT"]}',
 '{"compliant_if": "xprotect_updated"}'
);

-- Configuration Management Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('macos', 'system_info', ARRAY['sw_vers'], 'RWNCSA-CM-002', 'Baseline Configuration', 'Configuration Management',
 'Get macOS version and build information',
 '{"look_for": ["ProductName", "ProductVersion", "BuildVersion"]}',
 '{"compliant_if": "version_current", "min_version": "13.0"}'
),

('macos', 'running_services', ARRAY['launchctl', 'list'], 'RWNCSA-CM-007', 'Least Functionality', 'Configuration Management',
 'List running services and daemons',
 '{"look_for": ["PID", "Status"], "count_services": true}',
 '{"compliant_if": "services_documented"}'
),

('macos', 'startup_items', ARRAY['ls', '-la', '/Library/LaunchDaemons/'], 'RWNCSA-CM-007', 'Least Functionality', 'Configuration Management',
 'Check system startup items and daemons',
 '{"look_for": [".plist"], "warning_patterns": ["com.unknown"]}',
 '{"compliant_if": "startup_items_reviewed"}'
),

('macos', 'installed_apps', ARRAY['ls', '/Applications/'], 'RWNCSA-CM-008', 'Software Inventory', 'Configuration Management',
 'List installed applications',
 '{"count_apps": true}',
 '{"compliant_if": "apps_inventoried"}'
);

-- System and Communications Protection Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('macos', 'network_connections', ARRAY['netstat', '-an'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'Review active network connections',
 '{"look_for": ["ESTABLISHED", "LISTEN", "TIME_WAIT"], "count_connections": true}',
 '{"compliant_if": "connections_monitored"}'
),

('macos', 'firewall_status', ARRAY['defaults', 'read', '/Library/Preferences/com.apple.alf', 'globalstate'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'Check macOS firewall status',
 '{"look_for": ["0", "1", "2"]}',
 '{"compliant_if": "value_not_equals", "unexpected": "0"}'
),

('macos', 'firewall_apps', ARRAY['socketfilterfw', '--listapps'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'List applications with firewall exceptions',
 '{"count_exceptions": true}',
 '{"compliant_if": "exceptions_documented"}'
),

('macos', 'sharing_status', ARRAY['systemsetup', '-getremotelogin'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'Check if remote login (SSH) is enabled',
 '{"look_for": ["On", "Off"]}',
 '{"compliant_if": "documented"}'
),

('macos', 'wifi_status', ARRAY['networksetup', '-getairportpower', 'en0'], 'RWNCSA-SC-008', 'Network Disconnect', 'System and Communications Protection',
 'Check WiFi status',
 '{"look_for": ["On", "Off"]}',
 '{"compliant_if": "documented"}'
);

-- Identification and Authentication Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('macos', 'password_policy', ARRAY['pwpolicy', '-getglobalpolicy'], 'RWNCSA-IA-005', 'Authenticator Management', 'Identification and Authentication',
 'Check system password policy settings',
 '{"look_for": ["minChars", "requiresAlpha", "requiresNumeric"]}',
 '{"compliant_if": "policy_configured", "min_length": 8}'
),

('macos', 'screensaver_lock', ARRAY['defaults', 'read', 'com.apple.screensaver', 'askForPassword'], 'RWNCSA-IA-011', 'Session Lock', 'Identification and Authentication',
 'Check if screen saver requires password',
 '{"look_for": ["0", "1"]}',
 '{"compliant_if": "value_equals", "expected": "1"}'
),

('macos', 'filevault_status', ARRAY['fdesetup', 'status'], 'RWNCSA-IA-007', 'Cryptographic Authentication', 'Identification and Authentication',
 'Check FileVault disk encryption status',
 '{"look_for": ["FileVault is On", "FileVault is Off"]}',
 '{"compliant_if": "contains", "expected": "FileVault is On"}'
);

-- Media Protection Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('macos', 'disk_encryption', ARRAY['diskutil', 'apfs', 'list'], 'RWNCSA-MP-004', 'Media Storage', 'Media Protection',
 'Check disk encryption and APFS container status',
 '{"look_for": ["FileVault", "Encrypted"]}',
 '{"compliant_if": "encryption_enabled"}'
),

('macos', 'usb_devices', ARRAY['system_profiler', 'SPUSBDataType'], 'RWNCSA-MP-007', 'Media Use', 'Media Protection',
 'List connected USB devices',
 '{"count_devices": true}',
 '{"compliant_if": "devices_documented"}'
);

-- Contingency Planning Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('macos', 'time_machine', ARRAY['tmutil', 'listbackups'], 'RWNCSA-CP-009', 'System Backup', 'Contingency Planning',
 'Check Time Machine backup status',
 '{"count_backups": true}',
 '{"compliant_if": "backups_exist", "min_backups": 1}'
),

('macos', 'backup_destination', ARRAY['tmutil', 'destinationinfo'], 'RWNCSA-CP-009', 'System Backup', 'Contingency Planning',
 'Check backup destination configuration',
 '{"look_for": ["Name", "Kind", "Mount Point"]}',
 '{"compliant_if": "destination_configured"}'
);

COMMIT;
