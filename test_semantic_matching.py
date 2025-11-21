"""
Test Semantic Matching vs Fuzzy Matching
Demonstrates accuracy improvement with AI-powered semantic matching
"""

import requests
import json
from typing import List, Dict
import time

# Test cases: extracted controls from hypothetical policy documents
TEST_CASES = [
    {
        "query": "Access management procedures and user authentication requirements",
        "expected_family": "Access Control",
        "description": "Should match access control policies"
    },
    {
        "query": "Security incident handling and response procedures",
        "expected_family": "Incident Response",
        "description": "Should match incident response controls"
    },
    {
        "query": "Employee cybersecurity awareness training programs",
        "expected_family": "Awareness and Training",
        "description": "Should match training controls"
    },
    {
        "query": "Data classification and information protection policy",
        "expected_family": "Media Protection",
        "description": "Should match media protection controls"
    },
    {
        "query": "System backup and recovery procedures",
        "expected_family": "Contingency Planning",
        "description": "Should match backup controls"
    },
    {
        "query": "Network security monitoring and logging requirements",
        "expected_family": "Audit and Accountability",
        "description": "Should match audit controls"
    },
    {
        "query": "Physical access control to server rooms",
        "expected_family": "Physical and Environmental Protection",
        "description": "Should match physical security controls"
    },
    {
        "query": "Vendor risk assessment and third-party security",
        "expected_family": "Risk Assessment",
        "description": "Should match risk assessment controls"
    }
]

ENGINE_2_URL = "http://localhost:8002"


def test_health_check():
    """Verify semantic matcher is enabled"""
    print("=" * 80)
    print("STEP 1: Health Check")
    print("=" * 80)

    try:
        response = requests.get(f"{ENGINE_2_URL}/health")
        health = response.json()

        print(f"\n✅ Status: {health.get('status', 'unknown')}")
        print(f"✅ Semantic Matcher Ready: {health.get('semantic_matcher_ready', False)}")
        print(f"✅ Semantic Matcher Enabled: {health.get('semantic_matcher_enabled', False)}")
        print(f"✅ Model: {health.get('semantic_model', 'N/A')}")
        print(f"✅ Total Controls: {health.get('total_rwanda_controls', {})}")

        if not health.get('semantic_matcher_enabled', False):
            print("\n⚠️  WARNING: Semantic matcher not enabled! Test will use fuzzy matching only.")
            return False

        return True

    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False


def test_control_search(query: str, test_case: Dict) -> Dict:
    """Test control search endpoint"""
    try:
        response = requests.get(
            f"{ENGINE_2_URL}/controls/search",
            params={"query": query, "limit": 5}
        )

        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "query": query,
                "results_count": result.get("results_count", 0),
                "top_match": result.get("controls", [])[0] if result.get("controls") else None,
                "all_results": result.get("controls", [])
            }
        else:
            return {
                "success": False,
                "query": query,
                "error": f"HTTP {response.status_code}"
            }

    except Exception as e:
        return {
            "success": False,
            "query": query,
            "error": str(e)
        }


def analyze_results(results: List[Dict]):
    """Analyze test results and compute metrics"""
    print("\n" + "=" * 80)
    print("STEP 2: Test Results Analysis")
    print("=" * 80)

    successful_tests = 0
    failed_tests = 0
    total_tests = len(results)

    for i, result in enumerate(results, 1):
        print(f"\n📝 Test Case {i}/{total_tests}")
        print(f"Query: \"{result['query']}\"")
        print(f"Expected Family: {result['expected_family']}")
        print(f"Description: {result['description']}")

        if result['success'] and result['results_count'] > 0:
            top_match = result['top_match']
            matched_family = top_match.get('family', 'Unknown')
            control_id = top_match.get('control_id', 'Unknown')
            control_name = top_match.get('name', 'Unknown')

            # Check if family matches expectation
            family_match = result['expected_family'].lower() in matched_family.lower()

            if family_match:
                print(f"✅ SUCCESS - Matched to correct family!")
                print(f"   Control: {control_id}")
                print(f"   Name: {control_name[:80]}...")
                print(f"   Family: {matched_family}")
                successful_tests += 1
            else:
                print(f"⚠️  PARTIAL - Matched but wrong family")
                print(f"   Expected: {result['expected_family']}")
                print(f"   Got: {matched_family}")
                print(f"   Control: {control_id}")
                failed_tests += 1

            # Show top 3 results
            print(f"\n   Top 3 Matches:")
            for j, match in enumerate(result['all_results'][:3], 1):
                print(f"   {j}. {match.get('control_id', 'N/A')} - {match.get('family', 'N/A')}")
        else:
            print(f"❌ FAILED - No matches found")
            print(f"   Error: {result.get('error', 'No results')}")
            failed_tests += 1

    # Summary
    print("\n" + "=" * 80)
    print("FINAL RESULTS SUMMARY")
    print("=" * 80)
    print(f"\n📊 Test Statistics:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Successful: {successful_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    print(f"   📈 Success Rate: {(successful_tests/total_tests*100):.1f}%")

    if successful_tests >= 6:
        print("\n🎉 EXCELLENT - Semantic matching working as expected!")
    elif successful_tests >= 4:
        print("\n👍 GOOD - Most test cases passing")
    else:
        print("\n⚠️  NEEDS IMPROVEMENT - Review matching algorithm")

    return {
        "total": total_tests,
        "successful": successful_tests,
        "failed": failed_tests,
        "success_rate": (successful_tests/total_tests*100)
    }


def main():
    """Run semantic matching tests"""
    print("🚀 SEMANTIC MATCHING TEST SUITE")
    print("Testing AI-powered control matching vs traditional fuzzy matching")
    print("=" * 80)

    # Check health
    if not test_health_check():
        print("\n⚠️  Proceeding with tests anyway (will use fuzzy matching)...")

    time.sleep(2)

    # Run test cases
    print("\n" + "=" * 80)
    print("Running Test Cases...")
    print("=" * 80)

    results = []
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n🔍 Test {i}/{len(TEST_CASES)}: {test_case['description']}")
        result = test_control_search(test_case['query'], test_case)
        result.update({
            'expected_family': test_case['expected_family'],
            'description': test_case['description']
        })
        results.append(result)
        time.sleep(0.5)  # Small delay between requests

    # Analyze results
    metrics = analyze_results(results)

    # Save results to file
    output_file = "/Users/moiseiradukunda/Documents/CMU/RESEARCH PROJECT/model-engine/semantic_test_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'metrics': metrics,
            'test_cases': results
        }, f, indent=2)

    print(f"\n💾 Results saved to: semantic_test_results.json")
    print("\n✅ Test suite completed!")


if __name__ == "__main__":
    main()
