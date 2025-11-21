#!/usr/bin/env python3
"""
Create Secure Admin Credentials for Phase 2.5 Model
Generates strong password and stores securely
"""

import hashlib
import secrets
import json
import getpass
from pathlib import Path
from datetime import datetime

def generate_strong_password(length=20):
    """Generate cryptographically strong password"""
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password, salt):
    """Hash password with PBKDF2"""
    return hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000  # 100,000 iterations
    ).hex()

def main():
    print("=" * 80)
    print("ADMIN CREDENTIAL CREATION FOR PHASE 2.5 MODEL")
    print("=" * 80)
    print("")

    # Get username
    username = input("Enter admin username [admin]: ").strip() or "admin"

    # Option to generate or enter password
    print("")
    print("Password Options:")
    print("  1. Generate strong password (recommended)")
    print("  2. Enter custom password (min 12 characters)")
    choice = input("Select option [1]: ").strip() or "1"

    if choice == "1":
        password = generate_strong_password(20)
        print(f"\n  ✅ Generated strong password: {password}")
        print("  ⚠️  SAVE THIS PASSWORD SECURELY - IT WON'T BE SHOWN AGAIN")
    else:
        while True:
            password = getpass.getpass("\nEnter admin password (min 12 chars): ")
            if len(password) < 12:
                print("  ❌ Password must be at least 12 characters")
                continue

            confirm = getpass.getpass("Confirm password: ")
            if password != confirm:
                print("  ❌ Passwords don't match")
                continue

            break

    # Generate salt and hash password
    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    # Generate API key
    api_key = secrets.token_urlsafe(32)

    # Create user record
    user_data = {
        'username': username,
        'password_hash': password_hash,
        'salt': salt,
        'role': 'admin',
        'api_key': api_key,
        'created_at': datetime.now().isoformat(),
        'permissions': [
            'predict',
            'train',
            'deploy',
            'view_metrics',
            'manage_users'
        ]
    }

    # Save securely
    credentials_dir = Path('config') / 'credentials'
    credentials_dir.mkdir(parents=True, exist_ok=True)

    credentials_file = credentials_dir / 'admin_user.json'
    with open(credentials_file, 'w') as f:
        json.dump(user_data, f, indent=2)

    # Set secure permissions
    import os
    os.chmod(credentials_file, 0o600)  # Read/write for owner only

    print("")
    print("=" * 80)
    print("ADMIN CREDENTIALS CREATED ✅")
    print("=" * 80)
    print(f"Username: {username}")
    print(f"Role: admin")
    print(f"API Key: {api_key}")
    print(f"Credentials file: {credentials_file}")
    print(f"File permissions: 600 (owner read/write only)")
    print("")
    print("Permissions:")
    for perm in user_data['permissions']:
        print(f"  ✅ {perm}")
    print("")
    print("=" * 80)
    print("IMPORTANT: SAVE THESE CREDENTIALS SECURELY")
    print("=" * 80)
    print("")
    print("Login with JWT:")
    print(f'  POST /api/auth/login')
    print(f'  {{  "username": "{username}", "password": "<password>" }}')
    print("")
    print("Or use API Key:")
    print(f'  Authorization: Bearer {api_key}')
    print("")
    print("=" * 80)

    # Log credential creation
    log_file = Path('logs') / 'audit' / 'security_events.log'
    if log_file.exists():
        with open(log_file, 'a') as f:
            event = {
                'timestamp': datetime.now().isoformat(),
                'event': 'ADMIN_CREDENTIAL_CREATED',
                'username': username,
                'role': 'admin'
            }
            f.write(json.dumps(event) + '\n')

if __name__ == '__main__':
    main()
