-- Rwanda NCSA Compliance Auditor - Windows Audit Taxonomy
-- PowerShell commands mapped to NCSA/NIST controls

-- ============================================================================
-- WINDOWS AUDIT COMMANDS TAXONOMY
-- ============================================================================

-- Access Control Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('windows', 'login_history', ARRAY['powershell', '-Command', 'Get-EventLog -LogName Security -InstanceId 4624 -Newest 10 | Select TimeGenerated,Message'], 'RWNCSA-AC-001', 'Account Management', 'Access Control',
 'Check Windows login events',
 '{"look_for": ["Logon Type", "Account Name"], "count_events": true}',
 '{"compliant_if": "login_records_exist", "min_entries": 1}'
),

('windows', 'current_users', ARRAY['powershell', '-Command', 'query user'], 'RWNCSA-AC-010', 'Concurrent Session Control', 'Access Control',
 'Monitor active user sessions',
 '{"look_for": ["USERNAME", "STATE"], "count_sessions": true}',
 '{"compliant_if": "sessions_monitored", "max_concurrent": 5}'
),

('windows', 'user_info', ARRAY['powershell', '-Command', 'whoami /all'], 'RWNCSA-AC-002', 'Access Enforcement', 'Access Control',
 'Verify user privileges and group memberships',
 '{"look_for": ["SID", "Group Name", "Administrators"], "warning_patterns": ["Administrators"]}',
 '{"compliant_if": "user_identified", "check_admin": true}'
),

('windows', 'local_admins', ARRAY['powershell', '-Command', 'Get-LocalGroupMember -Group Administrators'], 'RWNCSA-AC-006', 'Least Privilege', 'Access Control',
 'List local administrator accounts',
 '{"count_admins": true, "warning_patterns": ["Guest"]}',
 '{"compliant_if": "admins_documented", "max_admins": 3}'
),

('windows', 'user_accounts', ARRAY['powershell', '-Command', 'Get-LocalUser | Select Name,Enabled,LastLogon'], 'RWNCSA-AC-002', 'Access Enforcement', 'Access Control',
 'List all local user accounts',
 '{"look_for": ["Name", "Enabled"], "count_users": true}',
 '{"compliant_if": "accounts_listed"}'
),

('windows', 'account_lockout', ARRAY['powershell', '-Command', 'net accounts'], 'RWNCSA-AC-007', 'Unsuccessful Logon Attempts', 'Access Control',
 'Check account lockout policy',
 '{"look_for": ["Lockout threshold", "Lockout duration", "Lockout observation window"]}',
 '{"compliant_if": "lockout_configured", "threshold_max": 5}'
);

-- Audit and Accountability Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('windows', 'audit_policy', ARRAY['powershell', '-Command', 'auditpol /get /category:*'], 'RWNCSA-AU-001', 'Audit Policy', 'Audit and Accountability',
 'Check Windows audit policy settings',
 '{"look_for": ["Logon/Logoff", "Object Access", "Policy Change", "Success", "Failure"]}',
 '{"compliant_if": "audit_enabled"}'
),

('windows', 'security_log_config', ARRAY['powershell', '-Command', 'Get-EventLog -List | Where {$_.Log -eq \"Security\"} | Select MaximumKilobytes,OverflowAction'], 'RWNCSA-AU-004', 'Audit Storage Capacity', 'Audit and Accountability',
 'Check security event log configuration',
 '{"look_for": ["MaximumKilobytes", "OverflowAction"]}',
 '{"compliant_if": "storage_configured", "min_size_kb": 20480}'
),

('windows', 'recent_security_events', ARRAY['powershell', '-Command', 'Get-EventLog -LogName Security -Newest 50 | Select TimeGenerated,EventID,Message'], 'RWNCSA-AU-003', 'Audit Log Content', 'Audit and Accountability',
 'Review recent security events',
 '{"count_events": true}',
 '{"compliant_if": "logs_available"}'
),

('windows', 'disk_usage', ARRAY['powershell', '-Command', 'Get-PSDrive -PSProvider FileSystem | Select Name,Used,Free'], 'RWNCSA-AU-004', 'Audit Storage Capacity', 'Audit and Accountability',
 'Check disk space for audit logs',
 '{"look_for": ["Used", "Free"], "check_percent": true}',
 '{"compliant_if": "storage_available", "min_free_percent": 10}'
);

-- System and Information Integrity Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('windows', 'defender_status', ARRAY['powershell', '-Command', 'Get-MpComputerStatus | Select AntivirusEnabled,RealTimeProtectionEnabled,AntivirusSignatureLastUpdated'], 'RWNCSA-SI-003', 'Malicious Code Protection', 'System and Information Integrity',
 'Check Windows Defender status',
 '{"look_for": ["AntivirusEnabled", "RealTimeProtectionEnabled", "True"]}',
 '{"compliant_if": "av_enabled", "realtime_required": true}'
),

('windows', 'defender_scan', ARRAY['powershell', '-Command', 'Get-MpThreatDetection | Select ThreatID,ThreatStatusID'], 'RWNCSA-SI-003', 'Malicious Code Protection', 'System and Information Integrity',
 'Check for detected threats',
 '{"count_threats": true}',
 '{"compliant_if": "no_active_threats"}'
),

('windows', 'process_list', ARRAY['powershell', '-Command', 'Get-Process | Select ProcessName,Id,CPU | Sort CPU -Descending | Select -First 20'], 'RWNCSA-SI-004', 'Information System Monitoring', 'System and Information Integrity',
 'Check running processes',
 '{"count_processes": true, "warning_patterns": ["crypto", "miner"]}',
 '{"compliant_if": "processes_monitored"}'
),

('windows', 'sfc_status', ARRAY['powershell', '-Command', 'sfc /verifyonly'], 'RWNCSA-SI-007', 'Software Integrity', 'System and Information Integrity',
 'Verify system file integrity',
 '{"look_for": ["Windows Resource Protection", "integrity violations"]}',
 '{"compliant_if": "integrity_verified"}'
),

('windows', 'windows_update', ARRAY['powershell', '-Command', 'Get-HotFix | Sort InstalledOn -Descending | Select -First 10'], 'RWNCSA-SI-002', 'Flaw Remediation', 'System and Information Integrity',
 'Check recent Windows updates',
 '{"look_for": ["HotFixID", "InstalledOn"], "count_updates": true}',
 '{"compliant_if": "updates_installed", "recent_days": 30}'
);

-- Configuration Management Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('windows', 'system_info', ARRAY['powershell', '-Command', 'Get-ComputerInfo | Select WindowsProductName,WindowsVersion,OsBuildNumber'], 'RWNCSA-CM-002', 'Baseline Configuration', 'Configuration Management',
 'Get Windows version information',
 '{"look_for": ["WindowsProductName", "WindowsVersion"]}',
 '{"compliant_if": "version_documented"}'
),

('windows', 'running_services', ARRAY['powershell', '-Command', 'Get-Service | Where Status -eq Running | Select Name,DisplayName'], 'RWNCSA-CM-007', 'Least Functionality', 'Configuration Management',
 'List running Windows services',
 '{"count_services": true}',
 '{"compliant_if": "services_documented"}'
),

('windows', 'startup_programs', ARRAY['powershell', '-Command', 'Get-CimInstance Win32_StartupCommand | Select Name,Location,Command'], 'RWNCSA-CM-007', 'Least Functionality', 'Configuration Management',
 'Check startup programs',
 '{"count_startups": true}',
 '{"compliant_if": "startups_reviewed"}'
),

('windows', 'installed_software', ARRAY['powershell', '-Command', 'Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select DisplayName,Publisher,InstallDate | Sort DisplayName'], 'RWNCSA-CM-008', 'Software Inventory', 'Configuration Management',
 'List installed software',
 '{"count_software": true}',
 '{"compliant_if": "software_inventoried"}'
);

-- System and Communications Protection Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('windows', 'firewall_status', ARRAY['powershell', '-Command', 'Get-NetFirewallProfile | Select Name,Enabled'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'Check Windows Firewall status',
 '{"look_for": ["Domain", "Private", "Public", "True"]}',
 '{"compliant_if": "firewall_enabled", "all_profiles": true}'
),

('windows', 'firewall_rules', ARRAY['powershell', '-Command', 'Get-NetFirewallRule | Where Enabled -eq True | Select DisplayName,Direction,Action | Select -First 20'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'List active firewall rules',
 '{"count_rules": true}',
 '{"compliant_if": "rules_configured"}'
),

('windows', 'network_connections', ARRAY['powershell', '-Command', 'Get-NetTCPConnection | Where State -eq Established | Select LocalPort,RemoteAddress,RemotePort'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'Review active network connections',
 '{"count_connections": true}',
 '{"compliant_if": "connections_monitored"}'
),

('windows', 'listening_ports', ARRAY['powershell', '-Command', 'Get-NetTCPConnection | Where State -eq Listen | Select LocalPort'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'List listening ports',
 '{"count_ports": true}',
 '{"compliant_if": "ports_documented"}'
),

('windows', 'smb_config', ARRAY['powershell', '-Command', 'Get-SmbServerConfiguration | Select EnableSMB1Protocol,EnableSMB2Protocol'], 'RWNCSA-SC-008', 'Transmission Confidentiality', 'System and Communications Protection',
 'Check SMB protocol configuration',
 '{"look_for": ["EnableSMB1Protocol", "False"]}',
 '{"compliant_if": "smb1_disabled"}'
),

('windows', 'rdp_config', ARRAY['powershell', '-Command', 'Get-ItemProperty \"HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server\" | Select fDenyTSConnections'], 'RWNCSA-SC-010', 'Network Disconnect', 'System and Communications Protection',
 'Check Remote Desktop configuration',
 '{"look_for": ["fDenyTSConnections"]}',
 '{"compliant_if": "rdp_configured"}'
);

-- Identification and Authentication Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('windows', 'password_policy', ARRAY['powershell', '-Command', 'net accounts'], 'RWNCSA-IA-005', 'Authenticator Management', 'Identification and Authentication',
 'Check password policy settings',
 '{"look_for": ["Minimum password length", "Maximum password age", "Password history"]}',
 '{"compliant_if": "policy_configured", "min_length": 8}'
),

('windows', 'screensaver_policy', ARRAY['powershell', '-Command', 'Get-ItemProperty \"HKCU:\\Control Panel\\Desktop\" | Select ScreenSaveActive,ScreenSaverIsSecure,ScreenSaveTimeOut'], 'RWNCSA-IA-011', 'Session Lock', 'Identification and Authentication',
 'Check screen lock settings',
 '{"look_for": ["ScreenSaverIsSecure", "1"]}',
 '{"compliant_if": "screen_lock_enabled"}'
),

('windows', 'bitlocker_status', ARRAY['powershell', '-Command', 'Get-BitLockerVolume | Select MountPoint,VolumeStatus,ProtectionStatus'], 'RWNCSA-IA-007', 'Cryptographic Authentication', 'Identification and Authentication',
 'Check BitLocker encryption status',
 '{"look_for": ["FullyEncrypted", "On"]}',
 '{"compliant_if": "encryption_enabled"}'
);

-- Media Protection Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('windows', 'usb_devices', ARRAY['powershell', '-Command', 'Get-PnpDevice | Where Class -eq USB | Select FriendlyName,Status'], 'RWNCSA-MP-007', 'Media Use', 'Media Protection',
 'List connected USB devices',
 '{"count_devices": true}',
 '{"compliant_if": "devices_documented"}'
),

('windows', 'drive_encryption', ARRAY['powershell', '-Command', 'Get-WmiObject -Class Win32_EncryptableVolume -Namespace root\\CIMV2\\Security\\MicrosoftVolumeEncryption | Select DriveLetter,ProtectionStatus'], 'RWNCSA-MP-004', 'Media Storage', 'Media Protection',
 'Check drive encryption status',
 '{"look_for": ["ProtectionStatus"]}',
 '{"compliant_if": "encryption_enabled"}'
);

-- Contingency Planning Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('windows', 'backup_status', ARRAY['powershell', '-Command', 'Get-WBSummary'], 'RWNCSA-CP-009', 'System Backup', 'Contingency Planning',
 'Check Windows Backup status',
 '{"look_for": ["LastSuccessfulBackupTime", "NextBackupTime"]}',
 '{"compliant_if": "backup_configured"}'
),

('windows', 'restore_points', ARRAY['powershell', '-Command', 'Get-ComputerRestorePoint | Select Description,CreationTime | Select -First 5'], 'RWNCSA-CP-010', 'System Recovery', 'Contingency Planning',
 'List system restore points',
 '{"count_restores": true}',
 '{"compliant_if": "restore_points_exist", "min_restores": 1}'
),

('windows', 'vss_status', ARRAY['powershell', '-Command', 'vssadmin list shadows'], 'RWNCSA-CP-009', 'System Backup', 'Contingency Planning',
 'Check Volume Shadow Copy status',
 '{"look_for": ["Shadow Copy Volume", "Creation Time"]}',
 '{"compliant_if": "vss_enabled"}'
);

COMMIT;
