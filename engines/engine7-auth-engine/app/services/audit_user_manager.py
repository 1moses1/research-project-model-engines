"""
Audit User Manager Service
Creates and manages read-only audit users on target systems
"""

import platform
from typing import Dict, List, Optional


class AuditUserManager:
    """Manage audit users on target systems"""

    # Whitelisted audit commands per OS
    AUDIT_COMMANDS = {
        "linux": {
            "log_reading": ["cat", "head", "tail", "less", "grep", "awk"],
            "system_info": ["journalctl", "last", "lastlog", "who", "w", "uptime"],
            "process_network": ["ps", "netstat", "ss", "lsof"],
            "user_info": ["id", "getent", "groups"],
            "service_status": ["systemctl status", "service --status-all"],
            "filesystem": ["ls", "stat", "file", "df", "du"]
        },
        "darwin": {  # macOS
            "log_reading": ["cat", "head", "tail", "less", "grep", "awk"],
            "system_info": ["log show", "last", "who", "w", "uptime"],
            "process_network": ["ps", "netstat", "lsof"],
            "user_info": ["id", "dscl . list /Users"],
            "service_status": ["launchctl list"],
            "filesystem": ["ls", "stat", "file", "df", "du"]
        },
        "windows": {
            "log_reading": ["Get-EventLog", "Get-WinEvent"],
            "system_info": ["Get-ComputerInfo", "Get-Process", "Get-Service"],
            "process_network": ["Get-NetTCPConnection", "Get-Process"],
            "user_info": ["Get-LocalUser", "Get-LocalGroup"],
            "service_status": ["Get-Service"],
            "filesystem": ["Get-ChildItem", "Get-Acl"]
        }
    }

    # Audit directories by OS
    AUDIT_DIRECTORIES = {
        "linux": [
            "/var/log/",
            "/var/log/audit/",
            "/var/log/syslog",
            "/var/log/auth.log",
            "/var/log/secure",
            "/var/log/messages",
            "/etc/passwd",
            "/etc/group",
            "/etc/ssh/sshd_config"
        ],
        "darwin": [
            "/var/log/",
            "/var/log/system.log",
            "/var/log/secure.log",
            "/private/var/log/"
        ],
        "windows": [
            "C:\\Windows\\System32\\winevt\\Logs\\",
            "C:\\Windows\\System32\\config\\"
        ]
    }

    def __init__(self):
        self.current_os = platform.system().lower()
        if self.current_os == "darwin":
            self.current_os = "darwin"

    def get_os_commands(self, os_type: str = None) -> Dict:
        """Get audit commands for an OS"""
        os_type = os_type or self.current_os
        return self.AUDIT_COMMANDS.get(os_type, self.AUDIT_COMMANDS["linux"])

    def get_audit_directories(self, os_type: str = None) -> List[str]:
        """Get audit directories for an OS"""
        os_type = os_type or self.current_os
        return self.AUDIT_DIRECTORIES.get(os_type, self.AUDIT_DIRECTORIES["linux"])

    async def create_audit_user(
        self,
        hostname: str,
        admin_username: str,
        admin_password: Optional[str],
        audit_username: str = "rwanda_ncsa_auditor",
        allowed_directories: List[str] = None
    ) -> Dict:
        """
        Create a read-only audit user on the target system.

        This is a simulation - in production, this would:
        1. SSH to the target machine as admin
        2. Create the user with restricted shell (rbash)
        3. Set up ACLs for read-only access to specified directories
        4. Generate and securely store credentials
        """
        allowed_directories = allowed_directories or self.get_audit_directories()

        # Generate user creation script based on OS
        if hostname in ["localhost", "127.0.0.1"]:
            os_type = self.current_os
        else:
            os_type = "linux"  # Default assumption for remote

        if os_type in ["linux", "darwin"]:
            creation_script = self._generate_linux_user_script(
                audit_username,
                allowed_directories
            )
        else:
            creation_script = self._generate_windows_user_script(
                audit_username,
                allowed_directories
            )

        return {
            "status": "created",
            "username": audit_username,
            "hostname": hostname,
            "os_type": os_type,
            "shell": "/bin/rbash" if os_type != "windows" else "restricted",
            "allowed_directories": allowed_directories,
            "allowed_commands": list(self.get_os_commands(os_type).keys()),
            "creation_script": creation_script,
            "note": "User created with read-only permissions"
        }

    def _generate_linux_user_script(
        self,
        username: str,
        directories: List[str]
    ) -> str:
        """Generate Linux user creation script"""
        acl_commands = "\n".join([
            f"setfacl -m u:{username}:rx {d}" for d in directories
        ])

        return f'''#!/bin/bash
# Create audit user with restricted shell
useradd -m -s /bin/rbash {username}

# Set random password (will be stored securely)
PASSWORD=$(openssl rand -base64 12)
echo "{username}:$PASSWORD" | chpasswd

# Create restricted bin directory
mkdir -p /home/{username}/bin
chmod 755 /home/{username}/bin

# Link only allowed commands
for cmd in cat head tail less grep journalctl last who ps netstat ss df ls; do
    ln -s $(which $cmd) /home/{username}/bin/$cmd 2>/dev/null
done

# Set PATH to only use restricted bin
echo "export PATH=/home/{username}/bin" >> /home/{username}/.bashrc
chmod 444 /home/{username}/.bashrc

# Set up read-only ACLs for audit directories
{acl_commands}

# Lock down home directory
chmod 750 /home/{username}

echo "Audit user '{username}' created successfully"
'''

    def _generate_windows_user_script(
        self,
        username: str,
        directories: List[str]
    ) -> str:
        """Generate Windows user creation script"""
        return f'''# PowerShell script to create audit user
$Password = ConvertTo-SecureString (New-Guid).Guid -AsPlainText -Force
New-LocalUser -Name "{username}" -Password $Password -Description "Rwanda NCSA Audit User"

# Add to Event Log Readers group (read-only)
Add-LocalGroupMember -Group "Event Log Readers" -Member "{username}"

# Set up read-only permissions for audit directories
# ... (ACL configuration)

Write-Host "Audit user '{username}' created successfully"
'''
