"""
ENGINE 7: Authentication & Authorization Engine
Rwanda NCSA Compliance Auditor v1.0.0

Handles:
- Machine authentication (SSH/WinRM for audit access)
- Platform user authentication (JWT)
- Secure audit user creation with read-only permissions
- Session management
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import os
import jwt
import secrets
import hashlib
import platform
from enum import Enum

from app.services.machine_auth import MachineAuthService
from app.services.platform_auth import PlatformAuthService
from app.services.session_manager import SessionManager
from app.services.audit_user_manager import AuditUserManager

# Initialize FastAPI
app = FastAPI(
    title="ENGINE 7: Authentication & Authorization Engine",
    description="Secure authentication for machine auditing and platform access",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Configuration
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = os.getenv("AUTH_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("AUTH_ACCESS_TOKEN_EXPIRE_MINUTES", 30))

# Initialize services
machine_auth = MachineAuthService()
platform_auth = PlatformAuthService(secret_key=SECRET_KEY, algorithm=ALGORITHM)
session_manager = SessionManager()
audit_user_manager = AuditUserManager()


# ============================================================================
# Models
# ============================================================================

class OSType(str, Enum):
    LINUX = "linux"
    MACOS = "macos"
    WINDOWS = "windows"


class AuthMethod(str, Enum):
    SSH_KEY = "ssh_key"
    SSH_PASSWORD = "ssh_password"
    LOCAL = "local"
    WINRM = "winrm"


class MachineConnectRequest(BaseModel):
    """Request to connect to a target machine for auditing"""
    hostname: str = Field(..., description="Target hostname or IP")
    port: int = Field(22, description="SSH/WinRM port")
    username: str = Field(..., description="Username for authentication")
    auth_method: AuthMethod = Field(..., description="Authentication method")
    password: Optional[str] = Field(None, description="Password (if using password auth)")
    ssh_key_path: Optional[str] = Field(None, description="Path to SSH private key")
    os_type: OSType = Field(OSType.LINUX, description="Target OS type")

    class Config:
        json_schema_extra = {
            "example": {
                "hostname": "192.168.1.100",
                "port": 22,
                "username": "admin",
                "auth_method": "ssh_key",
                "ssh_key_path": "/path/to/id_rsa",
                "os_type": "linux"
            }
        }


class AuditUserCreateRequest(BaseModel):
    """Request to create audit user on target machine"""
    hostname: str = Field(..., description="Target hostname")
    admin_username: str = Field(..., description="Admin username for user creation")
    admin_password: Optional[str] = Field(None, description="Admin password")
    audit_username: str = Field("rwanda_ncsa_auditor", description="Audit user to create")
    allowed_directories: List[str] = Field(
        default=["/var/log/", "/etc/"],
        description="Directories the audit user can access"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "hostname": "192.168.1.100",
                "admin_username": "root",
                "audit_username": "rwanda_ncsa_auditor",
                "allowed_directories": ["/var/log/", "/etc/", "/var/log/audit/"]
            }
        }


class PlatformLoginRequest(BaseModel):
    """Platform user login"""
    username: str
    password: str


class PlatformRegisterRequest(BaseModel):
    """Platform user registration"""
    username: str
    email: str
    password: str
    role: str = "auditor"


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class MachineConnectionResponse(BaseModel):
    """Machine connection response"""
    connected: bool
    session_id: str
    hostname: str
    os_type: str
    audit_user: Optional[str] = None
    message: str


class AuditUserPermissions(BaseModel):
    """Audit user permissions display"""
    username: str
    allowed_directories: List[str]
    allowed_commands: List[str]
    prohibited_commands: List[str]
    read_only: bool = True
    can_execute_shell: bool = False


# ============================================================================
# Platform Authentication Endpoints
# ============================================================================

@app.post("/auth/register", response_model=TokenResponse)
async def register_user(request: PlatformRegisterRequest):
    """Register a new platform user"""
    try:
        user = await platform_auth.register_user(
            username=request.username,
            email=request.email,
            password=request.password,
            role=request.role
        )

        token = platform_auth.create_access_token(
            data={"sub": user["username"], "role": user["role"]},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return TokenResponse(
            access_token=token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/auth/login", response_model=TokenResponse)
async def login(request: PlatformLoginRequest):
    """Login to the platform"""
    try:
        user = await platform_auth.authenticate_user(
            username=request.username,
            password=request.password
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

        # Create session
        session_id = await session_manager.create_session(
            user_id=user["id"],
            user_agent="API",
            ip_address="local"
        )

        token = platform_auth.create_access_token(
            data={
                "sub": user["username"],
                "role": user["role"],
                "session_id": session_id
            },
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )

        return TokenResponse(
            access_token=token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Logout and invalidate session"""
    try:
        payload = platform_auth.verify_token(credentials.credentials)
        session_id = payload.get("session_id")

        if session_id:
            await session_manager.revoke_session(session_id)

        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/auth/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    try:
        payload = platform_auth.verify_token(credentials.credentials)
        return {
            "username": payload.get("sub"),
            "role": payload.get("role"),
            "session_id": payload.get("session_id")
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


# ============================================================================
# Machine Authentication Endpoints
# ============================================================================

@app.post("/auth/machine/connect", response_model=MachineConnectionResponse)
async def connect_to_machine(
    request: MachineConnectRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Connect to a target machine for auditing"""
    # Verify platform authentication first
    try:
        platform_auth.verify_token(credentials.credentials)
    except:
        raise HTTPException(status_code=401, detail="Platform authentication required")

    try:
        result = await machine_auth.connect(
            hostname=request.hostname,
            port=request.port,
            username=request.username,
            auth_method=request.auth_method.value,
            password=request.password,
            ssh_key_path=request.ssh_key_path,
            os_type=request.os_type.value
        )

        return MachineConnectionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/auth/machine/permissions", response_model=AuditUserPermissions)
async def get_audit_permissions():
    """Get the permissions that will be granted to the audit user"""
    return AuditUserPermissions(
        username="rwanda_ncsa_auditor",
        allowed_directories=[
            "/var/log/",
            "/var/log/audit/",
            "/var/log/syslog",
            "/var/log/auth.log",
            "/var/log/secure",
            "/etc/ (read-only configs)"
        ],
        allowed_commands=[
            "cat", "head", "tail", "less", "grep",
            "journalctl", "last", "lastlog", "who", "w",
            "ps", "netstat", "ss", "df", "du",
            "systemctl status", "service status",
            "id", "getent", "groups"
        ],
        prohibited_commands=[
            "rm", "mv", "cp", "chmod", "chown",
            "sudo", "su", "passwd",
            "wget", "curl", "nc",
            "python", "perl", "ruby", "bash", "sh",
            "kill", "reboot", "shutdown",
            "iptables", "firewall-cmd"
        ],
        read_only=True,
        can_execute_shell=False
    )


@app.post("/auth/machine/create-audit-user")
async def create_audit_user(
    request: AuditUserCreateRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create a read-only audit user on the target machine.

    SECURITY WARNING: This will prompt for confirmation before creating the user.
    The user will have ONLY read-only access to specified directories.
    """
    # Verify platform authentication
    try:
        platform_auth.verify_token(credentials.credentials)
    except:
        raise HTTPException(status_code=401, detail="Platform authentication required")

    # Show what we're about to do
    permissions_preview = {
        "action": "CREATE_AUDIT_USER",
        "target_host": request.hostname,
        "audit_username": request.audit_username,
        "permissions": {
            "type": "READ_ONLY",
            "allowed_directories": request.allowed_directories,
            "shell": "/bin/rbash",  # Restricted bash
            "sudo_access": False,
            "home_directory": f"/home/{request.audit_username}"
        },
        "security_notes": [
            "User will have NO write permissions",
            "User cannot execute arbitrary commands",
            "User cannot access /root or private keys",
            "All actions will be logged",
            "Session timeout: 30 minutes"
        ],
        "requires_confirmation": True
    }

    return {
        "status": "CONFIRMATION_REQUIRED",
        "message": "Review the permissions below and confirm creation",
        "preview": permissions_preview,
        "confirm_endpoint": "/auth/machine/create-audit-user/confirm"
    }


@app.post("/auth/machine/create-audit-user/confirm")
async def confirm_create_audit_user(
    request: AuditUserCreateRequest,
    confirmation: str = "I_CONFIRM_AUDIT_USER_CREATION",
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Confirm and execute audit user creation"""
    if confirmation != "I_CONFIRM_AUDIT_USER_CREATION":
        raise HTTPException(
            status_code=400,
            detail="Invalid confirmation. Must be: I_CONFIRM_AUDIT_USER_CREATION"
        )

    try:
        result = await audit_user_manager.create_audit_user(
            hostname=request.hostname,
            admin_username=request.admin_username,
            admin_password=request.admin_password,
            audit_username=request.audit_username,
            allowed_directories=request.allowed_directories
        )

        return {
            "status": "SUCCESS",
            "message": f"Audit user '{request.audit_username}' created successfully",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/auth/machine/disconnect/{session_id}")
async def disconnect_machine(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Disconnect from a machine audit session"""
    try:
        await machine_auth.disconnect(session_id)
        return {"message": "Disconnected successfully", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/auth/machine/sessions")
async def list_machine_sessions(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """List active machine audit sessions"""
    try:
        sessions = await machine_auth.list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Session Management Endpoints
# ============================================================================

@app.get("/sessions")
async def list_sessions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """List all active platform sessions"""
    payload = platform_auth.verify_token(credentials.credentials)
    sessions = await session_manager.get_user_sessions(payload.get("sub"))
    return {"sessions": sessions}


@app.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Revoke a specific session"""
    await session_manager.revoke_session(session_id)
    return {"message": "Session revoked", "session_id": session_id}


# ============================================================================
# Health & Info Endpoints
# ============================================================================

@app.get("/")
async def root():
    """Service information"""
    return {
        "service": "ENGINE 7: Authentication & Authorization Engine",
        "version": "1.0.0",
        "status": "running",
        "capabilities": [
            "Platform user authentication (JWT)",
            "Machine authentication (SSH/WinRM)",
            "Secure audit user creation",
            "Session management",
            "Command whitelist enforcement"
        ],
        "current_os": platform.system()
    }


@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "service": "Auth Engine",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# Startup
# ============================================================================

@app.on_event("startup")
async def startup():
    print("=" * 80)
    print("ENGINE 7: Authentication & Authorization Engine")
    print("Rwanda NCSA Compliance Auditor v1.0.0")
    print("=" * 80)
    print(f"🔐 Platform Auth: JWT (HS256)")
    print(f"🖥️  Machine Auth: SSH, WinRM, Local")
    print(f"👤 Audit User: rwanda_ncsa_auditor (read-only)")
    print(f"⏱️  Token Expiry: {ACCESS_TOKEN_EXPIRE_MINUTES} minutes")
    print(f"🖥️  Current OS: {platform.system()}")
    print("=" * 80)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
