#!/usr/bin/env python3
"""
Generate API Keys for Rwanda SOC Analysts
Creates different roles with appropriate permissions
"""

import secrets
import json
from pathlib import Path
from datetime import datetime

def generate_api_key():
    """Generate secure API key"""
    return secrets.token_urlsafe(32)

def main():
    print("=" * 80)
    print("API KEY GENERATION FOR RWANDA SOC")
    print("=" * 80)
    print("")

    # Predefined user roles
    users_to_create = [
        {
            'username': 'soc_analyst_1',
            'role': 'analyst',
            'description': 'SOC Analyst - Predictions & Metrics',
            'permissions': ['predict', 'view_metrics']
        },
        {
            'username': 'soc_analyst_2',
            'role': 'analyst',
            'description': 'SOC Analyst - Predictions & Metrics',
            'permissions': ['predict', 'view_metrics']
        },
        {
            'username': 'soc_viewer',
            'role': 'viewer',
            'description': 'SOC Viewer - Metrics Only',
            'permissions': ['view_metrics']
        },
        {
            'username': 'api_integration',
            'role': 'api_user',
            'description': 'API Integration - Automated Predictions',
            'permissions': ['predict']
        },
        {
            'username': 'security_admin',
            'role': 'admin',
            'description': 'Security Administrator - Full Access',
            'permissions': ['predict', 'train', 'deploy', 'view_metrics', 'manage_users']
        }
    ]

    print(f"Generating API keys for {len(users_to_create)} users...")
    print("")

    credentials_dir = Path('config') / 'credentials'
    credentials_dir.mkdir(parents=True, exist_ok=True)

    all_keys = []

    for user in users_to_create:
        api_key = generate_api_key()

        user_data = {
            'username': user['username'],
            'role': user['role'],
            'description': user['description'],
            'api_key': api_key,
            'permissions': user['permissions'],
            'created_at': datetime.now().isoformat(),
            'active': True
        }

        # Save individual user file
        user_file = credentials_dir / f"{user['username']}.json"
        with open(user_file, 'w') as f:
            json.dump(user_data, f, indent=2)

        import os
        os.chmod(user_file, 0o600)

        all_keys.append(user_data)

        print(f"✅ {user['username']}")
        print(f"   Role: {user['role']}")
        print(f"   API Key: {api_key}")
        print(f"   Permissions: {', '.join(user['permissions'])}")
        print("")

    # Save master API key file
    master_file = credentials_dir / 'all_api_keys.json'
    with open(master_file, 'w') as f:
        json.dump(all_keys, f, indent=2)

    import os
    os.chmod(master_file, 0o600)

    print("=" * 80)
    print("API KEY GENERATION COMPLETE ✅")
    print("=" * 80)
    print(f"Total users created: {len(all_keys)}")
    print(f"Credentials directory: {credentials_dir}")
    print(f"Master file: {master_file}")
    print("")

    print("Usage Examples:")
    print("-" * 80)
    print("")
    print("1. Analyst making prediction:")
    print("   curl -X POST https://localhost:5000/api/predict \\")
    print("     -H 'Authorization: Bearer <ANALYST_API_KEY>' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"log_message\": \"...\"}'")
    print("")
    print("2. Viewer checking metrics:")
    print("   curl https://localhost:5000/api/metrics \\")
    print("     -H 'Authorization: Bearer <VIEWER_API_KEY>'")
    print("")
    print("3. Admin deploying model:")
    print("   curl -X POST https://localhost:5000/api/deploy \\")
    print("     -H 'Authorization: Bearer <ADMIN_API_KEY>'")
    print("")
    print("=" * 80)
    print("")

    # Distribution instructions
    print("SECURE DISTRIBUTION INSTRUCTIONS:")
    print("-" * 80)
    print("1. Save this output securely (password manager/vault)")
    print("2. Distribute keys via secure channel (encrypted email/Slack DM)")
    print("3. Never commit API keys to git")
    print("4. Rotate keys every 90 days")
    print("5. Revoke keys immediately if compromised")
    print("")
    print("To revoke a key:")
    print(f"  1. Edit {credentials_dir}/<username>.json")
    print("  2. Set 'active': false")
    print("  3. User's API calls will be rejected")
    print("")
    print("=" * 80)

    # Log key generation
    log_file = Path('logs') / 'audit' / 'security_events.log'
    if log_file.exists():
        with open(log_file, 'a') as f:
            event = {
                'timestamp': datetime.now().isoformat(),
                'event': 'API_KEYS_GENERATED',
                'count': len(all_keys),
                'users': [u['username'] for u in all_keys]
            }
            f.write(json.dumps(event) + '\n')

if __name__ == '__main__':
    main()
