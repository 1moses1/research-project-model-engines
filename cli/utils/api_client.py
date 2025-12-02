"""
API Client for communicating with engines
"""

import os
import json
import httpx
from typing import Dict, Optional, Any
from pathlib import Path


class APIClient:
    """Client for communicating with Rwanda NCSA Compliance Auditor engines"""

    # Default engine ports
    ENGINE_PORTS = {
        "log_collector": 8001,
        "document_processor": 8002,
        "xgboost_classifier": 8003,
        "decision_engine": 8004,
        "web_ui": 8005,
        "report_generator": 8006,
        "auth_engine": 8007,
    }

    def __init__(self, base_url: str = "http://localhost", token: str = None):
        self.base_url = base_url
        self.token = token or os.getenv("RWANDA_NCSA_TOKEN")
        self.config_file = Path.home() / ".rwanda-ncsa" / "config.json"
        self._load_config()

    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                self.token = self.token or config.get("token")
                self.base_url = config.get("base_url", self.base_url)

    def _save_config(self, config: dict):
        """Save configuration to file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _get_engine_url(self, engine: str, endpoint: str = "") -> str:
        """Get full URL for an engine endpoint"""
        port = self.ENGINE_PORTS.get(engine, 8000)
        return f"{self.base_url}:{port}{endpoint}"

    async def login(self, username: str, password: str) -> Dict:
        """Login to the platform"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._get_engine_url("auth_engine", "/auth/login"),
                json={"username": username, "password": password},
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self._save_config({
                    "token": self.token,
                    "base_url": self.base_url
                })
                return data
            else:
                raise Exception(f"Login failed: {response.text}")

    async def logout(self) -> Dict:
        """Logout from the platform"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._get_engine_url("auth_engine", "/auth/logout"),
                headers=self._get_headers()
            )

            self.token = None
            if self.config_file.exists():
                self.config_file.unlink()

            return {"message": "Logged out successfully"}

    async def get_current_user(self) -> Dict:
        """Get current user info"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self._get_engine_url("auth_engine", "/auth/me"),
                headers=self._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception("Not authenticated")

    async def classify_log(self, log_message: str) -> Dict:
        """Classify a log message"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._get_engine_url("xgboost_classifier", "/classify"),
                json={"log_message": log_message},
                headers=self._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Classification failed: {response.text}")

    async def process_document(self, file_path: str) -> Dict:
        """Process a policy document"""
        async with httpx.AsyncClient() as client:
            with open(file_path, 'rb') as f:
                files = {"file": (Path(file_path).name, f, "application/pdf")}
                response = await client.post(
                    self._get_engine_url("document_processor", "/upload"),
                    files=files,
                    headers={"Authorization": f"Bearer {self.token}"} if self.token else {}
                )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Document processing failed: {response.text}")

    async def collect_logs(self, hostname: str, log_type: str = "all") -> Dict:
        """Collect logs from a target machine"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._get_engine_url("log_collector", "/collect"),
                json={"hostname": hostname, "log_type": log_type},
                headers=self._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Log collection failed: {response.text}")

    async def generate_report(self, audit_id: str, format: str = "pdf") -> Dict:
        """Generate compliance report"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._get_engine_url("report_generator", "/generate"),
                json={"audit_id": audit_id, "format": format},
                headers=self._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Report generation failed: {response.text}")

    async def get_engine_health(self, engine: str) -> Dict:
        """Check engine health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    self._get_engine_url(engine, "/health")
                )

                if response.status_code == 200:
                    return {"status": "healthy", **response.json()}
                else:
                    return {"status": "unhealthy", "code": response.status_code}
        except Exception as e:
            return {"status": "offline", "error": str(e)}

    async def get_all_engines_status(self) -> Dict[str, Dict]:
        """Get status of all engines"""
        status = {}
        for engine in self.ENGINE_PORTS:
            status[engine] = await self.get_engine_health(engine)
        return status

    async def connect_to_machine(
        self,
        hostname: str,
        username: str,
        auth_method: str,
        port: int = 22,
        password: str = None,
        ssh_key_path: str = None,
        os_type: str = "linux"
    ) -> Dict:
        """Connect to a target machine for auditing"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._get_engine_url("auth_engine", "/auth/machine/connect"),
                json={
                    "hostname": hostname,
                    "port": port,
                    "username": username,
                    "auth_method": auth_method,
                    "password": password,
                    "ssh_key_path": ssh_key_path,
                    "os_type": os_type
                },
                headers=self._get_headers()
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Connection failed: {response.text}")
