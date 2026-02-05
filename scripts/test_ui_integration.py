#!/usr/bin/env python3
"""
Test UI Integration API Endpoints

This script tests the new UI integration endpoints added to Engine 6
according to the UI_INTEGRATION_PLAN.md.
"""

import asyncio
import httpx
import json
from datetime import datetime

API_BASE = "http://localhost:8006"


async def test_dashboard_endpoints():
    """Test dashboard-related endpoints"""
    print("\n" + "=" * 60)
    print("Testing Dashboard Endpoints")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test /api/stats/overview
        print("\n1. GET /api/stats/overview")
        try:
            response = await client.get(f"{API_BASE}/api/stats/overview")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Compliance Rate: {data.get('compliance_rate', 'N/A')}%")
                print(f"   Risk Level: {data.get('risk_level', 'N/A')}")
                print(f"   Total Audits: {data.get('total_audits', 0)}")
        except Exception as e:
            print(f"   Error: {e}")

        # Test /api/audits/recent
        print("\n2. GET /api/audits/recent")
        try:
            response = await client.get(f"{API_BASE}/api/audits/recent?limit=5")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Total: {data.get('total', 0)} audits")
                for audit in data.get('audits', [])[:3]:
                    print(f"   - {audit.get('audit_id')}: {audit.get('status')}")
        except Exception as e:
            print(f"   Error: {e}")

        # Test /api/control-families
        print("\n3. GET /api/control-families")
        try:
            response = await client.get(f"{API_BASE}/api/control-families")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Total Families: {data.get('total', 0)}")
                for family in data.get('families', [])[:5]:
                    print(f"   - {family}")
        except Exception as e:
            print(f"   Error: {e}")


async def test_audit_workflow():
    """Test the complete audit workflow"""
    print("\n" + "=" * 60)
    print("Testing Audit Workflow")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Configure audit
        print("\n1. POST /api/audit/configure")
        config = {
            "audit_type": "full",
            "log_sources": [{"type": "sample"}],
            "document_ids": [],
            "control_families": [],
            "target_host": "localhost",
            "company_name": "Test Organization",
            "framework": "Rwanda-NCSA"
        }

        try:
            response = await client.post(
                f"{API_BASE}/api/audit/configure",
                json=config
            )
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                audit_id = data.get('audit_id')
                print(f"   Audit ID: {audit_id}")
                print(f"   Status: {data.get('status')}")

                # Step 2: Start audit
                print("\n2. POST /api/audit/start")
                start_response = await client.post(
                    f"{API_BASE}/api/audit/start",
                    json={"config": config}
                )
                print(f"   Status: {start_response.status_code}")

                if start_response.status_code == 200:
                    start_data = start_response.json()
                    audit_id = start_data.get('audit_id')
                    print(f"   Started Audit: {audit_id}")

                    # Step 3: Check status (poll a few times)
                    print("\n3. GET /api/audit/{audit_id}/status (polling)")
                    for i in range(5):
                        await asyncio.sleep(2)
                        status_response = await client.get(
                            f"{API_BASE}/api/audit/{audit_id}/status"
                        )
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            progress = status_data.get('progress', 0)
                            stage = status_data.get('current_stage', 'unknown')
                            message = status_data.get('message', '')
                            print(f"   [{i+1}] {progress}% - {stage}: {message[:50]}...")

                            if status_data.get('status') in ['completed', 'failed']:
                                break
                        else:
                            print(f"   [{i+1}] Error: {status_response.status_code}")

                    # Step 4: Get results (if completed)
                    print("\n4. GET /api/audit/{audit_id}/results")
                    results_response = await client.get(
                        f"{API_BASE}/api/audit/{audit_id}/results"
                    )
                    print(f"   Status: {results_response.status_code}")
                    if results_response.status_code == 200:
                        results_data = results_response.json()
                        summary = results_data.get('summary', {})
                        print(f"   Compliance Rate: {summary.get('compliance_rate', 'N/A')}%")
                        print(f"   Risk Level: {summary.get('risk_level', 'N/A')}")
                        print(f"   Total Controls: {summary.get('total_controls', 0)}")

                    # Step 5: Get report preview
                    print("\n5. GET /api/audit/{audit_id}/report/preview")
                    preview_response = await client.get(
                        f"{API_BASE}/api/audit/{audit_id}/report/preview"
                    )
                    print(f"   Status: {preview_response.status_code}")
                    if preview_response.status_code == 200:
                        preview_data = preview_response.json()
                        print(f"   Company: {preview_data.get('company_name', 'N/A')}")
                        print(f"   Framework: {preview_data.get('framework', 'N/A')}")

        except Exception as e:
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()


async def test_legacy_endpoints():
    """Test legacy v3 API endpoints still work"""
    print("\n" + "=" * 60)
    print("Testing Legacy v3 Endpoints")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:
        endpoints = [
            ("GET", "/api/v3/audits"),
            ("GET", "/api/v3/system/status"),
            ("GET", "/api/v3/engines/status"),
            ("GET", "/api/v3/taxonomies"),
            ("GET", "/api/v3/controls"),
            ("GET", "/health"),
            ("GET", "/api"),
        ]

        for method, endpoint in endpoints:
            try:
                if method == "GET":
                    response = await client.get(f"{API_BASE}{endpoint}")
                print(f"{method} {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"{method} {endpoint}: Error - {e}")


async def main():
    print("=" * 60)
    print("UI Integration API Test Suite")
    print(f"Testing against: {API_BASE}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)

    # Check if API is running
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{API_BASE}/health")
            if response.status_code != 200:
                print(f"\nERROR: API not healthy (status: {response.status_code})")
                print("Please start Engine 6 first:")
                print("  cd engines/engine6-web-ui/backend")
                print("  python api.py")
                return
    except Exception as e:
        print(f"\nERROR: Cannot connect to API at {API_BASE}")
        print(f"Error: {e}")
        print("\nPlease start Engine 6 first:")
        print("  cd engines/engine6-web-ui/backend")
        print("  python api.py")
        return

    # Run tests
    await test_dashboard_endpoints()
    await test_legacy_endpoints()
    await test_audit_workflow()

    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
