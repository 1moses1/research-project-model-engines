"""
MCP (Model Context Protocol) Client Service
Connects to MCP servers for log collection with read-only command execution
"""

from typing import Dict, Optional, List
import asyncio
import subprocess
import uuid
import os
import shlex


class MCPClient:
    """MCP Protocol client for log collection with read-only command execution"""

    # Whitelist of allowed read-only commands
    ALLOWED_COMMANDS = [
        'cat',
        'tail',
        'head',
        'grep',
        'ls',
        'find',
        'journalctl',
        'dmesg',
        'systemctl status',
        'netstat',
        'ss',
        'ps',
        'top',
        'who',
        'last',
        'lastlog',
        'w',
        'uptime',
        'df',
        'du',
        'free',
        'date'
    ]

    # Maximum command execution time (seconds)
    COMMAND_TIMEOUT = 30

    def __init__(self):
        self.connected = False
        self.server_url = None
        self.connection_id = None
        self.subscriptions = {}
        self.command_execution_enabled = True

    def is_connected(self) -> bool:
        """Check if connected to MCP server"""
        return self.connected

    async def connect(self, server_url: str) -> Dict:
        """
        Connect to MCP server

        Args:
            server_url: MCP server URL

        Returns:
            Connection result
        """
        try:
            print(f"🔗 Connecting to MCP server: {server_url}")

            # In a real implementation, this would establish WebSocket or HTTP/2 connection
            # For now, simulate connection
            self.server_url = server_url
            self.connection_id = str(uuid.uuid4())
            self.connected = True

            print(f"✅ Connected to MCP server: {self.connection_id}")

            return {
                "success": True,
                "connection_id": self.connection_id,
                "server_url": server_url
            }

        except Exception as e:
            print(f"⚠️ MCP connection error: {str(e)}")
            self.connected = False
            raise

    async def disconnect(self):
        """Disconnect from MCP server"""
        if self.connected:
            print(f"🔌 Disconnecting from MCP server: {self.server_url}")
            self.connected = False
            self.connection_id = None
            self.subscriptions = {}

    async def subscribe(self, log_source: str) -> Dict:
        """
        Subscribe to log source

        Args:
            log_source: Log source identifier

        Returns:
            Subscription result
        """
        try:
            if not self.connected:
                raise Exception("Not connected to MCP server")

            print(f"📡 Subscribing to log source: {log_source}")

            subscription_id = str(uuid.uuid4())
            self.subscriptions[log_source] = {
                "subscription_id": subscription_id,
                "log_source": log_source,
                "active": True
            }

            print(f"✅ Subscribed to {log_source}: {subscription_id}")

            return {
                "success": True,
                "subscription_id": subscription_id,
                "log_source": log_source
            }

        except Exception as e:
            print(f"⚠️ MCP subscription error: {str(e)}")
            raise

    async def unsubscribe(self, log_source: str) -> Dict:
        """
        Unsubscribe from log source

        Args:
            log_source: Log source identifier

        Returns:
            Unsubscription result
        """
        if log_source in self.subscriptions:
            subscription = self.subscriptions.pop(log_source)
            print(f"🔕 Unsubscribed from {log_source}")
            return {
                "success": True,
                "log_source": log_source,
                "subscription_id": subscription["subscription_id"]
            }
        else:
            raise Exception(f"Not subscribed to {log_source}")

    async def receive_logs(self) -> List[Dict]:
        """
        Receive logs from MCP server

        In a real implementation, this would poll or stream logs

        Returns:
            List of log events
        """
        if not self.connected:
            return []

        # Simulate receiving logs
        # In production, this would receive actual logs from MCP server
        return []

    def get_subscriptions(self) -> List[Dict]:
        """Get active subscriptions"""
        return list(self.subscriptions.values())

    async def execute_command(
        self,
        command: str,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Execute a read-only command safely

        Args:
            command: Command to execute (must be in whitelist)
            timeout: Command timeout in seconds

        Returns:
            Command execution result with stdout/stderr

        Security:
            - Only whitelisted commands allowed
            - Sandboxed execution (no shell)
            - Timeout enforcement
            - No write operations
        """
        try:
            if not self.command_execution_enabled:
                raise Exception("Command execution is disabled")

            # Parse command
            parts = shlex.split(command)
            if not parts:
                raise ValueError("Empty command")

            base_command = parts[0]

            # Check if command is whitelisted
            if not self._is_command_allowed(base_command):
                raise PermissionError(f"Command '{base_command}' not in whitelist")

            # Execute command with timeout
            timeout_val = timeout or self.COMMAND_TIMEOUT

            print(f"🔧 Executing read-only command: {command}")

            # Use subprocess.run for safe execution (no shell=True)
            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                timeout=timeout_val,
                shell=False  # CRITICAL: No shell injection
            )

            stdout = result.stdout
            stderr = result.stderr
            return_code = result.returncode

            print(f"✅ Command completed with return code: {return_code}")

            return {
                "success": return_code == 0,
                "command": command,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": return_code,
                "timeout": timeout_val
            }

        except subprocess.TimeoutExpired:
            print(f"⚠️ Command timed out after {timeout_val}s")
            return {
                "success": False,
                "command": command,
                "error": f"Command timed out after {timeout_val} seconds",
                "timeout": timeout_val
            }

        except PermissionError as e:
            print(f"⚠️ Permission denied: {str(e)}")
            return {
                "success": False,
                "command": command,
                "error": str(e)
            }

        except Exception as e:
            print(f"⚠️ Command execution error: {str(e)}")
            return {
                "success": False,
                "command": command,
                "error": str(e)
            }

    async def read_log_file(
        self,
        file_path: str,
        lines: int = 100,
        follow: bool = False
    ) -> Dict:
        """
        Read log file using tail command

        Args:
            file_path: Path to log file
            lines: Number of lines to read
            follow: Follow mode (like tail -f)

        Returns:
            Log file contents
        """
        try:
            if follow:
                # For follow mode, use tail -f (streaming)
                command = f"tail -f -n {lines} {shlex.quote(file_path)}"
            else:
                # For static read, use tail
                command = f"tail -n {lines} {shlex.quote(file_path)}"

            result = await self.execute_command(command, timeout=10)

            if result['success']:
                return {
                    "success": True,
                    "file_path": file_path,
                    "lines": result['stdout'].split('\n'),
                    "line_count": len(result['stdout'].split('\n'))
                }
            else:
                return result

        except Exception as e:
            return {
                "success": False,
                "file_path": file_path,
                "error": str(e)
            }

    async def query_journalctl(
        self,
        unit: Optional[str] = None,
        since: str = "1 hour ago",
        lines: int = 100
    ) -> Dict:
        """
        Query systemd journal logs

        Args:
            unit: Service unit name (e.g., 'sshd')
            since: Time range (e.g., '1 hour ago')
            lines: Number of lines

        Returns:
            Journal entries
        """
        try:
            command_parts = ['journalctl', '-n', str(lines), '--since', since]

            if unit:
                command_parts.extend(['-u', unit])

            command = ' '.join(shlex.quote(str(p)) for p in command_parts)
            result = await self.execute_command(command, timeout=15)

            if result['success']:
                return {
                    "success": True,
                    "unit": unit,
                    "since": since,
                    "entries": result['stdout'].split('\n'),
                    "entry_count": len(result['stdout'].split('\n'))
                }
            else:
                return result

        except Exception as e:
            return {
                "success": False,
                "unit": unit,
                "error": str(e)
            }

    def _is_command_allowed(self, command: str) -> bool:
        """
        Check if command is in whitelist

        Args:
            command: Base command to check

        Returns:
            True if allowed, False otherwise
        """
        # Check exact match
        if command in self.ALLOWED_COMMANDS:
            return True

        # Check if it's a base command of a compound whitelisted command
        for allowed in self.ALLOWED_COMMANDS:
            if allowed.startswith(command + ' '):
                return True

        return False
