#!/usr/bin/env python3
"""
Quick test script for ENGINE 2 Document Processor API
Tests the Rwanda NCSA control mapping fix
"""

import requests
import json
import sys

API_URL = "http://localhost:8002/process/document"
PDF_PATH = "docs/sample_policy_docs/Alvin Tech Internal Audit Report.pdf"

def test_document_processing():
    """Test document processing with Rwanda NCSA framework"""

    print("=" * 80)
    print("ENGINE 2 Document Processor - Rwanda NCSA Control Mapping Test")
    print("=" * 80)
    print()

    # Test parameters
    params = {
        "company_name": "Alvin Tech",
        "framework": "Rwanda-NCSA"
    }

    print(f"📄 Testing with: {PDF_PATH}")
    print(f"🎯 Framework: {params['framework']}")
    print(f"🏢 Company: {params['company_name']}")
    print()

    try:
        # Upload and process document
        with open(PDF_PATH, 'rb') as f:
            files = {'file': f}
            print("⏳ Sending document to API...")
            response = requests.post(API_URL, params=params, files=files, timeout=60)

        if response.status_code == 200:
            result = response.json()

            print("✅ Processing successful!")
            print()
            print("=" * 80)
            print("RESULTS")
            print("=" * 80)
            print()
            print(f"Company: {result.get('company_name')}")
            print(f"Framework: {result.get('framework')}")
            print(f"Document: {result.get('filename')}")
            print(f"Processing Time: {result.get('processing_time_seconds', 0):.2f}s")
            print()

            controls = result.get('controls', [])
            print(f"📋 Total Controls Extracted: {len(controls)}")
            print()

            # Show matched and unmatched controls
            matched = [c for c in controls if c.get('rwanda_ncsa_mapping')]
            unmatched = [c for c in controls if not c.get('rwanda_ncsa_mapping')]

            print(f"✅ Matched to Rwanda NCSA: {len(matched)}")
            print(f"❌ Unmatched: {len(unmatched)}")
            print()

            if matched:
                print("=" * 80)
                print("MATCHED CONTROLS (First 3)")
                print("=" * 80)
                for i, control in enumerate(matched[:3], 1):
                    mapping = control['rwanda_ncsa_mapping']
                    print(f"\n{i}. {control.get('control_name', 'N/A')}")
                    print(f"   ID: {control.get('control_id', 'N/A')}")
                    print(f"   Family: {control.get('family', 'N/A')}")
                    print(f"   ✅ Mapped to Rwanda: {mapping.get('control_id')} - {mapping.get('name', '')[:60]}...")
                    print(f"   Match Score: {mapping.get('match_score', 0)}")

            if unmatched:
                print("\n" + "=" * 80)
                print("UNMATCHED CONTROLS (First 2)")
                print("=" * 80)
                for i, control in enumerate(unmatched[:2], 1):
                    print(f"\n{i}. {control.get('control_name', 'N/A')}")
                    print(f"   ID: {control.get('control_id', 'N/A')}")
                    print(f"   Family: {control.get('family', 'N/A')}")
                    print(f"   ❌ No Rwanda NCSA mapping found")

            print("\n" + "=" * 80)
            print("TEST COMPLETE")
            print("=" * 80)

            # Return success code
            return 0

        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(response.text)
            return 1

    except requests.Timeout:
        print("❌ Error: Request timed out after 60 seconds")
        return 1
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(test_document_processing())
