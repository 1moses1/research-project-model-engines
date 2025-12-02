"""
Session Manager Service
Handles platform user sessions
"""

import secrets
from typing import Dict, List, Optional
from datetime import datetime


class SessionManager:
    """Manage user sessions"""

    def __init__(self):
        self.sessions: Dict[str, Dict] = {}

    async def create_session(
        self,
        user_id: str,
        user_agent: str = "unknown",
        ip_address: str = "unknown"
    ) -> str:
        """Create a new session"""
        session_id = secrets.token_hex(32)

        self.sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "user_agent": user_agent,
            "ip_address": ip_address,
            "created_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
            "active": True
        }

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    async def get_user_sessions(self, user_id: str) -> List[Dict]:
        """Get all sessions for a user"""
        return [
            s for s in self.sessions.values()
            if s["user_id"] == user_id and s["active"]
        ]

    async def revoke_session(self, session_id: str):
        """Revoke a session"""
        if session_id in self.sessions:
            self.sessions[session_id]["active"] = False

    async def update_activity(self, session_id: str):
        """Update session last activity"""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
