"""
Platform Authentication Service
Handles JWT-based user authentication for the platform
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
import jwt
import hashlib
import secrets
import json
from pathlib import Path


class PlatformAuthService:
    """Platform user authentication using JWT"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.users_file = Path(__file__).parent.parent / "data" / "users.json"
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_users()

    def _load_users(self):
        """Load users from file"""
        if self.users_file.exists():
            with open(self.users_file, 'r') as f:
                self.users = json.load(f)
        else:
            # Create default admin user
            self.users = {
                "admin": {
                    "id": "1",
                    "username": "admin",
                    "email": "admin@rwanda-ncsa.gov.rw",
                    "password_hash": self._hash_password("admin123"),
                    "role": "admin",
                    "created_at": datetime.utcnow().isoformat()
                }
            }
            self._save_users()

    def _save_users(self):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f, indent=2)

    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        return self._hash_password(password) == password_hash

    async def register_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "auditor"
    ) -> Dict:
        """Register a new user"""
        if username in self.users:
            raise ValueError(f"User '{username}' already exists")

        user_id = str(len(self.users) + 1)
        user = {
            "id": user_id,
            "username": username,
            "email": email,
            "password_hash": self._hash_password(password),
            "role": role,
            "created_at": datetime.utcnow().isoformat()
        }

        self.users[username] = user
        self._save_users()

        return {"id": user_id, "username": username, "role": role}

    async def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user with username and password"""
        if username not in self.users:
            return None

        user = self.users[username]
        if not self._verify_password(password, user["password_hash"]):
            return None

        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=30))
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
