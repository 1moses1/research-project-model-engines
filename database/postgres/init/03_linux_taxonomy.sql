-- Rwanda NCSA Compliance Auditor - Linux Audit Taxonomy
-- Real commands mapped to NCSA/NIST controls

-- ============================================================================
-- LINUX AUDIT COMMANDS TAXONOMY
-- ============================================================================

-- Access Control Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('linux', 'login_history', ARRAY['last', '-10'], 'RWNCSA-AC-001', 'Account Management', 'Access Control',
 'Check login history for unauthorized access attempts',
 '{"look_for": ["reboot", "shutdown", "still logged in"], "warning_patterns": ["root"]}',
 '{"compliant_if": "login_records_exist", "min_entries": 1}'
),

('linux', 'current_users', ARRAY['who'], 'RWNCSA-AC-010', 'Concurrent Session Control', 'Access Control',
 'Monitor active user sessions for unauthorized concurrent access',
 '{"look_for": ["pts", "tty"], "count_sessions": true}',
 '{"compliant_if": "sessions_monitored", "max_concurrent": 5}'
),

('linux', 'user_info', ARRAY['id'], 'RWNCSA-AC-002', 'Access Enforcement', 'Access Control',
 'Verify user privileges and group memberships',
 '{"look_for": ["uid", "gid", "groups"], "warning_patterns": ["wheel", "sudo", "root"]}',
 '{"compliant_if": "user_identified", "check_admin": true}'
),

('linux', 'sudo_config', ARRAY['cat', '/etc/sudoers'], 'RWNCSA-AC-006', 'Least Privilege', 'Access Control',
 'Review sudo configuration for privilege escalation controls',
 '{"look_for": ["NOPASSWD", "ALL=(ALL)"], "warning_patterns": ["NOPASSWD"]}',
 '{"compliant_if": "sudo_configured", "no_nopasswd": true}'
),

('linux', 'user_accounts', ARRAY['cat', '/etc/passwd'], 'RWNCSA-AC-002', 'Access Enforcement', 'Access Control',
 'List all user accounts on the system',
 '{"look_for": ["/bin/bash", "/bin/sh", "nologin"], "count_users": true}',
 '{"compliant_if": "accounts_listed"}'
),

('linux', 'shadow_permissions', ARRAY['ls', '-la', '/etc/shadow'], 'RWNCSA-AC-003', 'Access Enforcement', 'Access Control',
 'Check shadow file permissions',
 '{"look_for": ["rw-------", "root"]}',
 '{"compliant_if": "permissions_secure"}'
),

('linux', 'pam_config', ARRAY['cat', '/etc/pam.d/common-auth'], 'RWNCSA-AC-007', 'Unsuccessful Logon Attempts', 'Access Control',
 'Check PAM authentication configuration',
 '{"look_for": ["pam_tally", "pam_faillock", "deny"]}',
 '{"compliant_if": "lockout_configured"}'
);

-- Audit and Accountability Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('linux', 'auditd_status', ARRAY['systemctl', 'status', 'auditd'], 'RWNCSA-AU-001', 'Audit Policy', 'Audit and Accountability',
 'Check audit daemon status',
 '{"look_for": ["active (running)", "inactive", "enabled"]}',
 '{"compliant_if": "contains", "expected": "active"}'
),

('linux', 'audit_rules', ARRAY['auditctl', '-l'], 'RWNCSA-AU-002', 'Audit Events', 'Audit and Accountability',
 'List active audit rules',
 '{"count_rules": true}',
 '{"compliant_if": "rules_configured", "min_rules": 5}'
),

('linux', 'disk_usage', ARRAY['df', '-h'], 'RWNCSA-AU-004', 'Audit Storage Capacity', 'Audit and Accountability',
 'Verify sufficient storage for audit logs',
 '{"look_for": ["Filesystem", "Size", "Used", "Avail"], "check_percent": true}',
 '{"compliant_if": "storage_available", "min_free_percent": 10}'
),

('linux', 'auth_log', ARRAY['tail', '-50', '/var/log/auth.log'], 'RWNCSA-AU-003', 'Audit Log Content', 'Audit and Accountability',
 'Review authentication logs',
 '{"look_for": ["sshd", "sudo", "authentication"], "count_events": true}',
 '{"compliant_if": "logs_available"}'
),

('linux', 'syslog_config', ARRAY['cat', '/etc/rsyslog.conf'], 'RWNCSA-AU-003', 'Audit Log Content', 'Audit and Accountability',
 'Check syslog configuration',
 '{"look_for": ["auth", "authpriv", "*.info"]}',
 '{"compliant_if": "syslog_configured"}'
),

('linux', 'journald_status', ARRAY['journalctl', '--disk-usage'], 'RWNCSA-AU-004', 'Audit Storage Capacity', 'Audit and Accountability',
 'Check journald disk usage',
 '{"look_for": ["Archived", "journals"]}',
 '{"compliant_if": "journald_active"}'
);

-- System and Information Integrity Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('linux', 'process_list', ARRAY['ps', 'aux'], 'RWNCSA-SI-003', 'Malicious Code Protection', 'System and Information Integrity',
 'Check for security software and suspicious processes',
 '{"look_for": ["clamav", "fail2ban", "rkhunter", "aide"], "warning_patterns": ["crypto", "miner"]}',
 '{"compliant_if": "security_software_running"}'
),

('linux', 'clamav_status', ARRAY['systemctl', 'status', 'clamav-freshclam'], 'RWNCSA-SI-003', 'Malicious Code Protection', 'System and Information Integrity',
 'Check ClamAV antivirus status',
 '{"look_for": ["active", "running"]}',
 '{"compliant_if": "contains", "expected": "active"}'
),

('linux', 'fail2ban_status', ARRAY['fail2ban-client', 'status'], 'RWNCSA-SI-004', 'Information System Monitoring', 'System and Information Integrity',
 'Check fail2ban intrusion prevention status',
 '{"look_for": ["Number of jail", "Jail list"]}',
 '{"compliant_if": "fail2ban_active"}'
),

('linux', 'rkhunter_check', ARRAY['rkhunter', '--check', '--skip-keypress'], 'RWNCSA-SI-007', 'Software Integrity', 'System and Information Integrity',
 'Run rootkit hunter scan',
 '{"look_for": ["Checking", "Warning", "OK"]}',
 '{"compliant_if": "no_rootkits"}'
),

('linux', 'aide_status', ARRAY['aide', '--check'], 'RWNCSA-SI-007', 'Software Integrity', 'System and Information Integrity',
 'Check file integrity with AIDE',
 '{"look_for": ["AIDE found differences", "AIDE found NO differences"]}',
 '{"compliant_if": "integrity_verified"}'
);

-- Configuration Management Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('linux', 'os_release', ARRAY['cat', '/etc/os-release'], 'RWNCSA-CM-002', 'Baseline Configuration', 'Configuration Management',
 'Get Linux distribution and version information',
 '{"look_for": ["NAME", "VERSION", "ID"]}',
 '{"compliant_if": "version_documented"}'
),

('linux', 'kernel_version', ARRAY['uname', '-a'], 'RWNCSA-CM-002', 'Baseline Configuration', 'Configuration Management',
 'Check kernel version',
 '{"look_for": ["Linux", "x86_64", "aarch64"]}',
 '{"compliant_if": "kernel_current"}'
),

('linux', 'running_services', ARRAY['systemctl', 'list-units', '--type=service', '--state=running'], 'RWNCSA-CM-007', 'Least Functionality', 'Configuration Management',
 'List running services',
 '{"count_services": true}',
 '{"compliant_if": "services_documented"}'
),

('linux', 'enabled_services', ARRAY['systemctl', 'list-unit-files', '--type=service', '--state=enabled'], 'RWNCSA-CM-007', 'Least Functionality', 'Configuration Management',
 'List enabled services at boot',
 '{"count_services": true}',
 '{"compliant_if": "boot_services_reviewed"}'
),

('linux', 'installed_packages', ARRAY['dpkg', '-l'], 'RWNCSA-CM-008', 'Software Inventory', 'Configuration Management',
 'List installed packages (Debian/Ubuntu)',
 '{"count_packages": true}',
 '{"compliant_if": "packages_inventoried"}'
),

('linux', 'rpm_packages', ARRAY['rpm', '-qa'], 'RWNCSA-CM-008', 'Software Inventory', 'Configuration Management',
 'List installed packages (RHEL/CentOS)',
 '{"count_packages": true}',
 '{"compliant_if": "packages_inventoried"}'
);

-- System and Communications Protection Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('linux', 'network_connections', ARRAY['ss', '-tulpn'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'Review active network connections and listening ports',
 '{"look_for": ["LISTEN", "ESTABLISHED"], "count_connections": true}',
 '{"compliant_if": "connections_monitored"}'
),

('linux', 'iptables_rules', ARRAY['iptables', '-L', '-n', '-v'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'Check iptables firewall rules',
 '{"look_for": ["Chain INPUT", "Chain OUTPUT", "ACCEPT", "DROP"]}',
 '{"compliant_if": "firewall_configured"}'
),

('linux', 'ufw_status', ARRAY['ufw', 'status', 'verbose'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'Check UFW firewall status',
 '{"look_for": ["Status: active", "Status: inactive"]}',
 '{"compliant_if": "contains", "expected": "Status: active"}'
),

('linux', 'firewalld_status', ARRAY['firewall-cmd', '--state'], 'RWNCSA-SC-007', 'Boundary Protection', 'System and Communications Protection',
 'Check firewalld status (RHEL/CentOS)',
 '{"look_for": ["running", "not running"]}',
 '{"compliant_if": "value_equals", "expected": "running"}'
),

('linux', 'ssh_config', ARRAY['cat', '/etc/ssh/sshd_config'], 'RWNCSA-SC-008', 'Transmission Confidentiality', 'System and Communications Protection',
 'Review SSH server configuration',
 '{"look_for": ["PermitRootLogin", "PasswordAuthentication", "Protocol"]}',
 '{"compliant_if": "ssh_hardened", "root_login_disabled": true}'
),

('linux', 'selinux_status', ARRAY['getenforce'], 'RWNCSA-SC-004', 'Information in Shared Resources', 'System and Communications Protection',
 'Check SELinux enforcement status',
 '{"look_for": ["Enforcing", "Permissive", "Disabled"]}',
 '{"compliant_if": "value_equals", "expected": "Enforcing"}'
),

('linux', 'apparmor_status', ARRAY['aa-status'], 'RWNCSA-SC-004', 'Information in Shared Resources', 'System and Communications Protection',
 'Check AppArmor status (Ubuntu/Debian)',
 '{"look_for": ["profiles are loaded", "profiles in enforce mode"]}',
 '{"compliant_if": "apparmor_active"}'
);

-- Identification and Authentication Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('linux', 'password_policy', ARRAY['cat', '/etc/login.defs'], 'RWNCSA-IA-005', 'Authenticator Management', 'Identification and Authentication',
 'Check system password policy settings',
 '{"look_for": ["PASS_MAX_DAYS", "PASS_MIN_DAYS", "PASS_MIN_LEN", "PASS_WARN_AGE"]}',
 '{"compliant_if": "policy_configured", "min_length": 8}'
),

('linux', 'pwquality_config', ARRAY['cat', '/etc/security/pwquality.conf'], 'RWNCSA-IA-005', 'Authenticator Management', 'Identification and Authentication',
 'Check password quality requirements',
 '{"look_for": ["minlen", "dcredit", "ucredit", "lcredit"]}',
 '{"compliant_if": "pwquality_configured"}'
),

('linux', 'empty_passwords', ARRAY['awk', '-F:', '($2 == "") {print $1}', '/etc/shadow'], 'RWNCSA-IA-005', 'Authenticator Management', 'Identification and Authentication',
 'Check for accounts with empty passwords',
 '{"expect_empty": true}',
 '{"compliant_if": "no_empty_passwords"}'
),

('linux', 'ssh_keys', ARRAY['find', '/home', '-name', 'authorized_keys', '-exec', 'cat', '{}', ';'], 'RWNCSA-IA-002', 'Identification and Authentication', 'Identification and Authentication',
 'Review SSH authorized keys',
 '{"count_keys": true}',
 '{"compliant_if": "keys_documented"}'
);

-- Media Protection Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('linux', 'luks_status', ARRAY['lsblk', '-f'], 'RWNCSA-MP-004', 'Media Storage', 'Media Protection',
 'Check disk encryption status (LUKS)',
 '{"look_for": ["crypto_LUKS", "LUKS"]}',
 '{"compliant_if": "encryption_enabled"}'
),

('linux', 'mounted_filesystems', ARRAY['mount'], 'RWNCSA-MP-004', 'Media Storage', 'Media Protection',
 'List mounted filesystems and options',
 '{"look_for": ["noexec", "nosuid", "nodev"]}',
 '{"compliant_if": "mounts_secure"}'
),

('linux', 'usb_devices', ARRAY['lsusb'], 'RWNCSA-MP-007', 'Media Use', 'Media Protection',
 'List connected USB devices',
 '{"count_devices": true}',
 '{"compliant_if": "devices_documented"}'
);

-- Contingency Planning Family
INSERT INTO os_audit_taxonomies (os_type, command_name, command_args, control_id, control_name, control_family, description, expected_indicators, compliance_criteria)
VALUES
('linux', 'backup_cron', ARRAY['crontab', '-l'], 'RWNCSA-CP-009', 'System Backup', 'Contingency Planning',
 'Check cron jobs for backup schedules',
 '{"look_for": ["backup", "rsync", "tar"]}',
 '{"compliant_if": "backup_scheduled"}'
),

('linux', 'backup_logs', ARRAY['ls', '-la', '/var/backups/'], 'RWNCSA-CP-009', 'System Backup', 'Contingency Planning',
 'Check backup directory',
 '{"check_recent": true}',
 '{"compliant_if": "backups_exist"}'
);

COMMIT;
